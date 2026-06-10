import pytest
from werkzeug.security import generate_password_hash
from main import app, db, Lead, users

@pytest.fixture
def test_client():
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"  # Databáze v RAM
    app.config["WTF_CSRF_ENABLED"] = False  # Vypnutí ochrany formulářů pro testy

    users.clear()
    users["test_admin"] = {"password": generate_password_hash("admin123"), "role": "admin"}
    users["test_sales"] = {"password": generate_password_hash("sales123"), "role": "sales"}

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()  # Po testu vše smaže

def login(client, username, password):
    return client.post("/login", data={"username": username, "password": password}, follow_redirects=True)

def test_unauthenticated_user_redirects_to_login(test_client):
    """Nepřihlášený uživatel se nedostane na hlavní stránku."""
    response = test_client.get("/")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_successful_login(test_client):
    """Správné přihlášení projde."""
    response = login(test_client, "test_sales", "sales123")
    assert response.status_code == 200
    assert b"Spatne uzivatelske jmeno" not in response.data


def test_lead_scoring_logic_saves_hot_lead(test_client):
    """Odeslání formuláře s ideálním zákazníkem vytvoří HOT lead."""
    login(test_client, "test_sales", "sales123")

    form_data = {
        "client_name": "Jan Novák",
        "brand": "Škoda",
        "model": "Kodiaq",
        "contract_type": "navsteva_prodejny",
        "selection_stage": "ma_vybrano",
        "interest_level": "testovaci_jizda",
        "config": "pripravena",
        "budget": "pripraven_financovat",
        "finance": "hotovost",
        "timing": "chci_ihned",
        "availability": "skladovy_vuz"
    }

    response = test_client.post("/", data=form_data, follow_redirects=True)
    assert response.status_code == 200

    saved_lead = db.session.scalars(db.select(Lead)).first()
    assert saved_lead is not None
    assert saved_lead.client_name == "Jan Novák"
    assert saved_lead.status == "HOT"
    assert saved_lead.score == 100


def test_authorization_user_cannot_view_others_lead(test_client):
    """Prodejce nesmí vidět detail leadu cizího prodejce."""
    login(test_client, "test_sales", "sales123")
    test_client.post("/", data={"client_name": "Můj Zákazník"})
    lead = db.session.scalars(db.select(Lead)).first()
    lead_id = lead.id
    test_client.get("/logout", follow_redirects=True)

    users["test_sales_2"] = {"password": generate_password_hash("sales123"), "role": "sales"}
    login(test_client, "test_sales_2", "sales123")

    response = test_client.get(f"/lead/{lead_id}")
    assert response.status_code == 403
    assert b"Do tohoto leadu nem" in response.data


def test_admin_can_delete_any_lead(test_client):
    """Admin má právo smazat jakýkoliv lead."""
    login(test_client, "test_sales", "sales123")
    test_client.post("/", data={"client_name": "Na smazání"})
    lead = db.session.scalars(db.select(Lead)).first()
    lead_id = lead.id
    test_client.get("/logout")

    login(test_client, "test_admin", "admin123")
    response = test_client.post(f"/delete-lead/{lead_id}", follow_redirects=True)
    assert response.status_code == 200

    leads_in_db = db.session.scalars(db.select(Lead)).all()
    assert len(leads_in_db) == 0


def test_non_existent_page_returns_404(test_client):
    """Zadání neexistující URL vrátí status 404 a chybovou stránku."""
    response = test_client.get("/--")
    assert response.status_code == 404
    assert b"404" in response.data
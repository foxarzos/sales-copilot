import pytest
from unittest.mock import patch
from werkzeug.security import generate_password_hash
from main import app, db, Lead, users


@pytest.fixture
def test_client():
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"  # Databáze v RAM
    app.config["WTF_CSRF_ENABLED"] = False

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


@patch('main.ai_strategy')
def test_lead_scoring_logic_saves_hot_lead(mock_ai_strategy, test_client):
    """Odeslání formuláře s ideálním zákazníkem vytvoří HOT lead a uloží AI doporučení."""

    # Co má AI vrátit, místo aby reálně volalo Gemini
    # První řádek je shrnutí, další řádky jsou tipy
    mock_ai_strategy.return_value = "Falešné AI shrnutí zákazníka\nPrvní prodejní krok\nDruhý prodejní krok"

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

    assert saved_lead.ai_summary == "Falešné AI shrnutí zákazníka"
    assert saved_lead.ai_tips == "První prodejní krok|Druhý prodejní krok"


def test_lead_detail_displays_ai_data(test_client):
    """Stránka detailu leadu správně zobrazuje uložená AI data."""
    login(test_client, "test_sales", "sales123")

    new_lead = Lead(
        client_name="Petr Novotný",
        status="WARM",
        score=60,
        ai_summary="Shrnutí pro Petra",
        ai_tips="Tip 1|Tip 2",
        created_by="test_sales"
    )
    db.session.add(new_lead)
    db.session.commit()

    response = test_client.get(f"/lead/{new_lead.id}")
    assert response.status_code == 200

    assert "Shrnutí pro Petra".encode('utf-8') in response.data
    assert "Tip 1|Tip 2".encode('utf-8') in response.data


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
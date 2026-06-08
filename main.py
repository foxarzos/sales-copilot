from flask import Flask, render_template, request, redirect
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from config import Config
import json
import os

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)

class Lead(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    client_name = db.Column(db.String(100))
    brand = db.Column(db.String(50))
    model = db.Column(db.String(50))
    intent = db.Column(db.String(50))
    config = db.Column(db.String(50))
    finance = db.Column(db.String(50))
    budget = db.Column(db.String(50))
    activity = db.Column(db.String(50))
    trigger = db.Column(db.String(50))
    competition = db.Column(db.String(50))
    timing = db.Column(db.String(50))
    status = db.Column(db.String(20))
    score = db.Column(db.Integer)

    won = db.Column(db.Boolean, nullable=True)

    created_by = db.Column(db.String(100))
    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.utcnow() + timedelta(hours=2)
    )


with app.app_context():
    db.create_all()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

class User(UserMixin):
    def __init__(self, username, role):
        self.id = username
        self.username = username
        self.role = role

def load_users_from_file():
    if os.path.exists("users.json"):
        with open("users.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return {"admin": {"password": "admin", "role": "admin"}}

users = load_users_from_file()

@login_manager.user_loader
def load_user(user_id):
    if user_id not in users:
        return None
    return User(username=user_id, role=users[user_id]["role"])

@app.route("/login", methods=["GET", "POST"])
def login():

    error = None

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username in users and check_password_hash(users[username]["password"], password):
            user_role = users[username]["role"]
            user = User(username=username, role=user_role)
            login_user(user)
            return redirect("/")
        else:
            error = "Špatné uživatelské jméno nebo heslo"

    return render_template("login.html",error=error)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/login")

@app.route("/", methods=["GET","POST"])
@login_required
def home():
    score = 0
    status = None
    doporuceni = []

    if request.method == "POST":
        jmeno_zakaznika = request.form.get("client_name")
        brand = request.form.get("brand")
        model = request.form.get("model")
        typ_kontraktu = request.form.get("contract_type")
        faze_vyberu = request.form.get("selection_stage")
        uroven_zajmu = request.form.get("interest_level")
        pripravenost_konfigurace = request.form.get("config")
        rozpocet = request.form.get("budget")
        financovani = request.form.get("finance")
        casovy_horizont = request.form.get("timing")
        dostupnost_modelu = request.form.get("availability")

        base_score = 0

        contract_type_weights = {"jen_vola_pise": 5, "navsteva_prodejny": 25}
        base_score += contract_type_weights.get(typ_kontraktu, 0)

        selection_stage_weights = {
            "nevi_co_chce": 5,
            "musi_budget": 10,
            "porovnava_konkurenci": 15,
            "ma_vybrano": 25
        }
        base_score += selection_stage_weights.get(faze_vyberu, 0)

        interest_level_weights = {
            "pta_se_na_detaily": 10,
            "prohlizi_interier": 10,
            "tco": 15,
            "zustatkova_hodnota": 15,
            "testovaci_jizda": 30
        }
        base_score += interest_level_weights.get(uroven_zajmu, 0)

        config_state_weights = {
            "bez_konfigurace": 0,
            "chce_poradit": 5,
            "chce_doladit": 12,
            "pripravena": 20
        }
        base_score += config_state_weights.get(pripravenost_konfigurace, 0)

        base_score = min(base_score, 100)

        korekce = []

        budget_multipliers = {
            "nedostatecny": 0.4,
            "presne_definovany": 1.0,
            "realny_rezerva": 1.1,
            "pripraven_financovat": 1.2
        }
        korekce.append(budget_multipliers.get(rozpocet, 1.0))

        finance_multipliers = {
            "hotovost": 1.0,
            "klasicky_uver": 1.1,
            "operativni_leasing": 1.15,
            "firem_flotila": 1.2
        }
        korekce.append(finance_multipliers.get(financovani, 1.0))

        timing_multipliers = {
            "jen_se_divam": 0.5,
            "pristi_rok": 0.7,
            "do_3_mesicu": 1.1,
            "chci_ihned": 1.3
        }
        korekce.append(timing_multipliers.get(casovy_horizont, 1.0))

        availability_multipliers = {
            "dlouha_lhuta": 0.8,
            "bezna_lhuta": 1.0,
            "skladovy_vuz": 1.2
        }
        korekce.append(availability_multipliers.get(dostupnost_modelu, 1.0))

        final_multiplier = sum(korekce) / len(korekce)

        score = min(round(base_score * final_multiplier), 100)

        vybrany_vuz = request.form.get("car_selection")

        if vybrany_vuz:
            brand, model = vybrany_vuz.split("|")

        if score >= 75:
            status = "HOT"
        elif score >= 40:
            status = "WARM"
        else:
            status = "COLD"

        lead = Lead(
            client_name=jmeno_zakaznika,
            brand=brand,
            model=model,
            intent=faze_vyberu,
            finance=financovani,
            config=pripravenost_konfigurace,
            budget=rozpocet,
            activity=uroven_zajmu,
            trigger=typ_kontraktu,
            competition=dostupnost_modelu,
            timing=casovy_horizont,
            score=score,
            status=status,
            created_by=current_user.id
        )

        db.session.add(lead)
        db.session.commit()

        if casovy_horizont == "chci_ihned" and dostupnost_modelu == "skladovy_vuz":
            doporuceni.append(
                "⚠️ <b>Rezervujte vůz:</b> Zákazník spěchá a auto máte skladem. Nabídněte okamžitou rezervaci vozu ještě dnes.")

        if dostupnost_modelu == "dlouha_lhuta" and casovy_horizont in ["chci_ihned", "do_3_mesicu"]:
            doporuceni.append(
                "🔄 <b>Nabídněte alternativu:</b> Čekací doba je 6+ měsíců, ale klient chce auto dříve. Nabídněte předváděcí vůz nebo podobnou skladovku, jinak odejde ke konkurenci.")

        if pripravenost_konfigurace in ["chce_poradit", "chce_doladit"]:
            doporuceni.append(
                "💻 <b>Konfigurace:</b> Pozvěte klienta na kávu ke konfigurátoru na showroomu a sestavte auto společně. Zvyšte tím šanci na prodej příplatkové výbavy.")

        if uroven_zajmu == "testovaci_jizda":
            doporuceni.append(
                "🔑 <b>Posaďte ho za volant:</b> Testovací jízda je klíč k prodeji. Pokud ještě neproběhla, zarezervujte termín do 48 hodin.")

        if status == "HOT":
            doporuceni.append(
                "🔥 <b>TOP Priorita:</b> Tento lead má nejvyšší prioritu. Kontaktujte ho minimálně každých 48 hodin, dokud nepodepíše.")
        elif status == "WARM":
            doporuceni.append(
                "📞 <b>Následný krok:</b> Klient porovnává možnosti. Pošlete mu personalizovanou nabídku do e-mailu a zavolejte za 3 dny.")
        elif status == "COLD":
            doporuceni.append(
                "📧 <b>Budování vztahu:</b> Klient není připraven ke koupi nebo teprve mapuje trh. Zapiště si kontakt na klienta a ozvěte se za měsíc.")

    return render_template("index.html", score=score, status=status, doporuceni=doporuceni)

@app.route("/leads")
@login_required
def leads():
    if current_user.role == "admin":
        query = db.select(Lead).order_by(Lead.id.desc())
    else:
        query = db.select(Lead).where(Lead.created_by == current_user.id).order_by(Lead.id.desc())

    all_leads = db.session.scalars(query).all()
    return render_template("leads.html", leads=all_leads)

@app.route("/lead/<int:id>")
@login_required
def lead_detail(id):
    lead = db.get_or_404(Lead, id)
    if current_user.role != "admin" and lead.created_by != current_user.id:
        return "Do tohoto leadu nemáš přístup.", 403
    return render_template("lead_detail.html", lead=lead)

@app.route("/update-lead/<int:id>", methods=["POST"])
@login_required
def update_lead(id):
    lead = db.get_or_404(Lead, id)

    if current_user.role != "admin" and lead.created_by != current_user.id:
        return "Nemáš oprávnění upravovat tento lead.", 403

    result = request.form.get("won")

    if result == "true":
        lead.won = True
    elif result == "false":
        lead.won = False

    db.session.commit()

    return redirect("/leads")

@app.route("/delete-lead/<int:id>", methods=["POST"])
@login_required
def delete_lead(id):
    lead = db.get_or_404(Lead, id)

    if current_user.role != "admin" and lead.created_by != current_user.id:
        return "Nemáš oprávnění smazat tento lead.", 403

    db.session.delete(lead)
    db.session.commit()

    return redirect("/leads")

@app.route("/landing")
def landing():
    return render_template("landing.html")

if __name__ == "__main__":
    app.run(debug=True)




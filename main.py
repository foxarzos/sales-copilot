from flask import Flask, render_template, request, redirect
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta, timezone
from config import Config
from scoring import calculate_lead_data
from flask_wtf.csrf import CSRFProtect
import json
import os
from ai_service import ai_strategy

app = Flask(__name__)
app.config.from_object(Config)
csrf = CSRFProtect(app)

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
    ai_summary = db.Column(db.Text, nullable=True)
    ai_tips = db.Column(db.Text, nullable=True)
    won = db.Column(db.Boolean, nullable=True)

    created_by = db.Column(db.String(100))
    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(hours=2)
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

@app.route("/", methods=["GET", "POST"])
@login_required
def home():
    score = 0
    status = None
    doporuceni = []
    ai_summary = None
    ai_tips = []

    if request.method == "POST":
        jmeno_zakaznika = request.form.get("client_name")

        score, status, doporuceni, brand, model = calculate_lead_data(request.form)

        lead = Lead(
            client_name=jmeno_zakaznika,
            brand=brand,
            model=model,
            intent=request.form.get("selection_stage"),
            finance=request.form.get("finance"),
            config=request.form.get("config"),
            budget=request.form.get("budget"),
            activity=request.form.get("interest_level"),
            trigger=request.form.get("contract_type"),
            competition=request.form.get("availability"),
            timing=request.form.get("timing"),
            score=score,
            status=status,
            created_by=current_user.id
        )

        try:
            # raise Exception("Simulovaný limit kvóty")
            raw_ai_text = ai_strategy(lead)

            if raw_ai_text:
                lines = [line.strip() for line in raw_ai_text.split('\n') if line.strip()]

                if lines:
                    ai_summary = lines[0]
                    ai_tips = lines[1:]
                else:
                    ai_summary = "Systémové vyhodnocení leadu (AI nedostupná):"
                    ai_tips = doporuceni
            else:
                ai_summary = "Systémové vyhodnocení leadu (AI nedostupná):"
                ai_tips = doporuceni

        except Exception as e:
            print(f"⚠️ Gemini API Quota Limit hit ({e}). Přepínám na statický fallback.")

            if doporuceni:
                ai_summary = doporuceni[0]
                ai_tips = doporuceni[1:]
            else:
                ai_summary = f"Systémové vyhodnocení ({status} lead - Limit AI vyčerpán):"
                ai_tips = []

        lead.ai_summary = ai_summary
        lead.ai_tips = "|".join(ai_tips) if ai_tips else ""

        db.session.add(lead)
        db.session.commit()

    return render_template("index.html", score=score, status=status, doporuceni=doporuceni,ai_summary=ai_summary,ai_tips=ai_tips)

@app.route("/leads")
@login_required
def leads():
    sort_by = request.args.get('sort', 'newest')

    if current_user.role == "admin":
        query = db.select(Lead)
    else:
        query = db.select(Lead).where(Lead.created_by == current_user.id)

    if sort_by == "score":
        query = query.order_by(Lead.score.desc())
    elif sort_by == "alphabetical":
        query = query.order_by(Lead.client_name.asc())
    else:
        query = query.order_by(Lead.id.desc())

    all_leads = db.session.scalars(query).all()

    return render_template("leads.html", leads=all_leads, current_sort=sort_by)

@app.route("/lead/<int:id>")
@login_required
def lead_detail(id):
    lead = db.get_or_404(Lead, id)
    if current_user.role != "admin" and lead.created_by != current_user.id:
        return render_template("403.html"), 403
    return render_template("lead_detail.html", lead=lead)

@app.route("/update-lead/<int:id>", methods=["POST"])
@login_required
def update_lead(id):
    lead = db.get_or_404(Lead, id)

    if current_user.role != "admin" and lead.created_by != current_user.id:
        return render_template("403.html"), 403

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
        return render_template("403.html"), 403

    db.session.delete(lead)
    db.session.commit()

    return redirect("/leads")

@app.route("/landing")
def landing():
    return render_template("landing.html")

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

if __name__ == "__main__":
    app.run(debug=True)




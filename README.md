# 🚀 SalesCopilot – AI Lead Scoring Systém pro Automotive

**SalesCopilot** je komplexní full-stack webová aplikace navržená pro automatické vyhodnocování, analýzu a prioritizaci zákaznických poptávek (leadů) v automobilovém průmyslu. Systém využívá pokročilé modely umělé inteligence k tomu, aby z textu a parametrů poptávky okamžitě identifikoval zákazníky s nejvyšším potenciálem k nákupu, navrhl prodejní argumenty a zefektivnil práci obchodního týmu.

Aplikace je plně nasazena v cloudovém produkčním prostředí a aktivně ji využívají **3 uživatelé v reálném provozu**.

**Web projektu:** [salescopilotcz.onrender.com](https://salescopilotcz.onrender.com)

*(Uvnitř aplikace probíhá ostrý provoz, detailní ukázky systému naleznete níže ve vizuálním workflow).*

---

## 📷 Ukázka z aplikace (Vizuální workflow)

### 1. Vstupní stránka (Landing Page)
Prezentace klíčových funkcí systému pro koncové uživatele.
<img width="1919" height="956" alt="image" src="https://github.com/user-attachments/assets/076d18b9-70b5-4cbe-92d4-d514eaac7f0d" />


### 2. Zabezpečené rozhraní (Login)
Autentizace uživatelů zajišťující řízený přístup k obchodním datům.
<img width="1919" height="957" alt="image" src="https://github.com/user-attachments/assets/a95a4644-f1a1-41fd-8b8e-017855593db3" />

### 3. AI Analýza a vyhodnocení leadu
Pohled do detailu leadu s okamžitou AI nápovědou. Prodejce vidí nejen pravděpodobnost uzavření obchodu, ale také podrobné shrnutí kontextu zákazníka a konkrétní doporučenou strategii (např. využití testovací jízdy k odhalení potřeb), což výrazně zvyšuje šanci na úspěšný prodej.
<img width="1919" height="956" alt="image" src="https://github.com/user-attachments/assets/5031b529-0f03-4da8-8bdd-e8936da11739" />

### 4. Obchodní Dashboard (Seznam leadů)
Přehledná správa a prioritizace rozpracovaných poptávek podle stavu a úspěšnosti.
<img width="1919" height="958" alt="image" src="https://github.com/user-attachments/assets/83eb7e51-8824-461c-866e-88dd86861f66" />


### 5. Inteligentní analýza (Detail vyhodnoceného leadu)
Systém v praxi. Na základě zadaných parametrů generuje **Google GenAI** textové shrnutí situace klienta a doporučuje konkrétní prodejní kroky a výzvy.
<img width="1919" height="956" alt="image" src="https://github.com/user-attachments/assets/36cd65dd-98ff-4c70-9a33-4e7ed0ac40bd" />


### 6. Správa incidentů a logování
Důkaz spolehlivosti produkčního běhu. Aplikace zaznamenává veškeré HTTP požadavky a vlastní stavy, jako je úspěšné zpracování odpovědi z AI API.
<img width="1919" height="956" alt="image" src="https://github.com/user-attachments/assets/2a0408a1-5626-45c7-b7fc-d13c145c9e10" />

---

## 🛠️ Použitý Tech Stack & Architektura

* **Backend:** Python (Framework Flask)
* **Frontend:** HTML5, CSS3, moderní UI komponenty (plně responzivní design)
* **ORM & Databáze:** SQLAlchemy, PostgreSQL (hostováno na platformě Supabase)
* **AI Integrace:** Google GenAI API (model Gemini 2.5 Flash pro analýzu a text generation)
* **Infrastruktura & DevOps:** Cloud platforma Render
* **CI/CD:** Automatizovaná pipeline (propojení GitHub -> Render, každý stabilní push automaticky nasazuje novou verzi)
* **Vývojové prostředí:** OS Windows (lokální debugování, správa závislostí přes venv)

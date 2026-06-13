import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MAPPINGS = {
    "contract_type": {
        "pise_mail": "Píše e-mail / Webový formulář",
        "jen_vola": "Pouze telefonuje",
        "navsteva_prodejny": "Osobní návštěva prodejny"
    },
    "selection_stage": {
        "nevi_co_chce": "Neví, co přesně chce",
        "musi_budget": "Musí se vejít do budgetu",
        "porovnava_konkurenci": "Porovnává s konkurencí",
        "ma_vybrano": "Má vybraný konkrétní model"
    },
    "interest_level": {
        "pta_se_na_detaily": "Zajímá se o technické detaily",
        "testovaci_jizda": "Má zájem o testovací jízdu",
        "prohlizi_interier": "Prohlíží si interiér",
        "zustatkova_hodnota": "Zajímá ho zůstatková hodnota",
        "tco": "Řeší celkové náklady na vlastnictví (TCO) - firmy"
    },
    "config": {
        "bez_konfigurace": "Zatím bez konfigurace",
        "chce_poradit": "Chce poradit s konfigurací od nuly",
        "chce_doladit": "Chce pouze doladit stávající konfiguraci",
        "pripravena": "Má připravenou hotovou konfiguraci"
    },
    "budget": {
        "nedostatecnony": "Nedostatečný (chce model mimo možnosti)",
        "presne_definovany": "Přesně definovaný rozpočet",
        "realny_rezerva": "Reálný rozpočet s rezervou",
        "pripraven_financovat": "Předem schválen financovat"
    },
    "finance": {
        "hotovost": "Hotovost",
        "klasicky_uver": "Klasický úvěr",
        "operativni_leasing": "Operativní leasing",
        "firem_flotila": "Firemní flotila"
    },
    "timing": {
        "jen_se_divam": "Jen se dívá / zjišťuje",
        "pristi_rok": "6 a více měsíců",
        "do_3_mesicu": "Do 3 měsíců",
        "chci_ihned": "Chce vozidlo ihned (skladovku)"
    },
    "availability": {
        "dlouha_lhuta": "Dlouhá čekací lhůta (6+ měsíců)",
        "bezna_lhuta": "Běžná čekací lhůta (do 3 měsíců)",
        "skladovy_vuz": "Skladový vůz (ihned)"
    }
}

def ai_strategy(lead):
    c_type = MAPPINGS["contract_type"].get(lead.trigger, "Nezadáno")
    stage = MAPPINGS["selection_stage"].get(lead.intent, "Nezadáno")
    interest = MAPPINGS["interest_level"].get(lead.activity, "Nezadáno")
    config = MAPPINGS["config"].get(lead.config, "Nezadáno")
    budget = MAPPINGS["budget"].get(lead.budget, "Nezadáno")
    finance = MAPPINGS["finance"].get(lead.finance, "Nezadáno")
    timing = MAPPINGS["timing"].get(lead.timing, "Nezadáno")
    availability = MAPPINGS["availability"].get(lead.competition, "Nezadáno")

    prompt = f"""
    Jsi špičkový AI kouč pro prodejce nových vozů. Tvým úkolem je analyzovat tento obchodní případ pro vůz {lead.brand} {lead.model} a dát prodejci okamžitý návod.
    
    VSTUPNÍ DATA O KLIENTOVI:
    - Typ kontaktu: {c_type} | Fáze výběru: {stage} | Úroveň zájmu: {interest}
    - Konfigurace: {config} | Rozpočet: {budget} | Finance: {finance}
    - Timing: {timing} | Dostupnost vozu: {availability}
    
    ÚKOL:
    Vytvoř přesně 3 prodejní doporučení/tipy šité na míru této situaci. Inteligentně analyzuj chování zákazníků a navrhni přesné prodejní fráze pro obchodní úspěch.
    
    STRIKTNÍ PRAVIDLA PRO DÉLKU:
    - Každé doporučení musí být extrémně stručné a úderné.
    - Délka jednoho doporučení musí být POUZE 1 NEBO MAXIMÁLNĚ 2 VĚTY. Pokud to lze říct jednou větou, udělej to. Žádné obecné informace.
    
    KRITICKÉ PRAVIDLO PRO FORMÁT:
    Napiš text tak, aby každý tip byl na samostatném novém řádku. Nepoužívej žádná čísla odrážek (1., 2.) ani pomlčky. Každý řádek musí začínat emoji a názvem v HTML formátu <b>...</b>, přesně takto:
    
    [Zde napiš celkové shrnutí tohoto leadu a situace zákazníka přesně na 2 až 3 výstižné věty]
    🔥 <b>Výzva:</b> [Zde napiš 1 až max 2 věty o hlavní komplikaci]
    🎯 <b>Strategie:</b> [Zde napiš 1 až max 2 věty, co přesně má prodejce udělat]
    💬 <b>Argument:</b> [Zde napiš konkrétní prodejní větu na 1 až max 2 věty, kterou má prodejce klientovi říct]
    💡 <b>Tip:</b> [Zde vymysli krátký a úderný tip pro prodejce na závěr]
    """

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return response.text
    except Exception as e:
        print(f"Chyba při volání Gemini API: {e}")
        raise e
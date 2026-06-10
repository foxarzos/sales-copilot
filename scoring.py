def calculate_lead_data(form_data):
    typ_kontraktu = form_data.get("contract_type")
    faze_vyberu = form_data.get("selection_stage")
    uroven_zajmu = form_data.get("interest_level")
    pripravenost_konfigurace = form_data.get("config")
    rozpocet = form_data.get("budget")
    financovani = form_data.get("finance")
    casovy_horizont = form_data.get("timing")
    dostupnost_modelu = form_data.get("availability")

    brand = form_data.get("brand")
    model = form_data.get("model")
    vybrany_vuz = form_data.get("car_selection")

    if vybrany_vuz:
        brand, model = vybrany_vuz.split("|")

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

    if score >= 75:
        status = "HOT"
    elif score >= 40:
        status = "WARM"
    else:
        status = "COLD"

    doporuceni = []

    if casovy_horizont == "chci_ihned" and dostupnost_modelu == "skladovy_vuz":
        doporuceni.append(
            "<b>Okamžitá rezervace:</b> Zákazník spěchá a vůz je skladem. Využijte toho! Vytvořte FOMO efekt a nabídněte mu okamžitou rezervaci vozu.")

    if dostupnost_modelu == "dlouha_lhuta" and casovy_horizont in ["chci_ihned", "do_3_mesicu"]:
        doporuceni.append(
            "<b>Záchrana obchodu:</b> Čekací doba z výroby je moc dlouhá a hrozí, že klient půjde ke konkurenci. Okamžitě mu předložte alternativu – nabídněte předváděcí vůz, roční auto z programu nebo skladovku v podobné výbavě.")

    if pripravenost_konfigurace in ["chce_poradit", "chce_doladit"]:
        doporuceni.append(
            "<b>Osobní konfigurace:</b> Klient si není jistý výbavou. Neřešte to přes e-mail! Pozvěte ho na kávu ke konfigurátoru na showroomu. Společná konfigurace vozu tvoří emoci a dramaticky zvyšuje šanci, že si připlatí za lepší výbavu.")

    if uroven_zajmu == "testovaci_jizda":
        doporuceni.append(
            "<b>Testovací jízda:</b> Auto prodávají emoce za volantem. Vaším jediným cílem je teď dostat klienta do vozu. Dejte mu na výběr ze 2 konkrétních termínů a zarezervujte jízdu nejpozději do 48 hodin.")

    if status == "HOT":
        doporuceni.append(
            "<b>🔥Closing priorita:</b> Klient je připraven koupit. Úkolem je vyřešit poslední administrativu (financování, protiúčet). Buďte proaktivní, udržujte kontakt každých 48 hodin a uzavřete smlouvu dřív, než nákupní emoce ochladne.")
    elif status == "WARM":
        doporuceni.append(
            "<b>🟡Aktivní Follow-up:</b> Klient má zájem, ale srovnává nabídky a přemýšlí. Pošlete mu kalkulaci/konfiguraci a rovnou si na konci hovoru domluvte PŘESNÝ čas dalšího kontaktování. Nenechávejte rozhodnutí na něm.")
    elif status == "COLD":
        doporuceni.append(
            "<b>❄️Budování vztahu:</b> Klient se teprve rozhlíží. Netlačte na něj. Nastavte si připomenutí kontaktování do kalendáře na další měsíc a ozvěte se mu s nějakou přidanou hodnotou (např. pozvánka na testovací dny nebo nový akční ceník).")

    return score, status, doporuceni, brand, model
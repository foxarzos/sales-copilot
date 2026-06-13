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
            "⚡ OKAMŽITÁ REZERVACE - Zákazník spěchá a vůz je skladem. Využijte toho! Vytvořte FOMO efekt a nabídněte mu okamžitou rezervaci vozu.")

    if dostupnost_modelu == "dlouha_lhuta" and casovy_horizont in ["chci_ihned", "do_3_mesicu"]:
        doporuceni.append(
            "🛡️ ZÁCHRANA OBCHODU - Čekací doba je moc dlouhá a hrozí, že klient odejde ke konkurenci. Okamžitě mu předložte alternativu – nabídněte předváděcí vůz, roční auto z programu nebo skladovku v podobné výbavě.")

    if pripravenost_konfigurace in ["chce_poradit", "chce_doladit"]:
        doporuceni.append(
            "☕ OSOBNÍ KONFIGURACE - Klient si není jistý výbavou. Neřešte to přes e-mail. Pozvěte ho na kávu ke konfigurátoru na showroomu. Společná konfigurace vozu tvoří emoci a zvyšuje šanci, že si připlatí za lepší výbavu.")

    if uroven_zajmu == "testovaci_jizda":
        doporuceni.append(
            "🏎️ TESTOVACÍ JÍZDA - Emoce prodávají. Vaším jediným cílem je teď dostat klienta do vozu. Dejte mu na výběr ze dvou konkrétních termínů a zarezervujte jízdu nejpozději do 48 hodin.")

    if status == "HOT":
        doporuceni.insert(0,
                          "🔥 CLOSING PRIORITA - Klient je připraven koupit. Úkolem je vyřešit poslední administrativu (financování, protiúčet). Buďte proaktivní, udržujte kontakt každých 48 hodin a uzavřete smlouvu dřív, než nákupní emoce ochladne.")

        doporuceni.append(
            "💬 <b>Finální ujištění:</b> „Vypadá to, že jsme našli přesně to, co jste hledal. Brání nám teď ještě něco v tom, abychom rovnou vozidlo objednali/rezervovali?“")
        doporuceni.append(
            "💬 <b>Práce s nedostatkem:</b> „Dívám se do systému a na tento model v této barvě mám ve výrobě už jen jedno volné místo. Mám ho zablokovat na Vaše jméno, ať o něj nepřijdeme?“")
        doporuceni.append(
            "💬 <b>Záchrana při záseku na ceně:</b> „Ve výsledku se bavíme o rozdílu zhruba 800 Kč měsíčně na splátce. Stojí Vám těch pár set za to, abyste nemusel dělat kompromisy na další 4 roky?“")
        doporuceni.append(
            "💡 <b>Tip pro prodejce:</b> Jakmile položíte závěrečnou otázku k uzavření obchodu (např. 'Podepíšeme to?'), mlčte. Kdo promluví jako první, prohrává.")

    elif status == "WARM":

        doporuceni.insert(0,
                          "🟡 AKTIVNÍ FOLLOW-UP - Klient má zájem, ale srovnává nabídky a přemýšlí. Pošlete mu kalkulaci/konfiguraci a rovnou si na konci hovoru domluvte přesný čas dalšího kontaktování. Nenechávejte rozhodnutí na něm.")

        doporuceni.append(
            "💬 <b>Při testovací jízdě:</b> „Všimněte si teď, jak auto skvěle tlumí nerovnosti. To je přesně to, o čem jsme mluvili po telefonu. Jaký z jízdy máte pocit oproti Vašemu současnému vozu?“")
        doporuceni.append(
            "💬 <b>Zvládnutí námitky:</b> „Naprosto rozumím, auto se nekupuje každý den. Většinou to znamená, že si klienti nejsou jistí samotným autem, nebo ještě ladíme rozpočet. Můžu se upřímně zeptat, jak to cítíte vy?“")
        doporuceni.append(
            "💬 <b>Konkurence:</b> „Konkurence dělá skvělá auta, to nepopírám. Kdybyste si ale odmyslel tu cenovku a mohl si vybrat jen podle toho, ve kterém autě se cítíte lépe... které by to bylo?“")
        doporuceni.append(
            "💡 <b>Tip pro prodejce:</b> Pokud klient mluví o konkurenci, nikdy ji nehaňte. Spíše ho naveďte k tomu, aby si sám uvědomil, proč je vaše nabídka hodnotnější.")

    elif status == "COLD":
        doporuceni.insert(0,
                          "❄️ BUDOVÁNÍ VZTAHU – Klient se teprve rozhlíží. Netlačte na něj. Nastavte si připomenutí kontaktování do kalendáře na další měsíc a ozvěte se mu s nějakou přidanou hodnotou (např. pozvánka na testovací dny nebo nový akční ceník).")

        doporuceni.append(
            "💬 <b>Odhalení skrytých potřeb:</b> „Když si představíte svůj ideální vůz na další tři, čtyři roky, co v něm nesmí chybět?“")
        doporuceni.append(
            "💬 <b>Převzetí kontroly:</b> „Většina mých klientů na našich vozech nejvíce oceňuje ticho v kabině a skvělý infotainment. Jak to máte s technologiemi v autě vy, využijete je?“")
        doporuceni.append(
            "💬 <b>Pomalé směřování k akci:</b> „Nechci vás teď zahltit letáky a čísly. Co kdybyste se u nás příští týden na 20 minut zastavil, dáme si kávu a vy si do toho auta jenom zkusíte sednout?“")
        doporuceni.append(
            "💡 <b>Tip pro prodejce:</b> Poslouchejte v poměru 80/20. Klient by měl mluvit 80 % času. Vaším cílem je zjistit jeho 'bolest' (problém se starým vozem, rodina se rozrůstá, chce reprezentovat).")

    return score, status, doporuceni, brand, model
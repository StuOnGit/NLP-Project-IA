from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
import pyperclip


def start_browser():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


def extract_all_services():
    """Estrae tutti i servizi da https://ifttt.com/explore/services"""
    driver = start_browser()
    driver.get("https://ifttt.com/explore/services")
    time.sleep(4)

     # Trova i servizi
    service_cards = driver.find_elements(By.CSS_SELECTOR, "a[class*='service-card']")
    services = []

    for card in service_cards:
        name = card.get_attribute("aria-label") or card.text.strip()
        link = card.get_attribute("href")
        if name and link:
            services.append((name, link))

    driver.quit()
    return services


def get_triggers_actions_queries(service_url):
    """Dato l'URL di un servizio, estrae link a trigger,action e query"""
    driver = start_browser()
    driver.get(service_url)
    time.sleep(3)

    result = {"triggers": [], "actions": [], "queries": []}
    try:
        triggers = driver.find_elements(By.CSS_SELECTOR, "a[href*='/triggers/']")
        actions = driver.find_elements(By.CSS_SELECTOR, "a[href*='/actions/']")
        queries = driver.find_elements(By.CSS_SELECTOR, "a[href*='/queries/']")
      
        result["triggers"] = list({el.get_attribute("href") for el in triggers})
        result["actions"] = list({el.get_attribute("href") for el in actions})
        result["queries"] = list({el.get_attribute("href") for el in queries})
    except Exception as e:
        print("Errore estraendo trigger/actions/queries:", e)
    finally:
        driver.quit()
    return result



def extract_trigger_details(url):
    driver = start_browser()
    driver.get(trigger_url)
    time.sleep(3)

    data = []

    try:
        sections = driver.find_elements(By.TAG_NAME, "section")
        for section in sections:
            try:
                # Prova a prendere l'h3, se non c'è, usa stringa vuota
                h3_elements = section.find_elements(By.TAG_NAME, "h3")
                section_title = h3_elements[0].text.strip() if h3_elements else ""

                divs = section.find_elements(By.TAG_NAME, "div")
                for div in divs:
                    try:
                        title_element = div.find_element(By.TAG_NAME, "h4")
                        title = title_element.text.strip()
                        # Optional: descrizione se presente
                        try:
                            description = div.find_element(By.CLASS_NAME, "type-definition").text.strip()
                        except:
                            description = ""

                        # Cerca elementi <dl> se presenti
                        dl = div.find_element(By.TAG_NAME, "dl")
                        dt_elements = dl.find_elements(By.TAG_NAME, "dt")
                        dd_elements = dl.find_elements(By.TAG_NAME, "dd")

                        details = {dt.text.strip(): dd.text.strip() for dt, dd in zip(dt_elements, dd_elements)}

                        data.append({
                            "section": section_title,
                            "title": title,
                            "description": description,
                            "details": details
                        })
                    except:
                        continue
            except:
                continue
    finally:
        driver.quit()

    return data

   


# === MAIN ===
if __name__ == "__main__":
    print("Estrazione automatica dei servizi IFTTT...")
    services = extract_all_services()
    print(f"Servizi:")
    for name, link in services:
        print(f" - {name}: {link}")  
    print(f"Servizi trovati: {len(services)}")

    while True:
        user_input = input("\nScrivi un servizio da cercare (o 'exit'): ").strip().lower()
        if user_input == "exit":
            break

        # Trova servizi che contengono il testo cercato
        matching_services = [(name, link) for name, link in services if user_input in name.lower()]

        if not matching_services:
            print(" Nessun servizio trovato.")
            continue

        # Stampa i match trovati
        print(f"\nServizi trovati per '{user_input}':")
        for idx, (name, link) in enumerate(matching_services):
            print(f" [{idx}] {name} -> {link}")

        # Lascia scegliere un servizio da cui estrarre trigger/action
        selected = input("\n Inserisci l'indice del servizio da aprire (o invio per saltare): ").strip()
        if not selected.isdigit() or int(selected) >= len(matching_services):
            print("Salto...")
            continue

        _, selected_url = matching_services[int(selected)]
        print(f"\nCarico: {selected_url}")

        ta = get_triggers_actions(selected_url)

        print("\nTrigger:")
        for idx, t in enumerate(ta["triggers"]):
            print(f" [{idx}]  {t}")

        print("\n⚡ Actions:")
        for idx,a in enumerate(ta["actions"]):
            print(f" [{idx}] {a}")

        for idx, t in enumerate(ta["triggers"]):
            choice = input("\n👉 Vuoi aprire un trigger? Inserisci numero (o invio per saltare): ").strip()
            if choice.isdigit():
                index = int(choice)
                if 0 <= index < len(ta["triggers"]):
                    trigger_url = ta["triggers"][index]
                    data = extract_trigger_details(trigger_url)
                    for item in data:
                        print(f"\nSezione: {item['section']}")
                        print(f" Titolo: {item['title']}")
                        print(f" Descrizione: {item['description']}")
                        print(" Dettagli:")
                        for key, value in item['details'].items():
                            print(f"  - {key}: {value}")


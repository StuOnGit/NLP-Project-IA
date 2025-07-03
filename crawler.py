from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time

API_TITLE = "Developer info"

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
        channel = card.get_attribute("aria-label") or card.text.strip()
        link = card.get_attribute("href")
        if channel and link:
            services.append((channel, link))

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



def extract_detail_data(url):
    driver = start_browser()
    driver.get(url)
    time.sleep(3)

    data = []
    developer_info = {}
    
    try:
        sections = driver.find_elements(By.TAG_NAME, "section")
        for section in sections:
            try:
                h3_elements = section.find_elements(By.TAG_NAME, "h3")
                section_title = h3_elements[0].text.strip() if h3_elements else ""

                # Estrai developer_info UNA SOLA VOLTA
                if not developer_info:
                    h4_elements = section.find_elements(By.TAG_NAME, "h4")
                    for h4 in h4_elements:
                        if h4.text.strip() == API_TITLE:
                            dl_elements = section.find_elements(By.TAG_NAME, "dl")
                            for dl in dl_elements:
                                dt_elements = dl.find_elements(By.TAG_NAME, "dt")
                                dd_elements = dl.find_elements(By.TAG_NAME, "dd")
                                for dt, dd in zip(dt_elements, dd_elements):
                                    developer_info[dt.text.strip()] = dd.text.strip()

                divs = section.find_elements(By.TAG_NAME, "div")
                for div in divs:
                    try:
                        title_element = div.find_element(By.TAG_NAME, "h4") or ""
                        title = title_element.text.strip()
                        try:
                            description = div.find_element(By.CLASS_NAME, "type-definition").text.strip()
                        except:
                            description = ""

                        details = {}
                        dl_elements = div.find_elements(By.TAG_NAME, "dl")
                        for dl in dl_elements:
                            dt_elements = dl.find_elements(By.TAG_NAME, "dt")
                            dd_elements = dl.find_elements(By.TAG_NAME, "dd")
                            for dt, dd in zip(dt_elements, dd_elements):
                                details[dt.text.strip()] = dd.text.strip()

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
    return developer_info, data

   
def format_and_copy(dev_info, details, selected_channel):
    
    
    lines = []
    lines.append(f"Servizio: {selected_channel}")
    lines.append("")
    lines.append("Developer info:")

    for k, v in dev_info.items():
        lines.append(f"  {k}: {v}")
    lines.append("")  # Riga vuota

    for i, entry in enumerate(details, 1):
        lines.append(f"Elemento {i}:")
        for key in sorted(entry.keys()):
            lines.append(f"  {key}: {entry[key]}")
        lines.append("")  # Riga vuota tra elementi
    formatted = "\n".join(lines)
    print("Dettagli estratti e copiati negli appunti:\n")
    print(formatted)
    return formatted

# === MAIN ===
def get_info_service():
    """Funzione principale per estrarre e visualizzare i servizi IFTTT"""
    print("Estrazione automatica dei servizi IFTTT...")
    services = extract_all_services()
    print(f"Servizi:")
    for channel, link in services:
        print(f" - {channel}: {link}")  
    print(f"Servizi trovati: {len(services)}")

    while True:
        user_input = input("\nScrivi un servizio da cercare (o 'exit'): ").strip().lower()
        if user_input == "exit":
            break

        # Trova servizi che contengono il testo cercato
        matching_services = [(channel, link) for channel, link in services if user_input in channel.lower()]

        if not matching_services:
            print(" Nessun servizio trovato.")
            continue

        # Stampa i match trovati
        print(f"\nServizi trovati per '{user_input}':")
        for idx, (channel, link) in enumerate(matching_services):
            print(f" [{idx}] {channel} -> {link}")

        # Lascia scegliere un servizio da cui estrarre trigger/action
        selected = input("\n Inserisci l'indice del servizio da aprire (o invio per saltare): ").strip()
        if not selected.isdigit() or int(selected) >= len(matching_services):
            print("Salto...")
            continue

        _, selected_url = matching_services[int(selected)]
        selected_channel = matching_services[int(selected)][0]  # Prendi il nome del servizio
        print(f"\nCarico: {selected_url}")

        ta = get_triggers_actions_queries(selected_url)

        all_links = []
        i = 0
        print("\nTrigger:")
        for idx, t in enumerate(ta["triggers"]):
            print(f" [{i}]  [{idx}]{t}")
            all_links.append(t)
            i += 1

        print("\nActions:")
        for idx,a in enumerate(ta["actions"]):
            print(f" [{i}] [{idx}]{a}")
            all_links.append(a)
            i += 1

        print("\nQueries:")
        for idx,q in enumerate(ta["queries"]):
            print(f" [{i}] [{idx}]{q}")
            all_links.append(q)
            i += 1

        sel = int(input("\nInserisci l'indice del link da aprire (o invio per saltare): ").strip())
        if sel >= 0 or sel <= len(all_links):
            detail_url = all_links[sel]
            print(f"Estrazione dettagli da: {detail_url}")
            developer_info, details = extract_detail_data(detail_url)
            format_and_copy(developer_info, details, selected_channel)

            print("\n\nDettagli estratti:")
            output = {
                "service_name": selected_channel,
                "developer_info": developer_info,
                "details": details
            }
            print(output)
            return output
           
        else:
            print("Indice non valido, salto...")
        

if __name__ == "__main__":
    try:
        get_info_service()
    except Exception as e:
        print(f"Errore durante l'esecuzione: {e}")

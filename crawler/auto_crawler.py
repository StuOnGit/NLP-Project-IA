from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
import ast
import json
import pandas as pd
import re
from difflib import SequenceMatcher

API_TITLE = "Developer info"
FILE_CSV = "Step1_Raw_Data_with_FilterCode1.csv"
OUTPUT_PATH = "data/generated_prompt_data.json"
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
def get_info_service(samples=1000,file_csv=FILE_CSV):
    correct = 0
    """Funzione principale per estrarre e visualizzare i servizi IFTTT"""
    print("Estrazione automatica dei servizi IFTTT...")
    services = extract_all_services()
    print(f"Servizi:")
    for channel, link in services:
        print(f" - {channel}: {link}")  
    print(f"Servizi trovati: {len(services)}")

    prompt_data = []

    for iteration in range( samples ):

        # prende la riga all'indice i del file csv e controlla se il secondo campo è true o false
        if os.path.exists(file_csv):
            df = pd.read_csv(file_csv)
            if iteration >= len(df):
                print(f"Indice {iteration} fuori dai limiti del file CSV, salto...")
                continue
            row = df.iloc[iteration]
            if not row.get("by_service_owner", False) or str(row.get("by_service_owner", "")).lower() not in ["true", "1"]:
                print(f"Riga {iteration} non valida, salto...")
                continue

        print(f"\n--- Iterazione {iteration}/{samples} ---")

        # se ritorna none la funzione skippa il for
        trigger = check_trigger_action(row, iteration, services, type="trigger")
        if  trigger == None:
            print(f"Riga {iteration} non valida, salto...")
            continue
        action = check_trigger_action(row, iteration, services, type="action")
        if  action == None:
            print(f"Riga {iteration} non valida, salto...")
            continue
        


        print(trigger)
        print(action)
        
        entry = {
            "original_description": row.get("description", ""),
            "trigger_channel": trigger.get("service_name", ""),
            "trigger_permission_id": trigger.get("permission_id", ""),
            "trigger_developer_info": trigger.get("developer_info", {}),
            "trigger_details": trigger.get("details", []),
            "action_channel": action.get("service_name", ""),
            "action_permission_id": action.get("permission_id", ""),
            "action_developer_info": action.get("developer_info", {}),
            "action_details": action.get("details", []),
            "filter_code": row.get("filter_code", "")
        }
        prompt_data.append(entry)
        correct += 1
        
        

    return correct, prompt_data
            
def similar(a, b, threshold=0.7):
    """Restituisce True se le due stringhe sono simili oltre la soglia."""
    return SequenceMatcher(None, a, b).ratio() >= threshold

def extract_core_path(path):
    """Estrae la parte finale significativa di una path tipo /triggers/xxx o /actions/xxx"""
    # Prende solo la parte dopo l'ultimo slash
    return path.strip("/").split("/")[-1].lower()

def check_trigger_action(row, num_row, services, type="trigger" or "action"):
    output = None
    try:
        idx = 0 if type == "trigger" else 1

        channels = row.get("channels", [])
        permissions = row.get("permissions", [])

        # Parsing sicuro se sono stringhe
        if isinstance(channels, str):
            channels = ast.literal_eval(channels)
        if isinstance(permissions, str):
            permissions = ast.literal_eval(permissions)

        if len(channels) <= idx or len(permissions) <= idx:
            print(f"Riga {num_row}: non ci sono abbastanza elementi in channels o permissions.")
            return None

        channel_name = channels[idx].get("name", "")
        permission_id = permissions[idx].get("id", "")

        matched_service = [(c, l) for c, l in services if channel_name.lower() in c.lower()]
        if not matched_service:
            print(f"Riga {num_row}: canale '{channel_name}' non trovato nei servizi.")
            return None

        selected_channel, selected_url = matched_service[0]
        if not selected_url:
            print(f"Riga {num_row}: URL del canale '{selected_channel}' non trovato.")
            return None
        print(f"Carico: {selected_url}")
        ta = get_triggers_actions_queries(selected_url)
        if not ta:
            print(f"Riga {num_row}: Nessun trigger/action trovato per il canale '{selected_channel}'.")
            return None
        key = "triggers" if type == "trigger" else "actions"
        found = False

        perm_core = extract_core_path(permission_id)
        for url in ta.get(key, []):
            url_core = extract_core_path(url)
            # Confronto fuzzy
            if similar(perm_core, url_core, threshold=0.7) or perm_core in url_core or url_core in perm_core:
                print(f"Trovato {type} con permission_id '{permission_id}' (core: '{perm_core}') in {url} (core: '{url_core}')")
                print(f"Estrazione dettagli da: {url}")
                developer_info, details = extract_detail_data(url)
                format_and_copy(developer_info, details, selected_channel)
                print("\n\nDettagli estratti:")
                output = {
                    "service_name": selected_channel,
                    "developer_info": developer_info,
                    "details": details
                    }
                print(output)
                
                found = True
                break
        if not found:
            print(f"{type.capitalize()} con permission_id '{permission_id}' non trovato nei {key} di {selected_url}")
            return None


        return output

    except Exception as e:
        print(f"Errore durante l'elaborazione della riga {num_row} per il tipo '{type}': {e}")
        return None
        # ora apre il servizio scelto
    

if __name__ == "__main__":
    try:
        correct, prompt_data = get_info_service(1000)
        if correct is not None:
            print(f"Correct number of rows are : {correct}")
            # salvalo su output.txt
            with open("output.txt", "w") as f:
                f.write(str(correct))
            os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
            with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
                json.dump(prompt_data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Errore durante l'esecuzione: {e}")

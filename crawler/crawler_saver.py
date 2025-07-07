from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.firefox import GeckoDriverManager
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import json
import math
import os

def start_browser():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    return webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=options)

def extract_all_services():
    driver = start_browser()
    driver.get("https://ifttt.com/explore/services")
    time.sleep(4)
    service_cards = driver.find_elements(By.CSS_SELECTOR, "a[class*='service-card']")
    services = []
    for card in service_cards:
        name = card.get_attribute("aria-label") or card.text.strip()
        link = card.get_attribute("href")
        if name and link:
            services.append((name, link))
    driver.quit()
    return services

def extract_category(service_url, category):
    driver = start_browser()
    driver.get(service_url)
    time.sleep(3)
    urls = []
    try:
        elements = driver.find_elements(By.CSS_SELECTOR, f"a[href*='/{category}/']")
        urls = list({el.get_attribute("href") for el in elements})
    except Exception as e:
        print(f"Errore estraendo {category} da {service_url}: {e}")
    finally:
        driver.quit()
    return urls

def get_triggers_actions_queries(service_url):
    results = {}
    for cat in ['triggers', 'actions', 'queries']:
        results[cat] = extract_category(service_url, cat)
    return results

def extract_service_data(service_tuple):
    name, url = service_tuple
    print(f"[START] Processing service: {name}")
    data = {"triggers": [], "actions": [], "queries": []}
    try:
        items = get_triggers_actions_queries(url)
        data.update(items)
    except Exception as e:
        print(f"Errore elaborando servizio {name}: {e}")
    print(f"[DONE] Finished service: {name}")
    return (name, data)

def chunk_list(lst, n):
    """Divide la lista lst in n chunk quasi uguali"""
    k, m = divmod(len(lst), n)
    return (lst[i*k + min(i, m):(i+1)*k + min(i+1, m)] for i in range(n))

if __name__ == "__main__":
    print("Estrazione servizi IFTTT...")
    services = extract_all_services()
    print(f"Trovati {len(services)} servizi.")

    max_threads = 5  # o metti da input o config
    num_threads = min(max_threads, len(services))
    print(f"Avvio elaborazione in parallelo con {num_threads} thread...")

    all_results = {}

    # Chunk services per thread
    service_chunks = list(chunk_list(services, num_threads))

    def process_chunk(chunk):
        chunk_results = {}
        for svc in chunk:
            name, data = extract_service_data(svc)
            chunk_results[name] = data
        return chunk_results

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(process_chunk, chunk) for chunk in service_chunks]
        for future in as_completed(futures):
            result = future.result()
            all_results.update(result)

    # Salvataggio dati
    os.makedirs("data", exist_ok=True)
    with open("data/ifttt_services_parallel.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)

    print("Estrazione completata. Dati salvati in 'data/ifttt_services_parallel.json'")

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time


def start_headless_browser():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


def fetch_services_with_selenium():
    driver = start_headless_browser()
    driver.get("https://ifttt.com/services")

    # Attendi che la pagina carichi dinamicamente i servizi
    time.sleep(5)

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


if __name__ == "__main__":
    services = fetch_services_with_selenium()
    print(f"Trovati {len(services)} servizi:\n")
    for name, link in services:  
        print(f"- {name}: {link}")

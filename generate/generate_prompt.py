import pandas as pd
import json
import os
import random
import re
from crawler.crawler import get_info_service

DATASET_PATH = "Step1_Raw_Data_with_FilterCode1.csv"
OUTPUT_PATH = "data/generated_prompt_data.json"
SAMPLES = 2


def clean_string(s):
    if not isinstance(s, str):
        return ""
    return re.sub(r'[\n\r\t]+', ' ', s).strip()


def parse_crawler_output(crawler_output):
    """
    Parse the output from get_info_service():
    crawler_output: tuple (dict_info, list_ingredients)
    
    Returns:
        slug (str or None)
        parsed_ingredients (list of dict)
    """
    if not crawler_output or not isinstance(crawler_output, tuple) or len(crawler_output) != 2:
        return None, []

    info_dict, ingredients_list = crawler_output
    slug = info_dict.get('API endpoint slug', None)

    parsed_ingredients = []
    for item in ingredients_list:
        parsed_ingredients.append({
            'section': item.get('section', ''),
            'title': item.get('title', ''),
            'description': item.get('description', ''),
            'details': item.get('details', {})
        })

    return slug, parsed_ingredients


def main():
    if not os.path.exists(DATASET_PATH):
        print(f"Dataset non trovato: {DATASET_PATH}")
        return

    df = pd.read_csv(DATASET_PATH)
    df = df.sample(n=SAMPLES, random_state=42).reset_index(drop=True)
    prompt_data = []

    for idx, row in df.iterrows():
        print(f"\n[{idx+1}/{SAMPLES}] Regola: {clean_string(row.get('description', ''))[:60]}...")

        filter_code = clean_string(row.get("filter_code") or "")
        original_description = clean_string(row.get("description") or "")

        # --- TRIGGER ---
        print("\n--- TRIGGER ---")
        trigger_output = get_info_service()  # L'utente seleziona il servizio trigger
        if not trigger_output:
            print("Nessun output dal crawler per il trigger.")
            continue
        trigger_channel = trigger_output.get("service_name", "")
        trigger_slug, trigger_fields = parse_crawler_output((trigger_output.get("developer_info", {}), trigger_output.get("details", [])))
        print(f"Trigger channel: {trigger_channel}")
        print(f"Trigger slug: {trigger_slug}")

        # --- ACTION ---
        print("\n--- ACTION ---")
        action_output = get_info_service()  # L'utente seleziona il servizio action
        if not action_output:
            print("Nessun output dal crawler per l'action.")
            continue
        action_channel = action_output.get("service_name", "")
        action_slug, action_fields = parse_crawler_output((action_output.get("developer_info", {}), action_output.get("details", [])))
        print(f"Action channel: {action_channel}")
        print(f"Action slug: {action_slug}")

        entry = {
            "original_description": original_description,
            "trigger_channel": trigger_channel,
            "trigger_slug": trigger_slug,
            "trigger_fields": trigger_fields,
            "action_channel": action_channel,
            "action_slug": action_slug,
            "action_fields": action_fields,
            "filter_code": filter_code
        }
        prompt_data.append(entry)

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(prompt_data, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Dati salvati in {OUTPUT_PATH}")


if __name__ == "__main__":
    main()

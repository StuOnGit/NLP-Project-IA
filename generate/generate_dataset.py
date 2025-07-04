import os
import json
import ast
import pandas as pd
from crawler.crawler import get_info_service
from generate.generate_prompt import clean_string, parse_crawler_output

DATASET_PATH = "Step1_Raw_Data_with_FilterCode1.csv"
SAMPLES = 1000

OUTPUT_PATH = "data/TRY_prompt_data.json"


def main():
    if not os.path.exists(DATASET_PATH):
        print(f"Dataset non trovato: {DATASET_PATH}")
        return

    df = pd.read_csv(DATASET_PATH)
    df = df.sample(n=SAMPLES, random_state=42).reset_index(drop=True)
    prompt_data = []

    for idx, row in df.iterrows():
        print(f"\n[{idx+1}/{SAMPLES}] Regola: {clean_string(row.get('description', ''))[:60]}...")

        # 1. Controlla by_service_owner
        by_service_owner = row.get("by_service_owner", False)
        if not by_service_owner or str(by_service_owner).lower() not in ["true", "1"]:
            print("by_service_owner non vero, salto.")
            continue

        # 2. Parsing colonne channels e permissions con ast.literal_eval
        try:
            channels = ast.literal_eval(row.get("channels", "[]"))
            permissions = ast.literal_eval(row.get("permissions", "[]"))
        except Exception as e:
            print(f"Errore parsing colonne channels/permissions: {e}")
            continue

        if len(channels) < 2 or len(permissions) < 2:
            print("Meno di due elementi in channels o permissions, salto.")
            continue

        # --- TRIGGER ---
        trigger_name = channels[0].get("name", "")
        trigger_permission_id = permissions[0].get("id", "")
        print(f"\n--- TRIGGER: {trigger_name} ---")
        trigger_output = get_info_service()  # L'utente seleziona il servizio trigger
        if not trigger_output or trigger_output.get("service_name", "").lower() != trigger_name.lower():
            print("Il servizio trigger selezionato non corrisponde al nome richiesto.")
            continue

        # Cerca se l'id è presente nei dettagli del trigger
        _, trigger_details = parse_crawler_output((trigger_output.get("developer_info", {}), trigger_output.get("details", [])))
        found_trigger_id = any(
            trigger_permission_id == v
            for entry in trigger_details
            for v in entry.get("details", {}).values()
        )
        if not found_trigger_id:
            print(f"ID trigger '{trigger_permission_id}' non trovato nei dettagli.")
            continue

        # --- ACTION ---
        action_name = channels[1].get("name", "")
        action_permission_id = permissions[1].get("id", "")
        print(f"\n--- ACTION: {action_name} ---")
        action_output = get_info_service()  # L'utente seleziona il servizio action
        if not action_output or action_output.get("service_name", "").lower() != action_name.lower():
            print("Il servizio action selezionato non corrisponde al nome richiesto.")
            continue

        _, action_details = parse_crawler_output((action_output.get("developer_info", {}), action_output.get("details", [])))
        found_action_id = any(
            action_permission_id == v
            for entry in action_details
            for v in entry.get("details", {}).values()
        )
        if not found_action_id:
            print(f"ID action '{action_permission_id}' non trovato nei dettagli.")
            continue

        # --- Se tutto corrisponde, salva ---
        filter_code = clean_string(row.get("filter_code") or "")
        original_description = clean_string(row.get("description") or "")
        trigger_channel = trigger_output.get("service_name", "")
        trigger_slug, trigger_fields = parse_crawler_output((trigger_output.get("developer_info", {}), trigger_output.get("details", [])))
        action_channel = action_output.get("service_name", "")
        action_slug, action_fields = parse_crawler_output((action_output.get("developer_info", {}), action_output.get("details", [])))

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
import json
import os

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
input_path = f"{base_dir}/output/generated_filtercode_from_intent_1-547_300_validate.jsonl"
output_path = f"{base_dir}/output/1-300_intent_filtercode_only.jsonl"
output_json = f"{base_dir}/output/1-300_intent_filtercode_only.json"

# Estrai solo intent e filter_code
with open(input_path, "r", encoding="utf-8") as fin, open(output_path, "w", encoding="utf-8") as fout:
    for line in fin:
        if line.strip():
            obj = json.loads(line)
            filtered = {
                "intent": obj.get("intent"),
                "filter_code": obj.get("filter_code")
            }
            fout.write(json.dumps(filtered, ensure_ascii=False) + "\n")

# Converte il file .jsonl in un file .json (lista di dict)
with open(output_path, "r", encoding="utf-8") as fin, open(output_json, "w", encoding="utf-8") as fout:
    data = [json.loads(line) for line in fin if line.strip()]
    json.dump(data, fout, ensure_ascii=False, indent=2)

print(f"File creato: {output_path}")
print(f"File JSON creato: {output_json}")

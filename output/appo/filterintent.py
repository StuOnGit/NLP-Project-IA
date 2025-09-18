import json
import os

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
input_path = f"{base_dir}/output/1-300 controllate e 200 validate.jsonl"
output_path = f"{base_dir}/output/1-300_controllate_e_200_validate_onlydesc_intent.jsonl"

with open(input_path, "r", encoding="utf-8") as fin, open(output_path, "w", encoding="utf-8") as fout:
    for line in fin:
        if line.strip():
            obj = json.loads(line)
            filtered = {
                "original_description": obj.get("original_description"),
                "intent": obj.get("intent")
            }
            fout.write(json.dumps(filtered, ensure_ascii=False) + "\n")

print(f"File creato: {output_path}")


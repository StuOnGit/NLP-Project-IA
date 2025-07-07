import json
import os

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

input_path = f"{base_dir}/data/generated_prompt_data.json"
output_path = f"{base_dir}/data/generated_prompt_data2.jsonl"

with open(input_path, "r", encoding="utf-8") as f:
    data = json.load(f)

with open(output_path, "w", encoding="utf-8") as f_out:
    for item in data:
        f_out.write(json.dumps(item, ensure_ascii=False) + "\n")

print(f"Creato file JSONL: {output_path}")

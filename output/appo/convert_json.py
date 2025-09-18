import json
import os
import argparse
import sys

def json_to_jsonl(input_path, output_path):
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    with open(output_path, "w", encoding="utf-8") as f_out:
        for item in data:
            f_out.write(json.dumps(item, ensure_ascii=False) + "\n")
    print(f"Creato file JSONL: {output_path}")

def jsonl_to_json(input_path, output_path):
    data = []
    with open(input_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                data.append(json.loads(line))
    with open(output_path, "w", encoding="utf-8") as f_out:
        json.dump(data, f_out, ensure_ascii=False, indent=2)
    print(f"Creato file JSON: {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Converti tra JSON e JSONL")
    parser.add_argument("--to-jsonl", action="store_true", help="Converti da JSON a JSONL")
    parser.add_argument("--to-json", action="store_true", help="Converti da JSONL a JSON")
    parser.add_argument("--input", type=str, help="Percorso file di input (opzionale)")
    parser.add_argument("--output", type=str, help="Percorso file di output (opzionale)")
    args = parser.parse_args()

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    default_json = f"{base_dir}/generated_prompt_data_step1234.json"
    default_jsonl = f"{base_dir}/output/generated_prompt_data_step1234.jsonl"

    if args.to_jsonl:
        input_path = args.input or default_json
        output_path = args.output or default_jsonl
        json_to_jsonl(input_path, output_path)
    elif args.to_json:
        input_path = args.input or default_jsonl
        output_path = args.output or (default_json.replace(".json", "_from_jsonl.json"))
        jsonl_to_json(input_path, output_path)
    else:
        print("Specifica --to-jsonl o --to-json")
        sys.exit(1)

if __name__ == "__main__":
    main()
import json
import os

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
input_path = f"{base_dir}/output/generated_filtercode_from_intent_547-1752.jsonl"
output_jsonl = f"{base_dir}/output/547-1752_intent_filtercode_only_func.jsonl"
output_json = f"{base_dir}/output/547-1752_intent_filtercode_only_func.json"
output_txt = f"{base_dir}/output/547-1752_filtercode_only_func.txt"

# Estrai solo intent e filter_code
with open(input_path, "r", encoding="utf-8") as fin, open(output_jsonl, "w", encoding="utf-8") as fout:
    for line in fin:
        if line.strip():
            obj = json.loads(line)
            filtered = {
                "intent": obj.get("intent"),
                "filter_code": obj.get("filter_code"),
                # "trigger_developer_info": obj.get("trigger_developer_info"),
                # "action_developer_info": obj.get("action_developer_info")
            }
            fout.write(json.dumps(filtered, ensure_ascii=False) + "\n")



# Converte il file .jsonl in un file .json (lista di dict) e formatta filter_code
def format_filter_code(code):
    if not code:
        return code
    lines = code.splitlines()
    formatted = '\n'.join(line.rstrip() for line in lines)
    return formatted

data = []
filtercode_list = []
with open(output_jsonl, "r", encoding="utf-8") as fin:
    for line in fin:
        if line.strip():
            obj = json.loads(line)
            # Format filter_code
            if "filter_code" in obj and obj["filter_code"]:
                obj["filter_code"] = format_filter_code(obj["filter_code"])
                filtercode_list.append(obj["filter_code"])
            data.append(obj)

with open(output_json, "w", encoding="utf-8") as fout:
    json.dump(data, fout, ensure_ascii=False, indent=2)


# Scrivi intent e filter_code formattati in un file txt, separati da una riga vuota
with open(output_txt, "w", encoding="utf-8") as ftxt:
    for obj in data:
        intent = obj.get("intent", "")
        filter_code = obj.get("filter_code", "")
        trigger_info = json.dumps(obj.get("trigger_developer_info", {}), ensure_ascii=False, indent=2)
        action_info = json.dumps(obj.get("action_developer_info", {}), ensure_ascii=False, indent=2)
        ftxt.write(
            "=== INTENT ===\n" + intent +
            # "\n\n=== TRIGGER_DEVELOPER_INFO ===\n" + trigger_info +
            # "\n\n=== ACTION_DEVELOPER_INFO ===\n" + action_info +
            "\n\n=== FILTERCODE ===\n" + filter_code +
            "\n\n---\n\n"
        )

print(f"File creato: {output_jsonl}")
print(f"File JSON creato: {output_json}")
print(f"File TXT creato: {output_txt}")

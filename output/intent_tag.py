import json
import os

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
file1 = os.path.join(base_dir, "output", "generated_intent_output_1-547.jsonl")
file2 = os.path.join(base_dir, "output", "finali", "generated_intent_1-547_300_validate_llama3.jsonl")
# output_file = os.path.join(base_dir, "output", "finali", "intent_tagged_1-547.json")
output_jsonl = os.path.join(base_dir, "output", "finali", "intent_tagged_1-547.jsonl")
output_nonvalid = os.path.join(base_dir, "output", "finali", "intent_nonvalid_in_file2.jsonl")

def load_jsonl(path):
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]

data1 = load_jsonl(file1)
data2 = load_jsonl(file2)

# Per confronto, usiamo la stringa json normalizzata

def obj_to_str(obj):
    return json.dumps(obj, sort_keys=True, ensure_ascii=False)

strs1 = set(obj_to_str(obj) for obj in data1)
strs2 = set(obj_to_str(obj) for obj in data2)

result = []
# Mantieni l'ordine e la struttura delle righe di input
for obj in data1:
    obj_str = obj_to_str(obj)
    valid = obj_str in strs2
    new_obj = {"valid": valid}
    new_obj.update(obj)
    result.append(new_obj)

nonvalid_in_file2 = []
for obj in data2:
    obj_str = obj_to_str(obj)
    if obj_str not in strs1:
        new_obj = {"valid": False}
        new_obj.update(obj)
        result.append(new_obj)
        nonvalid_in_file2.append(obj)

# with open(output_file, "w", encoding="utf-8") as fout:
#     json.dump(result, fout, ensure_ascii=False, indent=2)

# Scrivi il file JSONL

with open(output_jsonl, "w", encoding="utf-8") as fout:
    for obj in result:
        fout.write(json.dumps(obj, ensure_ascii=False) + "\n")

# Scrivi il file delle righe non valide di file1 contenute in file2
with open(output_nonvalid, "w", encoding="utf-8") as fout:
    for obj in nonvalid_in_file2:
        fout.write(json.dumps(obj, ensure_ascii=False) + "\n")

valid_count = sum(1 for r in result if r["valid"])
not_valid_count = len(result) - valid_count
# print(f"File creato: {output_file}")
print(f"File creato: {output_jsonl}")
print(f"File creato: {output_nonvalid}")
print(f"Validi: {valid_count}")
print(f"Non validi: {not_valid_count}")

import json
import os

filepath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

file1 = f"{filepath}fullraw_dup.jsonl"
file2 = f"{filepath}generated_prompt_data_step1234.jsonl"
output_file = f"{filepath}generated_prompt_data_step1234_fin.jsonl"

def load_jsonl(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return [json.loads(line.strip()) for line in f if line.strip()]

def check_duplicates_between_files():
    data1 = load_jsonl(file1)
    data2 = load_jsonl(file2)
    set1 = set(json.dumps(obj, sort_keys=True) for obj in data1)
    set2 = set(json.dumps(obj, sort_keys=True) for obj in data2)
    duplicates = set1 & set2

    print(f"Numero di duplicati trovati tra i due file: {len(duplicates)}\n")

    ix = 1
    for dup in duplicates:
        obj = json.loads(dup)
        idx1 = [i+1 for i, x in enumerate(data1) if json.dumps(x, sort_keys=True) == dup]
        idx2 = [i+1 for i, x in enumerate(data2) if json.dumps(x, sort_keys=True) == dup]
        print(f"Duplicato {ix} trovato alle righe file1: {idx1}, file2: {idx2} (totale occorrenze: {len(idx1) + len(idx2)})")
        ix += 1
        print("-" * 60)

    crea_file = input("Vuoi creare il file merged senza duplicati? (s/n): ").strip().lower()
    if crea_file == "s":
        # Unione senza duplicati
        unique_json = {}
        for obj in data1 + data2:
            key = json.dumps(obj, sort_keys=True)
            unique_json[key] = obj

        print(f"Totale righe uniche: {len(unique_json)}")

        with open(output_file, "w", encoding="utf-8") as f_out:
            for obj in unique_json.values():
                f_out.write(json.dumps(obj, ensure_ascii=False) + "\n")

        print(f"File unificato senza duplicati salvato in: {output_file}")
    else:
        print("File merged non creato.")

def check_duplicates_in_file1():
    # Scansiona tutti i file .jsonl nella cartella output
    output_dir = os.path.join(filepath, "output")
    jsonl_files = [f for f in os.listdir(output_dir) if f.endswith('.jsonl')]
    if not jsonl_files:
        print("Nessun file .jsonl trovato nella cartella output.")
        return
    for fname in jsonl_files:
        full_path = os.path.join(output_dir, fname)
        data = load_jsonl(full_path)
        seen = {}
        for idx, obj in enumerate(data):
            key = json.dumps(obj, sort_keys=True)
            if key not in seen:
                seen[key] = []
            seen[key].append(idx)
        duplicates = {k: v for k, v in seen.items() if len(v) > 1}
        print(f"File: {fname}")
        print(f"  Numero di righe totali: {len(data)}")
        print(f"  Numero di righe duplicate: {len(duplicates)}")
        if duplicates:
            ix = 1
            for k, idxs in duplicates.items():
                idxs_plus1 = [i+1 for i in idxs]
                print(f"    Duplicato {ix} alle righe: {idxs_plus1} (totale occorrenze: {len(idxs)})")
                ix += 1
            print("  -" * 30)
            crea_file = input(f"Vuoi creare il file {fname.replace('.jsonl', '')}_nodup.jsonl senza duplicati? (s/n): ").strip().lower()
            if crea_file == "s":
                unique_json = {}
                for obj in data:
                    key = json.dumps(obj, sort_keys=True)
                    unique_json[key] = obj
                output_nodup = os.path.join(output_dir, f"{fname.replace('.jsonl', '')}_nodup.jsonl")
                with open(output_nodup, "w", encoding="utf-8") as f_out:
                    for obj in unique_json.values():
                        f_out.write(json.dumps(obj, ensure_ascii=False) + "\n")
                print(f"  File senza duplicati creato: {output_nodup}")
        else:
            print("  Nessuna riga duplicata trovata.")
        print()

if __name__ == "__main__":
    print("Scegli modalità:")
    print("1 - Confronta due file e crea file unificato senza duplicati")
    print("2 - Cerca duplicati interni in file1")
    scelta = input("Inserisci 1 o 2: ").strip()
    if scelta == "1":
        check_duplicates_between_files()
    elif scelta == "2":
        check_duplicates_in_file1()
    else:
        print("Scelta non valida.")

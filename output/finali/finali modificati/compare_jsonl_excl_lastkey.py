import json
import os

filepath = os.path.dirname(os.path.abspath(__file__))

def remove_filter_code_old(file_path):
    """
    Rimuove la chiave 'filter_code_old' da ogni riga del file jsonl, se presente, e salva il risultato in un nuovo file.
    """
    out_path = file_path.replace('.jsonl', '_nofiltercodeold.jsonl')
    count = 0
    with open(file_path, 'r', encoding='utf-8') as fin, open(out_path, 'w', encoding='utf-8') as fout:
        for line in fin:
            if not line.strip():
                continue
            obj = json.loads(line)
            if 'filter_code_old' in obj:
                del obj['filter_code_old']
                count += 1
            fout.write(json.dumps(obj, ensure_ascii=False) + '\n')
    print(f"Fatto. Rimosse 'filter_code_old' da {count} righe. File salvato come: {out_path}")


def load_jsonl(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return [json.loads(line.strip()) for line in f if line.strip()]

def compare_jsonl_exclude_last_key(file1, file2):
    with open(file1, 'r', encoding='utf-8') as f1, open(file2, 'r', encoding='utf-8') as f2:
        lines1 = f1.readlines()
        lines2 = f2.readlines()

    if len(lines1) != len(lines2):
        print("I file hanno un numero diverso di righe.")
        return

    for idx, (l1, l2) in enumerate(zip(lines1, lines2), 1):
        d1 = json.loads(l1)
        d2 = json.loads(l2)
        keys1 = list(d1.keys())[:-3] if len(d1) > 3 else []
        keys2 = list(d2.keys())[:-3] if len(d2) > 3 else []
        if keys1 != keys2:
            print(f"Riga {idx}: le chiavi (escluse le ultime 3) non corrispondono.")
            continue
        for k in keys1:
            if d1[k] != d2[k]:
                print(f"Riga {idx}, chiave '{k}': valori diversi -> {d1[k]} != {d2[k]}")
                break
        else:
            continue
    print("Confronto completato.")

def check_duplicates_in_file_exclude_last_key():
    output_dir = filepath
    jsonl_files = [f for f in os.listdir(output_dir) if f.endswith('.jsonl')]
    if not jsonl_files:
        print("Nessun file .jsonl trovato nella cartella di lavoro.")
        return
    print("Scegli il file su cui cercare duplicati (escludendo le ultime 3 chiavi):")
    for i, fname in enumerate(jsonl_files, 1):
        print(f"{i} - {fname}")
    scelta = input("Numero file: ").strip()
    try:
        idx = int(scelta) - 1
        fname = jsonl_files[idx]
    except (ValueError, IndexError):
        print("Scelta non valida.")
        return
    full_path = os.path.join(output_dir, fname)
    data = load_jsonl(full_path)
    seen = {}
    for idx, obj in enumerate(data):
        keys = list(obj.keys())
        if not keys or len(keys) <= 3:
            continue
        obj_excl = {k: obj[k] for k in keys[:-3]}
        key = json.dumps(obj_excl, sort_keys=True)
        if key not in seen:
            seen[key] = []
        seen[key].append(idx)
    duplicates = {k: v for k, v in seen.items() if len(v) > 1}
    print(f"File: {fname}")
    print(f"  Numero di righe totali: {len(data)}")
    print(f"  Numero di righe duplicate (escludendo ultime 3 chiavi): {len(duplicates)}")
    if duplicates:
        ix = 1
        for k, idxs in duplicates.items():
            idxs_plus1 = [i+1 for i in idxs]
            print(f"    Duplicato {ix} alle righe: {idxs_plus1} (totale occorrenze: {len(idxs)})")
            ix += 1
        print("  -" * 30)
        crea_file = input(f"Vuoi creare il file {fname.replace('.jsonl', '')}_nodup_excllast3.jsonl senza questi duplicati? (s/n): ").strip().lower()
        if crea_file == "s":
            unique_json = {}
            for obj in data:
                keys = list(obj.keys())
                if not keys or len(keys) <= 3:
                    continue
                obj_excl = {k: obj[k] for k in keys[:-3]}
                key = json.dumps(obj_excl, sort_keys=True)
                if key not in unique_json:
                    unique_json[key] = obj
            output_nodup = os.path.join(output_dir, f"{fname.replace('.jsonl', '')}_nodup.jsonl")
            with open(output_nodup, "w", encoding="utf-8") as f_out:
                for obj in unique_json.values():
                    f_out.write(json.dumps(obj, ensure_ascii=False) + "\n")
            print(f"  File senza duplicati (escludendo ultime 3 chiavi) creato: {output_nodup}")
    else:
        print("Nessuna riga duplicata trovata (escludendo ultime 3 chiavi).")
        
    print()

def main():
    print("Scegli modalità:")
    print("1 - Confronta due file jsonl escludendo le ultime 3 chiavi")
    print("2 - Cerca duplicati interni in un file escludendo le ultime 3 chiavi")
    print("3 - Trova le righe di un file che non sono nell'altro (confronto completo)")
    print("4 - Rimuovi la chiave 'filter_code_old' da ogni riga di un file jsonl")
    scelta = input("Inserisci 1, 2, 3 o 4: ").strip()
    if scelta == "1":
        output_dir = filepath
        jsonl_files = [f for f in os.listdir(output_dir) if f.endswith('.jsonl')]
        if len(jsonl_files) < 2:
            print("Servono almeno due file .jsonl nella cartella di lavoro.")
            return
        print("Scegli il primo file da confrontare:")
        for i, fname in enumerate(jsonl_files, 1):
            print(f"{i} - {fname}")
        scelta1 = input("Numero file 1: ").strip()
        print("Scegli il secondo file da confrontare:")
        for i, fname in enumerate(jsonl_files, 1):
            print(f"{i} - {fname}")
        scelta2 = input("Numero file 2: ").strip()
        try:
            idx1 = int(scelta1) - 1
            idx2 = int(scelta2) - 1
            fname1 = jsonl_files[idx1]
            fname2 = jsonl_files[idx2]
        except (ValueError, IndexError):
            print("Scelta non valida.")
            return
        file1 = os.path.join(output_dir, fname1)
        file2 = os.path.join(output_dir, fname2)
        compare_jsonl_exclude_last_key(file1, file2)
    elif scelta == "2":
        check_duplicates_in_file_exclude_last_key()
    elif scelta == "3":
        output_dir = filepath
        jsonl_files = [f for f in os.listdir(output_dir) if f.endswith('.jsonl')]
        if len(jsonl_files) < 2:
            print("Servono almeno due file .jsonl nella cartella di lavoro.")
            return
        print("Scegli il primo file da confrontare:")
        for i, fname in enumerate(jsonl_files, 1):
            print(f"{i} - {fname}")
        scelta1 = input("Numero file 1: ").strip()
        print("Scegli il secondo file da confrontare:")
        for i, fname in enumerate(jsonl_files, 1):
            print(f"{i} - {fname}")
        scelta2 = input("Numero file 2: ").strip()
        try:
            idx1 = int(scelta1) - 1
            idx2 = int(scelta2) - 1
            fname1 = jsonl_files[idx1]
            fname2 = jsonl_files[idx2]
        except (ValueError, IndexError):
            print("Scelta non valida.")
            return
        file1 = os.path.join(output_dir, fname1)
        file2 = os.path.join(output_dir, fname2)
        find_rows_not_in_other(file1, file2)
    elif scelta == "4":
        output_dir = filepath
        jsonl_files = [f for f in os.listdir(output_dir) if f.endswith('.jsonl')]
        if not jsonl_files:
            print("Nessun file .jsonl trovato nella cartella di lavoro.")
            return
        print("Scegli il file da processare per rimuovere la chiave 'filter_code_old':")
        for i, fname in enumerate(jsonl_files, 1):
            print(f"{i} - {fname}")
        scelta = input("Numero file: ").strip()
        try:
            idx = int(scelta) - 1
            fname = jsonl_files[idx]
        except (ValueError, IndexError):
            print("Scelta non valida.")
            return
        file_path = os.path.join(output_dir, fname)
        remove_filter_code_old(file_path)
    else:
        print("Scelta non valida.")

def find_rows_not_in_other(file1, file2):
    """
    Trova e stampa le righe (oggetti) che sono in file1 ma non in file2 e viceversa.
    """
    data1 = load_jsonl(file1)
    data2 = load_jsonl(file2)
    def strip_last3(obj):
        keys = list(obj.keys())
        if not keys or len(keys) <= 3:
            return {}
        return {k: obj[k] for k in keys[:-3]}

    str1 = [json.dumps(strip_last3(obj), sort_keys=True) for obj in data1]
    str2 = [json.dumps(strip_last3(obj), sort_keys=True) for obj in data2]
    set2 = set(str2)
    set1 = set(str1)

    only_in_1 = [(i, s) for i, s in enumerate(str1) if s not in set2]
    only_in_2 = [(i, s) for i, s in enumerate(str2) if s not in set1]

    if only_in_1:
        print(f"\nNumero/i di riga presenti solo in {os.path.basename(file1)} (totale: {len(only_in_1)}):")
        for ix, _ in only_in_1:
            print(f"{ix+1}")
    else:
        print(f"\nNessuna riga unica trovata in {os.path.basename(file1)}.")

    if only_in_2:
        print(f"\nNumero/i di riga presenti solo in {os.path.basename(file2)} (totale: {len(only_in_2)}):")
        for ix, _ in only_in_2:
            print(f"{ix+1}")
    else:
        print(f"\nNessuna riga unica trovata in {os.path.basename(file2)}.")

if __name__ == "__main__":
    main()

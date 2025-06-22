import pandas as pd
from pathlib import Path   
import re

# Percorso al file CSV
csv_file_raw = "data/Step1_Raw_Data_with_FilterCode1.csv"
csv_file_populare = "data/Step2_Popular_Rules_with_FilterCode.csv"
csv_file_iot = "data/Step3_IoT_Rules_with_FilterCode.csv"
output_file = "output_token_count.txt"

# Lista dei file CSV
files = [
    csv_file_raw,
    csv_file_populare,
    csv_file_iot
]

token_tables = []
labels = []

for file in files:
    try:
        df = pd.read_csv(file)
        if 'description' not in df.columns:
            print(f"⚠️ Colonna 'description' non trovata in {file}.")
            continue
         # Unisci tutte le descrizioni in un unico testo
        all_text = " ".join(df['description'].dropna().astype(str)).lower()
        # Tokenizza: solo parole di almeno 2 lettere
        tokens = re.findall(r'\b[a-z]{2,}\b', all_text)
        # Conta le occorrenze
        counts = pd.Series(tokens).value_counts()
        print(f"File: {file} - Numero token: {len(tokens)} - Token unici: {len(counts)}")
        token_tables.append(counts.rename(Path(file).name).to_frame())
        labels.append(Path(file).name)
    except Exception as e:
        print(f"⚠️ Errore nella lettura del file {file}: {e}")
    

# Unione delle tabelle
df_merged = pd.concat(token_tables, axis=1).fillna(0).astype(int)
df_merged["totale"] = df_merged.sum(axis=1)
df_merged = df_merged.sort_values("totale", ascending=False)
df_merged.index.name = "token"
df_merged = df_merged.reset_index()

# Salva il risultato
df_merged.to_csv("token_summary.csv", index=False)
print("✅ File salvato: token_summary.csv")

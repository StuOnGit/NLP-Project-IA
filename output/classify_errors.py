import json
import pandas as pd

# Logica di classificazione più sofisticata per riflettere meglio le regole dell'utente.
def classify_error_detailed(item):
    intent = item.get('intent', '').strip()
    original_description = item.get('original_description', '').strip()

    # Categoria 1: Intent vuoto o mancante
    if not intent or intent == '""':
        return 'Incompleto/Vuoto'

    # Categoria 2: Descrizione originale mancante
    if not original_description:
        return 'Descrizione Vuota'

    # Categoria 3: L'intent ripete la descrizione senza aggiungere valore.
    # Euristica migliorata: controlla se l'intent è una semplice parafrasi e non contiene parametri concreti.
    if (original_description.lower() in intent.lower() or intent.lower() in original_description.lower()) and len(intent) < len(original_description) + 30:
        has_numbers = any(char.isdigit() for char in intent)
        has_quotes = '"' in intent or "'" in intent
        if not has_numbers and not has_quotes:
            return 'Ripete Descrizione'

    # Categoria 4: Fallback per errori complessi.
    return 'Logica Fraintesa/Allucinazione'


errors = []
file_path = r'C:\Users\mario\Documents\GitHub\NLP-Project-IA\output\ultimi\intent_tagged_1-547.jsonl'

with open(file_path, 'r', encoding='utf-8') as f:
    for i, line in enumerate(f):
        try:
            data = json.loads(line)
            if not data.get('valid', True):
                error_category = classify_error_detailed(data)
                errors.append({'ID_Esempio': i, 'Categoria_Errore': error_category})
        except json.JSONDecodeError:
            print(f"Skipping invalid JSON on line {i+1}")

df_errors = pd.DataFrame(errors)
output_path = r'C:\Users\mario\Documents\GitHub\NLP-Project-IA\output\error_analysis.csv'
df_errors.to_csv(output_path, index=False)

print(f"Creato file error_analysis.csv con {len(df_errors)} errori, usando una classificazione più dettagliata.")

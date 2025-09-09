import re
import json
import os
from openai import OpenAI
import time
import itertools
from openai.types.chat import ChatCompletionSystemMessageParam,ChatCompletionUserMessageParam

# Leggi il system prompt dal file di testo
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
prompt_path = f"{base_dir}/llm/system_prompt_generate_filtercode_from_intent.txt"
with open(prompt_path, "r", encoding="utf-8") as f_prompt:
  SYSTEM_PROMPT = f_prompt.read()

# Configura il client OpenAI (sostituisci con il modello open source che preferisci)
client = OpenAI(api_key="lmstudio-community/llama-3.3-70b-instruct", base_url="http://127.0.0.1:1234/v1")
MODEL_ID = "llama-3.3-70b"  # Sostituisci con il modello open source più adatto

input_path = f"{base_dir}/output/1-547 controllate e 300 validate.jsonl"
output_path = f"{base_dir}/output/generated_filtercode_from_intent_1-547_300_validate.jsonl"

# Controlla se il file di input esiste
if not os.path.exists(input_path):
    print(f"Errore: Il file di input non esiste: {input_path}")
    exit()

with open(input_path, "r", encoding="utf-8") as f_in, open(output_path, "w", encoding="utf-8") as f_out:
    for idx, line in enumerate(itertools.islice(f_in, 0, 1000)):
        try:
            json_obj = json.loads(line)
        except json.JSONDecodeError:
            print(f"Riga {idx+1}: Errore nel decodificare il JSON. Riga saltata.")
            continue

        # Assicurati che l'intent esista prima di procedere
        if not json_obj.get("intent"):
            print(f"Riga {idx+1}: Campo 'intent' mancante. Riga saltata.")
            continue

        user_prompt = json.dumps(json_obj, ensure_ascii=False)
        messages = [
            ChatCompletionSystemMessageParam(role="system", content=SYSTEM_PROMPT),
            ChatCompletionUserMessageParam(role="user", content=user_prompt)
        ]

        try:
            response = client.chat.completions.create(
                model=MODEL_ID,
                messages=messages,
                stream=False
            )
            content = response.choices[0].message.content
            output = content.strip() if content is not None else ""

            # Estrai FILTERCODE delimitato dai simboli speciali
            filter_code = ""
            filtercode_match = re.search(r'<<<FILTERCODE>>>(.*?)<<<END_FILTERCODE>>>', output, re.DOTALL)

            if filtercode_match:
                filter_code = filtercode_match.group(1).strip()
            else:
                print(f"Riga {idx+1}: Nessun '<<<FILTERCODE>>>' trovato nell'output del modello. L'output era:\n{output}")

            # Gestione logica richiesta per filter_code con eccezione
            if "filter_code" not in json_obj or json_obj["filter_code"] == "":
                # Se filter_code è vuoto o assente
                json_obj["filter_code"] = filter_code
            else:  # Se filter_code NON è vuoto
                json_obj["filter_code_old"] = json_obj["filter_code"]
                json_obj["filter_code"] = filter_code

            f_out.write(json.dumps(json_obj, ensure_ascii=False) + "\n")
            print(f"Riga: {idx+1}\nOutput:\n{output}\n{'*'*60}\nIntent: {json_obj.get('intent', '')}\nGenerated Filter Code:\n{filter_code}\n{'-'*60}")

        except Exception as e:
            print(f"Riga {idx+1}: Si è verificato un errore durante la chiamata al modello: {e}")

        # time.sleep(1) # Riduci o rimuovi il delay se non necessario

print(f"Completato. Output salvato in: {output_path}")
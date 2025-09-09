import re
import json
import os
from openai import OpenAI
import time
import itertools
from openai.types.chat import ChatCompletionSystemMessageParam,ChatCompletionUserMessageParam,ChatCompletionAssistantMessageParam

# Leggi il system prompt dal file di testo
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
prompt_path = f"{base_dir}/llm/system_prompt_generate_intent.txt"
with open(prompt_path, "r", encoding="utf-8") as f_prompt:
  SYSTEM_PROMPT = f_prompt.read()

# Configura il client OpenAI (sostituisci con il modello open source che preferisci)
client = OpenAI(api_key="lmstudio-community/llama-3.3-70b-instruct", base_url="http://127.0.0.1:1234/v1")
MODEL_ID = "llama-3.3-70b"  # Sostituisci con il modello open source più adatto

input_path = f"{base_dir}/data/generated_prompt_data_step1234.jsonl"
output_path = f"{base_dir}/output/generated_intent_output.jsonl"

with open(input_path, "r", encoding="utf-8") as f_in, open(output_path, "w", encoding="utf-8") as f_out:
    for idx, line in enumerate(itertools.islice(f_in, 0, 1000)):
        json_obj = json.loads(line)
        user_prompt = json.dumps(json_obj, ensure_ascii=False)
        messages = [
            ChatCompletionSystemMessageParam(role="system", content=SYSTEM_PROMPT),
            ChatCompletionUserMessageParam(role="user", content=user_prompt)
        ]
        # print (f"messaggesssss: {messages}\n\n\n")
        response = client.chat.completions.create(
            model=MODEL_ID,
            messages=messages,
            stream=False
        )
        content = response.choices[0].message.content
        output = content.strip() if content is not None else ""

        # Estrai INTENT e FILTERCODE delimitati dai simboli speciali
        intent = ""
        # filter_code = ""

        intent_match = re.search(r'<<<INTENT>>>(.*?)<<<END_INTENT>>>', output, re.DOTALL)
        if intent_match:
            intent = intent_match.group(1).strip()

        # filtercode_match = re.search(r'<<<FILTERCODE>>>(.*?)<<<END_FILTERCODE>>>', output, re.DOTALL)
        # print(f"filtercode_match: {filtercode_match}")
        # if filtercode_match:
        #     filter_code = filtercode_match.group(1).strip()

        json_obj["intent"] = intent
        # Gestione logica richiesta per filter_code con eccezione
        # if json_obj["filter_code"] == "":
        #     print('filter_code vuoto')  # Se filter_code è vuoto o assente
        #     json_obj["filter_code"] = filter_code
        # else:  # Se filter_code NON è vuoto
        #     print('filter_code presente')  # Se filter_code è vuoto o assente
        #     json_obj["filter_code_old"] = json_obj["filter_code"]
        #     json_obj["filter_code"] = filter_code

        f_out.write(json.dumps(json_obj, ensure_ascii=False) + "\n")
        print(f"Riga: {idx+1}\nPrompt description:\n{json_obj.get('original_description', '')}\n\nOutput:\n{output}\n{'-'*60}")
        # time.sleep(10)

print(f"Completato. Output salvato in: {output_path}")

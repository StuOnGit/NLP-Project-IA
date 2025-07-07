import json
import os
from openai import OpenAI
from openai.types.chat import ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam, ChatCompletionAssistantMessageParam

# Carica il dataset di action e trigger
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#data_path = os.path.join(base_dir, "..", "data", "generated_prompt_data.json")

# Carica il dataset di action e trigger
with open(f"{base_dir}/output/generated_prompt_data_step1(1-1000)-74.jsonl", "r", encoding="utf-8") as f:
    dataset = [json.loads(line) for line in f if line.strip()]

# Costruisci un contesto sintetico per il modello
contesto = "Queste sono alcune azioni e trigger disponibili per creare automazioni IFTTT. Per ogni richiesta in linguaggio naturale, genera il filtercode corrispondente, usando la sintassi e le API fornite. Esempi:\n"
for esempio in dataset[:]:  # Limita il contesto ai primi 5 esempi per non superare il limite del prompt
    contesto += f"\nDescrizione: {esempio['original_description']}\nTrigger: {esempio['trigger_channel']}\nAction: {esempio['action_channel']}\n"
contesto += "\nQuando ricevi una nuova richiesta, rispondi con il filtercode generato."

client = OpenAI(api_key="g4a-RKoZQ1QpMyUewi5Vm7beXzVD2BM3DsUYV4y", base_url="https://api.gpt4-all.xyz/v1")
messages = [
    ChatCompletionSystemMessageParam(role="system", content=contesto)
]

print(contesto)

print("Chat IFTTT filtercode (digita 'exit' per uscire)")
while True:
    user_input = input("Tu: ")
    if user_input.strip().lower() == "exit":
        break
    messages.append(ChatCompletionUserMessageParam(role="user", content=user_input))
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        stream=False,
    )
    assistant_reply = (response.choices[0].message.content or "").strip()
    print(f"Filtercode:\n{assistant_reply}\n")
    messages.append(ChatCompletionAssistantMessageParam(role="assistant", content=assistant_reply))

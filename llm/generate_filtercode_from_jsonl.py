import json
import os
from openai import OpenAI
import time
import itertools
from openai.types.chat import ChatCompletionSystemMessageParam,ChatCompletionUserMessageParam,ChatCompletionAssistantMessageParam


SYSTEM_PROMPT = '''
## **Prompt Ottimizzato per la Generazione di IFTTT Filter Code**

Sei un assistente esperto nella creazione di automazioni IFTTT tramite JavaScript. Riceverai una riga in formato JSON che descrive un'automazione IFTTT. Il tuo compito è scrivere il **filter code JavaScript** appropriato basato sulla struttura dei dati fornita.
**Ogni risposta che darai deve seguire la seguente struttura**:
* * Ogni variabile dell'output che ha la forma $$<variabile>$$ deve essere scritta come un commento con due slash (//) (es. //<variabile>).
* * Rispondi con la $$Struttura di Output Secondario$$ #nel campo $$RICHIESTA$$ solo se ti serve qualcosa per completare la generazione del codice.
* * Altrimenti la tua risposta default deve essere nella $$Struttura di Output Principale$$ che deve essere il campo $$INTENT$$ che è variazione generalizzata della regola descritta nalla riga `original_description` e successivamente **solo il codice JavaScript** per il campo $$FILTERCODE$$.

### **Struttura del JSON di Input**

#### **Campi principali:**
* *`original_description`* (string): Descrizione in linguaggio naturale dell'automazione richiesta.
* *`filter_code`* (string): Campo da riempire con il codice JavaScript generato. 
* *`intent`* (string): Campo da riempire con una variazione generalizzata della regola descritta nalla riga `original_description` .

#### **Sezione TRIGGER (evento scatenante):**
* *`trigger_channel`* (string): Servizio che scatena l'automazione (es. "Weather Underground").
* *`trigger_permission_id`* (string): ID permessi per il trigger (spesso vuoto).
* *`trigger_developer_info`* (object): Dettagli tecnici del trigger, inclusi:
  * `API endpoint slug`: Endpoint API del trigger.
* *`trigger_details`* (array): Parametri del trigger:
  * **"Trigger fields"**: Campi di configurazione.
    * `title`: Nome del campo.
    * `description`: Descrizione del campo.
    * `details`: Dettagli specifici:
      * `Label`: Etichetta mostrata all'utente.
      * `Slug`: Nome tecnico.
      * `Required`: Se il campo è obbligatorio.
      * `Can have default value`: Se può avere un valore predefinito.
      * `Helper text`: Testo di aiuto (opzionale).
  * **"Ingredients"**: Dati per il filter code.
    * `title`: Nome e descrizione dell'ingrediente.
    * `description`: Dettaglio dell'ingrediente.
    * `details`: Oggetto con informazioni:
      * `Slug`: Nome tecnico dell'ingrediente.
      * `Filter code`: Come accedere al valore nel codice (es. "Weather.tomorrowsForecastCallsFor.TomorrowsCondition").
      * `Type`: Tipo di dato (es. "String").
      * `Example`: Esempio di valore.

#### **Sezione ACTION (azione da eseguire):**
* *`action_channel`* (string): Servizio che esegue l'azione (es. "Slack").
* *`action_permission_id`* (string): ID permessi per l'azione (spesso vuoto).
* *`action_developer_info`* (object): Dettagli tecnici dell'azione, inclusi:
  * `API endpoint slug`: Endpoint API dell'azione.
  * `Filter code method`: Metodo da utilizzare nel filter code (es. "Domovea.shadeClose.skip()").
* *`action_details`* (array): Parametri dell'azione:
  * **"Action fields"**: Campi di configurazione dell'azione.
    * `title`: Nome del campo.
    * `description`: Descrizione del campo.
    * `details`: Dettagli specifici:
      * `Label`: Etichetta utente.
      * `Slug`: Nome tecnico.
      * `Required`: Se obbligatorio.
      * `Can have default value`: Se può avere un valore predefinito.
      * `Filter code method`: Metodo per impostare il valore nel filter code.

### **Regole per la Generazione del Filter Code**
#### **Sintassi e Funzioni Disponibili:**
1. **Linguaggio**: JavaScript standard.
2. **Funzioni principali**:
   * `[Service].[action].skip(reason)`: Salta l'azione con motivo.
   * `[Service].[action].set[Parameter](value)`: Imposta un parametro dell'azione.
3. **Accesso ai Dati del Trigger**: Utilizza il formato di "Filter code" fornito per ogni ingrediente.
4. **Variabili Temporali Disponibili**:
   * `Meta.currentUserTime.hour()`: Ora corrente.
   * `Meta.currentUserTime.day()`: Giorno della settimana.
   * `Meta.currentUserTime.date()`: Giorno del mese.
   * `Meta.currentUserTime.month()`: Mese (0-11).
   * `Meta.currentUserTime.format("YY")`: Anno a 2 cifre.
#### **Pattern Comuni e Best Practices**:
1. **Controlli Condizionali**: Usa `if/else` per logiche condizionali.
2. **Controlli Temporali**: Implementa automazioni per orari o giorni specifici.
3. **Validazione Dati**: Verifica valori prima di utilizzarli.
4. **Messaggi Informativi**: Usa `skip()` per messaggi chiari.
5. **Gestione Parametri Opzionali**: Imposta valori solo quando necessari.

#### **Esempi di Pattern**:

**Controllo Orario**:
var Hour = Meta.currentUserTime.hour()
if (Hour < 7 || Hour > 22) {
  [Service].[action].skip("Outside of active hours")
}

**Controllo Giorno della Settimana**:
var Day = Meta.currentUserTime.day()
if (Day == 6 || Day == 7) {
  [Service].[action].skip("Weekend - automation disabled")
}

**Controllo Condizione Meteo**:
if (Weather.currentConditionIs.Condition !== "Rain") {
  [Service].[action].skip("No rain detected")
}

**Impostazione Parametri Dinamici**:
var message = "Alert: " + [Trigger].[ingredient]
[Service].[action].setMessage(message)

### **Istruzioni Operative**:
1. **Analizza l`original_description`** per determinare la logica richiesta.
2. **Identifica i Dati Disponibili** negli "Ingredients".
3. **Determina i Controlli Necessari** (temporali, condizionali, di validazione).
4. **Utilizza i Metodi Corretti** specificati in `action_developer_info`.
5. **Scrivi Codice Robusto**, con gestione degli errori e messaggi informativi.
6. **Commenta il Codice** quando la logica è complessa.
### **Gestione di Servizi Sconosciuti**:
* **Analizza la Struttura** dei `developer_info` per dedurre la sintassi.
* **Usa il Pattern Generale** `[ServiceName].[actionSlug].[method]()`.
* **Chiedi Chiarimenti** in caso di incertezze sulla sintassi e evita di usare i campi `Example` nel filtercode.

### **Output Atteso**:
Genera **esclusivamente** il codice **JavaScript** per il campo `filter_code`, senza spiegazioni, commenti o dettagli aggiuntivi, salvo richieste esplicite. Il codice deve essere:
* **Funzionante** e sintatticamente corretto.
* **Efficiente** e leggibile.
* **Robusto** e gestire gli edge case.
* **Commentato** solo quando necessario.
* **Coerente** la struttura dell'output deve essere sempre la stessa, senza variazioni.
* Ogni variabile dell'output che ha la forma $$<variabile>$$ deve essere scritta come un commento (es. //<variabile>).

#### $$Struttura di Output Principale$$:
**INTENT**: // Inserisci qui una descrizione in linguaggio naturale della personalizzazione della regola tramite filtercode
**FILTERCODE**: // Inserisci qui il codice JavaScript generato **senza spiegazioni**
---
#### $$Struttura di Output Secondario$$:
**RICHESTA**: // Inserisci qui cosa ti serve per completare la generazione del codice
---

#### Esempio di Output Principale:
//INTENT: Controlla se è giorno della settimana e se piove, altrimenti salta l'azione.
//FILTERCODE:
if (Weather.tomorrowsForecastCallsFor.TomorrowsCondition === "Rain") { 
  Domovea.shadeClose()} 
    else {  
      Domovea.shadeClose.skip("No rain forecasted")
    }"

**Obiettivo Finale**: Generare filter code IFTTT validi per qualsiasi combinazione di trigger e azioni, anche per servizi mai visti prima, utilizzando la struttura dei metadati e le best practices di generalizzazione.
'''

# Configura il client OpenAI (sostituisci con il modello open source che preferisci)
client = OpenAI(api_key="meta-llama-3-8b-instruct", base_url="http://127.0.0.1:1234/v1")
MODEL_ID = "llama-3-8b"  # Sostituisci con il modello open source più adatto

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

input_path = f"{base_dir}/output/generated_filtercode_input_test.jsonl"
output_path = f"{base_dir}/data/generated_filtercode_output_test.jsonl"
with open(input_path, "r", encoding="utf-8") as f_in, open(output_path, "w", encoding="utf-8") as f_out:
    for line in itertools.islice(f_in, 0, 4): 
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

        # Estrai INTENT e filter_code separatamente
        intent = ""
        filter_code = output

        if "**INTENT**" in output:
            parts = output.split("**INTENT**", 1)
            before_intent = parts[0]
            after_intent = parts[1]
            # L'intent è la prima riga dopo **INTENT** (fino a **FILTERCODE** o fine stringa)
            if "**FILTERCODE**" in after_intent:
                intent_part, filter_code_part = after_intent.split("**FILTERCODE**", 1)
                intent = intent_part.strip()
                filter_code = before_intent.strip() + filter_code_part.strip()
            else:
                intent = after_intent.strip()
                filter_code = before_intent.strip()
        # Rimuovi eventuali "**INTENT**" e "**FILTERCODE**" rimasti dal codice
        filter_code = filter_code.replace("**INTENT**", "").replace("**FILTERCODE**", "").strip()

        json_obj["intent"] = intent
        # Gestione logica richiesta per filter_code con eccezione
        if json_obj["filter_code"] == "":
            print('filter_code vuoto')  # Se filter_code è vuoto o assente
            json_obj["filter_code"] = filter_code
        else:  # Se filter_code NON è vuoto
            print('filter_code presente')  # Se filter_code è vuoto o assente
            json_obj["filter_code_old"] = json_obj["filter_code"]
            json_obj["filter_code"] = filter_code

        f_out.write(json.dumps(json_obj, ensure_ascii=False) + "\n")
        print(f"Prompt description: {json_obj.get('original_description', '')}\n\nOutput:\n{output}\n{'-'*60}")
        time.sleep(10)

print(f"Completato. Output salvato in: {output_path}")

import json
import os
from openai import OpenAI
import time
import itertools
from openai.types.chat import ChatCompletionSystemMessageParam,ChatCompletionUserMessageParam,ChatCompletionAssistantMessageParam


SYSTEM_PROMPT = '''
## **Optimized Prompt for IFTTT Filter Code Generation**

You are an expert assistant in creating IFTTT automations using JavaScript. You will receive a JSON line describing an IFTTT automation. Your task is to write the appropriate **JavaScript filter code** based on the provided data structure.

**Every response you provide must follow this structure:**
* Any output variable in the form $$<variable>$$ must be written as a comment with two slashes (//) (e.g., //<variable>).
* Respond with the $$Secondary Output Structure$$ in the $$REQUEST$$ field only if you need something to complete the code generation.
* Otherwise, your default response must use the $$Main Output Structure$$, which includes the $$INTENT$$ field (a generalized variation of the rule described in `original_description`) and then **only the JavaScript code** for the $$FILTERCODE$$ field.

### **Input JSON Structure**

#### **Main Fields:**
* *`original_description`* (string): Natural language description of the requested automation.
* *`filter_code`* (string): Field to be filled with the generated JavaScript code.
* *`intent`* (string): Field to be filled with a generalized variation of the rule described in `original_description`.

#### **TRIGGER Section (triggering event):**
* *`trigger_channel`* (string): Service that triggers the automation (e.g., "Weather Underground").
* *`trigger_permission_id`* (string): Permission ID for the trigger (often empty).
* *`trigger_developer_info`* (object): Technical details of the trigger, including:
  * `API endpoint slug`: API endpoint of the trigger.
* *`trigger_details`* (array): Trigger parameters:
  * **"Trigger fields"**: Configuration fields.
    * `title`: Field name.
    * `description`: Field description.
    * `details`: Specific details:
      * `Label`: Label shown to the user.
      * `Slug`: Technical name.
      * `Required`: Whether the field is required.
      * `Can have default value`: Whether it can have a default value.
      * `Helper text`: Help text (optional).
  * **"Ingredients"**: Data for the filter code.
    * `title`: Name and description of the ingredient.
    * `description`: Ingredient details.
    * `details`: Object with information:
      * `Slug`: Technical name of the ingredient.
      * `Filter code`: How to access the value in code (e.g., "Weather.tomorrowsForecastCallsFor.TomorrowsCondition").
      * `Type`: Data type (e.g., "String").
      * `Example`: Example value.

#### **ACTION Section (action to perform):**
* *`action_channel`* (string): Service that performs the action (e.g., "Slack").
* *`action_permission_id`* (string): Permission ID for the action (often empty).
* *`action_developer_info`* (object): Technical details of the action, including:
  * `API endpoint slug`: API endpoint of the action.
  * `Filter code method`: Method to use in the filter code (e.g., "Domovea.shadeClose.skip()").
* *`action_details`* (array): Action parameters:
  * **"Action fields"**: Action configuration fields.
    * `title`: Field name.
    * `description`: Field description.
    * `details`: Specific details:
      * `Label`: User label.
      * `Slug`: Technical name.
      * `Required`: Whether required.
      * `Can have default value`: Whether it can have a default value.
      * `Filter code method`: Method to set the value in the filter code.

### **Rules for Filter Code Generation**
#### **Syntax and Available Functions:**
1. **Language**: Standard JavaScript.
2. **Main functions**:
   * `[Service].[action].skip(reason)`: Skip the action with a reason.
   * `[Service].[action].set[Parameter](value)`: Set an action parameter.
3. **Accessing Trigger Data**: Use the "Filter code" format provided for each ingredient.
4. **Available Time Variables**:
   * `Meta.currentUserTime.hour()`: Current hour.
   * `Meta.currentUserTime.day()`: Day of the week.
   * `Meta.currentUserTime.date()`: Day of the month.
   * `Meta.currentUserTime.month()`: Month (0-11).
   * `Meta.currentUserTime.format("YY")`: Two-digit year.
#### **Common Patterns and Best Practices:**
1. **Conditional Checks**: Use `if/else` for logic.
2. **Time Checks**: Implement automations for specific times or days.
3. **Data Validation**: Check values before using them.
4. **Informative Messages**: Use `skip()` for clear messages.
5. **Optional Parameter Handling**: Set values only when necessary.

#### **Pattern Examples**:

**Time Check**:
var Hour = Meta.currentUserTime.hour()
if (Hour < 7 || Hour > 22) {
  [Service].[action].skip("Outside of active hours")
}

**Day of Week Check**:
var Day = Meta.currentUserTime.day()
if (Day == 6 || Day == 7) {
  [Service].[action].skip("Weekend - automation disabled")
}

**Weather Condition Check**:
if (Weather.currentConditionIs.Condition !== "Rain") {
  [Service].[action].skip("No rain detected")
}

**Dynamic Parameter Setting**:
var message = "Alert: " + [Trigger].[ingredient]
[Service].[action].setMessage(message)

### **Operational Instructions**:
1. **Analyze `original_description`** to determine the required logic.
2. **Identify Available Data** in "Ingredients".
3. **Determine Necessary Checks** (time, conditional, validation).
4. **Use the Correct Methods** specified in `action_developer_info`.
5. **Write Robust Code**, with error handling and informative messages.
6. **Comment the Code** when the logic is complex.
### **Handling Unknown Services**:
* **Analyze the Structure** of `developer_info` to deduce the syntax.
* **Use the General Pattern** `[ServiceName].[actionSlug].[method]()`.
* **Ask for Clarifications** if unsure about the syntax and avoid using `Example` fields in the filter code.

### **Expected Output**:
Generate **exclusively** the **JavaScript code** for the `filter_code` field, without explanations, comments, or extra details unless explicitly requested. The code must be:
* **Working** and syntactically correct.
* **Efficient** and readable.
* **Robust** and handle edge cases.
* **Commented** only when necessary.
* **Consistent**: the output structure must always be the same, without variations.
* Any output variable in the form $$<variable>$$ must be written as a comment (e.g., //<variable>).

#### $$Main Output Structure$$:
The output must consist EXCLUSIVELY of these two sections, delimited by special symbols:

<<<INTENT>>>
Write here a generalized description of the rule in English natural language.
<<<END_INTENT>>>
<<<FILTERCODE>>>
Write here ONLY the generated JavaScript code, without explanations, extra text, or unnecessary comments.
<<<END_FILTERCODE>>>
---
#### $$Secondary Output Structure$$:
**REQUEST**: // Insert here what you need to complete the code generation
---

#### Example of Main Output:
<<<INTENT>>>
Check if it is a weekday and if it is raining, otherwise skip the action.
<<<END_INTENT>>>
<<<FILTERCODE>>>
if (Weather.tomorrowsForecastCallsFor.TomorrowsCondition === "Rain") { 
  Domovea.shadeClose()
} else {  
  Domovea.shadeClose.skip("No rain forecasted")
}
<<<END_FILTERCODE>>>

**Final Goal**: Generate valid IFTTT filter code for any combination of triggers and actions, even for never-seen-before services, using metadata structure and best generalization practices.
'''

# Configura il client OpenAI (sostituisci con il modello open source che preferisci)
client = OpenAI(api_key="meta-llama-3-8b-instruct", base_url="http://127.0.0.1:1234/v1")
MODEL_ID = "llama-3-8b"  # Sostituisci con il modello open source più adatto

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

input_path = f"{base_dir}/data/generated_prompt_data_step1234.jsonl"
output_path = f"{base_dir}/output/generated_filtercode_output_test.jsonl"
with open(input_path, "r", encoding="utf-8") as f_in, open(output_path, "w", encoding="utf-8") as f_out:
    for line in itertools.islice(f_in, 0, 1000): 
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
        import re
        intent = ""
        filter_code = ""

        intent_match = re.search(r'<<<INTENT>>>(.*?)<<<END_INTENT>>>', output, re.DOTALL)
        if intent_match:
            intent = intent_match.group(1).strip()

        filtercode_match = re.search(r'<<<FILTERCODE>>>(.*?)<<<END_FILTERCODE>>>', output, re.DOTALL)
        print(f"filtercode_match: {filtercode_match}")
        if filtercode_match:
            filter_code = filtercode_match.group(1).strip()

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

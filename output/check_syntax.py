
import esprima
import json
import sys
import re

def check_syntax(file_path):
    correct_count = 0
    total_count = 0

    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            total_count += 1
            try:
                data = json.loads(line)
                # Estrai il codice. Potrebbe essere necessario adattare "filter_code" 
                # al nome esatto del campo nel tuo JSONL.
                code_to_check = data.get("filter_code")
                
                if not code_to_check:
                    # Prova a estrarre il codice racchiuso tra <<<FILTERCODE>>> e <<<END_FILTERCODE>>>
                    match = re.search(r'<<<FILTERCODE>>>\s*(.*?)\s*<<<END_FILTERCODE>>>', code_to_check, re.DOTALL)
                    if match:
                        code_to_check = match.group(1)
                    else:
                        print(f"Warning: No code found in line {total_count}")
                        continue

                # Esegui il parsing del codice JavaScript
                esprima.parseScript(code_to_check)
                correct_count += 1
            except json.JSONDecodeError:
                print(f"Warning: Could not parse JSON on line {total_count}")
            except Exception as e:
                # Il parsing è fallito, quindi la sintassi è errata.
                # print(f"Syntax error on line {total_count}: {e}") # Decommenta per debuggare
                pass

    success_rate = (correct_count / total_count) * 100 if total_count > 0 else 0
    
    print(f"--- Analisi Sintattica per: {file_path} ---")
    print(f"File analizzati: {total_count}")
    print(f"Codici sintatticamente corretti: {correct_count}")
    print(f"Tasso di successo: {success_rate:.2f}%")
    print("--------------------------------------------------")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python check_syntax.py <path_del_file_jsonl>")
        sys.exit(1)
    
    file_to_check = sys.argv[1]
    check_syntax(file_to_check)

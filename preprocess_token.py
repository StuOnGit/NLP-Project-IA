import re
import pandas as pd


files = [
    "data/Step1_Raw_Data_with_FilterCode1.csv",
    "data/Step2_Popular_Rules_with_FilterCode.csv",
    "data/Step3_IoT_Rules_with_FilterCode.csv"
]
LABELS = {
    'if': 'IF',
    'else': 'ELSE',
    'for': 'FOR',
    'while': 'WHILE',
    '=': 'ASSIGN',
    '==': 'COND',
    '!=': 'COND',
    '<=': 'COND',
    '>=': 'COND',
    '<': 'COND',
    '>': 'COND',
    '(': 'LPAREN',
    ')': 'RPAREN',
    '{': 'LBRACE',
    '}': 'RBRACE',
    ';': 'END',
    '.': 'DOT',
    # Puoi aggiungere altre regole...
}
def label_token(token):
    if token in LABELS:
        return LABELS[token]
    elif token.isdigit():
        return 'NUM'
    elif re.match(r'^[A-Z][a-zA-Z0-9_]*$', token):
        return 'OBJ'  # Oggetto o classe
    elif re.match(r'^[a-z_][a-zA-Z0-9_]*$', token):
        return 'VAR'  # Variabile o funzione
    else:
        return 'UNK'

def tokenize_description(text):
    return re.findall(r'\b[a-zA-Z]{2,}\b', text.lower())

def tokenize_filter_code(code):
    return re.findall(r'\w+|==|!=|<=|>=|[^\s\w]', code.lower())


rows = []

for file in files:
    df = pd.read_csv(file)
    if 'description' in df.columns and 'filter_code' in df.columns:
        i = 0
        for _, row in df.iterrows():
            desc = str(row['description']) if pd.notna(row['description']) else ""
            code = str(row['filter_code']) if pd.notna(row['filter_code']) else ""
            desc_tokens = tokenize_description(desc)
            code_tokens = tokenize_filter_code(code)
            code_labels = [label_token(tok) for tok in code_tokens]
            rows.append({
                "id": i,
                "description": desc,
                "desc_tokens": desc_tokens,
                "filter_code": code,
                "code_tokens": code_tokens,
                "code_labels": code_labels
            })
            i += 1

df_out = pd.DataFrame(rows)
df_out.to_csv("tokenized_labeled.csv", index=False)
print("✅ File salvato: tokenized_labeled.csv")
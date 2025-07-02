# import json
# from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
# from nltk.translate.meteor_score import meteor_score
# from rouge_score import rouge_scorer

# # === Load test data ===
# # Ogni entry: {"description": ..., "reference_code": ..., "generated_code": ...}
# with open("data/evaluation_set.json", "r", encoding="utf-8") as f:
#     dataset = json.load(f)

# bleu_scores = []
# meteor_scores = []
# rouge_l_f1_scores = []

# scorer = rouge_scorer.RougeScorer(["rougeL"], use_stemmer=True)
# smoothie = SmoothingFunction().method4

# for i, sample in enumerate(dataset):
#     reference = sample["reference_code"].strip()
#     hypothesis = sample["generated_code"].strip()

#     # BLEU
#     bleu = sentence_bleu([reference.split()], hypothesis.split(), smoothing_function=smoothie)
#     bleu_scores.append(bleu)

#     # METEOR
#     meteor = meteor_score([reference], hypothesis)
#     meteor_scores.append(meteor)

#     # ROUGE-L (F1)
#     rouge_scores = scorer.score(reference, hypothesis)
#     rouge_l_f1 = rouge_scores["rougeL"].fmeasure
#     rouge_l_f1_scores.append(rouge_l_f1)

#     # Opzionale: stampa progressiva
#     if (i+1) % 1000 == 0:
#         print(f"Iterazione {i+1}: BLEU={bleu:.4f}, METEOR={meteor:.4f}, ROUGE-L={rouge_l_f1:.4f}")

# # === Average Metrics ===
# def average(lst):
#     return sum(lst) / len(lst) if lst else 0.0

# print("\n--- RISULTATI FINALI DOPO 10.000 ESECUZIONI ---")
# print(f"BLEU medio: {average(bleu_scores):.4f}")
# print(f"METEOR medio: {average(meteor_scores):.4f}")
# print(f"ROUGE-L medio: {average(rouge_l_f1_scores):.4f}")

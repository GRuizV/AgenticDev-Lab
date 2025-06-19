import json
from collections import Counter
import pandas as pd




# Aux Normalizer
def normalize_description(desc: str) -> str:
    return Counter(c for c in desc.lower() if c.isalnum())

# Aux Match Validator
def is_match(tx1: dict, tx2: dict) -> bool:
    return (
        tx1["date"] == tx2["date"] and
        abs(tx1["amount"] - tx2["amount"]) <= 5 and
        normalize_description(tx1["description"]) == normalize_description(tx2["description"])
    )


# Evaluate LLM output where structure matches ground_truth: grouped by bill
def evaluate_llm_output(gt_path: str, llm_path: str) -> dict:

    with open(gt_path, "r", encoding="utf-8") as f:
        gt_json = json.load(f)

    with open(llm_path, "r", encoding="utf-8") as f:
        llm_json = json.load(f)

    results = []
    gt_bills = {bill["bill_name"]: bill["transactions"] for bill in gt_json["bills"]}
    llm_bills = {bill["bill_name"]: bill["transactions"] for bill in llm_json["bills"]}

    for bill_name, gt_txns in gt_bills.items():

        llm_txns = llm_bills.get(bill_name, [])

        matched_gt = set()
        matched_llm = set()

        for i, llm_tx in enumerate(llm_txns):

            for j, gt_tx in enumerate(gt_txns):

                if j in matched_gt:
                    continue

                if is_match(llm_tx, gt_tx):                    
                    matched_llm.add(i)
                    matched_gt.add(j)
                    break

        count = len(llm_txns)
        tp = len(matched_llm)
        fp = len(llm_txns) - tp
        fn = len(gt_txns) - tp
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0

        gt_sum = sum(tx["amount"] for tx in gt_txns)
        llm_sum = sum(tx["amount"] for tx in llm_txns if tx["amount"] > 0)

        results.append({
            "bill_name": bill_name,
            "tp": tp,
            "fp": fp,
            "fn": fn,
            "precision": round(precision, 3),
            "recall": round(recall, 3),
            "count": count,
            "llm_total": llm_sum,
            "gt_total": gt_sum
        })

    overall_count = sum(r["count"] for r in results)
    overall_tp = sum(r["tp"] for r in results)
    overall_fp = sum(r["fp"] for r in results)
    overall_fn = sum(r["fn"] for r in results)
    overall_precision = overall_tp / (overall_tp + overall_fp) if (overall_tp + overall_fp) > 0 else 0.0
    overall_recall = overall_tp / (overall_tp + overall_fn) if (overall_tp + overall_fn) > 0 else 0.0
    overall_llm_total = sum(r["llm_total"] for r in results)
    overall_gt_total = sum(r["gt_total"] for r in results)
    

    summary = {
        "overall": {
            "true_positives": overall_tp,
            "false_positives": overall_fp,
            "false_negatives": overall_fn,
            "precision": round(overall_precision, 3),
            "recall": round(overall_recall, 3),
            "count": overall_count,            
            "llm_total": overall_llm_total,
            "gt_total": overall_gt_total
        },
        "per_bill": results
    }

    return summary



# === CONFIG ===
gt_path = r"C:\Users\USUARIO\OneDrive\Nima Cloud\02 Desarrollo de Producto\PBA\POCs\Extraccion de Data\Pruebas\test #0\Metricas\ground_truth.json"
llm_path = r"C:\Users\USUARIO\OneDrive\Nima Cloud\02 Desarrollo de Producto\PBA\POCs\Extraccion de Data\Pruebas\test #0\Resultados\Claude.json"



# === RUN ===
results = evaluate_llm_output(gt_path=gt_path, llm_path=llm_path)



# === OUTPUT ===
print("\n=== Overall Performance ===")
for k, v in results["overall"].items():
    print(f"{k.replace('_', ' ').title()}: {v}")

print("\n=== Per-Bill Breakdown ===")
df = pd.DataFrame(results["per_bill"])
print(df.to_string(index=False))








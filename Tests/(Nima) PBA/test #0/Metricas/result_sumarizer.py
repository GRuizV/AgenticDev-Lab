import json
import pandas as pd

# Base file path
file_path = r"C:\Users\USUARIO\OneDrive\Nima Cloud\02 Desarrollo de Producto\PBA\POCs\Extraccion de Data\Pruebas\test #0\Metricas\ground_truth.json"

# Summarize each bill by total charges and number of transactions
summary = []

with open(file_path, "r", encoding="utf-8") as f:
    data = json.load(f)



for bill in data["bills"]:
    
    bill_name = bill["bill_name"]
    transactions = bill["transactions"]
    total_amount = sum(tx["amount"] for tx in transactions)
    num_transactions = len(transactions)
    summary.append({
        "bill_name": bill_name,
        "num_transactions": num_transactions,
        "total_amount": round(total_amount, 2)
    })


# Create a DataFrame for display
df_summary = pd.DataFrame(summary)

print(df_summary)

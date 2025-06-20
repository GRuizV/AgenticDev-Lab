import json
import pandas as pd

# Base file path
file_path = r"C:\Users\USUARIO\GR\Software Development\Agentic Dev\Tests\(Nima) PBA\ground_truth.json"

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

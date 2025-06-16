## 🧠 Goal
Build a standalone Python CLI app that receives a **credit card bill in PDF format** and **extracts the list of expenses** from it using **text-based PDF parsing**.

## 🎯 Scope
- ✅ Input: Text-based PDF from **one known card issuer** (6 samples available).
- ✅ Output: CLI table displaying each expense (date, description, amount).
- ✅ Tools: Use `pdfplumber` for parsing.
- ❌ No categorization, aggregation, CSV export, or GUI (yet).
- 🧪 Success Criteria: Correctly extracts and reports back expense lines for known samples.

## 📎 Context
- Expense lines contain several tokens, but we are only interested in 3 parts:
  - A **date** segment: formatted like `21 04 25` (assumed `DD MM YY`)
  - A **description** segment: e.g., `HOMECENTER VTAS A DIST BOGOTA`
  - A **currency amount**: e.g., `$704,700.00`
  - All monetary amounts are in **Colombian Pesos (COP)**, typically formatted with a dollar sign (`$`) and comma separators (e.g., `$704,700.00`).

- Example line (raw from `pdfplumber`): "4290 21 04 25 HOMECENTER VTAS A DIST BOGOTA 25.61 $704,700.00 $704,700.00 $0.00 01 01 00"

- What we want extracted:
    - Date: 21 04 25
    - Description: HOMECENTER VTAS A DIST BOGOTA
    - Amount: $704,700.00

## 🛠 Tools & Requirements
- Python 3.x
- `pdfplumber` for PDF reading
- `re` (if needed) to extract segments
- `tabulate` or `rich` for CLI report

## 🧾 Instructions
- Extract all relevant lines from the PDF using `pdfplumber`
- Identify and extract:
    - The first instance of a date segment (`\d{2} \d{2} \d{2}`)
    - The longest alphanumeric block between date and amount (description)
    - The first currency-formatted number (amount)
- Print results to terminal in clean tabular format
- Do not build additional logic (filters, validation, etc.)
- Keep code readable and ready for iteration
- Comment enough the code so it is already human-understandable


## 🧠 Goal
Build a standalone Python CLI app that receives a **credit card bill in PDF format** and **extracts the list of expenses** from it using **OCR-based parsing**.

## 🎯 Scope
- ✅ Input: Image-based or scanned PDF from **one known card issuer** (6 samples available).
- ✅ Output: CLI table displaying each expense (date, description, amount).
- ✅ Tools: Use OCR via `pdf2image` + `pytesseract` to extract text.
- ❌ No categorization, aggregation, CSV export, or GUI (yet).
- 🧪 Success Criteria: Correctly extracts and reports back expense lines for known samples.

## 📎 Context
- Expense lines contain several tokens, but we are only interested in 3 parts:
  - A **date** segment: formatted like `21 04 25` (assumed `DD MM YY`)
  - A **description** segment: e.g., `HOMECENTER VTAS A DIST BOGOTA`
  - A **currency amount**: e.g., `$704,700.00`
  - All monetary amounts are in **Colombian Pesos (COP)**, typically formatted with a dollar sign (`$`) and comma separators (e.g., `$704,700.00`).

- Example line (from OCR):  
  `"4290 21 04 25 HOMECENTER VTAS A DIST BOGOTA 25.61 $704,700.00 $704,700.00 $0.00 01 01 00"`

- What we want extracted:
    - Date: 21 04 25
    - Description: HOMECENTER VTAS A DIST BOGOTA
    - Amount: $704,700.00

## 🛠 Tools & Requirements
- Python 3.x
- `pdf2image` to convert PDF pages to images
- `pytesseract` for OCR text extraction
- `re` (if needed) to extract segments
- `tabulate` or `rich` for CLI report

## 🧾 Instructions
- Convert each page of the PDF to an image using `pdf2image`
- Use `pytesseract` to extract raw text from each image
- Identify and extract:
    - The first instance of a date segment (`\d{2} \d{2} \d{2}`)
    - The longest alphanumeric block between date and amount (description)
    - The first currency-formatted number (amount)
- Print results to terminal in clean tabular format
- Do not build additional logic (filters, validation, etc.)
- Keep code readable and ready for iteration
- Comment enough the code so it is already human-understandable
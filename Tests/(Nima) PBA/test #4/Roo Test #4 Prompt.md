## 🧠 Goal
Build a standalone Python CLI app that receives a **credit card bill in PDF format** and extracts a list of expenses per document. The app must identify and extract the transaction date, merchant description, and the correct amount per transaction.

- This project is intented to live inside @/Tests/(Nima)\ PBA/test\ #4/pdf_extractor/

## 🎯 Scope
- ✅ Input: Six text-based PDFs from one known card issuer
- ✅ Output: CLI table listing one row per expense, with:
  - Date
  - Description
  - Amount (in COP)

  Example: 
    ============================================================
    EXTRACTED CREDIT CARD EXPENSES
    ============================================================
    Total expenses found: 18
    ============================================================

    +----------+-----------------------------------+-------------+
    | Date     | Description                       | Amount      |
    +==========+===================================+=============+
    | 26/02/25 | SEGURO DE VIDA DEUDOR 0           | $0.00       |
    +----------+-----------------------------------+-------------+
    | 23/02/25 | SC CENTENARIO CALI 26             | $73,087.00  |
    +----------+-----------------------------------+-------------+
    | 21/02/25 | TIENDA D1 VILLA DEL PR CALI 26    | $19,780.00  |
    +----------+-----------------------------------+-------------+
    | 21/02/25 | SUPER INTER UNICO SALO CALI 26    | $72,840.00  |
    +----------+-----------------------------------+-------------+
    | 18/02/25 | TIENDA D1 VAL CALI CAL CALI 26    | $37,410.00  |
    +----------+-----------------------------------+-------------+
    | 18/02/25 | LIBRERIA SAN PABLO CALI 26        | $29,500.00  |
    +----------+-----------------------------------+-------------+
    | 11/02/25 | TIENDA D1 VILLA DEL PR CALI 26    | $12,040.00  |
    +----------+-----------------------------------+-------------+
    | 11/02/25 | CTRO DIAGNOST AUTOM VA CALI 26    | $302,500.00 |
    +----------+-----------------------------------+-------------+
    | 11/02/25 | SC LA PRIMERA CALI 26             | $48,700.00  |
    +----------+-----------------------------------+-------------+
    | 10/02/25 | SMART FIT METROPOLIS BOGOTA DC 26 | $79,900.00  |
    +----------+-----------------------------------+-------------+
    | 03/02/25 | SUPER INTER UNICO SALO CALI 26    | $82,954.00  |
    +----------+-----------------------------------+-------------+
    | 03/02/25 | TIENDA D1 VILLA DEL PR CALI 26    | $82,550.00  |
    +----------+-----------------------------------+-------------+
    | 01/02/25 | PAGO ATH CANALES ELECTRONICOS 0   | $0.00       |
    +----------+-----------------------------------+-------------+
    | 01/02/25 | HOMECENTER CALI 24                | $64,900.00  |
    +----------+-----------------------------------+-------------+
    | 30/01/25 | STETIK DENT CALI 0                | $680,000.00 |
    +----------+-----------------------------------+-------------+
    | 25/01/25 | H M MALLPLAZA PLAZA DE CALI 0     | $64,900.00  |
    +----------+-----------------------------------+-------------+
    | 25/01/25 | SC EL LIMONAR CALI 0              | $13,900.00  |
    +----------+-----------------------------------+-------------+
    | 24/01/25 | THE BARBER FACTORY CALI 0         | $38,000.00  |
    +----------+-----------------------------------+-------------+

    ============================================================
    SUMMARY
    ============================================================
    Total transactions: 18
    Total amount: $1,702,961.00

- ✅ Constraints:
  - The **sum of the extracted expenses must match the known total**
  - The **number of extracted transactions must match the expected count**

## 📎 Context
- Each expense line in the PDFs includes:
  - Several numerical tokens
  - One or more currency-formatted values (e.g., `$79,900.00`)
  - A short-form date (e.g., `10 02 25`)
  - Descriptive merchant name.

  - From the test PDF files you will identify an expense because it will look like this: "8632 10 02 25 SMART FIT METROPOLIS BOGOTA DC 26.19 $79,900.00 $79,900.00 $0.00 01 01 00". From this line the relevant info will be: 
    + The date: '10 02 25' (being the first pair of digits the day number, the next pair the month number, and the last pair).
    + The description of the expense: "SMART FIT METROPOLIS BOGOTA DC". This may vary from expense to expense, but the most common case is that the real important part of the expense detail is for the most part strings.
    + The total amount of the expense is commonly the first subtring you find following this pattern '$79,900.00'.


### Validation Data:

| PDF File Name           | Expected Total (COP) | Expected Transactions |
|-------------------------|----------------------|------------------------|
| AV - MC - 02 - FEB-2025 | $434,980.00          | 5                      |
| AV - MC - 03 - MAR-2025 | $44,900.00           | 2                      |
| AV - MC - 04 - ABR-2025 | $1,068,097.00        | 9                      |
| AV - VS - 02 - FEB-2025 | $1,702,961.00        | 18                     |
| AV - VS - 03 - MAR-2025 | $810,460.00          | 14                     |
| AV - VS - 04 - ABR-2025 | $1,058,980.00        | 20                     |

- You will have a JSON file named 'ground_truth.json' which contains an schema with the verified data that you are supposed to extract from the tests PDFs. This file is at @/Tests/(Nima)\ PBA/test\ #4/pdf_extractor/pj_directory/src/ground_truth/ground_truth.json

  + You may expect the following schema from the ground_truth file with the data contain in the table:

    "
    {
    "bills": [
        {
        "bill_name": "string",             // e.g. "AV - MC - 02 - FEB-2025"
        "transactions": [
          {
              "date": "string (YYYY-MM-DD)", // e.g. "2025-02-06"
              "description": "string",       // e.g. "MERCADO PAGO*TECNOPLAZ 760001CALI"
              "amount": "integer"            // e.g. 115900 (in cents or currency units, depending on context)
          }
        ]
        }
        ]
    }
    "

- You will have the 6 base PDF files from above to test the app at @/Tests/(Nima)\ PBA/test\ #4/pdf_extractor/pj_directory/src/ground_truth/

## 🛠 Requirements
- Use Python 3 to implement a CLI app.
- You may work with pdfplumber python library for the files extraction.
- Implement two way to run the app:
  1. Extract, present and summarize individually and in bulk all PDF files in a folder path (initially the path provided with the 6 base PDF files). But leave it to be directly configured in code the folder path to review Card Bills from.
  2. Ask the path to one Card Bill PDF file to extract, analyze, summarize and display. And also leave it to be directly configured in code the folder path to review Card Bill from.

- Extract a clean list of transactions including:
  - Date
  - Description
  - Correct amount

- Output the transactions as a readable CLI table.

- At the end of the script, display:
  - The total extracted amount  
  - The number of transactions extracted

- When testings always verify against the ground_truth file.
- Create a feature to teach the app new patterns from new PDF formats or new Card issuers. 
  + This must be implemented so the user can teach new patterns and indicate what's relevant from it: which substring is the Date, which is the Description and which the total amount from the new expenses format.

  + When a new pattern is taught it should have a knowledge base to store it and when a extaction task is assigned, the app have a base to compare the extractions from. Making it that at some point, whatever is passed to the app it knows where to look for to find something similar and extract the data with its current knowledge.

- Clearly comment your reasoning and implementation choices in the code.

## 🧪 Evaluation Criteria
- Soundness of tool and method selection
- Accuracy of extracted values (dates, descriptions, amounts)
- Correct identification of valid transaction lines vs. irrelevant data
- Match between calculated and expected totals and transaction counts
- Clarity and maintainability of the code
- Completeness of output and internal validation logic


## Instructions

First, begin this project by replacing all template placeholders in `roo_state/project_state.md` with the actual purpose, current active goal, updated task queue, and clarified agents involved. Clean up the example comments if you find them.

Then, assign the first system architecture task. Suggest which internal components and logic flows will be needed to fulfill the requirements, and hand this task to the Architect agent for design and planning.
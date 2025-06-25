## 🧠 Goal
Build a standalone Python CLI app that receives a **credit card bill in PDF format** and extracts a list of expenses per document. The app must identify and extract the transaction date, merchant description, and the correct amount per transaction without predefined parsing instructions.

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
- ❌ Do not assume any specific library for PDF parsing — evaluate and select the most suitable tool for the task
- ❌ Do not rely on provided regex patterns or known column positions — evaluate and select the most suitable way to identify the data requested for the task

## 📎 Context
- Each expense line in the PDFs includes:
  - Several numerical tokens
  - One or more currency-formatted values (e.g., `$79,900.00`)
  - A short-form date (e.g., `10 02 25`)
  - Descriptive merchant name
- Only one currency-formatted value per line is the correct transaction amount. Others may represent installments or internal breakdowns.
- The app must determine which value reflects the actual expense and validate its output using the expected totals and transaction counts.

### Validation Data:

| PDF File Name           | Expected Total (COP) | Expected Transactions |
|-------------------------|----------------------|------------------------|
| AV - MC - 02 - FEB-2025 | $434,980.00          | 5                      |
| AV - MC - 03 - MAR-2025 | $44,900.00           | 2                      |
| AV - MC - 04 - ABR-2025 | $1,068,097.00        | 9                      |
| AV - VS - 02 - FEB-2025 | $1,702,961.00        | 18                     |
| AV - VS - 03 - MAR-2025 | $810,460.00          | 14                     |
| AV - VS - 04 - ABR-2025 | $1,058,980.00        | 20                     |

## 🛠 Requirements
- Use Python 3 to implement a CLI app
- Choose and justify the best text extraction method for PDFs
- Infer the structure of each transaction line without being told how it is formatted
- Extract a clean list of transactions including:
  - Date
  - Description
  - Correct amount
- Output the transactions as a readable CLI table
- At the end of the script, display:
  - The total extracted amount  
  - The number of transactions extracted  
- Validate these results against the table provided above
- Clearly comment your reasoning and implementation choices in the code

## 🧪 Evaluation Criteria
- Soundness of tool and method selection
- Accuracy of extracted values (dates, descriptions, amounts)
- Correct identification of valid transaction lines vs. irrelevant data
- Match between calculated and expected totals and transaction counts
- Clarity and maintainability of the code
- Completeness of output and internal validation logic
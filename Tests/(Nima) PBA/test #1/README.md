# PDF Credit Card Expense Extractor

A standalone Python CLI application that extracts credit card expenses from PDF files and displays them in a clean table format.

## Features

- Extracts text from PDF files using `pdfplumber`
- Parses expense lines with specific format patterns
- Extracts three key components:
  - **Date**: First occurrence of pattern `DD MM YY` format
  - **Description**: Longest alphanumeric block between date and amount
  - **Amount**: First currency-formatted number with $ and commas (Colombian Pesos)
- Displays results in a clean CLI table using `tabulate`
- Comprehensive error handling and validation
- Detailed logging of extraction process

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

Or install individually:
```bash
pip install pdfplumber tabulate
```

## Usage

1. Update the `pdf_path` variable in the `main()` function with your actual PDF file path
2. Run the application:
```bash
python pdf_expense_extractor.py
```

## Expected PDF Format

The application expects expense lines in the following format:
```
4290 21 04 25 HOMECENTER VTAS A DIST BOGOTA 25.61 $704,700.00 $704,700.00 $0.00 01 01 00
```

Where:
- `21 04 25` is the date (DD MM YY)
- `HOMECENTER VTAS A DIST BOGOTA` is the description
- `$704,700.00` is the amount in Colombian Pesos

## Output

The application displays:
- Processing information during extraction
- A formatted table with Date, Description, and Amount columns
- Summary statistics including total transactions and total amount

## Error Handling

The application includes comprehensive error handling for:
- Missing or invalid PDF files
- PDF text extraction failures
- Missing dependencies
- Parsing errors
- Invalid expense line formats

## Code Structure

- `PDFExpenseExtractor`: Main class handling PDF processing and expense extraction
- `validate_pdf_file()`: Validates PDF file existence and format
- `extract_text_from_pdf()`: Extracts text content from all PDF pages
- `parse_expense_line()`: Parses individual expense lines using regex patterns
- `extract_expenses()`: Orchestrates the full extraction process
- `display_expenses()`: Formats and displays results in a table

## Dependencies

- `pdfplumber`: For PDF text extraction
- `tabulate`: For clean CLI table formatting
- `re`: Built-in regex module for pattern matching
- `pathlib`: Built-in module for file path handling
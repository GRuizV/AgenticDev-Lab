# PDF Credit Card Expense Extractor

A Python CLI application for extracting credit card transaction data from PDF files with exact validation against expected totals and transaction counts.

## Features

- **Multi-Library Support**: Automatically selects the best PDF parsing library (pdfplumber, pymupdf, PyPDF2)
- **Pattern Detection**: Intelligent transaction pattern recognition without predefined regex
- **Exact Validation**: Validates extracted totals within ±$1 tolerance and exact transaction counts
- **CLI Table Output**: Professional table formatting for transaction display
- **Robust Error Handling**: Comprehensive error handling with fallback mechanisms
- **Detailed Reporting**: Validation reports with success/failure analysis

## Installation

1. **Clone or download the project**:
   ```bash
   cd "Tests/(Nima) PBA/test #3"
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

   **Note**: At least one PDF parsing library is required:
   - `pdfplumber` (recommended for tabular data)
   - `pymupdf` (high performance)
   - `PyPDF2` (lightweight fallback)

## Usage

### Basic Usage

Process all PDF files in the default directory:
```bash
python -m pdf_expense_extractor
```

### Specify PDF Directory

```bash
python -m pdf_expense_extractor --dir "./path/to/pdfs"
```

### Verbose Output

```bash
python -m pdf_expense_extractor --verbose
```

### Process Single File

```bash
python -m pdf_expense_extractor --single-file "path/to/file.pdf"
```

### Test PDF Parsers

```bash
python -m pdf_expense_extractor --test-parsers "path/to/file.pdf"
```

### Generate Detailed Report

```bash
python -m pdf_expense_extractor --report
```

## Expected Results

The application validates against these expected results:

| PDF File | Expected Total | Expected Count |
|----------|----------------|----------------|
| AV - MC - 02 - FEB-2025 | $434,980.00 | 5 transactions |
| AV - MC - 03 - MAR-2025 | $44,900.00 | 2 transactions |
| AV - MC - 04 - ABR-2025 | $1,068,097.00 | 9 transactions |
| AV - VS - 02 - FEB-2025 | $1,702,961.00 | 18 transactions |
| AV - VS - 03 - MAR-2025 | $810,460.00 | 14 transactions |
| AV - VS - 04 - ABR-2025 | $1,058,980.00 | 20 transactions |

## Output Format

### Transaction Table
```
┌────────────┬─────────────────────────────────────┬─────────────┐
│ Date       │ Description                         │ Amount      │
├────────────┼─────────────────────────────────────┼─────────────┤
│ 2025-02-06 │ MERCADO PAGO*TECNOPLAZ 760001CALI   │ $115,900.00 │
│ 2025-02-10 │ MERCPAGO*CRUZVERDEPAGO BARRANQUILLA │ $224,180.00 │
│ 2025-02-14 │ CINECOLOMBIA BOGOTA                 │ $50,000.00  │
│ 2025-02-15 │ PAYU*NETFLIX 110111BOGOTA           │ $44,900.00  │
└────────────┴─────────────────────────────────────┴─────────────┘
```

### Validation Results
```
Validation Results:
──────────────────────────────────────────────────
✓ Transaction Count: 5/5 (Expected: 5)
✓ Total Amount: $434,980.00 (Expected: $434,980.00, Diff: $0.00)
✅ VALIDATION PASSED
```

## Command Line Options

| Option | Description |
|--------|-------------|
| `--dir DIR` | Directory containing PDF files |
| `--tolerance FLOAT` | Amount tolerance for validation (default: 1.0) |
| `--verbose, -v` | Enable verbose output |
| `--no-progress` | Disable progress display |
| `--test-parsers FILE` | Test all parsers on a specific PDF |
| `--single-file FILE` | Process a single PDF file |
| `--report` | Generate detailed validation report |
| `--version` | Show version information |

## Architecture

### Core Components

- **PDF Parser Factory**: Automatically selects the best available PDF library
- **Pattern Detector**: Intelligent transaction pattern recognition
- **Transaction Validator**: Validates against expected results with tolerance
- **CLI Interface**: User-friendly command-line interface

### Supported PDF Libraries

1. **pdfplumber** (Primary): Best for tabular data extraction
2. **pymupdf** (Secondary): High performance, good text positioning  
3. **PyPDF2** (Fallback): Lightweight, basic text extraction

### Data Flow

1. **PDF Discovery**: Locate PDF files in specified directory
2. **Library Selection**: Choose optimal PDF parser based on evaluation
3. **Text Extraction**: Extract raw text from PDF files
4. **Pattern Detection**: Identify and parse transaction patterns
5. **Data Validation**: Compare against expected results
6. **Output Formatting**: Display results in CLI table format

## Error Handling

- **PDF Reading Errors**: Automatic fallback to alternative libraries
- **Pattern Matching Failures**: Detailed logging of unmatched content
- **Validation Failures**: Specific reporting of count/amount mismatches
- **File Access Issues**: Clear error messages with suggested solutions

## Validation Logic

### Transaction Count
- **Requirement**: Exact match with expected count
- **Failure**: Reports difference between extracted and expected counts

### Amount Validation  
- **Requirement**: Total within ±$1.00 tolerance
- **Calculation**: Sum of all non-zero transaction amounts
- **Exclusions**: Payments, adjustments, and zero-amount transactions

### Excluded Transaction Types
- PAGO ATH CANALES ELECTRONICOS
- SEGURO DE VIDA DEUDOR
- INTERESES FACTURADOS
- ABONO SUCURSAL VIRTUAL
- AJUSTE MANUAL A FAVOR

## Troubleshooting

### No PDF Libraries Available
```bash
pip install pdfplumber pymupdf PyPDF2
```

### PDF Directory Not Found
- Verify the path to your PDF directory
- Use absolute paths if relative paths fail
- Check file permissions

### Validation Failures
- Review transaction patterns in verbose mode
- Check for missing or extra transactions
- Verify amount calculations

### Parser Errors
- Test different parsers with `--test-parsers`
- Check PDF file integrity
- Ensure PDF is not encrypted or corrupted

## Development

### Project Structure
```
pdf_expense_extractor/
├── main.py                 # CLI entry point
├── core/                   # Core processing logic
├── models/                 # Data models
├── parsers/                # PDF parser implementations
├── config/                 # Configuration and patterns
└── utils/                  # Utility functions
```

### Adding New PDF Formats
1. Analyze PDF structure
2. Update patterns in `config/patterns.py`
3. Add expected results in `config/expected_results.py`
4. Test with new files

## License

This project is part of the Agentic Development test suite.

## Version

1.0.0 - Initial implementation with comprehensive PDF extraction and validation.
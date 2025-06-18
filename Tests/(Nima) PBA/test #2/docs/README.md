# PDF Expense Extractor

A Python CLI tool that extracts expense data from credit card PDF bills using OCR (Optical Character Recognition). The tool converts PDF pages to images and uses Tesseract OCR to extract text, then parses the text to identify transaction details.

## Features

- **PDF Processing**: Converts PDF pages to images for OCR processing
- **OCR Text Extraction**: Uses Tesseract OCR to extract text from scanned documents
- **Smart Parsing**: Extracts Date, Description, and Amount from transaction lines
- **Clean Output**: Displays results in a formatted table with summary statistics
- **Colombian Peso Support**: Optimized for Colombian peso currency format ($XXX,XXX.XX)

## Installation

### 1. Install System Dependencies

**Tesseract OCR** must be installed on your system:

#### Windows
```bash
# Using winget (recommended)
winget install UB-Mannheim.TesseractOCR

# Or download from: https://github.com/UB-Mannheim/tesseract/wiki
```

#### macOS
```bash
brew install tesseract
```

#### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
```

#### CentOS/RHEL
```bash
sudo yum install tesseract
```

### 2. Install Python Dependencies

```bash
# Navigate to the project directory
cd "Tests/(Nima) PBA/test #2"

# Install Python dependencies
pip install -r requirements.txt
```

## Usage

### Basic Usage

1. **Set the PDF file path**: Open `src/pdf_expense_extractor.py` and modify the `PDF_FILE_PATH` variable at the top of the file:

```python
# Change this line to point to your PDF file
PDF_FILE_PATH = "path/to/your/credit_card_statement.pdf"
```

2. **Run the extractor**:

```bash
python src/pdf_expense_extractor.py
```

### Test PDFs Location

The project includes sample PDF files located at:
```
Tests/(Nima) PBA/Test PDFs/
├── MC - FEB-2025.pdf
├── MC - MAR-2025.pdf
├── MC - ABR-2025.pdf
├── VS - FEB-2025.pdf
├── VS - MAR-2025.pdf
└── VS - ABR-2025.pdf
```

The default configuration points to `../Test PDFs/MC - FEB-2025.pdf` relative to the script location.

### Batch Testing

To test all PDF files systematically:

```bash
python tests/batch_test_pdfs.py
```

This will:
- Test all 6 PDF files automatically
- Generate a comprehensive report comparing MC vs VS card formats
- Analyze results by month and card type
- Save detailed results to a JSON file for further analysis

### Examples

```bash
# After setting PDF_FILE_PATH = "statement_202412.pdf"
python src/pdf_expense_extractor.py

# After setting PDF_FILE_PATH = "/full/path/to/documents/statement.pdf"
python src/pdf_expense_extractor.py
```

### Configuration

Edit the `PDF_FILE_PATH` variable in the script:

```python
# Examples of valid paths:
PDF_FILE_PATH = "credit_card_statement.pdf"                    # Same directory
PDF_FILE_PATH = "documents/statement.pdf"                      # Relative path
PDF_FILE_PATH = "/full/path/to/statement.pdf"                  # Absolute path
PDF_FILE_PATH = "C:/Users/Username/Documents/statement.pdf"    # Windows path
```

## Expected Input Format

The tool is designed to parse credit card transaction lines in this format:

```
4290 21 04 25 HOMECENTER VTAS A DIST BOGOTA 25.61 $704,700.00 $704,700.00 $0.00 01 01 00
```

### Parsing Logic

From each transaction line, the tool extracts:

1. **Date**: First occurrence of `DD MM YY` pattern → `21/04/25`
2. **Description**: Text between date and first amount → `HOMECENTER VTAS A DIST BOGOTA`
3. **Amount**: First currency-formatted number → `$704,700.00`

## Sample Output

```
PDF Expense Extractor v1.0.0
========================================
Converting PDF to images: statement.pdf
Processing 3 page(s) with OCR...
  Processing page 1/3
  Processing page 2/3
  Processing page 3/3
Analyzing 1247 lines for expense data...
  Found expense on line 45: 21/04/25 | HOMECENTER VTAS A DIST BOGOTA... | $704,700.00
  Found expense on line 67: 22/04/25 | SUPERMERCADO OLIMPICA BOGOTA... | $156,800.00
  Found expense on line 89: 23/04/25 | GASOLINA TERPEL ESTACION... | $85,000.00

================================================================================
EXTRACTED EXPENSES (3 transactions found)
================================================================================
┌──────────┬─────────────────────────────────────────────────────┬──────────────┐
│ Date     │ Description                                         │ Amount       │
├──────────┼─────────────────────────────────────────────────────┼──────────────┤
│ 21/04/25 │ HOMECENTER VTAS A DIST BOGOTA                       │ $704,700.00  │
│ 22/04/25 │ SUPERMERCADO OLIMPICA BOGOTA                        │ $156,800.00  │
│ 23/04/25 │ GASOLINA TERPEL ESTACION                            │ $85,000.00   │
└──────────┴─────────────────────────────────────────────────────┴──────────────┘

SUMMARY:
Total Transactions: 3
Total Amount: $946,500.00
```

## Technical Details

### Dependencies

- **pdf2image**: Converts PDF pages to PIL Image objects
- **pytesseract**: Python wrapper for Tesseract OCR engine
- **tabulate**: Creates formatted tables for CLI output
- **Pillow**: Image processing library (dependency of pdf2image)

### Processing Workflow

1. **PDF Validation**: Checks if the input file exists and has .pdf extension
2. **Image Conversion**: Converts each PDF page to a high-resolution image
3. **OCR Processing**: Extracts text from each image using Tesseract
4. **Text Analysis**: Processes each line looking for transaction patterns
5. **Data Extraction**: Uses regex patterns to extract date, description, and amount
6. **Output Formatting**: Displays results in a clean table format

### Regex Patterns Used

- **Date Pattern**: `\b(\d{2}\s+\d{2}\s+\d{2})\b` - Matches DD MM YY format
- **Amount Pattern**: `\$[\d,]+\.?\d*` - Matches Colombian peso format ($XXX,XXX.XX)

## Troubleshooting

### Common Issues

1. **"Tesseract not found"**
   - Ensure Tesseract OCR is installed on your system
   - On Windows, make sure Tesseract is in your PATH

2. **"No expenses found"**
   - Check if the PDF contains the expected transaction format
   - Verify the PDF is image-based (scanned) rather than text-based
   - Try with a higher quality scan

3. **Poor OCR accuracy**
   - Ensure the PDF has good image quality
   - Check that text is clearly readable in the original document
   - Consider preprocessing the images for better contrast

4. **Missing dependencies**
   - Run `pip install -r requirements.txt` to install all dependencies
   - Ensure you're using Python 3.7 or higher

### Performance Notes

- Processing time depends on PDF size and number of pages
- Large PDFs (>10 pages) may take several minutes to process
- OCR accuracy improves with higher quality source documents

## Limitations

- Designed specifically for Colombian peso currency format
- Optimized for the specific transaction line format shown in examples
- Requires image-based PDFs (scanned documents) for OCR processing
- May not work well with heavily formatted or complex layouts

## Future Enhancements

Potential improvements for future iterations:
- Support for multiple currency formats
- CSV export functionality
- Transaction categorization
- Date range filtering
- Batch processing of multiple PDFs
- GUI interface
- Configuration file for custom parsing patterns

## License

This project is provided as-is for educational and testing purposes.
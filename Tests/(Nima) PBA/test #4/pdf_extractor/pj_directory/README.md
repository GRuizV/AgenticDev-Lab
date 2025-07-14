# PDF Credit Card Expense Extractor

A Python CLI application that extracts credit card transaction data from PDF statements using pdfplumber, with pattern recognition and validation against ground truth data.

## Features

- **PDF Processing**: Extract text from PDF credit card statements using pdfplumber
- **Pattern Recognition**: Support for Avianca credit cards (MC and VS) with extensible pattern system
- **Ground Truth Validation**: Compare extracted data against expected results
- **CLI Interface**: Command-line tool with multiple output formats (table, JSON, CSV)
- **Batch Processing**: Process multiple PDF files in a directory
- **Configurable**: YAML-based configuration with environment variable support
- **Robust Error Handling**: Comprehensive logging and error recovery

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/pdfextractor/pdf-credit-card-extractor.git
cd pdf-credit-card-extractor

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

### Using pip (when published)

```bash
pip install pdf-credit-card-extractor
```

## Quick Start

### Extract from a single PDF

```bash
# Basic extraction
pdf-extractor extract statement.pdf

# With specific pattern and JSON output
pdf-extractor extract statement.pdf --pattern avianca_mc --format json

# Save results to file
pdf-extractor extract statement.pdf --output results.json --format json
```

### Batch processing

```bash
# Process all PDFs in a directory
pdf-extractor batch /path/to/pdfs

# With validation against ground truth
pdf-extractor batch /path/to/pdfs --validate --ground-truth ground_truth.json
```

### Validation

```bash
# Validate extraction against ground truth
pdf-extractor validate statement.pdf ground_truth.json
```

### List available patterns

```bash
# Simple list
pdf-extractor patterns

# Detailed information
pdf-extractor patterns --detailed
```

## Configuration

The application uses a YAML configuration file (`config.yaml`) for settings:

```yaml
# Extraction settings
extraction:
  default_pattern: null  # Auto-detect if null
  confidence_threshold: 0.7
  timeout_seconds: 300

# Validation settings
validation:
  tolerance_percentage: 0.05  # 5% tolerance
  min_accuracy_threshold: 0.8

# Output settings
output:
  default_format: "table"
  date_format: "%Y-%m-%d"
  currency_symbol: "$"

# Logging settings
logging:
  level: "INFO"
  file_path: "logs/pdf_extractor.log"
  console_output: true
```

## Supported Credit Cards

Currently supports:
- **Avianca MasterCard** (`avianca_mc`)
- **Avianca Visa** (`avianca_vs`)

The pattern system is extensible for adding new credit card issuers.

## Ground Truth Format

Ground truth data should be in JSON format:

```json
{
  "bill_name": {
    "expected_count": 25,
    "expected_total": 1234567.89,
    "transactions": [
      {
        "date": "2025-02-15",
        "description": "COMPRA EN ESTABLECIMIENTO",
        "amount": 50000.00
      }
    ]
  }
}
```

## API Usage

```python
from pdf_extractor import PDFProcessor, GroundTruthValidator

# Initialize processor
processor = PDFProcessor()

# Process a PDF
result = processor.process_pdf("statement.pdf")

# Access extracted transactions
for transaction in result.transactions:
    print(f"{transaction.date}: {transaction.description} - ${transaction.amount}")

# Validate against ground truth
validator = GroundTruthValidator()
validation_result = validator.validate_extraction(
    result.transactions, 
    "bill_name", 
    "ground_truth.json"
)
```

## Development

### Setup Development Environment

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black src/

# Lint code
flake8 src/

# Type checking
mypy src/
```

### Project Structure

```
pdf_extractor/
├── src/pdf_extractor/
│   ├── cli/              # Command-line interface
│   ├── core/             # Core processing logic
│   ├── data/             # Data models and parsers
│   ├── extraction/       # PDF extraction modules
│   ├── patterns/         # Pattern recognition
│   ├── config/           # Configuration management
│   └── utils/            # Utilities and error handling
├── tests/                # Test suite
├── config.yaml           # Default configuration
├── requirements.txt      # Dependencies
└── setup.py             # Package setup
```

## Architecture

The application follows a modular architecture:

1. **Data Layer**: Transaction models and parsing utilities
2. **Extraction Layer**: PDF text extraction using pdfplumber
3. **Pattern Layer**: Credit card specific pattern recognition
4. **Core Layer**: Main processing orchestration
5. **CLI Layer**: Command-line interface and formatting

## Performance

- Processes typical credit card PDFs (5-10 pages) in 2-5 seconds
- Memory usage scales with PDF size (typically 50-200MB)
- Supports batch processing of multiple files
- Pattern caching for improved performance

## Troubleshooting

### Common Issues

1. **PDF not recognized**: Try different patterns or check PDF format
2. **Low accuracy**: Adjust confidence thresholds in configuration
3. **Memory issues**: Process files individually instead of batch
4. **Permission errors**: Check file access permissions

### Logging

Enable debug logging for detailed information:

```bash
export PDF_EXTRACTOR_LOG_LEVEL=DEBUG
pdf-extractor extract statement.pdf
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

- Documentation: [Read the Docs](https://pdf-credit-card-extractor.readthedocs.io/)
- Issues: [GitHub Issues](https://github.com/pdfextractor/pdf-credit-card-extractor/issues)
- Discussions: [GitHub Discussions](https://github.com/pdfextractor/pdf-credit-card-extractor/discussions)

## Changelog

### Version 1.0.0
- Initial release
- Support for Avianca credit cards
- CLI interface with multiple output formats
- Ground truth validation
- Configurable pattern recognition
- Comprehensive error handling and logging
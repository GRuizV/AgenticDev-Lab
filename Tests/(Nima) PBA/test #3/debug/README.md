# Debug Directory

This directory contains debugging tools and logs for the PDF Credit Card Expense Extractor testing process.

## Structure

- `debug_logs/` - Contains debug output logs from testing sessions
- `text_samples/` - Contains extracted text samples from PDFs for analysis
- `pattern_analysis/` - Contains pattern matching analysis results
- `debug_parser.py` - Main debugging script for analyzing PDF parsing issues

## Usage

The debugging tools help identify issues with:
1. PDF text extraction quality
2. Pattern recognition accuracy
3. Transaction parsing logic
4. Amount and date extraction

## Testing Session Log

### Session 1: Initial Testing (2025-06-19)
- **Issue**: Application extracts text successfully but finds 0 transactions
- **Status**: Investigating pattern matching and transaction detection logic
- **Next Steps**: Analyze actual PDF text structure vs expected patterns
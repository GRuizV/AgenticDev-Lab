#!/usr/bin/env python3
"""
Debug script to analyze PDF parsing issues.
Organized debugging for the PDF Credit Card Expense Extractor.
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Add parent directory to path to import the package
sys.path.insert(0, str(Path(__file__).parent.parent))

from pdf_expense_extractor.parsers.pdf_parser_factory import PDFParserFactory
from pdf_expense_extractor.core.pattern_detector import TransactionPatternDetector
from pdf_expense_extractor.utils.text_processing import clean_text, extract_lines
from pdf_expense_extractor.config.patterns import TRANSACTION_PATTERNS

def save_debug_log(content: str, filename: str):
    """Save debug content to log file."""
    log_dir = Path(__file__).parent / "debug_logs"
    log_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"{timestamp}_{filename}"
    
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Debug log saved: {log_file}")

def analyze_pdf_text_extraction(pdf_path: str):
    """Analyze PDF text extraction with different parsers."""
    print(f"Analyzing PDF: {pdf_path}")
    print("=" * 60)
    
    factory = PDFParserFactory()
    results = {}
    
    for parser_name in ['pymupdf', 'pdfplumber', 'PyPDF2']:
        print(f"\n--- {parser_name.upper()} PARSER ---")
        try:
            parser = factory.get_parser(parser_name)
            text = parser.extract_text(pdf_path)
            
            results[parser_name] = {
                'text': text,
                'length': len(text),
                'lines': extract_lines(clean_text(text))
            }
            
            print(f"Text length: {len(text)} characters")
            print(f"Lines count: {len(results[parser_name]['lines'])}")
            
            # Save extracted text sample
            save_debug_log(text, f"{parser_name}_text_extraction.txt")
            
        except Exception as e:
            print(f"Error with {parser_name}: {e}")
            results[parser_name] = {'error': str(e)}
    
    return results

def analyze_pattern_matching(text: str, parser_name: str):
    """Analyze pattern matching on extracted text."""
    print(f"\n--- PATTERN ANALYSIS FOR {parser_name.upper()} ---")
    
    analysis_log = []
    analysis_log.append(f"Pattern Analysis for {parser_name}")
    analysis_log.append("=" * 50)
    
    cleaned_text = clean_text(text)
    lines = extract_lines(cleaned_text)
    
    analysis_log.append(f"Total lines: {len(lines)}")
    analysis_log.append(f"Text length: {len(text)} characters")
    analysis_log.append("")
    
    # Show lines with potential transaction data
    analysis_log.append("Lines containing $ and numbers:")
    transaction_like_lines = []
    for i, line in enumerate(lines):
        if '$' in line and any(c.isdigit() for c in line):
            transaction_like_lines.append(f"Line {i}: {repr(line)}")
            if len(transaction_like_lines) <= 10:  # Limit for readability
                analysis_log.append(f"Line {i}: {repr(line)}")
    
    analysis_log.append(f"\nTotal lines with $ and numbers: {len(transaction_like_lines)}")
    analysis_log.append("")
    
    # Test each pattern
    analysis_log.append("Pattern Testing Results:")
    for i, pattern in enumerate(TRANSACTION_PATTERNS):
        analysis_log.append(f"\nPattern {i+1}: {pattern.pattern}")
        matches = pattern.findall(cleaned_text)
        analysis_log.append(f"Matches found: {len(matches)}")
        
        if matches:
            for j, match in enumerate(matches[:3]):  # Show first 3 matches
                analysis_log.append(f"  Match {j+1}: {match}")
        
        print(f"Pattern {i+1}: {len(matches)} matches")
    
    # Save analysis log
    log_content = "\n".join(analysis_log)
    save_debug_log(log_content, f"{parser_name}_pattern_analysis.txt")
    
    return len([m for pattern in TRANSACTION_PATTERNS for m in pattern.findall(cleaned_text)])

def test_transaction_detection(pdf_path: str):
    """Test the full transaction detection pipeline."""
    print(f"\n--- TRANSACTION DETECTION TEST ---")
    
    # Extract text and test pattern detection
    extraction_results = analyze_pdf_text_extraction(pdf_path)
    
    # Test pattern matching for each successful extraction
    for parser_name, result in extraction_results.items():
        if 'error' not in result:
            total_matches = analyze_pattern_matching(result['text'], parser_name)
            print(f"{parser_name}: {total_matches} total pattern matches")
            
            # Test full transaction extraction
            detector = TransactionPatternDetector()
            transactions = detector.extract_transactions(result['text'])
            print(f"{parser_name}: {len(transactions)} transactions extracted")
            
            # Get debug info
            debug_info = detector.get_debug_info(result['text'])
            print(f"{parser_name}: Debug info - {debug_info}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python debug_parser.py <pdf_file>")
        print("Example: python debug_parser.py '../Test PDFs/AV - MC - 02 - FEB-2025.pdf'")
        sys.exit(1)
    
    pdf_file = sys.argv[1]
    if not Path(pdf_file).exists():
        print(f"File not found: {pdf_file}")
        sys.exit(1)
    
    test_transaction_detection(pdf_file)
    print(f"\nDebugging complete. Check debug_logs/ directory for detailed analysis.")
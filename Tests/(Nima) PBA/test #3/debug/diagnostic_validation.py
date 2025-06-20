#!/usr/bin/env python3
"""
Diagnostic Validation Script
Purpose: Add logs to validate assumptions about pattern detection and transaction recognition issues
"""

import sys
import re
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from pdf_expense_extractor.parsers.pdf_parser_factory import PDFParserFactory
from pdf_expense_extractor.config.patterns import TRANSACTION_PATTERNS
from pdf_expense_extractor.utils.text_processing import clean_text, extract_lines

def diagnose_pattern_issues(pdf_file="AV - MC - 02 - FEB-2025.pdf"):
    """Diagnose pattern detection issues with detailed logging."""
    
    print("=" * 80)
    print("DIAGNOSTIC VALIDATION - PATTERN DETECTION ANALYSIS")
    print("=" * 80)
    print(f"Target File: {pdf_file}")
    print()
    
    # Extract text
    factory = PDFParserFactory()
    parser = factory.get_parser('pymupdf')
    
    pdf_path = f"../Test PDFs/{pdf_file}"
    if not Path(pdf_path).exists():
        # Try different locations
        possible_paths = [
            f"Test PDFs/{pdf_file}",
            f"Tests/{pdf_file}",
            pdf_file
        ]
        
        for path in possible_paths:
            if Path(path).exists():
                pdf_path = path
                break
        else:
            print(f"❌ PDF file not found: {pdf_file}")
            return
    
    try:
        text = parser.extract_text(pdf_path)
        print(f"✅ Extracted {len(text)} characters from {pdf_file}")
    except Exception as e:
        print(f"❌ Failed to extract text: {e}")
        return
    
    # Clean and process text
    cleaned_text = clean_text(text)
    lines = extract_lines(cleaned_text)
    
    print(f"📄 Total lines: {len(lines)}")
    print()
    
    # DIAGNOSTIC 1: Analyze lines with currency symbols
    print("DIAGNOSTIC 1: Lines containing currency symbols ($)")
    print("-" * 50)
    
    currency_lines = []
    for i, line in enumerate(lines):
        if '$' in line and any(c.isdigit() for c in line):
            currency_lines.append((i, line.strip()))
    
    print(f"Found {len(currency_lines)} lines with $ and numbers")
    
    # Show first 10 currency lines
    for i, (line_num, line) in enumerate(currency_lines[:10]):
        print(f"Line {line_num:3d}: {line}")
    
    if len(currency_lines) > 10:
        print(f"... and {len(currency_lines) - 10} more lines")
    
    print()
    
    # DIAGNOSTIC 2: Test current patterns
    print("DIAGNOSTIC 2: Current Pattern Matching Results")
    print("-" * 50)
    
    total_matches = 0
    for i, pattern in enumerate(TRANSACTION_PATTERNS):
        matches = pattern.findall(cleaned_text)
        total_matches += len(matches)
        
        print(f"Pattern {i+1}: {len(matches)} matches")
        print(f"  Regex: {pattern.pattern}")
        
        # Show first 3 matches
        for j, match in enumerate(matches[:3]):
            print(f"  Match {j+1}: {match}")
        
        if len(matches) > 3:
            print(f"  ... and {len(matches) - 3} more matches")
        print()
    
    print(f"Total pattern matches: {total_matches}")
    print()
    
    # DIAGNOSTIC 3: Analyze unmatched currency lines
    print("DIAGNOSTIC 3: Unmatched Currency Lines Analysis")
    print("-" * 50)
    
    # Find lines that contain currency but weren't matched by patterns
    matched_line_content = set()
    for pattern in TRANSACTION_PATTERNS:
        for match in pattern.finditer(cleaned_text):
            # Get the line containing this match
            start_pos = match.start()
            line_start = cleaned_text.rfind('\n', 0, start_pos) + 1
            line_end = cleaned_text.find('\n', start_pos)
            if line_end == -1:
                line_end = len(cleaned_text)
            matched_line_content.add(cleaned_text[line_start:line_end].strip())
    
    unmatched_currency_lines = []
    for line_num, line in currency_lines:
        if line not in matched_line_content:
            unmatched_currency_lines.append((line_num, line))
    
    print(f"Found {len(unmatched_currency_lines)} unmatched currency lines")
    
    # Show first 10 unmatched lines
    for i, (line_num, line) in enumerate(unmatched_currency_lines[:10]):
        print(f"Line {line_num:3d}: {line}")
    
    if len(unmatched_currency_lines) > 10:
        print(f"... and {len(unmatched_currency_lines) - 10} more unmatched lines")
    
    print()
    
    # DIAGNOSTIC 4: Pattern analysis recommendations
    print("DIAGNOSTIC 4: Pattern Analysis Recommendations")
    print("-" * 50)
    
    if len(unmatched_currency_lines) > total_matches:
        print("❌ CRITICAL: More unmatched currency lines than matched patterns!")
        print("   Recommendation: Patterns are too restrictive")
    elif len(unmatched_currency_lines) > total_matches * 0.5:
        print("⚠️  WARNING: Significant number of unmatched currency lines")
        print("   Recommendation: Patterns need enhancement")
    else:
        print("✅ GOOD: Most currency lines are being matched")
    
    print(f"\nPattern Coverage: {(total_matches / len(currency_lines)) * 100:.1f}%")
    print(f"Expected for {pdf_file}: 5 transactions")
    print(f"Current extraction: {total_matches} matches")
    
    if total_matches < 5:
        print("❌ CONFIRMED: Pattern detection is the primary issue")
    else:
        print("✅ Pattern detection seems adequate, check transaction creation logic")
    
    return {
        'total_lines': len(lines),
        'currency_lines': len(currency_lines),
        'pattern_matches': total_matches,
        'unmatched_lines': len(unmatched_currency_lines),
        'coverage_percent': (total_matches / len(currency_lines)) * 100 if currency_lines else 0
    }

def main():
    """Run diagnostic validation."""
    
    # Test with the first target file
    result = diagnose_pattern_issues("AV - MC - 02 - FEB-2025.pdf")
    
    if result:
        print("\n" + "=" * 80)
        print("DIAGNOSTIC SUMMARY:")
        print("=" * 80)
        print(f"Total text lines: {result['total_lines']}")
        print(f"Currency-containing lines: {result['currency_lines']}")
        print(f"Pattern matches: {result['pattern_matches']}")
        print(f"Unmatched currency lines: {result['unmatched_lines']}")
        print(f"Pattern coverage: {result['coverage_percent']:.1f}%")
        
        if result['coverage_percent'] < 50:
            print("\n❌ DIAGNOSIS CONFIRMED: Pattern detection is inadequate")
            print("   PRIMARY ISSUE: Regex patterns are too restrictive")
            print("   NEXT ACTION: Enhance patterns in config/patterns.py")
        elif result['pattern_matches'] < 5:
            print("\n❌ DIAGNOSIS CONFIRMED: Transaction creation logic issues")
            print("   PRIMARY ISSUE: Pattern matches not converting to transactions")
            print("   NEXT ACTION: Debug core/pattern_detector.py")
        else:
            print("\n✅ DIAGNOSIS: Pattern detection working, check other components")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Analyze the actual PDF format to understand why pattern matching fails.
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def analyze_pdf_format():
    """Analyze the actual PDF text format."""
    print("🔍 PDF FORMAT ANALYSIS")
    print("=" * 60)
    
    try:
        from pdf_expense_extractor.parsers.pdf_parser_factory import PDFParserFactory
        from pdf_expense_extractor.config.patterns import TRANSACTION_PATTERNS
        import re
        
        # Extract text from the actual PDF
        factory = PDFParserFactory()
        parser = factory.get_parser('pymupdf')
        pdf_path = project_root.parent / "Test PDFs" / "AV - MC - 02 - FEB-2025.pdf"
        
        text = parser.extract_text(str(pdf_path))
        print(f"✓ Text extracted: {len(text)} characters")
        print()
        
        # Show first 500 characters
        print("FIRST 500 CHARACTERS:")
        print("-" * 30)
        print(repr(text[:500]))
        print()
        
        # Split into lines and analyze
        lines = text.split('\n')
        print(f"Total lines: {len(lines)}")
        print()
        
        # Find lines with DETALLE
        print("LINES WITH 'DETALLE':")
        print("-" * 25)
        for i, line in enumerate(lines):
            if 'DETALLE' in line.upper():
                print(f"Line {i:3d}: {repr(line)}")
                # Show surrounding lines (context)
                start = max(0, i-3)
                end = min(len(lines), i+10)
                print("CONTEXT:")
                for j in range(start, end):
                    marker = ">>>" if j == i else "   "
                    print(f"{marker} {j:3d}: {repr(lines[j])}")
                print()
        
        # Look for amount patterns
        print("LINES WITH AMOUNTS (containing commas and digits):")
        print("-" * 50)
        amount_lines = []
        for i, line in enumerate(lines):
            if ',' in line and any(c.isdigit() for c in line):
                amount_lines.append((i, line))
                print(f"Line {i:3d}: {repr(line)}")
        print()
        
        # Test current patterns against the text
        print("TESTING CURRENT PATTERNS:")
        print("-" * 30)
        for i, pattern in enumerate(TRANSACTION_PATTERNS):
            print(f"Pattern {i+1}: {pattern.pattern}")
            matches = pattern.findall(text)
            print(f"  Matches found: {len(matches)}")
            if matches:
                for j, match in enumerate(matches[:3]):  # Show first 3 matches
                    print(f"    Match {j+1}: {match}")
            print()
        
        # Look for potential transaction ID patterns
        print("POTENTIAL TRANSACTION ID PATTERNS:")
        print("-" * 40)
        # Look for 4+ digit numbers
        digit_pattern = re.compile(r'\b\d{4,}\b')
        digit_matches = digit_pattern.findall(text)
        print(f"4+ digit numbers found: {len(digit_matches)}")
        for i, match in enumerate(digit_matches[:10]):  # Show first 10
            print(f"  {i+1}: {match}")
        print()
        
        # Look for date-like patterns
        print("DATE-LIKE PATTERNS:")
        print("-" * 20)
        # Look for DD MM YY patterns on separate lines
        for i in range(len(lines) - 3):
            line1 = lines[i].strip()
            line2 = lines[i+1].strip()
            line3 = lines[i+2].strip()
            line4 = lines[i+3].strip()
            
            # Check if we have day, month, year pattern
            if (re.match(r'^\d{1,2}$', line1) and 
                re.match(r'^\d{1,2}$', line2) and 
                re.match(r'^\d{2}$', line3)):
                print(f"Potential date at lines {i}-{i+2}: {line1}/{line2}/{line3}")
                print(f"  Following line: {repr(line4)}")
                # Show more context
                for j in range(max(0, i-2), min(len(lines), i+8)):
                    marker = ">>>" if j >= i and j <= i+2 else "   "
                    print(f"  {marker} {j:3d}: {repr(lines[j])}")
                print()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_pdf_format()
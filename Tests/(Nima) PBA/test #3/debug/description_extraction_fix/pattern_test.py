#!/usr/bin/env python3
"""
Pattern Testing Script for Description Extraction Fix

This script tests regex patterns against actual PDF text structure to debug
why transaction descriptions are not being extracted correctly.

Purpose: Fix the transaction description extraction issue where the application
extracts incorrect descriptions (like "DETALLE") instead of merchant names.
"""

import re
import sys
import os
from pathlib import Path

# Add the parent directories to the path so we can import the modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from pdf_expense_extractor.config.patterns import TRANSACTION_PATTERNS
from pdf_expense_extractor.utils.text_processing import clean_text, extract_lines

def test_patterns_on_sample_text():
    """Test current patterns against known transaction structure."""
    
    print("=" * 60)
    print("PATTERN TESTING FOR DESCRIPTION EXTRACTION FIX")
    print("=" * 60)
    
    # Sample text based on actual PyMuPDF extraction from AV - MC - 02 - FEB-2025.pdf
    sample_text = """7888
15
02
25
26.19
$44,900.00
$44,900.00
$0.00
01
01
00
PAYU*NETFLIX           110111BOGOTA
9493
14
02
25
26.19
$50,000.00
$50,000.00
$0.00
01
01
00
CINE COLOMBIA          BOGOTA
0293
10
02
25
26.19
$224,180.00
$224,180.00
$0.00
01
01
00
MERCPAGO*CRUZVERDEPAGO BARRANQUILLA"""

    print("Testing with sample transaction text:")
    print("-" * 40)
    print(sample_text[:200] + "...")
    print("-" * 40)
    
    print(f"\nCurrent patterns count: {len(TRANSACTION_PATTERNS)}")
    
    for i, pattern in enumerate(TRANSACTION_PATTERNS):
        print(f"\nPattern {i + 1}:")
        print(f"Regex: {pattern.pattern}")
        
        matches = pattern.findall(sample_text)
        print(f"Matches found: {len(matches)}")
        
        for j, match in enumerate(matches):
            print(f"  Match {j + 1}: {match}")
    
    return len([m for pattern in TRANSACTION_PATTERNS for m in pattern.findall(sample_text)])

def test_improved_patterns():
    """Test improved patterns that should work with the multi-line structure."""
    
    print("\n" + "=" * 60)
    print("TESTING IMPROVED PATTERNS")
    print("=" * 60)
    
    # Improved patterns for the actual structure
    improved_patterns = [
        # Pattern 1: Transaction ID, day, month, year, then amount (skipping rate)
        re.compile(
            r'(\d{4})\s*\n\s*(\d{1,2})\s*\n\s*(\d{1,2})\s*\n\s*(\d{2})\s*\n\s*[\d.]+\s*\n\s*\$?([\d,]+\.?\d*)',
            re.MULTILINE | re.DOTALL
        ),
        
        # Pattern 2: More flexible spacing
        re.compile(
            r'(\d{4})\n(\d{1,2})\n(\d{1,2})\n(\d{2})\n[\d.]+\n\$?([\d,]+\.?\d*)',
            re.MULTILINE
        ),
        
        # Pattern 3: Capture the description too
        re.compile(
            r'(\d{4})\n(\d{1,2})\n(\d{1,2})\n(\d{2})\n[\d.]+\n\$?([\d,]+\.?\d*)\n\$?[\d,]+\.?\d*\n\$?[\d,]+\.?\d*\n\d+\n\d+\n\d+\n([A-Z][A-Z0-9\s\*\-\.]+)',
            re.MULTILINE
        )
    ]
    
    sample_text = """7888
15
02
25
26.19
$44,900.00
$44,900.00
$0.00
01
01
00
PAYU*NETFLIX           110111BOGOTA
9493
14
02
25
26.19
$50,000.00
$50,000.00
$0.00
01
01
00
CINE COLOMBIA          BOGOTA"""

    for i, pattern in enumerate(improved_patterns):
        print(f"\nImproved Pattern {i + 1}:")
        print(f"Regex: {pattern.pattern}")
        
        matches = pattern.findall(sample_text)
        print(f"Matches found: {len(matches)}")
        
        for j, match in enumerate(matches):
            print(f"  Match {j + 1}: {match}")
            if len(match) >= 5:
                transaction_id, day, month, year, amount = match[0], match[1], match[2], match[3], match[4]
                print(f"    Transaction ID: {transaction_id}")
                print(f"    Date: {day}/{month}/{year}")
                print(f"    Amount: {amount}")
                if len(match) > 5:
                    print(f"    Description: {match[5]}")

def test_description_extraction():
    """Test description extraction from the multi-line structure."""
    
    print("\n" + "=" * 60)
    print("TESTING DESCRIPTION EXTRACTION")
    print("=" * 60)
    
    # Full sample with line numbers to simulate actual extraction
    full_sample = """192
7888
193
15
194
02
195
25
196
26.19
197
$44,900.00
198
$44,900.00
199
$0.00
200
01
201
01
202
00
203
PAYU*NETFLIX           110111BOGOTA
204
9493
205
14
206
02
207
25
208
26.19
209
$50,000.00
210
$50,000.00
211
$0.00
212
01
213
01
214
00
215
CINE COLOMBIA          BOGOTA"""

    lines = full_sample.split('\n')
    print(f"Total lines: {len(lines)}")
    
    # Look for transaction patterns
    transaction_starts = []
    for i, line in enumerate(lines):
        if re.match(r'^\d{4}$', line.strip()):  # Transaction ID pattern
            transaction_starts.append(i)
    
    print(f"Found {len(transaction_starts)} potential transaction starts: {transaction_starts}")
    
    # For each transaction start, find the description
    for start_idx in transaction_starts:
        if start_idx + 12 < len(lines):  # Ensure we have enough lines
            transaction_id = lines[start_idx].strip()
            day = lines[start_idx + 2].strip()
            month = lines[start_idx + 4].strip()
            year = lines[start_idx + 6].strip()
            amount = lines[start_idx + 10].strip()
            description = lines[start_idx + 24].strip()  # Description is 12 lines after transaction ID
            
            print(f"\nTransaction found:")
            print(f"  ID: {transaction_id}")
            print(f"  Date: {day}/{month}/{year}")
            print(f"  Amount: {amount}")
            print(f"  Description: {description}")

if __name__ == "__main__":
    print("Description Extraction Fix - Pattern Testing")
    print("Testing current patterns and proposing improvements...")
    
    # Test current patterns
    current_matches = test_patterns_on_sample_text()
    print(f"\nCurrent patterns total matches: {current_matches}")
    
    # Test improved patterns
    test_improved_patterns()
    
    # Test description extraction logic
    test_description_extraction()
    
    print("\n" + "=" * 60)
    print("TESTING COMPLETE")
    print("=" * 60)
    print("Next steps:")
    print("1. Update TRANSACTION_PATTERNS with improved patterns")
    print("2. Fix description extraction logic in pattern_detector.py")
    print("3. Test against actual PDF file")
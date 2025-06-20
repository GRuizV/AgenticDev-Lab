#!/usr/bin/env python3
"""
Detailed pipeline debugging to understand why full pipeline fails.

This script traces through the exact execution path of the full pipeline
to identify where transactions are lost.
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def debug_full_pipeline():
    """Debug the full pipeline step by step."""
    print("=" * 60)
    print("DETAILED FULL PIPELINE DEBUG")
    print("=" * 60)
    
    from pdf_expense_extractor.core.pattern_detector import TransactionPatternDetector
    from pdf_expense_extractor.utils.text_processing import clean_text, extract_lines
    
    # Test text that should work
    test_text = """DETALLE
7888
15
02
25
44,900.00
TEST MERCHANT LOCATION
"""
    
    print(f"Input text:\n{repr(test_text)}")
    print()
    
    # Step 1: Text cleaning
    cleaned_text = clean_text(test_text)
    print(f"Cleaned text:\n{repr(cleaned_text)}")
    print()
    
    # Step 2: Line extraction
    lines = extract_lines(cleaned_text)
    print(f"Extracted lines ({len(lines)}):")
    for i, line in enumerate(lines):
        print(f"  {i}: {repr(line)}")
    print()
    
    # Step 3: Transaction section detection
    detector = TransactionPatternDetector()
    transaction_lines = detector._find_transaction_section(lines)
    print(f"Transaction section lines ({len(transaction_lines)}):")
    for i, line in enumerate(transaction_lines):
        print(f"  {i}: {repr(line)}")
    print()
    
    # Step 4: Line-by-line parsing simulation
    print("Line-by-line parsing simulation:")
    transactions = []
    i = 0
    
    while i < len(transaction_lines):
        line = transaction_lines[i].strip()
        print(f"\nProcessing line {i}: {repr(line)}")
        
        if not line:
            print("  -> Empty line, skipping")
            i += 1
            continue
        
        # Test pattern matching on this line
        transaction_data = detector._parse_transaction_line(line)
        print(f"  -> Pattern match result: {transaction_data}")
        
        if transaction_data:
            print("  -> Transaction data found!")
            
            # Look for description
            description = detector._find_description(transaction_lines, i + 1)
            print(f"  -> Description search result: {repr(description)}")
            
            # Use default if no description
            if not description:
                description = f"TRANSACTION {transaction_data.get('date', 'UNKNOWN')}"
                print(f"  -> Using default description: {repr(description)}")
            
            transaction_data['description'] = description
            
            # Check if we have all required data
            required_keys = ['date', 'description', 'amount']
            has_all_keys = all(key in transaction_data for key in required_keys)
            print(f"  -> Has all required keys {required_keys}: {has_all_keys}")
            print(f"  -> Transaction data: {transaction_data}")
            
            if has_all_keys:
                try:
                    from pdf_expense_extractor.models.transaction import Transaction
                    transaction = Transaction(
                        date=transaction_data['date'],
                        description=transaction_data['description'],
                        amount=transaction_data['amount']
                    )
                    transactions.append(transaction)
                    print(f"  -> ✅ Transaction created: {transaction}")
                except Exception as e:
                    print(f"  -> ❌ Transaction creation failed: {e}")
            else:
                print(f"  -> ❌ Missing required data")
            
            i += 2  # Skip description line
        else:
            print("  -> No transaction data found")
            i += 1
    
    print(f"\nFinal result: {len(transactions)} transactions created")
    for i, t in enumerate(transactions):
        print(f"  {i+1}: {t}")
    
    return len(transactions)

def test_with_actual_extractor():
    """Test with the actual extractor for comparison."""
    print("\n" + "=" * 60)
    print("ACTUAL EXTRACTOR TEST")
    print("=" * 60)
    
    from pdf_expense_extractor.core.pattern_detector import TransactionPatternDetector
    
    test_text = """DETALLE
7888
15
02
25
44,900.00
TEST MERCHANT LOCATION
"""
    
    detector = TransactionPatternDetector()
    transactions = detector.extract_transactions(test_text)
    
    print(f"Actual extractor result: {len(transactions)} transactions")
    for i, t in enumerate(transactions):
        print(f"  {i+1}: {t}")
    
    return len(transactions)

def main():
    """Run detailed debugging."""
    print("DETAILED PIPELINE DEBUGGING")
    print("Investigating why full pipeline extracts 0 transactions")
    
    manual_count = debug_full_pipeline()
    actual_count = test_with_actual_extractor()
    
    print("\n" + "=" * 60)
    print("COMPARISON SUMMARY")
    print("=" * 60)
    print(f"Manual simulation: {manual_count} transactions")
    print(f"Actual extractor:  {actual_count} transactions")
    
    if manual_count > 0 and actual_count == 0:
        print("🔍 Issue is in the actual extractor logic")
    elif manual_count == 0 and actual_count == 0:
        print("🔍 Issue is in the pattern matching or data extraction")
    elif manual_count == actual_count and manual_count > 0:
        print("✅ Both work - issue might be elsewhere")
    else:
        print("🤔 Unexpected result difference")

if __name__ == "__main__":
    main()
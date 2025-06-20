#!/usr/bin/env python3
"""
Step-by-step debugging script for transaction creation issue.

This script tests each component of the transaction extraction pipeline
to identify where the failure occurs.

Author: Code Mode
Date: 2025-06-19
Issue: Pattern matching works but 0 transactions created
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def test_step_1_basic_utilities():
    """Step 1: Test basic utility functions."""
    print("=" * 60)
    print("STEP 1: Testing Basic Utilities")
    print("=" * 60)
    
    try:
        from pdf_expense_extractor.utils.date_parser import parse_date
        from pdf_expense_extractor.utils.amount_parser import parse_amount
        
        # Test with the specific data from debug evidence
        test_date = '15022025'  # From groups ('7888', '15', '02', '25', '44,900.00')
        test_amount = '44,900.00'
        
        print(f"Testing date parsing with: {test_date}")
        parsed_date = parse_date(test_date)
        print(f"Result: {parsed_date}")
        
        print(f"Testing amount parsing with: {test_amount}")
        parsed_amount = parse_amount(test_amount)
        print(f"Result: {parsed_amount}")
        
        if parsed_date and parsed_amount:
            print("✅ Step 1 PASSED: Basic utilities working")
            return True
        else:
            print("❌ Step 1 FAILED: Utility functions returning None")
            return False
            
    except Exception as e:
        print(f"❌ Step 1 FAILED: Exception in utilities: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_step_2_pattern_matching():
    """Step 2: Test pattern matching in isolation."""
    print("\n" + "=" * 60)
    print("STEP 2: Testing Pattern Matching")
    print("=" * 60)
    
    try:
        from pdf_expense_extractor.config.patterns import TRANSACTION_PATTERNS
        
        # Test with simplified text that should match
        test_text = """7888
15
02
25
44,900.00"""
        
        print(f"Testing with text:\n{repr(test_text)}")
        print(f"Number of patterns to test: {len(TRANSACTION_PATTERNS)}")
        
        total_matches = 0
        for i, pattern in enumerate(TRANSACTION_PATTERNS):
            print(f"\nPattern {i+1}: {pattern.pattern}")
            matches = pattern.findall(test_text)
            print(f"Matches found: {len(matches)}")
            if matches:
                print(f"First match: {matches[0]}")
                total_matches += len(matches)
        
        if total_matches > 0:
            print(f"✅ Step 2 PASSED: Found {total_matches} total matches")
            return True
        else:
            print("❌ Step 2 FAILED: No pattern matches found")
            return False
            
    except Exception as e:
        print(f"❌ Step 2 FAILED: Exception in pattern matching: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_step_3_transaction_data_extraction():
    """Step 3: Test transaction data extraction from match."""
    print("\n" + "=" * 60)
    print("STEP 3: Testing Transaction Data Extraction")
    print("=" * 60)
    
    try:
        import re
        from pdf_expense_extractor.core.pattern_detector import TransactionPatternDetector
        
        # Create detector instance
        detector = TransactionPatternDetector()
        
        # Simulate the match found in debug evidence
        test_groups = ('7888', '15', '02', '25', '44,900.00')
        test_line = "7888 15 02 25 44,900.00"
        
        print(f"Testing with groups: {test_groups}")
        print(f"Testing with line: {test_line}")
        
        # Create a mock match object
        class MockMatch:
            def __init__(self, groups):
                self._groups = groups
            def groups(self):
                return self._groups
        
        mock_match = MockMatch(test_groups)
        
        # Test the extraction method
        result = detector._extract_transaction_data(mock_match, test_line)
        print(f"Extraction result: {result}")
        
        if result and 'date' in result and 'amount' in result:
            print(f"✅ Step 3 PASSED: Extracted date={result['date']}, amount={result['amount']}")
            return True
        else:
            print("❌ Step 3 FAILED: Transaction data extraction returned None or incomplete")
            return False
            
    except Exception as e:
        print(f"❌ Step 3 FAILED: Exception in transaction data extraction: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_step_4_transaction_creation():
    """Step 4: Test Transaction object creation."""
    print("\n" + "=" * 60)
    print("STEP 4: Testing Transaction Object Creation")
    print("=" * 60)
    
    try:
        from pdf_expense_extractor.models.transaction import Transaction
        
        # Test with valid data
        test_data = {
            'date': '2025-02-15',
            'description': 'TEST MERCHANT',
            'amount': 44900.0
        }
        
        print(f"Testing Transaction creation with: {test_data}")
        
        transaction = Transaction(
            date=test_data['date'],
            description=test_data['description'],
            amount=test_data['amount']
        )
        
        print(f"Created transaction: {transaction}")
        print(f"✅ Step 4 PASSED: Transaction object created successfully")
        return True
        
    except Exception as e:
        print(f"❌ Step 4 FAILED: Exception in transaction creation: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_step_5_full_pipeline():
    """Step 5: Test the full pipeline with minimal data."""
    print("\n" + "=" * 60)
    print("STEP 5: Testing Full Pipeline")
    print("=" * 60)
    
    try:
        from pdf_expense_extractor.core.pattern_detector import TransactionPatternDetector
        
        # Create minimal test text that should work
        test_text = """DETALLE
7888
15
02
25
44,900.00
TEST MERCHANT LOCATION
"""
        
        print(f"Testing full pipeline with text:\n{repr(test_text)}")
        
        detector = TransactionPatternDetector()
        transactions = detector.extract_transactions(test_text)
        
        print(f"Transactions extracted: {len(transactions)}")
        for i, t in enumerate(transactions):
            print(f"  Transaction {i+1}: {t}")
        
        if len(transactions) > 0:
            print(f"✅ Step 5 PASSED: Full pipeline extracted {len(transactions)} transactions")
            return True
        else:
            print("❌ Step 5 FAILED: Full pipeline extracted 0 transactions")
            return False
            
    except Exception as e:
        print(f"❌ Step 5 FAILED: Exception in full pipeline: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all debugging steps."""
    print("TRANSACTION CREATION DEBUG - STEP BY STEP TESTING")
    print("Issue: Pattern matching works but 0 transactions created")
    print("Target: Extract 5 transactions from AV - MC - 02 - FEB-2025.pdf")
    
    steps = [
        test_step_1_basic_utilities,
        test_step_2_pattern_matching,
        test_step_3_transaction_data_extraction,
        test_step_4_transaction_creation,
        test_step_5_full_pipeline
    ]
    
    results = []
    for step_func in steps:
        try:
            result = step_func()
            results.append(result)
            if not result:
                print(f"\n🛑 STOPPING: {step_func.__name__} failed")
                break
        except Exception as e:
            print(f"\n💥 CRITICAL ERROR in {step_func.__name__}: {e}")
            results.append(False)
            break
    
    # Summary
    print("\n" + "=" * 60)
    print("DEBUGGING SUMMARY")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Steps passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 ALL STEPS PASSED - Issue may be elsewhere")
    else:
        print(f"🔍 ISSUE IDENTIFIED at step {passed + 1}")
        print("Check the failed step output above for details")

if __name__ == "__main__":
    main()
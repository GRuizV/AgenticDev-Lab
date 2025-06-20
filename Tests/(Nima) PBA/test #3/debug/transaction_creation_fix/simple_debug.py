#!/usr/bin/env python3
"""
Simple debug script to identify transaction creation issue.
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def debug_transaction_creation():
    """Debug transaction creation step by step."""
    print("🔧 SIMPLE TRANSACTION CREATION DEBUG")
    print("=" * 50)
    
    try:
        from pdf_expense_extractor.core.pattern_detector import TransactionPatternDetector
        from pdf_expense_extractor.parsers.pdf_parser_factory import PDFParserFactory
        from pdf_expense_extractor.config.patterns import TRANSACTION_PATTERNS
        
        # Extract text
        factory = PDFParserFactory()
        parser = factory.get_parser('pymupdf')
        pdf_path = project_root.parent / "Test PDFs" / "AV - MC - 02 - FEB-2025.pdf"
        text = parser.extract_text(str(pdf_path))
        
        print(f"✓ Text extracted: {len(text)} characters")
        
        # Test first pattern only
        pattern = TRANSACTION_PATTERNS[1]  # Pattern 2 had good matches
        matches = pattern.findall(text)
        print(f"✓ Pattern matches: {len(matches)}")
        
        if matches:
            match = matches[0]  # Test first match
            print(f"✓ First match: {match}")
            
            # Test transaction data extraction
            detector = TransactionPatternDetector()
            
            class MockMatch:
                def __init__(self, groups):
                    self._groups = groups
                def groups(self):
                    return self._groups
            
            mock_match = MockMatch(match)
            transaction_data = detector._extract_transaction_data(mock_match, str(match))
            print(f"✓ Transaction data: {transaction_data}")
            
            if transaction_data:
                # Test transaction creation
                from pdf_expense_extractor.models.transaction import Transaction
                
                try:
                    transaction = Transaction(
                        date=transaction_data['date'],
                        description='TEST DESCRIPTION',
                        amount=transaction_data['amount']
                    )
                    print(f"✓ Transaction created: {transaction}")
                except Exception as e:
                    print(f"✗ Transaction creation failed: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                print("✗ No transaction data extracted")
        
        # Test full extraction
        print("\nFULL EXTRACTION TEST:")
        print("-" * 25)
        detector = TransactionPatternDetector()
        transactions = detector.extract_transactions(text)
        print(f"Final result: {len(transactions)} transactions")
        
        if transactions:
            for i, t in enumerate(transactions):
                print(f"  {i+1}: {t}")
        else:
            print("No transactions extracted")
            
            # Debug the extraction process
            print("\nDEBUGGING EXTRACTION PROCESS:")
            print("-" * 35)
            
            from pdf_expense_extractor.utils.text_processing import clean_text, extract_lines
            
            cleaned_text = clean_text(text)
            lines = extract_lines(cleaned_text)
            transaction_lines = detector._find_transaction_section(lines)
            
            print(f"Total lines: {len(lines)}")
            print(f"Transaction section lines: {len(transaction_lines)}")
            
            if transaction_lines:
                print("First 10 transaction section lines:")
                for i, line in enumerate(transaction_lines[:10]):
                    print(f"  {i}: {repr(line)}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_transaction_creation()
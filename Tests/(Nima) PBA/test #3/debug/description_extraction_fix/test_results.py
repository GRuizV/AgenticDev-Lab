#!/usr/bin/env python3
"""
Test Results Analysis for Description Extraction Fix

This script runs the extractor and compares results with ground truth
to validate the fix and identify remaining issues.
"""

import sys
import os
import json
from pathlib import Path

# Add the parent directories to the path so we can import the modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from pdf_expense_extractor.parsers.pdf_parser_factory import PDFParserFactory
from pdf_expense_extractor.core.pattern_detector import TransactionPatternDetector

def load_ground_truth():
    """Load ground truth data for comparison."""
    ground_truth_path = Path(__file__).parent.parent.parent.parent / "ground_truth.json"
    
    with open(ground_truth_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Find AV - MC - 02 - FEB-2025 data
    for bill in data['bills']:
        if bill['bill_name'] == 'AV - MC - 02 - FEB-2025':
            return bill['transactions']
    
    return []

def test_extraction():
    """Test the current extraction and compare with ground truth."""
    
    print("=" * 60)
    print("DESCRIPTION EXTRACTION FIX - TEST RESULTS")
    print("=" * 60)
    
    # Load ground truth
    ground_truth = load_ground_truth()
    print(f"Ground truth transactions: {len(ground_truth)}")
    
    for i, gt_transaction in enumerate(ground_truth, 1):
        print(f"  {i}. {gt_transaction['date']} - {gt_transaction['description']} - ${gt_transaction['amount']:,}")
    
    print("\n" + "-" * 60)
    
    # Test extraction
    pdf_path = "../Test PDFs/AV - MC - 02 - FEB-2025.pdf"
    
    factory = PDFParserFactory()
    parser = factory.get_parser('pymupdf')
    text = parser.extract_text(pdf_path)
    
    detector = TransactionPatternDetector()
    transactions = detector.extract_transactions(text)
    
    print(f"Extracted transactions: {len(transactions)}")
    
    for i, transaction in enumerate(transactions, 1):
        print(f"  {i}. {transaction.date} - {transaction.description} - ${transaction.amount:,}")
    
    print("\n" + "-" * 60)
    print("COMPARISON ANALYSIS")
    print("-" * 60)
    
    # Compare descriptions
    gt_descriptions = [t['description'] for t in ground_truth if t['amount'] > 0]  # Exclude zero amounts
    extracted_descriptions = [t.description for t in transactions]
    
    print(f"Expected descriptions (non-zero amounts): {len(gt_descriptions)}")
    for desc in gt_descriptions:
        print(f"  - {desc}")
    
    print(f"\nExtracted descriptions: {len(extracted_descriptions)}")
    for desc in extracted_descriptions:
        print(f"  - {desc}")
    
    # Check matches
    print(f"\nDescription matching:")
    for gt_desc in gt_descriptions:
        found = False
        for ext_desc in extracted_descriptions:
            if gt_desc.upper() in ext_desc.upper() or ext_desc.upper() in gt_desc.upper():
                print(f"  ✅ MATCH: '{gt_desc}' ~ '{ext_desc}'")
                found = True
                break
        if not found:
            print(f"  ❌ MISSING: '{gt_desc}'")
    
    # Calculate totals
    gt_total = sum(t['amount'] for t in ground_truth if t['amount'] > 0)
    extracted_total = sum(t.amount for t in transactions)
    
    print(f"\nAmount comparison:")
    print(f"  Expected total: ${gt_total:,}")
    print(f"  Extracted total: ${extracted_total:,}")
    print(f"  Difference: ${abs(gt_total - extracted_total):,}")
    
    # Success criteria
    print(f"\nSUCCESS CRITERIA:")
    print(f"  Transaction count: {len(transactions)}/4 (excluding zero amounts) {'✅' if len(transactions) == 4 else '❌'}")
    print(f"  Amount accuracy: {'✅' if abs(gt_total - extracted_total) < 100 else '❌'}")
    print(f"  Description quality: {'✅' if len([d for d in gt_descriptions if any(d.upper() in e.upper() for e in extracted_descriptions)]) >= 3 else '❌'}")

if __name__ == "__main__":
    test_extraction()
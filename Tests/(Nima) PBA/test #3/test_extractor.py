"""
Simple test script for the PDF expense extractor.
"""

import sys
from pathlib import Path
from pdf_expense_extractor.main import main
from pdf_expense_extractor.core.cli_interface import ExpenseExtractorCLI
from pdf_expense_extractor.config.settings import Settings


def test_basic_functionality():
    """Test basic functionality of the extractor."""
    print("Testing PDF Credit Card Expense Extractor")
    print("=" * 50)
    
    # Test 1: Check if parsers are available
    print("\n1. Testing PDF parser availability...")
    cli = ExpenseExtractorCLI()
    
    available_parsers = cli.parser_factory.available_parsers
    if available_parsers:
        print(f"✅ Found {len(available_parsers)} available parsers:")
        for parser in available_parsers:
            print(f"   - {parser}")
    else:
        print("❌ No PDF parsers available. Please install pdfplumber, pymupdf, or PyPDF2.")
        return False
    
    # Test 2: Check if PDF directory exists
    print("\n2. Testing PDF directory access...")
    pdf_dir = Path("../Test PDFs")
    
    if pdf_dir.exists():
        pdf_files = list(pdf_dir.glob("*.pdf"))
        print(f"✅ Found PDF directory with {len(pdf_files)} PDF files")
        
        # List some files
        for i, pdf_file in enumerate(pdf_files[:3]):
            print(f"   - {pdf_file.name}")
        if len(pdf_files) > 3:
            print(f"   ... and {len(pdf_files) - 3} more files")
    else:
        print(f"❌ PDF directory not found: {pdf_dir}")
        print("   Please ensure the Test PDFs directory exists relative to this script")
        return False
    
    # Test 3: Test single file processing (if files exist)
    if pdf_files:
        print("\n3. Testing single file processing...")
        test_file = pdf_files[0]
        print(f"   Testing with: {test_file.name}")
        
        try:
            result = cli.process_single_file(str(test_file))
            
            if 'error' in result:
                print(f"❌ Error processing file: {result['error']}")
                return False
            else:
                transactions = result['transactions']
                validation = result['validation']
                
                print(f"✅ Successfully extracted {len(transactions)} transactions")
                print(f"   Validation: {'PASSED' if validation.valid else 'FAILED'}")
                
                if not validation.valid:
                    print(f"   Count: {validation.extracted_count}/{validation.expected_count}")
                    print(f"   Amount: ${validation.extracted_total:,.2f}/${validation.expected_total:,.2f}")
        
        except Exception as e:
            print(f"❌ Exception during processing: {e}")
            return False
    
    # Test 4: Test configuration
    print("\n4. Testing configuration...")
    settings = Settings.default()
    print(f"✅ Default settings loaded:")
    print(f"   Amount tolerance: ${settings.amount_tolerance}")
    print(f"   PDF libraries: {settings.pdf_libraries}")
    
    print("\n" + "=" * 50)
    print("✅ Basic functionality tests completed successfully!")
    return True


def test_parser_comparison():
    """Test and compare different PDF parsers."""
    print("\nTesting PDF Parser Comparison")
    print("=" * 50)
    
    cli = ExpenseExtractorCLI()
    pdf_dir = Path("../Test PDFs")
    
    if not pdf_dir.exists():
        print("❌ PDF directory not found for parser testing")
        return
    
    pdf_files = list(pdf_dir.glob("*.pdf"))
    if not pdf_files:
        print("❌ No PDF files found for parser testing")
        return
    
    test_file = pdf_files[0]
    print(f"Testing parsers with: {test_file.name}")
    
    results = cli.test_parsers(str(test_file))
    
    if 'error' in results:
        print(f"❌ Error testing parsers: {results['error']}")
        return
    
    print("\nParser Comparison Results:")
    print("-" * 30)
    
    for parser_name, result in results.items():
        status = "✅ SUCCESS" if result['success'] else "❌ FAILED"
        print(f"{parser_name}: {status}")
        
        if result['success']:
            print(f"  Text Length: {result['text_length']:,} characters")
            print(f"  Score: {result['score']:.2f}")
        else:
            print(f"  Error: {result.get('error', 'Unknown error')}")
        print()


def main_test():
    """Main test function."""
    print("PDF Credit Card Expense Extractor - Test Suite")
    print("=" * 60)
    
    try:
        # Run basic functionality tests
        if not test_basic_functionality():
            print("\n❌ Basic functionality tests failed!")
            return 1
        
        # Run parser comparison tests
        test_parser_comparison()
        
        print("\n" + "=" * 60)
        print("🎉 All tests completed!")
        print("\nTo run the full extractor, use:")
        print("python -m pdf_expense_extractor --verbose")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main_test())
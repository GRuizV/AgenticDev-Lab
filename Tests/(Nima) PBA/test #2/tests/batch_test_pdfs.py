#!/usr/bin/env python3
"""
Batch PDF Testing Script for Expense Extractor

This script systematically tests all PDF files in the Test PDFs directory
using the existing ExpenseExtractor class. It generates a comprehensive
test report comparing results between MC and VS card formats.

Usage:
    python batch_test_pdfs.py

Requirements:
    - All dependencies from requirements.txt must be installed
    - Test PDFs directory with PDF files to test
    - Existing pdf_expense_extractor.py with ExpenseExtractor class
"""

import os
import sys
import json
import traceback
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional

# Add parent directory to path to import the ExpenseExtractor
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src'))

try:
    from pdf_expense_extractor import ExpenseExtractor
    print("✓ Successfully imported ExpenseExtractor class")
except ImportError as e:
    print(f"❌ Error importing ExpenseExtractor: {e}")
    print("Please ensure pdf_expense_extractor.py is in the same directory")
    sys.exit(1)


class BatchPDFTester:
    """
    Comprehensive PDF testing class that tests multiple PDF files
    and generates detailed reports.
    """
    
    def __init__(self, test_pdf_dir: str = None):
        if test_pdf_dir is None:
            # Calculate path relative to this script's location
            test_pdf_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'Test PDFs')
        """
        Initialize the batch tester.
        
        Args:
            test_pdf_dir (str): Directory containing test PDF files
        """
        self.test_pdf_dir = Path(test_pdf_dir)
        self.extractor = ExpenseExtractor()
        self.test_results = {}
        self.start_time = datetime.now()
        
        # Define expected PDF files to test
        self.target_files = [
            "MC - FEB-2025.pdf",
            "MC - MAR-2025.pdf", 
            "MC - ABR-2025.pdf",
            "VS - FEB-2025.pdf",
            "VS - MAR-2025.pdf",
            "VS - ABR-2025.pdf"
        ]
    
    def validate_test_environment(self) -> bool:
        """
        Validate that all required files and dependencies are available.
        
        Returns:
            bool: True if environment is valid, False otherwise
        """
        print("\n" + "="*80)
        print("VALIDATING TEST ENVIRONMENT")
        print("="*80)
        
        # Check if test PDF directory exists
        if not self.test_pdf_dir.exists():
            print(f"❌ Test PDF directory not found: {self.test_pdf_dir}")
            return False
        print(f"✓ Test PDF directory found: {self.test_pdf_dir}")
        
        # Check for target PDF files
        missing_files = []
        available_files = []
        
        for file_name in self.target_files:
            file_path = self.test_pdf_dir / file_name
            if file_path.exists():
                available_files.append(file_name)
                print(f"✓ Found: {file_name}")
            else:
                missing_files.append(file_name)
                print(f"❌ Missing: {file_name}")
        
        if missing_files:
            print(f"\n⚠️  {len(missing_files)} files are missing:")
            for file in missing_files:
                print(f"   - {file}")
            print(f"✓ {len(available_files)} files are available for testing")
        else:
            print(f"\n✓ All {len(self.target_files)} target files are available!")
        
        return len(available_files) > 0
    
    def test_single_pdf(self, pdf_path: Path) -> Dict:
        """
        Test a single PDF file and capture comprehensive results.
        
        Args:
            pdf_path (Path): Path to the PDF file to test
            
        Returns:
            Dict: Test results for the file
        """
        file_name = pdf_path.name
        print(f"\n📄 Testing: {file_name}")
        print("-" * 60)
        
        result = {
            "file_name": file_name,
            "file_path": str(pdf_path),
            "file_size_mb": round(pdf_path.stat().st_size / (1024*1024), 2),
            "test_timestamp": datetime.now().isoformat(),
            "success": False,
            "expenses_found": 0,
            "sample_expenses": [],
            "error_message": None,
            "processing_time_seconds": 0,
            "card_type": "MC" if file_name.startswith("MC") else "VS",
            "month": file_name.split(" - ")[1].split("-")[0] if " - " in file_name else "Unknown"
        }
        
        start_time = datetime.now()
        
        try:
            # Extract text from PDF
            print(f"🔍 Extracting text from {file_name}...")
            text = self.extractor.extract_text_from_pdf(str(pdf_path))
            
            if not text or len(text.strip()) < 50:
                result["error_message"] = "OCR extraction failed or returned minimal text"
                print(f"⚠️  Warning: Minimal text extracted ({len(text)} characters)")
                return result
            
            print(f"✓ Extracted {len(text)} characters of text")
            
            # Extract expenses
            print(f"🔍 Parsing expenses from extracted text...")
            expenses = self.extractor.extract_expenses(text)
            
            result["expenses_found"] = len(expenses)
            result["success"] = True
            
            # Store sample expenses (first 3)
            result["sample_expenses"] = expenses[:3] if expenses else []
            
            # Calculate total amount
            total_amount = 0
            for _, _, amount in expenses:
                try:
                    # Extract numeric value from amount string
                    numeric_amount = amount.replace('$', '').replace(',', '')
                    total_amount += float(numeric_amount)
                except (ValueError, AttributeError):
                    pass
            
            result["total_amount"] = round(total_amount, 2)
            
            print(f"✓ Successfully extracted {len(expenses)} expenses")
            if expenses:
                print(f"💰 Total amount: ${total_amount:,.2f}")
                print(f"📋 Sample expense: {expenses[0][0]} | {expenses[0][1][:40]}... | {expenses[0][2]}")
            
        except Exception as e:
            result["error_message"] = str(e)
            result["error_traceback"] = traceback.format_exc()
            print(f"❌ Error processing {file_name}: {e}")
        
        finally:
            result["processing_time_seconds"] = round(
                (datetime.now() - start_time).total_seconds(), 2
            )
        
        return result
    
    def run_batch_tests(self) -> None:
        """
        Run tests on all available PDF files.
        """
        print("\n" + "="*80)
        print("STARTING BATCH PDF TESTING")
        print("="*80)
        
        if not self.validate_test_environment():
            print("❌ Environment validation failed. Cannot proceed with testing.")
            return
        
        # Test each available file
        for file_name in self.target_files:
            file_path = self.test_pdf_dir / file_name
            
            if file_path.exists():
                result = self.test_single_pdf(file_path)
                self.test_results[file_name] = result
            else:
                print(f"\n⏭️  Skipping missing file: {file_name}")
        
        # Generate comprehensive report
        self.generate_test_report()
    
    def generate_test_report(self) -> None:
        """
        Generate a comprehensive test report with analysis and comparisons.
        """
        print("\n" + "="*80)
        print("COMPREHENSIVE TEST REPORT")
        print("="*80)
        
        total_time = (datetime.now() - self.start_time).total_seconds()
        tested_files = len(self.test_results)
        successful_tests = sum(1 for r in self.test_results.values() if r["success"])
        
        print(f"📊 OVERALL SUMMARY")
        print(f"   Total files tested: {tested_files}")
        print(f"   Successful extractions: {successful_tests}")
        print(f"   Failed extractions: {tested_files - successful_tests}")
        print(f"   Total testing time: {total_time:.2f} seconds")
        
        # Results by file
        print(f"\n📋 DETAILED RESULTS BY FILE")
        print("-" * 80)
        
        for file_name, result in self.test_results.items():
            status = "✓ SUCCESS" if result["success"] else "❌ FAILED"
            expenses_count = result["expenses_found"]
            processing_time = result["processing_time_seconds"]
            
            print(f"\n📄 {file_name}")
            print(f"   Status: {status}")
            print(f"   File size: {result['file_size_mb']} MB")
            print(f"   Processing time: {processing_time}s")
            print(f"   Expenses found: {expenses_count}")
            
            if result["success"] and result["sample_expenses"]:
                print(f"   Total amount: ${result.get('total_amount', 0):,.2f}")
                print(f"   Sample expenses:")
                for i, (date, desc, amount) in enumerate(result["sample_expenses"][:2], 1):
                    print(f"      {i}. {date} | {desc[:35]}... | {amount}")
            
            if result["error_message"]:
                print(f"   Error: {result['error_message']}")
        
        # Analysis by card type
        self.analyze_by_card_type()
        
        # Analysis by month
        self.analyze_by_month()
        
        # Save detailed results to JSON
        self.save_detailed_results()
    
    def analyze_by_card_type(self) -> None:
        """
        Analyze and compare results between MC and VS card types.
        """
        print(f"\n🏦 ANALYSIS BY CARD TYPE")
        print("-" * 80)
        
        mc_results = {k: v for k, v in self.test_results.items() if v["card_type"] == "MC"}
        vs_results = {k: v for k, v in self.test_results.items() if v["card_type"] == "VS"}
        
        # MC Analysis
        mc_successful = sum(1 for r in mc_results.values() if r["success"])
        mc_total_expenses = sum(r["expenses_found"] for r in mc_results.values())
        mc_avg_processing_time = (sum(r["processing_time_seconds"] for r in mc_results.values()) / 
                                 len(mc_results)) if mc_results else 0
        
        print(f"💳 MC (MasterCard) Results:")
        print(f"   Files tested: {len(mc_results)}")
        print(f"   Successful: {mc_successful}/{len(mc_results)}")
        print(f"   Total expenses extracted: {mc_total_expenses}")
        print(f"   Average processing time: {mc_avg_processing_time:.2f}s")
        
        # VS Analysis
        vs_successful = sum(1 for r in vs_results.values() if r["success"])
        vs_total_expenses = sum(r["expenses_found"] for r in vs_results.values())
        vs_avg_processing_time = (sum(r["processing_time_seconds"] for r in vs_results.values()) / 
                                 len(vs_results)) if vs_results else 0
        
        print(f"\n💳 VS (Visa) Results:")
        print(f"   Files tested: {len(vs_results)}")
        print(f"   Successful: {vs_successful}/{len(vs_results)}")
        print(f"   Total expenses extracted: {vs_total_expenses}")
        print(f"   Average processing time: {vs_avg_processing_time:.2f}s")
        
        # Comparison
        print(f"\n📊 CARD TYPE COMPARISON:")
        if mc_results and vs_results:
            mc_success_rate = (mc_successful / len(mc_results)) * 100
            vs_success_rate = (vs_successful / len(vs_results)) * 100
            
            print(f"   MC success rate: {mc_success_rate:.1f}%")
            print(f"   VS success rate: {vs_success_rate:.1f}%")
            
            if mc_success_rate > vs_success_rate:
                print(f"   🏆 MC files processed more successfully")
            elif vs_success_rate > mc_success_rate:
                print(f"   🏆 VS files processed more successfully")
            else:
                print(f"   🤝 Both card types processed equally well")
        
    def analyze_by_month(self) -> None:
        """
        Analyze results by month to identify patterns.
        """
        print(f"\n📅 ANALYSIS BY MONTH")
        print("-" * 80)
        
        months = {}
        for result in self.test_results.values():
            month = result["month"]
            if month not in months:
                months[month] = {"files": 0, "successful": 0, "total_expenses": 0}
            
            months[month]["files"] += 1
            if result["success"]:
                months[month]["successful"] += 1
                months[month]["total_expenses"] += result["expenses_found"]
        
        for month, data in months.items():
            success_rate = (data["successful"] / data["files"]) * 100
            print(f"📅 {month}:")
            print(f"   Files: {data['files']}")
            print(f"   Success rate: {success_rate:.1f}%")
            print(f"   Total expenses: {data['total_expenses']}")
    
    def save_detailed_results(self) -> None:
        """
        Save detailed test results to a JSON file for further analysis.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Save results in the same directory as this test file
        results_file = os.path.join(os.path.dirname(__file__), f"batch_test_results_{timestamp}.json")
        
        detailed_results = {
            "test_summary": {
                "timestamp": self.start_time.isoformat(),
                "total_files_tested": len(self.test_results),
                "successful_tests": sum(1 for r in self.test_results.values() if r["success"]),
                "total_testing_time_seconds": (datetime.now() - self.start_time).total_seconds()
            },
            "individual_results": self.test_results
        }
        
        try:
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(detailed_results, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Detailed results saved to: {results_file}")
        except Exception as e:
            print(f"\n⚠️  Could not save detailed results: {e}")


def main():
    """
    Main entry point for the batch testing script.
    """
    print("PDF Expense Extractor - Batch Testing Script")
    print("=" * 50)
    print("This script will test all PDF files systematically using")
    print("the existing ExpenseExtractor class.")
    print()
    
    # Initialize and run batch tester
    tester = BatchPDFTester()
    tester.run_batch_tests()
    
    print("\n" + "="*80)
    print("BATCH TESTING COMPLETED")
    print("="*80)
    print("Review the results above for detailed analysis.")
    print("Check the generated JSON file for raw data if needed.")


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Comprehensive Validation Analysis for PDF Credit Card Expense Extractor
Created: 2025-06-19 21:35
Purpose: Systematic analysis of extraction issues and validation against ground truth

CRITICAL ISSUES IDENTIFIED:
1. Missing Transactions - Only extracting 30-50% of expected transactions
2. Description Extraction Issues - Extra data in descriptions needs cleaning
3. Pattern Detection Problems - Regex patterns missing many valid transactions

VALIDATION RESULTS FROM LAST RUN:
- AV - MC - 02 - FEB-2025: 2/5 transactions, $269,080/$434,980 (missing $165,900)
- AV - MC - 03 - MAR-2025: 1/2 transactions, $44,900/$44,900 (amount correct, count wrong)
- AV - MC - 04 - ABR-2025: 5/9 transactions, $1,000,725/$1,068,097 (missing $67,372)
- AV - VS - 02 - FEB-2025: 8/18 transactions, $368,684/$1,702,961 (missing $1,334,277)
- AV - VS - 03 - MAR-2025: 6/14 transactions, $349,552/$810,460 (missing $460,908)
- AV - VS - 04 - ABR-2025: 9/20 transactions, $579,590/$1,058,980 (missing $479,390)
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add parent directory to path to import the package
sys.path.insert(0, str(Path(__file__).parent.parent))

from pdf_expense_extractor.main import main
from pdf_expense_extractor.core.cli_interface import ExpenseExtractorCLI
from pdf_expense_extractor.config.expected_results import EXPECTED_RESULTS

def analyze_validation_results():
    """Analyze the validation results from the comprehensive test run."""
    
    print("=" * 80)
    print("COMPREHENSIVE VALIDATION ANALYSIS")
    print("=" * 80)
    print(f"Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Target files from the task description
    target_files = {
        "AV - MC - 02 - FEB-2025": {"expected_total": 434980.00, "expected_count": 5},
        "AV - MC - 03 - MAR-2025": {"expected_total": 44900.00, "expected_count": 2},
        "AV - MC - 04 - ABR-2025": {"expected_total": 1068097.00, "expected_count": 9},
        "AV - VS - 02 - FEB-2025": {"expected_total": 1702961.00, "expected_count": 18},
        "AV - VS - 03 - MAR-2025": {"expected_total": 810460.00, "expected_count": 14},
        "AV - VS - 04 - ABR-2025": {"expected_total": 1058980.00, "expected_count": 20}
    }
    
    # Results from the test run (extracted from the output)
    actual_results = {
        "AV - MC - 02 - FEB-2025": {"actual_total": 269080.00, "actual_count": 2},
        "AV - MC - 03 - MAR-2025": {"actual_total": 44900.00, "actual_count": 1},
        "AV - MC - 04 - ABR-2025": {"actual_total": 1000725.00, "actual_count": 5},
        "AV - VS - 02 - FEB-2025": {"actual_total": 368684.00, "actual_count": 8},
        "AV - VS - 03 - MAR-2025": {"actual_total": 349552.00, "actual_count": 6},
        "AV - VS - 04 - ABR-2025": {"actual_total": 579590.00, "actual_count": 9}
    }
    
    print("DETAILED ANALYSIS BY FILE:")
    print("-" * 80)
    
    total_missing_transactions = 0
    total_amount_difference = 0
    
    for file_name, expected in target_files.items():
        actual = actual_results.get(file_name, {"actual_total": 0, "actual_count": 0})
        
        missing_count = expected["expected_count"] - actual["actual_count"]
        amount_diff = expected["expected_total"] - actual["actual_total"]
        
        total_missing_transactions += missing_count
        total_amount_difference += amount_diff
        
        print(f"\n📄 {file_name}")
        print(f"   Expected: {expected['expected_count']} transactions, ${expected['expected_total']:,.2f}")
        print(f"   Actual:   {actual['actual_count']} transactions, ${actual['actual_total']:,.2f}")
        print(f"   Missing:  {missing_count} transactions, ${amount_diff:,.2f}")
        
        # Calculate accuracy percentages
        count_accuracy = (actual["actual_count"] / expected["expected_count"]) * 100 if expected["expected_count"] > 0 else 0
        amount_accuracy = (actual["actual_total"] / expected["expected_total"]) * 100 if expected["expected_total"] > 0 else 0
        
        print(f"   Accuracy: {count_accuracy:.1f}% count, {amount_accuracy:.1f}% amount")
        
        if count_accuracy < 100 or amount_accuracy < 90:
            print(f"   ❌ CRITICAL: Significant extraction issues detected")
        elif count_accuracy == 100 and amount_accuracy >= 99:
            print(f"   ✅ GOOD: Extraction within acceptable tolerance")
        else:
            print(f"   ⚠️  WARNING: Minor extraction issues")
    
    print("\n" + "=" * 80)
    print("OVERALL SUMMARY:")
    print("=" * 80)
    print(f"Total Missing Transactions: {total_missing_transactions}")
    print(f"Total Missing Amount: ${total_amount_difference:,.2f}")
    print(f"Overall Success Rate: {((68 - total_missing_transactions) / 68) * 100:.1f}% transactions")
    print(f"Overall Amount Accuracy: {((5119418 - total_amount_difference) / 5119418) * 100:.1f}%")
    
    return analyze_root_causes()

def analyze_root_causes():
    """Analyze the root causes of extraction failures."""
    
    print("\n" + "=" * 80)
    print("ROOT CAUSE ANALYSIS:")
    print("=" * 80)
    
    # Based on the test output, identify the main issues
    issues = [
        {
            "issue": "Pattern Detection Incomplete",
            "description": "Regex patterns are only matching a subset of valid transactions",
            "evidence": "All files show significantly fewer transactions than expected",
            "impact": "High - Primary cause of missing transactions",
            "priority": 1
        },
        {
            "issue": "Description Extraction Contaminated", 
            "description": "Extracted descriptions contain extra data (transaction IDs, dates, amounts)",
            "evidence": "Descriptions like 'PAYU*NETFLIX 110111BOGOTA 9493 14 02 25 26.19' should be 'PAYU*NETFLIX 110111BOGOTA'",
            "impact": "Medium - Affects data quality but not validation totals",
            "priority": 2
        },
        {
            "issue": "Transaction Line Recognition",
            "description": "Pattern detector may not be identifying all transaction line formats",
            "evidence": "Consistent under-extraction across all PDF files",
            "impact": "High - Directly causes missing transactions",
            "priority": 1
        },
        {
            "issue": "Amount Extraction Logic",
            "description": "May be selecting wrong amount values from transaction lines",
            "evidence": "Some files have correct amounts but wrong counts, suggesting partial extraction",
            "impact": "Medium - Affects validation accuracy",
            "priority": 2
        }
    ]
    
    for i, issue in enumerate(issues, 1):
        print(f"\n{i}. {issue['issue']} (Priority {issue['priority']})")
        print(f"   Description: {issue['description']}")
        print(f"   Evidence: {issue['evidence']}")
        print(f"   Impact: {issue['impact']}")
    
    return recommend_fixes()

def recommend_fixes():
    """Recommend specific fixes for the identified issues."""
    
    print("\n" + "=" * 80)
    print("RECOMMENDED FIXES:")
    print("=" * 80)
    
    fixes = [
        {
            "priority": 1,
            "component": "Pattern Detection",
            "action": "Enhance regex patterns in config/patterns.py",
            "details": [
                "Add more flexible transaction line patterns",
                "Include patterns for different amount formats",
                "Add fallback patterns for edge cases",
                "Test patterns against actual PDF text samples"
            ]
        },
        {
            "priority": 1,
            "component": "Transaction Extraction Logic",
            "action": "Improve core/pattern_detector.py",
            "details": [
                "Review transaction line identification logic",
                "Add better handling for multi-line transactions",
                "Improve amount selection from multiple values",
                "Add debug logging for unmatched lines"
            ]
        },
        {
            "priority": 2,
            "component": "Description Cleaning",
            "action": "Enhance utils/text_processing.py",
            "details": [
                "Add description cleanup patterns",
                "Remove transaction IDs and extra data",
                "Normalize merchant names consistently",
                "Preserve essential location information"
            ]
        },
        {
            "priority": 3,
            "component": "Validation Framework",
            "action": "Improve debugging capabilities",
            "details": [
                "Add detailed extraction logs",
                "Show unmatched text sections",
                "Provide pattern match statistics",
                "Generate extraction confidence scores"
            ]
        }
    ]
    
    for fix in fixes:
        print(f"\n🔧 Priority {fix['priority']}: {fix['component']}")
        print(f"   Action: {fix['action']}")
        for detail in fix['details']:
            print(f"   • {detail}")
    
    return generate_action_plan()

def generate_action_plan():
    """Generate a specific action plan for fixing the issues."""
    
    print("\n" + "=" * 80)
    print("IMMEDIATE ACTION PLAN:")
    print("=" * 80)
    
    steps = [
        {
            "step": 1,
            "title": "Analyze PDF Text Structure",
            "actions": [
                "Extract raw text from one target PDF file",
                "Manually identify all transaction lines",
                "Document the exact patterns and formats",
                "Compare with current regex patterns"
            ],
            "files": ["debug/text_analysis.py"],
            "time": "30 minutes"
        },
        {
            "step": 2,
            "title": "Fix Pattern Detection",
            "actions": [
                "Update TRANSACTION_PATTERNS in config/patterns.py",
                "Add more comprehensive regex patterns",
                "Test patterns against sample text",
                "Validate pattern matches"
            ],
            "files": ["config/patterns.py", "core/pattern_detector.py"],
            "time": "45 minutes"
        },
        {
            "step": 3,
            "title": "Improve Description Extraction",
            "actions": [
                "Add description cleanup logic",
                "Remove extra transaction data",
                "Test description cleaning",
                "Validate against ground truth"
            ],
            "files": ["utils/text_processing.py"],
            "time": "30 minutes"
        },
        {
            "step": 4,
            "title": "Comprehensive Testing",
            "actions": [
                "Run full validation against all 6 target files",
                "Compare results with expected values",
                "Document accuracy improvements",
                "Generate final validation report"
            ],
            "files": ["debug/final_validation.py"],
            "time": "20 minutes"
        }
    ]
    
    total_time = sum(int(step["time"].split()[0]) for step in steps)
    
    print(f"Estimated Total Time: {total_time} minutes")
    print()
    
    for step in steps:
        print(f"Step {step['step']}: {step['title']} ({step['time']})")
        for action in step['actions']:
            print(f"   • {action}")
        print(f"   Files: {', '.join(step['files'])}")
        print()
    
    print("=" * 80)
    print("NEXT STEPS:")
    print("1. Run this analysis to understand current state")
    print("2. Execute Step 1 to analyze PDF text structure")
    print("3. Implement fixes in priority order")
    print("4. Test and validate improvements")
    print("5. Generate final comprehensive validation report")
    print("=" * 80)

def main():
    """Main analysis function."""
    try:
        analyze_validation_results()
        print(f"\n✅ Analysis complete. See recommendations above.")
        print(f"📝 Log saved to: {__file__}")
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
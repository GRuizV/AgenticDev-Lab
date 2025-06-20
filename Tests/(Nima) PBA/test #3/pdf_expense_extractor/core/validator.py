"""
Transaction validation framework.
"""

from typing import List, Dict, Optional
from ..models.transaction import Transaction
from ..models.validation_result import ValidationResult
from ..config.expected_results import EXPECTED_RESULTS


class TransactionValidator:
    """Validates extracted transaction data against expected results."""
    
    def __init__(self, amount_tolerance: float = 1.0):
        """
        Initialize the validator.
        
        Args:
            amount_tolerance: Tolerance for amount validation (±dollars)
        """
        self.amount_tolerance = amount_tolerance
        self.expected_results = EXPECTED_RESULTS
    
    def validate_extraction(self, bill_name: str, transactions: List[Transaction]) -> ValidationResult:
        """
        Validate extracted transactions against expected results.
        
        Args:
            bill_name: Name of the bill/PDF file (without extension)
            transactions: List of extracted transactions
            
        Returns:
            ValidationResult with detailed validation information
        """
        # Get expected results for this bill
        expected = self.expected_results.get(bill_name)
        
        if not expected:
            return ValidationResult(
                valid=False,
                count_valid=False,
                amount_valid=False,
                extracted_count=len(transactions),
                expected_count=0,
                extracted_total=0.0,
                expected_total=0.0,
                amount_difference=0.0,
                error=f"No expected results found for bill: {bill_name}"
            )
        
        # Calculate extracted totals
        extracted_count = len(transactions)
        extracted_total = sum(t.amount for t in transactions)
        
        # Get expected values
        expected_count = expected['count']
        expected_total = expected['total']
        
        # Validate count (exact match required)
        count_valid = extracted_count == expected_count
        
        # Validate amount (within tolerance)
        amount_difference = abs(extracted_total - expected_total)
        amount_valid = amount_difference <= self.amount_tolerance
        
        # Overall validation
        overall_valid = count_valid and amount_valid
        
        return ValidationResult(
            valid=overall_valid,
            count_valid=count_valid,
            amount_valid=amount_valid,
            extracted_count=extracted_count,
            expected_count=expected_count,
            extracted_total=extracted_total,
            expected_total=expected_total,
            amount_difference=amount_difference
        )
    
    def validate_all_extractions(self, results: Dict[str, List[Transaction]]) -> Dict[str, ValidationResult]:
        """
        Validate multiple extraction results.
        
        Args:
            results: Dictionary mapping bill names to transaction lists
            
        Returns:
            Dictionary mapping bill names to validation results
        """
        validations = {}
        
        for bill_name, transactions in results.items():
            validations[bill_name] = self.validate_extraction(bill_name, transactions)
        
        return validations
    
    def get_summary_stats(self, validations: Dict[str, ValidationResult]) -> Dict:
        """
        Get summary statistics for validation results.
        
        Args:
            validations: Dictionary of validation results
            
        Returns:
            Dictionary with summary statistics
        """
        total_files = len(validations)
        passed_validations = sum(1 for v in validations.values() if v.valid)
        failed_validations = total_files - passed_validations
        
        count_failures = sum(1 for v in validations.values() if not v.count_valid)
        amount_failures = sum(1 for v in validations.values() if not v.amount_valid)
        
        total_extracted = sum(v.extracted_count for v in validations.values())
        total_expected = sum(v.expected_count for v in validations.values())
        
        total_amount_extracted = sum(v.extracted_total for v in validations.values())
        total_amount_expected = sum(v.expected_total for v in validations.values())
        
        return {
            'total_files': total_files,
            'passed_validations': passed_validations,
            'failed_validations': failed_validations,
            'success_rate': (passed_validations / total_files * 100) if total_files > 0 else 0,
            'count_failures': count_failures,
            'amount_failures': amount_failures,
            'total_transactions_extracted': total_extracted,
            'total_transactions_expected': total_expected,
            'total_amount_extracted': total_amount_extracted,
            'total_amount_expected': total_amount_expected,
            'total_amount_difference': abs(total_amount_extracted - total_amount_expected)
        }
    
    def get_detailed_report(self, validations: Dict[str, ValidationResult]) -> str:
        """
        Generate a detailed validation report.
        
        Args:
            validations: Dictionary of validation results
            
        Returns:
            Formatted report string
        """
        lines = []
        lines.append("DETAILED VALIDATION REPORT")
        lines.append("=" * 50)
        
        # Summary statistics
        stats = self.get_summary_stats(validations)
        lines.append(f"\nSUMMARY:")
        lines.append(f"Total Files: {stats['total_files']}")
        lines.append(f"Passed: {stats['passed_validations']}")
        lines.append(f"Failed: {stats['failed_validations']}")
        lines.append(f"Success Rate: {stats['success_rate']:.1f}%")
        
        # Individual results
        lines.append(f"\nINDIVIDUAL RESULTS:")
        lines.append("-" * 50)
        
        for bill_name, validation in validations.items():
            status = "✅ PASS" if validation.valid else "❌ FAIL"
            lines.append(f"\n{bill_name}: {status}")
            
            if validation.error:
                lines.append(f"  Error: {validation.error}")
            else:
                lines.append(f"  Count: {validation.extracted_count}/{validation.expected_count} {'✅' if validation.count_valid else '❌'}")
                lines.append(f"  Amount: ${validation.extracted_total:,.2f}/${validation.expected_total:,.2f} {'✅' if validation.amount_valid else '❌'}")
                if not validation.amount_valid:
                    lines.append(f"  Difference: ${validation.amount_difference:.2f}")
        
        # Failed validations details
        failed_validations = {k: v for k, v in validations.items() if not v.valid}
        if failed_validations:
            lines.append(f"\nFAILED VALIDATIONS ANALYSIS:")
            lines.append("-" * 50)
            
            for bill_name, validation in failed_validations.items():
                lines.append(f"\n{bill_name}:")
                if validation.error:
                    lines.append(f"  Error: {validation.error}")
                else:
                    if not validation.count_valid:
                        diff = validation.extracted_count - validation.expected_count
                        lines.append(f"  Count Issue: {diff:+d} transactions")
                    
                    if not validation.amount_valid:
                        diff = validation.extracted_total - validation.expected_total
                        lines.append(f"  Amount Issue: ${diff:+,.2f}")
        
        return "\n".join(lines)
    
    def is_bill_supported(self, bill_name: str) -> bool:
        """
        Check if a bill is supported (has expected results).
        
        Args:
            bill_name: Name of the bill
            
        Returns:
            True if bill is supported
        """
        return bill_name in self.expected_results
    
    def get_supported_bills(self) -> List[str]:
        """
        Get list of supported bill names.
        
        Returns:
            List of supported bill names
        """
        return list(self.expected_results.keys())
    
    def get_expected_results(self, bill_name: str) -> Optional[Dict]:
        """
        Get expected results for a specific bill.
        
        Args:
            bill_name: Name of the bill
            
        Returns:
            Expected results dictionary or None
        """
        return self.expected_results.get(bill_name)
    
    def update_tolerance(self, new_tolerance: float):
        """
        Update the amount tolerance.
        
        Args:
            new_tolerance: New tolerance value
        """
        if new_tolerance < 0:
            raise ValueError("Tolerance must be non-negative")
        
        self.amount_tolerance = new_tolerance
    
    def add_expected_result(self, bill_name: str, expected_total: float, expected_count: int):
        """
        Add expected results for a new bill.
        
        Args:
            bill_name: Name of the bill
            expected_total: Expected total amount
            expected_count: Expected transaction count
        """
        if expected_total < 0:
            raise ValueError("Expected total must be non-negative")
        
        if expected_count < 0:
            raise ValueError("Expected count must be non-negative")
        
        self.expected_results[bill_name] = {
            'total': expected_total,
            'count': expected_count
        }
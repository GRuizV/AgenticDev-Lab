"""
Validator module for validating extracted data against ground truth.
"""

import json
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
from decimal import Decimal

from ..data.models import Transaction, ValidationResult, ValidationReport, GroundTruthEntry


class Validator:
    """Validates extracted data against ground truth."""
    
    def __init__(self, ground_truth_path: Optional[str] = None):
        """
        Initialize the validator.
        
        Args:
            ground_truth_path: Path to ground truth JSON file
        """
        self.logger = logging.getLogger(__name__)
        self.ground_truth_path = ground_truth_path
        self.ground_truth_data: Dict[str, GroundTruthEntry] = {}
        
        if ground_truth_path:
            self.load_ground_truth(ground_truth_path)
    
    def load_ground_truth(self, file_path: str) -> bool:
        """
        Load ground truth data from JSON file.
        
        Args:
            file_path: Path to the ground truth JSON file
            
        Returns:
            True if loaded successfully, False otherwise
        """
        try:
            ground_truth_file = Path(file_path)
            if not ground_truth_file.exists():
                self.logger.error(f"Ground truth file not found: {file_path}")
                return False
            
            with open(ground_truth_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.ground_truth_data = {}
            
            # Parse ground truth entries
            for entry in data:
                bill_name = entry.get("bill_name", "")
                if bill_name:
                    ground_truth_entry = GroundTruthEntry.from_dict(entry)
                    self.ground_truth_data[bill_name] = ground_truth_entry
            
            self.logger.info(f"Loaded ground truth data for {len(self.ground_truth_data)} bills")
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading ground truth from {file_path}: {str(e)}")
            return False
    
    def validate_extraction(self, bill_name: str, transactions: List[Transaction]) -> ValidationResult:
        """
        Validate extracted transactions against ground truth.
        
        Args:
            bill_name: Name/identifier of the bill
            transactions: List of extracted transactions
            
        Returns:
            ValidationResult object with comparison details
        """
        try:
            # Get ground truth for this bill
            ground_truth = self.ground_truth_data.get(bill_name)
            
            if ground_truth is None:
                self.logger.warning(f"No ground truth data found for bill: {bill_name}")
                return ValidationResult(
                    bill_name=bill_name,
                    expected_total=Decimal('0'),
                    actual_total=sum(t.amount for t in transactions),
                    expected_count=0,
                    actual_count=len(transactions),
                    accuracy=0.0,
                    missing_transactions=[],
                    extra_transactions=transactions
                )
            
            # Calculate actual totals
            actual_total = sum(t.amount for t in transactions)
            actual_count = len(transactions)
            
            # Calculate accuracy metrics
            total_accuracy = self._calculate_total_accuracy(
                ground_truth.expected_total, actual_total
            )
            count_accuracy = 1.0 if ground_truth.expected_count == actual_count else 0.0
            
            # Overall accuracy (weighted average)
            overall_accuracy = (total_accuracy * 0.7) + (count_accuracy * 0.3)
            
            # Identify missing and extra transactions
            missing_transactions, extra_transactions = self._analyze_transaction_differences(
                ground_truth, transactions
            )
            
            validation_result = ValidationResult(
                bill_name=bill_name,
                expected_total=ground_truth.expected_total,
                actual_total=actual_total,
                expected_count=ground_truth.expected_count,
                actual_count=actual_count,
                accuracy=overall_accuracy,
                missing_transactions=missing_transactions,
                extra_transactions=extra_transactions
            )
            
            self.logger.info(f"Validation completed for {bill_name}: {overall_accuracy:.2%} accuracy")
            return validation_result
            
        except Exception as e:
            self.logger.error(f"Error validating extraction for {bill_name}: {str(e)}")
            return ValidationResult(
                bill_name=bill_name,
                expected_total=Decimal('0'),
                actual_total=Decimal('0'),
                expected_count=0,
                actual_count=0,
                accuracy=0.0
            )
    
    def _calculate_total_accuracy(self, expected: Decimal, actual: Decimal) -> float:
        """
        Calculate accuracy based on total amounts.
        
        Args:
            expected: Expected total amount
            actual: Actual total amount
            
        Returns:
            Accuracy score between 0.0 and 1.0
        """
        if expected == 0:
            return 1.0 if actual == 0 else 0.0
        
        # Calculate percentage difference
        difference = abs(expected - actual)
        percentage_diff = float(difference / expected)
        
        # Convert to accuracy (1.0 = perfect, 0.0 = completely wrong)
        accuracy = max(0.0, 1.0 - percentage_diff)
        
        return accuracy
    
    def _analyze_transaction_differences(self, ground_truth: GroundTruthEntry, 
                                       transactions: List[Transaction]) -> tuple[List[Transaction], List[Transaction]]:
        """
        Analyze differences between expected and actual transactions.
        
        Args:
            ground_truth: Ground truth entry
            transactions: Extracted transactions
            
        Returns:
            Tuple of (missing_transactions, extra_transactions)
        """
        # For now, we can only detect count differences since we don't have
        # detailed transaction-level ground truth data
        
        missing_transactions = []
        extra_transactions = []
        
        expected_count = ground_truth.expected_count
        actual_count = len(transactions)
        
        if actual_count < expected_count:
            # We have fewer transactions than expected
            # Create placeholder missing transactions
            missing_count = expected_count - actual_count
            avg_amount = ground_truth.expected_total / expected_count if expected_count > 0 else Decimal('0')
            
            for i in range(missing_count):
                missing_transaction = Transaction(
                    date=None,  # We don't know the expected date
                    description=f"Missing transaction {i+1}",
                    amount=avg_amount,
                    raw_text="",
                    confidence=0.0
                )
                missing_transactions.append(missing_transaction)
        
        elif actual_count > expected_count:
            # We have more transactions than expected
            # Mark the excess as extra (starting from the end)
            excess_count = actual_count - expected_count
            extra_transactions = transactions[-excess_count:]
        
        return missing_transactions, extra_transactions
    
    def generate_validation_report(self, results: List[ValidationResult]) -> ValidationReport:
        """
        Generate comprehensive validation report.
        
        Args:
            results: List of validation results
            
        Returns:
            ValidationReport object
        """
        try:
            if not results:
                return ValidationReport(
                    validation_results=[],
                    overall_accuracy=0.0,
                    total_files_validated=0,
                    passed_validations=0,
                    failed_validations=0
                )
            
            # Calculate overall metrics
            total_files = len(results)
            passed_validations = sum(1 for r in results if r.is_valid)
            failed_validations = total_files - passed_validations
            
            # Calculate overall accuracy (weighted by expected totals)
            total_expected = sum(r.expected_total for r in results)
            if total_expected > 0:
                weighted_accuracy = sum(
                    r.accuracy * float(r.expected_total / total_expected) 
                    for r in results
                )
            else:
                weighted_accuracy = sum(r.accuracy for r in results) / len(results)
            
            report = ValidationReport(
                validation_results=results,
                overall_accuracy=weighted_accuracy,
                total_files_validated=total_files,
                passed_validations=passed_validations,
                failed_validations=failed_validations
            )
            
            self.logger.info(f"Generated validation report: {passed_validations}/{total_files} passed")
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating validation report: {str(e)}")
            return ValidationReport(
                validation_results=results,
                overall_accuracy=0.0,
                total_files_validated=len(results),
                passed_validations=0,
                failed_validations=len(results)
            )
    
    def validate_batch(self, extraction_results: Dict[str, List[Transaction]]) -> ValidationReport:
        """
        Validate a batch of extraction results.
        
        Args:
            extraction_results: Dictionary mapping bill names to transaction lists
            
        Returns:
            ValidationReport for the entire batch
        """
        validation_results = []
        
        for bill_name, transactions in extraction_results.items():
            result = self.validate_extraction(bill_name, transactions)
            validation_results.append(result)
        
        return self.generate_validation_report(validation_results)
    
    def get_ground_truth_summary(self) -> Dict[str, Any]:
        """
        Get summary of loaded ground truth data.
        
        Returns:
            Dictionary containing ground truth summary
        """
        if not self.ground_truth_data:
            return {
                "total_bills": 0,
                "total_expected_transactions": 0,
                "total_expected_amount": "0.00",
                "bills": []
            }
        
        total_transactions = sum(gt.expected_count for gt in self.ground_truth_data.values())
        total_amount = sum(gt.expected_total for gt in self.ground_truth_data.values())
        
        bills_info = [
            {
                "bill_name": name,
                "expected_count": gt.expected_count,
                "expected_total": str(gt.expected_total)
            }
            for name, gt in self.ground_truth_data.items()
        ]
        
        return {
            "total_bills": len(self.ground_truth_data),
            "total_expected_transactions": total_transactions,
            "total_expected_amount": str(total_amount),
            "bills": bills_info
        }
    
    def check_bill_coverage(self, bill_names: List[str]) -> Dict[str, Any]:
        """
        Check which bills have ground truth coverage.
        
        Args:
            bill_names: List of bill names to check
            
        Returns:
            Dictionary with coverage information
        """
        covered_bills = []
        missing_bills = []
        
        for bill_name in bill_names:
            if bill_name in self.ground_truth_data:
                covered_bills.append(bill_name)
            else:
                missing_bills.append(bill_name)
        
        return {
            "total_bills": len(bill_names),
            "covered_bills": covered_bills,
            "missing_bills": missing_bills,
            "coverage_percentage": len(covered_bills) / len(bill_names) * 100 if bill_names else 0
        }
    
    def add_ground_truth_entry(self, bill_name: str, expected_total: Decimal, expected_count: int) -> bool:
        """
        Add a new ground truth entry.
        
        Args:
            bill_name: Name of the bill
            expected_total: Expected total amount
            expected_count: Expected transaction count
            
        Returns:
            True if added successfully, False otherwise
        """
        try:
            entry = GroundTruthEntry(
                bill_name=bill_name,
                expected_total=expected_total,
                expected_count=expected_count
            )
            
            self.ground_truth_data[bill_name] = entry
            self.logger.info(f"Added ground truth entry for {bill_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding ground truth entry for {bill_name}: {str(e)}")
            return False
    
    def save_ground_truth(self, file_path: str) -> bool:
        """
        Save current ground truth data to file.
        
        Args:
            file_path: Path where to save the ground truth data
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            data = [entry.to_dict() for entry in self.ground_truth_data.values()]
            
            output_path = Path(file_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Saved ground truth data to {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving ground truth to {file_path}: {str(e)}")
            return False
    
    def get_validation_thresholds(self) -> Dict[str, float]:
        """
        Get validation thresholds for different metrics.
        
        Returns:
            Dictionary containing validation thresholds
        """
        return {
            "minimum_accuracy": 0.95,  # 95% accuracy required
            "total_tolerance_percentage": 0.01,  # 1% tolerance for totals
            "count_tolerance": 0,  # Exact count match required
            "confidence_threshold": 0.8  # Minimum confidence for transactions
        }
    
    def is_validation_passed(self, result: ValidationResult) -> bool:
        """
        Check if a validation result meets the passing criteria.
        
        Args:
            result: ValidationResult to check
            
        Returns:
            True if validation passed, False otherwise
        """
        thresholds = self.get_validation_thresholds()
        
        return (
            result.accuracy >= thresholds["minimum_accuracy"] and
            result.total_match and
            result.count_match
        )
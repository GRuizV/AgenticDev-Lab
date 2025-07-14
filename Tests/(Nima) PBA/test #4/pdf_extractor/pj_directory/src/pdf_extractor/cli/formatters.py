"""
Output formatters for CLI display.
"""

import json
import csv
from typing import List, Dict, Any, Optional
from io import StringIO
from tabulate import tabulate

from ..data.models import Transaction, ProcessingResult, ValidationResult


class OutputFormatter:
    """Handles formatting of output for different display formats."""
    
    def __init__(self):
        self.supported_formats = ["table", "json", "csv"]
    
    def format_transactions(self, transactions: List[Transaction], format_type: str = "table") -> str:
        """
        Format transactions for display.
        
        Args:
            transactions: List of Transaction objects
            format_type: Output format ("table", "json", "csv")
            
        Returns:
            Formatted string
        """
        if format_type not in self.supported_formats:
            raise ValueError(f"Unsupported format: {format_type}. Supported: {self.supported_formats}")
        
        if not transactions:
            return "No transactions found."
        
        if format_type == "table":
            return self._format_transactions_table(transactions)
        elif format_type == "json":
            return self._format_transactions_json(transactions)
        elif format_type == "csv":
            return self._format_transactions_csv(transactions)
    
    def _format_transactions_table(self, transactions: List[Transaction]) -> str:
        """Format transactions as a table."""
        headers = ["Date", "Description", "Amount (COP)", "Confidence"]
        rows = []
        
        for transaction in transactions:
            rows.append([
                transaction.date.strftime("%Y-%m-%d"),
                transaction.description[:50] + "..." if len(transaction.description) > 50 else transaction.description,
                f"${transaction.amount:,.2f}",
                f"{transaction.confidence:.2%}"
            ])
        
        # Add total row
        total_amount = sum(t.amount for t in transactions)
        rows.append([
            "TOTAL",
            f"{len(transactions)} transactions",
            f"${total_amount:,.2f}",
            ""
        ])
        
        return tabulate(rows, headers=headers, tablefmt="grid")
    
    def _format_transactions_json(self, transactions: List[Transaction]) -> str:
        """Format transactions as JSON."""
        data = {
            "transactions": [t.to_dict() for t in transactions],
            "summary": {
                "count": len(transactions),
                "total_amount": str(sum(t.amount for t in transactions))
            }
        }
        return json.dumps(data, indent=2, ensure_ascii=False)
    
    def _format_transactions_csv(self, transactions: List[Transaction]) -> str:
        """Format transactions as CSV."""
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(["Date", "Description", "Amount", "Confidence", "Raw_Text"])
        
        # Write transactions
        for transaction in transactions:
            writer.writerow([
                transaction.date.strftime("%Y-%m-%d"),
                transaction.description,
                str(transaction.amount),
                str(transaction.confidence),
                transaction.raw_text.replace('\n', ' ').replace('\r', ' ')
            ])
        
        return output.getvalue()
    
    def format_processing_result(self, result: ProcessingResult, format_type: str = "table") -> str:
        """
        Format processing result for display.
        
        Args:
            result: ProcessingResult object
            format_type: Output format
            
        Returns:
            Formatted string
        """
        if format_type == "json":
            return json.dumps(result.to_dict(), indent=2, ensure_ascii=False)
        
        # For table and CSV, show transactions plus summary
        output_lines = []
        
        # Header
        output_lines.append(f"Processing Result for: {result.file_path}")
        output_lines.append("=" * 60)
        output_lines.append(f"Pattern used: {result.pattern_used}")
        output_lines.append(f"Processing time: {result.processing_time:.2f}s")
        output_lines.append(f"Success: {'Yes' if result.success else 'No'}")
        
        if result.errors:
            output_lines.append(f"Errors: {', '.join(result.errors)}")
        
        if result.warnings:
            output_lines.append(f"Warnings: {', '.join(result.warnings)}")
        
        output_lines.append("")
        
        # Transactions
        if result.transactions:
            output_lines.append("Extracted Transactions:")
            output_lines.append(self.format_transactions(result.transactions, format_type))
        else:
            output_lines.append("No transactions extracted.")
        
        return "\n".join(output_lines)
    
    def format_validation_result(self, result: ValidationResult) -> str:
        """
        Format validation result for display.
        
        Args:
            result: ValidationResult object
            
        Returns:
            Formatted string
        """
        output_lines = []
        
        # Header
        output_lines.append(f"Validation Result for: {result.bill_name}")
        output_lines.append("=" * 50)
        
        # Summary
        status = "✓ PASSED" if result.is_valid else "✗ FAILED"
        output_lines.append(f"Status: {status}")
        output_lines.append(f"Overall Accuracy: {result.accuracy:.2%}")
        output_lines.append("")
        
        # Comparison table
        comparison_data = [
            ["Metric", "Expected", "Actual", "Match"],
            ["Transaction Count", str(result.expected_count), str(result.actual_count), 
             "✓" if result.count_match else "✗"],
            ["Total Amount", f"${result.expected_total:,.2f}", f"${result.actual_total:,.2f}", 
             "✓" if result.total_match else "✗"]
        ]
        
        output_lines.append(tabulate(comparison_data, headers="firstrow", tablefmt="grid"))
        output_lines.append("")
        
        # Missing transactions
        if result.missing_transactions:
            output_lines.append(f"Missing Transactions ({len(result.missing_transactions)}):")
            for i, transaction in enumerate(result.missing_transactions, 1):
                output_lines.append(f"  {i}. {transaction.description} - ${transaction.amount}")
            output_lines.append("")
        
        # Extra transactions
        if result.extra_transactions:
            output_lines.append(f"Extra Transactions ({len(result.extra_transactions)}):")
            for i, transaction in enumerate(result.extra_transactions, 1):
                output_lines.append(f"  {i}. {transaction.description} - ${transaction.amount}")
            output_lines.append("")
        
        return "\n".join(output_lines)
    
    def format_batch_summary(self, results: Dict[str, Any], format_type: str = "table") -> str:
        """
        Format batch processing summary.
        
        Args:
            results: Batch processing results
            format_type: Output format
            
        Returns:
            Formatted string
        """
        if format_type == "json":
            return json.dumps(results, indent=2, ensure_ascii=False, default=str)
        
        output_lines = []
        
        # Header
        output_lines.append("BATCH PROCESSING SUMMARY")
        output_lines.append("=" * 50)
        
        # Summary statistics
        if "summary" in results:
            summary = results["summary"]
            output_lines.append(f"Total files: {summary.get('total_files', 0)}")
            output_lines.append(f"Successful: {summary.get('successful_files', 0)}")
            output_lines.append(f"Failed: {summary.get('failed_files', 0)}")
            output_lines.append(f"Success rate: {summary.get('success_rate', 0):.1f}%")
            output_lines.append(f"Total transactions: {summary.get('total_transactions', 0)}")
            output_lines.append(f"Processing time: {summary.get('processing_time', 0):.2f}s")
            
            if "validation" in summary:
                val = summary["validation"]
                output_lines.append(f"Overall accuracy: {val.get('overall_accuracy', 0):.1%}")
                output_lines.append(f"Validation pass rate: {val.get('pass_rate', 0):.1f}%")
        
        output_lines.append("")
        
        # File-by-file results
        if "file_results" in results:
            output_lines.append("FILE RESULTS:")
            
            file_data = []
            for file_name, file_result in results["file_results"].items():
                pr = file_result.get("processing_result")
                vr = file_result.get("validation_result")
                
                status = "✓" if file_result.get("overall_success") else "✗"
                transactions = len(pr.transactions) if pr else 0
                amount = f"${pr.total_amount:,.2f}" if pr else "$0.00"
                accuracy = f"{vr.accuracy:.1%}" if vr else "N/A"
                
                file_data.append([status, file_name, transactions, amount, accuracy])
            
            headers = ["Status", "File", "Transactions", "Amount", "Accuracy"]
            output_lines.append(tabulate(file_data, headers=headers, tablefmt="grid"))
        
        return "\n".join(output_lines)
    
    def format_pattern_list(self, patterns: List[str], pattern_info: Optional[Dict[str, Any]] = None) -> str:
        """
        Format list of available patterns.
        
        Args:
            patterns: List of pattern names
            pattern_info: Optional detailed pattern information
            
        Returns:
            Formatted string
        """
        if not patterns:
            return "No patterns available."
        
        output_lines = []
        output_lines.append("AVAILABLE PATTERNS")
        output_lines.append("=" * 30)
        
        if pattern_info:
            # Detailed view with pattern information
            for pattern_name in patterns:
                info = pattern_info.get(pattern_name, {})
                output_lines.append(f"• {pattern_name}")
                output_lines.append(f"  Issuer: {info.get('issuer', 'Unknown')}")
                output_lines.append(f"  Card Type: {info.get('card_type', 'Unknown')}")
                output_lines.append(f"  Confidence: {info.get('confidence_threshold', 0):.1%}")
                output_lines.append("")
        else:
            # Simple list
            for pattern_name in patterns:
                output_lines.append(f"• {pattern_name}")
        
        return "\n".join(output_lines)
    
    def format_error(self, error_message: str) -> str:
        """
        Format error message for display.
        
        Args:
            error_message: Error message
            
        Returns:
            Formatted error string
        """
        return f"❌ ERROR: {error_message}"
    
    def format_warning(self, warning_message: str) -> str:
        """
        Format warning message for display.
        
        Args:
            warning_message: Warning message
            
        Returns:
            Formatted warning string
        """
        return f"⚠️  WARNING: {warning_message}"
    
    def format_success(self, success_message: str) -> str:
        """
        Format success message for display.
        
        Args:
            success_message: Success message
            
        Returns:
            Formatted success string
        """
        return f"✅ SUCCESS: {success_message}"
    
    def format_info(self, info_message: str) -> str:
        """
        Format info message for display.
        
        Args:
            info_message: Info message
            
        Returns:
            Formatted info string
        """
        return f"ℹ️  INFO: {info_message}"
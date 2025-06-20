"""
CLI output formatting utilities.
"""

from typing import List
from ..models.transaction import Transaction
from ..models.validation_result import ValidationResult


class CLITableFormatter:
    """Formats output for CLI display."""
    
    def __init__(self, table_width: int = 80):
        """
        Initialize formatter.
        
        Args:
            table_width: Maximum width for table display
        """
        self.table_width = table_width
    
    def display_transactions(self, transactions: List[Transaction], title: str = "Transactions") -> None:
        """
        Display transactions in a formatted table.
        
        Args:
            transactions: List of transactions to display
            title: Table title
        """
        if not transactions:
            print(f"\n{title}: No transactions found")
            return
        
        print(f"\n{title}:")
        
        # Calculate column widths
        date_width = 12
        amount_width = 15
        desc_width = self.table_width - date_width - amount_width - 6  # 6 for borders and spaces
        
        # Table header
        header = f"┌{'─' * date_width}┬{'─' * desc_width}┬{'─' * amount_width}┐"
        separator = f"├{'─' * date_width}┼{'─' * desc_width}┼{'─' * amount_width}┤"
        footer = f"└{'─' * date_width}┴{'─' * desc_width}┴{'─' * amount_width}┘"
        
        print(header)
        print(f"│{'Date':<{date_width}}│{'Description':<{desc_width}}│{'Amount':<{amount_width}}│")
        print(separator)
        
        # Transaction rows
        for transaction in transactions:
            date_str = transaction.date
            amount_str = f"${transaction.amount:,.2f}"
            
            # Truncate description if too long
            desc_str = transaction.description
            if len(desc_str) > desc_width - 1:
                desc_str = desc_str[:desc_width - 4] + "..."
            
            print(f"│{date_str:<{date_width}}│{desc_str:<{desc_width}}│{amount_str:>{amount_width}}│")
        
        print(footer)
        
        # Summary
        total_amount = sum(t.amount for t in transactions)
        print(f"\nTotal: ${total_amount:,.2f} ({len(transactions)} transactions)")
    
    def display_validation(self, validation: ValidationResult) -> None:
        """
        Display validation results.
        
        Args:
            validation: Validation result to display
        """
        print("\nValidation Results:")
        print("─" * 50)
        
        if validation.error:
            print(validation.overall_message)
            return
        
        print(validation.count_message)
        print(validation.amount_message)
        print(validation.overall_message)
    
    def display_summary(self, results: dict) -> None:
        """
        Display summary of all processing results.
        
        Args:
            results: Dictionary of processing results by file
        """
        print("\n" + "=" * 60)
        print("PROCESSING SUMMARY")
        print("=" * 60)
        
        total_files = len(results)
        successful_files = 0
        failed_files = 0
        validation_passed = 0
        validation_failed = 0
        
        for file_name, result in results.items():
            if 'error' in result:
                failed_files += 1
                print(f"\n❌ {file_name}: {result['error']}")
            else:
                successful_files += 1
                validation = result.get('validation')
                if validation and validation.valid:
                    validation_passed += 1
                    print(f"\n✅ {file_name}: Validation PASSED")
                else:
                    validation_failed += 1
                    print(f"\n❌ {file_name}: Validation FAILED")
                    if validation:
                        print(f"   Count: {validation.extracted_count}/{validation.expected_count}")
                        print(f"   Amount: ${validation.extracted_total:,.2f}/${validation.expected_total:,.2f}")
        
        print(f"\n" + "─" * 60)
        print(f"Files Processed: {total_files}")
        print(f"Successfully Extracted: {successful_files}")
        print(f"Failed to Extract: {failed_files}")
        print(f"Validation Passed: {validation_passed}")
        print(f"Validation Failed: {validation_failed}")
        
        if validation_passed == total_files:
            print("\n🎉 ALL VALIDATIONS PASSED!")
        elif validation_passed > 0:
            print(f"\n⚠️  {validation_passed}/{total_files} validations passed")
        else:
            print("\n❌ NO VALIDATIONS PASSED")
    
    def display_progress(self, current: int, total: int, file_name: str) -> None:
        """
        Display progress information.
        
        Args:
            current: Current file number
            total: Total number of files
            file_name: Name of current file being processed
        """
        progress = (current / total) * 100
        print(f"\n[{current}/{total}] ({progress:.1f}%) Processing: {file_name}")
    
    def display_header(self, title: str = "PDF Credit Card Expense Extractor") -> None:
        """
        Display application header.
        
        Args:
            title: Application title
        """
        print("=" * len(title))
        print(title)
        print("=" * len(title))
    
    def display_error(self, error_msg: str, file_name: str = None) -> None:
        """
        Display error message.
        
        Args:
            error_msg: Error message to display
            file_name: Optional file name where error occurred
        """
        if file_name:
            print(f"\n❌ Error processing {file_name}: {error_msg}")
        else:
            print(f"\n❌ Error: {error_msg}")
    
    def display_warning(self, warning_msg: str) -> None:
        """
        Display warning message.
        
        Args:
            warning_msg: Warning message to display
        """
        print(f"\n⚠️  Warning: {warning_msg}")
    
    def display_info(self, info_msg: str) -> None:
        """
        Display information message.
        
        Args:
            info_msg: Information message to display
        """
        print(f"\nℹ️  {info_msg}")


def format_currency(amount: float, currency_symbol: str = "$") -> str:
    """
    Format currency amount for display.
    
    Args:
        amount: Amount to format
        currency_symbol: Currency symbol
        
    Returns:
        Formatted currency string
    """
    return f"{currency_symbol}{amount:,.2f}"


def format_percentage(value: float, decimal_places: int = 1) -> str:
    """
    Format percentage for display.
    
    Args:
        value: Percentage value (0-100)
        decimal_places: Number of decimal places
        
    Returns:
        Formatted percentage string
    """
    return f"{value:.{decimal_places}f}%"


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate text to specified length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix
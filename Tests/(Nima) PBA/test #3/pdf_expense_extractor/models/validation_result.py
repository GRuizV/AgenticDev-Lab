"""
Validation result data model.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ValidationResult:
    """Represents the result of transaction validation."""
    
    valid: bool
    count_valid: bool
    amount_valid: bool
    extracted_count: int
    expected_count: int
    extracted_total: float
    expected_total: float
    amount_difference: float
    error: Optional[str] = None
    
    def __post_init__(self):
        """Validate result data after initialization."""
        if self.error and self.valid:
            raise ValueError("Cannot have error message with valid result")
        
        if not self.error and not self.valid and (self.count_valid and self.amount_valid):
            raise ValueError("Invalid state: valid flags don't match overall validity")
    
    @property
    def count_message(self) -> str:
        """Get count validation message."""
        if self.count_valid:
            return f"✓ Transaction Count: {self.extracted_count}/{self.expected_count}"
        else:
            return f"❌ Transaction Count: {self.extracted_count}/{self.expected_count} (Expected: {self.expected_count})"
    
    @property
    def amount_message(self) -> str:
        """Get amount validation message."""
        if self.amount_valid:
            return f"✓ Total Amount: ${self.extracted_total:,.2f} (Expected: ${self.expected_total:,.2f}, Diff: ${self.amount_difference:.2f})"
        else:
            return f"❌ Total Amount: ${self.extracted_total:,.2f} (Expected: ${self.expected_total:,.2f}, Diff: ${self.amount_difference:.2f})"
    
    @property
    def overall_message(self) -> str:
        """Get overall validation message."""
        if self.error:
            return f"❌ VALIDATION ERROR: {self.error}"
        elif self.valid:
            return "✅ VALIDATION PASSED"
        else:
            return "❌ VALIDATION FAILED"
    
    def to_dict(self) -> dict:
        """Convert validation result to dictionary."""
        return {
            'valid': self.valid,
            'count_valid': self.count_valid,
            'amount_valid': self.amount_valid,
            'extracted_count': self.extracted_count,
            'expected_count': self.expected_count,
            'extracted_total': self.extracted_total,
            'expected_total': self.expected_total,
            'amount_difference': self.amount_difference,
            'error': self.error
        }
    
    def __str__(self) -> str:
        """String representation of validation result."""
        if self.error:
            return f"Validation Error: {self.error}"
        
        lines = [
            self.count_message,
            self.amount_message,
            self.overall_message
        ]
        return "\n".join(lines)
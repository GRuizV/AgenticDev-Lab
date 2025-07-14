"""
Core data models for the PDF extractor application.
"""

from dataclasses import dataclass, field
from datetime import datetime, date
from decimal import Decimal
from typing import List, Dict, Optional, Any
import json


@dataclass
class Transaction:
    """Represents a single credit card transaction."""
    
    date: date
    description: str
    amount: Decimal
    raw_text: str = ""
    confidence: float = 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert transaction to dictionary format."""
        return {
            "date": self.date.isoformat(),
            "description": self.description,
            "amount": str(self.amount),
            "raw_text": self.raw_text,
            "confidence": self.confidence
        }
    
    def validate(self) -> bool:
        """Validate transaction data completeness."""
        return (
            self.date is not None and
            self.description.strip() != "" and
            self.amount > 0 and
            0.0 <= self.confidence <= 1.0
        )
    
    def __str__(self) -> str:
        return f"{self.date} | {self.description} | ${self.amount:,.2f}"


@dataclass
class Pattern:
    """Represents a PDF pattern for transaction extraction."""
    
    name: str
    issuer: str
    card_type: str
    transaction_regex: str
    date_format: str
    amount_format: str
    description_cleanup_rules: List[str] = field(default_factory=list)
    confidence_threshold: float = 0.8
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert pattern to dictionary format."""
        return {
            "name": self.name,
            "issuer": self.issuer,
            "card_type": self.card_type,
            "transaction_regex": self.transaction_regex,
            "date_format": self.date_format,
            "amount_format": self.amount_format,
            "description_cleanup_rules": self.description_cleanup_rules,
            "confidence_threshold": self.confidence_threshold
        }


@dataclass
class ProcessingResult:
    """Result of processing a single PDF file."""
    
    file_path: str
    transactions: List[Transaction]
    pattern_used: str
    processing_time: float
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    success: bool = True
    
    @property
    def transaction_count(self) -> int:
        """Get the number of transactions extracted."""
        return len(self.transactions)
    
    @property
    def total_amount(self) -> Decimal:
        """Get the total amount of all transactions."""
        return sum(t.amount for t in self.transactions)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary format."""
        return {
            "file_path": self.file_path,
            "transactions": [t.to_dict() for t in self.transactions],
            "pattern_used": self.pattern_used,
            "processing_time": self.processing_time,
            "transaction_count": self.transaction_count,
            "total_amount": str(self.total_amount),
            "errors": self.errors,
            "warnings": self.warnings,
            "success": self.success
        }


@dataclass
class ValidationResult:
    """Result of validating extracted data against ground truth."""
    
    bill_name: str
    expected_total: Decimal
    actual_total: Decimal
    expected_count: int
    actual_count: int
    accuracy: float
    missing_transactions: List[Transaction] = field(default_factory=list)
    extra_transactions: List[Transaction] = field(default_factory=list)
    
    @property
    def total_match(self) -> bool:
        """Check if total amounts match within tolerance."""
        tolerance = Decimal('0.01')  # 1 cent tolerance
        return abs(self.expected_total - self.actual_total) <= tolerance
    
    @property
    def count_match(self) -> bool:
        """Check if transaction counts match."""
        return self.expected_count == self.actual_count
    
    @property
    def is_valid(self) -> bool:
        """Check if validation passed."""
        return self.total_match and self.count_match and self.accuracy >= 0.95
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert validation result to dictionary format."""
        return {
            "bill_name": self.bill_name,
            "expected_total": str(self.expected_total),
            "actual_total": str(self.actual_total),
            "expected_count": self.expected_count,
            "actual_count": self.actual_count,
            "accuracy": self.accuracy,
            "total_match": self.total_match,
            "count_match": self.count_match,
            "is_valid": self.is_valid,
            "missing_transactions": [t.to_dict() for t in self.missing_transactions],
            "extra_transactions": [t.to_dict() for t in self.extra_transactions]
        }


@dataclass
class BatchResult:
    """Result of processing multiple PDF files."""
    
    results: List[ProcessingResult]
    total_files: int
    successful_files: int
    failed_files: int
    total_transactions: int
    processing_time: float
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage."""
        if self.total_files == 0:
            return 0.0
        return (self.successful_files / self.total_files) * 100
    
    @property
    def total_amount(self) -> Decimal:
        """Get total amount across all successful files."""
        return sum(r.total_amount for r in self.results if r.success)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert batch result to dictionary format."""
        return {
            "results": [r.to_dict() for r in self.results],
            "total_files": self.total_files,
            "successful_files": self.successful_files,
            "failed_files": self.failed_files,
            "success_rate": self.success_rate,
            "total_transactions": self.total_transactions,
            "total_amount": str(self.total_amount),
            "processing_time": self.processing_time
        }


@dataclass
class ValidationReport:
    """Comprehensive validation report for multiple files."""
    
    validation_results: List[ValidationResult]
    overall_accuracy: float
    total_files_validated: int
    passed_validations: int
    failed_validations: int
    
    @property
    def pass_rate(self) -> float:
        """Calculate validation pass rate as percentage."""
        if self.total_files_validated == 0:
            return 0.0
        return (self.passed_validations / self.total_files_validated) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert validation report to dictionary format."""
        return {
            "validation_results": [vr.to_dict() for vr in self.validation_results],
            "overall_accuracy": self.overall_accuracy,
            "total_files_validated": self.total_files_validated,
            "passed_validations": self.passed_validations,
            "failed_validations": self.failed_validations,
            "pass_rate": self.pass_rate
        }


@dataclass
class GroundTruthEntry:
    """Represents a ground truth entry for validation."""
    
    bill_name: str
    expected_total: Decimal
    expected_count: int
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GroundTruthEntry':
        """Create GroundTruthEntry from dictionary."""
        return cls(
            bill_name=data["bill_name"],
            expected_total=Decimal(str(data["expected_total"])),
            expected_count=int(data["expected_count"])
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "bill_name": self.bill_name,
            "expected_total": str(self.expected_total),
            "expected_count": self.expected_count
        }
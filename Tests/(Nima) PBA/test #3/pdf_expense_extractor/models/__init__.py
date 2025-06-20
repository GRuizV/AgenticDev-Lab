"""
Data models for the PDF expense extractor.
"""

from .transaction import Transaction
from .validation_result import ValidationResult

__all__ = ['Transaction', 'ValidationResult']
"""
Configuration module for the PDF expense extractor.
"""

from .expected_results import EXPECTED_RESULTS
from .patterns import TRANSACTION_PATTERNS, DESCRIPTION_PATTERNS
from .settings import Settings

__all__ = ['EXPECTED_RESULTS', 'TRANSACTION_PATTERNS', 'DESCRIPTION_PATTERNS', 'Settings']
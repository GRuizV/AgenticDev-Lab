"""
PDF Credit Card Expense Extractor

A Python CLI application that extracts credit card transaction data from PDF files
using pdfplumber, with pattern recognition and validation against ground truth data.
"""

__version__ = "1.0.0"
__author__ = "PDF Extractor Team"
__description__ = "PDF Credit Card Expense Extractor CLI"

from .data.models import Transaction, ProcessingResult, ValidationResult, BatchResult
from .core.pdf_parser import PDFParser
from .core.pattern_engine import PatternEngine
from .core.validator import Validator
from .core.processor import PDFProcessor
from .cli.main import main as cli_main

__all__ = [
    "Transaction",
    "ProcessingResult",
    "ValidationResult",
    "BatchResult",
    "PDFParser",
    "PatternEngine",
    "Validator",
    "PDFProcessor",
    "cli_main"
]
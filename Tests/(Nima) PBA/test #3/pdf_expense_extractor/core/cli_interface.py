"""
Command-line interface for the PDF expense extractor.
"""

import sys
from pathlib import Path
from typing import List, Dict, Optional
from ..models.transaction import Transaction
from ..models.validation_result import ValidationResult
from ..parsers.pdf_parser_factory import PDFParserFactory
from ..core.pattern_detector import TransactionPatternDetector
from ..core.validator import TransactionValidator
from ..utils.formatter import CLITableFormatter
from ..config.settings import Settings


class ExpenseExtractorCLI:
    """Command-line interface for PDF expense extraction."""
    
    def __init__(self, settings: Settings = None):
        """
        Initialize the CLI interface.
        
        Args:
            settings: Application settings
        """
        self.settings = settings or Settings.default()
        self.parser_factory = PDFParserFactory()
        self.pattern_detector = TransactionPatternDetector()
        self.validator = TransactionValidator(self.settings.amount_tolerance)
        self.formatter = CLITableFormatter(self.settings.table_width)
    
    def run(self, pdf_directory: str = None) -> int:
        """
        Main execution flow.
        
        Args:
            pdf_directory: Directory containing PDF files
            
        Returns:
            Exit code (0 for success, 1 for failure)
        """
        try:
            # Display header
            self.formatter.display_header()
            
            # Determine PDF directory
            pdf_dir = Path(pdf_directory or self.settings.pdf_directory)
            
            if not pdf_dir.exists():
                self.formatter.display_error(f"PDF directory not found: {pdf_dir}")
                return 1
            
            # Discover PDF files
            pdf_files = self._discover_pdf_files(pdf_dir)
            
            if not pdf_files:
                self.formatter.display_error("No PDF files found in directory")
                return 1
            
            # Check parser availability
            if not self.parser_factory.available_parsers:
                self.formatter.display_error("No PDF parsing libraries available. Please install pdfplumber, pymupdf, or PyPDF2.")
                return 1
            
            if self.settings.verbose:
                self._display_parser_info()
            
            # Process files
            results = self._process_files(pdf_files)
            
            # Display summary
            self.formatter.display_summary(results)
            
            # Check if all validations passed
            all_passed = all(
                'validation' in result and result['validation'].valid 
                for result in results.values() 
                if 'error' not in result
            )
            
            return 0 if all_passed else 1
            
        except KeyboardInterrupt:
            self.formatter.display_info("Operation cancelled by user")
            return 1
        except Exception as e:
            self.formatter.display_error(f"Unexpected error: {e}")
            if self.settings.verbose:
                import traceback
                print(traceback.format_exc())
            return 1
    
    def _discover_pdf_files(self, pdf_dir: Path) -> List[Path]:
        """
        Discover PDF files in the directory.
        
        Args:
            pdf_dir: Directory to search
            
        Returns:
            List of PDF file paths
        """
        pdf_files = []
        
        # Look for PDF files
        for pdf_file in pdf_dir.glob("*.pdf"):
            if pdf_file.is_file():
                pdf_files.append(pdf_file)
        
        # Sort files for consistent processing order
        pdf_files.sort(key=lambda x: x.name)
        
        return pdf_files
    
    def _display_parser_info(self):
        """Display information about available parsers."""
        self.formatter.display_info("Available PDF parsers:")
        for parser in self.parser_factory.available_parsers:
            print(f"  - {parser}")
    
    def _process_files(self, pdf_files: List[Path]) -> Dict[str, dict]:
        """
        Process all PDF files.
        
        Args:
            pdf_files: List of PDF files to process
            
        Returns:
            Dictionary with processing results
        """
        results = {}
        total_files = len(pdf_files)
        
        for i, pdf_file in enumerate(pdf_files, 1):
            if self.settings.show_progress:
                self.formatter.display_progress(i, total_files, pdf_file.name)
            
            try:
                # Extract transactions
                transactions = self._extract_transactions(pdf_file)
                
                # Display transaction table
                bill_name = pdf_file.stem
                self.formatter.display_transactions(transactions, f"Transactions from {pdf_file.name}")
                
                # Validate results
                validation = self.validator.validate_extraction(bill_name, transactions)
                
                # Display validation results
                self.formatter.display_validation(validation)
                
                results[bill_name] = {
                    'transactions': transactions,
                    'validation': validation,
                    'file_path': str(pdf_file)
                }
                
            except Exception as e:
                error_msg = str(e)
                self.formatter.display_error(error_msg, pdf_file.name)
                results[pdf_file.stem] = {
                    'error': error_msg,
                    'file_path': str(pdf_file)
                }
        
        return results
    
    def _extract_transactions(self, pdf_file: Path) -> List[Transaction]:
        """
        Extract transactions from a PDF file.
        
        Args:
            pdf_file: Path to PDF file
            
        Returns:
            List of extracted transactions
        """
        # Get the best parser for this PDF
        parser = self.parser_factory.get_best_parser(pdf_file)
        
        if not parser:
            raise RuntimeError("No suitable PDF parser available")
        
        if self.settings.verbose:
            self.formatter.display_info(f"Using {parser.library_name} parser")
        
        # Extract text from PDF
        try:
            text = parser.extract_text(pdf_file)
        except Exception as e:
            raise RuntimeError(f"Failed to extract text: {e}")
        
        if not text:
            raise RuntimeError("No text extracted from PDF")
        
        if self.settings.verbose:
            self.formatter.display_info(f"Extracted {len(text)} characters of text")
        
        # Extract transactions from text
        transactions = self.pattern_detector.extract_transactions(text)
        
        if self.settings.verbose:
            debug_info = self.pattern_detector.get_debug_info(text)
            self.formatter.display_info(f"Pattern detection: {debug_info}")
        
        return transactions
    
    def process_single_file(self, pdf_path: str) -> Dict:
        """
        Process a single PDF file.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Processing result dictionary
        """
        pdf_file = Path(pdf_path)
        
        if not pdf_file.exists():
            return {'error': f"File not found: {pdf_path}"}
        
        if not pdf_file.suffix.lower() == '.pdf':
            return {'error': f"Not a PDF file: {pdf_path}"}
        
        try:
            transactions = self._extract_transactions(pdf_file)
            bill_name = pdf_file.stem
            validation = self.validator.validate_extraction(bill_name, transactions)
            
            return {
                'transactions': transactions,
                'validation': validation,
                'file_path': str(pdf_file)
            }
            
        except Exception as e:
            return {'error': str(e), 'file_path': str(pdf_file)}
    
    def test_parsers(self, pdf_path: str) -> Dict:
        """
        Test all available parsers on a PDF file.
        
        Args:
            pdf_path: Path to PDF file for testing
            
        Returns:
            Test results for all parsers
        """
        pdf_file = Path(pdf_path)
        
        if not pdf_file.exists():
            return {'error': f"File not found: {pdf_path}"}
        
        return self.parser_factory.test_all_parsers(pdf_file)
    
    def get_validation_report(self, results: Dict[str, dict]) -> str:
        """
        Generate a detailed validation report.
        
        Args:
            results: Processing results
            
        Returns:
            Formatted validation report
        """
        validations = {}
        
        for bill_name, result in results.items():
            if 'validation' in result:
                validations[bill_name] = result['validation']
        
        return self.validator.get_detailed_report(validations)
    
    def set_verbose(self, verbose: bool):
        """Enable or disable verbose output."""
        self.settings.verbose = verbose
    
    def set_progress(self, show_progress: bool):
        """Enable or disable progress display."""
        self.settings.show_progress = show_progress
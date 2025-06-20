"""
Base parser interface for PDF text extraction.
"""

from abc import ABC, abstractmethod
from typing import Optional, List
from pathlib import Path


class BaseParser(ABC):
    """Abstract base class for PDF parsers."""
    
    def __init__(self, library_name: str):
        """
        Initialize parser.
        
        Args:
            library_name: Name of the PDF library
        """
        self.library_name = library_name
        self._is_available = None
    
    @property
    def is_available(self) -> bool:
        """
        Check if the PDF library is available.
        
        Returns:
            True if library is available, False otherwise
        """
        if self._is_available is None:
            self._is_available = self._check_availability()
        return self._is_available
    
    @abstractmethod
    def _check_availability(self) -> bool:
        """
        Check if the required library is installed and available.
        
        Returns:
            True if library is available, False otherwise
        """
        pass
    
    @abstractmethod
    def extract_text(self, pdf_path: Path) -> Optional[str]:
        """
        Extract text from PDF file.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Extracted text or None if extraction fails
        """
        pass
    
    @abstractmethod
    def extract_text_by_page(self, pdf_path: Path) -> Optional[List[str]]:
        """
        Extract text from PDF file page by page.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            List of text strings (one per page) or None if extraction fails
        """
        pass
    
    def test_extraction(self, pdf_path: Path) -> bool:
        """
        Test if parser can successfully extract text from a PDF.
        
        Args:
            pdf_path: Path to PDF file for testing
            
        Returns:
            True if extraction is successful, False otherwise
        """
        try:
            text = self.extract_text(pdf_path)
            return text is not None and len(text.strip()) > 0
        except Exception:
            return False
    
    def get_info(self) -> dict:
        """
        Get information about the parser.
        
        Returns:
            Dictionary with parser information
        """
        return {
            'library_name': self.library_name,
            'is_available': self.is_available,
            'class_name': self.__class__.__name__
        }
    
    def __str__(self) -> str:
        """String representation of parser."""
        status = "available" if self.is_available else "not available"
        return f"{self.library_name} parser ({status})"
    
    def __repr__(self) -> str:
        """Detailed string representation of parser."""
        return f"{self.__class__.__name__}(library_name='{self.library_name}', available={self.is_available})"


class ParserError(Exception):
    """Exception raised by PDF parsers."""
    
    def __init__(self, message: str, parser_name: str = None, original_error: Exception = None):
        """
        Initialize parser error.
        
        Args:
            message: Error message
            parser_name: Name of the parser that failed
            original_error: Original exception that caused this error
        """
        self.parser_name = parser_name
        self.original_error = original_error
        
        if parser_name:
            full_message = f"{parser_name}: {message}"
        else:
            full_message = message
            
        if original_error:
            full_message += f" (Original error: {original_error})"
            
        super().__init__(full_message)
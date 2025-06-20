"""
PDF parser implementation using pdfplumber library.
"""

from typing import Optional, List
from pathlib import Path
from .base_parser import BaseParser, ParserError


class PDFPlumberParser(BaseParser):
    """PDF parser using pdfplumber library."""
    
    def __init__(self):
        """Initialize pdfplumber parser."""
        super().__init__("pdfplumber")
    
    def _check_availability(self) -> bool:
        """Check if pdfplumber is available."""
        try:
            import pdfplumber
            return True
        except ImportError:
            return False
    
    def extract_text(self, pdf_path: Path) -> Optional[str]:
        """
        Extract text from PDF using pdfplumber.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Extracted text or None if extraction fails
        """
        if not self.is_available:
            raise ParserError("pdfplumber library is not available", self.library_name)
        
        try:
            import pdfplumber
            
            text_parts = []
            
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
            
            return '\n'.join(text_parts) if text_parts else None
            
        except Exception as e:
            raise ParserError(f"Failed to extract text from {pdf_path}", self.library_name, e)
    
    def extract_text_by_page(self, pdf_path: Path) -> Optional[List[str]]:
        """
        Extract text from PDF page by page using pdfplumber.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            List of text strings (one per page) or None if extraction fails
        """
        if not self.is_available:
            raise ParserError("pdfplumber library is not available", self.library_name)
        
        try:
            import pdfplumber
            
            pages_text = []
            
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    pages_text.append(page_text if page_text else "")
            
            return pages_text if pages_text else None
            
        except Exception as e:
            raise ParserError(f"Failed to extract text by page from {pdf_path}", self.library_name, e)
    
    def extract_tables(self, pdf_path: Path) -> Optional[List]:
        """
        Extract tables from PDF using pdfplumber.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            List of tables or None if extraction fails
        """
        if not self.is_available:
            raise ParserError("pdfplumber library is not available", self.library_name)
        
        try:
            import pdfplumber
            
            all_tables = []
            
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    tables = page.extract_tables()
                    if tables:
                        all_tables.extend(tables)
            
            return all_tables if all_tables else None
            
        except Exception as e:
            raise ParserError(f"Failed to extract tables from {pdf_path}", self.library_name, e)
    
    def get_page_info(self, pdf_path: Path) -> Optional[dict]:
        """
        Get information about PDF pages.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dictionary with page information
        """
        if not self.is_available:
            return None
        
        try:
            import pdfplumber
            
            with pdfplumber.open(pdf_path) as pdf:
                return {
                    'page_count': len(pdf.pages),
                    'metadata': pdf.metadata,
                    'pages': [
                        {
                            'page_number': i + 1,
                            'width': page.width,
                            'height': page.height,
                            'rotation': page.rotation
                        }
                        for i, page in enumerate(pdf.pages)
                    ]
                }
                
        except Exception:
            return None
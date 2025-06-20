"""
PDF parser implementation using PyPDF2 library.
"""

from typing import Optional, List
from pathlib import Path
from .base_parser import BaseParser, ParserError


class PyPDF2Parser(BaseParser):
    """PDF parser using PyPDF2 library."""
    
    def __init__(self):
        """Initialize PyPDF2 parser."""
        super().__init__("PyPDF2")
    
    def _check_availability(self) -> bool:
        """Check if PyPDF2 is available."""
        try:
            import PyPDF2
            return True
        except ImportError:
            return False
    
    def extract_text(self, pdf_path: Path) -> Optional[str]:
        """
        Extract text from PDF using PyPDF2.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Extracted text or None if extraction fails
        """
        if not self.is_available:
            raise ParserError("PyPDF2 library is not available", self.library_name)
        
        try:
            import PyPDF2
            
            text_parts = []
            
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
            
            return '\n'.join(text_parts) if text_parts else None
            
        except Exception as e:
            raise ParserError(f"Failed to extract text from {pdf_path}", self.library_name, e)
    
    def extract_text_by_page(self, pdf_path: Path) -> Optional[List[str]]:
        """
        Extract text from PDF page by page using PyPDF2.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            List of text strings (one per page) or None if extraction fails
        """
        if not self.is_available:
            raise ParserError("PyPDF2 library is not available", self.library_name)
        
        try:
            import PyPDF2
            
            pages_text = []
            
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    pages_text.append(page_text if page_text else "")
            
            return pages_text if pages_text else None
            
        except Exception as e:
            raise ParserError(f"Failed to extract text by page from {pdf_path}", self.library_name, e)
    
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
            import PyPDF2
            
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                pages_info = []
                for i, page in enumerate(pdf_reader.pages):
                    # PyPDF2 has limited page info compared to other libraries
                    pages_info.append({
                        'page_number': i + 1,
                        'rotation': page.rotation if hasattr(page, 'rotation') else 0
                    })
                
                return {
                    'page_count': len(pdf_reader.pages),
                    'metadata': pdf_reader.metadata if hasattr(pdf_reader, 'metadata') else {},
                    'pages': pages_info
                }
                
        except Exception:
            return None
    
    def is_encrypted(self, pdf_path: Path) -> bool:
        """
        Check if PDF is encrypted.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            True if PDF is encrypted, False otherwise
        """
        if not self.is_available:
            return False
        
        try:
            import PyPDF2
            
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                return pdf_reader.is_encrypted
                
        except Exception:
            return False
    
    def decrypt_pdf(self, pdf_path: Path, password: str) -> bool:
        """
        Attempt to decrypt an encrypted PDF.
        
        Args:
            pdf_path: Path to PDF file
            password: Password to decrypt the PDF
            
        Returns:
            True if decryption successful, False otherwise
        """
        if not self.is_available:
            return False
        
        try:
            import PyPDF2
            
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                if pdf_reader.is_encrypted:
                    return pdf_reader.decrypt(password) == 1
                return True  # Not encrypted
                
        except Exception:
            return False
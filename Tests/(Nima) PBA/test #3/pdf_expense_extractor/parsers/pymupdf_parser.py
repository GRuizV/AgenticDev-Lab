"""
PDF parser implementation using pymupdf (fitz) library.
"""

from typing import Optional, List
from pathlib import Path
from .base_parser import BaseParser, ParserError


class PyMuPDFParser(BaseParser):
    """PDF parser using pymupdf (fitz) library."""
    
    def __init__(self):
        """Initialize pymupdf parser."""
        super().__init__("pymupdf")
    
    def _check_availability(self) -> bool:
        """Check if pymupdf is available."""
        try:
            import fitz  # pymupdf
            return True
        except ImportError:
            return False
    
    def extract_text(self, pdf_path: Path) -> Optional[str]:
        """
        Extract text from PDF using pymupdf.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Extracted text or None if extraction fails
        """
        if not self.is_available:
            raise ParserError("pymupdf library is not available", self.library_name)
        
        try:
            import fitz
            
            text_parts = []
            
            doc = fitz.open(pdf_path)
            try:
                for page_num in range(doc.page_count):
                    page = doc[page_num]
                    page_text = page.get_text()
                    if page_text:
                        text_parts.append(page_text)
            finally:
                doc.close()
            
            return '\n'.join(text_parts) if text_parts else None
            
        except Exception as e:
            raise ParserError(f"Failed to extract text from {pdf_path}", self.library_name, e)
    
    def extract_text_by_page(self, pdf_path: Path) -> Optional[List[str]]:
        """
        Extract text from PDF page by page using pymupdf.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            List of text strings (one per page) or None if extraction fails
        """
        if not self.is_available:
            raise ParserError("pymupdf library is not available", self.library_name)
        
        try:
            import fitz
            
            pages_text = []
            
            doc = fitz.open(pdf_path)
            try:
                for page_num in range(doc.page_count):
                    page = doc[page_num]
                    page_text = page.get_text()
                    pages_text.append(page_text if page_text else "")
            finally:
                doc.close()
            
            return pages_text if pages_text else None
            
        except Exception as e:
            raise ParserError(f"Failed to extract text by page from {pdf_path}", self.library_name, e)
    
    def extract_text_with_layout(self, pdf_path: Path) -> Optional[str]:
        """
        Extract text with layout preservation using pymupdf.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Extracted text with layout or None if extraction fails
        """
        if not self.is_available:
            raise ParserError("pymupdf library is not available", self.library_name)
        
        try:
            import fitz
            
            text_parts = []
            
            doc = fitz.open(pdf_path)
            try:
                for page_num in range(doc.page_count):
                    page = doc[page_num]
                    # Use "dict" format to preserve layout information
                    text_dict = page.get_text("dict")
                    page_text = self._extract_text_from_dict(text_dict)
                    if page_text:
                        text_parts.append(page_text)
            finally:
                doc.close()
            
            return '\n'.join(text_parts) if text_parts else None
            
        except Exception as e:
            raise ParserError(f"Failed to extract text with layout from {pdf_path}", self.library_name, e)
    
    def _extract_text_from_dict(self, text_dict: dict) -> str:
        """
        Extract text from pymupdf text dictionary while preserving layout.
        
        Args:
            text_dict: Text dictionary from pymupdf
            
        Returns:
            Extracted text string
        """
        text_parts = []
        
        for block in text_dict.get("blocks", []):
            if "lines" in block:  # Text block
                for line in block["lines"]:
                    line_text = ""
                    for span in line.get("spans", []):
                        line_text += span.get("text", "")
                    if line_text.strip():
                        text_parts.append(line_text.strip())
        
        return '\n'.join(text_parts)
    
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
            import fitz
            
            doc = fitz.open(pdf_path)
            try:
                pages_info = []
                for page_num in range(doc.page_count):
                    page = doc[page_num]
                    rect = page.rect
                    pages_info.append({
                        'page_number': page_num + 1,
                        'width': rect.width,
                        'height': rect.height,
                        'rotation': page.rotation
                    })
                
                return {
                    'page_count': doc.page_count,
                    'metadata': doc.metadata,
                    'pages': pages_info
                }
            finally:
                doc.close()
                
        except Exception:
            return None
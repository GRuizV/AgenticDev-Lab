"""
PDFPlumber-based text extraction for PDF files.
"""

import pdfplumber
import logging
from typing import List, Dict, Optional, Any
from pathlib import Path


class PDFPlumberExtractor:
    """Handles PDF text extraction using pdfplumber library."""
    
    def __init__(self, extraction_settings: Optional[Dict[str, Any]] = None):
        """
        Initialize the PDFPlumber extractor.
        
        Args:
            extraction_settings: Custom extraction settings
        """
        self.logger = logging.getLogger(__name__)
        
        # Default extraction settings optimized for credit card PDFs
        self.extraction_settings = {
            'x_tolerance': 3,
            'y_tolerance': 3,
            'layout': True,
            'strip_text': True,
            'use_text_flow': False,
            'horizontal_ltr': True,
            'vertical_ttb': True
        }
        
        # Update with custom settings if provided
        if extraction_settings:
            self.extraction_settings.update(extraction_settings)
    
    def extract_text(self, pdf_path: str) -> str:
        """
        Extract text from PDF using pdfplumber.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text as a single string
            
        Raises:
            FileNotFoundError: If PDF file doesn't exist
            Exception: If extraction fails
        """
        pdf_file = Path(pdf_path)
        if not pdf_file.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                text_content = []
                
                for page_num, page in enumerate(pdf.pages, 1):
                    self.logger.debug(f"Extracting text from page {page_num}")
                    
                    # Extract text with settings
                    page_text = page.extract_text(**self.extraction_settings)
                    
                    if page_text:
                        text_content.append(page_text)
                    else:
                        self.logger.warning(f"No text extracted from page {page_num}")
                
                full_text = '\n'.join(text_content)
                self.logger.info(f"Successfully extracted {len(full_text)} characters from {len(pdf.pages)} pages")
                
                return full_text
                
        except Exception as e:
            self.logger.error(f"Failed to extract text from {pdf_path}: {str(e)}")
            raise Exception(f"PDF extraction failed: {str(e)}")
    
    def extract_with_layout(self, pdf_path: str) -> List[Dict[str, Any]]:
        """
        Extract text preserving layout information.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            List of dictionaries containing text and layout information
        """
        pdf_file = Path(pdf_path)
        if not pdf_file.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        try:
            layout_data = []
            
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    self.logger.debug(f"Extracting layout from page {page_num}")
                    
                    # Extract characters with positions
                    chars = page.chars
                    
                    # Group characters into lines
                    lines = self._group_chars_into_lines(chars)
                    
                    page_data = {
                        'page_number': page_num,
                        'page_width': page.width,
                        'page_height': page.height,
                        'lines': lines,
                        'raw_text': page.extract_text(**self.extraction_settings)
                    }
                    
                    layout_data.append(page_data)
            
            self.logger.info(f"Successfully extracted layout data from {len(layout_data)} pages")
            return layout_data
            
        except Exception as e:
            self.logger.error(f"Failed to extract layout from {pdf_path}: {str(e)}")
            raise Exception(f"Layout extraction failed: {str(e)}")
    
    def extract_tables(self, pdf_path: str) -> List[List[List[str]]]:
        """
        Extract table data if transactions are in table format.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            List of tables, where each table is a list of rows,
            and each row is a list of cell values
        """
        pdf_file = Path(pdf_path)
        if not pdf_file.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        try:
            all_tables = []
            
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    self.logger.debug(f"Extracting tables from page {page_num}")
                    
                    # Extract tables from the page
                    tables = page.extract_tables()
                    
                    if tables:
                        for table_num, table in enumerate(tables):
                            self.logger.debug(f"Found table {table_num + 1} on page {page_num} with {len(table)} rows")
                            all_tables.append(table)
                    else:
                        self.logger.debug(f"No tables found on page {page_num}")
            
            self.logger.info(f"Successfully extracted {len(all_tables)} tables")
            return all_tables
            
        except Exception as e:
            self.logger.error(f"Failed to extract tables from {pdf_path}: {str(e)}")
            raise Exception(f"Table extraction failed: {str(e)}")
    
    def _group_chars_into_lines(self, chars: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Group character data into lines based on y-coordinates.
        
        Args:
            chars: List of character dictionaries from pdfplumber
            
        Returns:
            List of line dictionaries with text and position info
        """
        if not chars:
            return []
        
        # Sort characters by y-coordinate (top to bottom) then x-coordinate (left to right)
        sorted_chars = sorted(chars, key=lambda c: (-c['top'], c['x0']))
        
        lines = []
        current_line = []
        current_y = None
        y_tolerance = self.extraction_settings.get('y_tolerance', 3)
        
        for char in sorted_chars:
            char_y = char['top']
            
            # Check if this character belongs to the current line
            if current_y is None or abs(char_y - current_y) <= y_tolerance:
                current_line.append(char)
                current_y = char_y
            else:
                # Start a new line
                if current_line:
                    lines.append(self._create_line_dict(current_line))
                current_line = [char]
                current_y = char_y
        
        # Add the last line
        if current_line:
            lines.append(self._create_line_dict(current_line))
        
        return lines
    
    def _create_line_dict(self, chars: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create a line dictionary from a list of characters.
        
        Args:
            chars: List of character dictionaries
            
        Returns:
            Dictionary containing line information
        """
        if not chars:
            return {}
        
        # Sort characters by x-coordinate (left to right)
        sorted_chars = sorted(chars, key=lambda c: c['x0'])
        
        # Extract text
        text = ''.join(char['text'] for char in sorted_chars)
        
        # Calculate bounding box
        x0 = min(char['x0'] for char in sorted_chars)
        x1 = max(char['x1'] for char in sorted_chars)
        top = min(char['top'] for char in sorted_chars)
        bottom = max(char['bottom'] for char in sorted_chars)
        
        return {
            'text': text.strip(),
            'x0': x0,
            'x1': x1,
            'top': top,
            'bottom': bottom,
            'width': x1 - x0,
            'height': bottom - top,
            'char_count': len(sorted_chars)
        }
    
    def get_pdf_info(self, pdf_path: str) -> Dict[str, Any]:
        """
        Get basic information about the PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary containing PDF metadata
        """
        pdf_file = Path(pdf_path)
        if not pdf_file.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                info = {
                    'file_path': str(pdf_file.absolute()),
                    'file_size': pdf_file.stat().st_size,
                    'page_count': len(pdf.pages),
                    'metadata': pdf.metadata or {},
                    'pages_info': []
                }
                
                # Get information for each page
                for page_num, page in enumerate(pdf.pages, 1):
                    page_info = {
                        'page_number': page_num,
                        'width': page.width,
                        'height': page.height,
                        'rotation': getattr(page, 'rotation', 0),
                        'char_count': len(page.chars),
                        'has_text': bool(page.extract_text())
                    }
                    info['pages_info'].append(page_info)
                
                return info
                
        except Exception as e:
            self.logger.error(f"Failed to get PDF info for {pdf_path}: {str(e)}")
            raise Exception(f"PDF info extraction failed: {str(e)}")
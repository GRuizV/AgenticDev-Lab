"""
PDF parser factory for selecting and managing PDF libraries.
"""

from typing import Optional, List, Dict
from pathlib import Path
from .base_parser import BaseParser, ParserError
from .pdfplumber_parser import PDFPlumberParser
from .pymupdf_parser import PyMuPDFParser
from .pypdf2_parser import PyPDF2Parser


class PDFParserFactory:
    """Factory for creating and managing PDF parsers."""
    
    def __init__(self):
        """Initialize the parser factory."""
        self._parsers = {}
        self._evaluation_cache = {}
        self._initialize_parsers()
    
    def _initialize_parsers(self):
        """Initialize all available parsers."""
        parser_classes = [
            PDFPlumberParser,
            PyMuPDFParser,
            PyPDF2Parser
        ]
        
        for parser_class in parser_classes:
            try:
                parser = parser_class()
                self._parsers[parser.library_name] = parser
            except Exception as e:
                # Parser initialization failed, skip it
                pass
    
    @property
    def available_parsers(self) -> List[BaseParser]:
        """
        Get list of available parsers.
        
        Returns:
            List of available parser instances
        """
        return [parser for parser in self._parsers.values() if parser.is_available]
    
    @property
    def parser_names(self) -> List[str]:
        """
        Get list of available parser names.
        
        Returns:
            List of parser library names
        """
        return [parser.library_name for parser in self.available_parsers]
    
    def get_parser(self, library_name: str = None) -> Optional[BaseParser]:
        """
        Get a specific parser by library name.
        
        Args:
            library_name: Name of the PDF library (optional)
            
        Returns:
            Parser instance or None if not available
        """
        if library_name:
            parser = self._parsers.get(library_name)
            return parser if parser and parser.is_available else None
        
        # Return the best available parser
        return self.get_best_parser()
    
    def get_best_parser(self, pdf_path: Path = None) -> Optional[BaseParser]:
        """
        Get the best available parser, optionally tested against a specific PDF.
        
        Args:
            pdf_path: Optional PDF file to test parsers against
            
        Returns:
            Best parser instance or None if none available
        """
        available = self.available_parsers
        
        if not available:
            return None
        
        if pdf_path and pdf_path.exists():
            # Test parsers against the specific PDF
            return self._evaluate_parsers_for_pdf(pdf_path)
        
        # Return parsers in order of preference
        preference_order = ['pdfplumber', 'pymupdf', 'PyPDF2']
        
        for preferred_name in preference_order:
            for parser in available:
                if parser.library_name == preferred_name:
                    return parser
        
        # Return first available parser if none match preferences
        return available[0]
    
    def _evaluate_parsers_for_pdf(self, pdf_path: Path) -> Optional[BaseParser]:
        """
        Evaluate parsers against a specific PDF file.
        
        Args:
            pdf_path: PDF file to test against
            
        Returns:
            Best parser for this PDF or None
        """
        cache_key = str(pdf_path)
        
        if cache_key in self._evaluation_cache:
            parser_name = self._evaluation_cache[cache_key]
            return self._parsers.get(parser_name)
        
        best_parser = None
        best_score = -1
        
        for parser in self.available_parsers:
            try:
                score = self._evaluate_parser(parser, pdf_path)
                if score > best_score:
                    best_score = score
                    best_parser = parser
            except Exception:
                # Parser failed evaluation, skip it
                continue
        
        if best_parser:
            self._evaluation_cache[cache_key] = best_parser.library_name
        
        return best_parser
    
    def _evaluate_parser(self, parser: BaseParser, pdf_path: Path) -> float:
        """
        Evaluate a parser's performance on a specific PDF.
        
        Args:
            parser: Parser to evaluate
            pdf_path: PDF file to test
            
        Returns:
            Score (higher is better)
        """
        score = 0.0
        
        try:
            # Test basic text extraction
            text = parser.extract_text(pdf_path)
            if text and len(text.strip()) > 0:
                score += 1.0
                
                # Bonus for longer text (more content extracted)
                score += min(len(text) / 10000, 1.0)
                
                # Bonus for finding transaction-like patterns
                if self._contains_transaction_patterns(text):
                    score += 2.0
                
                # Bonus for finding amount patterns
                if self._contains_amount_patterns(text):
                    score += 1.0
                
                # Bonus for finding date patterns
                if self._contains_date_patterns(text):
                    score += 1.0
            
        except Exception:
            score = 0.0
        
        return score
    
    def _contains_transaction_patterns(self, text: str) -> bool:
        """Check if text contains transaction-like patterns."""
        import re
        
        patterns = [
            r'\$[\d,]+\.?\d*',  # Dollar amounts
            r'MERCADO PAGO',    # Known merchant patterns
            r'PAYU\*',          # Payment processor patterns
            r'\d{8}',           # Date patterns (DDMMYYYY)
        ]
        
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False
    
    def _contains_amount_patterns(self, text: str) -> bool:
        """Check if text contains amount patterns."""
        import re
        return bool(re.search(r'\$[\d,]+\.?\d*', text))
    
    def _contains_date_patterns(self, text: str) -> bool:
        """Check if text contains date patterns."""
        import re
        return bool(re.search(r'\d{2}[/\-]\d{2}[/\-]\d{4}|\d{8}', text))
    
    def test_all_parsers(self, pdf_path: Path) -> Dict[str, dict]:
        """
        Test all available parsers against a PDF file.
        
        Args:
            pdf_path: PDF file to test
            
        Returns:
            Dictionary with test results for each parser
        """
        results = {}
        
        for parser in self.available_parsers:
            try:
                # Test extraction
                text = parser.extract_text(pdf_path)
                success = text is not None and len(text.strip()) > 0
                
                results[parser.library_name] = {
                    'success': success,
                    'text_length': len(text) if text else 0,
                    'score': self._evaluate_parser(parser, pdf_path) if success else 0.0,
                    'error': None
                }
                
            except Exception as e:
                results[parser.library_name] = {
                    'success': False,
                    'text_length': 0,
                    'score': 0.0,
                    'error': str(e)
                }
        
        return results
    
    def get_parser_info(self) -> Dict[str, dict]:
        """
        Get information about all parsers.
        
        Returns:
            Dictionary with parser information
        """
        info = {}
        
        for name, parser in self._parsers.items():
            info[name] = parser.get_info()
        
        return info
    
    def clear_cache(self):
        """Clear the evaluation cache."""
        self._evaluation_cache.clear()
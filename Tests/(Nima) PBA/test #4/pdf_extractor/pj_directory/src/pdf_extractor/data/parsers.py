"""
Data parsing utilities for dates, amounts, and descriptions.
"""

import re
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from typing import Optional, List
from dateutil import parser as date_parser


class DateParser:
    """Handles parsing of various date formats found in PDF files."""
    
    def __init__(self):
        # Common date patterns for credit card statements
        self.date_patterns = [
            # DD MM YY format (e.g., "15 03 25")
            (r'(\d{1,2})\s+(\d{1,2})\s+(\d{2})', '%d %m %y'),
            # DD/MM/YY format (e.g., "15/03/25")
            (r'(\d{1,2})/(\d{1,2})/(\d{2})', '%d/%m/%y'),
            # DD-MM-YY format (e.g., "15-03-25")
            (r'(\d{1,2})-(\d{1,2})-(\d{2})', '%d-%m-%y'),
            # DD MM YYYY format (e.g., "15 03 2025")
            (r'(\d{1,2})\s+(\d{1,2})\s+(\d{4})', '%d %m %Y'),
            # DD/MM/YYYY format (e.g., "15/03/2025")
            (r'(\d{1,2})/(\d{1,2})/(\d{4})', '%d/%m/%Y'),
            # YYYY-MM-DD format (e.g., "2025-03-15")
            (r'(\d{4})-(\d{1,2})-(\d{1,2})', '%Y-%m-%d'),
        ]
    
    def parse_date(self, date_str: str) -> Optional[date]:
        """
        Parse a date string using various patterns.
        
        Args:
            date_str: String containing date information
            
        Returns:
            Parsed date object or None if parsing fails
        """
        if not date_str or not date_str.strip():
            return None
        
        date_str = date_str.strip()
        
        # Try each pattern
        for pattern, format_str in self.date_patterns:
            match = re.search(pattern, date_str)
            if match:
                try:
                    parsed_date = datetime.strptime(match.group(0), format_str).date()
                    # Handle 2-digit years by assuming 20xx
                    if parsed_date.year < 100:
                        parsed_date = parsed_date.replace(year=parsed_date.year + 2000)
                    return parsed_date
                except ValueError:
                    continue
        
        # Fallback to dateutil parser
        try:
            parsed_date = date_parser.parse(date_str, fuzzy=True).date()
            return parsed_date
        except (ValueError, TypeError):
            return None
    
    def extract_date_from_text(self, text: str) -> Optional[date]:
        """
        Extract the first valid date found in text.
        
        Args:
            text: Text containing potential date information
            
        Returns:
            First valid date found or None
        """
        # Split text into potential date components
        words = text.split()
        
        # Try combinations of 2-3 consecutive words
        for i in range(len(words) - 1):
            for j in range(i + 2, min(i + 4, len(words) + 1)):
                date_candidate = ' '.join(words[i:j])
                parsed_date = self.parse_date(date_candidate)
                if parsed_date:
                    return parsed_date
        
        return None


class AmountParser:
    """Handles parsing of monetary amounts from PDF text."""
    
    def __init__(self):
        # Amount patterns for different formats
        self.amount_patterns = [
            # $1,234.56 or $1234.56
            r'\$\s*([\d,]+\.?\d*)',
            # 1,234.56 or 1234.56 (without currency symbol)
            r'([\d,]+\.\d{2})',
            # 1.234,56 (European format)
            r'([\d.]+,\d{2})',
            # Plain numbers at end of line
            r'(\d+\.?\d*)\s*$'
        ]
    
    def parse_amount(self, amount_str: str) -> Optional[Decimal]:
        """
        Parse an amount string to Decimal.
        
        Args:
            amount_str: String containing amount information
            
        Returns:
            Parsed amount as Decimal or None if parsing fails
        """
        if not amount_str or not amount_str.strip():
            return None
        
        amount_str = amount_str.strip()
        
        # Try each pattern
        for pattern in self.amount_patterns:
            match = re.search(pattern, amount_str)
            if match:
                amount_text = match.group(1)
                
                # Clean the amount text
                amount_text = amount_text.replace('$', '').replace(' ', '')
                
                # Handle European format (1.234,56 -> 1234.56)
                if ',' in amount_text and '.' in amount_text:
                    if amount_text.rfind(',') > amount_text.rfind('.'):
                        # European format: 1.234,56
                        amount_text = amount_text.replace('.', '').replace(',', '.')
                    else:
                        # US format: 1,234.56
                        amount_text = amount_text.replace(',', '')
                elif ',' in amount_text:
                    # Could be thousands separator or decimal separator
                    comma_pos = amount_text.rfind(',')
                    if len(amount_text) - comma_pos == 3:  # Likely decimal separator
                        amount_text = amount_text.replace(',', '.')
                    else:  # Likely thousands separator
                        amount_text = amount_text.replace(',', '')
                
                try:
                    return Decimal(amount_text)
                except (InvalidOperation, ValueError):
                    continue
        
        return None
    
    def extract_amount_from_text(self, text: str) -> Optional[Decimal]:
        """
        Extract the largest amount found in text.
        
        Args:
            text: Text containing potential amount information
            
        Returns:
            Largest amount found or None
        """
        amounts = []
        
        for pattern in self.amount_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                amount = self.parse_amount(match.group(0))
                if amount and amount > 0:
                    amounts.append(amount)
        
        return max(amounts) if amounts else None


class DescriptionCleaner:
    """Handles cleaning and normalizing transaction descriptions."""
    
    def __init__(self):
        # Common cleanup patterns
        self.cleanup_rules = [
            # Remove trailing numbers that might be reference codes
            (r'\s+\d{4,}\s*$', ''),
            # Remove multiple spaces
            (r'\s+', ' '),
            # Remove common location codes
            (r'\s+[A-Z]{2,3}\s*$', ''),
            # Remove asterisks and other special characters
            (r'[*#@]+', ''),
            # Remove leading/trailing whitespace
            (r'^\s+|\s+$', ''),
        ]
    
    def clean_description(self, description: str) -> str:
        """
        Clean and normalize a transaction description.
        
        Args:
            description: Raw description text
            
        Returns:
            Cleaned description
        """
        if not description:
            return ""
        
        cleaned = description
        
        # Apply cleanup rules
        for pattern, replacement in self.cleanup_rules:
            cleaned = re.sub(pattern, replacement, cleaned)
        
        # Capitalize first letter of each word
        cleaned = ' '.join(word.capitalize() for word in cleaned.split())
        
        return cleaned.strip()
    
    def extract_description_from_text(self, text: str, date_part: str = "", amount_part: str = "") -> str:
        """
        Extract description by removing date and amount parts from text.
        
        Args:
            text: Full transaction text
            date_part: Date portion to remove
            amount_part: Amount portion to remove
            
        Returns:
            Extracted and cleaned description
        """
        description = text
        
        # Remove date and amount parts
        if date_part:
            description = description.replace(date_part, '')
        if amount_part:
            description = description.replace(amount_part, '')
        
        # Clean the remaining text
        return self.clean_description(description)
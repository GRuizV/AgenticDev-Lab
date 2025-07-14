"""
Avianca credit card specific patterns for transaction extraction.
"""

import re
from typing import List, Optional, Dict, Any
from datetime import date
from decimal import Decimal

from ..data.models import Pattern, Transaction
from ..data.parsers import DateParser, AmountParser, DescriptionCleaner


class AviancaPatterns:
    """Handles Avianca credit card PDF pattern recognition and extraction."""
    
    def __init__(self):
        self.date_parser = DateParser()
        self.amount_parser = AmountParser()
        self.description_cleaner = DescriptionCleaner()
        
        # Avianca transaction patterns
        self.patterns = {
            "avianca_standard": Pattern(
                name="avianca_standard",
                issuer="avianca",
                card_type="both",
                # Pattern for: YYYY MM DD HH description amount
                transaction_regex=r"(\d{4})\s+(\d{2})\s+(\d{2})\s+(\d{2})\s+(.+?)\s+[\d,]+\.\d{2}\s+\$?([\d,]+\.\d{2})",
                date_format="%Y %m %d",
                amount_format="$X,XXX.XX",
                description_cleanup_rules=["remove_trailing_numbers", "clean_location_codes"],
                confidence_threshold=0.8
            ),
            "avianca_alternative": Pattern(
                name="avianca_alternative", 
                issuer="avianca",
                card_type="both",
                # Alternative pattern for different layouts
                transaction_regex=r"(\d{2})\s+(\d{2})\s+(\d{2})\s+(.+?)\s+\$?([\d,]+\.\d{2})",
                date_format="%d %m %y",
                amount_format="$X,XXX.XX",
                description_cleanup_rules=["remove_trailing_numbers", "clean_location_codes"],
                confidence_threshold=0.7
            )
        }
    
    def detect_avianca_pattern(self, text: str) -> Optional[str]:
        """
        Detect which Avianca pattern applies to the given text.
        
        Args:
            text: PDF text content
            
        Returns:
            Pattern name if detected, None otherwise
        """
        # Look for Avianca indicators
        avianca_indicators = [
            r"avianca",
            r"lifemiles",
            r"av\s*-\s*(mc|vs)",  # AV - MC or AV - VS
            r"tarjeta\s+de\s+credito"
        ]
        
        text_lower = text.lower()
        has_avianca_indicator = any(re.search(pattern, text_lower) for pattern in avianca_indicators)
        
        if not has_avianca_indicator:
            return None
        
        # Test each pattern to see which matches best
        best_pattern = None
        best_match_count = 0
        
        for pattern_name, pattern in self.patterns.items():
            matches = re.findall(pattern.transaction_regex, text, re.MULTILINE)
            match_count = len(matches)
            
            if match_count > best_match_count:
                best_match_count = match_count
                best_pattern = pattern_name
        
        # Return pattern if we found reasonable number of matches
        if best_match_count >= 2:  # At least 2 transactions
            return best_pattern
        
        return None
    
    def extract_transactions(self, text: str, pattern_name: str = None) -> List[Transaction]:
        """
        Extract transactions from Avianca PDF text.
        
        Args:
            text: PDF text content
            pattern_name: Specific pattern to use, or None for auto-detection
            
        Returns:
            List of extracted transactions
        """
        if pattern_name is None:
            pattern_name = self.detect_avianca_pattern(text)
        
        if pattern_name is None or pattern_name not in self.patterns:
            return []
        
        pattern = self.patterns[pattern_name]
        transactions = []
        
        # Find all transaction matches
        matches = re.finditer(pattern.transaction_regex, text, re.MULTILINE)
        
        for match in matches:
            transaction = self._parse_transaction_match(match, pattern)
            if transaction and transaction.validate():
                transactions.append(transaction)
        
        return transactions
    
    def _parse_transaction_match(self, match: re.Match, pattern: Pattern) -> Optional[Transaction]:
        """
        Parse a regex match into a Transaction object.
        
        Args:
            match: Regex match object
            pattern: Pattern used for matching
            
        Returns:
            Transaction object or None if parsing fails
        """
        try:
            groups = match.groups()
            
            if pattern.name == "avianca_standard":
                # Format: YYYY MM DD HH description amount
                year, month, day, hour, description, amount_str = groups
                date_str = f"{year} {month} {day}"
                
            elif pattern.name == "avianca_alternative":
                # Format: DD MM YY description amount
                day, month, year, description, amount_str = groups
                date_str = f"{day} {month} {year}"
            
            else:
                return None
            
            # Parse date
            transaction_date = self.date_parser.parse_date(date_str)
            if not transaction_date:
                return None
            
            # Parse amount
            amount = self.amount_parser.parse_amount(amount_str)
            if not amount:
                return None
            
            # Clean description
            cleaned_description = self.description_cleaner.clean_description(description)
            if not cleaned_description:
                return None
            
            # Create transaction
            transaction = Transaction(
                date=transaction_date,
                description=cleaned_description,
                amount=amount,
                raw_text=match.group(0),
                confidence=pattern.confidence_threshold
            )
            
            return transaction
            
        except Exception as e:
            # Log error but don't fail the entire extraction
            return None
    
    def get_pattern_info(self, pattern_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific pattern.
        
        Args:
            pattern_name: Name of the pattern
            
        Returns:
            Pattern information dictionary
        """
        if pattern_name not in self.patterns:
            return None
        
        pattern = self.patterns[pattern_name]
        return pattern.to_dict()
    
    def list_available_patterns(self) -> List[str]:
        """
        Get list of available Avianca patterns.
        
        Returns:
            List of pattern names
        """
        return list(self.patterns.keys())
    
    def validate_pattern_against_text(self, text: str, pattern_name: str) -> Dict[str, Any]:
        """
        Validate how well a pattern matches against text.
        
        Args:
            text: PDF text content
            pattern_name: Pattern to validate
            
        Returns:
            Validation results dictionary
        """
        if pattern_name not in self.patterns:
            return {"error": "Pattern not found"}
        
        pattern = self.patterns[pattern_name]
        
        # Count matches
        matches = re.findall(pattern.transaction_regex, text, re.MULTILINE)
        match_count = len(matches)
        
        # Try to extract transactions
        transactions = self.extract_transactions(text, pattern_name)
        valid_transactions = len(transactions)
        
        # Calculate success rate
        success_rate = valid_transactions / match_count if match_count > 0 else 0
        
        return {
            "pattern_name": pattern_name,
            "total_matches": match_count,
            "valid_transactions": valid_transactions,
            "success_rate": success_rate,
            "confidence": pattern.confidence_threshold,
            "recommended": success_rate >= 0.8 and match_count >= 2
        }
    
    def extract_bill_metadata(self, text: str) -> Dict[str, Any]:
        """
        Extract metadata about the bill (card type, period, etc.).
        
        Args:
            text: PDF text content
            
        Returns:
            Dictionary containing bill metadata
        """
        metadata = {
            "card_type": None,
            "period": None,
            "card_number": None,
            "issuer": "avianca"
        }
        
        # Extract card type (MC or VS)
        card_type_match = re.search(r"av\s*-\s*(mc|vs)", text.lower())
        if card_type_match:
            metadata["card_type"] = card_type_match.group(1).upper()
        
        # Extract period information
        period_patterns = [
            r"(\w{3})\s*-?\s*(\d{4})",  # MAR-2025 or MAR 2025
            r"(\d{2})\s*-\s*(\w{3})\s*-?\s*(\d{4})",  # 03-MAR-2025
        ]
        
        for pattern in period_patterns:
            period_match = re.search(pattern, text.upper())
            if period_match:
                if len(period_match.groups()) == 2:
                    month, year = period_match.groups()
                    metadata["period"] = f"{month}-{year}"
                elif len(period_match.groups()) == 3:
                    day, month, year = period_match.groups()
                    metadata["period"] = f"{month}-{year}"
                break
        
        # Extract partial card number
        card_number_match = re.search(r"(\*{4}\s*\d{4})", text)
        if card_number_match:
            metadata["card_number"] = card_number_match.group(1)
        
        return metadata
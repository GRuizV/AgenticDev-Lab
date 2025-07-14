"""
Core pattern matching engine for transaction extraction.
"""

import re
import logging
from typing import List, Optional, Dict, Any, Tuple
from datetime import date
from decimal import Decimal

from ..data.models import Pattern, Transaction
from ..data.parsers import DateParser, AmountParser, DescriptionCleaner


class PatternMatcher:
    """Core pattern matching and transaction extraction engine."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.date_parser = DateParser()
        self.amount_parser = AmountParser()
        self.description_cleaner = DescriptionCleaner()
        
        # Compiled regex cache for performance
        self._regex_cache = {}
    
    def match_transactions(self, text: str, pattern: Pattern) -> List[Transaction]:
        """
        Match transactions using regex patterns.
        
        Args:
            text: PDF text content
            pattern: Pattern object containing regex and parsing rules
            
        Returns:
            List of extracted transactions
        """
        if not text or not pattern:
            return []
        
        try:
            # Get compiled regex (with caching)
            regex = self._get_compiled_regex(pattern.transaction_regex)
            
            # Find all matches
            matches = list(regex.finditer(text))
            self.logger.debug(f"Found {len(matches)} potential matches with pattern {pattern.name}")
            
            transactions = []
            for match in matches:
                transaction = self._parse_match_to_transaction(match, pattern, text)
                if transaction and self.validate_transaction(transaction):
                    transactions.append(transaction)
                else:
                    self.logger.debug(f"Invalid transaction from match: {match.group(0)[:50]}...")
            
            self.logger.info(f"Successfully extracted {len(transactions)} valid transactions")
            return transactions
            
        except Exception as e:
            self.logger.error(f"Error matching transactions with pattern {pattern.name}: {str(e)}")
            return []
    
    def validate_transaction(self, transaction: Transaction) -> bool:
        """
        Validate individual transaction data.
        
        Args:
            transaction: Transaction object to validate
            
        Returns:
            True if transaction is valid, False otherwise
        """
        try:
            # Basic validation
            if not transaction.validate():
                return False
            
            # Additional business logic validation
            
            # Date should be reasonable (not too far in past/future)
            from datetime import date, timedelta
            today = date.today()
            min_date = today - timedelta(days=365 * 5)  # 5 years ago
            max_date = today + timedelta(days=365)  # 1 year in future
            
            if not (min_date <= transaction.date <= max_date):
                self.logger.debug(f"Transaction date out of range: {transaction.date}")
                return False
            
            # Amount should be reasonable (not negative, not too large)
            if transaction.amount <= 0 or transaction.amount > Decimal('10000000'):  # 10M limit
                self.logger.debug(f"Transaction amount out of range: {transaction.amount}")
                return False
            
            # Description should not be empty after cleaning
            if not transaction.description.strip():
                self.logger.debug("Transaction description is empty")
                return False
            
            return True
            
        except Exception as e:
            self.logger.debug(f"Error validating transaction: {str(e)}")
            return False
    
    def _get_compiled_regex(self, pattern_str: str) -> re.Pattern:
        """
        Get compiled regex with caching for performance.
        
        Args:
            pattern_str: Regex pattern string
            
        Returns:
            Compiled regex pattern
        """
        if pattern_str not in self._regex_cache:
            try:
                self._regex_cache[pattern_str] = re.compile(pattern_str, re.MULTILINE | re.DOTALL)
            except re.error as e:
                self.logger.error(f"Invalid regex pattern: {pattern_str}, error: {str(e)}")
                raise ValueError(f"Invalid regex pattern: {str(e)}")
        
        return self._regex_cache[pattern_str]
    
    def _parse_match_to_transaction(self, match: re.Match, pattern: Pattern, full_text: str) -> Optional[Transaction]:
        """
        Parse a regex match into a Transaction object.
        
        Args:
            match: Regex match object
            pattern: Pattern used for matching
            full_text: Full PDF text for context
            
        Returns:
            Transaction object or None if parsing fails
        """
        try:
            groups = match.groups()
            match_text = match.group(0)
            
            # Extract components based on pattern
            date_obj, description, amount = self._extract_transaction_components(
                groups, pattern, match_text
            )
            
            if not all([date_obj, description, amount]):
                return None
            
            # Create transaction
            transaction = Transaction(
                date=date_obj,
                description=description,
                amount=amount,
                raw_text=match_text,
                confidence=pattern.confidence_threshold
            )
            
            return transaction
            
        except Exception as e:
            self.logger.debug(f"Error parsing match to transaction: {str(e)}")
            return None
    
    def _extract_transaction_components(self, groups: Tuple, pattern: Pattern, match_text: str) -> Tuple[Optional[date], Optional[str], Optional[Decimal]]:
        """
        Extract date, description, and amount from regex groups.
        
        Args:
            groups: Regex match groups
            pattern: Pattern object with parsing rules
            match_text: Full matched text
            
        Returns:
            Tuple of (date, description, amount) or (None, None, None) if extraction fails
        """
        try:
            # This is a generic implementation - specific patterns may override this
            # For now, we'll assume the last group is amount and work backwards
            
            if len(groups) < 3:
                return None, None, None
            
            # Extract amount (usually the last group)
            amount_str = groups[-1]
            amount = self.amount_parser.parse_amount(amount_str)
            
            if not amount:
                return None, None, None
            
            # Extract date components (usually first few groups)
            date_parts = []
            description_parts = []
            
            # Determine which groups are date vs description
            for i, group in enumerate(groups[:-1]):  # Exclude amount group
                # Try to parse as date component
                if re.match(r'^\d{1,4}$', group.strip()):
                    date_parts.append(group)
                else:
                    description_parts.append(group)
            
            # Parse date
            date_str = ' '.join(date_parts) if date_parts else ''
            date_obj = self.date_parser.parse_date(date_str)
            
            # If date parsing failed, try to extract from full match
            if not date_obj:
                date_obj = self.date_parser.extract_date_from_text(match_text)
            
            # Parse description
            description = ' '.join(description_parts) if description_parts else ''
            
            # If no description from groups, extract from match text
            if not description.strip():
                # Remove date and amount parts from match text
                description = match_text
                if date_str:
                    description = description.replace(date_str, '')
                if amount_str:
                    description = description.replace(amount_str, '')
            
            # Clean description
            description = self.description_cleaner.clean_description(description)
            
            return date_obj, description, amount
            
        except Exception as e:
            self.logger.debug(f"Error extracting transaction components: {str(e)}")
            return None, None, None
    
    def test_pattern_against_text(self, text: str, pattern: Pattern) -> Dict[str, Any]:
        """
        Test how well a pattern performs against text.
        
        Args:
            text: PDF text content
            pattern: Pattern to test
            
        Returns:
            Dictionary with test results
        """
        try:
            # Get raw matches
            regex = self._get_compiled_regex(pattern.transaction_regex)
            raw_matches = list(regex.finditer(text))
            
            # Extract transactions
            transactions = self.match_transactions(text, pattern)
            
            # Calculate metrics
            total_matches = len(raw_matches)
            valid_transactions = len(transactions)
            success_rate = valid_transactions / total_matches if total_matches > 0 else 0
            
            # Analyze match quality
            match_samples = [match.group(0) for match in raw_matches[:5]]  # First 5 matches
            
            return {
                "pattern_name": pattern.name,
                "total_raw_matches": total_matches,
                "valid_transactions": valid_transactions,
                "success_rate": success_rate,
                "confidence_threshold": pattern.confidence_threshold,
                "match_samples": match_samples,
                "recommended": success_rate >= 0.8 and total_matches >= 2
            }
            
        except Exception as e:
            return {
                "pattern_name": pattern.name,
                "error": str(e),
                "recommended": False
            }
    
    def find_potential_patterns(self, text: str) -> List[Dict[str, Any]]:
        """
        Analyze text to find potential transaction patterns.
        
        Args:
            text: PDF text content
            
        Returns:
            List of potential pattern suggestions
        """
        suggestions = []
        
        # Common transaction line patterns
        potential_patterns = [
            # Date amount patterns
            r'(\d{1,2})\s+(\d{1,2})\s+(\d{2,4})\s+(.+?)\s+\$?([\d,]+\.\d{2})',
            r'(\d{4})\s+(\d{1,2})\s+(\d{1,2})\s+(.+?)\s+\$?([\d,]+\.\d{2})',
            r'(\d{1,2})/(\d{1,2})/(\d{2,4})\s+(.+?)\s+\$?([\d,]+\.\d{2})',
            # Description amount patterns
            r'(.+?)\s+(\d{1,2})/(\d{1,2})/(\d{2,4})\s+\$?([\d,]+\.\d{2})',
            r'(.+?)\s+\$?([\d,]+\.\d{2})\s*$'
        ]
        
        for i, pattern_str in enumerate(potential_patterns):
            try:
                regex = re.compile(pattern_str, re.MULTILINE)
                matches = list(regex.finditer(text))
                
                if len(matches) >= 2:  # At least 2 potential transactions
                    suggestions.append({
                        "pattern_id": f"suggested_{i+1}",
                        "regex": pattern_str,
                        "match_count": len(matches),
                        "sample_matches": [m.group(0) for m in matches[:3]],
                        "confidence": min(0.9, len(matches) / 10)  # Higher confidence with more matches
                    })
                    
            except re.error:
                continue
        
        # Sort by match count (descending)
        suggestions.sort(key=lambda x: x["match_count"], reverse=True)
        
        return suggestions[:5]  # Return top 5 suggestions
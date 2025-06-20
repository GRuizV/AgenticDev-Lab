"""
Transaction pattern detection and parsing.
"""

import re
from typing import List, Optional, Dict, Tuple
from ..models.transaction import Transaction
from ..config.patterns import TRANSACTION_PATTERNS, DESCRIPTION_PATTERNS
from ..config.expected_results import EXCLUDED_TRANSACTION_TYPES
from ..utils.text_processing import clean_text, extract_lines, clean_description
from ..utils.date_parser import parse_date, extract_date_from_line
from ..utils.amount_parser import parse_amount, extract_amounts_from_line


class TransactionPatternDetector:
    """Detects and parses transaction patterns from PDF text."""
    
    def __init__(self):
        """Initialize the pattern detector."""
        self.transaction_patterns = TRANSACTION_PATTERNS
        self.description_patterns = DESCRIPTION_PATTERNS
        self.excluded_types = EXCLUDED_TRANSACTION_TYPES
    
    def extract_transactions(self, text: str) -> List[Transaction]:
        """
        Extract transactions from PDF text.
        
        Args:
            text: Raw text from PDF extraction
            
        Returns:
            List of extracted transactions
        """
        if not text:
            return []
        
        # Clean and prepare text
        cleaned_text = clean_text(text)
        lines = extract_lines(cleaned_text)
        
        # Find transaction section
        transaction_lines = self._find_transaction_section(lines)
        
        # Extract transactions from the section
        transactions = self._parse_transactions(transaction_lines)
        
        # Filter out excluded transaction types
        filtered_transactions = self._filter_transactions(transactions)
        
        return filtered_transactions
    
    def _find_transaction_section(self, lines: List[str]) -> List[str]:
        """
        Find the section of text that contains transaction data.
        
        Args:
            lines: List of text lines
            
        Returns:
            List of lines containing transaction data
        """
        # For now, return all lines to ensure we don't miss transaction data
        # The patterns are working correctly, so the issue was section detection
        return lines
    
    def _is_transaction_section_start(self, line: str) -> bool:
        """Check if line marks the start of transaction section."""
        markers = [
            r'DETALLE',
            r'COMPROBANTE',
            r'NUMERO',
            r'VALOR COMPRA',
            r'DIAMESAÑO'
        ]
        
        for marker in markers:
            if re.search(marker, line, re.IGNORECASE):
                return True
        
        return False
    
    def _is_transaction_section_end(self, line: str) -> bool:
        """Check if line marks the end of transaction section."""
        markers = [
            r'CUPON DE PAGO',
            r'TOTAL\s+FACT',
            r'SALDO TOTAL',
            r'BANCOVALOR'
        ]
        
        for marker in markers:
            if re.search(marker, line, re.IGNORECASE):
                return True
        
        return False
    
    def _looks_like_transaction_line(self, line: str) -> bool:
        """Check if line looks like it contains transaction data."""
        # Look for patterns that suggest transaction data
        patterns = [
            r'\d{5,}\s*\d{8}',  # Transaction ID + date
            r'\$[\d,]+\.?\d*',  # Dollar amounts
            r'\d{8}\s*\$',      # Date + amount
        ]
        
        for pattern in patterns:
            if re.search(pattern, line):
                return True
        
        return False
    
    def _parse_transactions(self, lines: List[str]) -> List[Transaction]:
        """
        Parse transactions from lines of text.
        
        Args:
            lines: Lines of text containing transaction data
            
        Returns:
            List of parsed transactions
        """
        transactions = []
        
        # First, try to parse using multi-line patterns on the full text
        full_text = '\n'.join(lines)
        
        for pattern_idx, pattern in enumerate(self.transaction_patterns):
            matches = pattern.findall(full_text)
            
            for match_idx, match in enumerate(matches):
                # Create a mock match object for _extract_transaction_data
                class MockMatch:
                    def __init__(self, groups):
                        self._groups = groups
                    def groups(self):
                        return self._groups
                
                mock_match = MockMatch(match)
                transaction_data = self._extract_transaction_data(mock_match, str(match))
                
                if transaction_data:
                    # Use description from extracted data if available
                    description = transaction_data.get('description')
                    
                    # If no description in extracted data, look for it in the text
                    if not description:
                        description = self._find_description_for_match(lines, match)
                    
                    # Use a default description if none found
                    if not description:
                        description = f"TRANSACTION {transaction_data.get('date', 'UNKNOWN')}"
                    
                    transaction_data['description'] = description
                    
                    # Create transaction if we have all required data
                    if all(key in transaction_data for key in ['date', 'description', 'amount']):
                        try:
                            transaction = Transaction(
                                date=transaction_data['date'],
                                description=transaction_data['description'],
                                amount=transaction_data['amount']
                            )
                            transactions.append(transaction)
                        except ValueError as e:
                            # Skip invalid transactions
                            pass
        
        return transactions
    
    def _parse_transaction_line(self, line: str) -> Optional[Dict]:
        """
        Parse a single transaction line.
        
        Args:
            line: Line of text to parse
            
        Returns:
            Dictionary with transaction data or None
        """
        for pattern in self.transaction_patterns:
            match = pattern.search(line)
            if match:
                return self._extract_transaction_data(match, line)
        
        return None
    
    def _extract_transaction_data(self, match: re.Match, line: str) -> Optional[Dict]:
        """
        Extract transaction data from regex match.
        
        Args:
            match: Regex match object
            line: Original line of text
            
        Returns:
            Dictionary with transaction data
        """
        groups = match.groups()
        
        # Extract date and description based on pattern structure
        date_str = None
        description = None
        amount = None
        amount_str = None
        
        if len(groups) >= 5:
            # New pattern structure: (transaction_id, day, month, year, amount, [description])
            transaction_id, day, month, year, amount_str = groups[0], groups[1], groups[2], groups[3], groups[4]
            
            # Check if description is captured (6th group)
            if len(groups) >= 6:
                description = groups[5]
            
            # Convert 2-digit year to 4-digit year
            if len(year) == 2:
                year_int = int(year)
                if year_int >= 0 and year_int <= 30:  # Assume 2000-2030
                    year = f"20{year}"
                else:  # Assume 1970-1999
                    year = f"19{year}"
            
            # Ensure day and month are 2 digits
            day = day.zfill(2)
            month = month.zfill(2)
            
            date_str = f"{day}{month}{year}"
        
        if not date_str:
            # Try to extract date from the line
            date_str = extract_date_from_line(line)
        
        # Parse the date
        parsed_date = parse_date(date_str) if date_str else None
        
        # Extract amount
        if amount_str:
            amount = parse_amount(amount_str)
        
        # Fallback: extract amounts from line
        if amount is None or amount <= 0:
            amounts = extract_amounts_from_line(line)
            amount = amounts[0] if amounts else None
        
        # Clean up description if captured by regex
        if description:
            description = description.strip()
            # Remove location codes at the end (like "110111BOGOTA")
            description = re.sub(r'\s*\d{6,}[A-Z]*$', '', description)
            description = clean_description(description)
        
        if parsed_date and amount is not None and amount > 0:
            result = {
                'date': parsed_date,
                'amount': amount
            }
            if description:
                result['description'] = description
            return result
        
        return None
    
    def _find_description(self, lines: List[str], start_idx: int) -> Optional[str]:
        """
        Find transaction description starting from given line index.
        
        Args:
            lines: List of text lines
            start_idx: Index to start looking for description
            
        Returns:
            Cleaned description or None
        """
        if start_idx >= len(lines):
            return None
        
        # Check the next line for description
        desc_line = lines[start_idx].strip()
        
        if desc_line and self._is_description_line(desc_line):
            return clean_description(desc_line)
        
        return None
    
    def _is_description_line(self, line: str) -> bool:
        """
        Check if line appears to be a transaction description.
        
        Args:
            line: Line to check
            
        Returns:
            True if line appears to be a description
        """
        if not line:
            return False
        
        # Should not contain dollar signs (amounts)
        if '$' in line:
            return False
        
        # Should not be all numbers
        if re.match(r'^\d+$', line):
            return False
        
        # Should contain some letters
        if not re.search(r'[A-Z]', line.upper()):
            return False
        
        # Should start with letter or number
        if not re.match(r'^[A-Z0-9]', line.upper()):
            return False
        
        return True
    
    def _filter_transactions(self, transactions: List[Transaction]) -> List[Transaction]:
        """
        Filter out excluded transaction types.
        
        Args:
            transactions: List of transactions to filter
            
        Returns:
            Filtered list of transactions
        """
        filtered = []
        
        for transaction in transactions:
            # Skip zero-amount transactions
            if transaction.amount <= 0:
                continue
            
            # Skip excluded transaction types
            description_upper = transaction.description.upper()
            is_excluded = False
            
            for excluded_type in self.excluded_types:
                if excluded_type.upper() in description_upper:
                    is_excluded = True
                    break
            
            if not is_excluded:
                filtered.append(transaction)
        
        return filtered
    
    def get_debug_info(self, text: str) -> Dict:
        """
        Get debug information about pattern detection.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with debug information
        """
        cleaned_text = clean_text(text)
        lines = extract_lines(cleaned_text)
        transaction_lines = self._find_transaction_section(lines)
        
        return {
            'total_lines': len(lines),
            'transaction_section_lines': len(transaction_lines),
            'transaction_section_start': lines.index(transaction_lines[0]) if transaction_lines and transaction_lines[0] in lines else None,
            'patterns_tested': len(self.transaction_patterns),
            'excluded_types': self.excluded_types
        }
    
    def _parse_transaction_block(self, block_text: str, start_line: int) -> Optional[Dict]:
        """
        Parse a multi-line transaction block.
        
        Args:
            block_text: Text block containing potential transaction
            start_line: Starting line number for debugging
            
        Returns:
            Dictionary with transaction data or None
        """
        for pattern in self.transaction_patterns:
            match = pattern.search(block_text)
            if match:
                result = self._extract_transaction_data(match, block_text)
                if result:
                    print(f"Debug: Found transaction in block starting at line {start_line}: {result}")
                    return result
        return None
    
    def _find_description_in_block(self, lines: List[str]) -> Optional[str]:
        """
        Find transaction description within a block of lines.
        
        Args:
            lines: Block of lines to search
            
        Returns:
            Cleaned description or None
        """
        for line in lines:
            line = line.strip()
            if self._is_description_line(line):
                return clean_description(line)
        return None
    
    def _contains_transaction_data(self, line: str, match: tuple) -> bool:
        """
        Check if a line contains transaction data that matches our pattern.
        
        Args:
            line: Line to check
            match: The regex match tuple
            
        Returns:
            True if line contains matching transaction data
        """
        # Look for date components and amounts in the line
        # The match tuple contains (transaction_id, day, month, year, amount) or similar
        if len(match) >= 4:
            try:
                # Extract date components from match
                if len(match) >= 5:
                    # Pattern with transaction ID
                    day, month, year = str(match[1]), str(match[2]), str(match[3])
                else:
                    # Pattern without transaction ID
                    day, month, year = str(match[0]), str(match[1]), str(match[2])
                
                # Check if the line contains these date components
                if day in line and month in line and year in line:
                    return True
            except (IndexError, ValueError):
                pass
        
        return False
    
    def _extract_description_from_transaction_line(self, line: str) -> Optional[str]:
        """
        Extract merchant description from a transaction line.
        
        Args:
            line: Transaction line containing all data
            
        Returns:
            Extracted description or None
        """
        # Pattern for transaction lines: TransactionID Day Month Year Description Location Rate Amount Amount Amount Quotas
        # Example: "7888 15 02 25 PAYU*NETFLIX 110111BOGOTA 26.19 $44,900.00 $44,900.00 $0.00 01 01 00"
        
        # Remove extra spaces and split
        parts = line.split()
        
        if len(parts) < 8:  # Need at least: ID, day, month, year, description, rate, amount1, amount2
            return None
        
        # Find where the description starts and ends
        # Description starts after year (4th element) and ends before the rate (numeric value)
        description_parts = []
        start_idx = 4  # After transaction ID, day, month, year
        
        for i in range(start_idx, len(parts)):
            part = parts[i]
            
            # Stop when we hit a numeric rate (like "26.19") or amount (like "$44,900.00")
            if re.match(r'^\d+\.\d+$', part) or part.startswith('$'):
                break
            
            # Check if this part looks like a location code (numbers at the end)
            # If it's all digits or ends with location pattern, it might be location
            if re.match(r'^\d+[A-Z]*$', part) and len(description_parts) > 0:
                # This could be a location code, include it in description
                description_parts.append(part)
            elif not re.match(r'^\d+$', part):  # Not just numbers
                description_parts.append(part)
        
        if description_parts:
            description = ' '.join(description_parts)
            
            # Clean up the description
            # Remove common location patterns at the end if they look like codes
            description = re.sub(r'\s+\d{6,}[A-Z]*$', '', description)
            
            return description.strip()
        
        return None
    
    def _find_description_for_match(self, lines: List[str], match: tuple) -> Optional[str]:
        """
        Find transaction description for a specific match.
        
        Args:
            lines: List of text lines
            match: The regex match tuple
            
        Returns:
            Cleaned description or None
        """
        # For multi-line structure, find the description that follows the transaction data
        # The match contains (transaction_id, day, month, year, amount) or (day, month, year, amount)
        
        if len(match) >= 4:
            # Extract the components to search for
            if len(match) >= 5:
                # Pattern with transaction ID
                transaction_id, day, month, year = str(match[0]), str(match[1]), str(match[2]), str(match[3])
                search_components = [transaction_id, day, month, year]
            else:
                # Pattern without transaction ID
                day, month, year = str(match[0]), str(match[1]), str(match[2])
                search_components = [day, month, year]
            
            # Find the transaction block in the lines
            transaction_start_idx = None
            for i, line in enumerate(lines):
                line = line.strip()
                if line == search_components[0]:  # Found the first component
                    # Check if the following lines match the pattern
                    if self._matches_transaction_sequence(lines, i, search_components):
                        transaction_start_idx = i
                        break
            
            if transaction_start_idx is not None:
                # Look for description after the transaction block
                # Transaction block structure: ID, day, month, year, rate, amount1, amount2, amount3, quota1, quota2, quota3, description
                description_idx = transaction_start_idx + len(search_components) + 7  # Skip rate + 3 amounts + 3 quotas
                
                if description_idx < len(lines):
                    potential_description = lines[description_idx].strip()
                    if self._is_description_line(potential_description):
                        return clean_description(potential_description)
        
        # Fallback: look for description lines that contain text but not numbers/amounts
        for line in lines:
            line = line.strip()
            if self._is_description_line(line):
                return clean_description(line)
        return None
    
    def _matches_transaction_sequence(self, lines: List[str], start_idx: int, search_components: List[str]) -> bool:
        """
        Check if lines starting at start_idx match the expected transaction sequence.
        
        Args:
            lines: List of text lines
            start_idx: Starting index to check
            search_components: List of components to match in sequence
            
        Returns:
            True if the sequence matches
        """
        if start_idx + len(search_components) > len(lines):
            return False
        
        for i, component in enumerate(search_components):
            if lines[start_idx + i].strip() != component:
                return False
        
        return True
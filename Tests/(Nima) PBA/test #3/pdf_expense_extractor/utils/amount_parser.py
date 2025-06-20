"""
Amount parsing utilities for transaction amounts.
"""

import re
from typing import Optional


def parse_amount(amount_str: str) -> Optional[float]:
    """
    Parse amount from various formats and return as float.
    
    Args:
        amount_str: Amount string in various formats
        
    Returns:
        Amount as float or None if parsing fails
    """
    if not amount_str:
        return None
    
    # Clean the amount string
    amount_str = str(amount_str).strip()
    
    # Remove currency symbols and extra characters
    amount_str = re.sub(r'[$€£¥₹₽]', '', amount_str)
    
    # Remove parentheses (sometimes used for negative amounts)
    is_negative = '(' in amount_str and ')' in amount_str
    amount_str = re.sub(r'[()]', '', amount_str)
    
    # Handle comma as thousands separator
    # First, check if comma is likely a decimal separator
    comma_count = amount_str.count(',')
    dot_count = amount_str.count('.')
    
    if comma_count == 1 and dot_count == 0:
        # Could be decimal separator (European format)
        # Check if there are exactly 2 digits after comma
        if re.match(r'^\d+,\d{2}$', amount_str):
            amount_str = amount_str.replace(',', '.')
        else:
            # Likely thousands separator
            amount_str = amount_str.replace(',', '')
    elif comma_count > 0 and dot_count == 0:
        # Multiple commas, likely thousands separators
        amount_str = amount_str.replace(',', '')
    elif comma_count > 0 and dot_count == 1:
        # Both comma and dot, comma is thousands separator
        amount_str = amount_str.replace(',', '')
    
    # Remove any remaining non-digit characters except decimal point
    amount_str = re.sub(r'[^\d.]', '', amount_str)
    
    if not amount_str:
        return None
    
    try:
        amount = float(amount_str)
        return -amount if is_negative else amount
    except ValueError:
        return None


def extract_amounts_from_line(line: str) -> list:
    """
    Extract all amounts from a line of text.
    
    Args:
        line: Text line that may contain amounts
        
    Returns:
        List of amounts found in the line
    """
    if not line:
        return []
    
    amounts = []
    
    # Pattern to match various amount formats
    amount_patterns = [
        r'\$?([\d,]+\.?\d*)',  # $1,234.56 or 1,234.56
        r'([\d,]+\.?\d*)\s*\$',  # 1,234.56$
        r'([\d,]+,\d{2})',  # European format: 1.234,56
    ]
    
    for pattern in amount_patterns:
        matches = re.findall(pattern, line)
        for match in matches:
            amount = parse_amount(match)
            if amount is not None and amount > 0:  # Only positive amounts
                amounts.append(amount)
    
    return amounts


def format_amount(amount: float, currency_symbol: str = "$", decimal_places: int = 2) -> str:
    """
    Format amount for display.
    
    Args:
        amount: Amount to format
        currency_symbol: Currency symbol to use
        decimal_places: Number of decimal places
        
    Returns:
        Formatted amount string
    """
    if amount is None:
        return "N/A"
    
    # Format with thousands separator and specified decimal places
    formatted = f"{amount:,.{decimal_places}f}"
    
    return f"{currency_symbol}{formatted}"


def is_valid_amount(amount_str: str) -> bool:
    """
    Check if an amount string is valid.
    
    Args:
        amount_str: Amount string to validate
        
    Returns:
        True if amount is valid, False otherwise
    """
    amount = parse_amount(amount_str)
    return amount is not None and amount >= 0


def normalize_amount(amount: float, precision: int = 2) -> float:
    """
    Normalize amount to specified precision.
    
    Args:
        amount: Amount to normalize
        precision: Number of decimal places
        
    Returns:
        Normalized amount
    """
    if amount is None:
        return 0.0
    
    return round(amount, precision)


def compare_amounts(amount1: float, amount2: float, tolerance: float = 0.01) -> bool:
    """
    Compare two amounts with tolerance.
    
    Args:
        amount1: First amount
        amount2: Second amount
        tolerance: Tolerance for comparison
        
    Returns:
        True if amounts are equal within tolerance
    """
    if amount1 is None or amount2 is None:
        return False
    
    return abs(amount1 - amount2) <= tolerance


def sum_amounts(amounts: list) -> float:
    """
    Sum a list of amounts safely.
    
    Args:
        amounts: List of amounts to sum
        
    Returns:
        Sum of amounts
    """
    if not amounts:
        return 0.0
    
    total = 0.0
    for amount in amounts:
        if amount is not None:
            total += amount
    
    return total


def convert_centavos_to_pesos(centavos: int) -> float:
    """
    Convert centavos (integer) to pesos (float).
    
    Args:
        centavos: Amount in centavos
        
    Returns:
        Amount in pesos
    """
    if centavos is None:
        return 0.0
    
    return centavos / 100.0


def convert_pesos_to_centavos(pesos: float) -> int:
    """
    Convert pesos (float) to centavos (integer).
    
    Args:
        pesos: Amount in pesos
        
    Returns:
        Amount in centavos
    """
    if pesos is None:
        return 0
    
    return int(round(pesos * 100))
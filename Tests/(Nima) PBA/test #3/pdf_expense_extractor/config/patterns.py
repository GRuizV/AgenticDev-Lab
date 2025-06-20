"""
Regular expression patterns for transaction detection.
"""

import re

# Updated patterns for multi-line transaction structure (PyMuPDF format)
# Based on actual PDF analysis: Transaction ID, Day, Month, Year, Rate, Amounts, Quotas on separate lines
TRANSACTION_PATTERNS = [
    # Primary pattern: Multi-line structure with transaction ID, date components, rate, and amounts
    # Matches transaction blocks like:
    # 7888
    # 15
    # 02
    # 25
    # 26.19
    # $44,900.00
    # $44,900.00
    # $0.00
    # 01
    # 01
    # 00
    # PAYU*NETFLIX           110111BOGOTA
    re.compile(
        r'(\d{4})\n(\d{1,2})\n(\d{1,2})\n(\d{2})\n[\d.]+\n\$?([\d,]+\.?\d*)\n\$?[\d,]+\.?\d*\n\$?[\d,]+\.?\d*\n\d+\n\d+\n\d+\n([A-Z][A-Z0-9\s\*\-\.]+)',
        re.MULTILINE
    )
]

# Patterns for description lines (usually follow transaction lines)
DESCRIPTION_PATTERNS = [
    # Primary pattern: merchant name and location
    re.compile(
        r'^([A-Z][A-Z0-9\s\*\-\.]+)\s+([A-Z\s]+)$',
        re.MULTILINE
    ),
    
    # Alternative pattern: single description line
    re.compile(
        r'^([A-Z][A-Z0-9\s\*\-\.]+)$',
        re.MULTILINE
    ),
    
    # Pattern for descriptions with special characters
    re.compile(
        r'^([A-Z][A-Z0-9\s\*\-\.\(\)\/]+)(?:\s+([A-Z\s]+))?$',
        re.MULTILINE
    )
]

# Pattern to identify amount values in text
AMOUNT_PATTERN = re.compile(r'\$?([\d,]+\.?\d*)')

# Pattern to clean and normalize descriptions
DESCRIPTION_CLEANUP_PATTERNS = [
    # Remove extra whitespace
    (re.compile(r'\s+'), ' '),
    
    # Remove trailing/leading whitespace
    (re.compile(r'^\s+|\s+$'), ''),
    
    # Normalize merchant codes
    (re.compile(r'\*+'), '*'),
]

# Date patterns for various formats
DATE_PATTERNS = [
    # DDMMYYYY format
    re.compile(r'(\d{2})(\d{2})(\d{4})'),
    
    # DD/MM/YYYY format
    re.compile(r'(\d{2})/(\d{2})/(\d{4})'),
    
    # DD-MM-YYYY format
    re.compile(r'(\d{2})-(\d{2})-(\d{4})'),
]

# Patterns to identify transaction sections in PDF
TRANSACTION_SECTION_MARKERS = [
    re.compile(r'DETALLE', re.IGNORECASE),
    re.compile(r'COMPROBANTE', re.IGNORECASE),
    re.compile(r'NUMERO', re.IGNORECASE),
    re.compile(r'VALOR COMPRA', re.IGNORECASE),
]

# Patterns to identify end of transaction sections
TRANSACTION_END_MARKERS = [
    re.compile(r'CUPON DE PAGO', re.IGNORECASE),
    re.compile(r'TOTAL', re.IGNORECASE),
    re.compile(r'SALDO', re.IGNORECASE),
]
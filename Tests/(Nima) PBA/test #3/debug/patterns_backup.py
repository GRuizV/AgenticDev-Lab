"""
Regular expression patterns for transaction detection.
"""

import re

# Primary pattern for transaction lines based on PDF analysis
# Format: [TransactionID][Date][Amount Data]$[Amount]$[Amount]$[Amount][Flags]
TRANSACTION_PATTERNS = [
    # Primary pattern: captures transaction ID, date, and amounts
    re.compile(
        r'(\d{5,})\s*(\d{2})(\d{2})(\d{4})\s*\$?([\d,]+\.?\d*)\s*\$?([\d,]+\.?\d*)\s*\$?([\d,]+\.?\d*)',
        re.MULTILINE
    ),
    
    # Alternative pattern for different formatting
    re.compile(
        r'(\d+)\s+(\d{2})(\d{2})(\d{4})\s+\$?([\d,]+\.?\d*)',
        re.MULTILINE
    ),
    
    # Fallback pattern for simpler transaction lines
    re.compile(
        r'(\d{2})(\d{2})(\d{4})\s*\$?([\d,]+\.?\d*)',
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
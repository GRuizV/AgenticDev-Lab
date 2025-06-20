"""
Text processing utilities for cleaning and normalizing PDF text.
"""

import re
from typing import List


def clean_text(text: str) -> str:
    """
    Clean and normalize text extracted from PDF.
    
    Args:
        text: Raw text from PDF extraction
        
    Returns:
        Cleaned and normalized text
    """
    if not text:
        return ""
    
    # Remove null bytes and other control characters
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
    
    # Normalize line endings
    text = re.sub(r'\r\n|\r', '\n', text)
    
    # Remove excessive whitespace but preserve line structure
    text = re.sub(r'[ \t]+', ' ', text)
    
    # Remove empty lines with only whitespace
    lines = text.split('\n')
    cleaned_lines = [line.strip() for line in lines if line.strip()]
    
    return '\n'.join(cleaned_lines)


def normalize_whitespace(text: str) -> str:
    """
    Normalize whitespace in text while preserving structure.
    
    Args:
        text: Text to normalize
        
    Returns:
        Text with normalized whitespace
    """
    if not text:
        return ""
    
    # Replace multiple spaces with single space
    text = re.sub(r' +', ' ', text)
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    return text


def extract_lines(text: str) -> List[str]:
    """
    Extract lines from text and clean them.
    
    Args:
        text: Multi-line text
        
    Returns:
        List of cleaned lines
    """
    if not text:
        return []
    
    lines = text.split('\n')
    cleaned_lines = []
    
    for line in lines:
        cleaned_line = normalize_whitespace(line)
        if cleaned_line:  # Only include non-empty lines
            cleaned_lines.append(cleaned_line)
    
    return cleaned_lines


def clean_description(description: str) -> str:
    """
    Clean and normalize transaction description.
    
    Args:
        description: Raw transaction description
        
    Returns:
        Cleaned description
    """
    if not description:
        return ""
    
    # Normalize whitespace
    description = normalize_whitespace(description)
    
    # Remove excessive asterisks
    description = re.sub(r'\*+', '*', description)
    
    # Clean up common formatting issues
    description = re.sub(r'\s+', ' ', description)
    
    # Remove trailing punctuation except periods
    description = re.sub(r'[,;:\-]+$', '', description)
    
    return description.strip().upper()


def is_transaction_line(line: str) -> bool:
    """
    Check if a line appears to contain transaction data.
    
    Args:
        line: Text line to check
        
    Returns:
        True if line appears to contain transaction data
    """
    if not line:
        return False
    
    # Look for patterns that indicate transaction data
    patterns = [
        r'\$[\d,]+\.?\d*',  # Dollar amounts
        r'\d{8}',           # Date patterns (DDMMYYYY)
        r'\d{5,}',          # Transaction IDs
    ]
    
    for pattern in patterns:
        if re.search(pattern, line):
            return True
    
    return False


def is_description_line(line: str) -> bool:
    """
    Check if a line appears to be a transaction description.
    
    Args:
        line: Text line to check
        
    Returns:
        True if line appears to be a description
    """
    if not line:
        return False
    
    # Description lines typically:
    # - Start with uppercase letters
    # - Contain merchant names
    # - May have location information
    
    # Must start with uppercase letter or number
    if not re.match(r'^[A-Z0-9]', line):
        return False
    
    # Should not contain dollar signs (amounts)
    if '$' in line:
        return False
    
    # Should not be all numbers
    if re.match(r'^\d+$', line):
        return False
    
    # Should contain some letters
    if not re.search(r'[A-Z]', line):
        return False
    
    return True
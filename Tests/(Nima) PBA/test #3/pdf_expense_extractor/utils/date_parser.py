"""
Date parsing utilities for transaction dates.
"""

import re
from datetime import datetime
from typing import Optional


def parse_date(date_str: str) -> Optional[str]:
    """
    Parse date from various formats and return ISO format (YYYY-MM-DD).
    
    Args:
        date_str: Date string in various formats
        
    Returns:
        Date in ISO format (YYYY-MM-DD) or None if parsing fails
    """
    if not date_str:
        return None
    
    # Clean the date string
    date_str = date_str.strip()
    
    # Try different date patterns
    patterns = [
        # DDMMYYYY format (most common in PDFs)
        (r'^(\d{2})(\d{2})(\d{4})$', lambda m: f"{m.group(3)}-{m.group(2)}-{m.group(1)}"),
        
        # DD/MM/YYYY format
        (r'^(\d{1,2})/(\d{1,2})/(\d{4})$', lambda m: f"{m.group(3)}-{m.group(2):0>2}-{m.group(1):0>2}"),
        
        # DD-MM-YYYY format
        (r'^(\d{1,2})-(\d{1,2})-(\d{4})$', lambda m: f"{m.group(3)}-{m.group(2):0>2}-{m.group(1):0>2}"),
        
        # YYYY-MM-DD format (already ISO)
        (r'^(\d{4})-(\d{1,2})-(\d{1,2})$', lambda m: f"{m.group(1)}-{m.group(2):0>2}-{m.group(3):0>2}"),
        
        # YYYY/MM/DD format
        (r'^(\d{4})/(\d{1,2})/(\d{1,2})$', lambda m: f"{m.group(1)}-{m.group(2):0>2}-{m.group(3):0>2}"),
    ]
    
    for pattern, formatter in patterns:
        match = re.match(pattern, date_str)
        if match:
            try:
                iso_date = formatter(match)
                # Validate the date
                datetime.strptime(iso_date, "%Y-%m-%d")
                return iso_date
            except ValueError:
                continue
    
    return None


def extract_date_from_line(line: str) -> Optional[str]:
    """
    Extract date from a line of text that may contain other data.
    
    Args:
        line: Text line that may contain a date
        
    Returns:
        Date in ISO format or None if no valid date found
    """
    if not line:
        return None
    
    # Look for date patterns in the line
    date_patterns = [
        r'(\d{2})(\d{2})(\d{4})',  # DDMMYYYY
        r'(\d{1,2})/(\d{1,2})/(\d{4})',  # DD/MM/YYYY
        r'(\d{1,2})-(\d{1,2})-(\d{4})',  # DD-MM-YYYY
        r'(\d{4})-(\d{1,2})-(\d{1,2})',  # YYYY-MM-DD
    ]
    
    for pattern in date_patterns:
        matches = re.findall(pattern, line)
        for match in matches:
            if len(match) == 3:
                # Determine format and parse
                if len(match[0]) == 4:  # YYYY format
                    date_str = f"{match[0]}-{match[1]:0>2}-{match[2]:0>2}"
                else:  # DD format
                    date_str = f"{match[2]}-{match[1]:0>2}-{match[0]:0>2}"
                
                # Validate the date
                try:
                    datetime.strptime(date_str, "%Y-%m-%d")
                    return date_str
                except ValueError:
                    continue
    
    return None


def format_date(date_str: str, output_format: str = "%Y-%m-%d") -> Optional[str]:
    """
    Format a date string to the specified format.
    
    Args:
        date_str: Date string in ISO format
        output_format: Desired output format (default: ISO)
        
    Returns:
        Formatted date string or None if parsing fails
    """
    if not date_str:
        return None
    
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        return date_obj.strftime(output_format)
    except ValueError:
        return None


def is_valid_date(date_str: str) -> bool:
    """
    Check if a date string is valid.
    
    Args:
        date_str: Date string to validate
        
    Returns:
        True if date is valid, False otherwise
    """
    if not date_str:
        return False
    
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def get_date_range_for_month(year: int, month: int) -> tuple:
    """
    Get the date range for a specific month.
    
    Args:
        year: Year (e.g., 2025)
        month: Month (1-12)
        
    Returns:
        Tuple of (start_date, end_date) in ISO format
    """
    try:
        start_date = datetime(year, month, 1)
        
        # Get last day of month
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
        
        # Subtract one day to get last day of current month
        end_date = datetime(end_date.year, end_date.month, end_date.day - 1)
        
        return (
            start_date.strftime("%Y-%m-%d"),
            end_date.strftime("%Y-%m-%d")
        )
    except ValueError:
        return None, None
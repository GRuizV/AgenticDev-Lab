"""
Validation utilities for PDF Credit Card Expense Extractor.
"""

import re
import os
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Union, Optional, Tuple, List

from .exceptions import ValidationError, FileAccessError


def validate_file_path(file_path: Union[str, Path], must_exist: bool = True, 
                      file_extensions: Optional[List[str]] = None) -> Path:
    """
    Validate file path.
    
    Args:
        file_path: Path to validate
        must_exist: Whether file must exist
        file_extensions: Allowed file extensions (e.g., ['.pdf'])
        
    Returns:
        Validated Path object
        
    Raises:
        ValidationError: If validation fails
    """
    try:
        path = Path(file_path)
        
        if must_exist and not path.exists():
            raise ValidationError(
                f"File does not exist: {path}",
                validation_type="file_existence",
                expected_value="exists",
                actual_value="not_found"
            )
        
        if must_exist and not path.is_file():
            raise ValidationError(
                f"Path is not a file: {path}",
                validation_type="file_type",
                expected_value="file",
                actual_value="directory" if path.is_dir() else "other"
            )
        
        if file_extensions:
            if path.suffix.lower() not in [ext.lower() for ext in file_extensions]:
                raise ValidationError(
                    f"Invalid file extension: {path.suffix}. Expected: {file_extensions}",
                    validation_type="file_extension",
                    expected_value=file_extensions,
                    actual_value=path.suffix
                )
        
        return path
        
    except ValidationError:
        raise
    except Exception as e:
        raise ValidationError(
            f"File path validation failed: {str(e)}",
            validation_type="file_path"
        ) from e


def validate_pdf_file(file_path: Union[str, Path]) -> Path:
    """
    Validate PDF file specifically.
    
    Args:
        file_path: Path to PDF file
        
    Returns:
        Validated Path object
        
    Raises:
        ValidationError: If validation fails
    """
    path = validate_file_path(file_path, must_exist=True, file_extensions=['.pdf'])
    
    # Check file size
    try:
        file_size = path.stat().st_size
        if file_size == 0:
            raise ValidationError(
                f"PDF file is empty: {path}",
                validation_type="file_size",
                expected_value="> 0 bytes",
                actual_value="0 bytes"
            )
        
        # Check for reasonable file size (not too large)
        max_size = 100 * 1024 * 1024  # 100MB
        if file_size > max_size:
            raise ValidationError(
                f"PDF file too large: {file_size / 1024 / 1024:.1f}MB. Max: {max_size / 1024 / 1024}MB",
                validation_type="file_size",
                expected_value=f"<= {max_size / 1024 / 1024}MB",
                actual_value=f"{file_size / 1024 / 1024:.1f}MB"
            )
        
    except OSError as e:
        raise ValidationError(
            f"Cannot access PDF file: {str(e)}",
            validation_type="file_access"
        ) from e
    
    return path


def validate_date_range(start_date: Union[str, date, datetime], 
                       end_date: Union[str, date, datetime],
                       date_format: str = "%Y-%m-%d") -> Tuple[date, date]:
    """
    Validate date range.
    
    Args:
        start_date: Start date
        end_date: End date
        date_format: Date format for string parsing
        
    Returns:
        Tuple of validated dates
        
    Raises:
        ValidationError: If validation fails
    """
    try:
        # Convert to date objects
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, date_format).date()
        elif isinstance(start_date, datetime):
            start_date = start_date.date()
        
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, date_format).date()
        elif isinstance(end_date, datetime):
            end_date = end_date.date()
        
        # Validate range
        if start_date > end_date:
            raise ValidationError(
                f"Start date {start_date} is after end date {end_date}",
                validation_type="date_range",
                expected_value="start_date <= end_date",
                actual_value=f"start_date ({start_date}) > end_date ({end_date})"
            )
        
        # Check for reasonable date range
        today = date.today()
        if start_date > today:
            raise ValidationError(
                f"Start date {start_date} is in the future",
                validation_type="date_validity",
                expected_value="<= today",
                actual_value=str(start_date)
            )
        
        return start_date, end_date
        
    except ValueError as e:
        raise ValidationError(
            f"Invalid date format: {str(e)}",
            validation_type="date_format"
        ) from e


def validate_amount(amount: Union[str, int, float, Decimal], 
                   min_amount: Optional[float] = None,
                   max_amount: Optional[float] = None) -> Decimal:
    """
    Validate monetary amount.
    
    Args:
        amount: Amount to validate
        min_amount: Minimum allowed amount
        max_amount: Maximum allowed amount
        
    Returns:
        Validated Decimal amount
        
    Raises:
        ValidationError: If validation fails
    """
    try:
        # Convert to Decimal for precise monetary calculations
        if isinstance(amount, str):
            # Clean up string (remove currency symbols, commas)
            cleaned = re.sub(r'[^\d.-]', '', amount)
            if not cleaned:
                raise ValidationError(
                    f"Invalid amount format: '{amount}'",
                    validation_type="amount_format",
                    expected_value="numeric value",
                    actual_value=amount
                )
            amount_decimal = Decimal(cleaned)
        else:
            amount_decimal = Decimal(str(amount))
        
        # Validate range
        if min_amount is not None and amount_decimal < Decimal(str(min_amount)):
            raise ValidationError(
                f"Amount {amount_decimal} is below minimum {min_amount}",
                validation_type="amount_range",
                expected_value=f">= {min_amount}",
                actual_value=str(amount_decimal)
            )
        
        if max_amount is not None and amount_decimal > Decimal(str(max_amount)):
            raise ValidationError(
                f"Amount {amount_decimal} exceeds maximum {max_amount}",
                validation_type="amount_range",
                expected_value=f"<= {max_amount}",
                actual_value=str(amount_decimal)
            )
        
        return amount_decimal
        
    except (InvalidOperation, ValueError) as e:
        raise ValidationError(
            f"Invalid amount: {str(e)}",
            validation_type="amount_format"
        ) from e


def validate_pattern_name(pattern_name: str, available_patterns: Optional[List[str]] = None) -> str:
    """
    Validate pattern name.
    
    Args:
        pattern_name: Pattern name to validate
        available_patterns: List of available patterns
        
    Returns:
        Validated pattern name
        
    Raises:
        ValidationError: If validation fails
    """
    if not pattern_name or not isinstance(pattern_name, str):
        raise ValidationError(
            "Pattern name must be a non-empty string",
            validation_type="pattern_name",
            expected_value="non-empty string",
            actual_value=str(pattern_name)
        )
    
    # Check format (alphanumeric, underscore, hyphen)
    if not re.match(r'^[a-zA-Z0-9_-]+$', pattern_name):
        raise ValidationError(
            f"Invalid pattern name format: '{pattern_name}'. Use only letters, numbers, underscore, and hyphen",
            validation_type="pattern_name_format",
            expected_value="alphanumeric with _ and -",
            actual_value=pattern_name
        )
    
    # Check against available patterns if provided
    if available_patterns is not None and pattern_name not in available_patterns:
        raise ValidationError(
            f"Pattern '{pattern_name}' not found. Available: {available_patterns}",
            validation_type="pattern_availability",
            expected_value=f"one of {available_patterns}",
            actual_value=pattern_name
        )
    
    return pattern_name


def validate_confidence_score(confidence: Union[str, int, float]) -> float:
    """
    Validate confidence score.
    
    Args:
        confidence: Confidence score to validate
        
    Returns:
        Validated confidence score (0.0 to 1.0)
        
    Raises:
        ValidationError: If validation fails
    """
    try:
        confidence_float = float(confidence)
        
        if not 0.0 <= confidence_float <= 1.0:
            raise ValidationError(
                f"Confidence score {confidence_float} must be between 0.0 and 1.0",
                validation_type="confidence_range",
                expected_value="0.0 <= confidence <= 1.0",
                actual_value=str(confidence_float)
            )
        
        return confidence_float
        
    except (ValueError, TypeError) as e:
        raise ValidationError(
            f"Invalid confidence score: {str(e)}",
            validation_type="confidence_format"
        ) from e


def validate_output_format(output_format: str) -> str:
    """
    Validate output format.
    
    Args:
        output_format: Output format to validate
        
    Returns:
        Validated output format
        
    Raises:
        ValidationError: If validation fails
    """
    valid_formats = ["table", "json", "csv"]
    
    if output_format not in valid_formats:
        raise ValidationError(
            f"Invalid output format: '{output_format}'. Valid formats: {valid_formats}",
            validation_type="output_format",
            expected_value=f"one of {valid_formats}",
            actual_value=output_format
        )
    
    return output_format


def validate_directory_path(dir_path: Union[str, Path], must_exist: bool = True,
                           create_if_missing: bool = False) -> Path:
    """
    Validate directory path.
    
    Args:
        dir_path: Directory path to validate
        must_exist: Whether directory must exist
        create_if_missing: Whether to create directory if missing
        
    Returns:
        Validated Path object
        
    Raises:
        ValidationError: If validation fails
    """
    try:
        path = Path(dir_path)
        
        if not path.exists():
            if must_exist and not create_if_missing:
                raise ValidationError(
                    f"Directory does not exist: {path}",
                    validation_type="directory_existence",
                    expected_value="exists",
                    actual_value="not_found"
                )
            elif create_if_missing:
                path.mkdir(parents=True, exist_ok=True)
        
        if path.exists() and not path.is_dir():
            raise ValidationError(
                f"Path is not a directory: {path}",
                validation_type="directory_type",
                expected_value="directory",
                actual_value="file" if path.is_file() else "other"
            )
        
        return path
        
    except OSError as e:
        raise ValidationError(
            f"Directory validation failed: {str(e)}",
            validation_type="directory_access"
        ) from e


def validate_transaction_data(transaction_dict: dict) -> dict:
    """
    Validate transaction data dictionary.
    
    Args:
        transaction_dict: Transaction data to validate
        
    Returns:
        Validated transaction dictionary
        
    Raises:
        ValidationError: If validation fails
    """
    required_fields = ["date", "description", "amount"]
    
    for field in required_fields:
        if field not in transaction_dict:
            raise ValidationError(
                f"Missing required field: {field}",
                validation_type="transaction_field",
                expected_value=f"field '{field}' present",
                actual_value="missing"
            )
    
    # Validate individual fields
    try:
        # Validate date
        if isinstance(transaction_dict["date"], str):
            datetime.strptime(transaction_dict["date"], "%Y-%m-%d")
        
        # Validate amount
        validate_amount(transaction_dict["amount"])
        
        # Validate description
        if not transaction_dict["description"] or not isinstance(transaction_dict["description"], str):
            raise ValidationError(
                "Description must be a non-empty string",
                validation_type="transaction_description"
            )
        
    except ValidationError:
        raise
    except Exception as e:
        raise ValidationError(
            f"Transaction data validation failed: {str(e)}",
            validation_type="transaction_data"
        ) from e
    
    return transaction_dict


def validate_ground_truth_data(ground_truth: dict, bill_name: str) -> dict:
    """
    Validate ground truth data.
    
    Args:
        ground_truth: Ground truth data dictionary
        bill_name: Bill name to validate against
        
    Returns:
        Validated ground truth entry
        
    Raises:
        ValidationError: If validation fails
    """
    if bill_name not in ground_truth:
        raise ValidationError(
            f"Bill '{bill_name}' not found in ground truth data",
            validation_type="ground_truth_bill",
            expected_value=f"bill '{bill_name}' present",
            actual_value="missing"
        )
    
    bill_data = ground_truth[bill_name]
    required_fields = ["expected_count", "expected_total"]
    
    for field in required_fields:
        if field not in bill_data:
            raise ValidationError(
                f"Missing required field '{field}' in ground truth for bill '{bill_name}'",
                validation_type="ground_truth_field",
                expected_value=f"field '{field}' present",
                actual_value="missing"
            )
    
    # Validate field types
    try:
        expected_count = int(bill_data["expected_count"])
        if expected_count < 0:
            raise ValidationError(
                f"Expected count must be non-negative: {expected_count}",
                validation_type="ground_truth_count"
            )
        
        validate_amount(bill_data["expected_total"])
        
    except (ValueError, TypeError) as e:
        raise ValidationError(
            f"Invalid ground truth data types: {str(e)}",
            validation_type="ground_truth_types"
        ) from e
    
    return bill_data
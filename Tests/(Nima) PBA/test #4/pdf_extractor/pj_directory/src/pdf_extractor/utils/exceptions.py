"""
Custom exceptions for PDF Credit Card Expense Extractor.
"""

from typing import Optional, Dict, Any, List


class PDFExtractorError(Exception):
    """Base exception for PDF Extractor errors."""
    
    def __init__(self, message: str, error_code: Optional[str] = None, 
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
    
    def __str__(self):
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for logging/serialization."""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "error_code": self.error_code,
            "details": self.details
        }


class PDFProcessingError(PDFExtractorError):
    """Exception raised during PDF processing."""
    
    def __init__(self, message: str, file_path: Optional[str] = None, 
                 page_number: Optional[int] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.file_path = file_path
        self.page_number = page_number
        
        if file_path:
            self.details["file_path"] = file_path
        if page_number is not None:
            self.details["page_number"] = page_number


class PatternMatchError(PDFExtractorError):
    """Exception raised when pattern matching fails."""
    
    def __init__(self, message: str, pattern_name: Optional[str] = None,
                 text_sample: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.pattern_name = pattern_name
        self.text_sample = text_sample
        
        if pattern_name:
            self.details["pattern_name"] = pattern_name
        if text_sample:
            # Truncate text sample for logging
            self.details["text_sample"] = text_sample[:200] + "..." if len(text_sample) > 200 else text_sample


class ValidationError(PDFExtractorError):
    """Exception raised during validation."""
    
    def __init__(self, message: str, validation_type: Optional[str] = None,
                 expected_value: Optional[Any] = None, actual_value: Optional[Any] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.validation_type = validation_type
        self.expected_value = expected_value
        self.actual_value = actual_value
        
        if validation_type:
            self.details["validation_type"] = validation_type
        if expected_value is not None:
            self.details["expected_value"] = str(expected_value)
        if actual_value is not None:
            self.details["actual_value"] = str(actual_value)


class ConfigurationError(PDFExtractorError):
    """Exception raised for configuration-related errors."""
    
    def __init__(self, message: str, config_key: Optional[str] = None,
                 config_file: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.config_key = config_key
        self.config_file = config_file
        
        if config_key:
            self.details["config_key"] = config_key
        if config_file:
            self.details["config_file"] = config_file


class FileAccessError(PDFExtractorError):
    """Exception raised for file access errors."""
    
    def __init__(self, message: str, file_path: Optional[str] = None,
                 operation: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.file_path = file_path
        self.operation = operation
        
        if file_path:
            self.details["file_path"] = file_path
        if operation:
            self.details["operation"] = operation


class TransactionParsingError(PDFExtractorError):
    """Exception raised when parsing individual transactions."""
    
    def __init__(self, message: str, raw_text: Optional[str] = None,
                 field_name: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.raw_text = raw_text
        self.field_name = field_name
        
        if raw_text:
            # Truncate for logging
            self.details["raw_text"] = raw_text[:100] + "..." if len(raw_text) > 100 else raw_text
        if field_name:
            self.details["field_name"] = field_name


class GroundTruthError(PDFExtractorError):
    """Exception raised for ground truth related errors."""
    
    def __init__(self, message: str, bill_name: Optional[str] = None,
                 ground_truth_file: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.bill_name = bill_name
        self.ground_truth_file = ground_truth_file
        
        if bill_name:
            self.details["bill_name"] = bill_name
        if ground_truth_file:
            self.details["ground_truth_file"] = ground_truth_file


class TimeoutError(PDFExtractorError):
    """Exception raised when operations timeout."""
    
    def __init__(self, message: str, timeout_seconds: Optional[float] = None,
                 operation: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.timeout_seconds = timeout_seconds
        self.operation = operation
        
        if timeout_seconds is not None:
            self.details["timeout_seconds"] = timeout_seconds
        if operation:
            self.details["operation"] = operation


class DependencyError(PDFExtractorError):
    """Exception raised for missing or incompatible dependencies."""
    
    def __init__(self, message: str, dependency_name: Optional[str] = None,
                 required_version: Optional[str] = None, current_version: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.dependency_name = dependency_name
        self.required_version = required_version
        self.current_version = current_version
        
        if dependency_name:
            self.details["dependency_name"] = dependency_name
        if required_version:
            self.details["required_version"] = required_version
        if current_version:
            self.details["current_version"] = current_version


class BatchProcessingError(PDFExtractorError):
    """Exception raised during batch processing operations."""
    
    def __init__(self, message: str, failed_files: Optional[List[str]] = None,
                 total_files: Optional[int] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.failed_files = failed_files or []
        self.total_files = total_files
        
        if self.failed_files:
            self.details["failed_files"] = self.failed_files
            self.details["failed_count"] = len(self.failed_files)
        if total_files is not None:
            self.details["total_files"] = total_files


# Exception hierarchy mapping for error categorization
EXCEPTION_CATEGORIES = {
    "processing": [PDFProcessingError, TransactionParsingError, TimeoutError],
    "pattern": [PatternMatchError],
    "validation": [ValidationError, GroundTruthError],
    "configuration": [ConfigurationError],
    "file_access": [FileAccessError],
    "dependency": [DependencyError],
    "batch": [BatchProcessingError],
    "general": [PDFExtractorError]
}


def get_exception_category(exception: Exception) -> str:
    """
    Get the category of an exception.
    
    Args:
        exception: Exception instance
        
    Returns:
        Category name
    """
    exception_type = type(exception)
    
    for category, exception_types in EXCEPTION_CATEGORIES.items():
        if exception_type in exception_types:
            return category
    
    return "unknown"


def create_error_summary(exceptions: List[Exception]) -> Dict[str, Any]:
    """
    Create a summary of multiple exceptions.
    
    Args:
        exceptions: List of exceptions
        
    Returns:
        Error summary dictionary
    """
    if not exceptions:
        return {"total_errors": 0, "categories": {}}
    
    categories = {}
    for exc in exceptions:
        category = get_exception_category(exc)
        if category not in categories:
            categories[category] = {
                "count": 0,
                "errors": []
            }
        
        categories[category]["count"] += 1
        categories[category]["errors"].append({
            "type": exc.__class__.__name__,
            "message": str(exc),
            "details": getattr(exc, 'details', {})
        })
    
    return {
        "total_errors": len(exceptions),
        "categories": categories,
        "most_common_category": max(categories.keys(), key=lambda k: categories[k]["count"]) if categories else None
    }
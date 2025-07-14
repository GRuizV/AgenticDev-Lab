"""
Error handling utilities for PDF Credit Card Expense Extractor.
"""

import sys
import traceback
import functools
from typing import Any, Callable, Optional, Dict, List, Union
from pathlib import Path

from ..config.logging_config import get_logger, log_performance_metric
from .exceptions import (
    PDFExtractorError, PDFProcessingError, PatternMatchError, 
    ValidationError, ConfigurationError, FileAccessError,
    create_error_summary, get_exception_category
)


class ErrorHandler:
    """Centralized error handling and logging."""
    
    def __init__(self, logger_name: str = "pdf_extractor.errors"):
        self.logger = get_logger(logger_name)
        self.error_counts = {}
        self.recent_errors = []
        self.max_recent_errors = 50
    
    def handle_error(self, error: Exception, context: Optional[Dict[str, Any]] = None,
                    reraise: bool = True, log_level: str = "error") -> Optional[Dict[str, Any]]:
        """
        Handle an error with logging and optional context.
        
        Args:
            error: Exception to handle
            context: Additional context information
            reraise: Whether to reraise the exception
            log_level: Logging level (debug, info, warning, error, critical)
            
        Returns:
            Error information dictionary if not reraising
        """
        context = context or {}
        
        # Create error info
        error_info = {
            "type": error.__class__.__name__,
            "message": str(error),
            "category": get_exception_category(error),
            "context": context
        }
        
        # Add details if it's a PDFExtractorError
        if isinstance(error, PDFExtractorError):
            error_info.update({
                "error_code": error.error_code,
                "details": error.details
            })
        
        # Add traceback for debugging
        if log_level.lower() == "debug":
            error_info["traceback"] = traceback.format_exc()
        
        # Log the error
        log_method = getattr(self.logger, log_level.lower(), self.logger.error)
        log_message = f"{error_info['type']}: {error_info['message']}"
        
        if context:
            context_str = ", ".join(f"{k}={v}" for k, v in context.items())
            log_message += f" | Context: {context_str}"
        
        log_method(log_message)
        
        # Track error statistics
        self._track_error(error_info)
        
        if reraise:
            raise error
        
        return error_info
    
    def _track_error(self, error_info: Dict[str, Any]):
        """Track error for statistics."""
        error_type = error_info["type"]
        category = error_info["category"]
        
        # Update counts
        if error_type not in self.error_counts:
            self.error_counts[error_type] = 0
        self.error_counts[error_type] += 1
        
        # Add to recent errors
        self.recent_errors.append(error_info)
        if len(self.recent_errors) > self.max_recent_errors:
            self.recent_errors.pop(0)
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error statistics."""
        return {
            "total_errors": sum(self.error_counts.values()),
            "error_counts": self.error_counts.copy(),
            "recent_errors_count": len(self.recent_errors),
            "most_common_error": max(self.error_counts.keys(), 
                                   key=lambda k: self.error_counts[k]) if self.error_counts else None
        }
    
    def clear_statistics(self):
        """Clear error statistics."""
        self.error_counts.clear()
        self.recent_errors.clear()
    
    def create_error_report(self) -> str:
        """Create a formatted error report."""
        stats = self.get_error_statistics()
        
        if stats["total_errors"] == 0:
            return "No errors recorded."
        
        lines = [
            "ERROR REPORT",
            "=" * 40,
            f"Total Errors: {stats['total_errors']}",
            f"Most Common: {stats['most_common_error']}",
            "",
            "Error Breakdown:"
        ]
        
        for error_type, count in sorted(stats["error_counts"].items(), 
                                      key=lambda x: x[1], reverse=True):
            lines.append(f"  {error_type}: {count}")
        
        if self.recent_errors:
            lines.extend([
                "",
                f"Recent Errors (last {len(self.recent_errors)}):"
            ])
            
            for i, error in enumerate(self.recent_errors[-10:], 1):  # Last 10
                lines.append(f"  {i}. {error['type']}: {error['message']}")
        
        return "\n".join(lines)


# Global error handler instance
_error_handler = ErrorHandler()


def handle_errors(reraise: bool = True, log_level: str = "error", 
                 context: Optional[Dict[str, Any]] = None):
    """
    Decorator for automatic error handling.
    
    Args:
        reraise: Whether to reraise exceptions
        log_level: Logging level for errors
        context: Additional context to include
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                func_context = {
                    "function": func.__name__,
                    "module": func.__module__,
                    "args_count": len(args),
                    "kwargs_keys": list(kwargs.keys())
                }
                
                if context:
                    func_context.update(context)
                
                return _error_handler.handle_error(
                    e, context=func_context, reraise=reraise, log_level=log_level
                )
        
        return wrapper
    return decorator


def safe_execute(func: Callable, *args, default_return: Any = None, 
                log_errors: bool = True, **kwargs) -> Any:
    """
    Safely execute a function with error handling.
    
    Args:
        func: Function to execute
        *args: Function arguments
        default_return: Value to return on error
        log_errors: Whether to log errors
        **kwargs: Function keyword arguments
        
    Returns:
        Function result or default_return on error
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        if log_errors:
            _error_handler.handle_error(
                e, 
                context={"function": func.__name__},
                reraise=False
            )
        return default_return


def validate_file_access(file_path: Union[str, Path], operation: str = "read") -> Path:
    """
    Validate file access and raise appropriate errors.
    
    Args:
        file_path: Path to file
        operation: Type of operation (read, write)
        
    Returns:
        Validated Path object
        
    Raises:
        FileAccessError: If file access validation fails
    """
    try:
        path = Path(file_path)
        
        if operation == "read":
            if not path.exists():
                raise FileAccessError(
                    f"File does not exist: {path}",
                    file_path=str(path),
                    operation=operation,
                    error_code="FILE_NOT_FOUND"
                )
            
            if not path.is_file():
                raise FileAccessError(
                    f"Path is not a file: {path}",
                    file_path=str(path),
                    operation=operation,
                    error_code="NOT_A_FILE"
                )
            
            if not path.stat().st_size > 0:
                raise FileAccessError(
                    f"File is empty: {path}",
                    file_path=str(path),
                    operation=operation,
                    error_code="EMPTY_FILE"
                )
        
        elif operation == "write":
            # Check if parent directory exists or can be created
            if not path.parent.exists():
                try:
                    path.parent.mkdir(parents=True, exist_ok=True)
                except OSError as e:
                    raise FileAccessError(
                        f"Cannot create directory: {path.parent}",
                        file_path=str(path),
                        operation=operation,
                        error_code="DIRECTORY_CREATE_FAILED"
                    ) from e
        
        return path
        
    except FileAccessError:
        raise
    except Exception as e:
        raise FileAccessError(
            f"File access validation failed: {str(e)}",
            file_path=str(file_path),
            operation=operation,
            error_code="VALIDATION_FAILED"
        ) from e


def create_recovery_suggestions(error: Exception) -> List[str]:
    """
    Create recovery suggestions based on error type.
    
    Args:
        error: Exception to analyze
        
    Returns:
        List of recovery suggestions
    """
    suggestions = []
    
    if isinstance(error, FileAccessError):
        suggestions.extend([
            "Check if the file path is correct",
            "Verify file permissions",
            "Ensure the file is not locked by another process"
        ])
    
    elif isinstance(error, PDFProcessingError):
        suggestions.extend([
            "Verify the PDF file is not corrupted",
            "Try with a different PDF reader/library",
            "Check if the PDF is password protected",
            "Ensure sufficient memory is available"
        ])
    
    elif isinstance(error, PatternMatchError):
        suggestions.extend([
            "Try a different pattern or use auto-detection",
            "Check if the PDF format matches expected patterns",
            "Verify the credit card issuer is supported",
            "Consider creating a custom pattern"
        ])
    
    elif isinstance(error, ValidationError):
        suggestions.extend([
            "Check the ground truth data format",
            "Verify the bill name matches ground truth entries",
            "Review validation tolerance settings",
            "Ensure date and amount formats are consistent"
        ])
    
    elif isinstance(error, ConfigurationError):
        suggestions.extend([
            "Check the configuration file syntax",
            "Verify all required configuration keys are present",
            "Reset to default configuration if needed",
            "Check environment variable values"
        ])
    
    else:
        suggestions.extend([
            "Check the application logs for more details",
            "Verify system requirements are met",
            "Try restarting the application",
            "Contact support if the issue persists"
        ])
    
    return suggestions


def log_system_diagnostics():
    """Log system diagnostic information."""
    logger = get_logger("pdf_extractor.diagnostics")
    
    try:
        import platform
        import psutil
        import sys
        from pathlib import Path
        
        logger.info("System Diagnostics:")
        logger.info(f"  Platform: {platform.platform()}")
        logger.info(f"  Python: {sys.version}")
        logger.info(f"  Memory: {psutil.virtual_memory().percent}% used")
        logger.info(f"  Disk: {psutil.disk_usage('/').percent}% used")
        logger.info(f"  Working Directory: {Path.cwd()}")
        
    except ImportError:
        logger.warning("psutil not available for system diagnostics")
    except Exception as e:
        logger.error(f"Error collecting system diagnostics: {e}")


# Initialize error handler
def get_error_handler() -> ErrorHandler:
    """Get the global error handler instance."""
    return _error_handler
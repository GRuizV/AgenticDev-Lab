"""
Logging configuration for PDF Credit Card Expense Extractor.
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional, Dict, Any

from .settings import LoggingSettings, get_settings


class ColoredFormatter(logging.Formatter):
    """Colored formatter for console output."""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record):
        # Add color to levelname
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.COLORS['RESET']}"
        
        return super().format(record)


def setup_logging(settings: Optional[LoggingSettings] = None, 
                 logger_name: str = "pdf_extractor") -> logging.Logger:
    """
    Setup logging configuration.
    
    Args:
        settings: Logging settings (optional, will load from config if not provided)
        logger_name: Name of the logger
        
    Returns:
        Configured logger
    """
    if settings is None:
        app_settings = get_settings()
        settings = app_settings.logging
    
    # Get or create logger
    logger = logging.getLogger(logger_name)
    
    # Clear existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Set logging level
    level = getattr(logging, settings.level.upper(), logging.INFO)
    logger.setLevel(level)
    
    # Create formatter
    formatter = logging.Formatter(settings.format)
    colored_formatter = ColoredFormatter(settings.format)
    
    # Console handler
    if settings.console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(colored_formatter)
        logger.addHandler(console_handler)
    
    # File handler
    if settings.file_path:
        file_path = Path(settings.file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Use rotating file handler to manage file size
        file_handler = logging.handlers.RotatingFileHandler(
            filename=file_path,
            maxBytes=settings.max_file_size,
            backupCount=settings.backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    return logger


def get_logger(name: str = "pdf_extractor") -> logging.Logger:
    """
    Get a logger instance.
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)
    
    # If logger has no handlers, set it up
    if not logger.handlers:
        setup_logging(logger_name=name)
    
    return logger


def configure_module_loggers():
    """Configure loggers for different modules."""
    # Main application logger
    setup_logging(logger_name="pdf_extractor")
    
    # Module-specific loggers
    modules = [
        "pdf_extractor.core",
        "pdf_extractor.extraction", 
        "pdf_extractor.patterns",
        "pdf_extractor.data",
        "pdf_extractor.cli"
    ]
    
    for module in modules:
        logger = logging.getLogger(module)
        logger.setLevel(logging.INFO)
        # These will inherit handlers from parent logger


def log_system_info():
    """Log system and application information."""
    logger = get_logger()
    
    import platform
    import sys
    from .. import __version__
    
    logger.info("=" * 50)
    logger.info("PDF Credit Card Expense Extractor Starting")
    logger.info("=" * 50)
    logger.info(f"Application Version: {__version__}")
    logger.info(f"Python Version: {sys.version}")
    logger.info(f"Platform: {platform.platform()}")
    logger.info(f"Working Directory: {Path.cwd()}")
    logger.info("=" * 50)


def log_configuration(settings: Optional[Dict[str, Any]] = None):
    """
    Log current configuration settings.
    
    Args:
        settings: Settings dictionary to log
    """
    logger = get_logger()
    
    if settings is None:
        app_settings = get_settings()
        settings = app_settings.to_dict()
    
    logger.info("Current Configuration:")
    logger.info("-" * 30)
    
    # Log key settings (avoid logging sensitive information)
    safe_keys = [
        'extraction', 'validation', 'patterns', 'output',
        'app_name', 'version', 'config_version'
    ]
    
    for key in safe_keys:
        if key in settings:
            value = settings[key]
            if isinstance(value, dict):
                logger.info(f"{key}:")
                for sub_key, sub_value in value.items():
                    logger.info(f"  {sub_key}: {sub_value}")
            else:
                logger.info(f"{key}: {value}")
    
    logger.info("-" * 30)


class LoggerMixin:
    """Mixin class to add logging capabilities to other classes."""
    
    @property
    def logger(self) -> logging.Logger:
        """Get logger for this class."""
        class_name = self.__class__.__name__
        module_name = self.__class__.__module__
        logger_name = f"{module_name}.{class_name}"
        return get_logger(logger_name)
    
    def log_debug(self, message: str, *args, **kwargs):
        """Log debug message."""
        self.logger.debug(message, *args, **kwargs)
    
    def log_info(self, message: str, *args, **kwargs):
        """Log info message."""
        self.logger.info(message, *args, **kwargs)
    
    def log_warning(self, message: str, *args, **kwargs):
        """Log warning message."""
        self.logger.warning(message, *args, **kwargs)
    
    def log_error(self, message: str, *args, **kwargs):
        """Log error message."""
        self.logger.error(message, *args, **kwargs)
    
    def log_critical(self, message: str, *args, **kwargs):
        """Log critical message."""
        self.logger.critical(message, *args, **kwargs)
    
    def log_exception(self, message: str, *args, **kwargs):
        """Log exception with traceback."""
        self.logger.exception(message, *args, **kwargs)


def create_performance_logger() -> logging.Logger:
    """Create a dedicated logger for performance metrics."""
    logger = logging.getLogger("pdf_extractor.performance")
    
    if not logger.handlers:
        # Create performance log file
        perf_file = Path("logs/performance.log")
        perf_file.parent.mkdir(parents=True, exist_ok=True)
        
        handler = logging.handlers.RotatingFileHandler(
            filename=perf_file,
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=3
        )
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False
    
    return logger


def log_performance_metric(operation: str, duration: float, 
                         details: Optional[Dict[str, Any]] = None):
    """
    Log performance metrics.
    
    Args:
        operation: Name of the operation
        duration: Duration in seconds
        details: Additional details to log
    """
    perf_logger = create_performance_logger()
    
    message = f"Operation: {operation}, Duration: {duration:.3f}s"
    if details:
        detail_str = ", ".join(f"{k}={v}" for k, v in details.items())
        message += f", Details: {detail_str}"
    
    perf_logger.info(message)


# Initialize logging when module is imported
def _initialize_logging():
    """Initialize logging configuration on module import."""
    try:
        configure_module_loggers()
    except Exception:
        # Fallback to basic logging if configuration fails
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )


# Initialize on import
_initialize_logging()
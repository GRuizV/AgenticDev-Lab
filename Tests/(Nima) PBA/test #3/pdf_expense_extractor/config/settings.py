"""
Application settings and configuration.
"""

from dataclasses import dataclass
from typing import List


@dataclass
class Settings:
    """Application configuration settings."""
    
    # Validation settings
    amount_tolerance: float = 1.0  # ±$1 tolerance for amount validation
    
    # PDF processing settings
    pdf_libraries: List[str] = None
    max_retries: int = 3
    
    # Output settings
    table_width: int = 80
    show_progress: bool = True
    verbose: bool = False
    
    # File processing settings
    pdf_directory: str = "../Test PDFs/base_6"
    output_format: str = "table"  # table, json, csv
    
    def __post_init__(self):
        """Initialize default values after creation."""
        if self.pdf_libraries is None:
            self.pdf_libraries = ['pdfplumber', 'pymupdf', 'PyPDF2']
    
    @classmethod
    def default(cls) -> 'Settings':
        """Create default settings instance."""
        return cls()
    
    @classmethod
    def verbose(cls) -> 'Settings':
        """Create settings with verbose output enabled."""
        return cls(verbose=True, show_progress=True)
    
    def to_dict(self) -> dict:
        """Convert settings to dictionary."""
        return {
            'amount_tolerance': self.amount_tolerance,
            'pdf_libraries': self.pdf_libraries,
            'max_retries': self.max_retries,
            'table_width': self.table_width,
            'show_progress': self.show_progress,
            'verbose': self.verbose,
            'pdf_directory': self.pdf_directory,
            'output_format': self.output_format
        }


# Default application settings
DEFAULT_SETTINGS = Settings.default()
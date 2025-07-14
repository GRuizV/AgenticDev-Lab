"""
Application settings and configuration management.
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass, field, asdict


@dataclass
class ExtractionSettings:
    """Settings for PDF extraction."""
    default_pattern: Optional[str] = None
    confidence_threshold: float = 0.7
    max_pages: Optional[int] = None
    timeout_seconds: int = 300
    preserve_layout: bool = True
    extract_tables: bool = True


@dataclass
class ValidationSettings:
    """Settings for validation."""
    tolerance_percentage: float = 0.05  # 5% tolerance for amount matching
    require_exact_count: bool = True
    min_accuracy_threshold: float = 0.8
    validate_dates: bool = True
    validate_amounts: bool = True


@dataclass
class PatternSettings:
    """Settings for pattern recognition."""
    cache_patterns: bool = True
    auto_learn: bool = False
    pattern_confidence_threshold: float = 0.6
    max_pattern_cache_size: int = 100


@dataclass
class OutputSettings:
    """Settings for output formatting."""
    default_format: str = "table"
    date_format: str = "%Y-%m-%d"
    currency_symbol: str = "$"
    decimal_places: int = 2
    max_description_length: int = 50


@dataclass
class LoggingSettings:
    """Settings for logging."""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: Optional[str] = None
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    console_output: bool = True


@dataclass
class Settings:
    """Main application settings."""
    extraction: ExtractionSettings = field(default_factory=ExtractionSettings)
    validation: ValidationSettings = field(default_factory=ValidationSettings)
    patterns: PatternSettings = field(default_factory=PatternSettings)
    output: OutputSettings = field(default_factory=OutputSettings)
    logging: LoggingSettings = field(default_factory=LoggingSettings)
    
    # Application metadata
    app_name: str = "PDF Credit Card Expense Extractor"
    version: str = "1.0.0"
    config_version: str = "1.0"
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Settings':
        """Create Settings from dictionary."""
        # Extract nested settings
        extraction_data = data.get('extraction', {})
        validation_data = data.get('validation', {})
        patterns_data = data.get('patterns', {})
        output_data = data.get('output', {})
        logging_data = data.get('logging', {})
        
        return cls(
            extraction=ExtractionSettings(**extraction_data),
            validation=ValidationSettings(**validation_data),
            patterns=PatternSettings(**patterns_data),
            output=OutputSettings(**output_data),
            logging=LoggingSettings(**logging_data),
            app_name=data.get('app_name', "PDF Credit Card Expense Extractor"),
            version=data.get('version', "1.0.0"),
            config_version=data.get('config_version', "1.0")
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Settings to dictionary."""
        return asdict(self)
    
    def save_to_file(self, file_path: Union[str, Path], format_type: str = "yaml"):
        """
        Save settings to file.
        
        Args:
            file_path: Path to save the configuration file
            format_type: Format to save in ("yaml" or "json")
        """
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        data = self.to_dict()
        
        if format_type.lower() == "yaml":
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, indent=2)
        elif format_type.lower() == "json":
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        else:
            raise ValueError(f"Unsupported format: {format_type}")
    
    @classmethod
    def load_from_file(cls, file_path: Union[str, Path]) -> 'Settings':
        """
        Load settings from file.
        
        Args:
            file_path: Path to configuration file
            
        Returns:
            Settings object
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            if file_path.suffix.lower() in ['.yaml', '.yml']:
                data = yaml.safe_load(f)
            elif file_path.suffix.lower() == '.json':
                data = json.load(f)
            else:
                raise ValueError(f"Unsupported file format: {file_path.suffix}")
        
        return cls.from_dict(data or {})
    
    def update_from_env(self):
        """Update settings from environment variables."""
        # Extraction settings
        if os.getenv('PDF_EXTRACTOR_DEFAULT_PATTERN'):
            self.extraction.default_pattern = os.getenv('PDF_EXTRACTOR_DEFAULT_PATTERN')
        
        if os.getenv('PDF_EXTRACTOR_CONFIDENCE_THRESHOLD'):
            self.extraction.confidence_threshold = float(os.getenv('PDF_EXTRACTOR_CONFIDENCE_THRESHOLD'))
        
        if os.getenv('PDF_EXTRACTOR_TIMEOUT'):
            self.extraction.timeout_seconds = int(os.getenv('PDF_EXTRACTOR_TIMEOUT'))
        
        # Validation settings
        if os.getenv('PDF_EXTRACTOR_TOLERANCE'):
            self.validation.tolerance_percentage = float(os.getenv('PDF_EXTRACTOR_TOLERANCE'))
        
        if os.getenv('PDF_EXTRACTOR_MIN_ACCURACY'):
            self.validation.min_accuracy_threshold = float(os.getenv('PDF_EXTRACTOR_MIN_ACCURACY'))
        
        # Logging settings
        if os.getenv('PDF_EXTRACTOR_LOG_LEVEL'):
            self.logging.level = os.getenv('PDF_EXTRACTOR_LOG_LEVEL')
        
        if os.getenv('PDF_EXTRACTOR_LOG_FILE'):
            self.logging.file_path = os.getenv('PDF_EXTRACTOR_LOG_FILE')
        
        # Output settings
        if os.getenv('PDF_EXTRACTOR_DEFAULT_FORMAT'):
            self.output.default_format = os.getenv('PDF_EXTRACTOR_DEFAULT_FORMAT')


class SettingsManager:
    """Manages application settings with caching and file watching."""
    
    def __init__(self):
        self._settings: Optional[Settings] = None
        self._config_file: Optional[Path] = None
    
    def load_settings(self, config_file: Optional[Union[str, Path]] = None) -> Settings:
        """
        Load settings from file or create defaults.
        
        Args:
            config_file: Path to configuration file (optional)
            
        Returns:
            Settings object
        """
        if config_file:
            self._config_file = Path(config_file)
            if self._config_file.exists():
                self._settings = Settings.load_from_file(self._config_file)
            else:
                # Create default settings and save
                self._settings = Settings()
                self._settings.save_to_file(self._config_file)
        else:
            # Look for default config files
            possible_configs = [
                Path.cwd() / "config.yaml",
                Path.cwd() / "config.yml",
                Path.cwd() / "config.json",
                Path.home() / ".pdf_extractor" / "config.yaml",
                Path(__file__).parent.parent.parent / "config.yaml"
            ]
            
            for config_path in possible_configs:
                if config_path.exists():
                    self._config_file = config_path
                    self._settings = Settings.load_from_file(config_path)
                    break
            else:
                # No config file found, use defaults
                self._settings = Settings()
        
        # Update from environment variables
        self._settings.update_from_env()
        
        return self._settings
    
    def get_settings(self) -> Settings:
        """Get current settings, loading defaults if not already loaded."""
        if self._settings is None:
            return self.load_settings()
        return self._settings
    
    def reload_settings(self) -> Settings:
        """Reload settings from file."""
        if self._config_file and self._config_file.exists():
            self._settings = Settings.load_from_file(self._config_file)
            self._settings.update_from_env()
        return self._settings
    
    def save_settings(self, settings: Optional[Settings] = None):
        """Save current settings to file."""
        if settings:
            self._settings = settings
        
        if self._settings and self._config_file:
            self._settings.save_to_file(self._config_file)


# Global settings manager instance
_settings_manager = SettingsManager()


def get_settings(config_file: Optional[Union[str, Path]] = None) -> Settings:
    """
    Get application settings.
    
    Args:
        config_file: Optional path to configuration file
        
    Returns:
        Settings object
    """
    if config_file:
        return _settings_manager.load_settings(config_file)
    return _settings_manager.get_settings()


def reload_settings() -> Settings:
    """Reload settings from file."""
    return _settings_manager.reload_settings()


def save_settings(settings: Settings):
    """Save settings to file."""
    _settings_manager.save_settings(settings)
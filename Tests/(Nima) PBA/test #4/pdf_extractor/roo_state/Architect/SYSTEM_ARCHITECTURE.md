# PDF Credit Card Expense Extractor - System Architecture

## 1. Executive Summary

This document defines the complete system architecture for a Python CLI application that extracts credit card transaction data from PDF files using pdfplumber. The system is designed for modularity, extensibility, and robust pattern recognition with validation against ground truth data.

## 2. System Overview

### 2.1 Core Purpose
Extract transaction data (Date, Description, Amount) from credit card PDF statements and validate against known ground truth data.

### 2.2 Key Requirements
- Process 6 text-based PDFs from one known card issuer
- Extract exactly: Date, Description, Amount (in COP)
- Support single file and batch folder processing
- Validate against ground_truth.json with exact transaction counts and totals
- Learn new PDF patterns from different card issuers
- CLI interface for user interaction
- Use pdfplumber library for PDF text extraction

### 2.3 Expected Validation Targets
- AV - MC - 02 - FEB-2025: $434,980.00, 5 transactions
- AV - MC - 03 - MAR-2025: $44,900.00, 2 transactions  
- AV - MC - 04 - ABR-2025: $1,068,097.00, 9 transactions
- AV - VS - 02 - FEB-2025: $1,702,961.00, 18 transactions
- AV - VS - 03 - MAR-2025: $810,460.00, 14 transactions
- AV - VS - 04 - ABR-2025: $1,058,980.00, 20 transactions

## 3. System Architecture

### 3.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLI Interface Layer                      │
├─────────────────────────────────────────────────────────────────┤
│                     Application Core Layer                      │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │   PDF Parser    │  │ Pattern Engine  │  │   Validator     │  │
│  │     Module      │  │     Module      │  │     Module      │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│                      Data Processing Layer                      │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │ PDFPlumber      │  │ Pattern Matcher │  │ Data Formatter  │  │
│  │   Extractor     │  │     Engine      │  │     Engine      │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│                        Foundation Layer                         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │ Configuration   │  │ Logging System  │  │ Error Handler   │  │
│  │    Manager      │  │                 │  │                 │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Core Components

#### 3.2.1 CLI Interface Layer
- **Command Parser**: Handles command-line arguments and options
- **User Interface**: Provides interactive feedback and progress reporting
- **Output Formatter**: Formats results for console display

#### 3.2.2 Application Core Layer
- **PDF Parser Module**: Orchestrates PDF text extraction and processing
- **Pattern Engine Module**: Manages pattern recognition and learning
- **Validator Module**: Validates extracted data against ground truth

#### 3.2.3 Data Processing Layer
- **PDFPlumber Extractor**: Extracts raw text from PDF files using pdfplumber
- **Pattern Matcher Engine**: Applies patterns to identify transactions
- **Data Formatter Engine**: Normalizes and formats extracted data

#### 3.2.4 Foundation Layer
- **Configuration Manager**: Manages settings and patterns
- **Logging System**: Comprehensive logging and debugging
- **Error Handler**: Centralized error management

## 4. Detailed Component Design

### 4.1 PDF Parser Module

```python
class PDFParser:
    """Main orchestrator for PDF processing"""
    
    def __init__(self, config_manager, pattern_engine, validator):
        self.config = config_manager
        self.pattern_engine = pattern_engine
        self.validator = validator
        self.text_extractor = PDFPlumberExtractor()
        
    def process_file(self, pdf_path: str) -> ProcessingResult:
        """Process a single PDF file"""
        
    def process_batch(self, folder_path: str) -> BatchResult:
        """Process all PDFs in a folder"""
```

**Responsibilities:**
- Coordinate PDF processing workflow
- Manage single file and batch processing
- Integrate with pattern engine and validator
- Handle processing errors and retries

### 4.2 Pattern Engine Module

```python
class PatternEngine:
    """Manages transaction pattern recognition and learning"""
    
    def __init__(self, pattern_repository):
        self.patterns = pattern_repository
        self.matcher = PatternMatcher()
        
    def detect_pattern(self, text: str) -> PatternType:
        """Detect which pattern applies to the text"""
        
    def extract_transactions(self, text: str, pattern: PatternType) -> List[Transaction]:
        """Extract transactions using detected pattern"""
        
    def learn_new_pattern(self, text: str, expected_transactions: List[Transaction]) -> Pattern:
        """Learn a new pattern from user-provided examples"""
```

**Responsibilities:**
- Detect PDF format patterns automatically
- Extract transactions using appropriate patterns
- Learn new patterns from user examples
- Manage pattern repository and versioning

### 4.3 PDFPlumber Extractor

```python
class PDFPlumberExtractor:
    """Handles PDF text extraction using pdfplumber library"""
    
    def __init__(self):
        self.extraction_settings = {
            'x_tolerance': 3,
            'y_tolerance': 3,
            'layout': True,
            'strip_text': True
        }
        
    def extract_text(self, pdf_path: str) -> str:
        """Extract text using pdfplumber"""
        
    def extract_with_layout(self, pdf_path: str) -> List[Dict]:
        """Extract text preserving layout information"""
        
    def extract_tables(self, pdf_path: str) -> List[List[List[str]]]:
        """Extract table data if transactions are in table format"""
```

**Responsibilities:**
- Extract raw text from PDF files using pdfplumber
- Preserve text structure and formatting
- Handle table extraction for structured data
- Optimize extraction settings for credit card PDFs

### 4.4 Pattern Matcher Engine

```python
class PatternMatcher:
    """Core pattern matching and transaction extraction"""
    
    def __init__(self):
        self.date_parser = DateParser()
        self.amount_parser = AmountParser()
        self.description_cleaner = DescriptionCleaner()
        
    def match_transactions(self, text: str, pattern: Pattern) -> List[Transaction]:
        """Match transactions using regex patterns"""
        
    def validate_transaction(self, transaction: Transaction) -> bool:
        """Validate individual transaction data"""
```

**Responsibilities:**
- Apply regex patterns to extract transaction data
- Parse and normalize dates, amounts, descriptions
- Validate individual transaction completeness
- Handle edge cases and malformed data

### 4.5 Validator Module

```python
class Validator:
    """Validates extracted data against ground truth"""
    
    def __init__(self, ground_truth_path: str):
        self.ground_truth = self.load_ground_truth(ground_truth_path)
        
    def validate_extraction(self, bill_name: str, transactions: List[Transaction]) -> ValidationResult:
        """Validate extracted transactions against ground truth"""
        
    def generate_validation_report(self, results: List[ValidationResult]) -> ValidationReport:
        """Generate comprehensive validation report"""
```

**Responsibilities:**
- Load and manage ground truth data
- Compare extracted vs expected transactions
- Calculate accuracy metrics
- Generate detailed validation reports

## 5. Data Flow Architecture

### 5.1 Processing Pipeline

```
PDF File(s) → PDFPlumber Extraction → Pattern Detection → Transaction Extraction → Validation → Output
     ↓              ↓                      ↓                    ↓               ↓         ↓
   Input         Raw Text              Pattern Type        Transaction List   Results   Report
```

### 5.2 Detailed Data Flow

1. **Input Stage**
   - CLI receives file path or folder path
   - Validates input paths and file types
   - Prepares processing queue

2. **Extraction Stage**
   - PDFPlumber extractor processes PDF
   - Extracts text with layout preservation
   - Raw text stored with metadata

3. **Pattern Detection Stage**
   - Pattern engine analyzes text structure
   - Identifies card issuer and format type
   - Selects appropriate extraction pattern

4. **Transaction Extraction Stage**
   - Pattern matcher applies regex patterns
   - Extracts date, description, amount fields
   - Creates Transaction objects

5. **Validation Stage**
   - Validator compares against ground truth
   - Calculates accuracy metrics
   - Identifies discrepancies

6. **Output Stage**
   - Formatter creates CLI table output
   - Generates validation report
   - Logs processing results

## 6. Pattern Recognition System

### 6.1 Pattern Types

```python
@dataclass
class Pattern:
    name: str
    issuer: str
    card_type: str
    transaction_regex: str
    date_format: str
    amount_format: str
    description_cleanup_rules: List[str]
```

### 6.2 Known Patterns

#### 6.2.1 AV (Avianca) Pattern
```python
AV_PATTERN = Pattern(
    name="avianca_standard",
    issuer="avianca",
    card_type="both",
    transaction_regex=r"(\d{4})\s+(\d{2})\s+(\d{2})\s+(\d{2})\s+(.+?)\s+[\d,]+\.\d{2}\s+\$?([\d,]+\.\d{2})",
    date_format="%d %m %y",
    amount_format="$X,XXX.XX",
    description_cleanup_rules=["remove_trailing_numbers", "clean_location_codes"]
)
```

### 6.3 Pattern Learning System

```python
class PatternLearner:
    """Learns new patterns from user examples"""
    
    def analyze_text_structure(self, text: str) -> TextStructure:
        """Analyze text to identify potential patterns"""
        
    def generate_pattern_candidates(self, examples: List[TransactionExample]) -> List[Pattern]:
        """Generate pattern candidates from examples"""
        
    def validate_pattern(self, pattern: Pattern, test_text: str) -> PatternValidation:
        """Validate pattern against test data"""
```

## 7. CLI Interface Design

### 7.1 Command Structure

```bash
# Single file processing
pdf-extractor process-file <pdf_path> [--output-format table|json|csv]

# Batch processing
pdf-extractor process-batch <folder_path> [--output-format table|json|csv]

# Validation mode
pdf-extractor validate <pdf_path> --ground-truth <json_path>

# Pattern learning
pdf-extractor learn-pattern <pdf_path> --examples <examples_file>

# List available patterns
pdf-extractor list-patterns

# Configuration
pdf-extractor config --set <key>=<value>
pdf-extractor config --get <key>
```

### 7.2 CLI Interface Implementation

```python
class CLIInterface:
    """Main CLI interface controller"""
    
    def __init__(self):
        self.parser = self.create_argument_parser()
        self.processor = PDFProcessor()
        
    def create_argument_parser(self) -> argparse.ArgumentParser:
        """Create command line argument parser"""
        
    def handle_process_file(self, args) -> None:
        """Handle single file processing command"""
        
    def handle_process_batch(self, args) -> None:
        """Handle batch processing command"""
        
    def handle_validate(self, args) -> None:
        """Handle validation command"""
        
    def handle_learn_pattern(self, args) -> None:
        """Handle pattern learning command"""
```

## 8. Configuration Management

### 8.1 Configuration Structure

```yaml
# config.yaml
pdf_extractor:
  extraction:
    pdfplumber_settings:
      x_tolerance: 3
      y_tolerance: 3
      layout: true
      strip_text: true
    timeout_seconds: 30
    
  patterns:
    auto_detect: true
    default_pattern: "avianca_standard"
    pattern_confidence_threshold: 0.8
    
  validation:
    strict_mode: true
    tolerance_percentage: 0.01
    
  output:
    default_format: "table"
    decimal_places: 2
    currency_symbol: "$"
    
  logging:
    level: "INFO"
    file_path: "logs/pdf_extractor.log"
    max_file_size: "10MB"
    backup_count: 5
```

### 8.2 Configuration Manager

```python
class ConfigurationManager:
    """Manages application configuration"""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        self.config = self.load_config()
        
    def load_config(self) -> Dict:
        """Load configuration from file"""
        
    def get(self, key: str, default=None):
        """Get configuration value"""
        
    def set(self, key: str, value):
        """Set configuration value"""
        
    def save_config(self):
        """Save configuration to file"""
```

## 9. Error Handling Strategy

### 9.1 Error Categories

1. **Input Errors**
   - File not found
   - Invalid file format
   - Corrupted PDF files

2. **Processing Errors**
   - PDFPlumber extraction failures
   - Pattern matching failures
   - Data parsing errors

3. **Validation Errors**
   - Ground truth file issues
   - Validation mismatches
   - Missing expected data

4. **System Errors**
   - Memory limitations
   - Disk space issues
   - Permission errors

### 9.2 Error Handler Implementation

```python
class ErrorHandler:
    """Centralized error handling and recovery"""
    
    def __init__(self, logger):
        self.logger = logger
        self.error_strategies = self.setup_error_strategies()
        
    def handle_error(self, error: Exception, context: Dict) -> ErrorResponse:
        """Handle error with appropriate strategy"""
        
    def setup_error_strategies(self) -> Dict:
        """Setup error handling strategies"""
        
    def log_error(self, error: Exception, context: Dict):
        """Log error with context information"""
```

## 10. Data Models

### 10.1 Core Data Models

```python
@dataclass
class Transaction:
    date: datetime.date
    description: str
    amount: Decimal
    raw_text: str = ""
    confidence: float = 1.0
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        
    def validate(self) -> bool:
        """Validate transaction data"""

@dataclass
class ProcessingResult:
    file_path: str
    transactions: List[Transaction]
    pattern_used: str
    processing_time: float
    errors: List[str]
    warnings: List[str]
    
@dataclass
class ValidationResult:
    bill_name: str
    expected_total: Decimal
    actual_total: Decimal
    expected_count: int
    actual_count: int
    accuracy: float
    missing_transactions: List[Transaction]
    extra_transactions: List[Transaction]
    
@dataclass
class BatchResult:
    results: List[ProcessingResult]
    total_files: int
    successful_files: int
    failed_files: int
    total_transactions: int
    processing_time: float
```

## 11. Module Structure

### 11.1 Project Directory Structure

**Base Path**: `Tests/(Nima) PBA/test #4/pdf_extractor/pj_directory/src/`

```
Tests/(Nima) PBA/test #4/pdf_extractor/pj_directory/src/
├── ground_truth/           # Existing ground truth data
├── pdf_extractor/
│   ├── __init__.py
│   ├── main.py             # CLI entry point
│   ├── cli/
│   │   ├── __init__.py
│   │   ├── interface.py    # CLI interface implementation
│   │   ├── commands.py     # Command handlers
│   │   └── formatters.py   # Output formatters
│   ├── core/
│   │   ├── __init__.py
│   │   ├── pdf_parser.py   # Main PDF parser
│   │   ├── pattern_engine.py # Pattern recognition engine
│   │   ├── validator.py    # Validation logic
│   │   └── processor.py    # Processing orchestrator
│   ├── extraction/
│   │   ├── __init__.py
│   │   └── pdfplumber_extractor.py  # PDFPlumber text extraction
│   ├── patterns/
│   │   ├── __init__.py
│   │   ├── pattern_matcher.py  # Pattern matching logic
│   │   ├── pattern_learner.py  # Pattern learning system
│   │   ├── avianca_patterns.py # Avianca-specific patterns
│   │   └── pattern_repository.py
│   ├── data/
│   │   ├── __init__.py
│   │   ├── models.py       # Data models
│   │   ├── parsers.py      # Data parsers (date, amount)
│   │   └── formatters.py   # Data formatters
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── config.py       # Configuration management
│   │   ├── logging.py      # Logging setup
│   │   ├── errors.py       # Error handling
│   │   └── helpers.py      # Utility functions
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_pdf_parser.py
│   │   ├── test_pattern_engine.py
│   │   ├── test_validator.py
│   │   └── fixtures/       # Test data
│   └── config/
│       ├── config.yaml     # Main configuration
│       ├── patterns.yaml   # Pattern definitions
│       └── logging.yaml    # Logging configuration
├── requirements.txt        # Python dependencies
├── setup.py               # Installation script
└── README.md              # Project documentation
```

## 12. Extensibility Design

### 12.1 Plugin Architecture

```python
class PatternPlugin:
    """Base class for pattern plugins"""
    
    def detect_pattern(self, text: str) -> bool:
        raise NotImplementedError
        
    def extract_transactions(self, text: str) -> List[Transaction]:
        raise NotImplementedError
```

### 12.2 Adding New Card Issuers

1. **Create Pattern Definition**
   ```yaml
   # patterns/new_issuer.yaml
   new_issuer_pattern:
     name: "new_issuer_standard"
     issuer: "new_issuer"
     transaction_regex: "..."
     date_format: "..."
     amount_format: "..."
   ```

2. **Implement Pattern Class**
   ```python
   class NewIssuerPattern(PatternPlugin):
       def detect_pattern(self, text: str) -> bool:
           # Implementation
           
       def extract_transactions(self, text: str) -> List[Transaction]:
           # Implementation
   ```

3. **Register Pattern**
   ```python
   pattern_engine.register_pattern("new_issuer", NewIssuerPattern())
   ```

## 13. Performance Considerations

### 13.1 PDFPlumber Optimization

1. **Memory Management**
   - Process PDFs page by page for large files
   - Close PDF objects properly to free memory
   - Use context managers for resource management

2. **Processing Speed**
   - Cache compiled regex patterns
   - Optimize pdfplumber extraction settings
   - Early termination on pattern detection

3. **Scalability**
   - Configurable timeout limits
   - Progress reporting for long operations
   - Resource usage monitoring

### 13.2 Performance Monitoring

```python
class PerformanceMonitor:
    """Monitor and report performance metrics"""
    
    def __init__(self):
        self.metrics = {}
        
    def start_timer(self, operation: str):
        """Start timing an operation"""
        
    def end_timer(self, operation: str):
        """End timing and record duration"""
        
    def record_memory_usage(self, operation: str):
        """Record memory usage for operation"""
        
    def generate_report(self) -> PerformanceReport:
        """Generate performance report"""
```

## 14. Testing Strategy

### 14.1 Test Categories

1. **Unit Tests**
   - PDFPlumber extraction testing
   - Pattern matching accuracy
   - Data parsing validation

2. **Integration Tests**
   - End-to-end processing
   - CLI interface testing
   - Error handling validation

3. **Performance Tests**
   - Processing speed benchmarks
   - Memory usage validation
   - Batch processing limits

4. **Validation Tests**
   - Ground truth accuracy
   - Pattern detection reliability
   - Edge case handling

### 14.2 Test Implementation

```python
class TestPDFExtractor:
    """Comprehensive test suite"""
    
    def test_pdfplumber_extraction(self):
        """Test PDFPlumber text extraction accuracy"""
        
    def test_single_file_processing(self):
        """Test single file processing accuracy"""
        
    def test_batch_processing(self):
        """Test batch processing functionality"""
        
    def test_pattern_detection(self):
        """Test pattern detection accuracy"""
        
    def test_validation_accuracy(self):
        """Test validation against ground truth"""
        
    def test_error_handling(self):
        """Test error handling scenarios"""
```

## 15. Deployment and Installation

### 15.1 Installation Requirements

```python
# requirements.txt
pdfplumber>=0.7.0
click>=8.0.0
pyyaml>=6.0
python-dateutil>=2.8.0
tabulate>=0.9.0
colorama>=0.4.0
```

### 15.2 Installation Script

```python
# setup.py
from setuptools import setup, find_packages

setup(
    name="pdf-expense-extractor",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "pdfplumber>=0.7.0",
        "click>=8.0.0",
        "pyyaml>=6.0",
        "python-dateutil>=2.8.0",
        "tabulate>=0.9.0",
        "colorama>=0.4.0"
    ],
    entry_points={
        'console_scripts': [
            'pdf-extractor=pdf_extractor.main:main',
        ],
    },
)
```

## 16. Architecture Validation

### 16.1 Requirements Compliance

✅ **Input Processing**: Handles six text-based PDFs from one known card issuer
✅ **Data Extraction**: Extracts Date, Description, Amount (in COP) from transaction lines
✅ **CLI Interface**: Supports both single file and batch folder processing modes
✅ **Validation**: Matches extracted data against ground_truth.json
✅ **Pattern Learning**: System to teach new PDF patterns from different card issuers
✅ **Technology**: Python 3 with pdfplumber library exclusively

### 16.2 Architecture Quality Attributes

- **Modularity**: Clear separation of concerns with distinct modules
- **Extensibility**: Plugin architecture for new patterns
- **Maintainability**: Well-defined interfaces and comprehensive logging
- **Reliability**: Robust error handling and validation mechanisms
- **Performance**: Optimized pdfplumber processing
- **Usability**: Intuitive CLI interface with comprehensive help

## 17. Next Steps

1. **Implementation Phase**: Begin with core modules (PDF Parser, PDFPlumber Extractor)
2. **Pattern Development**: Implement Avianca pattern recognition
3. **CLI Development**: Create command-line interface
4. **Validation Integration**: Implement ground truth validation
5. **Testing**: Comprehensive testing with provided PDFs
6. **Documentation**: User guides and API documentation
7. **Optimization**: Performance tuning and error handling refinement

This architecture provides a solid foundation for building a robust, extensible PDF credit card expense extraction system using pdfplumber that meets all specified requirements while allowing for future enhancements and new card issuer support.

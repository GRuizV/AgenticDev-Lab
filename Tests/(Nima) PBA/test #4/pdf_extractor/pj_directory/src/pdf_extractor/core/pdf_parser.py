"""
Main PDF parser orchestrator for PDF processing workflow.
"""

import logging
import time
from typing import List, Optional, Dict, Any
from pathlib import Path

from ..data.models import ProcessingResult, Transaction
from ..extraction.pdfplumber_extractor import PDFPlumberExtractor
from .pattern_engine import PatternEngine
from .validator import Validator


class PDFParser:
    """Main orchestrator for PDF processing."""
    
    def __init__(self, config_manager=None, pattern_engine: Optional[PatternEngine] = None, 
                 validator: Optional[Validator] = None):
        """
        Initialize the PDF parser.
        
        Args:
            config_manager: Configuration manager instance
            pattern_engine: Pattern engine instance
            validator: Validator instance
        """
        self.logger = logging.getLogger(__name__)
        self.config = config_manager
        
        # Initialize components
        self.pattern_engine = pattern_engine or PatternEngine()
        self.validator = validator
        self.text_extractor = PDFPlumberExtractor()
        
        self.logger.info("PDF parser initialized")
    
    def process_file(self, pdf_path: str, pattern_name: Optional[str] = None) -> ProcessingResult:
        """
        Process a single PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            pattern_name: Specific pattern to use, or None for auto-detection
            
        Returns:
            ProcessingResult object with extraction results
        """
        start_time = time.time()
        
        try:
            self.logger.info(f"Processing PDF file: {pdf_path}")
            
            # Validate file exists
            pdf_file = Path(pdf_path)
            if not pdf_file.exists():
                error_msg = f"PDF file not found: {pdf_path}"
                self.logger.error(error_msg)
                return ProcessingResult(
                    file_path=pdf_path,
                    transactions=[],
                    pattern_used="none",
                    processing_time=time.time() - start_time,
                    errors=[error_msg],
                    success=False
                )
            
            # Extract text from PDF
            try:
                text_content = self.text_extractor.extract_text(pdf_path)
                if not text_content.strip():
                    warning_msg = f"No text content extracted from {pdf_path}"
                    self.logger.warning(warning_msg)
                    return ProcessingResult(
                        file_path=pdf_path,
                        transactions=[],
                        pattern_used="none",
                        processing_time=time.time() - start_time,
                        warnings=[warning_msg],
                        success=False
                    )
                
                self.logger.debug(f"Extracted {len(text_content)} characters of text")
                
            except Exception as e:
                error_msg = f"Text extraction failed: {str(e)}"
                self.logger.error(error_msg)
                return ProcessingResult(
                    file_path=pdf_path,
                    transactions=[],
                    pattern_used="none",
                    processing_time=time.time() - start_time,
                    errors=[error_msg],
                    success=False
                )
            
            # Detect or use specified pattern
            if pattern_name is None:
                pattern_name = self.pattern_engine.detect_pattern(text_content)
                if pattern_name is None:
                    warning_msg = "No suitable pattern detected for PDF"
                    self.logger.warning(warning_msg)
                    return ProcessingResult(
                        file_path=pdf_path,
                        transactions=[],
                        pattern_used="none",
                        processing_time=time.time() - start_time,
                        warnings=[warning_msg],
                        success=False
                    )
            
            self.logger.info(f"Using pattern: {pattern_name}")
            
            # Extract transactions
            try:
                transactions = self.pattern_engine.extract_transactions(text_content, pattern_name)
                self.logger.info(f"Extracted {len(transactions)} transactions")
                
                # Validate transactions
                valid_transactions = [t for t in transactions if t.validate()]
                if len(valid_transactions) < len(transactions):
                    invalid_count = len(transactions) - len(valid_transactions)
                    warning_msg = f"Filtered out {invalid_count} invalid transactions"
                    self.logger.warning(warning_msg)
                
                processing_time = time.time() - start_time
                
                result = ProcessingResult(
                    file_path=pdf_path,
                    transactions=valid_transactions,
                    pattern_used=pattern_name,
                    processing_time=processing_time,
                    success=len(valid_transactions) > 0
                )
                
                if len(valid_transactions) == 0:
                    result.warnings.append("No valid transactions extracted")
                
                self.logger.info(f"Processing completed in {processing_time:.2f}s")
                return result
                
            except Exception as e:
                error_msg = f"Transaction extraction failed: {str(e)}"
                self.logger.error(error_msg)
                return ProcessingResult(
                    file_path=pdf_path,
                    transactions=[],
                    pattern_used=pattern_name,
                    processing_time=time.time() - start_time,
                    errors=[error_msg],
                    success=False
                )
                
        except Exception as e:
            error_msg = f"Unexpected error processing {pdf_path}: {str(e)}"
            self.logger.error(error_msg)
            return ProcessingResult(
                file_path=pdf_path,
                transactions=[],
                pattern_used="none",
                processing_time=time.time() - start_time,
                errors=[error_msg],
                success=False
            )
    
    def process_batch(self, folder_path: str, pattern_name: Optional[str] = None) -> Dict[str, ProcessingResult]:
        """
        Process all PDFs in a folder.
        
        Args:
            folder_path: Path to the folder containing PDF files
            pattern_name: Specific pattern to use, or None for auto-detection
            
        Returns:
            Dictionary mapping file names to ProcessingResult objects
        """
        try:
            self.logger.info(f"Processing batch from folder: {folder_path}")
            
            folder = Path(folder_path)
            if not folder.exists():
                self.logger.error(f"Folder not found: {folder_path}")
                return {}
            
            # Find all PDF files
            pdf_files = list(folder.glob("*.pdf"))
            if not pdf_files:
                self.logger.warning(f"No PDF files found in {folder_path}")
                return {}
            
            self.logger.info(f"Found {len(pdf_files)} PDF files to process")
            
            results = {}
            for pdf_file in pdf_files:
                file_name = pdf_file.name
                self.logger.info(f"Processing file {file_name}")
                
                result = self.process_file(str(pdf_file), pattern_name)
                results[file_name] = result
                
                if result.success:
                    self.logger.info(f"✓ {file_name}: {len(result.transactions)} transactions")
                else:
                    self.logger.warning(f"✗ {file_name}: Processing failed")
            
            successful = sum(1 for r in results.values() if r.success)
            self.logger.info(f"Batch processing completed: {successful}/{len(results)} files successful")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error processing batch from {folder_path}: {str(e)}")
            return {}
    
    def process_with_validation(self, pdf_path: str, bill_name: Optional[str] = None, 
                              pattern_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a PDF file and validate against ground truth.
        
        Args:
            pdf_path: Path to the PDF file
            bill_name: Bill name for ground truth lookup (defaults to filename)
            pattern_name: Specific pattern to use, or None for auto-detection
            
        Returns:
            Dictionary containing processing and validation results
        """
        try:
            # Process the file
            processing_result = self.process_file(pdf_path, pattern_name)
            
            # Determine bill name
            if bill_name is None:
                bill_name = Path(pdf_path).stem
            
            # Validate if validator is available
            validation_result = None
            if self.validator:
                validation_result = self.validator.validate_extraction(
                    bill_name, processing_result.transactions
                )
            
            return {
                "processing_result": processing_result,
                "validation_result": validation_result,
                "bill_name": bill_name,
                "overall_success": processing_result.success and (
                    validation_result.is_valid if validation_result else True
                )
            }
            
        except Exception as e:
            self.logger.error(f"Error in process_with_validation for {pdf_path}: {str(e)}")
            return {
                "processing_result": None,
                "validation_result": None,
                "bill_name": bill_name or Path(pdf_path).stem,
                "overall_success": False,
                "error": str(e)
            }
    
    def analyze_pdf_structure(self, pdf_path: str) -> Dict[str, Any]:
        """
        Analyze PDF structure to help with pattern development.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary containing PDF structure analysis
        """
        try:
            self.logger.info(f"Analyzing PDF structure: {pdf_path}")
            
            # Get basic PDF info
            pdf_info = self.text_extractor.get_pdf_info(pdf_path)
            
            # Extract text and layout
            text_content = self.text_extractor.extract_text(pdf_path)
            layout_data = self.text_extractor.extract_with_layout(pdf_path)
            
            # Analyze text patterns
            pattern_analysis = self.pattern_engine.analyze_text_for_patterns(text_content)
            
            # Extract tables if any
            tables = self.text_extractor.extract_tables(pdf_path)
            
            analysis = {
                "pdf_info": pdf_info,
                "text_length": len(text_content),
                "layout_pages": len(layout_data),
                "tables_found": len(tables),
                "pattern_analysis": pattern_analysis,
                "sample_text": text_content[:500] if text_content else "",
                "recommendations": []
            }
            
            # Generate recommendations
            if tables:
                analysis["recommendations"].append(f"Found {len(tables)} tables - consider table-based extraction")
            
            if not pattern_analysis.get("detected_patterns"):
                analysis["recommendations"].append("No existing patterns detected - may need custom pattern")
            
            if pattern_analysis.get("suggested_patterns"):
                analysis["recommendations"].append("Found potential patterns - test suggested patterns")
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing PDF structure for {pdf_path}: {str(e)}")
            return {"error": str(e)}
    
    def test_pattern_on_pdf(self, pdf_path: str, pattern_name: str) -> Dict[str, Any]:
        """
        Test a specific pattern on a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            pattern_name: Name of the pattern to test
            
        Returns:
            Dictionary containing test results
        """
        try:
            self.logger.info(f"Testing pattern {pattern_name} on {pdf_path}")
            
            # Extract text
            text_content = self.text_extractor.extract_text(pdf_path)
            
            # Test pattern
            pattern_validation = self.pattern_engine.validate_pattern_against_text(
                text_content, pattern_name
            )
            
            # Try extraction
            transactions = self.pattern_engine.extract_transactions(text_content, pattern_name)
            
            return {
                "pattern_name": pattern_name,
                "pdf_path": pdf_path,
                "pattern_validation": pattern_validation,
                "extracted_transactions": len(transactions),
                "transactions": [t.to_dict() for t in transactions[:5]],  # First 5 for preview
                "success": len(transactions) > 0,
                "recommendations": self._generate_pattern_recommendations(pattern_validation, transactions)
            }
            
        except Exception as e:
            self.logger.error(f"Error testing pattern {pattern_name} on {pdf_path}: {str(e)}")
            return {
                "pattern_name": pattern_name,
                "pdf_path": pdf_path,
                "error": str(e),
                "success": False
            }
    
    def _generate_pattern_recommendations(self, validation: Dict[str, Any], 
                                        transactions: List[Transaction]) -> List[str]:
        """
        Generate recommendations based on pattern testing results.
        
        Args:
            validation: Pattern validation results
            transactions: Extracted transactions
            
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        if validation.get("success_rate", 0) < 0.8:
            recommendations.append("Low success rate - consider adjusting pattern regex")
        
        if validation.get("total_matches", 0) == 0:
            recommendations.append("No matches found - pattern may not be suitable for this PDF")
        
        if len(transactions) == 0:
            recommendations.append("No valid transactions extracted - check date/amount parsing")
        
        if validation.get("total_matches", 0) > len(transactions):
            recommendations.append("Some matches failed validation - review transaction validation rules")
        
        if not recommendations:
            recommendations.append("Pattern appears to work well for this PDF")
        
        return recommendations
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the PDF parser.
        
        Returns:
            Dictionary containing parser statistics
        """
        try:
            pattern_stats = self.pattern_engine.get_engine_stats()
            
            return {
                "parser_status": "operational",
                "pattern_engine": pattern_stats,
                "text_extractor": "pdfplumber",
                "validator_available": self.validator is not None,
                "config_loaded": self.config is not None
            }
            
        except Exception as e:
            return {
                "parser_status": "error",
                "error": str(e)
            }
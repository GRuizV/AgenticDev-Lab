"""
Main processing orchestrator that coordinates all components.
"""

import logging
import time
from typing import List, Dict, Any, Optional
from pathlib import Path

from ..data.models import BatchResult, ProcessingResult, ValidationReport
from .pdf_parser import PDFParser
from .pattern_engine import PatternEngine
from .validator import Validator


class PDFProcessor:
    """Main processing orchestrator that coordinates all components."""
    
    def __init__(self, config_manager=None, ground_truth_path: Optional[str] = None):
        """
        Initialize the PDF processor.
        
        Args:
            config_manager: Configuration manager instance
            ground_truth_path: Path to ground truth JSON file
        """
        self.logger = logging.getLogger(__name__)
        self.config = config_manager
        
        # Initialize core components
        self.pattern_engine = PatternEngine()
        self.validator = Validator(ground_truth_path) if ground_truth_path else None
        self.pdf_parser = PDFParser(config_manager, self.pattern_engine, self.validator)
        
        self.logger.info("PDF processor initialized")
    
    def process_single_file(self, pdf_path: str, pattern_name: Optional[str] = None, 
                          validate: bool = True) -> Dict[str, Any]:
        """
        Process a single PDF file with optional validation.
        
        Args:
            pdf_path: Path to the PDF file
            pattern_name: Specific pattern to use, or None for auto-detection
            validate: Whether to validate against ground truth
            
        Returns:
            Dictionary containing processing and validation results
        """
        try:
            self.logger.info(f"Processing single file: {pdf_path}")
            
            if validate and self.validator:
                # Process with validation
                result = self.pdf_parser.process_with_validation(pdf_path, None, pattern_name)
            else:
                # Process without validation
                processing_result = self.pdf_parser.process_file(pdf_path, pattern_name)
                result = {
                    "processing_result": processing_result,
                    "validation_result": None,
                    "bill_name": Path(pdf_path).stem,
                    "overall_success": processing_result.success
                }
            
            # Add summary information
            if result["processing_result"]:
                pr = result["processing_result"]
                result["summary"] = {
                    "file_path": pr.file_path,
                    "transactions_extracted": len(pr.transactions),
                    "total_amount": str(pr.total_amount),
                    "pattern_used": pr.pattern_used,
                    "processing_time": pr.processing_time,
                    "success": pr.success
                }
                
                if result["validation_result"]:
                    vr = result["validation_result"]
                    result["summary"]["validation"] = {
                        "accuracy": vr.accuracy,
                        "total_match": vr.total_match,
                        "count_match": vr.count_match,
                        "is_valid": vr.is_valid
                    }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error processing single file {pdf_path}: {str(e)}")
            return {
                "processing_result": None,
                "validation_result": None,
                "bill_name": Path(pdf_path).stem,
                "overall_success": False,
                "error": str(e)
            }
    
    def process_batch_folder(self, folder_path: str, pattern_name: Optional[str] = None, 
                           validate: bool = True) -> Dict[str, Any]:
        """
        Process all PDF files in a folder.
        
        Args:
            folder_path: Path to the folder containing PDF files
            pattern_name: Specific pattern to use, or None for auto-detection
            validate: Whether to validate against ground truth
            
        Returns:
            Dictionary containing batch processing results
        """
        start_time = time.time()
        
        try:
            self.logger.info(f"Processing batch folder: {folder_path}")
            
            folder = Path(folder_path)
            if not folder.exists():
                error_msg = f"Folder not found: {folder_path}"
                self.logger.error(error_msg)
                return {"error": error_msg, "success": False}
            
            # Find all PDF files
            pdf_files = list(folder.glob("*.pdf"))
            if not pdf_files:
                warning_msg = f"No PDF files found in {folder_path}"
                self.logger.warning(warning_msg)
                return {"warning": warning_msg, "success": False, "results": {}}
            
            self.logger.info(f"Found {len(pdf_files)} PDF files to process")
            
            # Process each file
            file_results = {}
            processing_results = []
            validation_results = []
            
            for pdf_file in pdf_files:
                file_name = pdf_file.name
                self.logger.info(f"Processing {file_name}")
                
                try:
                    if validate and self.validator:
                        # Process with validation
                        result = self.pdf_parser.process_with_validation(
                            str(pdf_file), file_name.replace('.pdf', ''), pattern_name
                        )
                        
                        if result["processing_result"]:
                            processing_results.append(result["processing_result"])
                        
                        if result["validation_result"]:
                            validation_results.append(result["validation_result"])
                    else:
                        # Process without validation
                        processing_result = self.pdf_parser.process_file(str(pdf_file), pattern_name)
                        processing_results.append(processing_result)
                        
                        result = {
                            "processing_result": processing_result,
                            "validation_result": None,
                            "bill_name": file_name.replace('.pdf', ''),
                            "overall_success": processing_result.success
                        }
                    
                    file_results[file_name] = result
                    
                    if result["overall_success"]:
                        self.logger.info(f"✓ {file_name}: Success")
                    else:
                        self.logger.warning(f"✗ {file_name}: Failed")
                        
                except Exception as e:
                    error_msg = f"Error processing {file_name}: {str(e)}"
                    self.logger.error(error_msg)
                    file_results[file_name] = {
                        "processing_result": None,
                        "validation_result": None,
                        "bill_name": file_name.replace('.pdf', ''),
                        "overall_success": False,
                        "error": error_msg
                    }
            
            # Generate batch result
            batch_result = self._create_batch_result(processing_results, time.time() - start_time)
            
            # Generate validation report if applicable
            validation_report = None
            if validation_results and self.validator:
                validation_report = self.validator.generate_validation_report(validation_results)
            
            # Create summary
            successful_files = sum(1 for r in file_results.values() if r["overall_success"])
            total_transactions = sum(
                len(r["processing_result"].transactions) 
                for r in file_results.values() 
                if r["processing_result"] and r["processing_result"].success
            )
            
            summary = {
                "total_files": len(pdf_files),
                "successful_files": successful_files,
                "failed_files": len(pdf_files) - successful_files,
                "total_transactions": total_transactions,
                "processing_time": time.time() - start_time,
                "success_rate": successful_files / len(pdf_files) * 100
            }
            
            if validation_report:
                summary["validation"] = {
                    "overall_accuracy": validation_report.overall_accuracy,
                    "passed_validations": validation_report.passed_validations,
                    "failed_validations": validation_report.failed_validations,
                    "pass_rate": validation_report.pass_rate
                }
            
            result = {
                "summary": summary,
                "batch_result": batch_result,
                "validation_report": validation_report,
                "file_results": file_results,
                "success": successful_files > 0
            }
            
            self.logger.info(f"Batch processing completed: {successful_files}/{len(pdf_files)} files successful")
            return result
            
        except Exception as e:
            self.logger.error(f"Error processing batch folder {folder_path}: {str(e)}")
            return {
                "error": str(e),
                "success": False,
                "processing_time": time.time() - start_time
            }
    
    def _create_batch_result(self, processing_results: List[ProcessingResult], 
                           total_time: float) -> BatchResult:
        """
        Create a BatchResult from individual processing results.
        
        Args:
            processing_results: List of ProcessingResult objects
            total_time: Total processing time
            
        Returns:
            BatchResult object
        """
        successful_results = [r for r in processing_results if r.success]
        failed_results = [r for r in processing_results if not r.success]
        
        total_transactions = sum(len(r.transactions) for r in successful_results)
        
        return BatchResult(
            results=processing_results,
            total_files=len(processing_results),
            successful_files=len(successful_results),
            failed_files=len(failed_results),
            total_transactions=total_transactions,
            processing_time=total_time
        )
    
    def analyze_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """
        Analyze a PDF file to understand its structure and suggest patterns.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary containing analysis results
        """
        try:
            self.logger.info(f"Analyzing PDF: {pdf_path}")
            
            analysis = self.pdf_parser.analyze_pdf_structure(pdf_path)
            
            # Add pattern suggestions
            if "pattern_analysis" in analysis:
                pattern_analysis = analysis["pattern_analysis"]
                
                # Get available patterns
                available_patterns = self.pattern_engine.list_available_patterns()
                analysis["available_patterns"] = available_patterns
                
                # Test promising patterns
                detected_patterns = pattern_analysis.get("detected_patterns", [])
                if detected_patterns:
                    analysis["pattern_tests"] = []
                    for pattern_info in detected_patterns[:3]:  # Test top 3
                        pattern_name = pattern_info["pattern_name"]
                        test_result = self.pdf_parser.test_pattern_on_pdf(pdf_path, pattern_name)
                        analysis["pattern_tests"].append(test_result)
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing PDF {pdf_path}: {str(e)}")
            return {"error": str(e)}
    
    def test_pattern(self, pdf_path: str, pattern_name: str) -> Dict[str, Any]:
        """
        Test a specific pattern on a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            pattern_name: Name of the pattern to test
            
        Returns:
            Dictionary containing test results
        """
        return self.pdf_parser.test_pattern_on_pdf(pdf_path, pattern_name)
    
    def validate_against_ground_truth(self, pdf_path: str, bill_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a PDF and validate against ground truth.
        
        Args:
            pdf_path: Path to the PDF file
            bill_name: Bill name for ground truth lookup
            
        Returns:
            Dictionary containing validation results
        """
        if not self.validator:
            return {"error": "No validator configured"}
        
        return self.process_single_file(pdf_path, None, True)
    
    def get_ground_truth_info(self) -> Dict[str, Any]:
        """
        Get information about loaded ground truth data.
        
        Returns:
            Dictionary containing ground truth information
        """
        if not self.validator:
            return {"error": "No validator configured"}
        
        return self.validator.get_ground_truth_summary()
    
    def list_available_patterns(self) -> List[str]:
        """
        Get list of all available patterns.
        
        Returns:
            List of pattern names
        """
        return self.pattern_engine.list_available_patterns()
    
    def get_pattern_info(self, pattern_name: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a pattern.
        
        Args:
            pattern_name: Name of the pattern
            
        Returns:
            Pattern information dictionary
        """
        return self.pattern_engine.get_pattern_info(pattern_name)
    
    def get_processor_status(self) -> Dict[str, Any]:
        """
        Get status information about the processor and its components.
        
        Returns:
            Dictionary containing status information
        """
        try:
            parser_stats = self.pdf_parser.get_processing_stats()
            
            status = {
                "processor_status": "operational",
                "components": {
                    "pdf_parser": parser_stats,
                    "pattern_engine": "operational",
                    "validator": "available" if self.validator else "not_configured"
                },
                "capabilities": {
                    "single_file_processing": True,
                    "batch_processing": True,
                    "pattern_detection": True,
                    "validation": self.validator is not None,
                    "pattern_learning": True
                }
            }
            
            if self.validator:
                ground_truth_info = self.validator.get_ground_truth_summary()
                status["ground_truth"] = ground_truth_info
            
            return status
            
        except Exception as e:
            return {
                "processor_status": "error",
                "error": str(e)
            }
    
    def create_processing_report(self, results: Dict[str, Any]) -> str:
        """
        Create a formatted text report from processing results.
        
        Args:
            results: Processing results dictionary
            
        Returns:
            Formatted report string
        """
        try:
            report_lines = []
            report_lines.append("PDF EXTRACTION REPORT")
            report_lines.append("=" * 50)
            report_lines.append("")
            
            # Summary section
            if "summary" in results:
                summary = results["summary"]
                report_lines.append("SUMMARY:")
                report_lines.append(f"  Total files processed: {summary.get('total_files', 0)}")
                report_lines.append(f"  Successful files: {summary.get('successful_files', 0)}")
                report_lines.append(f"  Failed files: {summary.get('failed_files', 0)}")
                report_lines.append(f"  Success rate: {summary.get('success_rate', 0):.1f}%")
                report_lines.append(f"  Total transactions: {summary.get('total_transactions', 0)}")
                report_lines.append(f"  Processing time: {summary.get('processing_time', 0):.2f}s")
                
                if "validation" in summary:
                    val = summary["validation"]
                    report_lines.append(f"  Overall accuracy: {val.get('overall_accuracy', 0):.1%}")
                    report_lines.append(f"  Validation pass rate: {val.get('pass_rate', 0):.1f}%")
                
                report_lines.append("")
            
            # File details section
            if "file_results" in results:
                report_lines.append("FILE DETAILS:")
                for file_name, file_result in results["file_results"].items():
                    pr = file_result.get("processing_result")
                    vr = file_result.get("validation_result")
                    
                    status = "✓" if file_result.get("overall_success") else "✗"
                    report_lines.append(f"  {status} {file_name}")
                    
                    if pr:
                        report_lines.append(f"    Transactions: {len(pr.transactions)}")
                        report_lines.append(f"    Total amount: ${pr.total_amount}")
                        report_lines.append(f"    Pattern: {pr.pattern_used}")
                        
                        if vr:
                            report_lines.append(f"    Accuracy: {vr.accuracy:.1%}")
                            report_lines.append(f"    Expected: {vr.expected_count} transactions, ${vr.expected_total}")
                    
                    if file_result.get("error"):
                        report_lines.append(f"    Error: {file_result['error']}")
                    
                    report_lines.append("")
            
            return "\n".join(report_lines)
            
        except Exception as e:
            return f"Error generating report: {str(e)}"
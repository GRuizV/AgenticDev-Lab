"""
Command handlers for CLI operations.
"""

import os
import sys
import time
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

from ..core.processor import PDFProcessor
from ..core.validator import GroundTruthValidator
from ..patterns.pattern_repository import PatternRepository
from .formatters import OutputFormatter


class CommandHandler:
    """Handles CLI command execution."""
    
    def __init__(self):
        self.processor = PDFProcessor()
        self.validator = GroundTruthValidator()
        self.pattern_repo = PatternRepository()
        self.formatter = OutputFormatter()
    
    def handle_extract(self, file_path: str, pattern: Optional[str] = None, 
                      output_format: str = "table", output_file: Optional[str] = None,
                      validate: bool = False, ground_truth_file: Optional[str] = None) -> int:
        """
        Handle single file extraction command.
        
        Args:
            file_path: Path to PDF file
            pattern: Pattern name to use (optional)
            output_format: Output format (table, json, csv)
            output_file: Output file path (optional)
            validate: Whether to validate against ground truth
            ground_truth_file: Path to ground truth file
            
        Returns:
            Exit code (0 for success, 1 for error)
        """
        try:
            # Validate input file
            if not os.path.exists(file_path):
                print(self.formatter.format_error(f"File not found: {file_path}"))
                return 1
            
            if not file_path.lower().endswith('.pdf'):
                print(self.formatter.format_error(f"File must be a PDF: {file_path}"))
                return 1
            
            print(self.formatter.format_info(f"Processing: {file_path}"))
            
            # Process the PDF
            start_time = time.time()
            result = self.processor.process_pdf(file_path, pattern_name=pattern)
            processing_time = time.time() - start_time
            
            if not result.success:
                print(self.formatter.format_error(f"Processing failed: {', '.join(result.errors)}"))
                return 1
            
            print(self.formatter.format_success(f"Extracted {len(result.transactions)} transactions in {processing_time:.2f}s"))
            
            # Format output
            output_content = self.formatter.format_processing_result(result, output_format)
            
            # Validation if requested
            validation_output = ""
            if validate and ground_truth_file:
                validation_result = self._validate_result(result, ground_truth_file)
                if validation_result:
                    validation_output = "\n\n" + self.formatter.format_validation_result(validation_result)
            
            # Output to file or console
            full_output = output_content + validation_output
            if output_file:
                self._write_output_file(full_output, output_file, output_format)
                print(self.formatter.format_success(f"Results saved to: {output_file}"))
            else:
                print(full_output)
            
            return 0
            
        except Exception as e:
            print(self.formatter.format_error(f"Unexpected error: {str(e)}"))
            return 1
    
    def handle_batch(self, input_dir: str, pattern: Optional[str] = None,
                    output_format: str = "table", output_file: Optional[str] = None,
                    validate: bool = False, ground_truth_file: Optional[str] = None) -> int:
        """
        Handle batch processing command.
        
        Args:
            input_dir: Directory containing PDF files
            pattern: Pattern name to use (optional)
            output_format: Output format
            output_file: Output file path (optional)
            validate: Whether to validate against ground truth
            ground_truth_file: Path to ground truth file
            
        Returns:
            Exit code (0 for success, 1 for error)
        """
        try:
            # Validate input directory
            if not os.path.exists(input_dir):
                print(self.formatter.format_error(f"Directory not found: {input_dir}"))
                return 1
            
            # Find PDF files
            pdf_files = self._find_pdf_files(input_dir)
            if not pdf_files:
                print(self.formatter.format_error(f"No PDF files found in: {input_dir}"))
                return 1
            
            print(self.formatter.format_info(f"Found {len(pdf_files)} PDF files"))
            
            # Load ground truth if validation requested
            ground_truth_data = None
            if validate and ground_truth_file:
                ground_truth_data = self._load_ground_truth(ground_truth_file)
                if not ground_truth_data:
                    print(self.formatter.format_warning("Could not load ground truth file"))
                    validate = False
            
            # Process files
            batch_results = self._process_batch(pdf_files, pattern, validate, ground_truth_data)
            
            # Format and output results
            output_content = self.formatter.format_batch_summary(batch_results, output_format)
            
            if output_file:
                self._write_output_file(output_content, output_file, output_format)
                print(self.formatter.format_success(f"Batch results saved to: {output_file}"))
            else:
                print(output_content)
            
            # Return appropriate exit code
            success_rate = batch_results.get("summary", {}).get("success_rate", 0)
            return 0 if success_rate > 50 else 1
            
        except Exception as e:
            print(self.formatter.format_error(f"Batch processing error: {str(e)}"))
            return 1
    
    def handle_validate(self, file_path: str, ground_truth_file: str,
                       pattern: Optional[str] = None, output_format: str = "table") -> int:
        """
        Handle validation command.
        
        Args:
            file_path: Path to PDF file
            ground_truth_file: Path to ground truth file
            pattern: Pattern name to use (optional)
            output_format: Output format
            
        Returns:
            Exit code (0 for success, 1 for error)
        """
        try:
            # Validate inputs
            if not os.path.exists(file_path):
                print(self.formatter.format_error(f"File not found: {file_path}"))
                return 1
            
            if not os.path.exists(ground_truth_file):
                print(self.formatter.format_error(f"Ground truth file not found: {ground_truth_file}"))
                return 1
            
            # Process PDF
            print(self.formatter.format_info(f"Processing and validating: {file_path}"))
            result = self.processor.process_pdf(file_path, pattern_name=pattern)
            
            if not result.success:
                print(self.formatter.format_error(f"Processing failed: {', '.join(result.errors)}"))
                return 1
            
            # Validate
            validation_result = self._validate_result(result, ground_truth_file)
            if not validation_result:
                print(self.formatter.format_error("Validation failed"))
                return 1
            
            # Output results
            output_content = self.formatter.format_validation_result(validation_result)
            print(output_content)
            
            return 0 if validation_result.is_valid else 1
            
        except Exception as e:
            print(self.formatter.format_error(f"Validation error: {str(e)}"))
            return 1
    
    def handle_patterns(self, detailed: bool = False) -> int:
        """
        Handle patterns listing command.
        
        Args:
            detailed: Whether to show detailed pattern information
            
        Returns:
            Exit code (0 for success)
        """
        try:
            patterns = self.pattern_repo.list_patterns()
            
            if detailed:
                pattern_info = {}
                for pattern_name in patterns:
                    pattern = self.pattern_repo.get_pattern(pattern_name)
                    if pattern:
                        pattern_info[pattern_name] = {
                            "issuer": pattern.issuer,
                            "card_type": pattern.card_type,
                            "confidence_threshold": pattern.confidence_threshold
                        }
                output_content = self.formatter.format_pattern_list(patterns, pattern_info)
            else:
                output_content = self.formatter.format_pattern_list(patterns)
            
            print(output_content)
            return 0
            
        except Exception as e:
            print(self.formatter.format_error(f"Error listing patterns: {str(e)}"))
            return 1
    
    def handle_info(self, file_path: str) -> int:
        """
        Handle file info command.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Exit code (0 for success, 1 for error)
        """
        try:
            if not os.path.exists(file_path):
                print(self.formatter.format_error(f"File not found: {file_path}"))
                return 1
            
            # Get basic file info
            file_stat = os.stat(file_path)
            file_size = file_stat.st_size
            
            print(f"File Information: {file_path}")
            print("=" * 50)
            print(f"Size: {file_size:,} bytes ({file_size / 1024 / 1024:.2f} MB)")
            print(f"Modified: {time.ctime(file_stat.st_mtime)}")
            
            # Try to get PDF-specific info
            try:
                from ..extraction.pdfplumber_extractor import PDFPlumberExtractor
                extractor = PDFPlumberExtractor()
                
                with extractor._open_pdf(file_path) as pdf:
                    print(f"Pages: {len(pdf.pages)}")
                    
                    # Sample first page for text content
                    if pdf.pages:
                        first_page = pdf.pages[0]
                        text_sample = first_page.extract_text()
                        if text_sample:
                            lines = text_sample.split('\n')[:10]  # First 10 lines
                            print(f"Text preview (first 10 lines):")
                            for i, line in enumerate(lines, 1):
                                print(f"  {i}: {line.strip()}")
                        else:
                            print("No text content detected")
                            
            except Exception as e:
                print(f"Could not extract PDF details: {str(e)}")
            
            return 0
            
        except Exception as e:
            print(self.formatter.format_error(f"Error getting file info: {str(e)}"))
            return 1
    
    def _find_pdf_files(self, directory: str) -> List[str]:
        """Find all PDF files in directory."""
        pdf_files = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.lower().endswith('.pdf'):
                    pdf_files.append(os.path.join(root, file))
        return sorted(pdf_files)
    
    def _load_ground_truth(self, ground_truth_file: str) -> Optional[Dict[str, Any]]:
        """Load ground truth data from file."""
        try:
            with open(ground_truth_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(self.formatter.format_warning(f"Could not load ground truth: {str(e)}"))
            return None
    
    def _validate_result(self, result, ground_truth_file: str):
        """Validate processing result against ground truth."""
        try:
            # Extract bill name from file path
            bill_name = Path(result.file_path).stem
            
            # Load and validate
            return self.validator.validate_extraction(
                result.transactions, 
                bill_name, 
                ground_truth_file
            )
        except Exception as e:
            print(self.formatter.format_warning(f"Validation error: {str(e)}"))
            return None
    
    def _process_batch(self, pdf_files: List[str], pattern: Optional[str], 
                      validate: bool, ground_truth_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Process a batch of PDF files."""
        start_time = time.time()
        
        file_results = {}
        successful_files = 0
        failed_files = 0
        total_transactions = 0
        validation_passes = 0
        total_accuracy = 0.0
        
        for i, file_path in enumerate(pdf_files, 1):
            print(f"Processing {i}/{len(pdf_files)}: {os.path.basename(file_path)}")
            
            try:
                # Process file
                result = self.processor.process_pdf(file_path, pattern_name=pattern)
                
                file_result = {
                    "processing_result": result,
                    "validation_result": None,
                    "overall_success": result.success
                }
                
                if result.success:
                    successful_files += 1
                    total_transactions += len(result.transactions)
                    
                    # Validate if requested
                    if validate and ground_truth_data:
                        validation_result = self._validate_result(result, ground_truth_data)
                        if validation_result:
                            file_result["validation_result"] = validation_result
                            total_accuracy += validation_result.accuracy
                            if validation_result.is_valid:
                                validation_passes += 1
                else:
                    failed_files += 1
                
                file_results[os.path.basename(file_path)] = file_result
                
            except Exception as e:
                failed_files += 1
                file_results[os.path.basename(file_path)] = {
                    "processing_result": None,
                    "validation_result": None,
                    "overall_success": False,
                    "error": str(e)
                }
        
        processing_time = time.time() - start_time
        
        # Calculate summary statistics
        total_files = len(pdf_files)
        success_rate = (successful_files / total_files) * 100 if total_files > 0 else 0
        
        summary = {
            "total_files": total_files,
            "successful_files": successful_files,
            "failed_files": failed_files,
            "success_rate": success_rate,
            "total_transactions": total_transactions,
            "processing_time": processing_time
        }
        
        if validate and successful_files > 0:
            overall_accuracy = total_accuracy / successful_files if successful_files > 0 else 0
            pass_rate = (validation_passes / successful_files) * 100 if successful_files > 0 else 0
            
            summary["validation"] = {
                "overall_accuracy": overall_accuracy,
                "validation_passes": validation_passes,
                "pass_rate": pass_rate
            }
        
        return {
            "summary": summary,
            "file_results": file_results
        }
    
    def _write_output_file(self, content: str, output_file: str, output_format: str):
        """Write output content to file."""
        try:
            # Create output directory if needed
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write content
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content)
                
        except Exception as e:
            print(self.formatter.format_error(f"Could not write output file: {str(e)}"))
            raise
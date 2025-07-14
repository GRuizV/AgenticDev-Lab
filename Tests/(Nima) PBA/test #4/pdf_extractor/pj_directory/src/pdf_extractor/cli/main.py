"""
Main CLI interface for PDF Credit Card Expense Extractor.
"""

import argparse
import sys
import os
from typing import Optional

from .handlers import CommandHandler
from .formatters import OutputFormatter


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        prog="pdf-extractor",
        description="Extract credit card transactions from PDF statements",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract transactions from a single PDF
  pdf-extractor extract statement.pdf
  
  # Extract with specific pattern and save to JSON
  pdf-extractor extract statement.pdf --pattern avianca_mc --format json --output results.json
  
  # Process all PDFs in a directory
  pdf-extractor batch /path/to/pdfs --validate --ground-truth ground_truth.json
  
  # Validate extraction against ground truth
  pdf-extractor validate statement.pdf ground_truth.json
  
  # List available patterns
  pdf-extractor patterns --detailed
  
  # Get file information
  pdf-extractor info statement.pdf
        """
    )
    
    # Global options
    parser.add_argument(
        "--version",
        action="version",
        version="PDF Extractor 1.0.0"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    # Create subparsers for commands
    subparsers = parser.add_subparsers(
        dest="command",
        help="Available commands",
        metavar="COMMAND"
    )
    
    # Extract command
    extract_parser = subparsers.add_parser(
        "extract",
        help="Extract transactions from a single PDF file",
        description="Extract credit card transactions from a PDF statement"
    )
    extract_parser.add_argument(
        "file",
        help="Path to PDF file"
    )
    extract_parser.add_argument(
        "--pattern", "-p",
        help="Pattern name to use for extraction (e.g., avianca_mc, avianca_vs)"
    )
    extract_parser.add_argument(
        "--format", "-f",
        choices=["table", "json", "csv"],
        default="table",
        help="Output format (default: table)"
    )
    extract_parser.add_argument(
        "--output", "-o",
        help="Output file path (default: stdout)"
    )
    extract_parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate extraction against ground truth"
    )
    extract_parser.add_argument(
        "--ground-truth", "-g",
        help="Path to ground truth JSON file"
    )
    
    # Batch command
    batch_parser = subparsers.add_parser(
        "batch",
        help="Process multiple PDF files in a directory",
        description="Process all PDF files in a directory"
    )
    batch_parser.add_argument(
        "directory",
        help="Directory containing PDF files"
    )
    batch_parser.add_argument(
        "--pattern", "-p",
        help="Pattern name to use for extraction"
    )
    batch_parser.add_argument(
        "--format", "-f",
        choices=["table", "json", "csv"],
        default="table",
        help="Output format (default: table)"
    )
    batch_parser.add_argument(
        "--output", "-o",
        help="Output file path (default: stdout)"
    )
    batch_parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate extractions against ground truth"
    )
    batch_parser.add_argument(
        "--ground-truth", "-g",
        help="Path to ground truth JSON file"
    )
    
    # Validate command
    validate_parser = subparsers.add_parser(
        "validate",
        help="Validate extraction against ground truth",
        description="Process a PDF and validate results against ground truth data"
    )
    validate_parser.add_argument(
        "file",
        help="Path to PDF file"
    )
    validate_parser.add_argument(
        "ground_truth",
        help="Path to ground truth JSON file"
    )
    validate_parser.add_argument(
        "--pattern", "-p",
        help="Pattern name to use for extraction"
    )
    validate_parser.add_argument(
        "--format", "-f",
        choices=["table", "json"],
        default="table",
        help="Output format (default: table)"
    )
    
    # Patterns command
    patterns_parser = subparsers.add_parser(
        "patterns",
        help="List available extraction patterns",
        description="Show available patterns for different card issuers"
    )
    patterns_parser.add_argument(
        "--detailed", "-d",
        action="store_true",
        help="Show detailed pattern information"
    )
    
    # Info command
    info_parser = subparsers.add_parser(
        "info",
        help="Show information about a PDF file",
        description="Display metadata and content preview for a PDF file"
    )
    info_parser.add_argument(
        "file",
        help="Path to PDF file"
    )
    
    return parser


def main(args: Optional[list] = None) -> int:
    """
    Main entry point for the CLI.
    
    Args:
        args: Command line arguments (for testing)
        
    Returns:
        Exit code (0 for success, 1 for error)
    """
    parser = create_parser()
    
    # Parse arguments
    if args is None:
        args = sys.argv[1:]
    
    parsed_args = parser.parse_args(args)
    
    # Show help if no command specified
    if not parsed_args.command:
        parser.print_help()
        return 1
    
    # Initialize handler and formatter
    handler = CommandHandler()
    formatter = OutputFormatter()
    
    try:
        # Route to appropriate command handler
        if parsed_args.command == "extract":
            return handler.handle_extract(
                file_path=parsed_args.file,
                pattern=parsed_args.pattern,
                output_format=parsed_args.format,
                output_file=parsed_args.output,
                validate=parsed_args.validate,
                ground_truth_file=parsed_args.ground_truth
            )
        
        elif parsed_args.command == "batch":
            return handler.handle_batch(
                input_dir=parsed_args.directory,
                pattern=parsed_args.pattern,
                output_format=parsed_args.format,
                output_file=parsed_args.output,
                validate=parsed_args.validate,
                ground_truth_file=parsed_args.ground_truth
            )
        
        elif parsed_args.command == "validate":
            return handler.handle_validate(
                file_path=parsed_args.file,
                ground_truth_file=parsed_args.ground_truth,
                pattern=parsed_args.pattern,
                output_format=parsed_args.format
            )
        
        elif parsed_args.command == "patterns":
            return handler.handle_patterns(
                detailed=parsed_args.detailed
            )
        
        elif parsed_args.command == "info":
            return handler.handle_info(
                file_path=parsed_args.file
            )
        
        else:
            print(formatter.format_error(f"Unknown command: {parsed_args.command}"))
            return 1
    
    except KeyboardInterrupt:
        print(formatter.format_info("Operation cancelled by user"))
        return 1
    
    except Exception as e:
        if parsed_args.verbose:
            import traceback
            traceback.print_exc()
        else:
            print(formatter.format_error(f"Unexpected error: {str(e)}"))
        return 1


def cli_entry_point():
    """Entry point for console script."""
    sys.exit(main())


if __name__ == "__main__":
    cli_entry_point()
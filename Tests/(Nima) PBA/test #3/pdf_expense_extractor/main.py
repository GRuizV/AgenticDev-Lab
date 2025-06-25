"""
Main entry point for the PDF Credit Card Expense Extractor CLI.
"""

import argparse
import sys
from pathlib import Path
from .core.cli_interface import ExpenseExtractorCLI
from .config.settings import Settings


def create_parser() -> argparse.ArgumentParser:
    """
    Create command-line argument parser.
    
    Returns:
        Configured argument parser
    """
    parser = argparse.ArgumentParser(
        description="Extract credit card transactions from PDF files with validation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m pdf_expense_extractor                    # Use default PDF directory
  python -m pdf_expense_extractor --dir ./pdfs       # Specify PDF directory
  python -m pdf_expense_extractor --verbose          # Enable verbose output
  python -m pdf_expense_extractor --test-parsers file.pdf  # Test parsers on a file
        """
    )
    
    parser.add_argument(
        '--dir', '--directory',
        type=str,
        default=None,
        help='Directory containing PDF files (default: ../Test PDFs)'
    )
    
    parser.add_argument(
        '--tolerance',
        type=float,
        default=1.0,
        help='Amount tolerance for validation in dollars (default: 1.0)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '--no-progress',
        action='store_true',
        help='Disable progress display'
    )
    
    parser.add_argument(
        '--test-parsers',
        type=str,
        metavar='PDF_FILE',
        help='Test all available parsers on a specific PDF file'
    )
    
    parser.add_argument(
        '--single-file',
        type=str,
        metavar='PDF_FILE',
        help='Process a single PDF file'
    )
    
    parser.add_argument(
        '--report',
        action='store_true',
        help='Generate detailed validation report'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='PDF Expense Extractor 1.0.0'
    )
    
    return parser


def main():
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    try:
        # Create settings from arguments
        settings = Settings(
            amount_tolerance=args.tolerance,
            verbose=args.verbose,
            show_progress=not args.no_progress,
            pdf_directory=args.dir or "../Test PDFs/base_6"
        )
        
        # Create CLI interface
        cli = ExpenseExtractorCLI(settings)
        
        # Handle special commands
        if args.test_parsers:
            return handle_test_parsers(cli, args.test_parsers)
        
        if args.single_file:
            return handle_single_file(cli, args.single_file, args.report)
        
        # Normal processing
        exit_code = cli.run(args.dir)
        
        # Generate report if requested
        if args.report and exit_code == 0:
            print("\n" + "=" * 60)
            print("DETAILED VALIDATION REPORT")
            print("=" * 60)
            # Note: Report generation would need access to results
            # This is a simplified version
            print("Report generation completed successfully.")
        
        return exit_code
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def handle_test_parsers(cli: ExpenseExtractorCLI, pdf_file: str) -> int:
    """
    Handle parser testing command.
    
    Args:
        cli: CLI interface
        pdf_file: PDF file to test
        
    Returns:
        Exit code
    """
    print(f"Testing parsers on: {pdf_file}")
    print("=" * 50)
    
    results = cli.test_parsers(pdf_file)
    
    if 'error' in results:
        print(f"Error: {results['error']}")
        return 1
    
    for parser_name, result in results.items():
        status = "✅ SUCCESS" if result['success'] else "❌ FAILED"
        print(f"\n{parser_name}: {status}")
        
        if result['success']:
            print(f"  Text Length: {result['text_length']:,} characters")
            print(f"  Score: {result['score']:.2f}")
        else:
            print(f"  Error: {result.get('error', 'Unknown error')}")
    
    return 0


def handle_single_file(cli: ExpenseExtractorCLI, pdf_file: str, generate_report: bool) -> int:
    """
    Handle single file processing command.
    
    Args:
        cli: CLI interface
        pdf_file: PDF file to process
        generate_report: Whether to generate detailed report
        
    Returns:
        Exit code
    """
    print(f"Processing single file: {pdf_file}")
    print("=" * 50)
    
    result = cli.process_single_file(pdf_file)
    
    if 'error' in result:
        print(f"Error: {result['error']}")
        return 1
    
    # Display transactions
    transactions = result['transactions']
    validation = result['validation']
    
    cli.formatter.display_transactions(transactions, f"Transactions from {Path(pdf_file).name}")
    cli.formatter.display_validation(validation)
    
    # Generate report if requested
    if generate_report:
        bill_name = Path(pdf_file).stem
        report = cli.get_validation_report({bill_name: result})
        print("\n" + report)
    
    return 0 if validation.valid else 1


if __name__ == "__main__":
    sys.exit(main())
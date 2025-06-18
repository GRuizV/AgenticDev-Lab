#!/usr/bin/env python3
"""
PDF Expense Extractor CLI

A command-line tool that extracts expense data from credit card PDF bills using OCR.
Converts PDF pages to images and uses Tesseract OCR to extract text, then parses
the text to identify Date, Description, and Amount for each transaction.

Usage:
    python pdf_expense_extractor.py

Note: Modify the PDF_FILE_PATH variable below to point to your PDF file.
"""

import re
import sys
import os
from pathlib import Path
from typing import List, Tuple, Optional

# =============================================================================
# CONFIGURATION - MODIFY THIS VARIABLE TO POINT TO YOUR PDF FILE
# =============================================================================
PDF_FILE_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'Test PDFs', 'MC - FEB-2025.pdf')
# =============================================================================

try:
    from pdf2image import convert_from_path
    import pytesseract
    from tabulate import tabulate
    
    # Import dependency config with fallback for direct execution
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'config'))
    from dependency_config import TESSERACT_CMD, POPPLER_PATH
    
    # Configure Tesseract path
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD
    print(f"✓ Tesseract configured: {TESSERACT_CMD}")
    print(f"✓ Poppler configured: {POPPLER_PATH}")
    
except ImportError as e:
    print(f"Error: Missing required dependency - {e}")
    print("Please install dependencies with: pip install -r requirements.txt")
    sys.exit(1)


class ExpenseExtractor:
    """
    Main class for extracting expense data from PDF credit card statements.
    """
    
    def __init__(self):
        """Initialize the expense extractor."""
        self.expenses = []
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Convert PDF to images and extract text using OCR.
        
        Args:
            pdf_path (str): Path to the PDF file
            
        Returns:
            str: Extracted text from all pages
            
        Raises:
            FileNotFoundError: If PDF file doesn't exist
            Exception: If PDF conversion or OCR fails
        """
        if not Path(pdf_path).exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        try:
            print(f"Converting PDF to images: {pdf_path}")
            # Convert PDF pages to images using configured Poppler path
            images = convert_from_path(pdf_path, poppler_path=POPPLER_PATH)
            
            extracted_text = ""
            print(f"Processing {len(images)} page(s) with OCR...")
            
            # Extract text from each page using OCR
            for i, image in enumerate(images, 1):
                print(f"  Processing page {i}/{len(images)}")
                page_text = pytesseract.image_to_string(image, lang='eng')
                extracted_text += page_text + "\n"
            
            return extracted_text
            
        except Exception as e:
            raise Exception(f"Failed to extract text from PDF: {str(e)}")
    
    def parse_expense_line(self, line: str) -> Optional[Tuple[str, str, str]]:
        """
        Parse a single line to extract expense data.
        
        Expected format example:
        "4290 21 04 25 HOMECENTER VTAS A DIST BOGOTA 25.61 $704,700.00 $704,700.00 $0.00 01 01 00"
        
        Args:
            line (str): Text line to parse
            
        Returns:
            Optional[Tuple[str, str, str]]: (date, description, amount) or None if no match
        """
        # Remove extra whitespace and normalize the line
        line = ' '.join(line.split())
        
        # Pattern to match date: first occurrence of DD MM YY format
        date_pattern = r'\b(\d{2}\s+\d{2}\s+\d{2})\b'
        date_match = re.search(date_pattern, line)
        
        if not date_match:
            return None
        
        date = date_match.group(1).replace(' ', '/')  # Convert to DD/MM/YY format
        date_end_pos = date_match.end()
        
        # Pattern to match Colombian peso amounts: $XXX,XXX.XX format
        amount_pattern = r'\$[\d,]+\.?\d*'
        amount_matches = re.findall(amount_pattern, line[date_end_pos:])
        
        if not amount_matches:
            return None
        
        # Take the first amount found (usually the transaction amount)
        amount = amount_matches[0]
        
        # Find the position of the first amount to determine description boundaries
        amount_start_pos = line.find(amount, date_end_pos)
        
        if amount_start_pos == -1:
            return None
        
        # Extract description between date and amount
        description_text = line[date_end_pos:amount_start_pos].strip()
        
        # Clean up description: remove extra numbers and common prefixes
        # Remove leading numbers that might be card numbers or reference codes
        description_text = re.sub(r'^\d+\s*', '', description_text)
        
        # Remove trailing decimal numbers that might be exchange rates or other data
        description_text = re.sub(r'\s+\d+\.\d+\s*$', '', description_text)
        
        # Clean up extra whitespace
        description_text = ' '.join(description_text.split())
        
        if not description_text:
            return None
        
        return (date, description_text, amount)
    
    def extract_expenses(self, text: str) -> List[Tuple[str, str, str]]:
        """
        Extract all expense entries from the OCR text.
        
        Args:
            text (str): OCR extracted text from PDF
            
        Returns:
            List[Tuple[str, str, str]]: List of (date, description, amount) tuples
        """
        expenses = []
        lines = text.split('\n')
        
        print(f"Analyzing {len(lines)} lines for expense data...")
        
        for line_num, line in enumerate(lines, 1):
            # Skip empty lines and lines that are too short
            if len(line.strip()) < 20:
                continue
            
            expense = self.parse_expense_line(line)
            if expense:
                expenses.append(expense)
                print(f"  Found expense on line {line_num}: {expense[0]} | {expense[1][:30]}... | {expense[2]}")
        
        return expenses
    
    def display_expenses(self, expenses: List[Tuple[str, str, str]]) -> None:
        """
        Display expenses in a formatted table.
        
        Args:
            expenses (List[Tuple[str, str, str]]): List of expense tuples
        """
        if not expenses:
            print("\nNo expenses found in the PDF.")
            return
        
        print(f"\n{'='*80}")
        print(f"EXTRACTED EXPENSES ({len(expenses)} transactions found)")
        print(f"{'='*80}")
        
        # Prepare data for tabulation
        headers = ["Date", "Description", "Amount"]
        table_data = []
        
        for date, description, amount in expenses:
            # Truncate long descriptions for better table formatting
            if len(description) > 50:
                description = description[:47] + "..."
            table_data.append([date, description, amount])
        
        # Display table using tabulate
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
        
        # Calculate and display summary
        total_amount = 0
        for _, _, amount in expenses:
            # Extract numeric value from amount string for calculation
            numeric_amount = re.sub(r'[^\d,.]', '', amount)
            numeric_amount = numeric_amount.replace(',', '')
            try:
                total_amount += float(numeric_amount)
            except ValueError:
                pass  # Skip if amount can't be converted
        
        print(f"\nSUMMARY:")
        print(f"Total Transactions: {len(expenses)}")
        print(f"Total Amount: ${total_amount:,.2f}")
    
    def process_pdf(self, pdf_path: str) -> None:
        """
        Main processing function that orchestrates the entire extraction workflow.
        
        Args:
            pdf_path (str): Path to the PDF file to process
        """
        try:
            # Step 1: Extract text from PDF using OCR
            text = self.extract_text_from_pdf(pdf_path)
            
            # Step 2: Parse expenses from extracted text
            expenses = self.extract_expenses(text)
            
            # Step 3: Display results
            self.display_expenses(expenses)
            
        except FileNotFoundError as e:
            print(f"Error: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"Error processing PDF: {e}")
            sys.exit(1)


def main():
    """
    Main CLI entry point.
    """
    print("PDF Expense Extractor v1.0.0")
    print("=" * 40)
    print(f"Processing PDF: {PDF_FILE_PATH}")
    print()
    
    # Validate PDF file extension
    if not PDF_FILE_PATH.lower().endswith('.pdf'):
        print("Error: PDF_FILE_PATH must point to a PDF file (*.pdf)")
        print(f"Current value: {PDF_FILE_PATH}")
        print("Please modify the PDF_FILE_PATH variable at the top of this script.")
        sys.exit(1)
    
    # Initialize extractor and process the PDF
    extractor = ExpenseExtractor()
    extractor.process_pdf(PDF_FILE_PATH)


if __name__ == "__main__":
    main()
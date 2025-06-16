#!/usr/bin/env python3
"""
PDF Credit Card Expense Extractor

A standalone CLI application that extracts credit card expenses from PDF files.
Parses expense lines and displays them in a clean table format.

Author: Roo Assistant
Date: 2025-06-16
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple, Optional


try:
    import pdfplumber

except ImportError:
    print("Error: pdfplumber is not installed. Please install it with: pip install pdfplumber")
    sys.exit(1)


try:
    from tabulate import tabulate

except ImportError:
    print("Error: tabulate is not installed. Please install it with: pip install tabulate")
    sys.exit(1)


class PDFExpenseExtractor:
    """
    A class to extract credit card expenses from PDF files.
    
    This class handles PDF text extraction and parsing of expense lines
    with the format: "4290 21 04 25 HOMECENTER VTAS A DIST BOGOTA 25.61 $704,700.00 $704,700.00 $0.00 01 01 00"
    """
    
    def __init__(self, pdf_path: str):
        """
        Initialize the extractor with a PDF file path.
        
        Args:
            pdf_path (str): Path to the PDF file to process
        """
        self.pdf_path = Path(pdf_path)
        self.expenses = []
        
        # Regex patterns for parsing expense lines
        self.date_pattern = r'\b(\d{2} \d{2} \d{2})\b'  # DD MM YY format
        self.amount_pattern = r'\$[\d,]+\.?\d*'  # Colombian Peso format with $ and commas
        
    def validate_pdf_file(self) -> bool:
        """
        Validate that the PDF file exists and is readable.
        
        Returns:
            bool: True if file is valid, False otherwise
        """
        if not self.pdf_path.exists():
            print(f"Error: PDF file not found at {self.pdf_path}")
            return False
            
        if not self.pdf_path.is_file():
            print(f"Error: {self.pdf_path} is not a file")
            return False
            
        if self.pdf_path.suffix.lower() != '.pdf':
            print(f"Error: {self.pdf_path} is not a PDF file")
            return False
            
        return True
    
    def extract_text_from_pdf(self) -> str:
        """
        Extract all text content from the PDF file.
        
        Returns:
            str: Extracted text content from all pages
        """
        
        try:

            full_text = ""

            with pdfplumber.open(self.pdf_path) as pdf:
                print(f"Processing PDF with {len(pdf.pages)} pages...")
                
                for page_num, page in enumerate(pdf.pages, 1):

                    page_text = page.extract_text()

                    if page_text:
                        full_text += page_text + "\n"
                        print(f"Extracted text from page {page_num}")

                    else:
                        print(f"Warning: No text found on page {page_num}")
                        
            return full_text
            
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            return ""
    
    def parse_expense_line(self, line: str) -> Optional[Tuple[str, str, str]]:

        """
        Parse a single expense line to extract date, description, and amount.
        
        Args:
            line (str): The expense line to parse
            
        Returns:
            Optional[Tuple[str, str, str]]: (date, description, amount) or None if parsing fails
        """
        # Find the first date pattern (DD MM YY format)
        date_match = re.search(self.date_pattern, line)

        if not date_match:
            return None
            
        date = date_match.group(1)
        date_end_pos = date_match.end()
        
        # Find the first amount pattern (Colombian Peso format)
        amount_match = re.search(self.amount_pattern, line)
        if not amount_match:
            return None
            
        amount = amount_match.group(0)
        amount_start_pos = amount_match.start()
        
        # Extract description as the longest alphanumeric block between date and amount
        description_text = line[date_end_pos:amount_start_pos].strip()
        
        # Find the longest alphanumeric sequence in the description area
        # This regex finds sequences of letters, numbers, and spaces
        alphanumeric_blocks = re.findall(r'[A-Za-z0-9\s]+', description_text)
        
        if alphanumeric_blocks:
            # Get the longest block and clean it up
            description = max(alphanumeric_blocks, key=len).strip()
            # Remove extra whitespace
            description = re.sub(r'\s+', ' ', description)
        else:
            description = "Unknown"
            
        return (date, description, amount)
    
    def extract_expenses(self) -> List[Tuple[str, str, str]]:
        """
        Extract all expenses from the PDF file.
        
        Returns:
            List[Tuple[str, str, str]]: List of (date, description, amount) tuples
        """
        if not self.validate_pdf_file():
            return []
            
        print(f"Extracting expenses from: {self.pdf_path}")
        
        # Extract text from PDF
        pdf_text = self.extract_text_from_pdf()
        if not pdf_text:
            print("No text could be extracted from the PDF")
            return []
            
        # Split text into lines for processing
        lines = pdf_text.split('\n')
        expenses = []
        
        print(f"Processing {len(lines)} lines of text...")
        
        # Process each line to find expense entries
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue
                
            # Try to parse the line as an expense
            expense = self.parse_expense_line(line)
            if expense:
                expenses.append(expense)
                print(f"Found expense on line {line_num}: {expense[1][:30]}...")
                
        self.expenses = expenses
        return expenses
    
    def display_expenses(self) -> None:
        """
        Display the extracted expenses in a clean table format.
        """
        if not self.expenses:
            print("No expenses found in the PDF file.")
            return
            
        print(f"\n{'='*60}")
        print(f"EXTRACTED CREDIT CARD EXPENSES")
        print(f"{'='*60}")
        print(f"Total expenses found: {len(self.expenses)}")
        print(f"{'='*60}\n")
        
        # Prepare data for tabulation
        headers = ["Date", "Description", "Amount"]
        table_data = []
        
        for date, description, amount in self.expenses:
            # Format date for better readability (DD/MM/YY)
            formatted_date = date.replace(' ', '/')
            
            # Truncate long descriptions for table display
            if len(description) > 40:
                display_description = description[:37] + "..."
            else:
                display_description = description
                
            table_data.append([formatted_date, display_description, amount])
        
        # Display the table using tabulate
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
        
        # Display summary statistics
        print(f"\n{'='*60}")
        print(f"SUMMARY")
        print(f"{'='*60}")
        print(f"Total transactions: {len(self.expenses)}")
        
        # Calculate total amount (remove $ and commas, then sum)
        try:
            total_amount = 0
            for _, _, amount in self.expenses:
                # Remove $ and commas, then convert to float
                clean_amount = amount.replace('$', '').replace(',', '')
                total_amount += float(clean_amount)
            
            print(f"Total amount: ${total_amount:,.2f}")
        except ValueError:
            print("Could not calculate total amount due to formatting issues")


def main():
    """
    Main function to run the PDF expense extractor CLI application.
    """
    print("PDF Credit Card Expense Extractor")
    print("=" * 40)
    
    # Hardcoded PDF path (placeholder - user will provide actual path)
    # TODO: Replace this with the actual PDF file path
    pdf_path = r"C:\Users\USUARIO\OneDrive\Nima Cloud\02 Desarrollo de Producto\PBA\POCs\LLM interpreta Extractos\Extractos\AvVillas\Visa\VS - ABR-2025.pdf"
    
    # For testing purposes, you can uncomment and modify this line:
    # pdf_path = input("Enter the path to your PDF file: ").strip()
    
    # Create extractor instance
    extractor = PDFExpenseExtractor(pdf_path)
    
    # Extract expenses from the PDF
    expenses = extractor.extract_expenses()
    
    # Display the results
    extractor.display_expenses()
    
    if expenses:
        print(f"\nExtraction completed successfully!")
        print(f"Found {len(expenses)} expense entries.")
    else:
        print("\nNo expenses were found in the PDF file.")
        print("Please check that the PDF contains the expected expense format.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)
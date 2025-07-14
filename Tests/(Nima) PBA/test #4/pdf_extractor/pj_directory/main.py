#!/usr/bin/env python3
"""
Main entry point for PDF Credit Card Expense Extractor CLI.
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from pdf_extractor.cli.main import main

if __name__ == "__main__":
    sys.exit(main())
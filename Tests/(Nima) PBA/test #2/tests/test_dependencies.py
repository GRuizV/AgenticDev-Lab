#!/usr/bin/env python3
"""
Test script to diagnose PDF processing dependencies
"""

print("Testing PDF processing dependencies...")
print("=" * 50)

# Test 1: Import dependencies
print("\n1. Testing Python package imports:")
try:
    import pdf2image
    print("✓ pdf2image imported successfully")
except ImportError as e:
    print(f"✗ pdf2image import failed: {e}")

try:
    import pytesseract
    print("✓ pytesseract imported successfully")
except ImportError as e:
    print(f"✗ pytesseract import failed: {e}")

try:
    from tabulate import tabulate
    print("✓ tabulate imported successfully")
except ImportError as e:
    print(f"✗ tabulate import failed: {e}")

# Test 2: Test pdf2image functionality
print("\n2. Testing pdf2image functionality:")
try:
    from pdf2image import convert_from_path
    # Try to get page count from a dummy call to trigger poppler check
    print("Attempting to test pdf2image with convert_from_path...")
    # This should fail with the poppler error
    convert_from_path("dummy.pdf")
except FileNotFoundError:
    print("✓ pdf2image works (FileNotFoundError expected for dummy file)")
except Exception as e:
    print(f"✗ pdf2image error: {e}")

# Test 3: Test pytesseract functionality  
print("\n3. Testing pytesseract functionality:")
try:
    import pytesseract
    # Try to get tesseract version
    version = pytesseract.get_tesseract_version()
    print(f"✓ Tesseract version: {version}")
except Exception as e:
    print(f"✗ Tesseract error: {e}")

print("\n" + "=" * 50)
print("Dependency test complete.")
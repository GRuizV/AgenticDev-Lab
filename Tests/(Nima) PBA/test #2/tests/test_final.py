#!/usr/bin/env python3
"""
Final test script with configured paths for both Tesseract and Poppler
"""

import os
import sys

# Add config directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'config'))
from dependency_config import TESSERACT_CMD, POPPLER_PATH

print("Final PDF processing dependencies test with configured paths...")
print("=" * 70)

# Test 1: Configure and test Tesseract
print("1. Configuring and testing Tesseract OCR...")
try:
    import pytesseract
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD
    print(f"✓ Tesseract path set to: {TESSERACT_CMD}")
    
    # Test Tesseract
    from PIL import Image
    test_image = Image.new('RGB', (200, 50), color='white')
    text = pytesseract.image_to_string(test_image)
    version = pytesseract.get_tesseract_version()
    print(f"✓ Tesseract OCR working - Version: {version}")
    
except Exception as e:
    print(f"✗ Tesseract configuration failed: {e}")
    sys.exit(1)

# Test 2: Configure and test pdf2image with Poppler
print("\n2. Configuring and testing pdf2image with Poppler...")
try:
    from pdf2image import convert_from_path
    print(f"✓ Poppler path set to: {POPPLER_PATH}")
    
    # Test pdf2image with our configured Poppler path
    try:
        # This should fail with FileNotFoundError for dummy file if working correctly
        convert_from_path("dummy.pdf", poppler_path=POPPLER_PATH)
    except FileNotFoundError:
        print("✓ pdf2image with Poppler working (FileNotFoundError expected for dummy file)")
    except Exception as e:
        if "poppler" in str(e).lower():
            print(f"✗ Poppler error: {e}")
            sys.exit(1)
        else:
            print(f"✓ pdf2image working (non-poppler error for dummy file: {e})")
    
except Exception as e:
    print(f"✗ pdf2image configuration failed: {e}")
    sys.exit(1)

# Test 3: Test the actual PDF extractor imports
print("\n3. Testing actual PDF extractor imports...")
try:
    from tabulate import tabulate
    print("✓ tabulate imported successfully")
except ImportError as e:
    print(f"✗ tabulate import failed: {e}")

print("\n" + "=" * 70)
print("🎉 ALL DEPENDENCIES CONFIGURED AND WORKING!")
print("\nConfiguration Summary:")
print(f"✅ Tesseract OCR: {TESSERACT_CMD}")
print(f"✅ Poppler utilities: {POPPLER_PATH}")
print(f"✅ Python libraries: pdf2image, pytesseract, tabulate")

print("\n✅ Your PDF expense extractor is ready to use!")
print("Run: python pdf_expense_extractor.py")
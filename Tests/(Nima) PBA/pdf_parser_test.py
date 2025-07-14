import pdfplumber

doc_path = r"C:\Users\USUARIO\GR\Software Development\Agentic Dev\Tests\(Nima) PBA\Test PDFs\base_6\AV - MC - 04 - ABR-2025.pdf"

with pdfplumber.open(doc_path) as pdf:

    first_page = pdf.pages[0]
    text = first_page.extract_text()
    print(text)
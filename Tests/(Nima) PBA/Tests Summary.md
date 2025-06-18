# Tests Summary

## Test #1
    
- **Purpose**: Validate feasibility of extracting expenses from a structured PDF using a Python CLI app.

- **Input**: Text-based credit card PDF from a known issuer (sample format controlled).

- **Extraction target**: 

    * Date in DD MM YY format (e.g., 21 04 25)
    * Description (e.g., HOMECENTER VTAS A DIST BOGOTA)
    * Amount in COP format with $ and commas (e.g., $704,700.00)

- **Expected output**: CLI table listing one row per expense with the extracted fields.

- **Scope**: No categorization, export, or inference logic — just raw extraction and tabular display.

- **Results**: The parser worked flawlessly with controlled input using ´pdfplumber´. Expense lines were accurately identified, and extracted fields were correctly placed in a clean CLI table. Regex-based pattern matching proved reliable, and the code was modular, well-documented, and resilient to edge cases. Overall, this validated the parser’s baseline performance under ideal conditions.




## Test #2

- **Purpose**: Validate feasibility of extracting expenses using OCR from a scanned or image-based PDF with a Python CLI app.

- **Input**: Image-based credit card PDF from a known issuer, converted via pdf2image.

- **Extraction target**: 

    * Date in DD MM YY format (e.g., 21 04 25)
    * Description (e.g., HOMECENTER VTAS A DIST BOGOTA)
    * Amount in COP format with $ and commas (e.g., $704,700.00)

- **Expected output**: CLI table listing one row per expense with the extracted fields.

- **Scope**: No categorization, export, or inference logic — just raw extraction and tabular display.

- **Results**: The app successfully extracted data using OCR, but with reduced accuracy compared to the text-based version. Some expense lines were misaligned due to OCR errors (e.g., missing spaces or distorted characters), requiring extra tolerance in the parsing logic. Still, key values (date and amount) were often recoverable. Overall, the test confirmed that OCR is viable but less reliable unless input quality is high or post-processing is added.













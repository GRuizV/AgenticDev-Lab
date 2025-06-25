# Tests Summary

## Test #0

- **Purpose**: Compare the extraction accuracy of three LLMs (ChatGPT, Claude, Gemini) when processing credit card PDFs using structured prompts.

- **Input**: Six credit card PDF statements (MC & VS, Feb–Apr 2025) with a verified ground truth of 57 transactions worth $5,120,378 COP.

- **Extraction target**:

    * Date (in normalized format)
    * Description (free-text normalized)
    * Amount (in COP, integer value with ±5 peso tolerance)

- **Expected output**: JSON with a `bill_name` field and a `transactions` array containing structured transaction data.

- **Scope**: Manual prompt-based testing of LLMs through web interfaces — no automation or inference logic in this phase.

- **Results**: All models performed well on simple MasterCard statements. Claude ranked first overall with 93.8% precision and 78.9% recall. ChatGPT followed closely. Gemini showed inconsistent results, completely failing to extract from one complex Visa statement. The evaluation framework successfully quantified extraction quality and revealed key differences in robustness and reliability across model families.




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




## Test #3

- **Purpose**: Evaluate Roo’s ability to autonomously infer PDF structure and extract expenses without any predefined parsing logic or tool constraints.

- **Input**: Text-based credit card PDFs from a known issuer, with consistent format but no hints provided.

- **Extraction target**:

    * Date in DD MM YY format (e.g., 10 02 25)
    * Description (e.g., SMART FIT METROPOLIS BOGOTA DC)
    * Amount in COP format with $ and commas (e.g., $79,900.00)

- **Expected output**: CLI table listing one row per expense with the extracted fields.

- **Scope**: Roo must select the PDF parser, infer the structure of expense lines, choose the correct amount among multiple, and match both the total amount and number of transactions per file using ground truth as validation.

- **Results**: TBD.








# 📓 Project Logbook

**Personal Billing Assistant (PBA)**  
This log tracks findings, decisions, and technical reasoning made throughout the development of the PBA system. It complements the README and serves as a memory anchor for both humans and LLM agents.

---

## June

### 📅 [2025-06-03] – Initial Architecture Defined

**Context:** Explored initial feasibility of parsing PDF bills for personal expense tracking.

**Action Taken:**  
- Drafted first architecture diagram (`docs/architecture/2025.06.03 - Draft de Arquitectura.drawio.xml`)
- Defined high-level components: ingestion, parsing, DB, notification, LLM interface


### 📅 [2025-06-04] – Ground Truth Established

**Context:** Needed a reliable way to verify Textract output accuracy.

**Action Taken:**  
- Manually extracted expected tables from multiple PDFs into Excel and JSON
- Created `data/ground_truth.json` and `ground truth total.md`

---

## July

### 📅 [2025-07-17] – Chose Amazon Textract Over Other OCR Engines

**Context:** Tested multiple tools to extract structured tables from complex PDFs.

**Options Considered:**
- Amazon Textract
- Tesseract + Pandas
- LayoutParser + PDFMiner

**Decision:** Amazon Textract (`analyzeDocument` endpoint)

**Rationale:**
- High table fidelity
- Robust against multi-column bank statements
- Native AWS integration for future Lambda triggers


### 📅 [2025-07-18] – Finalized Project Structure & Defined Dev Plan and LLM Strategy

**Context:** 
- Repo had grown organically during PoCs and needed restructuring.
- Prepared for full pipeline buildout.

**Action Taken:**
- Moved all PoCs into `experiments/`
- Created modular `src/` structure for production logic
- Created `tests/`, `docs/`, `data/`, and `config/` folders
- Created `PBA_Development_Plan.md` for phased implementation
- Confirmed WhatsApp + LLM interface as end-user layer (no frontend)
- Documented LLM expectations and interaction patterns in `PROJECT_OVERVIEW.md`


### 📅 [2025-07-22] – Switched to Async Textract API for PDF Compatibility

**Context:**  
Encountered `UnsupportedDocumentException` when calling `analyze_document()` on PDF files stored in S3.

**Investigation Outcome:**  
- AWS Textract requires the **async API (`start_document_analysis`)** for PDFs and TIFFs in S3.
- The synchronous `analyze_document()` only works with images (JPEG, PNG) passed via byte streams.
- The same document succeeded via AWS Console, confirming the format was valid.

**Action Taken:**  
- Rewrote `trigger_textract.py` to use the async API.
- Implemented polling loop with `get_document_analysis()`.
- Problem resolved and raw Textract output now retrieved as JSON.

### 📅 [2025-07-23] – Template Adapter System & Extended Transformer for Bancolombia Bills

**Context:**  
The expense extraction process initially focused on simple row normalization, assuming a stable and known bill structure.  
However:
- Different card issuers (and even updates from the same issuer) may change the structure of credit card statements.
- Bancolombia bills, while consistent now, cannot be guaranteed to keep the same format long-term.
- Bills often include payments, adjustments, and installment information that impact totals and must be handled correctly.

**Decisions:**  
- Introduced an **adapter-based transformer** using a JSON configuration file (`bill_templates.json`) to define:
  - Header patterns for table detection
  - Currency split rules (foreign (USD) vs domestic (COP))
  - Fields to extract and normalize
  - Excluded descriptions (e.g., `"ABONO SUCURSAL VIRTUAL"`) since it belongs to payments and those won't be part of this Use Case.
- Added a flexible architecture so that future card issuers or new Bancolombia templates can be supported by **adding/updating a config entry** instead of rewriting core logic.
- Extended `extract_expenses.py` logic to:
  - Use table-specific currency detection (scan rows until one record provides criteria match).
  - Filter out only specific payment rows (`ABONO SUCURSAL VIRTUAL`) while retaining all other adjustments (negative values preserved as negative floats).
  - Keep the `Cuotas` (installments) field as strings instead of converting to integers, since values like `"1/1"`, `"2/5"`, `"10/36"` indicate pending installments and are relevant for reporting as-is.
- Updated the template configuration file structure to be nested under `"bill_templates"` to prepare for future configuration extensions beyond billing templates.

**Outcomes:**  
- **Extensible extraction pipeline:** Core logic is now isolated from issuer-specific details.
- **Correct financial handling:** Adjustments and negatives are preserved, payments are excluded properly, and currency classification works without unnecessary full-row scanning.
- **Future-proofing:** Any future change in Bancolombia’s bill template or adding new issuers requires only config changes, not code rewrites.
- **DB-readiness:** Normalized record structure is consistent and ready for mapping into database schemas when that step arrives.

**Notes & Learnings:**  
- Bills contain payment and adjustment records that behave differently:
  - `"ABONO SUCURSAL VIRTUAL"` payments are excluded as they don’t affect expense analysis.
  - Other adjustments (negative values) are included, as excluding them causes totals to mismatch actual statements.
- Currency detection no longer requires scanning every row; scanning until one record matches criteria is sufficient since Bancolombia never mixes currencies in a single table.
- Template file naming and nesting (`bill_templates.json` under `bill_templates` key) improves long-term maintainability and separates future configurations.
- Although installments could be converted into pending counts (`"1/1" → 0 pending"`, `"2/5" → 3 pending"`), they are kept as raw strings for now to preserve full reporting context.

---

# 📌 PBA – Personal Billing Assistant
## Development Plan & Milestones

---

## ✅ Phase 0: Groundwork & Environment

- [x] Define architecture and core scope
- [x] Choose Textract as parsing engine
- [x] Complete PoCs and tool comparisons
- [x] Organize repo into production-grade structure
- [x] Setup virtual environment and dependency tracking (`requirements.txt`)
- [x] Ensure `.env` / secrets config is safely gitignored

---

## 🧩 Phase 1: Core PDF → DB Flow

### Objective: Upload → Textract → Parse → Store

#### Tasks
- [x] Implement `src/ingestion/upload_to_s3.py`
- [x] Implement `src/textract/trigger_textract.py`
- [x] Build `src/textract/parse_textract_output.py`
- [x] Write transformer: `src/core/extract_expenses.py` to select and clean the relevant tables.
- [ ] Implement DB insert logic in `src/db/store_expenses.py` 🔜
- [ ] Build orchestration script: `main_extract_and_store.py`

#### Validation
- [ ] Build tests under `tests/test_parser.py` and `test_store.py`
- [ ] Store outputs and logs for 3 known PDFs (ground truth validated)

---

## 📊 Phase 2: Report Generator

### Objective: Aggregate data into coherent monthly reports

#### Tasks
- [ ] Build `src/core/monthly_report.py` that summarizes expenses per user/card/month
- [ ] Include expense type detection (category heuristics if possible)
- [ ] Add CLI output with tabulate

#### Validation
- [ ] Compare monthly reports with `ground_truth.json`
- [ ] Export reports as `.md` or `.csv` for review

---

## 📬 Phase 3: Notifications and Eventing (Optional Pre-LLM)

### Objective: Notify user when a new bill is processed

#### Tasks
- [ ] Create WhatsApp notifier module in `src/notifications/whatsapp.py`
- [ ] Integrate with Lambda trigger logic (or simulate locally)

---

## 🧠 Phase 4: LLM Integration (MVP)

### Objective: Respond to natural queries via WhatsApp

#### Tasks
- [ ] Create prompt builder in `src/llm_interference/prompts.py`
- [ ] Implement question router in `src/llm_interference/qa_handler.py`
- [ ] Use stub/mock LLM first, then integrate with Bedrock

#### Validation
- [ ] Test with 5 fixed user questions against known reports
- [ ] Compare responses to expected answers from `ground_truth total.md`

---

## 🧪 Phase 5: Unified Testing & QA

### Objective: Ensure stability and correctness of the pipeline

#### Tasks
- [ ] Finalize all unit tests
- [ ] Add integration tests for full flow
- [ ] Benchmark against `experiments/` historical outputs

---

## 🚀 Phase 6: Deployment Readiness

- [ ] Containerize with Docker (if needed)
- [ ] Setup GitHub repo with proper README, structure explanation, architecture diagram
- [ ] Add Makefile or CLI helpers for common commands
- [ ] Document usage (dev and user guides in `docs/`)

---

## 🗃️ Appendix

- 📁 Ground truth: `data/ground_truth.json`, `ground truth total.md`
- 📁 Sample PDFs: `data/input_pdfs/`
- 📁 Architecture Docs: `docs/architecture/`
- 📁 Experiments & PoCs: `experiments/`

---
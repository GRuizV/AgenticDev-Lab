# Context Handover System – PBA Project (Model)

## Purpose
Enable smooth transfer of project context between sessions when:
- The active chat session becomes too long or complex (context bloated).
- A new session (or even a different person/agent) needs to pick up where we left off.

This ensures **no loss of historical reasoning** and allows new sessions to quickly hook into the ongoing workflow.

---

## How to Use This Model
1. **When context is bloated:** Trigger a “Context Check”.
2. **If recommended to start fresh:** Create a `handover.md` (or use this template directly in chat).
3. **Gather from the five core documents** (plus optional ones if relevant).
4. **Spawn new session:** Share `handover.md` at the start of the new session.
5. **Resume work** seamlessly.

---

## Core Handover Components

### 1. Project README
**Purpose:** Communicate the big picture.

**Include:**
- What the project is (one paragraph)
- Why it exists (problem being solved)
- High-level architecture (diagram or text)


---

### 2. Project Logbook
**Purpose:** Provide historical decisions and rationale.

**Include:**
- Key decisions made so far (with dates)
- Reasons behind them
- Outcomes of those decisions


---

### 3. Development Plan
**Purpose:** Show where we are in the roadmap.

**Include:**
- Current phase & next planned steps
- Completed tasks (checked)
- Pending tasks (unchecked)


---

### 4. App Directory Map
**Purpose:** Show project structure and key components.

**Include:**
- Project folder structure (tree view)
- For critical modules: 
  - file path
  - functions/classes inside
  - brief description of each function (I/O contract)


Example:
```
    src/
    ├── textract/
    │ ├── trigger_textract.py # Upload to S3, run Textract async, return full JSON
    │ └── parse_textract_output.py # Convert Textract JSON to raw tables (list of lists)
    ├── core/
    │ └── extract_expenses.py # Transform parsed tables → normalized expenses via template
```

---

### 5. Last Session Handover
**Purpose:** Bridge between sessions.

**Include:**
- Last achieved milestone
- Current open issues
- Next steps to execute immediately
- Any pending decisions or experiments

Example:

    *Last Achieved*
    - Implemented pagination in Textract async job → full JSON output.
    - Built and tested adapter-based transformer (bancolombia_v1).

    *Current Open Issues*
    - Need to fine-tune transformer output vs ground truth.
    - Validate precision & recall metrics for extracted expenses.

    *Next Steps*
    - Refine transformer field handling (e.g., date normalization, negative values).
    - Improve test coverage for edge cases.
    - Discuss DB storage format.

    *Pending Decisions*
    - Should Cuotas remain as strings permanently?
    - Should we split template config per issuer?

_You could use the handover template in the context_maintenance directory as well_ 

---

## Optional Components
### Data Contracts
Define input/output format for critical functions (JSON examples, schemas).

### Dependency Snapshot
`requirements.txt` or `poetry.lock` for environment reproducibility.

---

## Workflow Checklist
1. **Before session ends:** Update:
   - Logbook (if decisions were made)
   - Development Plan (if tasks completed)
   - Last Session Handover (snapshot)
2. **Generate Directory Map (if changed)**.
3. **Paste Handover Summary** into the chat when spawning a new session.

---

## Benefits
- Minimal onboarding time for new sessions or contributors
- Avoids rehashing old reasoning
- Reduces errors from context loss
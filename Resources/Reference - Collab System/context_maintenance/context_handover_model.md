# Context Handover System – PBA Project (Model)

## Purpose
Enable smooth transfer of project context between sessions when:
- The active chat session becomes too long or complex (context bloated).
- A new session (or even a different person/agent) needs to pick up where we left off.

This ensures **no loss of historical reasoning** and allows new sessions to quickly hook into the ongoing workflow.



## How to Use This Model
1. **When context is bloated:** Trigger a “Context Check”.
2. **If recommended to start fresh:** Create a `handover.md` (or use the session handover template directly in chat).
3. **Gather from the five core documents** (plus optional ones if relevant).
4. **Spawn new session:** Share `handover.md` at the start of the new session.
5. **Resume work** seamlessly.

---

## Core Handover Components

### 1. Project README
Communicates the big picture:
- What the project is (one paragraph)
- Why it exists (problem being solved)
- High-level architecture (diagram or text)


### 2. Project Logbook
Provides historical decisions and rationale:
- Key decisions made so far (with dates)
- Reasons behind them
- Outcomes of those decisions


### 3. Development Plan
Shows where we are in the roadmap:
- Current phase & next planned steps
- Completed tasks (checked)
- Pending tasks (unchecked)


### 4. App Directory Map
Shows project structure and key components:
- Project folder structure (tree view)
- For critical modules:
  - file path
  - functions/classes inside
  - brief description of each function (I/O contract)

#### Automated Generation
The directory map is generated using **`files_structure_generator_v2.py`**:
- **Location:** `docs/context_maintenance/files_structure_generator_v2.py`
- **Purpose:** Automatically scans the project folder, extracts functions and class signatures, and outputs a Markdown map.
- **Output:** Saved under `docs/context_maintenance/sessions/` as `project_map_YYYYMMDD_HHMMSS.md`

Usage:
```Python
    # Example
    generate_markdown_tree(
    start_path="path/to/project/root",
    output_dir="path/to/context_maintenance/"
    )
```


### 5. Last Session Handover
Bridges between sessions:

- Last achieved milestone
- Current open issues
- Next steps to execute immediately
- Pending decisions or experiments

Template provided in docs/context_maintenance/session_handover_template.md.


### 6. Last Session Handover
To ensure a new AI session (e.g., ChatGPT/GPT‑4o) adopts the correct Development Partner role, a prebuilt initialization prompt is included:

  * Location: docs/context_maintenance/dev_partner_prompt_chatgpt.md

  * Purpose:
    - Sets the AI assistant’s role and behavior expectations.
    - Ensures reproducible onboarding of any new session.

  * Usage:
    Paste the prompt at the start of any new session along with the handover context.

---

## Optional Components

  ### Data Contracts
  Defines input/output formats for critical functions (JSON examples, schemas).

  ### Dependency Snapshot
  requirements.txt or poetry.lock for environment reproducibility.

---

## Workflow Checklist
  
  1. Before session ends, update:
        * Logbook (if decisions were made).
        * Development Plan (if tasks completed).
        * Last Session Handover (snapshot).
  2. Generate Directory Map (if changed) using the structure generator script.
  3. Include Dev Partner Prompt in the new session initialization.
  4. Paste Handover Summary into the chat when spawning a new session.

---


## Benefits

  - Minimal onboarding time for new sessions or contributors.
  - Avoids rehashing old reasoning.
  - Reduces errors from context loss.
  - Automates context preparation (directory map generation).
  - Ensures consistent AI behavior (role prompt for Dev Partner).

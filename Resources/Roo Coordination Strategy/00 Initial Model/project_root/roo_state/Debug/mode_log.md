# 🐞 Debug Log

> This log documents actions and reasoning for the Debug mode.

---

# Mode's Log Example
- date: 2025-07-05
  task: Investigated failing login test
  input_from: Code
  result: Discovered session bug in login handler, test fails for expired token
  next_step: Requested Orchestrator assign fix to Code
  author: Debug
  hash_id: debug_001
--- YAML Example Ends ---

---

# Logging Instructions:
- Always append new entries in YAML list format
- Never delete or overwrite past entries — this log is append-only
- Maintain strict indentation and structure
- `hash_id` format suggestion: [mode_abbr]_[sequential_id], e.g., `orchestrator_001`
- Required fields: `date`, `task`, `input_from`, `result`, `next_step`, `author`, `hash_id`
- Optional: `details:` — use for rationale, links, affected files, etc.


# Modes Log
> Log your entries here.
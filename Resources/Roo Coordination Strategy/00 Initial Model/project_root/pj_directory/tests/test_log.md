# 🧪 Shared Tests Log

This file tracks all test files created or modified inside `pj_directory/tests/`.  
It is shared between Code and Debug agents and documents the reasoning, assumptions, and scope behind each test.  
All entries must be appended in structured YAML format.

---

- date: 2025-07-04
  author: Code
  test_file: test_login_flow.py
  reason: Validate login logic for OAuth
  linked_feature: auth/login.py
  assumptions:
    - User must have active session
    - Backend returns 200 on success
  result: Initial test scaffold added, pending CI run
  next_step: Confirm with Debug and expand edge cases

---

## Logging Instructions
- Append new entries using structured YAML list format.
- Do not overwrite or remove previous entries.
- Fields `test_file`, `reason`, and `linked_feature` are mandatory.
- Use `result` to summarize execution status (e.g. scaffolded, passed, failed).
- Use `next_step` to signal intended actions or handoffs (especially to Debug).


## Test Log
> Log the test log entries here
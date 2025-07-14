# 🚀 Launch Instructions for Roo Project

This file defines the exact sequence to initialize a new Roo-based agentic collaboration project.

---

## 🧱 Setup Steps

0. Rename `project_root/` to your actual project name (e.g. `landing_page_rebuild/`)
1. Create the directory and file scaffold as described in `README.md`
2. Populate each mode in Roo with its corresponding SOPF prompt from `roo_state/templates/`
3. Ensure that `.roo-config.yaml` is correctly placed in `roo_state/` and defines the mode-path bindings
4. Create the following files (if they don’t already exist):
   - `roo_state/project_state.md` (start with the example template)
   - `pj_directory/tests/tests_log.md`
   - Each agent's `mode_log.md` (can include just the example block)
5. Compose your initial human prompt for the Orchestrator (e.g., “We’re building a user onboarding microservice. Assign the first architectural design task.”)

    ### 📌 Important: End that prompt with this instruction:
    _add this to the end of your initial prompt_
    > Begin this project by replacing all template placeholders in `roo_state/project_state.md` with the actual purpose, current active goal, updated task queue, and clarified agents involved. Clean up the example comments if you find them.

---

## 🧪 Result

The system will self-bootstrap, assign its first task, and begin execution through the Orchestrator → Architect → Code/Debug loop.

You now have a running Roo project backed by structured memory and role-based logic.
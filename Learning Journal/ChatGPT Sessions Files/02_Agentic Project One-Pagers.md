# 💧 Phase 1 – Roo CLI Extension: Water Tracker

## 🔍 Problem / Motivation
The initial Water Tracker CLI logs hydration data interactively, but lacks structure, analytics, and persistence. As a learning sandbox, we’ll expand this tool into a small-scale data tracker app using Roo to test realistic CLI planning, persistence, and reporting patterns.

## 🎯 Goal
Incrementally upgrade the CLI app to:
- Persist structured data
- Provide meaningful summaries and daily/weekly feedback
- Export insights in CSV and visual form
- Reinforce Roo agentic workflows on real code

## 📦 Inputs / Artifacts
- `water_tracker.py`: working CLI logger (interactive)
- `water_log.txt`: current flat-text logs (to be migrated)
- Future output: `water_log.json`, `summary.csv`, `chart.png`

## 🪡 Scope of Changes

### ✅ Phase 1 Enhancements (Confirmed)
- **Persist settings (JSON)**: Track user preferences, goals, and config
- **Daily total report**: CLI option to report water consumed on a specific date
- **CSV logging**: Store logs in a clean tabular format (`timestamp`, `amount_ml`, `unit`)

### 🟡 Planned Next Enhancements
- **Daily goal performance report**: Track against a healthy daily target
- **Weekly/monthly summaries**: Total, average, and goal compliance metrics
- **Log review command**: CLI-based explorer for past logs and summaries
- **Plot export**: `.png` chart with daily intake and trend line

## 🧪 Roo Agentic Use
- Guide scaffolding for new features
- Propose function structures and data format strategies
- Modular planning via Boomerang (e.g. phase → doc → implement → summarize)
- Optional: self-documentation of changes via `Documentator` flow later

## 🧭 Learning Objectives
- Apply Roo to extend and maintain an existing CLI app
- Use JSON and CSV persistence strategies
- Build light reporting and visualization logic
- Practice testable micro-increments and agentic refactoring

## 🪜 Next Step
Start with **JSON persistence + CSV export + daily total report** as a Phase 1.1 milestone. Define interfaces, data migration plan, and CLI structure updates.

---

# 🔀 Phase 2 – Git Practice Project

## 🔍 Problem / Motivation
Most version control exposure so far has been limited to pushing final versions to remotes. This project is designed to **master Git locally** — using branching, merging, reverts, and rebases in a real development flow.

## 🎯 Goal
Develop a small but real CLI script with:
- At least 2–3 independent features (each in its own branch)
- Merge conflicts to resolve
- Regret-commits to revert or fix
- Tags or checkpoints for historical testing

## 🧱 Structure
- Base: `main` branch
- Feature branches: `feat/X`, `test/Y`, etc.
- Use tags (`v1.0`, `v2-draft`, etc.)
- Optional: conflict via intentionally diverging code/comments

## 🪡 Example Project Options
- CLI task manager
- Calculator with history/memory
- Note taker
- Dice/stat generator
- Expense logger

## 🧪 Roo Agentic Use
- (Optional) Use Roo to scaffold CLI logic
- Let Roo generate changelogs, conflict explanations, or README diffs
- Use Roo to reason about rollback strategies or rebase flows

## 🧭 Learning Objectives
- Practical Git: branching, merging, rebasing, reverting
- Controlled introduction of code drift and resolution
- Use of tags, logs, and diff history for traceability

## 🪜 Next Step
Pick a simple CLI idea from the list or propose your own. We'll define core feature branches and plan a commit graph.

---

# 🚀 Phase 3 – Real-World Agentic Project

## 🔍 Problem / Motivation
After learning Roo’s foundations and testing microprojects, we now aim to use Roo to manage and assist in building a real application or solution — leveraging **modular orchestration**, persistent summaries, and reusable tools.

## 🎯 Goal
Develop a working agentic app or system with:
- Multiple Roo agents (or task types)
- Long-lived project memory via `.md` or `.json` logs
- Reusable prompt scaffolds (`.roorules-*`)
- Decision logging and delegation

## 🔧 Candidate Domains
- Data tooling (e.g. log analyzers, budget trackers, ETL helpers)
- App scaffolding (CLI, backend, API)
- Automation scripts (report builders, changelog generators)
- ML/AI (prompt testers, annotators, dataset scanners)
- Your own planned real-world tool

## 🪡 Scope (Minimum Viable Agentic App)
- At least 3 phases (e.g. planning → implementation → summarization)
- At least 2 Roo agents (Orchestrator + 1 tool/user mode)
- Outputs real files or meaningful logs
- Modular inputs (e.g. plan files, `.roo` rulebases)

## 🧪 Roo Agentic Use
- Roo acts as builder, analyst, or planner in different steps
- Agents bridge context via summary files
- `.roorules-*` structure isolates prompting logic
- Logs are written by Documentator (if needed)
- Think agent can assist in complex branching points

## 🧭 Learning Objectives
- Orchestrate a complete build cycle with Roo
- Work modularly across tasks using persistence
- Observe where agent design hits limits or excels
- Prepare for applying Roo to professional projects

## 🪜 Next Step
Decide on the real project to build — even a rough idea is enough. Scope first 3 phases (Plan → Scaff → Implement), then define agent setup.
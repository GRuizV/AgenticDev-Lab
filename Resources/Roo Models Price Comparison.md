# Current Models Prices

**Date:** 09/07/25

| Model Name                 | Supports Images | Supports Compute Use | Prompt Caching | Max Output Tokens | Input Price     | Output Price     | Cache Read Price  | Cache Write Price  |
|----------------------------|------------------|-----------------------|----------------|-------------------|------------------|-------------------|--------------------|---------------------|
| claude-sonnet-4  | ✅               | ✅                    | ✅             | 64,000            | $3.00 / 1M tokens | $15.00 / 1M tokens | $0.30 / 1M tokens  | $3.75 / 1M tokens   |
| claude-3.7-sonnet| ✅               | ✅                    | ✅             | 8,192             | $3.00 / 1M tokens | $15.00 / 1M tokens | $0.30 / 1M tokens  | $3.75 / 1M tokens   |
| gemini-2.5-pro      | ✅               | ❌                    | ✅             | 65,536            | $1.25 / 1M tokens | $10.00 / 1M tokens | $0.31 / 1M tokens  | $1.63 / 1M tokens   |
| gemini-2.5-flash    | ✅               | ❌                    | ✅             | 65,535            | $0.30 / 1M tokens | $2.50 / 1M tokens  | $0.08 / 1M tokens  | $0.38 / 1M tokens   |
| gpt-4.1-mini        | ✅               | ❌                    | ❌             | 32,768            | $0.40 / 1M tokens | $1.60 / 1M tokens  | N/A               | N/A                |
| gpt-4.1             | ✅               | ❌                    | ❌             | 32,768            | $2.00 / 1M tokens | $8.00 / 1M tokens  | N/A               | N/A                |
| gpt-4o              | ✅               | ❌                    | ❌             | 16,384            | $2.50 / 1M tokens | $10.00 / 1M tokens | N/A               | N/A                |




## Recomendations

| Roo Mode       | Ideal Models                          | Why Use Them                                               |
|----------------|----------------------------------------|------------------------------------------------------------|
| **Ask**        | `gemini-2.5-flash`, `gpt-4.1-mini`     | Fast, cheap Q&A; no compute or memory needed               |
| **Code**       | `gpt-4.1`, `claude-sonnet-4`           | Code generation, multi-step logic, good with syntax        |
| **Debug**      | `claude-sonnet-4`, `gpt-4.1`           | Good reasoning over code; compare versions, isolate bugs   |
| **Orchestrator** | `claude-sonnet-4`, `gemini-2.5-pro`    | Best for agent routing, planning, JSON reasoning           |
| **Architect**  | `claude-sonnet-4`, `gpt-4.1`           | System design, structured output, documentation tasks      |



Keep all models with compute + caching for:

- Orchestrator
- Architect
- Debug
- Coding

Use flash/minis only in Ask, optionally as fallbacks elsewhere.
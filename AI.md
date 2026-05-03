# AI Usage Disclosure

## Overview

The vast majority of this project was built using **Copilot CLI** (terminal-based AI agent) running **Claude Opus 4.6 / GPT 5.5** as the underlying model. A small amount of initial project planning used **Gemini 3 Pro** via Antigravity. Everything done in PowerBI was done manually with **no AI assistance**.

| Tool                       | Model           | Used For                                                             |
| -------------------------- | --------------- | -------------------------------------------------------------------- |
| Copilot CLI                | Claude Opus 4.6 | ETL pipeline code, documentation, diagrams, validation, git workflow |
| Gemini 3 Pro (Antigravity) | Gemini 3 Pro    | Initial project plan generation (Week 1)                             |

---

## How Copilot CLI Was Used

### What It Is

Copilot CLI is an interactive terminal agent that can read files, write code, run commands, search the codebase, and execute multi-step workflows autonomously. It operates directly in the project directory with full access to the file system, Python environment, and Git.

### Configuration

The agent was configured with project-specific context and workflows:

- **`.github/copilot-instructions.md`** — Project context, architecture overview, ETL conventions, code style rules, and Git workflow guidelines. This file tells the agent what the project is about, where files live, and how to work.

- **`.github/skills/`** — Three custom skill files that define repeatable workflows:
  - **`weekly-workflow`** — Phased approach for each week: scope → plan → implement → deliver. The agent reads the project plan, audits the codebase, creates a structured plan, then implements with atomic commits.
  - **`git-workflow`** — Enforces branching model (feature branches → PRs → main), conventional commit messages, and commit granularity rules.
  - **`visuals`** — Enforces Excalidraw as the sole diagramming tool with specific export workflows.

### MCP Integrations

Copilot CLI used several MCP (Model Context Protocol) servers:

- **GitHub MCP** — Creating branches, opening PRs, merging PRs, checking commit history, all through the `gh` CLI and GitHub API.
- **Excalidraw MCP** — Creating diagrams programmatically (star-schema model, dashboard wireframe) and exporting to SVG/PNG.

### Typical Workflow

A typical week of work followed this pattern:

1. **User prompt**: "Do week N" (with the `weekly-workflow` skill invoked).
2. **Scoping**: Agent reads the project plan, business docs, and existing code to understand what needs to be built.
3. **Planning**: Agent produces a structured plan with todos, dependency ordering, and commit strategy. User reviews and approves.
4. **Implementation**: Agent writes all code (OOP Python classes), creates files, runs the pipeline to verify, and fixes any errors.
5. **Commits**: Agent makes atomic commits following conventional commit format (e.g., `feat(etl): add certifications silver cleaner`).
6. **PR workflow**: Agent pushes the feature branch, opens a PR with a descriptive body, and merges after user approval.

### What the Agent Did vs. What I Did

| Agent Responsibility                                       | My Responsibility                          |
| ---------------------------------------------------------- | ------------------------------------------ |
| Write all Python code (OOP classes, pipeline logic)        | Review plans before approving              |
| Design data cleaning rules based on exploration findings   | Provide high-level direction ("do week N") |
| Create documentation (data exploration, dimensional model) | Validate outputs make sense                |
| Run and debug the pipeline                                 | Make architectural decisions when asked    |
| Create Excalidraw diagrams                                 | Build the Power BI dashboard (manual)      |
| Handle Git workflow (branches, commits, PRs)               | Merge approval                             |

---

## Per-Phase AI Usage

### Phase 1: Planning & Design (Weeks 1–3)

**Week 1** — Gemini 3 Pro generated the initial project plan (`pm/r0984834_ProjectPlan.md`) from the assignment slides. Copilot CLI was not yet used.

**Week 2** — Copilot CLI profiled all 11 raw Excel files, creating `src/profiling/data_profiler.py` (OOP `DataProfiler` class) and generating `docs/week2_data_exploration.md` with column analysis, duplicate detection, and cross-file referential integrity findings.

**Week 3** — Copilot CLI designed the star schema, validated dimension cardinalities via Python notebooks, created `docs/dimensional_model.md`, and built the Excalidraw star-schema diagram exported as `docs/r0984834_Model.png`.

### Phase 2: ETL Development (Weeks 4–7)

This phase was built entirely by Copilot CLI following the medallion architecture:

**Week 4 (Bronze)** — Created `src/bronze/` package: `BaseExtractor` ABC + 3 concrete extractors (Certifications, Clubs, Results). Reads 11 Excel files into standardized DataFrames with snake_case columns.

**Week 5 (Silver)** — Created `src/silver/` package: `BaseCleaner` ABC + 3 concrete cleaners. Handles sentinel DOB replacement, country/province normalization (14 Belgium variants → 1), gender standardization (Male→M), place/score parsing (96.5% success rate), and multi-round deduplication (112K → 72K rows).

**Week 6 (Gold)** — Created `src/gold/` package: `BaseTransformer` ABC + 7 concrete transformers producing the star schema (5 dimensions + 2 facts). Includes fuzzy club name matching via `rapidfuzz` (87% match rate) and medal derivation.

**Week 7 (Validation)** — Created `src/quality/`: `OutputValidator` class running 68 automated checks (file existence, column schemas, row counts, FK integrity, null constraints, data value ranges, surrogate key uniqueness). All 68 pass.

### Phase 3: Dashboarding (Weeks 8–11)

**Week 8** — Copilot CLI designed the dashboard wireframe (`docs/r0984834_Wireframe.png`) using Excalidraw MCP: 4-page layout covering Overview, Demographics, Performance, and Regional analysis.

**Weeks 9–11** — Power BI dashboard building is done manually (no SDK exists for programmatic visual layout creation).

### Phase 4: Finalizing (Weeks 12–13)

**Week 12** — Copilot CLI re-ran the uv-backed ETL pipeline for reproducibility, documented the final validation results, summarized data-model assumptions, and added a rubric-aligned self-evaluation.

---

## Code Attribution

Every commit authored by the AI agent includes the trailer:

```
Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
```

This is automatically appended to all commits made during Copilot CLI sessions.

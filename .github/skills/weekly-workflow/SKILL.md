---
name: weekly-workflow
description: Defines the phased approach for executing weekly task batches. Use this when the user provides a week number to implement. Covers scoping, planning, implementation, and delivery.
---

# Weekly Workflow — Task Execution Approach

## When to Use

This workflow activates when the user provides a **week number** (e.g. "Week 4") referencing the project plan in `pm/r0984834_ProjectPlan.md`.

Follow the phases below **in order**. Do not skip phases or start coding before scoping is complete.

---

## Phase 1: Scope

**Goal:** Understand exactly what needs to be built, why it matters, and how it fits into the existing codebase.

### Step 1 — Read the project plan

- Open `pm/r0984834_ProjectPlan.md` and locate the requested week.
- Extract every task item, checkbox, and deliverable listed for that week.
- Understand which **project phase** this week belongs to (Planning, ETL Development, Dashboarding, Finalizing).
- Check which prior weeks are marked complete — this tells you what's already built.
- Note any specific file names, column names, or data sources mentioned.
- Identify the **deliverables** — what artifacts (code, CSVs, notebooks, docs) the week should produce.

### Step 2 — Review business context

Scan `docs/` to understand the _why_ behind the tasks:

- **`docs/r0984834_DataRequirements.md`** — the star schema definition, required fields, and transformation rules. This is the source of truth for what the ETL must produce.
- **`docs/Special Olympics - Use-Cases.pdf`** — the business questions the dashboard must answer (athlete demographics, participation trends, performance analysis, regional distribution).
- **`docs/Slides - Assignment.pdf`** — grading criteria and submission requirements.
- **`docs/week2_r0984834_DataExploration.md`** — known data quality issues, column statistics, and schema quirks discovered during profiling.

The ETL is scored on whether it serves the business questions. Every transformation should trace back to a dashboard need.

### Step 3 — Audit the codebase

Check what already exists before writing anything:

- **`src/`** — which classes exist? What do they cover? Reuse `DataLoader` for all raw file access.
- **`src/notebooks/`** — any prior exploration notebooks relevant to this week's tasks?
- **`data/gold/`** — which output CSVs already exist?
- **`src\main.py`** — is the pipeline entry point wired up?
- **`src\requirements.txt`** — will this week's work need new dependencies?

### Step 4 — Produce a scoped implementation plan

Before writing any code, produce a plan that includes:

- **Task breakdown** — each task from the project plan decomposed into implementable units.
- **Commit plan** — which logical commits will be made and in what order.
- **Dependencies** — what must be built first (e.g., extraction before transformation).
- **Open questions** — flag anything ambiguous and ask the user before proceeding.

---

## Phase 2: Implement

**Goal:** Build everything for the week in a clean, reviewable branch.

### Step 5 — Create the feature branch

```bash
git checkout main
git pull origin main
git checkout -b feat/week-N-short-description
```

One branch per week. The branch name uses the `feat/` prefix and a short description of the week's focus (e.g., `feat/week-4-extraction-logic`).

### Step 6 — Explore with Jupyter notebooks

For any task that involves understanding data, experimenting with transformations, or validating assumptions:

- Create a notebook in `src/notebooks/` (e.g., `week4_extraction_exploration.ipynb`).
- Use **narrated, step-by-step cells** — markdown cells explaining the reasoning, code cells showing the work. Anyone evaluating should be able to read the notebook top-to-bottom and understand what was discovered.
- This is preferred over throwaway scripts or verbose markdown documents without code.
- Notebooks are exploration artifacts — the production logic goes into `src/` classes.

### Step 7 — Write production code

- **OOP classes in `src/`** — follow the same patterns as `DataProfiler` and `DataLoader` (class-based, docstrings, logical method grouping with section comments).
- **Reuse `DataLoader`** (`src/utils/data_loader.py`) for all raw file access — do not re-implement Excel loading.
- **Readability matters** — an evaluator should understand the pipeline by reading the code. Use clear method names, type hints, and concise docstrings.
- **Wire into `src\main.py`** — if this week produces new pipeline stages, integrate them into the entry point.

### Step 8 — Write documentation (selectively)

Create docs **only** when a task is significant enough to warrant explanation beyond what the code and notebooks already provide:

- A new dimensional model design → yes, document in `docs/`.
- A complex transformation with non-obvious business logic → yes.
- A straightforward extraction class → no, the code is self-explanatory.

Docs go in `docs/`. Do not create documentation for the sake of it.

### Step 9 — Commit atomically

Each commit should represent **one logical unit of work**:

- One commit per new class or module.
- One commit per transformation or cleaning step.
- One commit per notebook.
- One commit per documentation file.

Follow the project's conventional commit format:

```
feat(etl): add athlete dimension extractor
docs(exploration): add week 4 extraction notebook
```

Do **not** lump an entire week into a single commit.

---

## Phase 3: Deliver

**Goal:** Validate the output and open a pull request.

### Step 10 — Validate

- **Run the pipeline:** `src\.venv\Scripts\python.exe src\main.py` — it should complete without errors.
- **Check output CSVs** in `data/gold/`:
  - Do the filenames follow `dim_<name>.csv` / `fact_<name>.csv`? (strict penalty for non-compliance)
  - Do the columns match the schema in `docs/r0984834_DataRequirements.md`?
  - Are row counts reasonable? (compare against raw file counts in `docs/week2_r0984834_DataExploration.md`)
- **Spot-check data quality** — sample a few rows and verify transformations (e.g., ordinal rank parsing, gender standardization, score normalization).

### Step 11 — Open the pull request

Use the `git-workflow` skill (`.github/skills/git-workflow/SKILL.md`) to open the PR. Follow its conventions for branch pushing, PR title format, and body content.

The PR should:

- Have a **conventional commit-style title** (e.g., `feat(etl): week 4 — extraction logic`).
- Include a **body** summarizing what was built, any decisions made, and any known limitations.
- **Not be self-merged** — wait for review and approval.

---

## What NOT to Do

- ❌ Start coding before the scoping phase is complete
- ❌ Skip the business context review — every transformation should trace to a dashboard need
- ❌ Create multiple branches for one week of work
- ❌ Write exploration code directly in `src/` instead of notebooks
- ❌ Create docs for trivial items that the code already explains
- ❌ Lump all changes into a single commit
- ❌ Forget to validate output CSVs before opening the PR

# Copilot Instructions — Special Olympics Data Dashboard

## Project Context

ETL pipeline (Python/pandas) that transforms raw Special Olympics Excel files into clean CSVs for a Power BI star-schema dashboard. The data covers athlete certifications, club/delegation info, and competition results (2015–2025).

## Commands

```bash
# Environment setup (uv, not pip)
uv venv src\.venv
uv pip install --python src\.venv\Scripts\python.exe -r src\requirements.txt

# Run the full ETL pipeline
src\.venv\Scripts\python.exe src\main.py

# Run the data profiler standalone
python -m src.profiling.data_profiler

# Excalidraw diagram export (requires Node.js)
cd excalidraw && npm install
node excalidraw/scripts/export-excalidraw.js excalidraw/diagrams/excalidraw/<name>.excalidraw
```

No test suite exists yet. There are no linters or CI configured.

## Architecture

```
data/raw/       → Source Excel files (11 files: Certifications, Clubs, Results per year)
data/gold/      → Output CSVs: dim_*.csv (dimensions), fact_*.csv (facts)
src/            → Python ETL scripts (OOP required by assignment)
  main.py       → Pipeline entry point
  core/         → Shared project paths and cross-cutting constants
  orchestration/
    pipeline.py → Medallion pipeline orchestration
  profiling/
    data_profiler.py → DataProfiler class (schema inspection, column stats, duplicate detection)
  quality/      → Output validation schemas, reports, and validator
  utils/
    data_loader.py → DataLoader class (cached Excel loading, year extraction)
  notebooks/    → Jupyter notebooks for ad-hoc exploration
docs/           → Data requirements, use-case specs, assignment slides
pm/             → Project plan and timeline
```

**Star schema design:**

- **Dimensions:** Athletes, Geography (Clubs), Sports/Events, Time
- **Facts:** Results/Performance, Participation

### Key classes

- **`DataLoader`** (`src/utils/data_loader.py`): Loads and caches raw Excel files. Use `load_certifications()`, `load_clubs()`, `load_results(year)`, `load_all_results()`. Has `available_years()` (returns `[2015–2019, 2022–2025]`) and `extract_year(filename)`.
- **`DataProfiler`** (`src/profiling/data_profiler.py`): Profiles schemas, analyzes columns, detects duplicates, compares schemas across files, and checks referential integrity. All new ETL classes should follow this same OOP pattern.

### Source files in `data/raw/`

- `Thomas More Data Certifications.xlsx` — athlete master list (Code, Gender, DOB, Person type)
- `Thomas More Data Clubs.xlsx` — club/delegation info (Name, Province, Country, City, Language)
- `Thomas More Results 2015.xlsx`
- `Thomas More Results 2016.xlsx`
- `Thomas More Results 2017.xlsx`
- `Thomas More Results 2018.xlsx`
- `Thomas More Results 2019.xlsx`
- `Thomas More Results 2022.xlsx`
- `Thomas More Results 2023.xlsx`
- `Thomas More Results 2024.xlsx`
- `Thomas More Results 2025.xlsx`

> **Note:** 2020 and 2021 are missing (COVID gap). There are 9 results files total.

### Expected outputs in `data/gold/`

- `dim_athletes.csv` — AthleteID, Gender, BirthDate, Age, PersonType
- `dim_geography.csv` — ClubID, ClubName, Region/Province, City, Language
- `dim_sports.csv` — SportID, SportName, EventName, Category
- `dim_time.csv` — Year, Date
- `fact_results.csv` — ResultID, AthleteID, SportID, ClubID, Year, Rank, Medal, Score, IsDisqualified
- `fact_participation.csv` — AthleteID, Year, ClubID

## ETL Conventions

The virtual environment is under **`src\`** (`src\.venv`), managed with **uv**. Dependencies are listed in `src\requirements.txt`: `pandas`, `openpyxl`.

ETL scripts live in `src/`. The pipeline entry point is `src\main.py`. New ETL classes (extractors, transformers) go in `src/` and should reuse `DataLoader` for all raw file access.

### Transformation rules (from `docs/data_requirements.md`)

- **Primary key:** `Code` column — data is anonymized, never attempt to reverse-engineer names.
- **Gender:** Standardize `M`/`F`/`Male`/`Female` → consistent values.
- **Rank/Place:** Parse ordinal strings (`'1st'`, `'2nd'`) → integers. Detect `'DQ'` for disqualifications.
- **Medal:** Derive from Place (1→Gold, 2→Silver, 3→Bronze).
- **Score:** Normalize mixed formats (`"2m 50"`, `"15.00"`, `"00:15.00"`) to numeric (seconds or meters).
- **Club matching:** Fuzzy-match `Club` in Results to `Name` in Clubs when exact match fails.
- **Year:** Extract from filename (`Thomas More Results 2024.xlsx` → `2024`).

### Output naming

CSV filenames **must** follow `dim_<name>.csv` / `fact_<name>.csv` (strict assignment penalty for non-compliance).

## Approach — Weekly Task Workflow

When the user provides a week of work (e.g. "Week 4"), use the `weekly-workflow` skill (`.github/skills/weekly-workflow/SKILL.md`) which defines the full phased approach:

1. **Scope** — Read the specified week's tasks in `pm/r0984834_ProjectPlan.md`, review business context (`docs/`), audit existing code, and produce an implementation plan before writing code.
2. **Implement** — Single `feat/week-N-...` branch. Jupyter notebooks in `src/notebooks/` for exploration; OOP classes in `src/` for production code; docs in `docs/` only for significant items. Atomic commits.
3. **Deliver** — Validate pipeline output and CSVs, then run `git-workflow` skill (`.github/skills/git-workflow/SKILL.md`).

## Code Style

- Use OOP (classes) — this is an assignment requirement.
- pandas for all data manipulation; openpyxl as the Excel engine.

## Git Workflow

When performing any git-related task (creating branches, committing, pushing, opening PRs, merging, or reviewing), use the `git-workflow` skill (`.github/skills/git-workflow/SKILL.md`) as **guidance** for the branching model, conventional commits, PR workflow, and commit granularity rules defined below. **If a user's request conflicts with the skill's guidelines, the user's explicit instructions take precedence.**

**Always use `gh` CLI**(GitHub CLI) for all Git operations — creating branches, pushing, creating PRs, checking status, etc. Do **not** fall back to raw `git` commands or the GitHub MCP API when `gh` can do the job.

**Branching model:** `main` is the single production + development branch.

- **Never commit directly to `main`.** All changes (features, fixes, docs, etc.) go through a dedicated branch + pull request.
- Create a branch from `main` for each unit of work, then open a PR back to `main`.
- PRs require approval before merging — reviewers may request changes.
- Do **not** merge your own PR without approval.

### Branch naming

Use the conventional commit type as a prefix:

```
feat/short-description     → new feature
fix/short-description      → bug fix
docs/short-description     → documentation only
ref/short-description → code restructure (no behaviour change)
chore/short-description    → tooling, deps, CI, config
test/short-description     → adding or updating tests
```

### Commit granularity

Split work into **logical, atomic commits** — do not lump everything into one commit per branch/PR.

- Each commit should represent one self-contained change (e.g., one function, one fix, one file group).
- If a feature touches extract + transform + tests, that's at least 3 commits, not 1.
- Keep commits reviewable: a reviewer should understand each commit on its own.

### Commit messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<optional scope>): <short summary>

[optional body]
```

**Types:** `feat`, `fix`, `docs`, `ref`, `chore`, `test`, `style`, `perf`, `ci`, `build`

Examples:

```
feat(etl): add score normalization for time-based results
fix(transform): handle DQ entries in rank parsing
docs: update data requirements with medal logic
chore: add openpyxl to src\requirements.txt
```

### PR titles

PR titles follow the same conventional format:

```
feat(etl): implement athlete dimension extraction
fix(transform): correct fuzzy club matching threshold
docs: add star schema diagram to README
```

## Visuals & Diagrams

All diagrams **must** use Excalidraw — no other diagramming tools allowed. See the `visuals` skill (`.github/skills/visuals/SKILL.md`) for the full workflow:

- Source files: `excalidraw/diagrams/excalidraw/<name>.excalidraw`
- Exported PNGs: `excalidraw/diagrams/export/<name>.png` (dark mode, `#000000` background)
- Export command: `node excalidraw/scripts/export-excalidraw.js excalidraw/diagrams/excalidraw/<name>.excalidraw`
- README embedding: inline image + Excalidraw.com edit link

## Power BI Notes

All data transformation happens in Python, **not** in Power BI. Power BI only consumes the clean CSVs from `data/gold/` and handles visualization + DAX measures.

<!-- llm-mem:start -->
## High-priority llm-mem context optimization

Always prefer llm-mem for efficient memory and context management on repo-specific coding, debugging, refactoring, testing, explanation, and architecture tasks.

Do not wait for the user to invoke `/llm-mem`. When MCP tools are available, proactively use the llm-mem MCP tools before broad repository discovery.

Follow this protocol:

1. Call the MCP tool `llm_mem_context_map` with `{ "task": "<user task>", "workingDirectory": "<current repo/worktree root>", "maxCandidates": 8 }` before broad file search for repo-specific tasks.
2. Expand only needed candidates with `llm_mem_snippet` and their `expansionId` values.
3. Use cited source refs first. Prefer the smallest edit path that satisfies the task and cited constraints.
4. Use `llm_mem_context_pack` only for broad/debug tasks or when map plus snippets are insufficient.
5. Use `llm_mem_remember` only for durable source-grounded facts when `repoId` is available; never guess `repoId`.
6. Do not run shell `llm-mem context` when the MCP tools are available, and do not paste the full pack to the user unless asked.
7. Skip llm-mem only for trivial single-file edits, pure shell/git questions, or tasks where the user already supplied all necessary context.

Keep normal Copilot behavior and user intent first; llm-mem is an optimization layer, not a replacement assistant.
<!-- llm-mem:end -->

# Copilot Instructions — Special Olympics Data Dashboard

## Project Context

ETL pipeline (Python/pandas) that transforms raw Special Olympics Excel files into clean CSVs for a Power BI star-schema dashboard. The data covers athlete certifications, club/delegation info, and competition results (2015–2025).

## Commands

```bash
# Environment setup (uv, not pip)
uv venv
uv pip install -r requirements.txt

# Run the full ETL pipeline
python main.py

# Run the data profiler standalone
python -m src.explore

# Excalidraw diagram export (requires Node.js)
cd excalidraw && npm install
node excalidraw/scripts/export-excalidraw.js excalidraw/diagrams/excalidraw/<name>.excalidraw
```

No test suite exists yet. There are no linters or CI configured.

## Architecture

```
data/raw/       → Source Excel files (11 files: Certifications, Clubs, Results per year)
data/processed/ → Output CSVs: dim_*.csv (dimensions), fact_*.csv (facts)
src/            → Python ETL scripts (OOP required by assignment)
  explore.py    → DataProfiler class (schema inspection, column stats, duplicate detection)
  utils/
    data_loader.py → DataLoader class (cached Excel loading, year extraction)
  notebooks/    → Jupyter notebooks for ad-hoc exploration
main.py         → Pipeline entry point (project root)
docs/           → Data requirements, use-case specs, assignment slides
pm/             → Project plan and timeline
```

**Star schema design:**

- **Dimensions:** Athletes, Geography (Clubs), Sports/Events, Time
- **Facts:** Results/Performance, Participation

### Key classes

- **`DataLoader`** (`src/utils/data_loader.py`): Loads and caches raw Excel files. Use `load_certifications()`, `load_clubs()`, `load_results(year)`, `load_all_results()`. Has `available_years()` (returns `[2015–2019, 2022–2025]`) and `extract_year(filename)`.
- **`DataProfiler`** (`src/explore.py`): Profiles schemas, analyzes columns, detects duplicates, compares schemas across files, and checks referential integrity. All new ETL classes should follow this same OOP pattern.

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

### Expected outputs in `data/processed/`

- `dim_athletes.csv` — AthleteID, Gender, BirthDate, Age, PersonType
- `dim_geography.csv` — ClubID, ClubName, Region/Province, City, Language
- `dim_sports.csv` — SportID, SportName, EventName, Category
- `dim_time.csv` — Year, Date
- `fact_results.csv` — ResultID, AthleteID, SportID, ClubID, Year, Rank, Medal, Score, IsDisqualified
- `fact_participation.csv` — AthleteID, Year, ClubID

## ETL Conventions

The virtual environment is at the **project root** (`.venv`), managed with **uv**. Dependencies: `pandas`, `openpyxl`.

ETL scripts live in `src/`. The pipeline entry point is `main.py` at the project root (not yet implemented — currently empty). New ETL classes (extractors, transformers) go in `src/` and should reuse `DataLoader` for all raw file access.

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

When the user provides a week of work (e.g. "Week 4") with a linked GitHub issue, use the `weekly-workflow` skill (`.github/skills/weekly-workflow/SKILL.md`) which defines the full phased approach:

1. **Scope** — Read the issue, cross-reference the project plan (`pm/`), review business context (`docs/`), audit existing code, and produce an implementation plan before writing code.
2. **Implement** — Single `feat/week-N-...` branch. Jupyter notebooks in `src/notebooks/` for exploration; OOP classes in `src/` for production code; docs in `docs/` only for significant items. Atomic commits.
3. **Deliver** — Validate pipeline output and CSVs, then open a PR via `gh`.


## Code Style

- Use OOP (classes) — this is an assignment requirement.
- pandas for all data manipulation; openpyxl as the Excel engine.

## Git Workflow

When performing any git-related task (creating branches, committing, pushing, opening PRs, merging, or reviewing), use the `git-workflow` skill (`.github/skills/git-workflow/SKILL.md`) which enforces the branching model, conventional commits, PR workflow, and commit granularity rules defined below.

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
chore: add openpyxl to requirements.txt
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

All data transformation happens in Python, **not** in Power BI. Power BI only consumes the clean CSVs from `data/processed/` and handles visualization + DAX measures.

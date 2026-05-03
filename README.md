# Project: Special Olympics Data Dashboard

Final PowerBI dashboard in [./pbix](./pbix), or directly open [./pbix/r0984834_Dashboard.pbix](./pbix/r0984834_Dashboard.pbix) in PowerBI or see [./pbix/pages](./pbix/pages).

## Overview

This project is about building an end-to-end data solution for the Special Olympics. We are acting as consultants for a client (Special Olympics) to transform raw data into actionable insights using Python and Power BI.

## Example

![PowerBI Overview Page](./pbix/pages/overview.png)

## The Goal

The main objective is to answer business questions about athlete participation, performance trends, and regional statistics. We need to show things like:

- Athlete distribution by age, gender, and sport.
- Performance improvements over time.
- Regional participation stats.

## Tech Stack

- **Source Data:** Raw Excel files (Certifications, Clubs, Historical Results).
- **ETL & Transformation:** Python (OOP principles).
- **Versioning:** GitHub.
- **Visualization:** Microsoft Power BI.
- **(Bonus):** MySQL & Medallion Architecture.

## Run the ETL

Use the uv-managed environment under `src\.venv`:

```powershell
uv venv src\.venv
uv pip install --python src\.venv\Scripts\python.exe -r src\requirements.txt
src\.venv\Scripts\python.exe src\main.py
```

This runs the full medallion pipeline from raw Excel files to validated gold-layer CSVs:

```text
data/raw -> data/bronze -> data/silver -> data/gold
```

## Project Workflow

- **Project Management:** Weekly planning and task breakdown.
- **Modeling:** Designing a Star Schema (Facts & Dimensions).
- **ETL Pipeline:** Writing Python scripts to clean raw Excel files and save them as CSVs.
- **Dashboarding:** Importing clean data into Power BI to build a professional report.
- **Validation:** Documenting everything and proving the numbers match the source.

## Final Data Model

The final Power BI model is a star schema with 5 dimensions and 2 facts:

| Table                    |   Rows | Purpose                                               |
| ------------------------ | -----: | ----------------------------------------------------- |
| `dim_athlete.csv`        | 20,221 | Certified people, demographics, and certificate flags |
| `dim_geography.csv`      |    437 | Clubs/delegations and regional attributes             |
| `dim_sport.csv`          |     23 | Distinct sports                                       |
| `dim_event.csv`          |    210 | Normalized competition events                         |
| `dim_time.csv`           |     11 | Reporting years, including the 2020-2021 COVID gap    |
| `fact_results.csv`       | 72,702 | Event-level performance results                       |
| `fact_participation.csv` | 27,829 | Athlete participation by club and year                |

The latest reproducibility run completed with **68/68 validation checks passed**. See [final validation](./docs/md/r0984834_FinalValidation.md) and the detailed [dimensional model](./docs/md/r0984834_DimensionalModel.md).

## Final Deliverables

Everything gets submitted in one ZIP file containing:

- Project Plan & Wireframes.
- Dimensional Model design.
- Power BI Dashboard (.pbix).
- Python Repository & Cleaned Data.
- Documentation with data audit.

Key project documentation:

- [Data requirements](./docs/md/r0984834_DataRequirements.md)
- [Data exploration and audit](./docs/md/r0984834_DataExploration.md)
- [Dimensional model](./docs/md/r0984834_DimensionalModel.md)
- [Final validation and self-evaluation](./docs/md/r0984834_FinalValidation.md)
- [Power BI setup and measures](./pbix/README.md)
- [AI usage disclosure](./AI.md)

## Evaluation Focus

- **Accuracy:** Numbers must match the raw data.
- **Professionalism:** Treat it like a real client job.
- **Design:** Intuitive and logical dashboard layout.

<!-- llm-mem:readme:start -->

## llm-mem

This repository is configured for [llm-mem](https://github.com/aryxenv/llm-mem) Copilot MCP integration. llm-mem keeps its index and run artifacts in the local `.llm-mem/` directory, which is intentionally ignored by Git.

If you do not already have the `llm-mem` CLI installed, clone or open the llm-mem source repo and link the CLI first:

```powershell
git clone https://github.com/aryxenv/llm-mem.git
cd llm-mem
npm install
npm run build
npm run link:cli
```

Then, from this repository, bootstrap your local index and MCP wiring:

```powershell
llm-mem integrate copilot install
```

Keep using `copilot` normally after that. The project MCP config, skill, and instructions tell Copilot when to use llm-mem context tools.

<!-- llm-mem:readme:end -->

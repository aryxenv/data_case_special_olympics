# Special Olympics Data Dashboard - Weekly Project Plan

**Timeline:** Feb 10, 2026 – May 15, 2026 (13 Weeks)  
**Weekly Effort:** ~4 Hours/Week  
**Goal:** Deliver a Python ETL pipeline and Power BI dashboard for Special Olympics.

---

## Weekly Schedule & Task List

### **Phase 1: Planning & Design (Weeks 1-3)**

#### **Week 1: Project Kickoff & Setup (Feb 10 - Feb 16)**

_Goal: Understand requirements and set up the workspace._

- [x] Read assignment slides and understand business questions (1h)
- [x] Create folder structure (`data/raw`, `data/processed`, `src/`) (0.5h)
- [x] Initialize Git repository and create `.gitignore` (0.5h)
- [x] List all required fields/metrics based on business questions (2h)

#### **Week 2: Data Exploration (Feb 17 - Feb 23)**

_Goal: Profile raw data and identify data quality issues._

- [x] Open `Certifications.xlsx`, `Clubs.xlsx`, `Historical_Results.xlsx` (1h)
- [x] Document relationships between sheets/files (1h)
- [x] Note down missing values, weird formats, or duplicates (2h)

#### **Week 3: Dimensional Modeling (Feb 24 - Mar 2)**

_Goal: Design the Star Schema (Gold Layer)._

- [x] Design Dimension tables (Athletes, Sports, Dates, Locations) (2h)
- [x] Design Fact tables (Results, Participation) (1.5h)
- [x] Create formal dimensional model (star-schema.png) using Excalidraw (0.5h)

---

### **Phase 2: ETL Development (Python) (Weeks 4-7)**

USE MEDALLION ARCHITECTURE (Bronze: Raw → Silver: Cleaned → Gold: Star Schema)

#### **Week 4: Extraction Logic (Mar 3 - Mar 9)**

_Goal: Read data from Excel into Python._

- [x] Set up Python virtual environment & install `pandas`, `openpyxl` (0.5h)
- [x] Write `extract.py` to read all Excel files into DataFrames (2.5h)
- [x] Verify row counts match raw files (1h)

#### **Week 5: Data Cleaning (Mar 10 - Mar 16)**

_Goal: Clean raw data using OOP principles._

- [x] Write `clean.py` class structure (1h)
- [x] Implement methods to handle NULLs and duplicates (2h)
- [x] Standardize date formats and string casing (1h)

#### **Week 6: Transformation & Aggregation (Mar 17 - Mar 23)**

_Goal: Shape data into the Star Schema._

- [ ] Write `transform.py` to merge tables into Facts & Dimensions (2.5h)
- [ ] Implement "20% Rule" validation logic for disqualifications (0.5h)
- [ ] Calculate derived columns (e.g., Age from Birthdate) (1h)

#### **Week 7: Export & Validation (Mar 24 - Mar 30)**

_Goal: Finalize ETL and generate CSVs for Power BI._

- [ ] Verify CSV filenames match `dim_xxx.csv` and `fact_xxx.csv` (STRICT 5pt PENALTY)
- [ ] Write `load.py` to export cleaned DataFrames to CSV (1.5h)
- [ ] Run full pipeline: Raw Excel → Python → Clean CSVs (1h)
- [ ] Check CSV output quality (do columns match the schema?) (1.5h)

---

### **Phase 3: Dashboarding (Power BI) (Weeks 8-11)**

#### **Week 8: Dashboard Setup (Mar 31 - Apr 6)**

_Goal: Design Dashboard Wireframe and export as `r0984834_Wireframe.pdf`._

- [ ] Design Dashboard Wireframe (1h)
- [ ] Import Clean CSVs into Power BI (1h)
- [ ] Create relationships (One-to-Many) between Facts & Dimensions (1h)
- [ ] Create basic Measures (Total Athletes, Medal Count) (2h)

#### **Week 9: Overview Dashboard Page (Apr 7 - Apr 13)**

_Goal: Visualize high-level KPIs._

- [ ] Build "Athlete Overview" page (Bar charts: Age, Gender) (2h)
- [ ] Add filters (Year, Sport, Region) (1h)
- [ ] Format layout and colors (1h)

#### **Week 10: Performance & Regional Details (Apr 14 - Apr 20)**

_Goal: Answer specific business questions._

- [ ] Build "Performance Trends" visual (Line chart over time) (2h)
- [ ] Build "Regional Map" or matrix (2h)

#### **Week 11: Polish & Interactivity (Apr 21 - Apr 27)**

_Goal: Make the report professional._

- [ ] Add navigation buttons/bookmarks (1h)
- [ ] specific logic checks (e.g. participation rates correctness) (2h)
- [ ] Final UI cleanup (titles, alignment) (1h)

---

### **Phase 4: Finalizing (Weeks 12-13)**

#### \*\*Week 12: Data model & Validation (include screenshots proving PBI vs Excel match)

_Goal: Ensure everything is robust._

- [ ] Re-run Python pipeline to ensure reproducibility (1h)
- [ ] Document the data model and assumptions (READ.me/PDF) (2h)
- [ ] Self-evaluation against assignment rubric (1h)

#### **Week 13: Final Submission Prep (May 5 - May 15)**

_Goal: Submit project._

- [ ] Clean up code (add comments) (1.5h)
- [ ] Organize folder structure for submission (1h)
- [ ] ZIP project (Code, PBIX, Docs) and submit (1.5h)

---

## Project Requirements Checklist (from Assignment)

**Technical Stack**

- [ ] **Python:** Used for ETL (Extract, Transform, Load)
- [ ] **OOP:** Python code uses Classes/Objects
- [ ] **Power BI:** Used for visualization (no data transformation in PBI)
- [ ] **Star Schema:** Dimensional model used (Facts/Dimensions)

**Deliverables**

- [ ] Python Code (Clean & Commented)
- [ ] Clean Data (CSV files)
- [ ] Power BI Report (.pbix)
- [ ] Documentation (Project Plan & Data Model)

**Business Goals**

- [ ] Show Athlete participation stats (Age, Gender, etc.)
- [ ] Show Performance trends over time
- [ ] Show Regional distribution

---

## AI Usage

Gemini 3 Pro was used to generate this project plan.

### Prompt 1: Initial Project Management Plan

```txt
create a weekly breakdown of the project found in #file:Slides - Assignment.pdf  in section Project Phases and task. today is 10 february 2026, the deadline for this is 15 may 2026. Create a logical weekly break of the project in PM folder with structured markdown. ensure the distribution of tasks is realistic and sequential (waterfall). you can find more of the requirements in #file:Slides - Assignment.pdf .
```

### Prompt 2: Summarize Project Management Plan

```txt
the #file:pm  folder is way too detailed. I simply want 1 file describing the weekly breakdown (assume I will spend 4 hours per week on this from 10 feb till 15 may (13 weeks)). Include the task list since that's quite nice to have to keep track. But again, all in 1 file, must still be logical, but just not so detailed as it is right now. Make sure the requirements are still correctly met based on #file:Slides - Assignment.pdf .
```

### Prompt 3: Week 2 Data Exploration

```txt
plan out the tasks of week 2 from the project plan, make sure to review the slides to have a complete overview of what is expected
```

Copilot CLI (Claude Opus 4.6) was used to:

- Rewrite `src/explore.py` as an OOP-based `DataProfiler` class
- Profile all 11 raw Excel files (Certifications, Clubs, 9 Results files)
- Document cross-file relationships and referential integrity
- Generate `docs/data_exploration.md` with comprehensive findings

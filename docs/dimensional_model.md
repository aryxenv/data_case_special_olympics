# Dimensional Model — Special Olympics Data Dashboard

> Star schema design for the ETL pipeline (Python → CSV) consumed by Power BI.

## Overview

The model follows a classic **star schema** with 5 dimension tables and 2 fact tables.
All data originates from 11 raw Excel files (1 Certifications, 1 Clubs, 9 yearly Results).

```
                    ┌──────────────┐
                    │  dim_athlete  │
                    └──────┬───────┘
                           │
┌───────────────┐   ┌──────┴───────┐   ┌────────────┐
│ dim_geography ├───┤ fact_results  ├───┤  dim_sport  │
└───────────────┘   └──────┬───────┘   └────────────┘
                           │
┌───────────────┐   ┌──────┴───────┐
│   dim_event   ├───┤              │
└───────────────┘   └──────┬───────┘
                           │
                    ┌──────┴───────┐
                    │   dim_time   │
                    └──────────────┘

┌──────────────┐   ┌────────────────────┐   ┌──────────────┐
│ dim_athlete  ├───┤ fact_participation  ├───┤  dim_time    │
└──────────────┘   └─────────┬──────────┘   └──────────────┘
                             │
                    ┌────────┴───────┐
                    │ dim_geography  │
                    └────────────────┘
```

All relationships are **many-to-one** (fact → dimension), modeled as One-to-Many in Power BI.

---

## Dimension Tables

### `dim_athlete`

Athletes, unified partners, coaches, and other participants from the Certifications master list.

| Column | Type | Source | Notes |
|--------|------|--------|-------|
| `athlete_key` | INT | Generated | Surrogate key (auto-increment) |
| `code` | VARCHAR(16) | Certifications.`Code` | Natural key — unique 16-char alphanumeric |
| `gender` | VARCHAR(1) | Certifications.`Gender` | Standardized: `M` / `F` / `U` |
| `date_of_birth` | DATE | Certifications.`DOB` | NULL for sentinel dates (1900-01-02) and missing values |
| `age` | INT | Derived from `DOB` | Recalculated as `reference_year - birth_year`. NULL when DOB is missing |
| `person_type` | VARCHAR(20) | Certifications.`Person type` | Athlete, Unified Partner, Coach, Staff, Volunteer, etc. |
| `has_mental_handicap_cert` | BOOLEAN | Certifications.`Mental Handicap (...)` | True if value = 1.0, False otherwise |
| `has_parents_consent_cert` | BOOLEAN | Certifications.`Parents Consent (...)` | True if value = 1.0, False otherwise |
| `has_hap_cert` | BOOLEAN | Certifications.`HAP (...)` | True if value = 1.0, False otherwise |
| `is_unified_partner_cert` | BOOLEAN | Certifications.`Unified Partner (...)` | True if value = 1.0, False otherwise |

**Primary key:** `athlete_key`  
**Natural key:** `code`  
**Row count:** ~20 221 (after dropping 780 empty rows from Certifications)  
**ETL rules:**
- Drop rows where all columns are NaN (780 empty padding rows).
- Replace sentinel DOB `1900-01-02` with NULL.
- Set `age = NULL` when DOB is missing (instead of 0).
- Map certificate columns: `1.0` → True, everything else → False.
- Gender is already `M`/`F`/`U` in Certifications — no mapping needed.

**Design note:** All person types are included (not just Athletes) so that coach counts, volunteer analysis, and unified partner metrics are possible in Power BI. Dashboard pages should filter on `person_type = 'Athlete'` for athlete-specific KPIs.

---

### `dim_geography`

Clubs and delegations from the Clubs master file, representing the organizational/regional dimension.

| Column | Type | Source | Notes |
|--------|------|--------|-------|
| `geography_key` | INT | Generated | Surrogate key (auto-increment). Key = -1 reserved for Unknown |
| `club_id` | INT | Clubs.`Group number` | Natural key — unique integer per club |
| `club_name` | VARCHAR(50) | Clubs.`Name` | Canonical name, title-cased |
| `province` | VARCHAR(30) | Clubs.`Province` | Standardized (typos fixed, casing normalized to 11 Belgian provinces) |
| `city` | VARCHAR(50) | Clubs.`City` | Title-cased, deduplicated (e.g., `GENK` and `Genk` → `Genk`) |
| `country` | VARCHAR(20) | Clubs.`Country` | Standardized: all Belgium variants → `Belgium`, one `Luxembourg` |
| `primary_language` | VARCHAR(10) | Clubs.`Primary language` | `Dutch` / `French` |
| `zipcode` | VARCHAR(5) | Clubs.`Zipcode` | String format. Outlier 29900 → 2990 |

**Primary key:** `geography_key`  
**Natural key:** `club_id`  
**Row count:** 437 (436 real clubs + 1 Unknown row)  
**ETL rules:**
- Standardize all 14 Country spelling variants to `Belgium` (except Luxembourg).
- Fix Province typos: `Babant Wallon` → `Brabant Wallon`, normalize hyphens and casing.
- Fix Province/Country swap on Group 786 (KHC SAINT-GEORGES).
- Fill 74 missing Country values with `Belgium` (all have Belgian provinces).
- Standardize city names to title case.
- Convert zipcode from float64 → string; fix 29900 → 2990.
- Insert a special row: `geography_key = -1, club_name = 'Unknown'` for unmatched Results clubs.

**Club matching strategy:** Results files reference clubs by name (not ID). The ETL must:
1. Exact match (case-insensitive, whitespace-stripped) against `club_name`.
2. Fuzzy match (Levenshtein distance) for near-misses (e.g., `REINE FABIOLA` → `CENTRE REINE FABIOLA`).
3. Assign `geography_key = -1` for clubs that remain unmatched.

---

### `dim_sport`

Distinct sports from the Results files.

| Column | Type | Source | Notes |
|--------|------|--------|-------|
| `sport_key` | INT | Generated | Surrogate key (auto-increment) |
| `sport_name` | VARCHAR(50) | Results.`Sport` | Canonical sport name |

**Primary key:** `sport_key`  
**Row count:** 23  
**ETL rules:**
- Use distinct `Sport` values across all Results years.
- Keep `Aquatics/Swimming` and `Swimming` as separate sports (different pool formats: AQ = 25m/50m, SW = 33m/66m).
- `Football/Soccer` is discontinued post-COVID (2022+) but retained in the dimension for historical analysis.

---

### `dim_event`

Distinct competition events, normalized via event code extraction from bilingual event names.

| Column | Type | Source | Notes |
|--------|------|--------|-------|
| `event_key` | INT | Generated | Surrogate key (auto-increment) |
| `sport_key` | INT (FK) | dim_sport | Links to parent sport |
| `event_code` | VARCHAR(10) | Extracted from Results.`Event` | Stable prefix: `AT17`, `AQ25`, `CY05`, etc. |
| `event_name` | VARCHAR(100) | Results.`Event` | Most common or most recent variant of the full name |

**Primary key:** `event_key`  
**Foreign key:** `sport_key` → `dim_sport.sport_key`  
**Row count:** ~182 (after event code normalization from 377 raw names)  
**ETL rules:**
- Extract event code prefix using regex: `^([A-Za-z]{2,5}\d*)\s*-` from event name.
- Edge cases without standard prefixes (finals, divisioning, APA sub-events) get assigned synthetic codes based on parent sport (e.g., `FO-FINAL`, `APA-PETANQUE`).
- For each event code, store the most frequently occurring full name as `event_name`.
- Link to `dim_sport` via the sport name on the same Results row.

---

### `dim_time`

Year-level time dimension (no specific competition dates are available in the data).

| Column | Type | Source | Notes |
|--------|------|--------|-------|
| `time_key` | INT | Year value | Natural key = year (e.g., 2015, 2024) |
| `year` | INT | Filename | 2015, 2016, 2017, 2018, 2019, 2022, 2023, 2024, 2025 |
| `is_covid_gap` | BOOLEAN | Derived | True for 2020, 2021 (no data, but included for completeness) |
| `period` | VARCHAR(15) | Derived | `Pre-COVID` (2015–2019), `COVID` (2020–2021), `Post-COVID` (2022–2025) |

**Primary key:** `time_key`  
**Row count:** 11 (9 data years + 2020 + 2021 for gap visualization)  
**ETL rules:**
- Generate rows for all years 2015–2025 (including COVID gap years).
- `is_covid_gap = True` for 2020 and 2021.
- `period` label derived from year range.

---

## Fact Tables

### `fact_results`

Individual competition results — one row per athlete per event per year (final/best round).

| Column | Type | Source | Notes |
|--------|------|--------|-------|
| `result_key` | INT | Generated | Surrogate key (auto-increment) |
| `athlete_key` | INT (FK) | dim_athlete | Via `Code` lookup |
| `geography_key` | INT (FK) | dim_geography | Via fuzzy `Club` → `Name` match |
| `sport_key` | INT (FK) | dim_sport | Via `Sport` lookup |
| `event_key` | INT (FK) | dim_event | Via event code extraction + lookup |
| `time_key` | INT (FK) | dim_time | Year from filename |
| `rank` | INT | Results.`Place` | Parsed: `1st`→1, `2nd`→2, ... NULL for DQ/DNS/DNF |
| `medal` | VARCHAR(6) | Derived from `rank` | `Gold` (1), `Silver` (2), `Bronze` (3), NULL otherwise |
| `score_value` | FLOAT | Results.`Score` | Parsed to numeric (total seconds, meters, or points) |
| `score_unit` | VARCHAR(10) | Derived from `Score` format | `seconds` / `meters` / `points` |
| `is_disqualified` | BOOLEAN | Results.`Place` | True if Place contains `DQ` |
| `result_status` | VARCHAR(5) | Results.`Place` | `DQ` / `DNS` / `DNF` / `DNC` / `DNT` / NULL for normal results |

**Primary key:** `result_key`  
**Foreign keys:** `athlete_key`, `geography_key`, `sport_key`, `event_key`, `time_key`  
**Grain:** One row per athlete × event × year (final round)  
**Row count (estimated):** ~72 700 (after deduplication from ~112 400 raw rows — ~35% multi-round removal)  
**ETL rules:**
- **Multi-round dedup:** Each (Code, Event, Sport, Year) group may have 2–3 rows (qualifying, prelim, final). Keep the row with a non-null `Place` value. If multiple have Place, prefer the one with the lowest rank (best result). Use `Summary (all)` to disambiguate when available (missing in 2023).
- **Place parsing:** Map ordinal strings to integers (`1st`→1, `2nd`→2, ..., `8th`→8, `10th`→10). Normalize DQ codes (`DQ: HE` → `DQ-HE`).
- **Score parsing:** Three patterns:
  - `X min, Y.ZZ sec` → total seconds (e.g., `13 min, 27.00 sec` → 807.0)
  - `Xm, Y.ZZcm` → total meters (e.g., `18m, 28.00cm` → 18.28)
  - `X.XX points` → numeric points (e.g., `57.90 points` → 57.9)
- **Medal derivation:** rank 1 → Gold, rank 2 → Silver, rank 3 → Bronze, else NULL.
- **Aquatics levels:** `AQ X.Y` Place values are skill-level classifications (not rankings). Set `rank = NULL`, `result_status = NULL`, store the AQ level as-is or in a separate column.

---

### `fact_participation`

Aggregated participation records — one row per athlete per club per year.

| Column | Type | Source | Notes |
|--------|------|--------|-------|
| `athlete_key` | INT (FK) | dim_athlete | Via `Code` lookup |
| `geography_key` | INT (FK) | dim_geography | Club in that year (from Results) |
| `time_key` | INT (FK) | dim_time | Year |
| `events_entered` | INT | Derived | Count of distinct events that year |
| `sports_entered` | INT | Derived | Count of distinct sports that year |

**Primary key:** Composite (`athlete_key`, `geography_key`, `time_key`)  
**Grain:** One row per athlete × club × year  
**Row count (estimated):** ~28 000 (based on unique Code × Year combinations across all Results)  
**ETL rules:**
- Derived from `fact_results` by grouping on (athlete_key, geography_key, time_key).
- `events_entered` = COUNT DISTINCT event_key per group.
- `sports_entered` = COUNT DISTINCT sport_key per group.
- Only includes athletes who actually competed (appear in Results), not the full Certifications roster.

---

## Output File Naming Convention

All CSVs are exported to `data/processed/` with strict naming:

| File | Table |
|------|-------|
| `dim_athlete.csv` | dim_athlete |
| `dim_geography.csv` | dim_geography |
| `dim_sport.csv` | dim_sport |
| `dim_event.csv` | dim_event |
| `dim_time.csv` | dim_time |
| `fact_results.csv` | fact_results |
| `fact_participation.csv` | fact_participation |

> ⚠️ **STRICT PENALTY (5 pts)** for non-compliant filenames per assignment rubric.

---

## Business Question Traceability

| Business Question | Answered By | Key Columns |
|-------------------|------------|-------------|
| **Athlete demographics** (age, gender) | `dim_athlete` + `fact_participation` | `gender`, `age`, `person_type` |
| **Participation trends** (growth over time) | `fact_participation` + `dim_time` | `time_key`, `events_entered`, `period` |
| **Performance analysis** (medals, results) | `fact_results` + `dim_athlete` + `dim_event` | `rank`, `medal`, `score_value`, `is_disqualified` |
| **Regional distribution** (globalization) | `fact_results` + `dim_geography` | `province`, `city`, `country`, `primary_language` |

---

## AI Usage

Copilot CLI (Claude Opus 4.6) was used to:
- Explore dimension cardinalities and validate grain decisions via Python (see `src/notebooks/week3_dimensional_modeling.ipynb`)
- Draft this dimensional model document based on findings from `docs/data_exploration.md` and `docs/data_requirements.md`
- Create the Excalidraw star-schema diagram and PNG export

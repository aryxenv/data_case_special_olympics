# Final Validation and Self-Evaluation

> Week 12 deliverable for the Special Olympics Data Dashboard.

## Scope

This document records the final data-model assumptions, reproducibility check, output validation, and self-evaluation against the assignment requirements. The Power BI vs Excel screenshot evidence is intentionally not reproduced here because it was already completed manually outside this task.

## Reproducibility check

The full ETL pipeline was re-run through the project's uv-managed `src\.venv` environment:

```powershell
src\.venv\Scripts\python.exe src\main.py
```

The run completed successfully and executed the full medallion flow:

1. Bronze extraction from raw Excel workbooks.
2. Silver cleaning and standardization.
3. Gold star-schema transformation.
4. Automated output validation.

Validation summary from the run:

| Result | Count |
| ------ | ----: |
| Total checks | 68 |
| Passed | 68 |
| Failed | 0 |

The reproducibility run did not produce unexpected generated-data changes.

## Gold-layer output audit

All final CSVs are written to `data/gold/` and follow the required `dim_*.csv` / `fact_*.csv` naming convention.

| File | Rows | Columns | Grain |
| ---- | ---: | ------: | ----- |
| `dim_athlete.csv` | 20,221 | 10 | One row per certified person code |
| `dim_geography.csv` | 437 | 8 | One row per club/delegation plus an `Unknown` fallback |
| `dim_sport.csv` | 23 | 2 | One row per distinct sport |
| `dim_event.csv` | 210 | 4 | One row per normalized event code and sport |
| `dim_time.csv` | 11 | 4 | One row per year from 2015 to 2025, including COVID gap years |
| `fact_results.csv` | 72,702 | 12 | One row per athlete, event, sport, and year after multi-round deduplication |
| `fact_participation.csv` | 27,829 | 5 | One row per athlete, club, and year |

### Output schemas

| Table | Columns |
| ----- | ------- |
| `dim_athlete` | `athlete_key`, `code`, `person_type`, `gender`, `date_of_birth`, `age`, `has_mental_handicap_cert`, `has_parents_consent_cert`, `has_hap_cert`, `is_unified_partner_cert` |
| `dim_geography` | `geography_key`, `club_id`, `club_name`, `province`, `city`, `country`, `primary_language`, `zipcode` |
| `dim_sport` | `sport_key`, `sport_name` |
| `dim_event` | `event_key`, `event_code`, `event_name`, `sport_key` |
| `dim_time` | `time_key`, `year`, `is_covid_gap`, `period` |
| `fact_results` | `result_key`, `athlete_key`, `geography_key`, `sport_key`, `event_key`, `time_key`, `rank`, `medal`, `score_value`, `score_unit`, `is_disqualified`, `result_status` |
| `fact_participation` | `athlete_key`, `geography_key`, `time_key`, `events_entered`, `sports_entered` |

## Data model

The final model is a star schema consumed by Power BI. It has five dimensions and two facts:

- `dim_athlete` describes certified people using the anonymized `Code` natural key.
- `dim_geography` describes clubs/delegations and regional attributes.
- `dim_sport` describes sports.
- `dim_event` describes normalized competition events and links each event to a sport.
- `dim_time` describes year-level reporting periods, including the 2020-2021 COVID gap.
- `fact_results` stores event-level performance outcomes.
- `fact_participation` aggregates participation by athlete, club, and year.

The detailed dimensional model is documented in [`docs/md/dimensional_model.md`](./dimensional_model.md). Power BI import settings, relationships, DAX measures, and page construction notes are documented in [`pbix/README.md`](../../pbix/README.md).

### Relationships

| From | To | Key |
| ---- | -- | --- |
| `dim_athlete` | `fact_results` | `athlete_key` |
| `dim_athlete` | `fact_participation` | `athlete_key` |
| `dim_geography` | `fact_results` | `geography_key` |
| `dim_geography` | `fact_participation` | `geography_key` |
| `dim_sport` | `fact_results` | `sport_key` |
| `dim_sport` | `dim_event` | `sport_key` |
| `dim_event` | `fact_results` | `event_key` |
| `dim_time` | `fact_results` | `time_key` |
| `dim_time` | `fact_participation` | `time_key` |

All fact-to-dimension relationships are many-to-one from the fact table to the dimension table.

## Key assumptions

| Area | Assumption |
| ---- | ---------- |
| Anonymity | `Code` is the only person identifier. The project does not infer or reconstruct names. |
| Athlete dimension | All certification person types are retained, including athletes, unified partners, coaches, and other support roles. Athlete-specific visuals filter `person_type = "Athlete"`. |
| Age and birth date | Missing DOB values remain null. Sentinel DOB `1900-01-02` is treated as missing, and age is nulled when DOB is missing. |
| Gender | Certification gender values are kept as `M`, `F`, or `U`. Result gender values are standardized from long-form values to those codes in silver. |
| COVID years | 2020 and 2021 are included in `dim_time` with `is_covid_gap = True`, even though no results files exist for those years. |
| Multi-round results | Multiple raw rows for the same athlete, event, sport, and year represent rounds or attempts. The silver layer keeps the best/final row using rank and score sorting rules. |
| Rank and disqualification | Ordinal places become integer ranks. `DQ*` values are normalized as result statuses and flagged with `is_disqualified = True`. |
| Aquatics levels | `AQ X.Y` place values are treated as skill classifications, not ranks, so they do not create medals. |
| Medal logic | Medals are derived only from rank: 1 = Gold, 2 = Silver, 3 = Bronze. |
| Score units | Scores are parsed into numeric values with units of `seconds`, `meters`, or `points`. Unparseable or absent scores remain null. |
| Club matching | Results club names are matched to the club dimension by normalized exact matching first and fuzzy matching second. Unmatched clubs use `geography_key = -1` (`Unknown`). |
| Orphan athlete codes | Result rows whose codes do not exist in Certifications are retained in `fact_results` with nullable `athlete_key`; rows without an athlete key are excluded from `fact_participation`. |
| Power BI transformations | Heavy cleaning and shaping are done in Python. Power BI is limited to import typing, relationships, DAX measures, and report visuals. |

## Business question coverage

| Business question | Supported by |
| ----------------- | ------------ |
| Participant distribution by age, gender, and sport | `dim_athlete`, `dim_sport`, `fact_participation`, `fact_results` |
| Average age by discipline and performance | `dim_athlete`, `dim_sport`, `fact_results` |
| Multi-discipline or sport-changing athletes | `fact_participation`, `fact_results`, `dim_sport`, `dim_time` |
| Experience vs final performance | `fact_participation`, `fact_results`, `dim_time` |
| Year-to-year development and score improvement | `fact_results`, `dim_event`, `dim_time` |
| Best results and medals | `fact_results`, `dim_event`, `dim_sport` |
| Disqualification percentage / 20 percent rule proxy | `fact_results.is_disqualified`, DQ-rate DAX measure |
| Regions with most participants | `dim_geography`, `fact_participation`, `fact_results` |
| Club size vs performance or participation rate | `dim_geography`, `dim_athlete`, `fact_participation`, `fact_results` |

## Self-evaluation against assignment requirements

| Requirement | Status | Evidence |
| ----------- | ------ | -------- |
| Weekly project planning | Complete | `pm/r0984834_ProjectPlan.md` |
| Star schema with fact and dimension tables | Complete | `docs/md/dimensional_model.md`, `data/gold/` |
| Python ETL pipeline | Complete | `src/main.py`, `src/orchestration/pipeline.py`, `src/bronze`, `src/silver`, `src/gold`, `src/quality` |
| OOP principles | Complete | Layer-specific base classes and concrete extractor, cleaner, transformer, and validator classes |
| Raw and clean data separation | Complete | `data/raw`, `data/bronze`, `data/silver`, `data/gold` |
| Required CSV naming convention | Complete | `dim_*.csv` and `fact_*.csv` in `data/gold` |
| Power BI semantic model | Complete | `pbix/r0984834_Dashboard.pbix`, `pbix/README.md` |
| Heavy transformations in Python, not Power BI | Complete | Python handles extraction, cleaning, deduplication, normalization, key generation, and facts/dimensions |
| Business-question dashboard coverage | Complete | Dashboard pages documented in `pbix/README.md` and screenshots in `pbix/pages` |
| Technical documentation and data audit | Complete | `docs/md/data_exploration.md`, `docs/md/dimensional_model.md`, this document |
| Validation evidence | Complete for ETL outputs | `src/quality` reports 68/68 checks passed; Power BI vs Excel screenshots were completed manually and are out of scope for this task |
| AI usage disclosure | Complete | `AI.md` |
| Medallion architecture bonus | Complete | Bronze, silver, and gold layers are implemented and documented |
| MySQL bonus | Not implemented | The final project uses CSV files loaded into Power BI, not a MySQL-backed semantic model |

## Known limitations

- The validation module proves the generated gold-layer CSVs satisfy expected schemas, row ranges, key integrity, value domains, and uniqueness checks. It does not replace the manually prepared Power BI vs Excel screenshot evidence.
- Some source values are incomplete by design, especially missing places/scores in qualifying or team-sport rows. Those are preserved as nulls after cleaning rather than forced into artificial values.
- Some result athlete codes do not exist in the Certifications master list. These rows are retained for performance analysis but cannot contribute to athlete-dimension demographic analysis.
- Club matching uses a deterministic fuzzy threshold. Remaining unmatched clubs are assigned to `Unknown` so Power BI relationships remain valid.
- The Power BI `.pbix` file is manually maintained; this repository documents its model and measures but does not programmatically generate visuals.

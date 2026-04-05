# Power BI Setup — Special Olympics Dashboard

## 1. Data Import

All 7 CSVs from `data/gold/` were imported via **Get Data → Text/CSV**:

| File                     | Table Name           |
| ------------------------ | -------------------- |
| `dim_athlete.csv`        | `dim_athlete`        |
| `dim_geography.csv`      | `dim_geography`      |
| `dim_sport.csv`          | `dim_sport`          |
| `dim_event.csv`          | `dim_event`          |
| `dim_time.csv`           | `dim_time`           |
| `fact_results.csv`       | `fact_results`       |
| `fact_participation.csv` | `fact_participation` |

**No transformations in Power Query** — all cleaning/shaping is handled by the Python ETL pipeline. Only data type verification was done on import.

## 2. Data Types

Verified in Power Query Editor after import:

### `dim_athlete`

| Column                     | Type         |
| -------------------------- | ------------ |
| `athlete_key`              | Whole Number |
| `code`                     | Text         |
| `person_type`              | Text         |
| `gender`                   | Text         |
| `date_of_birth`            | Date         |
| `age`                      | Whole Number |
| `has_mental_handicap_cert` | True/False   |
| `has_parents_consent_cert` | True/False   |
| `has_hap_cert`             | True/False   |
| `is_unified_partner_cert`  | True/False   |

### `dim_geography`

| Column             | Type         |
| ------------------ | ------------ |
| `geography_key`    | Whole Number |
| `club_id`          | Whole Number |
| `club_name`        | Text         |
| `province`         | Text         |
| `city`             | Text         |
| `country`          | Text         |
| `primary_language` | Text         |
| `zipcode`          | Text         |

### `dim_sport`

| Column       | Type         |
| ------------ | ------------ |
| `sport_key`  | Whole Number |
| `sport_name` | Text         |

### `dim_event`

| Column       | Type         |
| ------------ | ------------ |
| `event_key`  | Whole Number |
| `event_code` | Text         |
| `event_name` | Text         |
| `sport_key`  | Whole Number |

### `dim_time`

| Column         | Type         |
| -------------- | ------------ |
| `time_key`     | Whole Number |
| `year`         | Whole Number |
| `is_covid_gap` | True/False   |
| `period`       | Text         |

### `fact_results`

| Column            | Type           |
| ----------------- | -------------- |
| `result_key`      | Whole Number   |
| `athlete_key`     | Whole Number   |
| `geography_key`   | Whole Number   |
| `sport_key`       | Whole Number   |
| `event_key`       | Whole Number   |
| `time_key`        | Whole Number   |
| `rank`            | Whole Number   |
| `medal`           | Text           |
| `score_value`     | Decimal Number |
| `score_unit`      | Text           |
| `is_disqualified` | True/False     |
| `result_status`   | Text           |

### `fact_participation`

| Column           | Type         |
| ---------------- | ------------ |
| `athlete_key`    | Whole Number |
| `geography_key`  | Whole Number |
| `time_key`       | Whole Number |
| `events_entered` | Whole Number |
| `sports_entered` | Whole Number |

## 3. Relationships

Power BI auto-detected the relationships correctly. All are **One-to-Many**, **single cross-filter direction** (dimension → fact):

| From (1)                      | To (\*)                            | Key             |
| ----------------------------- | ---------------------------------- | --------------- |
| `dim_athlete.athlete_key`     | `fact_results.athlete_key`         | `athlete_key`   |
| `dim_athlete.athlete_key`     | `fact_participation.athlete_key`   | `athlete_key`   |
| `dim_geography.geography_key` | `fact_results.geography_key`       | `geography_key` |
| `dim_geography.geography_key` | `fact_participation.geography_key` | `geography_key` |
| `dim_sport.sport_key`         | `fact_results.sport_key`           | `sport_key`     |
| `dim_sport.sport_key`         | `dim_event.sport_key`              | `sport_key`     |
| `dim_event.event_key`         | `fact_results.event_key`           | `event_key`     |
| `dim_time.time_key`           | `fact_results.time_key`            | `time_key`      |
| `dim_time.time_key`           | `fact_participation.time_key`      | `time_key`      |

## 4. DAX Measures

### `fact_participation` table

#### Total Athletes

```dax
Total Athletes =
DISTINCTCOUNT(fact_participation[athlete_key])
```

Counts all unique participants across all years (includes Athletes, Unified Partners, Coaches, etc.).

#### Total Athletes (Type)

```dax
Total Athletes (Type) =
CALCULATE(
    DISTINCTCOUNT(fact_participation[athlete_key]),
    dim_athlete[person_type] = "Athlete"
)
```

Same as above but filtered to `person_type = "Athlete"` only — excludes coaches, volunteers, unified partners.

---

### `fact_results` table

#### Total Medals

```dax
Total Medals =
COUNTROWS(
    FILTER(fact_results, NOT(ISBLANK(fact_results[medal])))
)
```

Counts all rows where a medal was awarded (Gold, Silver, or Bronze).

#### Gold Medals

```dax
Gold Medals =
CALCULATE(
    COUNTROWS(fact_results),
    fact_results[medal] = "Gold"
)
```

#### Silver Medals

```dax
Silver Medals =
CALCULATE(
    COUNTROWS(fact_results),
    fact_results[medal] = "Silver"
)
```

#### Bronze Medals

```dax
Bronze Medals =
CALCULATE(
    COUNTROWS(fact_results),
    fact_results[medal] = "Bronze"
)
```

#### Total Events

```dax
Total Events =
DISTINCTCOUNT(fact_results[event_key])
```

Count of distinct events in the current filter context.

#### Total Sports

```dax
Total Sports =
DISTINCTCOUNT(fact_results[sport_key])
```

Count of distinct sports in the current filter context.

#### DQ Rate

```dax
DQ Rate =
DIVIDE(
    COUNTROWS(FILTER(fact_results, fact_results[is_disqualified] = TRUE())),
    COUNTROWS(fact_results),
    0
)
```

Ratio of disqualified results to total results. Returns 0 when there are no results (avoids division by zero).

---

### `dim_athlete` table

#### Avg Age

```dax
Avg Age =
AVERAGEX(
    FILTER(
        dim_athlete,
        dim_athlete[person_type] = "Athlete"
            && NOT(ISBLANK(dim_athlete[age]))
    ),
    dim_athlete[age]
)
```

Average age of athletes only (excluding coaches, volunteers, etc.), ignoring rows with missing DOB/age.

_This document was generated with the help of AI (Claude Opus 4.6)_

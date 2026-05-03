# Power BI Setup — Special Olympics Dashboard

Wireframe made in [docs/img/r0984834_Wireframe.png](../docs/img/r0984834_Wireframe.png).

If you are looking for the final PowerBI pages, open [./r0984834_Dashboard.pbix](./r0984834_Dashboard.pbix) in PowerBI or see [./pages](./pages).

Semantic model made in [docs/img/r0984834_Model.png](../docs/img/r0984834_Model.png), reflected in PowerBI too.

DAX Measures defined below.

Dashboard pages preview made in [pages](./pages/) - fully interactive once loaded in PowerBI.

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
CALCULATE(
    COUNTROWS(fact_results),
    fact_results[medal] IN {"Gold", "Silver", "Bronze"}
)
```

Counts all rows where a medal was awarded. Uses explicit value matching instead of `ISBLANK()` because the `medal` column contains empty strings (`""`) rather than true nulls for non-medal results.

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

#### Medal Rate

```dax
Medal Rate =
DIVIDE(
    CALCULATE(
        COUNTROWS(fact_results),
        fact_results[medal] IN {"Gold", "Silver", "Bronze"}
    ),
    COUNTROWS(fact_results),
    0
)
```

Percentage of results that earned a medal per sport. Complements DQ Rate — one shows failure rate, the other success rate.

#### New Athletes

```dax
New Athletes =
VAR CurrentYear = SELECTEDVALUE(dim_time[year])
RETURN
COUNTROWS(
    FILTER(
        VALUES(fact_participation[athlete_key]),
        CALCULATE(MIN(fact_participation[time_key]), ALL(dim_time)) = CurrentYear
    )
)
```

Athletes whose first-ever participation year matches the current year in context. 2015 shows 100% new (no prior data).

#### Returning Athletes

```dax
Returning Athletes =
VAR CurrentYear = SELECTEDVALUE(dim_time[year])
RETURN
COUNTROWS(
    FILTER(
        VALUES(fact_participation[athlete_key]),
        CALCULATE(MIN(fact_participation[time_key]), ALL(dim_time)) < CurrentYear
    )
)
```

Athletes who participated in a prior year. Uses `ALL(dim_time)` to look across all years regardless of current filter context.

#### New Athlete %

```dax
New Athlete % =
DIVIDE([New Athletes], [New Athletes] + [Returning Athletes], 0)
```

Ratio of new athletes to total participants for combo chart overlay.

#### Club Size

```dax
Club Size = DISTINCTCOUNT(fact_participation[athlete_key])
```

Count of distinct athletes per club in current filter context. Used in Club vs Performance scatter plot.

#### Medals Per Athlete

```dax
Medals Per Athlete = DIVIDE([Total Medals], [Club Size], 0)
```

Average medals earned per athlete at a club. Higher = more productive club.

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
            && COUNTROWS(RELATEDTABLE(fact_results)) > 0
    ),
    dim_athlete[age]
)
```

Average age of athletes only (excluding coaches, volunteers, etc.), ignoring rows with missing DOB/age.

#### Participation Count

```dax
Participation Count =
CALCULATE(
    DISTINCTCOUNT(fact_participation[athlete_key]),
    USERELATIONSHIP(fact_participation[time_key], dim_time[time_key])
)
```

Distinct athlete count per year, using `USERELATIONSHIP` to activate the inactive `fact_participation → dim_time` relationship (needed because `fact_results → dim_time` is the active one).

#### Athletes by Sport

```dax
Athletes by Sport =
DISTINCTCOUNT(fact_results[athlete_key])
```

Count of distinct athletes in the current filter context (used for the Athletes by Sport bar chart).

#### Years Active

```dax
Years Active = DISTINCTCOUNT(fact_participation[time_key])
```

Count of distinct years an athlete participated. Used in the Multi-Sport Athletes table.

---

## 4b. Calculated Columns

### `dim_athlete` table

#### Age Group

```dax
Age Group =
SWITCH(
    TRUE(),
    dim_athlete[age] < 10, "0-9",
    dim_athlete[age] < 20, "10-19",
    dim_athlete[age] < 30, "20-29",
    dim_athlete[age] < 40, "30-39",
    dim_athlete[age] < 50, "40-49",
    dim_athlete[age] < 60, "50-59",
    dim_athlete[age] < 70, "60-69",
    "70+"
)
```

Bins athlete ages into decade groups for histogram visuals. Created as a **calculated column** (not a measure) because it evaluates row-by-row.

### `dim_geography` table

#### Province Full

```dax
Province Full = dim_geography[province] & ", " & dim_geography[country]
```

Disambiguates province names that exist in multiple countries (e.g., "Limburg" in both Belgium and Netherlands). Created for map visuals but replaced by Treemap approach due to Bing geocoding limitations.

---

## 5. Page 1: Overview

Layout based on the wireframe ([docs/img/r0984834_Wireframe.png](../docs/img/r0984834_Wireframe.png)) — PAGE 1: Overview.

### KPI Cards (top row)

Three **Card** visuals arranged horizontally across the top:

| Card | Measure            | Format                |
| ---- | ------------------ | --------------------- |
| 1    | `[Total Athletes]` | Whole number          |
| 2    | `[Total Medals]`   | Whole number          |
| 3    | `[DQ Rate]`        | Percentage, 1 decimal |

### Participation Over Time

- **Visual type:** Line Chart
- **X-axis:** `dim_time[year]`
- **Y-axis:** `[Participation Count]`
- **Note:** 2020–2021 gap (COVID) appears naturally as missing data points.

### Gender Split

- **Visual type:** Donut Chart
- **Legend:** `dim_athlete[gender]`
- **Values:** `[Total Athletes]`

### Athletes by Sport

- **Visual type:** Clustered Bar Chart
- **Y-axis:** `dim_sport[sport_name]`
- **X-axis:** `[Athletes by Sport]`
- **Sort:** Descending by `[Athletes by Sport]`

### Medals by Year

- **Visual type:** Stacked Area Chart
- **X-axis:** `dim_time[year]`
- **Y-axis:** `[Total Medals]`
- **Legend:** `fact_results[medal]`
- **Legend colors:** Gold `#FFD700`, Silver `#C0C0C0`, Bronze `#CD7F32`

### Slicers (bottom row)

Three **Slicer** visuals (Dropdown style):

| Slicer | Field                     |
| ------ | ------------------------- |
| Year   | `dim_time[year]`          |
| Sport  | `dim_sport[sport_name]`   |
| Region | `dim_geography[province]` |

---

## 6. Page 2: Athlete Demographics

Layout based on the wireframe — PAGE 2: Athlete Demographics.

### Age Distribution (Histogram)

- **Visual type:** Clustered Column Chart
- **X-axis:** `dim_athlete[Age Group]` (calculated column)
- **Y-axis:** Count of `dim_athlete[athlete_key]`
- **Page-level filter:** `dim_athlete[person_type]` = `"Athlete"`

### Person by Type

- **Visual type:** Pie Chart
- **Legend:** `dim_athlete[person_type]`
- **Values:** Count of `dim_athlete[athlete_key]`

### Average Age by Sport

- **Visual type:** Clustered Bar Chart
- **Y-axis:** `dim_sport[sport_name]`
- **X-axis:** `[Avg Age]`
- **Sort:** Descending by `[Avg Age]`
- **Note:** Avg Age routes through `fact_results` via `RELATEDTABLE` so the sport filter context applies correctly.

### Multi-Sport Athletes

- **Visual type:** Table
- **Columns:** `dim_athlete[code]`, `[Total Sports]`, `[Total Events]`, `[Years Active]`
- **Visual-level filter:** `[Total Sports]` is greater than 1
- **Totals row:** Off (DISTINCTCOUNT totals are misleading for this table)
- **Excluded:** Blank codes

### New vs Returning Athletes

- **Visual type:** Line and Stacked Column Chart (combo)
- **X-axis:** `dim_time[year]`
- **Column Y-axis:** `[New Athletes]`, `[Returning Athletes]` (stacked bars, absolute counts)
- **Line Y-axis:** `[New Athlete %]` (percentage overlay on secondary axis)
- **Note:** 2015 shows 100% new (no prior data). Post-COVID 2022 shows spike in "returning" athletes.

### Slicers

Three **Slicer** visuals (Dropdown style):

| Slicer      | Field                      |
| ----------- | -------------------------- |
| Year        | `dim_time[year]`           |
| Gender      | `dim_athlete[gender]`      |
| Person Type | `dim_athlete[person_type]` |

---

## 7. Page 3: Performance and Trends

Layout based on the wireframe — PAGE 3: Performance and Trends.

### Medal Cards (top row)

Three **Card** visuals arranged horizontally:

| Card   | Measure           | Color            |
| ------ | ----------------- | ---------------- |
| Gold   | `[Gold Medals]`   | Gold `#FFD700`   |
| Silver | `[Silver Medals]` | Silver `#C0C0C0` |
| Bronze | `[Bronze Medals]` | Bronze `#CD7F32` |

### Medal Trends

- **Visual type:** Line Chart
- **X-axis:** `dim_time[year]`
- **Legend:** `fact_results[medal]`
- **Values:** Count of `fact_results[result_key]`
- **Visual-level filter:** `fact_results[medal]` IN {Gold, Silver, Bronze} (exclude blanks)

### DQ Rate by Sport

- **Visual type:** Clustered Bar Chart
- **Y-axis:** `dim_sport[sport_name]`
- **X-axis:** `[DQ Rate]` (formatted as percentage)
- **Sort:** Descending by `[DQ Rate]`

### Medal Rate by Sport

- **Visual type:** Clustered Bar Chart
- **Y-axis:** `dim_sport[sport_name]`
- **X-axis:** `[Medal Rate]` (formatted as percentage)
- **Sort:** Descending by `[Medal Rate]`
- **Note:** Complements DQ Rate — shows which sports have the highest medal conversion rate.

### Top Results Table

- **Visual type:** Table
- **Columns:** `dim_athlete[code]`, `dim_event[event_name]`, `dim_sport[sport_name]`, `fact_results[score_value]`, `dim_time[year]`
- **Visual-level filter:** `fact_results[rank]` = 1 (first-place results only)

### Slicers

Four **Slicer** visuals (Dropdown style):

| Slicer | Field                   |
| ------ | ----------------------- |
| Year   | `dim_time[year]`        |
| Sport  | `dim_sport[sport_name]` |
| Event  | `dim_event[event_name]` |
| Medal  | `fact_results[medal]`   |

---

## 8. Page 4: Regional Analysis

Layout based on the wireframe — PAGE 4: Regional Analysis.

### Participants by Province

- **Visual type:** Treemap
- **Group:** `dim_geography[province]`
- **Values:** `[Total Athletes]` (distinct count of athletes)
- **Visual-level filter:** Exclude blank provinces
- **Note:** Filled Map was attempted but Bing geocoding couldn't reliably resolve Belgian provinces (especially "Limburg" which exists in both Belgium and Netherlands). Treemap is the fallback.

### Language Split

- **Visual type:** Donut Chart
- **Legend:** `dim_geography[primary_language]`
- **Values:** `[Total Athletes]`

### Club vs Performance

- **Visual type:** Scatter Chart
- **X-axis:** `[Club Size]`
- **Y-axis:** `[Medals Per Athlete]`
- **Details:** `dim_geography[club_name]` (each dot = one club)
- **Note:** Shows whether larger clubs produce more medals per athlete or if small clubs can be equally productive.

### Top Clubs Table

- **Visual type:** Table
- **Columns:** `dim_geography[club_name]`, `dim_geography[province]`, `[Total Athletes]`, `[Total Medals]`, `[Total Events]`
- **Sort:** Descending by `[Total Medals]`

### Slicers

Three **Slicer** visuals (Dropdown style):

| Slicer   | Field                             |
| -------- | --------------------------------- |
| Year     | `dim_time[year]`                  |
| Province | `dim_geography[province]`         |
| Language | `dim_geography[primary_language]` |

_This document was generated with the help of AI (Claude Opus 4.6), dashboard may not reflect this documentation_

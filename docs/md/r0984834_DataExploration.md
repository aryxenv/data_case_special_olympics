# Data Exploration Report

> Auto-generated profiling of raw source files for the Special Olympics ETL pipeline.

## 1. Certifications File (`Thomas More Data Certifications.xlsx`)

### Structure

| Property     | Value                                                                                                                                                                                                   |
| ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Sheets       | 1 (`Sheet1`)                                                                                                                                                                                            |
| Rows         | 21 001                                                                                                                                                                                                  |
| Columns (10) | `Club`, `Code`, `Person type`, `Gender`, `DOB`, `Age`, `Mental Handicap (SOB has this certificate)`, `Parents Consent (SOB has this certificate)`, `HAP (SOB has this certificate)`, `Unified Partner (SOB has this certificate)` |

**Column dtypes:**

| Column                                           | Dtype          |
| ------------------------------------------------ | -------------- |
| Club                                             | object (str)   |
| Code                                             | object (str)   |
| Person type                                      | object (str)   |
| Gender                                           | object (str)   |
| DOB                                              | datetime64[ns] |
| Age                                              | float64        |
| Mental Handicap (SOB has this certificate)       | float64        |
| Parents Consent (SOB has this certificate)       | float64        |
| HAP (SOB has this certificate)                   | float64        |
| Unified Partner (SOB has this certificate)       | float64        |

---

### Column Analysis

#### Code (Primary Key)

- **Unique values:** 20 221 (across 20 221 non-null rows)
- **Missing:** 780 (3.71 %) — all belong to completely empty rows (see *Duplicates* below)
- **Duplicates among non-null codes:** 0 ✅ — `Code` is unique when present
- **Format:** 16-character uppercase alphanumeric string (e.g. `3B1D6O9Z08W7IOZG`). All codes are exactly 16 characters.

#### Gender

| Value | Count  | %      |
| ----- | ------ | ------ |
| M     | 12 530 | 59.66% |
| F     | 7 640  | 36.38% |
| U     | 51     | 0.24%  |
| NaN   | 780    | 3.71%  |

- Three distinct values: `M`, `F`, `U` (unknown/unspecified).
- The 51 `U` rows span Athletes (17), Unified Partners (22), Coaches (9), Volunteers (2), and A-HOD (1).
- No `Male`/`Female` long-form variants — gender is already short-form.

#### DOB (Date of Birth)

- **Dtype:** `datetime64[ns]` — already parsed as dates.
- **Missing:** 1 990 (9.48 %) — significantly more than the 780 empty rows, so ~1 210 real records also lack a DOB.
- **Range:** 1900-01-02 → 2020-12-05

**Decade distribution:**

| Decade | Count |
| ------ | ----- |
| 1900   | 6     |
| 1920   | 1     |
| 1930   | 14    |
| 1940   | 209   |
| 1950   | 1 171 |
| 1960   | 2 584 |
| 1970   | 2 939 |
| 1980   | 3 622 |
| 1990   | 4 515 |
| 2000   | 3 300 |
| 2010   | 648   |
| 2020   | 2     |

**Suspicious dates:**

- 6 rows have DOB = `1900-01-02` → likely a placeholder/sentinel value (all have Age = 125).
- 1 row has DOB = `1921-10-24` (Age 104) — possibly valid but worth flagging.
- 2 rows in 2020 — valid (young athletes born in 2020).

#### Age

- **Missing:** 780 (the empty rows)
- **Range:** 0 – 125
- **Mean:** 37.7, **Median:** 36
- **Age = 0:** 1 210 rows — these are Coaches/staff whose DOB is missing (`NaT`), so age was set to 0 rather than null. This is a data quality issue.
- **Age > 100:** 7 rows — the 6 sentinel-date rows (age 125) plus the 1921 record (age 104).

#### Person Type

| Value           | Count  | %      |
| --------------- | ------ | ------ |
| Athlete         | 15 864 | 75.54% |
| Coach           | 3 801  | 18.10% |
| Unified Partner | 516    | 2.46%  |
| NaN             | 780    | 3.71%  |
| Staff           | 19     | 0.09%  |
| Volunteer       | 6      | 0.03%  |
| Head Coach      | 3      |        |
| VIP             | 2      |        |
| Medical         | 2      |        |
| Security        | 2      |        |
| A-HOD           | 2      |        |
| Manager         | 1      |        |
| Family member   | 1      |        |
| Media           | 1      |        |
| AS-Staff        | 1      |        |

- 14 distinct person types (plus NaN).
- The core categories for the dashboard are **Athlete** (75.5 %), **Coach** (18.1 %), and **Unified Partner** (2.5 %).
- The remaining 10 types are rare (≤ 19 rows each) — decide during ETL whether to group them as "Other" or filter them out.

#### Club

- **Unique clubs:** 434
- **Missing:** 780 (the empty rows)
- **Largest club:** `General` with 7 310 members (34.8 %) — this appears to be a catch-all/default assignment, not a real club.
- Remaining clubs range from 1 to 367 members (`SOMIVAL VZW` = 367, `CENTRE REINE FABIOLA` = 259).
- Club names are uppercase strings, some with accented characters (e.g. `16 ÂMES`, `LE JARDIN DES FÉES`).
- One foreign club: `HAGEN (Germany)`.

#### Certificate Columns

All four certificate columns are binary flags (1.0 = has certificate, 0.0 = explicitly no, NaN = not recorded):

| Certificate      | Has (1) | No (0) | NaN (missing) |
| ---------------- | ------- | ------ | ------------- |
| Mental Handicap  | 9 795   | 18     | 11 188        |
| Parents Consent  | 6 616   | 27     | 14 358        |
| HAP              | 5 526   | 1      | 15 474        |
| Unified Partner  | 183     | 0      | 20 818        |

- High NaN rates are expected: certificates only apply to certain person types.
- The rare `0` values (18, 27, 1) suggest the column is mostly used as "has certificate" with NaN meaning "not applicable" rather than "unknown".
- 183 people have the Unified Partner certificate: 143 are typed as Unified Partner, 39 are Coaches, 1 is an Athlete.

---

### Data Quality Issues

| # | Issue | Severity | Rows Affected | Notes |
|---|-------|----------|---------------|-------|
| 1 | **780 completely empty rows** | 🔴 High | 780 (3.7 %) | Every column is NaN. These are padding/blank rows that must be dropped. |
| 2 | **DOB missing for ~1 210 real records** | 🟡 Medium | 1 210 (5.8 %) | Mostly Coaches — they have Age = 0 instead of NaN, masking the missing value. |
| 3 | **Age = 0 for missing DOBs** | 🟡 Medium | 1 210 | Age was computed as 0 when DOB is missing. ETL should set Age = NaN when DOB is missing. |
| 4 | **Sentinel DOB `1900-01-02`** | 🟡 Medium | 6 | Placeholder date yielding Age = 125. Replace with NaN during ETL. |
| 5 | **Gender = `U`** | 🟠 Low | 51 | Unknown/unspecified gender. Decide whether to keep as-is or map to NaN. |
| 6 | **`General` club (catch-all)** | 🟠 Low | 7 310 (34.8 %) | Not a real club — may need special handling when joining with Clubs file. |
| 7 | **Rare person types** | 🟠 Low | 40 | 10 types with ≤ 19 rows. Consider grouping as "Other" for analysis. |
| 8 | **Certificate `0` vs `NaN` ambiguity** | 🟠 Low | 46 total | A few rows have explicit `0` instead of NaN. Clarify meaning (refused vs not applicable?). |

---

### Key Observations

1. **Code is a reliable primary key** — 16-char alphanumeric, unique across all non-null rows. Safe to use as `AthleteID`.
2. **No gender standardization needed** — already uses `M`/`F` (no `Male`/`Female` variants). `U` is the only extra value.
3. **DOB is already datetime** — no parsing required, but sentinel values (`1900-01-02`) and missing values need cleanup.
4. **The "General" club dominates** — over a third of all records. This will need special handling in the geography dimension and when fuzzy-matching clubs from the Results files.
5. **Coaches lack DOBs** — Age = 0 is a red flag. The ETL should null-out Age when DOB is missing rather than defaulting to 0.
6. **Person type filtering** — for the `dim_athletes` dimension, likely only Athlete + Unified Partner rows should be included. Coaches and other staff may be excluded or placed in a separate dimension.
7. **Certificate columns are sparse** — useful for athlete profiling but NaN-heavy. Consider whether they belong in `dim_athletes` or a separate fact/bridge table.

---

## 2. Clubs File (`Thomas More Data Clubs.xlsx`)

### Structure

| Property | Value |
|----------|-------|
| Sheets | `Sheet1` (single sheet) |
| Rows | 436 |
| Columns | 17 |

**Columns and dtypes:**

| Column | Dtype | Description |
|--------|-------|-------------|
| Group number | int64 | Club identifier |
| Name | object | Club name |
| Primary language | object | Dutch or French |
| Address (Street and Number) | object | Street address |
| Zipcode | float64 | Postal code |
| City | object | City name |
| Province | object | Belgian province |
| Country | object | Country name |
| Participation Games 2015 | float64 | 0/1 flag (NaN = did not exist yet) |
| Participation Games 2016 | bool | True/False flag |
| Participation Games 2017 | bool | True/False flag |
| Participation Games 2018 | bool | True/False flag |
| Participation Games 2019 | bool | True/False flag |
| Participation Games 2022 | float64 | 1.0 flag (NaN = no participation) |
| Participation Games 2023 | float64 | 1.0 flag (NaN = no participation) |
| Participation Games 2024 | float64 | 1.0 flag (NaN = no participation) |
| Participation Games 2025 | float64 | 1.0 flag (NaN = no participation) |

> **Note:** Participation columns have inconsistent dtypes — 2016–2019 are `bool` (True/False), while 2015 and 2022–2025 are `float64` (1.0/NaN). This must be standardized during ETL.

### Column Analysis

#### Group Number (primary key candidate)
- **Unique count:** 436 (= row count → **fully unique**)
- **Missing:** 0
- **Range:** 100–788
- **Format:** Integer, not sequential — 88 gaps in the sequence (e.g., 106 is missing, jumps from 105 to 107)
- **Conclusion:** Reliable primary key for the geography dimension

#### Name (join key with Results)
- **Unique count:** 436 (= row count → **fully unique**)
- **Missing:** 0
- **Length:** 3–41 characters (mean 14.3)
- **No duplicate names** — each club has a distinct name
- **Conclusion:** Usable as join key, but Results files may use variant spellings → fuzzy matching likely needed

#### Province
- **Unique count:** 24 distinct values
- **Missing:** 6 (1.4%)
- **Key issue: spelling/formatting inconsistencies** — same province appears under multiple names:

| Canonical Province | Variants Found |
|---|---|
| Antwerpen | `Antwerpen` (58), `ANTWERPEN` (3), `Antwerpen` (2) |
| Hainaut | `Hainaut` (76), `HAINAUT` (2) |
| Brabant Wallon | `Brabant Wallon` (19), `Babant Wallon` (1, **typo**), `Brabant-Wallon` (1) |
| Vlaams Brabant | `Vlaams Brabant` (28), `Vlaams-Brabant` (2) |
| Oost-Vlaanderen | `Oost-Vlaanderen` (48), `Oost Vlaanderen` (2) |
| West-Vlaanderen | `West-Vlaanderen` (44), `West-Vlaanderen` (1), `West- Vlaanderen` (1, extra space) |
| Brussel/Bruxelles | `Brussel/Bruxelles` (29), `Bruxelles` (5), `BRUSSEL` (1) |

- Erroneous values: `Belgie` (1) and `Wallonie` (1) are countries/regions, not provinces
- **Top provinces:** Hainaut (76), Antwerpen (58), Oost-Vlaanderen (48), West-Vlaanderen (44), Liège (39)

#### Country
- **Unique count:** 14 distinct values
- **Missing:** 74 (17.0%) — **highest missing rate** of the core columns
- **Key issue: extreme spelling inconsistency** — all refer to Belgium but in many forms:

| Variant | Count |
|---------|-------|
| BELGIQUE | 121 |
| BELGIË | 99 |
| Belgique | 42 |
| Belgie | 38 |
| BELGIE | 25 |
| Belgium | 25 |
| België | 5 |
| belgique | 1 |
| Belguim | 1 (typo) |
| Belgïe | 1 (encoding issue) |
| Belgïum | 1 (encoding issue) |

- Erroneous values: `WAREGEM` (1) — this is a city, not a country; `West-Vlaanderen` (1) — this is a province (row 433, Province/Country columns are **swapped**)
- `Luxembourg` (1) — the only non-Belgium country in the dataset

#### City
- **Unique count:** 345
- **Missing:** 0
- **Case inconsistency:** 277 cities in ALL CAPS (63.5%), 159 in mixed case, 0 in all lowercase
- Cities like `BRUXELLES` (21 clubs) and `Bruxelles` may coexist as separate entries
- Duplicate city names with different casing: e.g., `GENK` (3) vs `Genk` (4), `GENT` (3) vs potentially others, `LIEGE` (3) vs `Liège` (4)
- **Top cities:** BRUXELLES (21), GEEL (6), Liège (4), Genk (4), NAMUR (4), KORTRIJK (4)

#### Primary Language
- **Unique count:** 2 (`Dutch`, `French`)
- **Missing:** 0
- **Distribution:** Dutch 229 (52.5%), French 207 (47.5%)
- Clean column — no issues

#### Zipcode
- **Missing:** 3 (0.7%)
- **Range:** 1000–29900
- **Outlier:** Group 787 ("ATHLETES FOR HOPE") has zipcode `29900` — Belgian postal codes max at 9999. This is likely a data entry error (should be `2990` for Wuustwezel).
- **Dtype:** float64 (due to NaN values) — should be converted to string/int
- **ETL handling:** The silver layer enriches the 3 missing real-club zipcodes through Nominatim geocoding: Group 126 → `1435`, Group 297 → `4000`, Group 332 → `7131`.

#### Address (Street and Number)
- **Missing:** 2 (0.5%)
- Not needed for the geography dimension, but available for reference

### Data Quality Issues

| Issue | Severity | Affected Column(s) | Count | Notes |
|-------|----------|-------------------|-------|-------|
| Country spelling variants | 🔴 High | Country | 362 (all non-null) | 14 variants of essentially "Belgium" — must standardize |
| Country missing values | 🔴 High | Country | 74 (17%) | Can infer from Province (all Belgian provinces) |
| Province spelling inconsistencies | 🟡 Medium | Province | ~15 rows | Case differences, hyphens, typos ("Babant") |
| Province/Country swap | 🟡 Medium | Province, Country | 1 row (Group 786) | Province="Belgie", Country="West-Vlaanderen" — swapped |
| Province erroneous values | 🟡 Medium | Province | 2 rows | "Belgie" and "Wallonie" are not provinces |
| City case inconsistency | 🟡 Medium | City | All rows | Mix of ALL CAPS and Mixed case — standardize |
| Country erroneous values | 🟡 Medium | Country | 2 rows | "WAREGEM" is a city; "West-Vlaanderen" is a province |
| Zipcode missing values | 🟡 Medium | Zipcode | 3 rows | Enriched in silver via Nominatim geocoding |
| Zipcode outlier | 🟡 Medium | Zipcode | 1 row (Group 787) | 29900 → likely 2990 |
| Participation dtype mismatch | 🟠 Low | Participation cols | All rows | 2016–2019 are bool; others are float64 |
| Participation missing = no participation | 🟠 Low | Participation cols | Varies | NaN means "did not participate" (not truly missing) |
| Province missing | 🟠 Low | Province | 6 (1.4%) | May be inferable from City/Zipcode |

### Key Observations

1. **Group number is a reliable primary key** — 436 unique integers, no duplicates, no nulls. Use this as `ClubID` in `dim_geography`.

2. **Name is fully unique** — safe as a join key with Results, but fuzzy matching will be needed since Results files may use variant club name spellings.

3. **Country column needs major cleanup** — 14 spelling variants of "Belgium" plus encoding issues (`Belgïe`, `Belgïum`). ETL should normalize all to a single canonical form. One row has `Luxembourg` as a genuine non-Belgian entry.

4. **Province/Country swap on row 433** (Group 786: KHC SAINT-GEORGES) — the Province and Country values are reversed. ETL must detect and fix this.

5. **Participation columns are bonus data** — they indicate which years each club participated in games. The inconsistent dtypes (bool vs float) and the NaN-as-"no" pattern need standardization. These can feed into `fact_participation`.

6. **City casing is mixed** — 63.5% ALL CAPS, 36.5% mixed. Standardize to title case during ETL. Watch for semantic duplicates (e.g., `GENK` vs `Genk`).

7. **All clubs are Belgian** (except 1 Luxembourg entry) — the dataset is Belgium-centric. Province values map to Belgian provinces/regions. The 74 missing Country values can be safely filled with "Belgium".

8. **Zipcode stored as float** due to 3 NaN values — convert to string or nullable int, enrich the 3 missing real-club zipcodes, and fix the 29900 outlier (likely 2990).

9. **No fully duplicate rows** — the dataset is clean in terms of complete row duplication.

10. **The file has 17 columns but only 7 are needed for `dim_geography`**: Group number, Name, Province, City, Country, Primary language (and optionally Zipcode). The 9 Participation columns feed `fact_participation` instead.

---

## 3. Results Files (`Thomas More Results YYYY.xlsx`)

### Overview

| Property | Value |
|---|---|
| Total files | 9 |
| Year range | 2015–2025 |
| COVID gap | 2020 and 2021 missing (no files) |
| Total records | **112,375** rows across all 9 files |
| Sheet per file | 1 (`Sheet1`) |
| Unique athletes | 7,607 across all years |

---

### Per-Year Structure

| Year | Sheets | Column Count | Columns | Row Count |
|------|--------|-------------|---------|-----------|
| 2015 | Sheet1 | 11 | Code, Club, Sport, Role, DOB, Age, Gender, Event, Place, Score, Summary (all) | 14,756 |
| 2016 | Sheet1 | 11 | Code, Club, Sport, Role, DOB, Age, Gender, Event, Place, Score, Summary (all) | 12,849 |
| 2017 | Sheet1 | 11 | Code, Club, Sport, Role, DOB, Age, Gender, Event, Place, Score, Summary (all) | 14,363 |
| 2018 | Sheet1 | 11 | Code, Club, Sport, Role, DOB, Age, Gender, Event, Place, Score, Summary (all) | 13,554 |
| 2019 | Sheet1 | 11 | Code, Club, Sport, Role, DOB, Age, Gender, Event, Place, Score, Summary (all) | 14,009 |
| 2022 | Sheet1 | 11 | Code, Club, Sport, Role, DOB, Age, Gender, Event, Place, Score, Summary (all) | 9,409 |
| 2023 | Sheet1 | **10** | Code, Club, Sport, Role, DOB, Age, Gender, Event, Place, Score | 11,798 |
| 2024 | Sheet1 | 11 | Code, Club, Sport, Role, DOB, Age, Gender, Event, Place, Score, Summary (all) | 11,239 |
| 2025 | Sheet1 | 11 | Code, Club, Sport, Role, DOB, Age, Gender, Event, Place, Score, Summary (all) | 10,398 |

**Data type notes:**
- `Age` is `int64` in most years but `float64` in 2016, 2022, 2023, 2025 (due to missing values forcing float).
- `DOB` is parsed as `datetime64[ns]` in all years.
- All other columns are `object` (string).

---

### Schema Comparison

10 core columns are present in **all** 9 years. Only one column differs:

| Column | 2015 | 2016 | 2017 | 2018 | 2019 | 2022 | 2023 | 2024 | 2025 |
|--------|------|------|------|------|------|------|------|------|------|
| Code | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Club | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Sport | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Role | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| DOB | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Age | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Gender | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Event | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Place | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Score | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| **Summary (all)** | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | **✗** | ✓ | ✓ |

> **Schema drift:** The `Summary (all)` column is **missing in 2023 only**. This column contains free-text metadata (qualifying times, bib numbers, final results). The ETL must handle its absence for 2023.

---

### Column Analysis

#### Code (Athlete ID)

| Year | Unique Codes | Missing |
|------|-------------|---------|
| 2015 | 3,288 | 0 |
| 2016 | 3,231 | 4 |
| 2017 | 3,446 | 0 |
| 2018 | 3,419 | 0 |
| 2019 | 3,482 | 0 |
| 2022 | 2,393 | 11 |
| 2023 | 2,969 | 63 |
| 2024 | 2,858 | 0 |
| 2025 | 2,788 | 1 |

**Multi-year participation:**

| Appeared in N years | Athletes |
|---------------------|----------|
| 1 year only | 2,023 |
| 2 years | 1,320 |
| 3 years | 892 |
| 4 years | 847 |
| 5 years | 776 |
| 6 years | 423 |
| 7 years | 396 |
| 8 years | 413 |
| All 9 years | 517 |

- **Total unique athletes:** 7,607
- **Returning athletes (2+ years):** 5,584 (73.4%)
- **517 athletes competed in every single year** — strong core of long-term participants.
- Post-COVID (2022) shows a notable drop in athletes (~2,400 vs ~3,400 pre-COVID).

#### Club

| Year | Distinct Clubs | Missing |
|------|---------------|---------|
| 2015 | 300 | 0 |
| 2016 | 304 | 4 |
| 2017 | 319 | 0 |
| 2018 | 314 | 0 |
| 2019 | 319 | 0 |
| 2022 | 252 | 11 |
| 2023 | 289 | 63 |
| 2024 | 285 | 0 |
| 2025 | 284 | 1 |

- **Total distinct club names (raw):** 491
- Many club name variations that may refer to the same club — ETL will need **fuzzy matching** to the Clubs master file.
- Known spelling variations observed:
  - `BLIJDORP  BUGGENHOUT` vs `BLIJDORP BUGGENHOUT` (extra space)
  - `Foyer du Calydon` vs `Foyer du Calydron` (typo)
  - `SCHOOL @ WATERKANT` vs `SCHOOL@WATERKANT`
  - `LES QUATRE SAISONS` / `LES QUATRE SAISONS 2` / `LES QUATRES SAISONS` / `LES QUATRES SAISONS 2` (extra 's')
  - `G - Omnisportclub Vlaamse Ardennen` vs `G-OMNISPORTCLUB VLAAMSE ARDENNEN` (casing + spaces)
  - `G - SEPPE VZW` vs `G-SEPPE VZW`
  - Mixed casing: `BBC De Westhoek Zwevezele`, `GFC Waasland-Beveren vzw`, `SwimAcad`
  - `SO NL- ASVZ` / `SO NL- PLONS` / `SO Nederland` — Netherlands-based clubs

#### Sport

| Year | Distinct Sports | Missing |
|------|----------------|---------|
| 2015 | 20 | 0 |
| 2016 | 20 | 0 |
| 2017 | 20 | 0 |
| 2018 | 20 | 0 |
| 2019 | 21 | 0 |
| 2022 | 16 | 0 |
| 2023 | 21 | 0 |
| 2024 | 19 | 0 |
| 2025 | 18 | 0 |

**All 23 distinct sports across all years:**
Adapted Physical Activities, Aquatics/Swimming, Athletics/Track and Field, Badminton, Basketball, Bocce, Bowling, Cycling, Equestrian, Floorball, Football/Soccer, Gymnastics (Artistic), Gymnastics (Rhythmic), Judo, Kayaking, Motor Activities, Netball, Sailing, Sportgames, Swimming, Table Tennis, Tennis, Triathlon

**Naming issue:** Both `Aquatics/Swimming` and `Swimming` exist as separate sport names. The ETL must determine whether these are truly separate or need merging. `Aquatics/Swimming` events have `AQ` codes while `Swimming` events have `SW` codes — they appear to be **different competition categories** (pool lengths differ: AQ uses 25m/50m/100m, SW uses 33m/66m/99m).

#### Event

| Year | Distinct Events | Missing |
|------|----------------|---------|
| 2015 | 136 | 0 |
| 2016 | 148 | 0 |
| 2017 | 140 | 0 |
| 2018 | 136 | 0 |
| 2019 | 129 | 0 |
| 2022 | 118 | 0 |
| 2023 | 143 | 0 |
| 2024 | 140 | 0 |
| 2025 | 138 | 0 |

- **Total distinct event names:** 375
- Events are **never missing** in any year.
- **Naming inconsistency is the biggest issue:**
  - Bilingual naming with inconsistent order: `AT17 - Softbalwerpen/Lancement softball` vs `AT17 - Lancement de softball/Softbalwerpen`
  - Year-to-year renames: `AT16 - Saut en longueur sans élan/Staande vertesprong` vs `AT16 - Verspringen zonder aanloop/Saut en longueur sans élan`
  - Typos: `APA - Staande hoogtespsrong` (missing 'r')
  - Prefix variations: `BO - Simple/Individueel` vs `BOI - Bocce Singles`
  - Copy artifacts: `(copy of) CY-Divisioning3-15 km`
  - Inconsistent formatting in APA events: some have `/` bilingual format, others use single language
  - Football events: `FO - 7 A Side Team`, `FO - Soccer 7 A Side Team`, `FINALES FO - 7 A Side Team`, `Finales  FO - 7 A Side Team`

#### Place (Rank)

| Year | Distinct Values | Missing | Missing % |
|------|----------------|---------|-----------|
| 2015 | 19 | 4,234 | 28.7% |
| 2016 | 24 | 2,880 | 22.4% |
| 2017 | 34 | 2,867 | 20.0% |
| 2018 | 37 | 2,766 | 20.4% |
| 2019 | 36 | 3,033 | 21.7% |
| 2022 | 31 | 2,145 | 22.8% |
| 2023 | 37 | 2,549 | 21.6% |
| 2024 | 33 | 2,712 | 24.1% |
| 2025 | 27 | 4,244 | **40.8%** |

**Total distinct Place values: 63**

Place values fall into these categories:

| Category | Values | Notes |
|----------|--------|-------|
| **Ordinal positions** | `1st`, `2nd`, `3rd`, `4th`, `5th`, `6th`, `7th`, `8th`, `10th` | Standard rankings — need to parse to integers |
| **Disqualifications** | `DQ`, `DQ-HE`, `DQ-ME`, `DQ-LI`, `DQ-FAL`, `DQ-FOU`, `DQ-GATE`, `DQ-INT`, `DQ-SUIT`, `DQ-TEC`, `DQ-USC`, `DQ: HE` | Multiple DQ reason codes; note `DQ: HE` vs `DQ-HE` inconsistency |
| **Did Not Start/Finish** | `DNS`, `DNF`, `DNC`, `DNT` | Non-completion codes |
| **Aquatics levels** | `AQ 0.1`–`AQ 6.2`, `AQ B.2`–`AQ C.6` | 30+ distinct AQ-prefixed values — appears to be skill-level classifications, NOT rankings |
| **Other** | `Part` (participation), `ZERO`, `SW7.2.2` | Edge cases |

**Key ETL decisions needed:**
- Parse `1st`→1, `2nd`→2, etc. for medal derivation
- Map all `DQ*` codes → disqualified flag (normalize `DQ: HE` to `DQ-HE`)
- Handle `DNS`/`DNF`/`DNC`/`DNT` as non-participation
- Decide how to treat `AQ X.Y` values (aquatics-specific classification, not place)
- 2025 has 40.8% missing — much higher than other years

#### Score

| Year | Non-null | Total | Missing | Missing % |
|------|----------|-------|---------|-----------|
| 2015 | 10,465 | 14,756 | 4,291 | 29.1% |
| 2016 | 10,099 | 12,849 | 2,750 | 21.4% |
| 2017 | 11,484 | 14,363 | 2,879 | 20.0% |
| 2018 | 9,839 | 13,554 | 3,715 | 27.4% |
| 2019 | 10,120 | 14,009 | 3,889 | 27.8% |
| 2022 | 7,367 | 9,409 | 2,042 | 21.7% |
| 2023 | 8,886 | 11,798 | 2,912 | 24.7% |
| 2024 | 8,568 | 11,239 | 2,671 | 23.8% |
| 2025 | 6,679 | 10,398 | 3,719 | **35.8%** |

**Score format patterns (all years use the same verbose format):**

| Pattern | Example | Frequency | ETL Action |
|---------|---------|-----------|------------|
| `X min, Y.ZZ sec` | `0 min, 8.89 sec`, `13 min, 27.00 sec` | Very common | Parse to total seconds |
| `X hr, Y min, Z.ZZ sec` | `2 hr, 3 min, 51.93 sec` | Rare (long races) | Parse to total seconds |
| `Xm, Y.ZZcm` | `18m, 28.00cm`, `0m, 30.00cm` | Common (field events) | Parse to total meters |
| `X points` / `X.XX points` | `8 points`, `57.90 points` | Common (judged sports) | Extract numeric value |
| `DNS` | `DNS` | Rare (in 2024) | Mark as non-participation |

> **Consistent format:** Unlike the initial project spec's expectation of formats like `"2m 50"` or `"00:15.00"`, the actual data uses a **single verbose format** consistently: `X min, Y.ZZ sec` for times, `Xm, Y.ZZcm` for distances. This simplifies parsing significantly. There are no bare numeric values (`"15.00"`) or colon-delimited times (`"00:15.00"`).

---

### Row Count Trends

```
Year  | Rows    | Athletes | Bar
------+---------+----------+--------------------------------------------
2015  | 14,756  | 3,288    | ████████████████████████████████████████
2016  | 12,849  | 3,231    | ██████████████████████████████████
2017  | 14,363  | 3,446    | ██████████████████████████████████████
2018  | 13,554  | 3,419    | ████████████████████████████████████
2019  | 14,009  | 3,482    | █████████████████████████████████████
--- COVID GAP: 2020, 2021 ---
2022  |  9,409  | 2,393    | █████████████████████████
2023  | 11,798  | 2,969    | ███████████████████████████████
2024  | 11,239  | 2,858    | ██████████████████████████████
2025  | 10,398  | 2,788    | ████████████████████████████
```

- Pre-COVID (2015–2019): ~13,000–14,800 rows, ~3,200–3,500 athletes
- Post-COVID (2022–2025): ~9,400–11,800 rows, ~2,400–3,000 athletes
- **~25% participation drop** post-COVID that has not fully recovered

---

### Data Quality Issues

#### 1. Significant Duplicate Rows (Critical)

| Year | Duplicates on (Code+Event+Sport) | % of rows |
|------|----------------------------------|-----------|
| 2015 | 7,563 | 51.3% |
| 2016 | 5,836 | 45.4% |
| 2017 | 6,938 | 48.3% |
| 2018 | 6,117 | 45.1% |
| 2019 | 6,735 | 48.1% |
| 2022 | 3,964 | 42.1% |
| 2023 | 5,539 | 46.9% |
| 2024 | 5,008 | 44.6% |
| 2025 | 4,101 | 39.4% |

**This is NOT actual duplication — it's a data structure issue.** The same athlete+event combination appears multiple times because the export includes **multiple rounds** (qualifying, preliminary, final) as separate rows. The `Score` column contains different values per row (e.g., qualifying score vs final score), and the `Summary (all)` column contains the consolidated view. The ETL pipeline must:
- **Decide which row to keep** — likely the final/medal round result
- Use `Summary (all)` to disambiguate when available
- Handle 2023 where `Summary (all)` is missing

#### 2. Missing Values Pattern

| Column | Pattern |
|--------|---------|
| **Place** | 20–41% missing across years. Highest in 2015 (28.7%) and 2025 (40.8%). Missing Place likely corresponds to divisioning/qualifying rounds where no ranking is assigned. |
| **Score** | 20–36% missing. Correlated with Place missingness. Missing Score appears in team sports and divisioning rounds. 2025 has the highest rate (35.8%). |
| **Code** | Near-complete, but 2023 has 63 missing codes (0.5%) — correlated with 63 missing values in Club, Role, Age, Gender (entire athlete row data missing). |
| **DOB** | Small number missing: 5 (2015), 4 (2016), 13 (2017), 8 (2019), 11 (2022), 68 (2023), 6 (2024), 24 (2025). |

#### 3. Gender Inconsistencies

- Most years: `Male` / `Female` only
- 2016, 2018, 2025: include `Unknown` (4, 4, and 3 rows respectively)
- 2016, 2022, 2023, 2025: have NaN gender values (tied to entirely missing athlete records)
- Gender values are consistently `Male`/`Female` — no `M`/`F` abbreviations found in Results files

#### 4. Schema Drift

- 2023 is missing the `Summary (all)` column — this column contains valuable metadata (qualifying times, bib numbers, level info, preliminary scores) that helps disambiguate multi-row records.

#### 5. Place Value Inconsistency

- DQ codes are inconsistent: `DQ-HE` vs `DQ: HE` (colon vs hyphen)
- Aquatics-specific level codes (`AQ 0.1`, `AQ 1.5`, etc.) mixed in with actual ranking values — these need separate handling

#### 6. Score Contains Non-Score Values

- The string `DNS` appears in the Score column in 2024, mixing status codes with actual scores
- All scores are string-formatted, requiring parsing of 3 distinct patterns (time, distance, points)

#### 7. Event Name Instability

- 375 distinct event names across 9 years, but many are the **same event with different bilingual orderings** (Dutch/French swap)
- The ETL should normalize event names, possibly by using the event code prefix (e.g., `AT17`, `AQ15`, `CY05`)

---

### Key Observations

1. **Multi-round data structure:** The largest data quality challenge is that each file contains multiple rows per athlete per event (qualifying, preliminary, final rounds). With ~45% of rows being "duplicates" on Code+Event+Sport, the ETL must implement **round disambiguation logic**.

2. **Score parsing is simpler than expected:** All scores use a consistent verbose format (`X min, Y.ZZ sec` / `Xm, Y.ZZcm` / `X.XX points`), not the varied formats originally anticipated.

3. **Post-COVID decline:** Participation dropped ~25% after the 2020–2021 gap and has not fully recovered by 2025.

4. **2023 is the most problematic year:** Missing `Summary (all)` column, highest Code missing rate (63 rows), will be hardest to deduplicate.

5. **2025 has highest missing rates:** Place missing at 40.8% and Score at 35.8% — may indicate incomplete/ongoing data or a format change.

6. **Event normalization is critical:** With 375 distinct event names (many just bilingual flips), the ETL should extract event code prefixes for reliable matching.

7. **Club name fuzzy matching needed:** 491 raw club names with known spelling variations, casing differences, and extra spaces must be matched to the master Clubs file.

8. **Aquatics dual naming:** `Aquatics/Swimming` (AQ events, 25m/50m pool) and `Swimming` (SW events, 33m/66m pool) are distinct competition formats — do **not** merge them.

---

## 4. Cross-File Relationships

### Code Linkage (Results ↔ Certifications)

The `Code` column is the primary join key between Results and the Certifications master list.

**Overall match rate:**

| Metric | Count | % |
|--------|------:|--:|
| Codes in Results | 7,607 | — |
| Codes in Certifications | 20,221 | — |
| **Matched** | **7,579** | **99.6% of Results** |
| Orphan in Results (not in Cert) | 28 | 0.4% |
| Cert-only (never competed) | 12,642 | 62.5% of Cert |

> **Key finding:** 99.6% match rate — the Code linkage is very strong. Only 28 athlete codes in Results have no corresponding Certifications record.

**Per-year breakdown:**

| Year | Unique Codes | Matched | Match % | Orphans | Orphan % |
|------|------------:|--------:|--------:|--------:|---------:|
| 2015 | 3,288 | 3,287 | 100.0% | 1 | 0.0% |
| 2016 | 3,231 | 3,230 | 100.0% | 1 | 0.0% |
| 2017 | 3,446 | 3,445 | 100.0% | 1 | 0.0% |
| 2018 | 3,419 | 3,417 | 99.9% | 2 | 0.1% |
| 2019 | 3,482 | 3,469 | 99.6% | 13 | 0.4% |
| 2022 | 2,393 | 2,391 | 99.9% | 2 | 0.1% |
| 2023 | 2,969 | 2,946 | 99.2% | 23 | 0.8% |
| 2024 | 2,858 | 2,856 | 99.9% | 2 | 0.1% |
| 2025 | 2,788 | 2,788 | 100.0% | 0 | 0.0% |

- **2023 has the most orphans** (23) — consistent with its known data quality issues (63 missing codes).
- **2019** is the second worst (13 orphans).
- All other years have 0–2 orphans.

**Person types of matched records:**

| Person Type | Count |
|-------------|------:|
| Athlete | 7,347 |
| Unified Partner | 169 |
| Coach | 63 |

> 96.9% of matched codes are Athletes, 2.2% Unified Partners, 0.8% Coaches. This confirms Results primarily track competition participants, not staff.

**Cert-only records (62.5%):** The Certifications file includes many non-competing individuals — Coaches (3,801), Staff, Volunteers, and Athletes who registered but never participated in results-tracked events. This is expected and does not indicate a data quality issue.

---

### Club Linkage (Results ↔ Clubs)

The `Club` column in Results must be matched to `Name` in the Clubs master file. Unlike Code, this is a **name-based join** with no shared numeric key.

**Exact match rate:**

| Metric | Count | % |
|--------|------:|--:|
| Unique club names in Results | 497 | — |
| Unique club names in Clubs | 436 | — |
| **Exact match** | **375** | **75.5%** |
| No match | 122 | 24.5% |

**Row-level coverage:**

| Match Level | Rows Matched | Total Rows | Coverage |
|-------------|------------:|----------:|---------:|
| Exact match | 95,132 | 112,296 | 84.7% |
| Case-insensitive + whitespace-stripped | 95,777 | 112,296 | 85.3% |
| **Unmatched after normalization** | **16,519** | **112,296** | **14.7%** |

> **14.7% of result rows** reference a club that does not exist in the Clubs master file — this is a significant gap that fuzzy matching must resolve.

**Case-insensitive matching gains:**

Lowercasing and stripping whitespace recovers 4 additional clubs:

| Results Name | Clubs Name |
|---|---|
| `2Gether On Wheels` | `2GETHER ON WHEELS` |
| `Foyer du Calydon` | `FOYER DU CALYDON` |
| `La Caravelle` | `LA CARAVELLE` |
| `OSTEND TENNIS CLUB ` (trailing space) | `OSTEND TENNIS CLUB` |

**Top 20 unmatched clubs by result row count:**

| Rows | Club Name | Likely Issue |
|-----:|-----------|-------------|
| 2,954 | `REINE FABIOLA` | Abbreviated form of `CENTRE REINE FABIOLA` |
| 781 | `ZWART GOOR` | Not in master |
| 590 | `FUNAMBULES DE WAVRE` | Not in master |
| 562 | `DE MEANDER` | Not in master |
| 513 | `B.S.C. LEISTUNGSZENTRUM DER D.G.` | German-speaking club |
| 509 | `L'EVEIL CENTRE REINE FABIOLA` | Compound name variant |
| 478 | `LES CHAFRIPONS` | Not in master |
| 382 | `A.C. LYRA` | Abbreviation mismatch |
| 358 | `OOSTHEUVEL-TEVONA` | Hyphenated compound |
| 355 | `AT ZODAS` | Not in master |
| 345 | `ROTONDE` | Not in master |
| 339 | `KERCKSTEDE` | Not in master |
| 336 | `BBC GEEL` | Not in master |
| 302 | `DEN DRIES` | Not in master |
| 269 | `SKALA AALST` | Not in master |
| 269 | `BLIJDORP  BUGGENHOUT` | Double space |
| 258 | `FUN GYM B` | Not in master |
| 254 | `DAGCENTRUM DENDERMONDE` | Not in master |
| 251 | `ROZENWINGERD` | Not in master |
| 249 | `DE LORK` | Not in master |

> **ETL action needed:** Many unmatched clubs appear to be legitimate clubs absent from the Clubs master file (not spelling variants). The ETL should:
> 1. Apply case-insensitive + whitespace normalization first
> 2. Use fuzzy matching (e.g., Levenshtein distance) for near-misses like `REINE FABIOLA` → `CENTRE REINE FABIOLA`
> 3. Flag genuinely missing clubs for manual review or create stub entries in `dim_geography`

---

### Internal Consistency

#### Certifications.Club vs Clubs.Name

| Metric | Count | % |
|--------|------:|--:|
| Unique clubs in Certifications | 434 | — |
| Matched to Clubs.Name | 421 | 97.0% |
| **Not in Clubs.Name** | **13** | **3.0%** |

The 13 unmatched Certifications clubs:

| Members | Club Name | Notes |
|--------:|-----------|-------|
| 7,310 | `General` | Catch-all/default — **not a real club**, absent from Clubs master |
| 25 | `SKALA AALST` | Likely a real club missing from master |
| 20 | `DARING CLUB LEUVEN ATLETIEK` | Likely a real club missing from master |
| 10 | `KV Mechelen` | Sports club, not in master |
| 8 | `Levante UD Valencia` | Foreign club (Spain) |
| 6 | `BOKA` | Not in master |
| 6 | `THALEIA OK` | Not in master |
| 5 | `'T VEER` | Leading apostrophe variant |
| 5 | `L'ARBORESPORT` | Not in master |
| 4 | `DE PELGRIM` | Not in master |
| 4 | `LA SAPINIERE` | Possible accent variant of master entry |
| 2 | `KVKG` | Abbreviation |
| 1 | `HAGEN (Germany)` | Foreign club |

> **`General` dominates:** 7,310 members (36.2%) are assigned to the `General` catch-all club, which does **not** exist in the Clubs master. Of these, 2,267 appear in Results under 381 different real clubs — so they do have actual club affiliations that could be recovered from the Results data.

#### Athlete Club Consistency (Certifications vs Results)

For the 7,579 athletes appearing in both files:

| Metric | Count | % |
|--------|------:|--:|
| Code+Club pairs (athlete appeared in ≥1 club in Results) | 8,896 | — |
| Exact club match (Cert Club = Result Club) | 4,753 | 53.4% |
| Case-insensitive match | 4,805 | 54.0% |
| Athletes with **no** matching club across any year | 2,800 | 36.9% |
| Athletes with ≥1 matching club year | 4,779 | 63.1% |
| Athletes competing under **multiple** clubs over time | 1,162 | 15.3% |

> **Key insights:**
> - Only 54% of code+club pairs match between Certifications and Results — club assignment is **not stable** across files.
> - 36.9% of athletes have a completely different club in Certifications vs Results. Many of these are the `General` group (2,267 athletes).
> - 15.3% of athletes changed clubs across competition years — this is expected (athletes transfer between clubs).
> - **ETL implication:** Do **not** rely on Certifications for club assignment. Use the Results `Club` column per year, and join to Clubs master via fuzzy matching.

#### Sport Naming Consistency Across Years

| Year | Distinct Sports |
|------|----------------:|
| 2015 | 20 |
| 2016 | 20 |
| 2017 | 20 |
| 2018 | 20 |
| 2019 | 21 |
| 2022 | 16 |
| 2023 | 21 |
| 2024 | 19 |
| 2025 | 18 |

- **14 sports** are present in all 9 years (stable core).
- **23 sports** appear across the full dataset.

**Sports with inconsistent presence:**

| Sport | Present | Absent | Notes |
|-------|---------|--------|-------|
| `Aquatics/Swimming` | 2015–2023 | 2024–2025 | Likely **renamed** to `Swimming` |
| `Swimming` | 2024–2025 | 2015–2023 | Appears when `Aquatics/Swimming` disappears |
| `Football/Soccer` | 2015–2019 | 2022–2025 | Discontinued post-COVID |
| `Bowling` | All except 2022 | 2022 | COVID-year gap |
| `Cycling` | All except 2022 | 2022 | COVID-year gap |
| `Equestrian` | All except 2022 | 2022 | COVID-year gap |
| `Judo` | All except 2025 | 2025 | Newly absent |
| `Kayaking` | 2023 only | All others | One-time event |
| `Sailing` | 2019, 2023 | All others | Sporadic |

> **ETL action:** `Aquatics/Swimming` → `Swimming` rename must be handled. `Football/Soccer` was discontinued post-COVID. 2022 had a reduced programme (16 vs 20 sports). `Kayaking` and `Sailing` are sporadic/one-off sports.

---

### Join Key Summary

| Relationship | Left Key | Right Key | Match Rate | Row Coverage | Action Needed |
|---|---|---|---|---|---|
| **Results → Certifications** | `Code` | `Code` | 99.6% (7,579/7,607) | ~100% of rows | Drop 28 orphan codes or create stub records; safe direct join |
| **Results → Clubs** | `Club` (name) | `Name` | 75.5% exact / 76.3% case-insensitive | 85.3% of rows | Fuzzy matching required; ~112 club names need resolution; 16.5k rows at risk |
| **Certifications → Clubs** | `Club` | `Name` | 97.0% (421/434) | — | 13 unmatched; `General` (7,310 rows) is the dominant gap |
| **Cert Club ↔ Results Club** | `Club` (per athlete) | `Club` (per athlete) | 54.0% | — | Club assignment differs; use Results `Club` as source of truth per year |
| **Sport names across years** | `Sport` | `Sport` | 14/23 stable | — | Normalize `Aquatics/Swimming` ↔ `Swimming`; handle discontinued sports |

**Referential integrity priority for ETL:**

1. 🟢 **Code join is reliable** — 99.6% match, use as primary key for `dim_athletes` ↔ `fact_results`.
2. 🟡 **Club join needs fuzzy matching** — 75.5% exact match is insufficient; implement case normalization + Levenshtein matching to close the 14.7% row gap.
3. 🟡 **`General` club requires special handling** — 7,310 Certifications rows (36.2%) have no real club. Recover from Results where possible (2,267 athletes have real clubs in Results).
4. 🟠 **Sport normalization** — `Aquatics/Swimming` rename in 2024–2025 must be mapped. `dim_sports` should use canonical names.
5. 🟢 **Cert-only records are expected** — 62.5% of Certifications never appear in Results (coaches, staff, non-competing athletes). Filter by `Person type = Athlete/Unified Partner` for `dim_athletes`.

---

## 5. Data Quality Summary

### 5.1 Critical Issues (Must Fix for ETL)

Issues that would **break the pipeline or produce incorrect results** if left unaddressed.

| # | Issue | Source | Rows Affected | Why Critical |
|---|-------|--------|---------------|--------------|
| C1 | **780 completely empty rows** in Certifications | Certifications | 780 | Will inflate counts and create ghost dimension records in `dim_athletes`. |
| C2 | **Club name fuzzy matching** — only 75.5% exact match between Results `Club` and Clubs `Name` | Results ↔ Clubs | ~16,500 (14.7% of fact rows) | Unresolved club names → NULL `ClubID` in `fact_results`, breaking regional analysis and club-level KPIs. |
| C3 | **Score format heterogeneity** — `X min, Y.ZZ sec`, `Xm, Y.ZZcm`, `X.XX points` | Results | All score cells | Scores must be parsed to numeric for performance trends, athlete development tracking, and best-results queries. Unparsed scores = no performance analysis. |
| C4 | **Place/Rank parsing** — 63 distinct values including ordinals (`1st`, `2nd`), 12 DQ code variants, DNS/DNF/DNC/DNT, and aquatics level indicators | Results | All Place cells | Rank must be integer for medal derivation (1→Gold, 2→Silver, 3→Bronze) and the 20% DQ rule calculation. Inconsistent DQ codes will under/over-count disqualifications. |
| C5 | **`General` club has no master entry** — 7,310 Certifications rows (34.8%) reference a catch-all club with no record in Clubs file | Certifications ↔ Clubs | 7,310 | Creates a NULL gap in `dim_geography`. 2,267 athletes can be recovered from Results club data; rest need a dedicated "Unknown" club record. |
| C6 | **Country spelling variants** — 14 variants of "Belgium" + encoding issues + province/city values in Country column | Clubs | 14 variants + 74 missing + row 433 swap | Breaks `dim_geography` grouping; regional analysis becomes unreliable. |
| C7 | **Sport name instability** — `Aquatics/Swimming` renamed to `Swimming` in 2024–2025 | Results | All aquatics rows across years | Without normalization, `dim_sports` will have duplicate entries and multi-year trend analysis for swimming will break. |

### 5.2 Medium Issues (Should Fix)

Issues that **degrade data quality** but won't break the pipeline outright.

| # | Issue | Source | Rows Affected | Impact |
|---|-------|--------|---------------|--------|
| M1 | **DOB missing** — ~1,210 NULLs (mostly Coaches) | Certifications | 1,210 | Age-based demographics incomplete. Coaches are filtered from `dim_athletes`, so athlete impact is lower (~200 athletes). |
| M2 | **Sentinel DOB** — 6 records with `1900-01-02` (Age 125) | Certifications | 6 | Outlier ages will skew "average age of best performers" use-case. |
| M3 | **Age = 0 instead of NaN** | Certifications | Unknown count | Will distort age distributions and averages unless converted to NULL. |
| M4 | **Province normalization** — 24 values instead of ~11 due to casing, hyphens, and typos | Clubs | Multiple | Regional grouping will have duplicates (e.g., "West-Vlaanderen" vs "West-vlaanderen"), fragmenting regional analysis. |
| M5 | **City casing** — 63% ALL CAPS, 37% mixed case | Clubs | ~300 clubs | Cosmetic for dashboard display but will cause duplicate cities in filters/slicers. |
| M6 | **491 raw club name variants** in Results | Results | Spread across all years | Even after fuzzy matching, remaining variants will fragment club-level aggregations. |
| M7 | **Bilingual event names** — 375 distinct event names with Dutch/French/English naming | Results | All event rows | `dim_sports` will be bloated with duplicates unless canonicalized. |
| M8 | **2025 high missingness** — Place 40.8% missing, Score 35.8% missing | Results (2025) | ~4,600 rows | Most recent year has weakest data; trend analysis for 2025 will be incomplete. |
| M9 | **`Summary (all)` column missing in 2023** | Results (2023) | All 2023 rows | Schema inconsistency; ETL must handle this column's absence gracefully. |
| M10 | **Certifications Club ↔ Results Club only 54% consistent** | Cross-file | ~3,800 athletes | Athletes appear under different clubs in each source; ETL must decide source of truth (Results club per year recommended). |

### 5.3 Low Issues (Nice to Fix)

| # | Issue | Source | Rows Affected | Impact |
|---|-------|--------|---------------|--------|
| L1 | **51 "U" (Unknown) gender values** | Certifications | 51 | Minor gap in gender distribution analysis; can map to "Unknown" in `dim_athletes`. |
| L2 | **Zipcode outlier** — `29900` should be `2990` | Clubs | 1 | Single-row fix; negligible dashboard impact. |
| L3 | **14 Person types** — only 3 matter (Athlete 75.5%, Coach 18.1%, Unified Partner 2.5%) | Certifications | ~820 (minor types) | Filter to relevant types; others are noise for the dashboard. |
| L4 | **Certificate columns 53–99% NaN** | Certifications | Most rows | Sparse but not needed for core use-cases; can be dropped or kept as optional flags. |
| L5 | **`Football/Soccer` discontinued post-COVID** | Results | Pre-2020 football rows | Historical only; no new data. Flag in `dim_sports` but no ETL action needed. |
| L6 | **Kayaking/Sailing sporadic appearances** | Results | Small | One-off sports; include in `dim_sports` as-is. |
| L7 | **Row 433 province/country swap** | Clubs | 1 | Single-row correction in `dim_geography` build. |

---

### 5.4 Impact on Use-Cases

Mapping of key quality issues to the specific business questions from the dashboard use-cases:

| Use-Case | Affected By | Severity | Notes |
|----------|-------------|----------|-------|
| **Distribution by age & gender** | M1 (DOB missing), M2 (sentinel DOB), M3 (Age=0), L1 (Gender "U") | 🟡 Medium | ~1,210 missing DOBs mostly affect coaches (filtered out). 6 sentinel dates and Age=0 will skew distributions if not cleaned. 51 unknown genders are minor. |
| **Average age of best performers** | M2 (sentinel DOB), C4 (Place parsing) | 🟡 Medium | Sentinel ages (125) will heavily skew averages. Place must be parsed to identify "best" performers. |
| **Athletes in multiple disciplines / changed sports** | C7 (sport name instability), M7 (bilingual events) | 🔴 High | Sport renaming (`Aquatics/Swimming` → `Swimming`) will create false "sport changes." Bilingual duplicates inflate discipline counts. |
| **Experience vs performance** | C3 (score parsing), C4 (place parsing) | 🔴 High | Both score and rank must be numeric for any performance correlation. This use-case is completely blocked without C3+C4. |
| **Year-over-year development** | C3 (score parsing), C7 (sport normalization), M8 (2025 missingness) | 🔴 High | Score comparisons across years require consistent parsing. 2025's 35–41% missingness weakens the latest data point. |
| **3+ competitions → better performance?** | C3 (score parsing), C4 (place parsing) | 🔴 High | Requires counting competitions per athlete and comparing scores — blocked without numeric scores and ranks. |
| **Score improvements since previous edition** | C3 (score parsing), C7 (sport normalization) | 🔴 High | Direct score comparison across years; completely dependent on consistent numeric conversion. |
| **Best results** | C3 (score parsing), C4 (place parsing) | 🔴 High | Ranking athletes by performance requires parsed scores and places. |
| **20% disqualification rule** | C4 (DQ code parsing) | 🔴 High | 12 inconsistent DQ code formats must be unified to accurately calculate DQ percentages per sport/event. Under-counting DQs defeats the purpose of this rule. |
| **Regional analysis** (participants by region, geography vs sport, club size vs performance) | C2 (club matching), C5 (General club), C6 (country variants), M4 (province normalization) | 🔴 High | The full club/geography chain is broken: 14.7% of fact rows lose their club link, 34.8% of athletes are in "General," and provinces are fragmented. |
| **Multi-year athlete tracking** | (Code join is solid at 99.6%) | 🟢 Low | Code-based joins are reliable. Only 28 orphan codes — this is the strongest part of the data. |

---

### 5.5 Recommended ETL Transformation Priority

Ordered by **impact × dependency** — later steps depend on earlier ones.

| Priority | Task | Issues Resolved | Rationale |
|----------|------|-----------------|-----------|
| **1** | **Drop empty rows & filter Person types** | C1, L3 | Fastest win: removes 780 ghost rows and scopes data to relevant types. Foundation for all downstream counts. |
| **2** | **Country / Province / City normalization** | C6, M4, M5, L2, L7 | Fix `dim_geography` first — it's a dimension that everything else joins to. Includes country dedup (14 → 1), province canonicalization (24 → ~11), city casing, zipcode fix, and row 433 swap. |
| **3** | **Club name fuzzy matching** | C2, M6 | Build the Club → ClubID mapping. Use case-insensitive normalization first, then Levenshtein/token-set matching for the remaining ~122 unmatched names. Unlocks 14.7% of fact rows. |
| **4** | **`General` club recovery** | C5, M10 | Cross-reference Results club data to recover real clubs for 2,267 athletes currently under "General." Create an "Unknown" stub for the rest. |
| **5** | **Sport & Event name canonicalization** | C7, M7 | Normalize `Aquatics/Swimming` → `Swimming`, unify bilingual event names, and build `dim_sports`. Required before any sport-based analysis. |
| **6** | **Score parsing** | C3 | Parse `X min, Y.ZZ sec` → seconds, `Xm, Y.ZZcm` → meters, `X.XX points` → float. This is the most complex transformation and unlocks all performance use-cases. |
| **7** | **Place / Rank parsing & Medal derivation** | C4 | Parse ordinals → integers, unify 12 DQ codes into a single `IsDisqualified` flag, handle DNS/DNF/DNC/DNT as NULLs. Derive Medal from Place (1→Gold, 2→Silver, 3→Bronze). |
| **8** | **DOB / Age cleanup** | M1, M2, M3 | Replace sentinel `1900-01-02` → NULL, convert Age=0 → NULL, recalculate age from DOB where possible. |
| **9** | **Gender standardization** | L1 | Map `U` → `Unknown`. Already clean otherwise (M/F only). |
| **10** | **Handle 2023 schema gap & 2025 missingness** | M8, M9 | Make `Summary (all)` column optional in the extract step. Document 2025 missingness as a known limitation in the dashboard. |
| **11** | **Certificate columns** | L4 | Decide keep/drop based on dashboard requirements. Low priority — not needed for core use-cases. |

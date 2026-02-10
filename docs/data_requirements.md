# Data Requirements & Metrics

*Verified against `data/raw` files on Feb 10, 2026.*

Based on the core business questions:
1. **Athlete Overview** (Demographics: Age, Gender)
2. **Participation Trends** (Growth over time)
3. **Performance Analysis** (Medals & Results)
4. **Regional Distribution** (Globalization of the games)

## Required Fields & Metrics

### 1. Dimension: Athletes
*Answers: Who is participating?*
- **Source**: `Thomas More Data Certifications.xlsx` (Master List) & `Results` files
- **Fields**:
    - `AthleteID`: Map from `Code` (Unique Identifier)
    - `FullName`: **Not Available** (Data is anonymized, use `Code`)
    - `Gender`: `Gender` (M/F/Male/Female - needs standardization)
    - `BirthDate`: `DOB` (Date)
    - `Age`: `Age` (Available, but verify recalculation `Year - DOB`)
    - `Type`: `Person type` (Athlete vs Unified Partner)

### 2. Dimension: Geography (Clubs/Delegations)
*Answers: Where are they from?*
- **Source**: `Thomas More Data Clubs.xlsx`
- **Fields**:
    - `ClubID`: `Group number`
    - `ClubName`: `Name` (Join Key with Results/Certifications)
    - `Region`: `Province` / `Country`
    - `City`: `City`
    - `Language`: `Primary language`

### 3. Dimension: Sports & Events
*Answers: What are they competing in?*
- **Source**: Derived from `Thomas More Results YYYY.xlsx`
- **Fields**:
    - `SportID`: **Generate Surrogate Key** (Distinct `Sport`)
    - `SportName`: `Sport` (e.g., 'Athletics/Track and Field')
    - `EventName`: `Event` (e.g., 'AT25 - Saut en longueur')
    - `Category`: Extract from `Event` or `Role`

### 4. Dimension: Time
*Answers: When did it happen?*
- **Source**: Extracted from Filenames (Year)
- **Fields**:
    - `Year`: Extract `2015`, `2024` from `Thomas More Results 2024.xlsx`
    - `Date`: Default to `Jan 1, Year` if specific dates missing.

### 5. Fact: Results / Performance
*Answers: How did they perform?*
- **Source**: `Thomas More Results YYYY.xlsx` (Union all years)
- **Fields**:
    - `ResultID`: **Generate Surrogate Key**
    - `AthleteID`: `Code` (FK)
    - `SportID`: Lookup on `Sport` (FK)
    - `ClubID`: Lookup on `Club` Name (FK)
    - `Year`: From Filename (FK)
    - `Rank`: `Place` (Needs parsing: '1st', '2nd' -> 1, 2)
    - `Medal`: Derived from `Place` (1-3)
    - `ResultValue`: `Score` (Clean '2m, 51.00cm' -> numeric)
    - `IsDisqualified`: Check `Place` for 'DQ' or `Summary` text

### 6. Fact: Participation
*Answers: Attendance stats*
- **Source**: Distinct `Code` per `Year` in Results
- **Fields**:
    - `AthleteID`: `Code`
    - `Year`: `Year`
    - `ClubID`: `Club`

## Key Transformation Rules (ETL)
1. **Anonymity**: Respect `Code` as the primary key. Do not attempt to reverse-engineer names.
2. **Medal Logic**: Map `Place` ('1st', '2nd', '3rd') to Gold/Silver/Bronze. Handle variations ('1', 'Gold', etc. if any).
3. **Score parsing**: Convert strings like "2m 50", "15.00", "00:15.00" to a standardized numeric format (seconds or meters).
4. **Club Matching**: Fuzzy match `Club` in Results to `Name` in Clubs if exact match fails (e.g., casing issues).


---

## AI Usage

### Prompt 1: Create Data requirements

```txt
see the entire project if the structure is there, i was planning on having all the python scripts in src/ folder and all the data in #file:data  within raw and processed (not sure what the best way is for ETL, help me out here) and create a list of all required fields/metrics based on business questions in #file:docs somewhere whether its a new markdown file or not, keep it structured
```

### Prompt 2: Verify fields and metrics availability

```txt
verify that #file:data_requirements.md is aligned with the #file:Special Olympics - Use-Cases.pdf  and the #file:raw data that is available. you can utilize python to verify the columns and column names, rows and so on if you want in #file:temp.py , pandas and numpy are installed. the venv is made in #file:src  and can be activated with uv
```
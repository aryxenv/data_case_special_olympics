"""Expected schemas and validation constants for gold-layer outputs."""

SCHEMAS: dict[str, dict[str, bool]] = {
    "dim_time": {
        "time_key": False, "year": False,
        "is_covid_gap": False, "period": False,
    },
    "dim_athlete": {
        "athlete_key": False, "code": False, "gender": True,
        "date_of_birth": True, "age": True, "person_type": True,
        "has_mental_handicap_cert": False, "has_parents_consent_cert": False,
        "has_hap_cert": False, "is_unified_partner_cert": False,
    },
    "dim_geography": {
        "geography_key": False, "club_id": False, "club_name": False,
        "province": True, "city": True, "country": True,
        "primary_language": True, "zipcode": True,
    },
    "dim_sport": {
        "sport_key": False, "sport_name": False,
    },
    "dim_event": {
        "event_key": False, "sport_key": False,
        "event_code": False, "event_name": False,
    },
    "fact_results": {
        "result_key": False, "athlete_key": True, "geography_key": False,
        "sport_key": True, "event_key": True, "time_key": False,
        "rank": True, "medal": True, "score_value": True,
        "score_unit": True, "is_disqualified": False, "result_status": True,
    },
    "fact_participation": {
        "athlete_key": False, "geography_key": False, "time_key": False,
        "events_entered": False, "sports_entered": False,
    },
}

ROW_BOUNDS: dict[str, tuple[int, int]] = {
    "dim_time": (11, 11),
    "dim_athlete": (19_000, 21_000),
    "dim_geography": (430, 500),
    "dim_sport": (15, 30),
    "dim_event": (100, 400),
    "fact_results": (60_000, 80_000),
    "fact_participation": (20_000, 40_000),
}

FK_CHECKS: list[tuple[str, str, str, str]] = [
    ("fact_results", "athlete_key", "dim_athlete", "athlete_key"),
    ("fact_results", "geography_key", "dim_geography", "geography_key"),
    ("fact_results", "sport_key", "dim_sport", "sport_key"),
    ("fact_results", "event_key", "dim_event", "event_key"),
    ("fact_results", "time_key", "dim_time", "time_key"),
    ("fact_participation", "athlete_key", "dim_athlete", "athlete_key"),
    ("fact_participation", "geography_key", "dim_geography", "geography_key"),
    ("fact_participation", "time_key", "dim_time", "time_key"),
    ("dim_event", "sport_key", "dim_sport", "sport_key"),
]

VALUE_CHECKS: dict[str, dict[str, set[str]]] = {
    "dim_athlete": {
        "gender": {"M", "F", "U"},
    },
    "dim_time": {
        "period": {"Pre-COVID", "COVID", "Post-COVID"},
    },
    "fact_results": {
        "medal": {"Gold", "Silver", "Bronze"},
        "score_unit": {"seconds", "meters", "points"},
    },
}

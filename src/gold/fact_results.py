"""Gold transformer for fact_results."""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd
from rapidfuzz import fuzz, process

from src.gold.base_transformer import BaseTransformer

logger = logging.getLogger(__name__)

_MEDAL_MAP = {1: "Gold", 2: "Silver", 3: "Bronze"}


class FactResultsTransformer(BaseTransformer):
    """Transform silver results into the fact_results star-schema table.

    Performs foreign-key lookups against all five dimensions:
    - athlete_key via code → dim_athlete
    - geography_key via fuzzy club name → dim_geography
    - sport_key via sport name → dim_sport
    - event_key via event code → dim_event
    - time_key = year → dim_time

    Also derives the ``medal`` column from ``rank``.
    """

    _FUZZY_THRESHOLD = 80  # minimum score for a fuzzy club match

    def __init__(
        self,
        silver_results: pd.DataFrame,
        dim_athlete: pd.DataFrame,
        dim_geography: pd.DataFrame,
        dim_sport: pd.DataFrame,
        dim_event: pd.DataFrame,
        output_dir: str | Path,
    ) -> None:
        super().__init__(output_dir)
        self._results = silver_results
        self._dim_athlete = dim_athlete
        self._dim_geography = dim_geography
        self._dim_sport = dim_sport
        self._dim_event = dim_event

    @property
    def _filename(self) -> str:
        return "fact_results.csv"

    @property
    def _expected_row_range(self) -> tuple[int, int]:
        return (60_000, 80_000)

    @property
    def _required_columns(self) -> list[str]:
        return [
            "result_key", "athlete_key", "geography_key", "sport_key",
            "event_key", "time_key", "rank", "medal", "score_value",
            "score_unit", "is_disqualified", "result_status",
        ]

    # ------------------------------------------------------------------
    # Transform
    # ------------------------------------------------------------------

    def transform(self) -> pd.DataFrame:
        df = self._results.copy()

        # Build lookup tables
        athlete_lookup = self._build_athlete_lookup()
        geography_lookup = self._build_geography_lookup()
        sport_lookup = dict(zip(self._dim_sport["sport_name"], self._dim_sport["sport_key"]))
        event_lookup = self._build_event_lookup()

        # FK: athlete_key
        df["athlete_key"] = df["code"].map(athlete_lookup)
        unmatched_athletes = df["athlete_key"].isna().sum()
        if unmatched_athletes:
            logger.warning("athlete_key: %d unmatched codes (set to NULL)", unmatched_athletes)

        # FK: geography_key via fuzzy club matching
        df["geography_key"] = df["club"].map(geography_lookup)
        unmatched_clubs = df["geography_key"].isna().sum()
        # Fill unmatched with Unknown (-1)
        df["geography_key"] = df["geography_key"].fillna(-1).astype(int)
        logger.info(
            "geography_key: %d matched, %d → Unknown (-1)",
            len(df) - unmatched_clubs, unmatched_clubs,
        )

        # FK: sport_key
        df["sport_key"] = df["sport"].map(sport_lookup)

        # FK: event_key
        df["event_key"] = df["event"].map(event_lookup)
        unmatched_events = df["event_key"].isna().sum()
        if unmatched_events:
            logger.warning("event_key: %d unmatched events", unmatched_events)

        # FK: time_key
        df["time_key"] = df["year"]

        # Derive medal from rank
        df["medal"] = df["rank"].map(_MEDAL_MAP)

        # Add surrogate key
        df.insert(0, "result_key", range(1, len(df) + 1))

        # Select and order final columns
        df = df[self._required_columns].copy()

        medal_counts = df["medal"].value_counts().to_dict()
        logger.info("fact_results: %d rows, medals: %s", len(df), medal_counts)
        return df

    # ------------------------------------------------------------------
    # Lookup builders
    # ------------------------------------------------------------------

    def _build_athlete_lookup(self) -> dict[str, int]:
        """code → athlete_key mapping."""
        return dict(zip(self._dim_athlete["code"], self._dim_athlete["athlete_key"]))

    def _build_geography_lookup(self) -> dict[str, int]:
        """Club name → geography_key, using exact + fuzzy matching.

        Returns a dict mapping every distinct club name in Results
        to a geography_key.
        """
        # Get all club names from dim_geography (excluding Unknown)
        dim = self._dim_geography[self._dim_geography["geography_key"] != -1]
        canonical_names = dict(zip(dim["club_name"], dim["geography_key"]))

        # Normalize canonical names for matching
        norm_canonical = {
            self._normalize(name): key
            for name, key in canonical_names.items()
        }

        # Distinct club names from results
        result_clubs = self._results["club"].dropna().unique()

        lookup: dict[str, int] = {}
        exact = 0
        fuzzy_matched = 0
        unmatched = 0

        for club in result_clubs:
            norm = self._normalize(str(club))

            # 1. Exact match (case-insensitive, whitespace-stripped)
            if norm in norm_canonical:
                lookup[club] = norm_canonical[norm]
                exact += 1
                continue

            # 2. Fuzzy match
            match = process.extractOne(
                norm,
                norm_canonical.keys(),
                scorer=fuzz.ratio,
                score_cutoff=self._FUZZY_THRESHOLD,
            )
            if match:
                lookup[club] = norm_canonical[match[0]]
                fuzzy_matched += 1
                continue

            # 3. Unmatched → will become -1 (Unknown)
            unmatched += 1

        logger.info(
            "Club matching: %d exact, %d fuzzy, %d unmatched (of %d total)",
            exact, fuzzy_matched, unmatched, len(result_clubs),
        )
        return lookup

    def _build_event_lookup(self) -> dict[str, int]:
        """Event name → event_key mapping.

        Maps every raw event name in silver_results to the appropriate
        event_key in dim_event via event code extraction.
        """
        import re
        _RE_CODE = re.compile(r"^([A-Za-z]{2,5}\d*)\s*-")

        # Build event_code → event_key from dim_event
        code_to_key = dict(zip(self._dim_event["event_code"], self._dim_event["event_key"]))

        result_events = self._results["event"].dropna().unique()
        lookup: dict[str, int] = {}

        for event in result_events:
            m = _RE_CODE.match(str(event).strip())
            code = m.group(1).upper() if m else None

            if code and code in code_to_key:
                lookup[event] = code_to_key[code]
            else:
                # Try to match via sport-based synthetic code
                # For now, find any dim_event row whose event_name matches
                exact = self._dim_event[self._dim_event["event_name"] == event]
                if not exact.empty:
                    lookup[event] = exact.iloc[0]["event_key"]

        return lookup

    @staticmethod
    def _normalize(name: str) -> str:
        """Lowercase, strip whitespace, collapse multiple spaces."""
        return " ".join(str(name).lower().split())

"""Gold transformer for fact_participation."""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

from src.gold.base_transformer import BaseTransformer

logger = logging.getLogger(__name__)


class FactParticipationTransformer(BaseTransformer):
    """Aggregate fact_results into participation records.

    One row per athlete × club × year, counting distinct events and
    sports entered.
    """

    def __init__(self, fact_results: pd.DataFrame, output_dir: str | Path) -> None:
        super().__init__(output_dir)
        self._fact_results = fact_results

    @property
    def _filename(self) -> str:
        return "fact_participation.csv"

    @property
    def _expected_row_range(self) -> tuple[int, int]:
        return (20_000, 40_000)

    @property
    def _required_columns(self) -> list[str]:
        return [
            "athlete_key", "geography_key", "time_key",
            "events_entered", "sports_entered",
        ]

    def transform(self) -> pd.DataFrame:
        df = self._fact_results.copy()

        # Filter out rows without athlete_key (orphan codes)
        df = df[df["athlete_key"].notna()].copy()

        agg = (
            df.groupby(["athlete_key", "geography_key", "time_key"])
            .agg(
                events_entered=("event_key", "nunique"),
                sports_entered=("sport_key", "nunique"),
            )
            .reset_index()
        )

        # Ensure integer types
        agg["athlete_key"] = agg["athlete_key"].astype(int)
        agg["geography_key"] = agg["geography_key"].astype(int)
        agg["time_key"] = agg["time_key"].astype(int)

        logger.info(
            "fact_participation: %d rows (avg %.1f events/athlete/year)",
            len(agg),
            agg["events_entered"].mean(),
        )
        return agg

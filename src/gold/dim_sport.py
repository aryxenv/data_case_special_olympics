"""Gold transformer for dim_sport."""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

from src.gold.base_transformer import BaseTransformer

logger = logging.getLogger(__name__)


class DimSportTransformer(BaseTransformer):
    """Build the sport dimension from distinct sport names in results."""

    def __init__(self, silver_results: pd.DataFrame, output_dir: str | Path) -> None:
        super().__init__(output_dir)
        self._results = silver_results

    @property
    def _filename(self) -> str:
        return "dim_sport.csv"

    @property
    def _expected_row_range(self) -> tuple[int, int]:
        return (15, 30)

    @property
    def _required_columns(self) -> list[str]:
        return ["sport_key", "sport_name"]

    def transform(self) -> pd.DataFrame:
        sports = sorted(self._results["sport"].dropna().unique())
        df = pd.DataFrame({
            "sport_key": range(1, len(sports) + 1),
            "sport_name": sports,
        })
        logger.info("dim_sport: %d distinct sports", len(df))
        return df

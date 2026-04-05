"""Gold transformer for dim_time."""

from __future__ import annotations

import logging

import pandas as pd

from src.gold.base_transformer import BaseTransformer

logger = logging.getLogger(__name__)


class DimTimeTransformer(BaseTransformer):
    """Generate the time dimension (year-level granularity).

    Produces rows for 2015–2025 including COVID gap years (2020–2021).
    """

    @property
    def _filename(self) -> str:
        return "dim_time.csv"

    @property
    def _expected_row_range(self) -> tuple[int, int]:
        return (11, 11)

    @property
    def _required_columns(self) -> list[str]:
        return ["time_key", "year", "is_covid_gap", "period"]

    def transform(self) -> pd.DataFrame:
        rows = []
        for year in range(2015, 2026):
            is_gap = year in (2020, 2021)
            if year <= 2019:
                period = "Pre-COVID"
            elif year <= 2021:
                period = "COVID"
            else:
                period = "Post-COVID"
            rows.append({
                "time_key": year,
                "year": year,
                "is_covid_gap": is_gap,
                "period": period,
            })

        df = pd.DataFrame(rows)
        logger.info("dim_time generated: %d rows", len(df))
        return df

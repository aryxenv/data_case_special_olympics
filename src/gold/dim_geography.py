"""Gold transformer for dim_geography."""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

from src.gold.base_transformer import BaseTransformer

logger = logging.getLogger(__name__)

# Columns to keep from silver_clubs for the geography dimension
_CORE_COLUMNS = [
    "group_number", "name", "province", "city",
    "country", "primary_language", "zipcode",
]


class DimGeographyTransformer(BaseTransformer):
    """Transform silver clubs into the geography dimension.

    Selects core columns, adds surrogate key, and appends an
    'Unknown' row for unmatched club references.
    """

    def __init__(self, silver_clubs: pd.DataFrame, output_dir: str | Path) -> None:
        super().__init__(output_dir)
        self._clubs = silver_clubs

    @property
    def _filename(self) -> str:
        return "dim_geography.csv"

    @property
    def _expected_row_range(self) -> tuple[int, int]:
        return (430, 500)

    @property
    def _required_columns(self) -> list[str]:
        return [
            "geography_key", "club_id", "club_name", "province",
            "city", "country", "primary_language", "zipcode",
        ]

    def transform(self) -> pd.DataFrame:
        df = self._clubs[_CORE_COLUMNS].copy()

        # Rename to match dimensional model schema
        df = df.rename(columns={
            "group_number": "club_id",
            "name": "club_name",
        })

        # Add surrogate key (starting at 1)
        df.insert(0, "geography_key", range(1, len(df) + 1))

        # Append Unknown row for unmatched club references
        unknown = pd.DataFrame([{
            "geography_key": -1,
            "club_id": -1,
            "club_name": "Unknown",
            "province": None,
            "city": None,
            "country": None,
            "primary_language": None,
            "zipcode": None,
        }])
        df = pd.concat([unknown, df], ignore_index=True)

        logger.info(
            "dim_geography: %d rows (%d clubs + 1 Unknown)",
            len(df), len(df) - 1,
        )
        return df

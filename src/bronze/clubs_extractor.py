"""Bronze extractor for the Clubs master file."""

from __future__ import annotations

import logging

import pandas as pd

from src.bronze.base_extractor import BaseExtractor

logger = logging.getLogger(__name__)


class ClubsExtractor(BaseExtractor):
    """Extract club/delegation records from the Clubs Excel file.

    Bronze-level transforms:
    - Rename columns to snake_case.
    - Ensure ``group_number`` is int dtype.
    - Convert ``zipcode`` from float to string.
    """

    @property
    def _filename(self) -> str:
        return "bronze_clubs.csv"

    @property
    def _expected_row_range(self) -> tuple[int, int]:
        return (430, 450)

    @property
    def _required_columns(self) -> list[str]:
        return [
            "group_number", "name", "primary_language",
            "zipcode", "city", "province", "country",
        ]

    # ------------------------------------------------------------------
    # Extraction
    # ------------------------------------------------------------------

    def extract(self) -> pd.DataFrame:
        """Load Clubs, rename columns, and enforce types."""
        df = self._loader.load_clubs()
        logger.info("Raw clubs loaded: %d rows", len(df))

        # Rename columns to snake_case
        df.columns = [self._to_snake_case(c) for c in df.columns]

        # Ensure group_number is int
        df["group_number"] = df["group_number"].astype(int)

        # Convert zipcode from float to string (strip trailing .0)
        df["zipcode"] = (
            df["zipcode"]
            .dropna()
            .astype(int)
            .astype(str)
            .reindex(df.index)
        )

        return df

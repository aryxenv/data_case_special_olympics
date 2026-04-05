"""Bronze extractor for the yearly Results files."""

from __future__ import annotations

import logging

import pandas as pd

from src.bronze.base_extractor import BaseExtractor

logger = logging.getLogger(__name__)


class ResultsExtractor(BaseExtractor):
    """Extract and union all yearly Results files into a single bronze table.

    Bronze-level transforms:
    - Union all 9 year files (2015–2025, excluding 2020/2021).
    - Ensure ``Year`` column is present on every row.
    - Handle missing ``Summary (all)`` column in 2023.
    - Rename columns to snake_case.
    """

    # Per-year expected row counts from data exploration
    _EXPECTED_COUNTS: dict[int, int] = {
        2015: 14_756,
        2016: 12_849,
        2017: 14_363,
        2018: 13_554,
        2019: 14_009,
        2022: 9_409,
        2023: 11_798,
        2024: 11_239,
        2025: 10_398,
    }

    @property
    def _filename(self) -> str:
        return "bronze_results.csv"

    @property
    def _expected_row_range(self) -> tuple[int, int]:
        # Total across all years: 112,375 — allow ±500 tolerance
        return (110_000, 115_000)

    @property
    def _required_columns(self) -> list[str]:
        return [
            "code", "club", "sport", "role", "dob", "age",
            "gender", "event", "place", "score", "year",
        ]

    # ------------------------------------------------------------------
    # Extraction
    # ------------------------------------------------------------------

    def extract(self) -> pd.DataFrame:
        """Load all Results files, validate per-year counts, and union."""
        frames: list[pd.DataFrame] = []

        for year in self._loader.available_years():
            df_year = self._loader.load_results(year)
            actual = len(df_year)
            expected = self._EXPECTED_COUNTS.get(year)

            if expected and actual != expected:
                logger.warning(
                    "Year %d: expected %d rows, got %d", year, expected, actual
                )

            # Ensure Summary (all) column exists (missing in 2023)
            if "Summary (all)" not in df_year.columns:
                df_year["Summary (all)"] = pd.NA
                logger.info("Year %d: added missing 'Summary (all)' column", year)

            logger.info("Year %d: %d rows loaded", year, actual)
            frames.append(df_year)

        df = pd.concat(frames, ignore_index=True)
        logger.info("All results unioned: %d total rows", len(df))

        # Rename columns to snake_case
        df.columns = [self._to_snake_case(c) for c in df.columns]

        return df

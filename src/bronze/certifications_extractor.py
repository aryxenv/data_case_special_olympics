"""Bronze extractor for the Certifications master file."""

from __future__ import annotations

import logging

import pandas as pd

from src.bronze.base_extractor import BaseExtractor

logger = logging.getLogger(__name__)


class CertificationsExtractor(BaseExtractor):
    """Extract athlete/person records from the Certifications Excel file.

    Bronze-level transforms:
    - Drop completely empty rows (all columns NaN).
    - Rename columns to snake_case.
    - Ensure ``code`` is string dtype.
    """

    @property
    def _filename(self) -> str:
        return "bronze_certifications.csv"

    @property
    def _expected_row_range(self) -> tuple[int, int]:
        # Raw: 21,001 rows — 780 empty → ~20,221 expected
        return (19_000, 21_000)

    @property
    def _required_columns(self) -> list[str]:
        return [
            "club", "code", "person_type", "gender", "dob", "age",
            "mental_handicap", "parents_consent", "hap", "unified_partner",
        ]

    # ------------------------------------------------------------------
    # Extraction
    # ------------------------------------------------------------------

    def extract(self) -> pd.DataFrame:
        """Load Certifications, drop empty rows, and rename columns."""
        df = self._loader.load_certifications()
        logger.info("Raw certifications loaded: %d rows", len(df))

        # Drop rows where every column is NaN (padding rows)
        df = df.dropna(how="all").reset_index(drop=True)
        logger.info("After dropping empty rows: %d rows", len(df))

        # Rename columns to snake_case
        df.columns = [self._to_snake_case(c) for c in df.columns]

        # Ensure code is string (not float/NaN weirdness)
        df["code"] = df["code"].astype(str)

        return df

"""Gold transformer for dim_athlete."""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

from src.gold.base_transformer import BaseTransformer

logger = logging.getLogger(__name__)


class DimAthleteTransformer(BaseTransformer):
    """Transform silver certifications into the athlete dimension.

    Adds surrogate key and renames columns to match the star schema.
    """

    def __init__(self, silver_certifications: pd.DataFrame, output_dir: str | Path) -> None:
        super().__init__(output_dir)
        self._certifications = silver_certifications

    @property
    def _filename(self) -> str:
        return "dim_athlete.csv"

    @property
    def _expected_row_range(self) -> tuple[int, int]:
        return (19_000, 21_000)

    @property
    def _required_columns(self) -> list[str]:
        return [
            "athlete_key", "code", "gender", "date_of_birth", "age",
            "person_type", "has_mental_handicap_cert", "has_parents_consent_cert",
            "has_hap_cert", "is_unified_partner_cert",
        ]

    def transform(self) -> pd.DataFrame:
        df = self._certifications.copy()

        # Rename to match dimensional model schema
        df = df.rename(columns={
            "dob": "date_of_birth",
            "mental_handicap": "has_mental_handicap_cert",
            "parents_consent": "has_parents_consent_cert",
            "hap": "has_hap_cert",
            "unified_partner": "is_unified_partner_cert",
        })

        # Drop the club column (not part of dim_athlete)
        df = df.drop(columns=["club"], errors="ignore")

        # Add surrogate key
        df.insert(0, "athlete_key", range(1, len(df) + 1))

        logger.info("dim_athlete: %d rows, surrogate keys 1–%d", len(df), len(df))
        return df

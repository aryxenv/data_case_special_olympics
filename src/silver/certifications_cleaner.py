"""Silver cleaner for the Certifications table."""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd

from src.silver.base_cleaner import BaseCleaner

logger = logging.getLogger(__name__)

_SENTINEL_DOB = pd.Timestamp("1900-01-02")


class CertificationsCleaner(BaseCleaner):
    """Clean certifications bronze data.

    Cleaning operations:
    1. Replace sentinel DOB (1900-01-02) with NaT.
    2. Null out age when DOB is missing (fixes age=0 bug).
    3. Map certificate columns to proper booleans.
    4. Validate gender values.
    """

    @property
    def _filename(self) -> str:
        return "silver_certifications.csv"

    @property
    def _expected_row_range(self) -> tuple[int, int]:
        return (19_000, 21_000)

    @property
    def _required_columns(self) -> list[str]:
        return [
            "club", "code", "person_type", "gender", "dob", "age",
            "mental_handicap", "parents_consent", "hap", "unified_partner",
        ]

    # ------------------------------------------------------------------
    # Cleaning
    # ------------------------------------------------------------------

    def clean(self) -> pd.DataFrame:
        df = self._df.copy()

        df = self._fix_sentinel_dob(df)
        df = self._fix_age_for_missing_dob(df)
        df = self._convert_certificates_to_bool(df)
        self._validate_gender(df)

        return df

    # ------------------------------------------------------------------
    # Private methods
    # ------------------------------------------------------------------

    @staticmethod
    def _fix_sentinel_dob(df: pd.DataFrame) -> pd.DataFrame:
        """Replace sentinel DOB 1900-01-02 with NaT."""
        df["dob"] = pd.to_datetime(df["dob"], errors="coerce")
        sentinel_mask = df["dob"] == _SENTINEL_DOB
        count = sentinel_mask.sum()
        if count:
            df.loc[sentinel_mask, "dob"] = pd.NaT
            logger.info("Replaced %d sentinel DOB values with NaT", count)
        return df

    @staticmethod
    def _fix_age_for_missing_dob(df: pd.DataFrame) -> pd.DataFrame:
        """Set age = NaN where DOB is missing (fixes age=0 default)."""
        missing_dob = df["dob"].isna()
        bad_age = missing_dob & df["age"].notna()
        count = bad_age.sum()
        if count:
            df.loc[missing_dob, "age"] = np.nan
            logger.info("Nulled age for %d rows with missing DOB", count)
        return df

    @staticmethod
    def _convert_certificates_to_bool(df: pd.DataFrame) -> pd.DataFrame:
        """Map certificate columns: 1.0 → True, everything else → False."""
        cert_cols = ["mental_handicap", "parents_consent", "hap", "unified_partner"]
        for col in cert_cols:
            df[col] = (df[col] == 1.0)
        return df

    @staticmethod
    def _validate_gender(df: pd.DataFrame) -> None:
        """Log warning if unexpected gender values found."""
        valid = {"M", "F", "U"}
        actual = set(df["gender"].dropna().unique())
        unexpected = actual - valid
        if unexpected:
            logger.warning("Unexpected gender values in certifications: %s", unexpected)
        else:
            logger.info("Gender values validated: %s", sorted(actual))

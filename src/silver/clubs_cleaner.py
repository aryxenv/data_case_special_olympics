"""Silver cleaner for the Clubs table."""

from __future__ import annotations

import logging

import pandas as pd

from src.silver.base_cleaner import BaseCleaner

logger = logging.getLogger(__name__)

# Canonical Belgian provinces (11 provinces + Brussels region)
_PROVINCE_MAP: dict[str, str] = {
    # Antwerpen variants
    "antwerpen": "Antwerpen",
    # Brabant Wallon variants
    "brabant wallon": "Brabant Wallon",
    "brabant-wallon": "Brabant Wallon",
    "babant wallon": "Brabant Wallon",  # typo in data
    # Brussel/Bruxelles variants
    "brussel/bruxelles": "Brussel/Bruxelles",
    "brussel": "Brussel/Bruxelles",
    "bruxelles": "Brussel/Bruxelles",
    # Hainaut
    "hainaut": "Hainaut",
    # Liège
    "liège": "Liège",
    "liege": "Liège",
    # Limburg
    "limburg": "Limburg",
    # Luxembourg (province)
    "luxembourg": "Luxembourg",
    # Namur
    "namur": "Namur",
    # Oost-Vlaanderen variants
    "oost-vlaanderen": "Oost-Vlaanderen",
    "oost vlaanderen": "Oost-Vlaanderen",
    # Vlaams-Brabant variants
    "vlaams-brabant": "Vlaams-Brabant",
    "vlaams brabant": "Vlaams-Brabant",
    # West-Vlaanderen variants
    "west-vlaanderen": "West-Vlaanderen",
    "west vlaanderen": "West-Vlaanderen",
    "west- vlaanderen": "West-Vlaanderen",  # extra space
}

# Values that are NOT valid provinces (regions/countries mis-entered)
_INVALID_PROVINCES = {"belgie", "wallonie"}

# All Belgium spelling variants → "Belgium"
_BELGIUM_VARIANTS = {
    "belgique", "belgië", "belgie", "belgium",
    "belguim",  # typo
    "belgïe", "belgïum",  # encoding issues
    "belgié",
}


class ClubsCleaner(BaseCleaner):
    """Clean clubs bronze data.

    Cleaning operations:
    1. Fix Province/Country swap (Group 786).
    2. Normalize country to 'Belgium' or 'Luxembourg'.
    3. Normalize province to 11 canonical Belgian provinces.
    4. Fill missing country with 'Belgium'.
    5. Title-case city names.
    6. Fix zipcode outlier (29900 → 2990).
    """

    @property
    def _filename(self) -> str:
        return "silver_clubs.csv"

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
    # Cleaning
    # ------------------------------------------------------------------

    def clean(self) -> pd.DataFrame:
        df = self._df.copy()

        df = self._fix_province_country_swap(df)
        df = self._normalize_country(df)
        df = self._normalize_province(df)
        df = self._standardize_city(df)
        df = self._fix_zipcode(df)

        return df

    # ------------------------------------------------------------------
    # Private methods
    # ------------------------------------------------------------------

    @staticmethod
    def _fix_province_country_swap(df: pd.DataFrame) -> pd.DataFrame:
        """Fix Group 786 where province and country are swapped."""
        mask = df["group_number"] == 786
        if mask.any():
            row = df.loc[mask].iloc[0]
            province_val = str(row["province"]).strip().lower()
            country_val = str(row["country"]).strip().lower()

            # Detect swap: province has a country name, country has a province name
            if province_val in _BELGIUM_VARIANTS and country_val in _PROVINCE_MAP:
                df.loc[mask, "province"] = row["country"]
                df.loc[mask, "country"] = row["province"]
                logger.info("Fixed Province/Country swap on Group 786")

        return df

    @staticmethod
    def _normalize_country(df: pd.DataFrame) -> pd.DataFrame:
        """Standardize all Belgium variants to 'Belgium', fill missing."""
        def _map_country(val: object) -> str | float:
            if pd.isna(val):
                return "Belgium"  # fill missing
            s = str(val).strip().lower()
            if s in _BELGIUM_VARIANTS:
                return "Belgium"
            if s == "luxembourg":
                return "Luxembourg"
            # Erroneous values: city or province names in country column
            if s in _PROVINCE_MAP or s in _INVALID_PROVINCES:
                return "Belgium"
            # Known city-as-country: WAREGEM
            if s == "waregem":
                return "Belgium"
            logger.warning("Unknown country value: '%s'", val)
            return "Belgium"

        before_missing = df["country"].isna().sum()
        df["country"] = df["country"].map(_map_country)
        logger.info(
            "Country normalized: filled %d missing, standardized to %s",
            before_missing, sorted(df["country"].unique()),
        )
        return df

    @staticmethod
    def _normalize_province(df: pd.DataFrame) -> pd.DataFrame:
        """Map province variants to canonical names."""
        def _map_province(val: object) -> str | float:
            if pd.isna(val):
                return val
            s = str(val).strip().lower()
            if s in _PROVINCE_MAP:
                return _PROVINCE_MAP[s]
            if s in _INVALID_PROVINCES:
                return pd.NA
            return str(val).strip()

        df["province"] = df["province"].map(_map_province)
        unique = sorted(df["province"].dropna().unique())
        logger.info("Province normalized to %d canonical values: %s", len(unique), unique)
        return df

    @staticmethod
    def _standardize_city(df: pd.DataFrame) -> pd.DataFrame:
        """Title-case city names for consistency."""
        df["city"] = df["city"].str.strip().str.title()
        logger.info("City names standardized to title case")
        return df

    @staticmethod
    def _fix_zipcode(df: pd.DataFrame) -> pd.DataFrame:
        """Fix outlier zipcode 29900 → 2990."""
        mask = df["zipcode"] == "29900"
        if mask.any():
            df.loc[mask, "zipcode"] = "2990"
            logger.info("Fixed zipcode 29900 → 2990 (Group 787)")
        return df

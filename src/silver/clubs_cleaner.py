"""Silver cleaner for the Clubs table."""

from __future__ import annotations

import json
import logging
import re
import time
import urllib.error
import urllib.parse
import urllib.request

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
    7. Enrich missing zipcodes with Nominatim geocoding.
    """

    _NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
    _NOMINATIM_USER_AGENT = "SpecialOlympicsETL/1.0 (student-project)"
    _NOMINATIM_TIMEOUT_SECONDS = 10
    _NOMINATIM_DELAY_SECONDS = 1.1

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
        df = self._enrich_missing_zipcodes(df)

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

    def _enrich_missing_zipcodes(self, df: pd.DataFrame) -> pd.DataFrame:
        """Fill missing zipcodes using Nominatim geocoding."""
        zipcode_text = df["zipcode"].astype("string").str.strip()
        missing = df["zipcode"].isna() | zipcode_text.isna() | (zipcode_text == "")
        missing_count = int(missing.sum())
        if missing_count == 0:
            return df

        logger.info("Attempting to enrich %d missing club zipcodes", missing_count)

        filled = 0
        lookup_cache: dict[tuple[str, str | None], str | None] = {}

        for idx, row in df.loc[missing].iterrows():
            query = self._build_geocoding_query(row)
            country_code = self._country_code(row.get("country"))
            if query is None:
                logger.warning(
                    "Could not build zipcode lookup query for Group %s (%s)",
                    row.get("group_number"),
                    row.get("name"),
                )
                continue

            cache_key = (query, country_code)
            if cache_key in lookup_cache:
                zipcode = lookup_cache[cache_key]
            else:
                zipcode = self._nominatim_lookup_zipcode(query, country_code)
                lookup_cache[cache_key] = zipcode
                time.sleep(self._NOMINATIM_DELAY_SECONDS)

            if zipcode is None:
                logger.warning(
                    "Could not enrich zipcode for Group %s (%s), query: '%s'",
                    row.get("group_number"),
                    row.get("name"),
                    query,
                )
                continue

            df.loc[idx, "zipcode"] = zipcode
            filled += 1
            logger.info(
                "Enriched zipcode for Group %s (%s): %s",
                row.get("group_number"),
                row.get("name"),
                zipcode,
            )

        logger.info("Zipcode enrichment filled %d/%d missing values", filled, missing_count)
        return df

    @staticmethod
    def _build_geocoding_query(row: pd.Series) -> str | None:
        """Build a geocoding query from available club location fields."""
        parts: list[str] = []
        for column in ("address_street_and_number", "city", "province", "country"):
            value = row.get(column)
            if pd.isna(value):
                continue
            text = str(value).strip()
            if text and text.lower() not in {"nan", "none"}:
                parts.append(text)
        return ", ".join(parts) if parts else None

    @staticmethod
    def _country_code(country: object) -> str | None:
        """Return a Nominatim country code for supported country names."""
        if pd.isna(country):
            return None
        normalized = str(country).strip().lower()
        if normalized == "belgium":
            return "be"
        if normalized == "luxembourg":
            return "lu"
        return None

    def _nominatim_lookup_zipcode(
        self,
        query: str,
        country_code: str | None,
    ) -> str | None:
        """Query Nominatim and return the first valid postal code."""
        params = {
            "q": query,
            "format": "json",
            "addressdetails": "1",
            "limit": "3",
        }
        if country_code:
            params["countrycodes"] = country_code

        url = f"{self._NOMINATIM_URL}?{urllib.parse.urlencode(params)}"
        request = urllib.request.Request(
            url,
            headers={"User-Agent": self._NOMINATIM_USER_AGENT},
        )

        try:
            with urllib.request.urlopen(
                request,
                timeout=self._NOMINATIM_TIMEOUT_SECONDS,
            ) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, UnicodeDecodeError) as exc:
            logger.warning("Nominatim lookup failed for query '%s': %s", query, exc)
            return None

        if not isinstance(payload, list):
            logger.warning("Unexpected Nominatim response for query '%s'", query)
            return None

        for result in payload:
            if not isinstance(result, dict):
                continue
            address = result.get("address")
            if not isinstance(address, dict):
                continue
            zipcode = self._normalize_zipcode(address.get("postcode"))
            if zipcode is not None:
                return zipcode

        return None

    @staticmethod
    def _normalize_zipcode(value: object) -> str | None:
        """Extract a valid Belgian/Luxembourg-style 4-digit postal code."""
        if pd.isna(value):
            return None
        match = re.search(r"\b\d{4}\b", str(value).strip())
        return match.group(0) if match else None

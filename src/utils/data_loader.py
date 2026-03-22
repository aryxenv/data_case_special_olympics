"""Utility for loading raw Special Olympics Excel files."""

from __future__ import annotations

import os
import re

import pandas as pd


class DataLoader:
    """Loads and caches raw Special Olympics Excel files."""

    _CERTIFICATIONS_FILE = "Thomas More Data Certifications.xlsx"
    _CLUBS_FILE = "Thomas More Data Clubs.xlsx"
    _RESULTS_TEMPLATE = "Thomas More Results {year}.xlsx"

    def __init__(self, raw_data_dir: str) -> None:
        self.raw_data_dir = raw_data_dir
        self._cache: dict[str, pd.DataFrame] = {}

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    @staticmethod
    def available_years() -> list[int]:
        """Return list of available result years (no 2020/2021)."""
        return [2015, 2016, 2017, 2018, 2019, 2022, 2023, 2024, 2025]

    @staticmethod
    def extract_year(filename: str) -> int:
        """Extract year from filename like 'Thomas More Results 2024.xlsx'."""
        match = re.search(r"(\d{4})", filename)
        if match is None:
            raise ValueError(f"Cannot extract year from filename: {filename}")
        return int(match.group(1))

    def list_raw_files(self) -> list[str]:
        """List all .xlsx files in the raw data directory."""
        return [
            f
            for f in os.listdir(self.raw_data_dir)
            if f.lower().endswith(".xlsx")
        ]

    # ------------------------------------------------------------------
    # Loaders
    # ------------------------------------------------------------------

    def load_certifications(self) -> pd.DataFrame:
        """Load Certifications Excel file, cached."""
        return self._load(self._CERTIFICATIONS_FILE)

    def load_clubs(self) -> pd.DataFrame:
        """Load Clubs Excel file, cached."""
        return self._load(self._CLUBS_FILE)

    def load_results(self, year: int) -> pd.DataFrame:
        """Load a single year's Results file, cached. Adds 'Year' column."""
        filename = self._RESULTS_TEMPLATE.format(year=year)
        df = self._load(filename)
        if "Year" not in df.columns:
            df["Year"] = year
        return df

    def load_all_results(self) -> pd.DataFrame:
        """Load and concatenate all Results files. Adds 'Year' column."""
        frames = [self.load_results(year) for year in self.available_years()]
        return pd.concat(frames, ignore_index=True)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _load(self, filename: str) -> pd.DataFrame:
        """Read an Excel file with caching."""
        if filename not in self._cache:
            path = os.path.join(self.raw_data_dir, filename)
            self._cache[filename] = pd.read_excel(path, engine="openpyxl")
        return self._cache[filename]

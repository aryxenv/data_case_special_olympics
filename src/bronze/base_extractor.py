"""Abstract base class for all bronze-layer extractors."""

from __future__ import annotations

import logging
import time
from abc import ABC, abstractmethod
from pathlib import Path

import pandas as pd

from src.utils import DataLoader

logger = logging.getLogger(__name__)


class BaseExtractor(ABC):
    """Template for bronze-layer extraction.

    Subclasses implement :meth:`extract` to read raw data and apply
    minimal transformations (column renaming, empty-row removal, type
    enforcement).  The :meth:`run` template method orchestrates the
    full extract → validate → save workflow.
    """

    def __init__(self, data_loader: DataLoader, output_dir: str | Path) -> None:
        self._loader = data_loader
        self._output_dir = Path(output_dir)
        self._output_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Abstract — each subclass must implement
    # ------------------------------------------------------------------

    @abstractmethod
    def extract(self) -> pd.DataFrame:
        """Read raw data and return a bronze-layer DataFrame."""
        ...

    @property
    @abstractmethod
    def _filename(self) -> str:
        """CSV filename for the persisted bronze output."""
        ...

    @property
    @abstractmethod
    def _expected_row_range(self) -> tuple[int, int]:
        """(min, max) expected row count for validation."""
        ...

    @property
    @abstractmethod
    def _required_columns(self) -> list[str]:
        """Columns that must be present after extraction."""
        ...

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def validate(self, df: pd.DataFrame) -> None:
        """Check row count bounds and required columns.

        Raises ``ValueError`` on any failed check.
        """
        row_min, row_max = self._expected_row_range
        if not (row_min <= len(df) <= row_max):
            raise ValueError(
                f"{self.__class__.__name__}: row count {len(df)} "
                f"outside expected range [{row_min}, {row_max}]"
            )

        missing = set(self._required_columns) - set(df.columns)
        if missing:
            raise ValueError(
                f"{self.__class__.__name__}: missing required columns: {missing}"
            )

        logger.info(
            "%s validated — %d rows, %d columns",
            self.__class__.__name__, len(df), len(df.columns),
        )

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def save(self, df: pd.DataFrame) -> Path:
        """Write the bronze DataFrame to CSV and return the output path."""
        path = self._output_dir / self._filename
        df.to_csv(path, index=False)
        logger.info("%s saved → %s", self.__class__.__name__, path)
        return path

    # ------------------------------------------------------------------
    # Template method
    # ------------------------------------------------------------------

    def run(self) -> pd.DataFrame:
        """Execute the full extract → validate → save workflow."""
        start = time.perf_counter()

        df = self.extract()
        self.validate(df)
        self.save(df)

        elapsed = time.perf_counter() - start
        logger.info(
            "%s completed in %.2fs (%d rows)",
            self.__class__.__name__, elapsed, len(df),
        )
        return df

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _to_snake_case(name: str) -> str:
        """Convert a column name to snake_case.

        Examples::

            'Person type'                              → 'person_type'
            'DOB'                                      → 'dob'
            'Mental Handicap (SOB has this certificate)' → 'mental_handicap'
            'Summary (all)'                            → 'summary_all'
            'Address (Street and Number)'              → 'address_street_and_number'
            'Participation Games 2015'                 → 'participation_games_2015'
        """
        import re

        # Strip parenthetical qualifiers but keep useful content
        # e.g. "Mental Handicap (SOB has this certificate)" → "Mental Handicap"
        # but  "Summary (all)" → "Summary all"
        # and  "Address (Street and Number)" → "Address Street and Number"
        name = re.sub(r"\(SOB[^)]*\)", "", name)  # drop SOB certification noise
        name = re.sub(r"[()]", " ", name)          # open remaining parens as spaces

        # Normalize whitespace and special chars
        name = re.sub(r"[^\w\s]", " ", name)
        name = "_".join(name.lower().split())
        return name

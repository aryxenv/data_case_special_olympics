"""Abstract base class for all silver-layer cleaners."""

from __future__ import annotations

import logging
import time
from abc import ABC, abstractmethod
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)


class BaseCleaner(ABC):
    """Template for silver-layer data cleaning.

    Subclasses implement :meth:`clean` to apply standardization,
    null handling, deduplication, and format normalization.
    The :meth:`run` template method orchestrates the
    full clean → validate → save workflow.
    """

    def __init__(self, df: pd.DataFrame, output_dir: str | Path) -> None:
        self._df = df.copy()
        self._output_dir = Path(output_dir)
        self._output_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Abstract — each subclass must implement
    # ------------------------------------------------------------------

    @abstractmethod
    def clean(self) -> pd.DataFrame:
        """Apply all cleaning logic and return the silver DataFrame."""
        ...

    @property
    @abstractmethod
    def _filename(self) -> str:
        """CSV filename for the persisted silver output."""
        ...

    @property
    @abstractmethod
    def _expected_row_range(self) -> tuple[int, int]:
        """(min, max) expected row count for validation."""
        ...

    @property
    @abstractmethod
    def _required_columns(self) -> list[str]:
        """Columns that must be present after cleaning."""
        ...

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def validate(self, df: pd.DataFrame) -> None:
        """Check row count bounds and required columns."""
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
        """Write the silver DataFrame to CSV."""
        path = self._output_dir / self._filename
        df.to_csv(path, index=False)
        logger.info("%s saved → %s", self.__class__.__name__, path)
        return path

    # ------------------------------------------------------------------
    # Template method
    # ------------------------------------------------------------------

    def run(self) -> pd.DataFrame:
        """Execute the full clean → validate → save workflow."""
        start = time.perf_counter()

        df = self.clean()
        self.validate(df)
        self.save(df)

        elapsed = time.perf_counter() - start
        logger.info(
            "%s completed in %.2fs (%d rows)",
            self.__class__.__name__, elapsed, len(df),
        )
        return df

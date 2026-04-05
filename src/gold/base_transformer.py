"""Abstract base class for all gold-layer transformers."""

from __future__ import annotations

import logging
import time
from abc import ABC, abstractmethod
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)


class BaseTransformer(ABC):
    """Template for gold-layer star-schema transformations.

    Subclasses implement :meth:`transform` to produce a single
    dimension or fact table.  The :meth:`run` template method
    orchestrates transform → validate → save.
    """

    def __init__(self, output_dir: str | Path) -> None:
        self._output_dir = Path(output_dir)
        self._output_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Abstract
    # ------------------------------------------------------------------

    @abstractmethod
    def transform(self) -> pd.DataFrame:
        """Produce the gold-layer DataFrame."""
        ...

    @property
    @abstractmethod
    def _filename(self) -> str:
        """CSV filename (e.g., ``dim_athlete.csv``)."""
        ...

    @property
    @abstractmethod
    def _expected_row_range(self) -> tuple[int, int]:
        ...

    @property
    @abstractmethod
    def _required_columns(self) -> list[str]:
        ...

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def validate(self, df: pd.DataFrame) -> None:
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
        path = self._output_dir / self._filename
        df.to_csv(path, index=False)
        logger.info("%s saved → %s", self.__class__.__name__, path)
        return path

    # ------------------------------------------------------------------
    # Template method
    # ------------------------------------------------------------------

    def run(self) -> pd.DataFrame:
        start = time.perf_counter()
        df = self.transform()
        self.validate(df)
        self.save(df)
        elapsed = time.perf_counter() - start
        logger.info(
            "%s completed in %.2fs (%d rows)",
            self.__class__.__name__, elapsed, len(df),
        )
        return df

"""ETL pipeline orchestrator for the Special Olympics data project.

Coordinates the medallion-architecture layers:
- **Bronze:** raw extraction (Week 4)
- **Silver:** cleaning & standardization (Week 5)
- **Gold:** star-schema transformation (Weeks 6-7 — placeholder)
"""

from __future__ import annotations

import logging
import time
from pathlib import Path

import pandas as pd

from src.bronze import CertificationsExtractor, ClubsExtractor, ResultsExtractor
from src.silver import (
    CertificationsCleaner,
    ClubsCleaner,
    ResultsCleaner,
)
from src.utils import DataLoader

logger = logging.getLogger(__name__)

# Project paths
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_RAW_DIR = _PROJECT_ROOT / "data" / "raw"
_BRONZE_DIR = _PROJECT_ROOT / "data" / "bronze"
_SILVER_DIR = _PROJECT_ROOT / "data" / "silver"
_PROCESSED_DIR = _PROJECT_ROOT / "data" / "processed"


class Pipeline:
    """Orchestrates the full ETL pipeline across medallion layers.

    Usage::

        pipeline = Pipeline()
        pipeline.run_bronze()      # Week 4
        pipeline.run_silver()      # Week 5
        # pipeline.run_gold()      # Weeks 6-7
    """

    def __init__(
        self,
        raw_dir: str | Path = _RAW_DIR,
        bronze_dir: str | Path = _BRONZE_DIR,
        silver_dir: str | Path = _SILVER_DIR,
        processed_dir: str | Path = _PROCESSED_DIR,
    ) -> None:
        self._raw_dir = Path(raw_dir)
        self._bronze_dir = Path(bronze_dir)
        self._silver_dir = Path(silver_dir)
        self._processed_dir = Path(processed_dir)
        self._loader = DataLoader(str(self._raw_dir))

        # Bronze outputs stored after extraction
        self.bronze_certifications: pd.DataFrame | None = None
        self.bronze_clubs: pd.DataFrame | None = None
        self.bronze_results: pd.DataFrame | None = None

        # Silver outputs stored after cleaning
        self.silver_certifications: pd.DataFrame | None = None
        self.silver_clubs: pd.DataFrame | None = None
        self.silver_results: pd.DataFrame | None = None

    # ------------------------------------------------------------------
    # Bronze layer
    # ------------------------------------------------------------------

    def run_bronze(self) -> None:
        """Execute all bronze-layer extractors."""
        logger.info("=" * 60)
        logger.info("BRONZE LAYER — Extraction")
        logger.info("=" * 60)
        start = time.perf_counter()

        self.bronze_certifications = CertificationsExtractor(
            self._loader, self._bronze_dir
        ).run()

        self.bronze_clubs = ClubsExtractor(
            self._loader, self._bronze_dir
        ).run()

        self.bronze_results = ResultsExtractor(
            self._loader, self._bronze_dir
        ).run()

        elapsed = time.perf_counter() - start
        self._log_summary("Bronze extraction", elapsed, {
            "Certifications": self.bronze_certifications,
            "Clubs": self.bronze_clubs,
            "Results": self.bronze_results,
        }, self._bronze_dir)

    # ------------------------------------------------------------------
    # Silver layer
    # ------------------------------------------------------------------

    def run_silver(self) -> None:
        """Execute all silver-layer cleaners.

        Requires bronze layer to have been run first.
        """
        if self.bronze_certifications is None:
            raise RuntimeError("Bronze layer must be run before Silver")

        logger.info("=" * 60)
        logger.info("SILVER LAYER — Cleaning")
        logger.info("=" * 60)
        start = time.perf_counter()

        self.silver_certifications = CertificationsCleaner(
            self.bronze_certifications, self._silver_dir
        ).run()

        self.silver_clubs = ClubsCleaner(
            self.bronze_clubs, self._silver_dir
        ).run()

        self.silver_results = ResultsCleaner(
            self.bronze_results, self._silver_dir
        ).run()

        elapsed = time.perf_counter() - start
        self._log_summary("Silver cleaning", elapsed, {
            "Certifications": self.silver_certifications,
            "Clubs": self.silver_clubs,
            "Results": self.silver_results,
        }, self._silver_dir)

    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------

    @staticmethod
    def _log_summary(
        label: str,
        elapsed: float,
        tables: dict[str, pd.DataFrame | None],
        output_dir: Path,
    ) -> None:
        """Print a summary of a pipeline stage."""
        logger.info("-" * 60)
        logger.info("%s complete (%.2fs)", label, elapsed)
        for name, df in tables.items():
            logger.info(
                "  %-17s: %s rows",
                name,
                f"{len(df):,}" if df is not None else "N/A",
            )
        logger.info("  Output dir     : %s", output_dir)
        logger.info("-" * 60)

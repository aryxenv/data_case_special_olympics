"""ETL pipeline orchestrator for the Special Olympics data project.

Coordinates the medallion-architecture layers:
- **Bronze:** raw extraction (Week 4)
- **Silver:** cleaning & standardization (Week 5 — placeholder)
- **Gold:** star-schema transformation (Weeks 6-7 — placeholder)
"""

from __future__ import annotations

import logging
import time
from pathlib import Path

import pandas as pd

from src.bronze import CertificationsExtractor, ClubsExtractor, ResultsExtractor
from src.utils import DataLoader

logger = logging.getLogger(__name__)

# Project paths
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_RAW_DIR = _PROJECT_ROOT / "data" / "raw"
_BRONZE_DIR = _PROJECT_ROOT / "data" / "bronze"
_PROCESSED_DIR = _PROJECT_ROOT / "data" / "processed"


class Pipeline:
    """Orchestrates the full ETL pipeline across medallion layers.

    Usage::

        pipeline = Pipeline()
        pipeline.run_bronze()      # Week 4
        # pipeline.run_silver()    # Week 5
        # pipeline.run_gold()      # Weeks 6-7
    """

    def __init__(
        self,
        raw_dir: str | Path = _RAW_DIR,
        bronze_dir: str | Path = _BRONZE_DIR,
        processed_dir: str | Path = _PROCESSED_DIR,
    ) -> None:
        self._raw_dir = Path(raw_dir)
        self._bronze_dir = Path(bronze_dir)
        self._processed_dir = Path(processed_dir)
        self._loader = DataLoader(str(self._raw_dir))

        # Bronze outputs stored after extraction
        self.bronze_certifications: pd.DataFrame | None = None
        self.bronze_clubs: pd.DataFrame | None = None
        self.bronze_results: pd.DataFrame | None = None

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
        self._log_bronze_summary(elapsed)

    def _log_bronze_summary(self, elapsed: float) -> None:
        """Print a summary of the bronze extraction results."""
        logger.info("-" * 60)
        logger.info("Bronze extraction complete (%.2fs)", elapsed)
        logger.info(
            "  Certifications : %s rows",
            f"{len(self.bronze_certifications):,}" if self.bronze_certifications is not None else "N/A",
        )
        logger.info(
            "  Clubs          : %s rows",
            f"{len(self.bronze_clubs):,}" if self.bronze_clubs is not None else "N/A",
        )
        logger.info(
            "  Results        : %s rows",
            f"{len(self.bronze_results):,}" if self.bronze_results is not None else "N/A",
        )
        logger.info("  Output dir     : %s", self._bronze_dir)
        logger.info("-" * 60)

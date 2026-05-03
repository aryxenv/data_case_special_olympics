r"""Special Olympics ETL pipeline - entry point.

Usage::

    python src\main.py
"""

import logging
from pathlib import Path
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.orchestration import Pipeline


def main() -> None:
    """Run the full ETL pipeline."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
        datefmt="%H:%M:%S",
        stream=sys.stdout,
    )

    pipeline = Pipeline()

    # Week 4: Bronze extraction
    pipeline.run_bronze()

    # Week 5: Silver cleaning
    pipeline.run_silver()

    # Week 6: Gold transformation (star schema)
    pipeline.run_gold()

    # Week 7: Output validation
    pipeline.run_validation()


if __name__ == "__main__":
    main()

"""Special Olympics ETL pipeline — entry point.

Usage::

    python main.py
"""

import logging
import sys

from src.pipeline import Pipeline


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

    # Weeks 6-7: Gold transformation (placeholder)
    # pipeline.run_gold()


if __name__ == "__main__":
    main()

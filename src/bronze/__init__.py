"""Bronze layer extractors for the Special Olympics ETL pipeline.

The bronze layer reads raw Excel files and applies minimal transformations
(column renaming, empty-row removal, type enforcement) before persisting
as CSV for downstream processing.
"""

from .base_extractor import BaseExtractor
from .certifications_extractor import CertificationsExtractor
from .clubs_extractor import ClubsExtractor
from .results_extractor import ResultsExtractor

__all__ = [
    "BaseExtractor",
    "CertificationsExtractor",
    "ClubsExtractor",
    "ResultsExtractor",
]

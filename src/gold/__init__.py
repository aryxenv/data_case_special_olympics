"""Gold layer transformers for the Special Olympics ETL pipeline.

The gold layer transforms cleaned silver data into the star schema:
5 dimension tables and 2 fact tables, exported to data/gold/.
"""

from .base_transformer import BaseTransformer
from .dim_athlete import DimAthleteTransformer
from .dim_event import DimEventTransformer
from .dim_geography import DimGeographyTransformer
from .dim_sport import DimSportTransformer
from .dim_time import DimTimeTransformer
from .fact_participation import FactParticipationTransformer
from .fact_results import FactResultsTransformer

__all__ = [
    "BaseTransformer",
    "DimAthleteTransformer",
    "DimEventTransformer",
    "DimGeographyTransformer",
    "DimSportTransformer",
    "DimTimeTransformer",
    "FactParticipationTransformer",
    "FactResultsTransformer",
]

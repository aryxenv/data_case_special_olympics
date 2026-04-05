"""Gold transformer for dim_event."""

from __future__ import annotations

import logging
import re
from pathlib import Path

import pandas as pd

from src.gold.base_transformer import BaseTransformer

logger = logging.getLogger(__name__)

# Regex for standard event code prefix: AT17, AQ25, CY05, BO, BOI, etc.
_RE_EVENT_CODE = re.compile(r"^([A-Za-z]{2,5}\d*)\s*-")

# Sport-code prefix mapping for synthetic codes (edge cases without standard prefix)
_SPORT_PREFIX: dict[str, str] = {
    "Football/Soccer": "FO",
    "Adapted Physical Activities": "APA",
    "Motor Activities": "MA",
    "Sportgames": "SG",
    "Floorball": "FL",
    "Netball": "NB",
}


class DimEventTransformer(BaseTransformer):
    """Build the event dimension with normalized event codes.

    Extracts stable event code prefixes (e.g., ``AT17``, ``AQ25``) from
    bilingual event names. For edge cases without a standard prefix,
    generates a synthetic code from the sport name.
    """

    def __init__(
        self,
        silver_results: pd.DataFrame,
        dim_sport: pd.DataFrame,
        output_dir: str | Path,
    ) -> None:
        super().__init__(output_dir)
        self._results = silver_results
        self._dim_sport = dim_sport

    @property
    def _filename(self) -> str:
        return "dim_event.csv"

    @property
    def _expected_row_range(self) -> tuple[int, int]:
        return (100, 400)

    @property
    def _required_columns(self) -> list[str]:
        return ["event_key", "sport_key", "event_code", "event_name"]

    def transform(self) -> pd.DataFrame:
        # Build sport name → sport_key lookup
        sport_lookup = dict(
            zip(self._dim_sport["sport_name"], self._dim_sport["sport_key"])
        )

        # Extract event codes from all result rows
        events = self._results[["sport", "event"]].dropna(subset=["event"]).copy()
        events["event_code"] = events["event"].apply(self._extract_code)

        # For rows without a standard code, generate synthetic code from sport
        no_code = events["event_code"].isna()
        if no_code.any():
            events.loc[no_code, "event_code"] = events.loc[no_code].apply(
                lambda r: self._synthetic_code(r["sport"], r["event"]), axis=1
            )

        # For each (event_code, sport) pair, pick the most frequent event name
        event_counts = (
            events.groupby(["event_code", "sport", "event"])
            .size()
            .reset_index(name="count")
        )
        best_names = (
            event_counts.sort_values("count", ascending=False)
            .drop_duplicates(subset=["event_code", "sport"], keep="first")
        )

        # Build the dimension table
        df = best_names[["event_code", "sport", "event"]].copy()
        df = df.rename(columns={"event": "event_name"})
        df["sport_key"] = df["sport"].map(sport_lookup)
        df = df.drop(columns=["sport"])
        df = df.sort_values(["sport_key", "event_code"]).reset_index(drop=True)
        df.insert(0, "event_key", range(1, len(df) + 1))

        logger.info(
            "dim_event: %d events from %d raw event names",
            len(df), events["event"].nunique(),
        )
        return df

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_code(event_name: str) -> str | None:
        """Extract event code prefix via regex (e.g., 'AT17 - ...' → 'AT17')."""
        m = _RE_EVENT_CODE.match(str(event_name).strip())
        return m.group(1).upper() if m else None

    @staticmethod
    def _synthetic_code(sport: str, event: str) -> str:
        """Generate a synthetic event code for events without a standard prefix."""
        prefix = _SPORT_PREFIX.get(sport, sport[:3].upper())
        # Use the first meaningful word after cleaning
        cleaned = re.sub(r"[^A-Za-z0-9\s]", "", str(event))
        words = cleaned.split()
        suffix = words[0].upper()[:6] if words else "OTHER"
        return f"{prefix}-{suffix}"

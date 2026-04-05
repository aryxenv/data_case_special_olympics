"""Silver cleaner for the Results table."""

from __future__ import annotations

import logging
import re

import numpy as np
import pandas as pd

from src.silver.base_cleaner import BaseCleaner

logger = logging.getLogger(__name__)

# Ordinal place → integer rank
_ORDINAL_MAP: dict[str, int] = {
    "1st": 1, "2nd": 2, "3rd": 3, "4th": 4, "5th": 5,
    "6th": 6, "7th": 7, "8th": 8, "9th": 9, "10th": 10,
}

# Non-completion status codes
_STATUS_CODES = {"DNS", "DNF", "DNC", "DNT"}

# Gender standardization map
_GENDER_MAP: dict[str, str] = {
    "Male": "M",
    "Female": "F",
    "Unknown": "U",
    "M": "M",
    "F": "F",
    "U": "U",
}

# Score parsing patterns
_RE_HR_MIN_SEC = re.compile(
    r"(\d+)\s*hr,\s*(\d+)\s*min,\s*([\d.]+)\s*sec"
)
_RE_MIN_SEC = re.compile(
    r"(\d+)\s*min,\s*([\d.]+)\s*sec"
)
_RE_METERS = re.compile(
    r"(\d+)m,\s*([\d.]+)cm"
)
_RE_POINTS = re.compile(
    r"([\d.]+)\s*points?"
)


class ResultsCleaner(BaseCleaner):
    """Clean results bronze data.

    Cleaning operations:
    1. Drop rows with null athlete code.
    2. Standardize gender (Male→M, Female→F, Unknown→U).
    3. Parse place column into rank, result_status, is_disqualified.
    4. Parse score column into score_value (float) and score_unit.
    5. Deduplicate multi-round entries per (code, event, sport, year).
    """

    @property
    def _filename(self) -> str:
        return "silver_results.csv"

    @property
    def _expected_row_range(self) -> tuple[int, int]:
        # 112,375 bronze → ~60,000-80,000 after dedup
        return (55_000, 85_000)

    @property
    def _required_columns(self) -> list[str]:
        return [
            "code", "club", "sport", "event", "year", "gender",
            "place", "rank", "result_status", "is_disqualified",
            "score", "score_value", "score_unit",
        ]

    # ------------------------------------------------------------------
    # Cleaning
    # ------------------------------------------------------------------

    def clean(self) -> pd.DataFrame:
        df = self._df.copy()

        df = self._drop_null_codes(df)
        df = self._standardize_gender(df)
        df = self._parse_place(df)
        df = self._parse_score(df)
        df = self._deduplicate_rounds(df)

        return df

    # ------------------------------------------------------------------
    # 1. Null code removal
    # ------------------------------------------------------------------

    @staticmethod
    def _drop_null_codes(df: pd.DataFrame) -> pd.DataFrame:
        """Remove rows where athlete code is missing."""
        null_mask = df["code"].isna() | (df["code"].astype(str).str.strip() == "")
        count = null_mask.sum()
        if count:
            df = df[~null_mask].reset_index(drop=True)
            logger.info("Dropped %d rows with null/empty code", count)
        return df

    # ------------------------------------------------------------------
    # 2. Gender standardization
    # ------------------------------------------------------------------

    @staticmethod
    def _standardize_gender(df: pd.DataFrame) -> pd.DataFrame:
        """Map Male→M, Female→F, Unknown→U."""
        df["gender"] = df["gender"].map(_GENDER_MAP)
        unmapped = df["gender"].isna().sum()
        logger.info(
            "Gender standardized — distribution: %s (unmapped NaN: %d)",
            df["gender"].value_counts().to_dict(), unmapped,
        )
        return df

    # ------------------------------------------------------------------
    # 3. Place parsing
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_place(df: pd.DataFrame) -> pd.DataFrame:
        """Parse place column into rank (int), result_status, is_disqualified."""
        ranks = []
        statuses = []
        is_dq = []

        for val in df["place"]:
            if pd.isna(val):
                ranks.append(np.nan)
                statuses.append(None)
                is_dq.append(False)
                continue

            val_str = str(val).strip()

            # Ordinal ranks (1st, 2nd, ...)
            if val_str.lower() in _ORDINAL_MAP:
                ranks.append(_ORDINAL_MAP[val_str.lower()])
                statuses.append(None)
                is_dq.append(False)

            # Disqualification codes
            elif val_str.upper().startswith("DQ"):
                ranks.append(np.nan)
                # Normalize: "DQ: HE" → "DQ-HE", "DQ-HE" stays
                normalized = re.sub(r"DQ[:\s]+", "DQ-", val_str.upper()).strip()
                statuses.append(normalized)
                is_dq.append(True)

            # Non-completion codes
            elif val_str.upper() in _STATUS_CODES:
                ranks.append(np.nan)
                statuses.append(val_str.upper())
                is_dq.append(False)

            # Aquatics skill levels (AQ 0.1, AQ 6.2, AQ B.2, etc.)
            elif val_str.upper().startswith("AQ "):
                ranks.append(np.nan)
                statuses.append(val_str.strip())
                is_dq.append(False)

            # Other (Part, ZERO, SW7.2.2, etc.)
            elif val_str.lower() in ("part", "zero"):
                ranks.append(np.nan)
                statuses.append(val_str.upper())
                is_dq.append(False)

            else:
                # Try numeric
                try:
                    ranks.append(int(float(val_str)))
                    statuses.append(None)
                    is_dq.append(False)
                except (ValueError, TypeError):
                    ranks.append(np.nan)
                    statuses.append(val_str)
                    is_dq.append(False)

        df["rank"] = pd.array(ranks, dtype=pd.Int64Dtype())
        df["result_status"] = statuses
        df["is_disqualified"] = is_dq

        ranked = df["rank"].notna().sum()
        dq_count = df["is_disqualified"].sum()
        status_count = df["result_status"].notna().sum()
        logger.info(
            "Place parsed — ranked: %d, DQ: %d, other status: %d, no place: %d",
            ranked, dq_count, status_count - dq_count,
            df["place"].isna().sum(),
        )
        return df

    # ------------------------------------------------------------------
    # 4. Score parsing
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_score(df: pd.DataFrame) -> pd.DataFrame:
        """Parse score strings into score_value (float) and score_unit."""
        values = []
        units = []

        for val in df["score"]:
            if pd.isna(val):
                values.append(np.nan)
                units.append(None)
                continue

            val_str = str(val).strip()

            # Skip non-score values (DNS, etc.)
            if val_str.upper() in _STATUS_CODES:
                values.append(np.nan)
                units.append(None)
                continue

            # Pattern 1: X hr, Y min, Z.ZZ sec
            m = _RE_HR_MIN_SEC.match(val_str)
            if m:
                hrs, mins, secs = float(m.group(1)), float(m.group(2)), float(m.group(3))
                values.append(hrs * 3600 + mins * 60 + secs)
                units.append("seconds")
                continue

            # Pattern 2: X min, Y.ZZ sec
            m = _RE_MIN_SEC.match(val_str)
            if m:
                mins, secs = float(m.group(1)), float(m.group(2))
                values.append(mins * 60 + secs)
                units.append("seconds")
                continue

            # Pattern 3: Xm, Y.ZZcm
            m = _RE_METERS.match(val_str)
            if m:
                meters, cm = float(m.group(1)), float(m.group(2))
                values.append(meters + cm / 100)
                units.append("meters")
                continue

            # Pattern 4: X.XX points
            m = _RE_POINTS.match(val_str)
            if m:
                values.append(float(m.group(1)))
                units.append("points")
                continue

            # Unparseable
            values.append(np.nan)
            units.append(None)

        df["score_value"] = values
        df["score_unit"] = units

        parsed = pd.notna(df["score_value"]).sum()
        total_non_null = df["score"].notna().sum()
        logger.info(
            "Score parsed — %d/%d non-null scores converted (%.1f%%)",
            parsed, total_non_null,
            parsed / total_non_null * 100 if total_non_null else 0,
        )

        # Log unit distribution
        unit_dist = df["score_unit"].value_counts().to_dict()
        logger.info("Score unit distribution: %s", unit_dist)

        return df

    # ------------------------------------------------------------------
    # 5. Multi-round deduplication
    # ------------------------------------------------------------------

    @staticmethod
    def _deduplicate_rounds(df: pd.DataFrame) -> pd.DataFrame:
        """Keep best/final result per (code, event, sport, year).

        Strategy: sort so the best row comes first, then drop duplicates.
        Priority: 1) has a rank, 2) lowest rank, 3) highest score, 4) last row.
        """
        before = len(df)
        group_key = ["code", "event", "sport", "year"]

        # Sort key: rows with rank first, then by rank asc, score desc
        df = df.copy()
        df["_has_rank"] = df["rank"].notna().astype(int) * -1  # -1 = has rank (sorts first)
        df["_rank_sort"] = df["rank"].fillna(9999)
        df["_score_sort"] = df["score_value"].fillna(-1) * -1  # negate for descending

        df = df.sort_values(
            ["_has_rank", "_rank_sort", "_score_sort"],
            ascending=True,
        )
        df = df.drop_duplicates(subset=group_key, keep="first")
        df = df.drop(columns=["_has_rank", "_rank_sort", "_score_sort"])
        df = df.reset_index(drop=True)

        after = len(df)
        logger.info(
            "Multi-round dedup: %d → %d rows (removed %d, %.1f%%)",
            before, after, before - after,
            (before - after) / before * 100 if before else 0,
        )
        return df

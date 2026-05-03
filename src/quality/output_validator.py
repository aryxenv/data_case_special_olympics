"""Post-pipeline validation for gold-layer star-schema outputs.

Checks file existence, column schemas, row counts, foreign-key
integrity, and data-quality assertions against the dimensional model.
"""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

from src.quality.reporting import CheckResult, ValidationReport
from src.quality.schemas import FK_CHECKS, ROW_BOUNDS, SCHEMAS, VALUE_CHECKS

logger = logging.getLogger(__name__)


class OutputValidator:
    """Validates gold-layer star-schema outputs against the dimensional model.

    Usage::

        validator = OutputValidator(gold_dir="data/gold")
        report = validator.run()
        report.log_summary()
    """

    def __init__(self, gold_dir: str | Path) -> None:
        self._gold_dir = Path(gold_dir)
        self._tables: dict[str, pd.DataFrame] = {}

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------

    def run(self) -> ValidationReport:
        """Execute all validation checks and return a report."""
        report = ValidationReport()

        self._check_files_exist(report)
        if report.failed > 0:
            return report  # can't proceed without files

        self._load_tables()
        self._check_schemas(report)
        self._check_row_counts(report)
        self._check_nulls(report)
        self._check_fk_integrity(report)
        self._check_data_values(report)
        self._check_surrogate_keys(report)

        return report

    # ------------------------------------------------------------------
    # File existence
    # ------------------------------------------------------------------

    def _check_files_exist(self, report: ValidationReport) -> None:
        for table in SCHEMAS:
            path = self._gold_dir / f"{table}.csv"
            exists = path.is_file()
            report.checks.append(CheckResult(
                name=f"file:{table}",
                passed=exists,
                message=f"{path.name} {'exists' if exists else 'MISSING'}",
            ))

    def _load_tables(self) -> None:
        for table in SCHEMAS:
            path = self._gold_dir / f"{table}.csv"
            self._tables[table] = pd.read_csv(path, low_memory=False)

    # ------------------------------------------------------------------
    # Schema validation
    # ------------------------------------------------------------------

    def _check_schemas(self, report: ValidationReport) -> None:
        for table, expected_cols in SCHEMAS.items():
            df = self._tables[table]
            actual = set(df.columns)
            expected = set(expected_cols.keys())

            missing = expected - actual
            extra = actual - expected

            passed = len(missing) == 0
            parts = []
            if missing:
                parts.append(f"missing: {sorted(missing)}")
            if extra:
                parts.append(f"extra: {sorted(extra)}")
            if not parts:
                parts.append(f"{len(expected)} columns OK")

            report.checks.append(CheckResult(
                name=f"schema:{table}",
                passed=passed,
                message="; ".join(parts),
            ))

    # ------------------------------------------------------------------
    # Row counts
    # ------------------------------------------------------------------

    def _check_row_counts(self, report: ValidationReport) -> None:
        for table, (lo, hi) in ROW_BOUNDS.items():
            n = len(self._tables[table])
            passed = lo <= n <= hi
            report.checks.append(CheckResult(
                name=f"rows:{table}",
                passed=passed,
                message=f"{n:,} rows (expected {lo:,}–{hi:,})",
            ))

    # ------------------------------------------------------------------
    # NULL checks on non-nullable columns
    # ------------------------------------------------------------------

    def _check_nulls(self, report: ValidationReport) -> None:
        for table, col_spec in SCHEMAS.items():
            df = self._tables[table]
            non_nullable = [c for c, nullable in col_spec.items() if not nullable]
            for col in non_nullable:
                if col not in df.columns:
                    continue
                null_count = df[col].isna().sum()
                passed = null_count == 0
                report.checks.append(CheckResult(
                    name=f"null:{table}.{col}",
                    passed=passed,
                    message=f"{null_count} nulls" if null_count else "no nulls",
                ))

    # ------------------------------------------------------------------
    # Foreign-key integrity
    # ------------------------------------------------------------------

    def _check_fk_integrity(self, report: ValidationReport) -> None:
        for fact_table, fk_col, dim_table, pk_col in FK_CHECKS:
            fact_df = self._tables[fact_table]
            dim_df = self._tables[dim_table]

            if fk_col not in fact_df.columns or pk_col not in dim_df.columns:
                continue

            fact_keys = set(fact_df[fk_col].dropna().unique())
            dim_keys = set(dim_df[pk_col].dropna().unique())
            orphans = fact_keys - dim_keys
            coverage = len(fact_keys - orphans) / len(fact_keys) * 100 if fact_keys else 100

            passed = len(orphans) == 0
            report.checks.append(CheckResult(
                name=f"fk:{fact_table}.{fk_col}→{dim_table}",
                passed=passed,
                message=f"{len(orphans)} orphans ({coverage:.1f}% coverage)",
            ))

    # ------------------------------------------------------------------
    # Data-value checks
    # ------------------------------------------------------------------

    def _check_data_values(self, report: ValidationReport) -> None:
        for table, col_checks in VALUE_CHECKS.items():
            df = self._tables[table]
            for col, valid_values in col_checks.items():
                if col not in df.columns:
                    continue
                actual = set(df[col].dropna().unique())
                invalid = actual - valid_values
                passed = len(invalid) == 0
                report.checks.append(CheckResult(
                    name=f"values:{table}.{col}",
                    passed=passed,
                    message=f"valid: {sorted(actual)}" if passed else f"invalid: {sorted(invalid)}",
                ))

    # ------------------------------------------------------------------
    # Surrogate key uniqueness
    # ------------------------------------------------------------------

    def _check_surrogate_keys(self, report: ValidationReport) -> None:
        sk_cols = {
            "dim_time": "time_key",
            "dim_athlete": "athlete_key",
            "dim_geography": "geography_key",
            "dim_sport": "sport_key",
            "dim_event": "event_key",
            "fact_results": "result_key",
        }
        for table, col in sk_cols.items():
            df = self._tables[table]
            if col not in df.columns:
                continue
            dupes = df[col].duplicated().sum()
            passed = dupes == 0
            report.checks.append(CheckResult(
                name=f"unique:{table}.{col}",
                passed=passed,
                message=f"{dupes} duplicates" if dupes else "unique",
            ))

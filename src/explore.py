"""Data profiling utility for Special Olympics raw Excel files.

Provides a class-based profiler to inspect schemas, detect quality issues,
and compare structures across the source files before ETL processing.
"""

import os

import pandas as pd


class DataProfiler:
    """Profiles raw Excel files: schemas, column stats, duplicates, and integrity checks."""

    def __init__(self, raw_data_dir: str):
        self.raw_data_dir = raw_data_dir
        self._profiles: dict[str, dict] = {}

    # ------------------------------------------------------------------
    # File-level profiling
    # ------------------------------------------------------------------

    def profile_file(self, filename: str) -> dict:
        """Return a profile dict for every sheet in *filename*.

        Keys per sheet: columns, dtypes, row_count, sample (first 5 rows).
        The result is also cached in ``self._profiles[filename]``.
        """
        filepath = os.path.join(self.raw_data_dir, filename)
        xls = pd.ExcelFile(filepath)
        profile: dict = {"filename": filename, "sheets": {}}

        for sheet in xls.sheet_names:
            df = pd.read_excel(xls, sheet_name=sheet)
            profile["sheets"][sheet] = {
                "columns": list(df.columns),
                "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
                "row_count": len(df),
                "sample": df.head(5).to_dict(orient="records"),
            }

        self._profiles[filename] = profile
        return profile

    # ------------------------------------------------------------------
    # Column-level analysis
    # ------------------------------------------------------------------

    @staticmethod
    def analyze_column(df: pd.DataFrame, column_name: str) -> dict:
        """Return descriptive statistics for a single column."""
        series = df[column_name]
        missing = int(series.isna().sum())
        total = len(series)

        stats: dict = {
            "dtype": str(series.dtype),
            "unique_count": int(series.nunique()),
            "missing_count": missing,
            "missing_pct": round(missing / total * 100, 2) if total else 0.0,
            "top_values": series.value_counts().head(10).to_dict(),
            "sample_distinct": list(series.dropna().unique()[:10]),
        }

        if pd.api.types.is_numeric_dtype(series):
            stats["min"] = series.min()
            stats["max"] = series.max()

        return stats

    # ------------------------------------------------------------------
    # Duplicate detection
    # ------------------------------------------------------------------

    @staticmethod
    def detect_duplicates(df: pd.DataFrame, key_columns: list[str]) -> pd.DataFrame:
        """Return rows that are duplicated on *key_columns*."""
        mask = df.duplicated(subset=key_columns, keep=False)
        return df.loc[mask].sort_values(key_columns)

    # ------------------------------------------------------------------
    # Schema comparison
    # ------------------------------------------------------------------

    def compare_schemas(self, file_list: list[str], sheet: str | None = None) -> dict:
        """Compare column sets across files, using the first sheet by default.

        Returns a dict with a ``common`` set and per-file ``added``/``removed``
        columns relative to the intersection.
        """
        schemas: dict[str, list[str]] = {}
        for fname in file_list:
            profile = self._profiles.get(fname) or self.profile_file(fname)
            target_sheet = sheet or next(iter(profile["sheets"]))
            schemas[fname] = profile["sheets"][target_sheet]["columns"]

        all_column_sets = [set(cols) for cols in schemas.values()]
        common = set.intersection(*all_column_sets) if all_column_sets else set()

        comparison: dict = {"common": sorted(common), "per_file": {}}
        for fname, cols in schemas.items():
            col_set = set(cols)
            comparison["per_file"][fname] = {
                "added": sorted(col_set - common),
                "removed": sorted(common - col_set),
            }
        return comparison

    # ------------------------------------------------------------------
    # Referential integrity
    # ------------------------------------------------------------------

    @staticmethod
    def check_referential_integrity(
        left_df: pd.DataFrame,
        right_df: pd.DataFrame,
        left_key: str,
        right_key: str,
    ) -> dict:
        """Find orphan keys between two DataFrames.

        Returns counts and sample values for keys present in one side but not
        the other.
        """
        left_keys = set(left_df[left_key].dropna().unique())
        right_keys = set(right_df[right_key].dropna().unique())

        left_only = sorted(left_keys - right_keys, key=str)
        right_only = sorted(right_keys - left_keys, key=str)

        return {
            "left_only_count": len(left_only),
            "left_only_sample": left_only[:20],
            "right_only_count": len(right_only),
            "right_only_sample": right_only[:20],
        }

    # ------------------------------------------------------------------
    # Report
    # ------------------------------------------------------------------

    def generate_report(self) -> None:
        """Print a formatted summary of all cached profiling results."""
        if not self._profiles:
            print("No files profiled yet. Call profile_file() first.")
            return

        separator = "=" * 72
        for filename, profile in self._profiles.items():
            print(f"\n{separator}")
            print(f"  FILE: {filename}")
            print(separator)
            for sheet_name, info in profile["sheets"].items():
                print(f"\n  Sheet: '{sheet_name}'")
                print(f"    Rows   : {info['row_count']}")
                print(f"    Columns: {info['columns']}")
                print("    Dtypes :")
                for col, dtype in info["dtypes"].items():
                    print(f"      {col:30s} {dtype}")
                if info["sample"]:
                    print(f"    Sample (row 0): {info['sample'][0]}")
        print(f"\n{separator}")
        print(f"  Total files profiled: {len(self._profiles)}")
        print(separator)


# ------------------------------------------------------------------
# Standalone demo
# ------------------------------------------------------------------

if __name__ == "__main__":
    RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
    profiler = DataProfiler(RAW_DIR)

    # 1. Profile every raw file
    raw_files = sorted(
        f for f in os.listdir(RAW_DIR) if f.endswith(".xlsx")
    )
    for f in raw_files:
        print(f"Profiling {f} ...")
        profiler.profile_file(f)

    # 2. Summary report
    profiler.generate_report()

    # 3. Column analysis on Certifications
    cert_path = os.path.join(RAW_DIR, "Thomas More Data Certifications.xlsx")
    cert_df = pd.read_excel(cert_path)
    print("\n--- Column analysis: Certifications ---")
    for col in cert_df.columns:
        stats = DataProfiler.analyze_column(cert_df, col)
        print(f"\n  [{col}]  dtype={stats['dtype']}  "
              f"unique={stats['unique_count']}  "
              f"missing={stats['missing_count']} ({stats['missing_pct']}%)")

    # 4. Compare schemas across all Results files
    results_files = [f for f in raw_files if "Results" in f]
    if len(results_files) > 1:
        print("\n--- Schema comparison: Results files ---")
        schema_cmp = profiler.compare_schemas(results_files)
        print(f"  Common columns: {schema_cmp['common']}")
        for fname, diff in schema_cmp["per_file"].items():
            if diff["added"]:
                print(f"  {fname}  extra: {diff['added']}")

    # 5. Duplicate check on Certifications (key = Code)
    if "Code" in cert_df.columns:
        dups = DataProfiler.detect_duplicates(cert_df, ["Code"])
        print(f"\n--- Duplicates on 'Code' in Certifications: {len(dups)} rows ---")

    # 6. Referential integrity: Results ↔ Certifications
    sample_results_file = os.path.join(RAW_DIR, "Thomas More Results 2024.xlsx")
    if os.path.exists(sample_results_file):
        res_df = pd.read_excel(sample_results_file)
        if "Code" in res_df.columns and "Code" in cert_df.columns:
            integrity = DataProfiler.check_referential_integrity(
                res_df, cert_df, "Code", "Code"
            )
            print(f"\n--- Referential integrity: Results 2024 ↔ Certifications ---")
            print(f"  In Results but not Certifications: {integrity['left_only_count']}")
            print(f"  In Certifications but not Results: {integrity['right_only_count']}")

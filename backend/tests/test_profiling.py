import tempfile
from pathlib import Path
import pandas as pd
import pytest
from app.engine.profiling import inspect_dataset_metadata, generate_dataset_profile, load_dataset

def test_csv_profiling():
    with tempfile.NamedTemporaryFile(suffix=".csv", mode="w", delete=False, newline="") as f:
        f.write("id,region,revenue,date\n")
        f.write("1,North,150.5,2026-01-01\n")
        f.write("2,South,230.0,2026-01-02\n")
        f.write("3,North,310.2,2026-01-03\n")
        f.write("4,East,,2026-01-04\n")
        csv_path = f.name

    try:
        meta = inspect_dataset_metadata(csv_path)
        assert meta["format"] == "csv"

        profile = generate_dataset_profile(csv_path)
        assert profile["row_count"] == 4
        assert profile["column_count"] == 4

        cols = {c["name"]: c for c in profile["columns"]}
        assert "revenue" in cols
        assert cols["revenue"]["type_category"] == "numeric"
        assert cols["revenue"]["null_count"] == 1
        assert cols["revenue"]["null_percentage"] == 25.0

        # Check numerical summaries
        assert "revenue" in profile["numerical_summaries"]
        stats = profile["numerical_summaries"]["revenue"]
        assert stats["min"] == 150.5
        assert stats["max"] == 310.2

        # Check sample data (3 rows)
        assert len(profile["sample_data"]) == 3
    finally:
        Path(csv_path).unlink(missing_ok=True)


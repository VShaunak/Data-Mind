import tempfile
from pathlib import Path
import pytest
from app.engine.sandbox import sandbox_manager

def test_sandbox_executes_safe_script():
    with tempfile.NamedTemporaryFile(suffix=".csv", mode="w", delete=False, newline="") as f:
        f.write("category,value\n")
        f.write("A,10\n")
        f.write("B,25\n")
        f.write("C,15\n")
        csv_path = f.name

    code = """
import pandas as pd
import plotly.express as px

df = pd.read_csv(DATASET_PATH)
metrics = {
    "total_records": len(df),
    "total_value": float(df["value"].sum())
}

fig = px.bar(df, x="category", y="value", title="Test Chart")
save_plotly_figure(fig, "plotly_chart.json")
save_summary_metrics(metrics, "summary_metrics.json")
"""

    try:
        res = sandbox_manager.execute(
            code=code,
            dataset_path=csv_path,
            session_id="test_sess",
            task_id="test_task_1"
        )
        assert res.success is True
        assert res.exit_code == 0
        assert res.chart_json is not None
        assert "data" in res.chart_json
        assert res.metrics_json is not None
        assert res.metrics_json["total_records"] == 3
        assert res.metrics_json["total_value"] == 50.0
    finally:
        Path(csv_path).unlink(missing_ok=True)

def test_sandbox_catches_runtime_error_and_traceback():
    with tempfile.NamedTemporaryFile(suffix=".csv", mode="w", delete=False, newline="") as f:
        f.write("category,value\n")
        f.write("A,10\n")
        csv_path = f.name

    code = """
import pandas as pd
df = pd.read_csv(DATASET_PATH)
# Intentionally trigger KeyError
x = df["NonExistentColumn"]
"""

    try:
        res = sandbox_manager.execute(
            code=code,
            dataset_path=csv_path,
            session_id="test_sess",
            task_id="test_task_2"
        )
        assert res.success is False
        assert res.exit_code != 0
        assert res.traceback is not None
        assert "KeyError" in res.traceback
    finally:
        Path(csv_path).unlink(missing_ok=True)


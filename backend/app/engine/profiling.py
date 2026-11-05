import os
import json
import sqlite3
from pathlib import Path
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
from app.config import settings

def load_dataset(file_path: str, sheet_name: Optional[str] = None, nrows: Optional[int] = None) -> pd.DataFrame:
    """Load dataset from supported formats into a pandas DataFrame."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Dataset file not found: {file_path}")

    ext = path.suffix.lower()
    if ext == ".csv":
        return pd.read_csv(file_path, nrows=nrows)
    elif ext in (".xlsx", ".xls"):
        return pd.read_excel(file_path, sheet_name=sheet_name or 0, nrows=nrows)
    elif ext == ".json":
        return pd.read_json(file_path)
    elif ext == ".parquet":
        df = pd.read_parquet(file_path)
        if nrows:
            return df.head(nrows)
        return df
    elif ext in (".db", ".sqlite", ".sqlite3"):
        conn = sqlite3.connect(file_path)
        # Find first table
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [t[0] for t in cur.fetchall() if not t[0].startswith("sqlite_")]
        if not tables:
            conn.close()
            raise ValueError(f"No tables found in SQLite database: {file_path}")
        table_to_use = sheet_name if (sheet_name and sheet_name in tables) else tables[0]
        query = f"SELECT * FROM {table_to_use}"
        if nrows:
            query += f" LIMIT {nrows}"
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    else:
        raise ValueError(f"Unsupported dataset format: {ext}")

def inspect_dataset_metadata(file_path: str) -> Dict[str, Any]:
    """Inspect file size, format, and available sheets/tables."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    ext = path.suffix.lower()
    stat = path.stat()
    size_mb = stat.st_size / (1024 * 1024)

    sheets = []
    if ext in (".xlsx", ".xls"):
        try:
            xl = pd.ExcelFile(file_path)
            sheets = xl.sheet_names
        except Exception:
            pass
    elif ext in (".db", ".sqlite", ".sqlite3"):
        try:
            conn = sqlite3.connect(file_path)
            cur = conn.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
            sheets = [t[0] for t in cur.fetchall() if not t[0].startswith("sqlite_")]
            conn.close()
        except Exception:
            pass

    return {
        "file_name": path.name,
        "file_size_bytes": stat.st_size,
        "file_size_formatted": f"{size_mb:.2f} MB" if size_mb >= 1.0 else f"{stat.st_size / 1024:.1f} KB",
        "format": ext.lstrip("."),
        "sheets_or_tables": sheets,
    }

def generate_dataset_profile(file_path: str, sheet_name: Optional[str] = None) -> Dict[str, Any]:
    """Generate a deterministic dataset profile for analytical planning & code generation."""
    meta = inspect_dataset_metadata(file_path)
    df = load_dataset(file_path, sheet_name=sheet_name, nrows=settings.MAX_PROFILE_ROWS)

    row_count = int(len(df))
    col_count = int(len(df.columns))
    duplicate_count = int(df.duplicated().sum())

    memory_bytes = int(df.memory_usage(deep=True).sum())
    memory_str = f"{memory_bytes / (1024 * 1024):.2f} MB" if memory_bytes >= 1024 * 1024 else f"{memory_bytes / 1024:.1f} KB"

    columns_profile = []
    numerical_summaries = {}
    categorical_summaries = {}
    datetime_columns = []

    for col in df.columns:
        series = df[col]
        dtype_str = str(series.dtype)
        null_count = int(series.isnull().sum())
        null_pct = round((null_count / row_count * 100.0), 2) if row_count > 0 else 0.0

        col_info = {
            "name": str(col),
            "dtype": dtype_str,
            "null_count": null_count,
            "null_percentage": null_pct,
            "unique_count": int(series.nunique(dropna=True)),
        }

        # Check if numeric
        if pd.api.types.is_numeric_dtype(series):
            desc = series.describe()
            numerical_summaries[str(col)] = {
                "mean": None if np.isnan(desc.get("mean", np.nan)) else round(float(desc.get("mean")), 4),
                "std": None if np.isnan(desc.get("std", np.nan)) else round(float(desc.get("std")), 4),
                "min": None if np.isnan(desc.get("min", np.nan)) else float(desc.get("min")),
                "25%": None if np.isnan(desc.get("25%", np.nan)) else float(desc.get("25%")),
                "50%": None if np.isnan(desc.get("50%", np.nan)) else float(desc.get("50%")),
                "75%": None if np.isnan(desc.get("75%", np.nan)) else float(desc.get("75%")),
                "max": None if np.isnan(desc.get("max", np.nan)) else float(desc.get("max")),
            }
            col_info["type_category"] = "numeric"
            col_info["min"] = numerical_summaries[str(col)]["min"]
            col_info["max"] = numerical_summaries[str(col)]["max"]

        # Check if datetime
        elif pd.api.types.is_datetime64_any_dtype(series) or "date" in str(col).lower() or "time" in str(col).lower():
            try:
                dt_series = pd.to_datetime(series, errors="coerce")
                valid_dt = dt_series.dropna()
                if not valid_dt.empty:
                    datetime_columns.append(str(col))
                    col_info["type_category"] = "datetime"
                    col_info["min"] = str(valid_dt.min())
                    col_info["max"] = str(valid_dt.max())
                else:
                    col_info["type_category"] = "string"
            except Exception:
                col_info["type_category"] = "string"

        # Otherwise categorical / object / string
        else:
            # Check if column is numeric data disguised as string/object (e.g. Batsman_Scored, price, amount)
            cleaned_sample = series.dropna().astype(str).str.strip().str.replace(r'[\$,]', '', regex=True)
            num_trial = pd.to_numeric(cleaned_sample.head(200), errors='coerce')
            valid_ratio = float(num_trial.notnull().mean()) if len(num_trial) > 0 else 0.0

            if valid_ratio >= 0.70:
                col_info["type_category"] = "numeric"
                col_info["is_numeric_string"] = True
                valid_nums = num_trial.dropna()
                if not valid_nums.empty:
                    numerical_summaries[str(col)] = {
                        "mean": round(float(valid_nums.mean()), 4),
                        "min": float(valid_nums.min()),
                        "max": float(valid_nums.max()),
                    }
                    col_info["min"] = float(valid_nums.min())
                    col_info["max"] = float(valid_nums.max())
            else:
                col_info["type_category"] = "categorical"
                top_vals = series.value_counts(dropna=True).head(5).to_dict()
                categorical_summaries[str(col)] = {str(k): int(v) for k, v in top_vals.items()}

        columns_profile.append(col_info)

    # 3-row representative sample serialized to clean JSON
    sample_df = df.head(settings.PROFILE_SAMPLE_SIZE)
    # Convert timestamps and NaNs to serializable objects
    sample_rows = json.loads(sample_df.to_json(orient="records", date_format="iso"))

    return {
        "file_name": meta["file_name"],
        "file_path": file_path,
        "format": meta["format"],
        "sheet_name": sheet_name,
        "row_count": row_count,
        "column_count": col_count,
        "duplicate_rows": duplicate_count,
        "memory_usage": memory_str,
        "columns": columns_profile,
        "numerical_summaries": numerical_summaries,
        "categorical_summaries": categorical_summaries,
        "datetime_columns": datetime_columns,
        "sample_data": sample_rows,
    }


import json
import re
from typing import Dict, Any, Optional

def extract_json_block(text: str) -> Optional[Dict[str, Any]]:
    """Robustly extract and parse a JSON object from LLM response text."""
    if not text:
        return None
    # 1. Try markdown code block ```json ... ```
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except Exception:
            pass

    # 2. Try first outer balanced curly braces
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        candidate = text[start:end + 1]
        try:
            return json.loads(candidate)
        except Exception:
            pass

    return None

def extract_python_code(text: str) -> str:
    """Robustly extract clean executable Python code from LLM response."""
    if not text:
        return ""
    # Look for ```python ... ```
    match = re.search(r"```(?:python)?\s*(.*?)\s*```", text, re.DOTALL)
    if match:
        return match.group(1).strip()

    # If no fences, but looks like python code, return as-is
    lines = text.strip().split("\n")
    cleaned_lines = []
    for line in lines:
        if line.startswith("```"):
            continue
        cleaned_lines.append(line)
    return "\n".join(cleaned_lines).strip()

def build_planning_prompt(user_prompt: str, dataset_profile: Dict[str, Any]) -> str:
    columns_summary = [
        f"- {col['name']} ({col['dtype']}, {col.get('type_category', 'general')}, nulls: {col['null_percentage']}%)"
        for col in dataset_profile.get("columns", [])
    ]
    sample_preview = json.dumps(dataset_profile.get("sample_data", [])[:2], indent=2, default=str)

    return f"""You are Data Mind, an expert principal data analyst and machine learning architect.

Analyze the user's objective and dataset profile to formulate a structured, deterministic analytical plan.

USER REQUEST:
"{user_prompt}"

DATASET PROFILE:
- File: {dataset_profile.get('file_name')} ({dataset_profile.get('format')})
- Shape: {dataset_profile.get('row_count')} rows x {dataset_profile.get('column_count')} columns
- Duplicate rows: {dataset_profile.get('duplicate_rows', 0)}
- Columns:
{chr(10).join(columns_summary)}

Sample Rows:
{sample_preview}

INSTRUCTIONS:
Return a valid JSON object matching this schema:
{{
  "objective": "Concise summary of the analytical goal",
  "cleaning_steps": ["step 1 (e.g. handle nulls via median/mode, robust datetime parsing)"],
  "analytical_techniques": ["e.g. descriptive statistics, Pearson/Spearman correlation, linear regression, ANOVA"],
  "primary_chart_type": "bar | line | scatter | box | histogram | heatmap | violin | pie",
  "chart_specification": {{
    "title": "Clear chart title",
    "x_axis": "column_name",
    "y_axis": "column_name",
    "color_or_group": "optional column name or null"
  }},
  "metrics_to_compute": ["metric 1", "metric 2"]
}}

Respond ONLY with the JSON object. Do not include markdown preamble.
"""

def build_code_generation_prompt(
    user_prompt: str,
    dataset_profile: Dict[str, Any],
    plan: Dict[str, Any],
    previous_code: Optional[str] = None,
    error_traceback: Optional[str] = None,
    attempt: int = 1,
) -> str:
    columns_info = json.dumps(dataset_profile.get("columns", []), indent=2, default=str)
    numerical_info = json.dumps(dataset_profile.get("numerical_summaries", {}), indent=2, default=str)
    categorical_info = json.dumps(dataset_profile.get("categorical_summaries", {}), indent=2, default=str)

    error_section = ""
    if error_traceback:
        error_section = f"""
CRITICAL: PREVIOUS EXECUTION FAILED (Attempt #{attempt - 1})!
PREVIOUS CODE:
```python
{previous_code}
```

TRACEBACK / ERROR:
{error_traceback}

DEBUGGING REQUIREMENTS:
1. Examine the traceback and column names carefully.
2. If KeyError occurred, check the actual columns in DATASET PROFILE below.
3. If Type/ValueError occurred, apply pd.to_numeric(..., errors='coerce') or pd.to_datetime(..., errors='coerce').
4. Fix the exact failure reason and verify imports.
"""

    refinement_section = ""
    if previous_code and not error_traceback:
        refinement_section = f"""
EXISTING WORKING CODE IN CURRENT SESSION:
```python
{previous_code}
```

ITERATIVE REFINEMENT & STYLING INSTRUCTION:
The user is providing an iterative follow-up or styling instruction on the existing chart (e.g. adjust bar thickness, move legend, change color palette, add average line, switch orientation, display percentages, highlight top category, or switch theme).
Modify the existing visualization while preserving its core data pipeline:
- 'thicker bars' -> adjust `bargap=0.15` in `fig.update_layout()`
- 'legend to right' -> `legend=dict(orientation='v', x=1.02, y=1)`
- 'legend top / horizontal' -> `legend=dict(orientation='h', y=1.05, x=0.5, xanchor='center')`
- 'add average / reference line' -> `fig.add_hline(y=avg_val, line_dash='dash', line_color='#EA4335', annotation_text=f'Avg: {{avg_val:,.1f}}')`
- 'show percentages' -> compute proportion `val / total * 100` and display on bars `text=[f'{{p:.1f}}%']`
- 'make horizontal' -> swap x and y, use `orientation='h'`
- 'blue / color palette' -> update `marker=dict(color=...)` or `color_discrete_sequence`
- 'dark mode' -> `template='plotly_dark'`, `paper_bgcolor='#202124'`, `plot_bgcolor='#202124'`
- 'remove gridlines' -> `xaxis=dict(showgrid=False), yaxis=dict(showgrid=False)`
"""

    return f"""You are Data Mind, an expert Python data scientist and senior visualization engineer.

GOAL:
User Request: "{user_prompt}"

ANALYSIS PLAN:
{json.dumps(plan, indent=2, default=str)}

DATASET SCHEMA & SUMMARY:
- Total rows: {dataset_profile.get('row_count')}, Total columns: {dataset_profile.get('column_count')}
- Columns:
{columns_info}
- Numerical statistics:
{numerical_info}
- Categorical top values:
{categorical_info}

{refinement_section}
{error_section}

ENVIRONMENT & CONTRACT RULES:
1. Read the dataset from the global constant `DATASET_PATH`:
   - If CSV: `df = pd.read_csv(DATASET_PATH)`
   - If Excel: `df = pd.read_excel(DATASET_PATH)`
   - If Parquet: `df = pd.read_parquet(DATASET_PATH)`
   - If JSON: `df = pd.read_json(DATASET_PATH)`
   - If SQLite: `import sqlite3; conn = sqlite3.connect(DATASET_PATH); df = pd.read_sql_query('SELECT * FROM ...', conn)`
2. Defensive data cleaning & preparation:
   - Handle missing values gracefully (median/mode imputation or dropna only where justified).
   - Use `pd.to_numeric(df[col].astype(str).str.strip().str.replace(r'[\$,]', '', regex=True), errors='coerce')` for numeric columns stored as text.
   - Use `pd.to_datetime(df[col], errors='coerce')` for dates.
3. Visualization & Formatting Requirements:
   - Create a polished, publication-quality Plotly figure (`fig = px.bar(...)` or `go.Figure(...)`).
   - If user requests Matplotlib/Seaborn or 300 DPI PNG/SVG, generate the Plotly figure AND save the image via Matplotlib (`plt.savefig(str(Path(OUTPUT_DIR) / 'publication_chart.png'), dpi=300)`).
   - Use a clean minimal layout (`template='plotly_white'`, readable sans-serif typography, subtle gridlines).
   - Title & Subtitle: Include a clear bold title and informative subtitle describing the key insight.
   - Value Labels: Display formatted numerical values directly on/outside bars (`text_auto=True` or `textposition='outside'`).
   - Numbers & Axes: Apply thousands separators to large numerical values (`tickformat=',.0f'`).
   - Category Sorting: Sort bars logically (descending order by metric value).
   - Accent Highlighting: When highlighting the top or primary category, apply an accent color (e.g. '#1A73E8') for the leading bar and restrained neutral (e.g. '#5F6368') for other bars.
   - Legends: When grouping by categories or series, format legends cleanly (`legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)`).
   - Reference Lines: Add average/median lines when comparative baselines are requested (`fig.add_hline(y=..., line_dash='dash')`).
   - Multi-chart / Dashboard / KPIs: If requested, support subplots with `plotly.subplots.make_subplots` or KPI indicator cards with `go.Indicator`.
   - MANDATORY: Call `save_plotly_figure(fig, 'plotly_chart.json')`.
4. Statistical Metrics:
   - Compute real statistical calculations (means, medians, correlations, totals, proportions, p-values, regression slopes).
   - MANDATORY: Call `save_summary_metrics(metrics_dict, 'summary_metrics.json')`.
5. Permitted imports: `pandas`, `numpy`, `scipy`, `statsmodels`, `sklearn`, `plotly`, `matplotlib`, `seaborn`, `PIL`, `pathlib`, `math`, `json`, `datetime`.
   DO NOT import `os`, `sys`, `subprocess`, `socket`, `shutil`.

OUTPUT FORMAT:
Respond with the executable Python script enclosed in a single ```python ``` code block.
"""

def build_report_prompt(
    user_prompt: str,
    dataset_profile: Dict[str, Any],
    plan: Dict[str, Any],
    metrics: Dict[str, Any],
    stdout: str,
) -> str:
    return f"""You are Data Mind, a senior research scientist and mathematical data analyst.

Write a rigorous, evidence-based analytical report based on the ACTUAL computed results.
Do NOT fabricate numbers. Every statistic must originate from the metrics or stdout below.

USER OBJECTIVE:
"{user_prompt}"

DATASET:
{dataset_profile.get('file_name')} ({dataset_profile.get('row_count')} rows, {dataset_profile.get('column_count')} columns)

COMPUTED SUMMARY METRICS:
{json.dumps(metrics, indent=2, default=str)}

CODE STDOUT OUTPUT:
{stdout[:2000]}

REPORT STRUCTURE REQUIREMENTS:
Produce a comprehensive report in GitHub-flavored Markdown with:
# 1. Executive Summary
# 2. Dataset Overview & Data Quality
# 3. Preprocessing & Cleaning Performed
# 4. Statistical Findings & Mathematical Results (include tables with computed values)
# 5. Variable Relationships, Trends & Patterns
# 6. Outlier & Anomaly Observations
# 7. Limitations & Assumptions
# 8. Actionable Evidence-Based Recommendations

Do not confuse correlation with causation. Maintain a professional, objective tone.
"""


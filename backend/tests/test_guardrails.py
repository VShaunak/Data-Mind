import pytest
from app.engine.guardrails import validate_python_code

def test_safe_data_science_code_passes():
    safe_code = """
import pandas as pd
import numpy as np
import plotly.express as px
from scipy import stats

df = pd.DataFrame({"a": [1, 2, 3], "b": [10, 20, 30]})
mean_val = float(df["a"].mean())
fig = px.bar(df, x="a", y="b", title="Safe Test")
"""
    is_valid, errors, warnings, imports = validate_python_code(safe_code)
    assert is_valid is True
    assert len(errors) == 0
    assert "pandas" in imports
    assert "numpy" in imports

def test_forbidden_os_system_blocked():
    malicious_code = """
import os
os.system("whoami")
"""
    is_valid, errors, warnings, imports = validate_python_code(malicious_code)
    assert is_valid is False
    assert any("Disallowed import: 'os'" in err for err in errors) or any("system" in err for err in errors)

def test_forbidden_subprocess_blocked():
    malicious_code = """
import subprocess
subprocess.run(["cmd.exe", "/c", "dir"])
"""
    is_valid, errors, warnings, imports = validate_python_code(malicious_code)
    assert is_valid is False
    assert any("subprocess" in err for err in errors)

def test_forbidden_eval_exec_blocked():
    code_eval = "eval('1 + 1')"
    is_valid, errors, _, _ = validate_python_code(code_eval)
    assert is_valid is False
    assert any("eval" in err for err in errors)

    code_exec = "exec('x = 2')"
    is_valid, errors, _, _ = validate_python_code(code_exec)
    assert is_valid is False
    assert any("exec" in err for err in errors)

def test_forbidden_dunder_introspection_blocked():
    code = "().__class__.__bases__[0].__subclasses__()"
    is_valid, errors, _, _ = validate_python_code(code)
    assert is_valid is False
    assert any("__subclasses__" in err or "__bases__" in err for err in errors)


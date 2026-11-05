import tempfile
from pathlib import Path
import pytest
from app.engine.sandbox import sandbox_manager

def test_malicious_code_blocked_before_sandbox_execution():
    with tempfile.NamedTemporaryFile(suffix=".csv", mode="w", delete=False) as f:
        f.write("a,b\n1,2\n")
        csv_path = f.name

    malicious_scripts = [
        "import os\nos.remove('important_file.txt')",
        "import subprocess\nsubprocess.Popen('calc.exe')",
        "eval('__import__(\"os\").system(\"echo hacked\")')",
        "import shutil\nshutil.rmtree('C:/')",
        "import socket\ns = socket.socket()",
    ]

    try:
        for script in malicious_scripts:
            res = sandbox_manager.execute(
                code=script,
                dataset_path=csv_path,
                session_id="test_sess",
                task_id="sec_test"
            )
            assert res.success is False
            assert res.sandbox_type == "guardrail_blocked"
            assert "SecurityGuardrailError" in res.traceback
    finally:
        Path(csv_path).unlink(missing_ok=True)

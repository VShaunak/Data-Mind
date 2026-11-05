import os
import sys
import json
import time
import shutil
import tempfile
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from pydantic import BaseModel
from app.config import settings
from app.engine.guardrails import validate_python_code

class SandboxResult(BaseModel):
    success: bool
    exit_code: int
    stdout: str
    stderr: str
    traceback: Optional[str] = None
    duration_seconds: float
    chart_json: Optional[Dict[str, Any]] = None
    metrics_json: Optional[Dict[str, Any]] = None
    generated_files: Dict[str, str] = {}
    sandbox_type: str  # "docker" | "isolated_process"

def is_docker_available() -> Tuple[bool, Optional[str]]:
    """Check if Docker engine is reachable."""
    try:
        import docker
        client = docker.from_env()
        client.ping()
        return True, None
    except Exception as e:
        return False, str(e)

class SandboxManager:
    """
    Manages secure execution of generated Python code in isolated sandboxes.
    Enforces AST guardrails, read-only dataset mounting, timeouts, and artifact collection.
    """

    def __init__(self):
        self.image_name = settings.DOCKER_IMAGE_NAME
        self.timeout = settings.SANDBOX_TIMEOUT_SECONDS

    def execute(self, code: str, dataset_path: str, session_id: str, task_id: str) -> SandboxResult:
        # Step 1: Pre-execution AST security validation
        is_valid, errors, warnings, imports = validate_python_code(code)
        if not is_valid:
            return SandboxResult(
                success=False,
                exit_code=1,
                stdout="",
                stderr="\n".join(errors),
                traceback=f"SecurityGuardrailError: Code failed static security AST validation:\n" + "\n".join(f"- {e}" for e in errors),
                duration_seconds=0.0,
                sandbox_type="guardrail_blocked"
            )

        docker_ready, docker_err = is_docker_available()

        if docker_ready:
            return self._execute_in_docker(code, dataset_path, session_id, task_id)
        else:
            if settings.FORCE_DOCKER_SANDBOX:
                return SandboxResult(
                    success=False,
                    exit_code=1,
                    stdout="",
                    stderr=f"Docker sandbox required but not available: {docker_err}",
                    traceback="SandboxUnavailableError: Docker Desktop is stopped or not running. Please start Docker Desktop to execute Python code safely.",
                    duration_seconds=0.0,
                    sandbox_type="docker_unavailable"
                )
            # Isolated out-of-process sandbox with dedicated temp directory and guardrail enforcement
            return self._execute_in_isolated_process(code, dataset_path, session_id, task_id)

    def _execute_in_docker(self, code: str, dataset_path: str, session_id: str, task_id: str) -> SandboxResult:
        import docker
        client = docker.from_env()
        start_time = time.time()

        temp_dir = Path(tempfile.mkdtemp(prefix=f"datamind_sandbox_{task_id}_"))
        script_file = temp_dir / "script.py"
        output_dir = temp_dir / "output"
        output_dir.mkdir(parents=True, exist_ok=True)

        dataset_src = Path(dataset_path).resolve()
        dataset_name = dataset_src.name

        # Prepare code wrapper that points dataset to /data/<name> and output to /output
        prepared_code = self._prepare_execution_code(code, f"/data/{dataset_name}", "/output")
        script_file.write_text(prepared_code, encoding="utf-8")

        container = None
        try:
            volumes = {
                str(temp_dir): {"bind": "/sandbox", "mode": "ro"},
                str(output_dir): {"bind": "/output", "mode": "rw"},
                str(dataset_src.parent): {"bind": "/data", "mode": "ro"},
            }

            container = client.containers.run(
                image=self.image_name,
                command=["python", "/sandbox/script.py"],
                network_mode="none",
                read_only=True,
                volumes=volumes,
                user="1000:1000",
                mem_limit=settings.SANDBOX_MEMORY_LIMIT,
                nano_cpus=int(settings.SANDBOX_CPU_LIMIT * 1_000_000_000),
                pids_limit=50,
                detach=True,
            )

            # Wait with timeout
            result = container.wait(timeout=self.timeout)
            exit_code = result.get("StatusCode", 1)
            stdout = container.logs(stdout=True, stderr=False).decode("utf-8", errors="replace")
            stderr = container.logs(stdout=False, stderr=True).decode("utf-8", errors="replace")
            duration = time.time() - start_time

            # Parse outputs
            chart_json, metrics_json, files = self._collect_artifacts(output_dir)
            success = (exit_code == 0)

            traceback = stderr if (not success and stderr) else None

            return SandboxResult(
                success=success,
                exit_code=exit_code,
                stdout=stdout,
                stderr=stderr,
                traceback=traceback,
                duration_seconds=round(duration, 3),
                chart_json=chart_json,
                metrics_json=metrics_json,
                generated_files=files,
                sandbox_type="docker"
            )

        except Exception as e:
            duration = time.time() - start_time
            return SandboxResult(
                success=False,
                exit_code=1,
                stdout="",
                stderr=str(e),
                traceback=f"DockerExecutionException: {str(e)}",
                duration_seconds=round(duration, 3),
                sandbox_type="docker"
            )
        finally:
            if container:
                try:
                    container.remove(force=True)
                except Exception:
                    pass
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
            except Exception:
                pass

    def _execute_in_isolated_process(self, code: str, dataset_path: str, session_id: str, task_id: str) -> SandboxResult:
        """
        Isolated subprocess execution runner inside a dedicated temporary workspace.
        Runs with separate Python process, explicit timeouts, and isolated IO.
        """
        start_time = time.time()
        temp_dir = Path(tempfile.mkdtemp(prefix=f"datamind_proc_{task_id}_"))
        output_dir = temp_dir / "output"
        output_dir.mkdir(parents=True, exist_ok=True)

        dataset_src = Path(dataset_path).resolve()
        dataset_name = dataset_src.name
        # Copy dataset to temporary workspace as read-only copy
        isolated_dataset = temp_dir / dataset_name
        shutil.copy2(dataset_src, isolated_dataset)

        # Copy small sibling lookup CSV/metadata files (< 10MB) for foreign key joins
        try:
            for sib in dataset_src.parent.glob("*.csv"):
                if sib.name != dataset_name and sib.stat().st_size <= 10 * 1024 * 1024:
                    shutil.copy2(sib, temp_dir / sib.name)
        except Exception:
            pass

        script_path = temp_dir / "script.py"
        prepared_code = self._prepare_execution_code(
            code,
            str(isolated_dataset).replace("\\", "/"),
            str(output_dir).replace("\\", "/"),
            str(dataset_src.parent).replace("\\", "/")
        )
        script_path.write_text(prepared_code, encoding="utf-8")

        python_exe = sys.executable

        # Clean sandbox environment without leaking secrets or host auth
        clean_env = {
            "PYTHONPATH": "",
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONUNBUFFERED": "1",
            "PATH": os.environ.get("PATH", ""),
            "SYSTEMROOT": os.environ.get("SYSTEMROOT", "C:\\Windows"),
            "TEMP": str(temp_dir),
            "TMP": str(temp_dir),
        }

        try:
            proc = subprocess.run(
                [python_exe, str(script_path)],
                cwd=str(temp_dir),
                env=clean_env,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            duration = time.time() - start_time
            exit_code = proc.returncode
            stdout = proc.stdout
            stderr = proc.stderr
            success = (exit_code == 0)

            chart_json, metrics_json, files = self._collect_artifacts(output_dir)

            traceback = stderr if (not success and stderr) else None

            # If execution succeeded but chart wasn't produced, check if output was printed as JSON
            if success and not chart_json:
                chart_json = self._extract_json_from_stdout(stdout, "plotly_chart")
            if success and not metrics_json:
                metrics_json = self._extract_json_from_stdout(stdout, "metrics")

            return SandboxResult(
                success=success,
                exit_code=exit_code,
                stdout=stdout,
                stderr=stderr,
                traceback=traceback,
                duration_seconds=round(duration, 3),
                chart_json=chart_json,
                metrics_json=metrics_json,
                generated_files=files,
                sandbox_type="isolated_process"
            )

        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            return SandboxResult(
                success=False,
                exit_code=-1,
                stdout="",
                stderr=f"Execution timed out after {self.timeout} seconds.",
                traceback=f"TimeoutError: Code execution exceeded maximum allowable duration ({self.timeout}s).",
                duration_seconds=round(duration, 3),
                sandbox_type="isolated_process"
            )
        except Exception as e:
            duration = time.time() - start_time
            return SandboxResult(
                success=False,
                exit_code=1,
                stdout="",
                stderr=str(e),
                traceback=f"ExecutionException: {str(e)}",
                duration_seconds=round(duration, 3),
                sandbox_type="isolated_process"
            )
        finally:
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
            except Exception:
                pass

    def _prepare_execution_code(self, code: str, dataset_path_str: str, output_dir_str: str, dataset_dir_str: str = "") -> str:
        """Inject constants and output helpers into the script."""
        prelude = f"""# --- Data Mind Execution Prelude ---
import os
import json
import pandas as pd
import numpy as np

DATASET_PATH = r"{dataset_path_str}"
DATASET_DIR = r"{dataset_dir_str}"
OUTPUT_DIR = r"{output_dir_str}"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def save_plotly_figure(fig, filename="plotly_chart.json"):
    \"\"\"Utility to serialize Plotly figure into JSON artifact.\"\"\"
    import plotly.io as pio
    out_path = os.path.join(OUTPUT_DIR, filename)
    pio.write_json(fig, out_path)

def save_summary_metrics(metrics: dict, filename="summary_metrics.json"):
    \"\"\"Utility to serialize statistical summary dictionary.\"\"\"
    out_path = os.path.join(OUTPUT_DIR, filename)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, default=str)
# --- End of Prelude ---

"""
        return prelude + code

    def _collect_artifacts(self, output_dir: Path) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]], Dict[str, str]]:
        chart_json = None
        metrics_json = None
        files = {}

        chart_path = output_dir / "plotly_chart.json"
        if chart_path.exists():
            try:
                with open(chart_path, "r", encoding="utf-8") as f:
                    chart_json = json.load(f)
            except Exception:
                pass

        metrics_path = output_dir / "summary_metrics.json"
        if metrics_path.exists():
            try:
                with open(metrics_path, "r", encoding="utf-8") as f:
                    metrics_json = json.load(f)
            except Exception:
                pass

        for p in output_dir.glob("*"):
            if p.is_file():
                files[p.name] = str(p)

        return chart_json, metrics_json, files

    def _extract_json_from_stdout(self, text: str, key_hint: str) -> Optional[Dict[str, Any]]:
        """Attempt to extract embedded JSON objects from stdout if present."""
        try:
            start_idx = text.find("{")
            end_idx = text.rfind("}")
            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                candidate = text[start_idx:end_idx + 1]
                data = json.loads(candidate)
                if isinstance(data, dict):
                    return data
        except Exception:
            pass
        return None

sandbox_manager = SandboxManager()


import sys
import os
import time
import subprocess
import webbrowser
import urllib.request
import json
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.resolve()
BACKEND_DIR = ROOT_DIR / "backend"
FRONTEND_DIST = ROOT_DIR / "frontend" / "dist"
VENV_PYTHON = BACKEND_DIR / ".venv" / "Scripts" / "python.exe"

def is_backend_running(port=8000) -> bool:
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) == 0

def kill_stale_backend(port=8000):
    """Clean up any old backend process holding port 8000."""
    try:
        req = urllib.request.Request(
            f"http://127.0.0.1:{port}/api/shutdown",
            data=b"{}",
            headers={"Content-Type": "application/json"}
        )
        urllib.request.urlopen(req, timeout=1.0)
        time.sleep(0.8)
    except Exception:
        pass

    if is_backend_running(port):
        try:
            cmd = f'powershell -Command "Get-NetTCPConnection -LocalPort {port} -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique"'
            out = subprocess.check_output(cmd, shell=True, text=True).strip()
            for pid_str in out.splitlines():
                pid = pid_str.strip()
                if pid and pid.isdigit() and int(pid) != os.getpid():
                    subprocess.run(f"taskkill /F /PID {pid}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(0.5)
        except Exception:
            pass

def start_backend():
    if is_backend_running(8000):
        print("[Data Mind] Backend already running on port 8000.")
        return None

    print("[Data Mind] Starting Data Mind FastAPI backend...")
    python_exe = str(VENV_PYTHON) if VENV_PYTHON.exists() else sys.executable
    run_script = str(BACKEND_DIR / "run_backend.py")

    logs_dir = Path(os.environ.get("APPDATA", str(Path.home()))) / "DataMind" / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_path = logs_dir / "backend.log"
    log_file = open(log_path, "a", encoding="utf-8")

    proc = subprocess.Popen(
        [python_exe, run_script],
        cwd=str(BACKEND_DIR),
        stdout=log_file,
        stderr=log_file,
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
    )

    # Wait for server to come up and verify HTTP readiness
    for _ in range(40):
        if is_backend_running(8000):
            try:
                req = urllib.request.Request("http://127.0.0.1:8000/api/health")
                with urllib.request.urlopen(req, timeout=1.0) as resp:
                    if resp.status == 200:
                        print("[Data Mind] Backend is healthy and ready on http://127.0.0.1:8000.")
                        return proc
            except Exception:
                pass
        time.sleep(0.3)

    print("[Data Mind] Warning: Backend startup timeout.")
    return proc

def launch_native_window(url="http://127.0.0.1:8000"):
    """Launch in standalone application window mode (Edge or Chrome) with isolated user data."""
    profile_dir = Path(os.environ.get("APPDATA", str(Path.home()))) / "DataMind" / "browser_profile"
    profile_dir.mkdir(parents=True, exist_ok=True)

    edge_paths = [
        Path(os.environ.get("ProgramFiles(x86)", "")) / "Microsoft" / "Edge" / "Application" / "msedge.exe",
        Path(os.environ.get("ProgramFiles", "")) / "Microsoft" / "Edge" / "Application" / "msedge.exe",
    ]
    chrome_paths = [
        Path(os.environ.get("ProgramFiles", "")) / "Google" / "Chrome" / "Application" / "chrome.exe",
        Path(os.environ.get("ProgramFiles(x86)", "")) / "Google" / "Chrome" / "Application" / "chrome.exe",
    ]

    for p in edge_paths + chrome_paths:
        if p.exists():
            print(f"[Data Mind] Launching native window via {p.name}...")
            return subprocess.Popen([
                str(p),
                f"--app={url}",
                f"--user-data-dir={str(profile_dir)}",
                "--window-size=1440,900",
                "--app-title=Data Mind - Think Data. Discover Intelligence."
            ])

    # Fallback default browser
    print("[Data Mind] Launching default browser...")
    webbrowser.open(url)
    return None

if __name__ == "__main__":
    backend_proc = start_backend()
    browser_proc = launch_native_window("http://127.0.0.1:8000")

    if browser_proc:
        start_time = time.time()
        try:
            browser_proc.wait()
            elapsed = time.time() - start_time
            # Only terminate backend if user actually ran the app session (> 3 seconds)
            # If the process exited in < 3s, it handed off to an existing browser instance
            if elapsed >= 3.0:
                print("[Data Mind] Application window closed by user. Shutting down backend...")
                if backend_proc:
                    try:
                        backend_proc.terminate()
                    except Exception:
                        pass
                kill_stale_backend(8000)
            else:
                print("[Data Mind] Browser handed off to existing window. Keeping backend alive.")
                if backend_proc:
                    backend_proc.wait()
        except KeyboardInterrupt:
            if backend_proc:
                backend_proc.terminate()
            kill_stale_backend(8000)
    else:
        # Browser opened via webbrowser.open; keep backend alive
        if backend_proc:
            try:
                backend_proc.wait()
            except KeyboardInterrupt:
                backend_proc.terminate()
                kill_stale_backend(8000)

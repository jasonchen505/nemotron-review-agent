"""Run a test command with a timeout and return truncated output."""
import shutil
import subprocess
from pathlib import Path

DEFAULT_TIMEOUT = 180
MAX_OUTPUT = 12000


def detect_test_command(cwd):
    """Best-effort auto-detection of the project's test command."""
    cwd = Path(cwd)
    if shutil.which("pytest") and ((cwd / "tests").is_dir() or (cwd / "test").is_dir()):
        return "pytest -x -q"
    if (cwd / "package.json").exists() and shutil.which("npm"):
        return "npm test -- --watchAll=false"
    if (cwd / "go.mod").exists() and shutil.which("go"):
        return "go test ./..."
    return None


def run_tests(command, cwd=".", timeout=DEFAULT_TIMEOUT):
    """Run `command` in `cwd`; return a formatted output block (or None)."""
    if not command:
        return None
    try:
        proc = subprocess.run(
            command, shell=True, cwd=cwd,
            capture_output=True, text=True, timeout=timeout,
        )
    except subprocess.TimeoutExpired as e:
        out = (e.stdout or "") + (e.stderr or "")
        return f"$ {command}\n[TIMED OUT after {timeout}s]\n{out[-MAX_OUTPUT:]}"
    except OSError as e:
        return f"$ {command}\n[FAILED TO START: {e}]"
    out = (proc.stdout or "") + (proc.stderr or "")
    return f"$ {command}\n[exit code {proc.returncode}]\n{out[-MAX_OUTPUT:]}"

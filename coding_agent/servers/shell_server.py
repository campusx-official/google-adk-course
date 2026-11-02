"""
safe-shell: a small MCP server that lets an agent run allowlisted commands.

Run directly (for testing):
    python coding_agent/servers/shell_server.py --root /absolute/path/to/workspace

ADK starts it automatically over stdio (see coding_agent/agent.py).

Works with both MCP Python SDK versions: 2.x (MCPServer) and 1.x (FastMCP,
the old name for the same class).
"""

import argparse
import shlex
import subprocess
import sys
from pathlib import Path

try:
    from mcp.server.mcpserver import MCPServer  # MCP SDK 2.x
except ImportError:
    from mcp.server.fastmcp import FastMCP as MCPServer  # MCP SDK 1.x

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

MAX_OUTPUT_CHARS = 4000          # keep tool output small for the model
DEFAULT_TIMEOUT_SECONDS = 60     # no command may run longer than this

# Programs the agent may run. Everything else is rejected.
# File reading/listing is deliberately NOT here (no cat, ls): the filesystem
# MCP server owns file access, so the model isn't torn between two tools.
ALLOWED_PROGRAMS = {"python", "pytest", "pip", "git"}

# Sub-commands that are blocked even though the program is allowed.
BLOCKED = {
    "git": {"push", "remote", "config", "reset", "clean", "rebase"},
    "pip": {"uninstall", "download"},
}

# ---------------------------------------------------------------------------

parser = argparse.ArgumentParser()
parser.add_argument("--root", required=True, help="Workspace folder commands run in")
ROOT = Path(parser.parse_args().root).resolve()
ROOT.mkdir(parents=True, exist_ok=True)

mcp = MCPServer(
    "safe-shell",
    instructions=(
        "Runs allowlisted commands (python, pytest, pip, git) inside the "
        "project workspace. Use it to run code and tests, not to read files."
    ),
)


def _truncate(text: str) -> str:
    if len(text) <= MAX_OUTPUT_CHARS:
        return text
    return f"...[truncated {len(text) - MAX_OUTPUT_CHARS} chars]...\n" + text[-MAX_OUTPUT_CHARS:]


def _check_allowed(parts: list[str]) -> str | None:
    """Return an error message if the command is not allowed, else None."""
    if not parts:
        return "Empty command."
    program = parts[0]
    if program not in ALLOWED_PROGRAMS:
        return f"'{program}' is not allowed. Allowed programs: {sorted(ALLOWED_PROGRAMS)}"
    if len(parts) > 1 and parts[1] in BLOCKED.get(program, set()):
        return f"'{program} {parts[1]}' is blocked for safety."
    if any(token in {"|", "&&", ";", ">", "<", "||"} for token in parts):
        return "Pipes, redirects and command chaining are not supported. Run one command at a time."
    return None


@mcp.tool()
def run_command(command: str, timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS) -> str:
    """Run one allowlisted command in the project workspace and return its output.

    Allowed programs: python, pytest, pip, git (git push/remote/config/reset/clean
    are blocked). Examples: "pytest -q", "python main.py", "git status",
    "git add .", "git commit -m 'Add todo API'".

    Args:
        command: The command line to run, e.g. "pytest -q".
        timeout_seconds: Maximum run time (capped at 60 seconds).
    """
    try:
        parts = shlex.split(command)
    except ValueError as e:
        return f"Could not parse command: {e}"

    error = _check_allowed(parts)
    if error:
        return f"REJECTED: {error}"

    # Run python/pytest/pip with the same interpreter as this server, so the
    # agent always uses the project's virtual environment.
    if parts[0] == "python":
        parts = [sys.executable, *parts[1:]]
    elif parts[0] in {"pytest", "pip"}:
        parts = [sys.executable, "-m", parts[0], *parts[1:]]

    timeout = max(1, min(timeout_seconds, DEFAULT_TIMEOUT_SECONDS))
    try:
        result = subprocess.run(
            parts,
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=timeout,
            shell=False,  # never pass commands through a shell
        )
    except subprocess.TimeoutExpired:
        return (
            f"TIMEOUT: command did not finish within {timeout}s. "
            "To run a web server, use the start_server tool instead."
        )
    except FileNotFoundError:
        return f"'{parts[0]}' is not installed on this machine."

    output = (result.stdout or "") + (result.stderr or "")
    return f"exit code: {result.returncode}\n{_truncate(output) or '(no output)'}"


@mcp.tool()
def workspace_info() -> str:
    """Return the workspace path commands run in, and the allowed programs."""
    return f"workspace: {ROOT}\nallowed programs: {sorted(ALLOWED_PROGRAMS)}"


# ---------------------------------------------------------------------------
# Long-running app server
# run_command waits for a command to finish, which a web server never does.
# These tools start uvicorn in the background and let the agent check on it.
# ---------------------------------------------------------------------------

import atexit
import os
import re
import time
import urllib.error
import urllib.request

SERVER_PORT = 8001  # 8000 is taken by adk web
import tempfile

# Kept outside the workspace so it never ends up in git commits.
LOG_FILE = Path(tempfile.gettempdir()) / "safe-shell-server.log"
_server: subprocess.Popen | None = None


def _read_log() -> str:
    try:
        return _truncate(LOG_FILE.read_text(errors="replace")) or "(no output yet)"
    except FileNotFoundError:
        return "(no log yet)"


@mcp.tool()
def start_server(module: str) -> str:
    """Start the FastAPI app with uvicorn in the background on http://127.0.0.1:8001.

    Use this to run the web app; run_command can't, because servers never exit.
    Stop it with stop_server. Use check_url to call it once it's running.

    Args:
        module: The ASGI app to serve, as "module:variable", e.g. "app:app".
    """
    global _server
    if not re.fullmatch(r"[A-Za-z_][\w.]*:[A-Za-z_]\w*", module):
        return "REJECTED: module must look like 'app:app'."
    if _server and _server.poll() is None:
        return f"Already running (pid {_server.pid}). Use stop_server first to restart."

    log = open(LOG_FILE, "w")
    _server = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", module, "--host", "127.0.0.1", "--port", str(SERVER_PORT)],
        cwd=ROOT,
        stdout=log,
        stderr=subprocess.STDOUT,
        env={**os.environ, "PYTHONUNBUFFERED": "1"},  # log lines appear immediately
    )
    time.sleep(2)  # give it a moment to start or crash
    if _server.poll() is not None:
        return f"Server exited immediately (code {_server.returncode}). Log:\n{_read_log()}"
    return f"Server running at http://127.0.0.1:{SERVER_PORT} (pid {_server.pid}).\n{_read_log()}"


@mcp.tool()
def stop_server() -> str:
    """Stop the background app server started with start_server."""
    global _server
    if not _server or _server.poll() is not None:
        return "No server is running."
    _server.terminate()
    try:
        _server.wait(timeout=5)
    except subprocess.TimeoutExpired:
        _server.kill()
    _server = None
    return "Server stopped."


@mcp.tool()
def server_logs() -> str:
    """Return the latest output of the background app server (errors, requests)."""
    status = "running" if _server and _server.poll() is None else "not running"
    return f"server is {status}\n{_read_log()}"


@mcp.tool()
def check_url(path: str = "/") -> str:
    """Send a GET request to the running app and return the status and body.

    Only the local app server can be reached, e.g. path="/todos/".
    """
    if not path.startswith("/"):
        return "REJECTED: path must start with '/', e.g. '/todos/'."
    url = f"http://127.0.0.1:{SERVER_PORT}{path}"
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            body = resp.read().decode(errors="replace")
            return f"HTTP {resp.status}\n{_truncate(body)}"
    except urllib.error.HTTPError as e:
        return f"HTTP {e.code}\n{_truncate(e.read().decode(errors='replace'))}"
    except Exception as e:
        return f"Could not reach {url}: {e}. Is the server running? Try server_logs."


@atexit.register
def _cleanup() -> None:
    """Don't leave a server running when the agent shuts down."""
    if _server and _server.poll() is None:
        _server.terminate()


if __name__ == "__main__":
    mcp.run()  # stdio transport by default
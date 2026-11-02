import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import (
    StdioConnectionParams,
    StreamableHTTPConnectionParams,
)
from mcp import StdioServerParameters


# 1. Load settings

AGENT_DIR = Path(__file__).resolve().parent
load_dotenv(AGENT_DIR / ".env")

WORKSPACE = Path(
    os.getenv("WORKSPACE_DIR", AGENT_DIR / "workspace")
).resolve()
WORKSPACE.mkdir(parents=True, exist_ok=True)

GITHUB_PAT = os.getenv("GITHUB_PAT")

NPX = "npx.cmd" if os.name == "nt" else "npx"
SHELL_SERVER = AGENT_DIR / "servers" / "shell_server.py"


# 2. Decide when shell tools need approval

AUTO_APPROVED_PREFIXES = (
    "pytest",
    "python -m pytest",
    "git status",
    "git diff",
    "git log",
)


def shell_needs_confirmation(command=None, module=None):
    """Return True to ask for approval; False to run immediately."""

    # Starting a server always needs approval.
    if module is not None:
        return True

    # Tools without a command do not need approval.
    if command is None:
        return False

    # Commands matching these prefixes run without approval.
    if command.strip().startswith(AUTO_APPROVED_PREFIXES):
        return False

    # All other commands need approval.
    return True


# 3. Connect to the local filesystem MCP server

filesystem_tools = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command=NPX,
            args=[
                "-y",
                "@modelcontextprotocol/server-filesystem",
                str(WORKSPACE),
            ],
        ),
        timeout=60,
    ),
    tool_filter=[
        "list_directory",
        "directory_tree",
        "read_text_file",
        "read_multiple_files",
        "search_files",
        "get_file_info",
        "create_directory",
        "write_file",
        "edit_file",
    ],
)


# 4. Connect to your local shell MCP server

shell_tools = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command=sys.executable,
            args=[
                str(SHELL_SERVER),
                "--root",
                str(WORKSPACE),
            ],
        ),
        timeout=90,
    ),
    tool_filter=[
        "run_command",
        "workspace_info",
        "start_server",
        "stop_server",
        "server_logs",
        "check_url",
    ],
    require_confirmation=shell_needs_confirmation,
)


# 5. Start the agent's tools list

tools = [filesystem_tools, shell_tools]


# 6. Add GitHub tools when a token is available

if GITHUB_PAT:
    github_url = "https://api.githubcopilot.com/mcp/"
    github_headers = {"Authorization": f"Bearer {GITHUB_PAT}"}

    # Reading from GitHub does not need approval.
    github_read_tools = McpToolset(
        connection_params=StreamableHTTPConnectionParams(
            url=github_url,
            headers=github_headers,
            timeout=30,
        ),
        tool_filter=[
            "get_me",
            "get_file_contents",
            "list_branches",
            "list_issues",
            "issue_read",
            "list_pull_requests",
        ],
    )

    # Writing to GitHub needs approval.
    github_write_tools = McpToolset(
        connection_params=StreamableHTTPConnectionParams(
            url=github_url,
            headers=github_headers,
            timeout=30,
        ),
        tool_filter=[
            "create_repository",
            "create_branch",
            "push_files",
            "create_pull_request",
            "add_issue_comment",
        ],
        require_confirmation=True,
    )

    tools.extend([github_read_tools, github_write_tools])


# 7. Define the agent's instructions

INSTRUCTION = f"""
You are a careful coding agent. You build and fix small Python projects.

Your workspace is: {WORKSPACE}
All files you create must be inside it.

How to use your tools:
- Files: use the filesystem tools to list, read, create and edit files.
  Prefer edit_file for small changes to existing files.
- Running code: use run_command (e.g. "pytest -q", "python main.py").
  Never use run_command to read or list files.
- GitHub: use the GitHub tools for anything remote (repositories, issues,
  branches, pull requests). To publish code, use push_files with the
  files' contents; never try "git push".

How to work:
1. Before writing code, look at what already exists in the workspace.
2. Work in small steps. After each change, run the tests.
3. If tests fail, read the error, fix the cause, and run them again.
   Stop after 3 failed attempts on the same problem and explain what's wrong.
4. Test web apps with pytest and FastAPI's TestClient first. To run the app
   for real, use start_server (never run_command with uvicorn), then
   check_url to call it and server_logs to see errors. The user can open
   http://127.0.0.1:8001 in their browser. Leave it running unless asked
   to stop it.
5. When finished, summarize what you changed and the final test result.
"""


# 8. Create the agent

root_agent = Agent(
    name="coding_agent",
    model='gemini-3.5-flash',
    description="A coding agent that edits files, runs tests and uses GitHub via MCP.",
    instruction=INSTRUCTION,
    tools=tools,
)
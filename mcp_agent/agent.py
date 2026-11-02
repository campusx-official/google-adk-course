import os
from pathlib import Path

from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import (
    StdioConnectionParams,
    StreamableHTTPConnectionParams,
)
from mcp import StdioServerParameters


load_dotenv()

github_token = os.getenv("GITHUB_TOKEN")
if not github_token:
    raise ValueError("Add GITHUB_TOKEN to your .env file.")

folder = Path(__file__).parent.joinpath("files").resolve()
folder.mkdir(exist_ok=True)


root_agent = Agent(
    name="github_publisher",
    model="gemini-3.5-flash",
    instruction=f"""
You have access to filesystem and GitHub MCP servers.
Use their tools to manage local files and handle GitHub workflows.
Local files are located in {folder}. Use absolute paths for filesystem operations.
""",
    tools=[
        # Read files from the local machine.
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="npx",
                    args=[
                        "-y",
                        "@modelcontextprotocol/server-filesystem",
                        str(folder),
                    ],
                )
            )
        ),

        # Github MCP Server
        McpToolset(
            connection_params=StreamableHTTPConnectionParams(
                url="https://api.githubcopilot.com/mcp/",
                headers={
                    "Authorization": f"Bearer {github_token}",
                }
            )
        )
    ]
)
# src/devops_mcp/server.py
from __future__ import annotations
from typing import List
from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent
from dotenv import load_dotenv

# Load .env from project root
load_dotenv()

# Initialize MCP server
mcp = FastMCP("devops-mcp")

# ── Base tools/prompts ────────────────────────────────────────────────────────
@mcp.tool()
def ping() -> str:
    """Simple health check."""
    return "pong"

@mcp.prompt()
def daily_brief_prompt() -> List[TextContent]:
    """Prompt template for daily summaries."""
    return [
        TextContent(
            type="text",
            text=(
                "Summarize today's meetings, top GitHub PRs, and key unread emails. "
                "Use bullet points, concise, under 12 lines."
            ),
        )
    ]

# ── Tool registrations ────────────────────────────────────────────────────────
# Minimal stack
from .tools import github as gh_tools
from .tools import calendar as cal_tools
from .tools import gmail as gm_tools
from .tools import brief as brief_tools
from .tools import github_list_repos as gh_list_repos_tools

gh_tools.register(mcp)
cal_tools.register(mcp)
gm_tools.register(mcp)
brief_tools.register(mcp)
gh_list_repos_tools.register(mcp)

# DevOps additions (Jenkins removed per request)
from .tools import ci_github_actions as gha_tools
from .tools import k8s_cluster as k8s_tools
from .tools import k8s_events as k8s_events_tools
from .tools import k8s_top as k8s_top_tools
from .tools import k8s_deploys as k8s_deploys_tools

gha_tools.register(mcp)
k8s_tools.register(mcp)
k8s_events_tools.register(mcp)
k8s_top_tools.register(mcp)
k8s_deploys_tools.register(mcp)

# ── Entrypoint ────────────────────────────────────────────────────────────────
def main() -> None:
    """Run the FastMCP server over stdio."""
    mcp.run()

if __name__ == "__main__":
    main()

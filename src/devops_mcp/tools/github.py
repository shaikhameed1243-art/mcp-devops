from __future__ import annotations
import os, httpx
from typing import List
from mcp.server.fastmcp import FastMCP

mcp: FastMCP

async def _client() -> httpx.AsyncClient:
    token = os.getenv("GITHUB_TOKEN", "").strip()
    if not token:
        raise RuntimeError("GITHUB_TOKEN is not set")
    return httpx.AsyncClient(
        base_url="https://api.github.com",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
        },
        timeout=20
    )

def register(server: FastMCP) -> None:
    global mcp
    mcp = server

    @mcp.tool()
    async def gh_list_prs(repo: str, state: str = "open", limit: int = 20) -> List[dict]:
        """List PRs for a repo (owner/name)."""
        async with await _client() as c:
            r = await c.get(f"/repos/{repo}/pulls", params={"state": state, "per_page": limit, "sort": "updated"})
            r.raise_for_status()
            return r.json()

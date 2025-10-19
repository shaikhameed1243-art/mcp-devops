from __future__ import annotations
import os, httpx
from typing import List
from mcp.server.fastmcp import FastMCP
mcp: FastMCP
async def _client() -> httpx.AsyncClient:
    token = os.getenv("GITHUB_TOKEN", "").strip()
    if not token:
        raise RuntimeError("GITHUB_TOKEN not set")
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
    async def gh_list_repos(limit: int = 50) -> List[str]:
        """
        List repositories visible to your token (read-only, limited to 50 by default).
        """
        async with await _client() as c:
            r = await c.get("/user/repos", params={"per_page": limit, "sort": "updated"})
            r.raise_for_status()
            data = r.json()
        return [f"{repo['full_name']} ({repo['html_url']})" for repo in data]

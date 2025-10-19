from __future__ import annotations
import os, httpx
from typing import List, Dict, Optional
from mcp.server.fastmcp import FastMCP
mcp: FastMCP
def _headers() -> Dict[str,str]:
    token = os.getenv("GITHUB_TOKEN","").strip()
    if not token:
        raise RuntimeError("GITHUB_TOKEN not set")
    return {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
def register(server: FastMCP) -> None:
    global mcp
    mcp = server
    @mcp.tool()
    async def gha_last_runs(repo: str, branch: str = "", limit: int = 10, status: str = "") -> List[Dict]:
        """
        List recent GitHub Actions workflow runs (read-only).
        - repo: owner/name
        - branch: optional filter
        - limit: number of runs (<=50)
        - status: optional (queued|in_progress|completed)
        """
        params = {"per_page": min(max(limit,1),50)}
        if branch: params["branch"] = branch
        if status: params["status"] = status
        async with httpx.AsyncClient(timeout=20) as c:
            r = await c.get(f"https://api.github.com/repos/{repo}/actions/runs", headers=_headers(), params=params)
            r.raise_for_status()
            runs = r.json().get("workflow_runs", [])
        out = []
        for w in runs:
            out.append({
                "id": w.get("id"),
                "name": (w.get("name") or w.get("display_title") or ""),
                "event": w.get("event"),
                "status": w.get("status"),
                "conclusion": w.get("conclusion"),
                "branch": (w.get("head_branch") or ""),
                "commit": (w.get("head_sha") or "")[:7],
                "url": w.get("html_url")
            })
        return out
    @mcp.tool()
    async def gha_failing_runs(repo: str, branch: str = "", limit: int = 20) -> List[Dict]:
        """
        List recent failing/unstable runs for a repo.
        """
        all_runs = await gha_last_runs(repo=repo, branch=branch, limit=limit, status="completed")
        return [r for r in all_runs if r.get("conclusion") in ("failure","timed_out","cancelled","neutral","action_required")]

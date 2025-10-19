from __future__ import annotations
import os, httpx, base64
from typing import List, Dict
from mcp.server.fastmcp import FastMCP
mcp: FastMCP
def _auth_headers() -> Dict[str,str]:
    base = os.getenv("JENKINS_BASE_URL","").rstrip("/")
    user = os.getenv("JENKINS_USER","")
    token = os.getenv("JENKINS_API_TOKEN","")
    if not (base and user and token):
        raise RuntimeError("Set JENKINS_BASE_URL, JENKINS_USER, JENKINS_API_TOKEN")
    b = base64.b64encode(f"{user}:{token}".encode()).decode()
    return base, {"Authorization": f"Basic {b}"}
def register(server: FastMCP) -> None:
    global mcp
    mcp = server
    @mcp.tool()
    async def jenkins_job_last_build(job: str) -> Dict:
        """
        Get last build summary for a job (read-only).
        - job: job name (url-encoded if nested), e.g. 'my-pipeline'
        """
        base, headers = _auth_headers()
        async with httpx.AsyncClient(timeout=20) as c:
            r = await c.get(f"{base}/job/{job}/lastBuild/api/json", headers=headers)
            r.raise_for_status()
            j = r.json()
        return {
            "id": j.get("id"),
            "number": j.get("number"),
            "result": j.get("result"),
            "duration_ms": j.get("duration"),
            "timestamp": j.get("timestamp"),
            "building": j.get("building"),
            "url": j.get("url"),
        }
    @mcp.tool()
    async def jenkins_view_failing(limit: int = 20) -> List[Dict]:
        """
        List failing jobs on the Jenkins root view (best-effort; read-only).
        """
        base, headers = _auth_headers()
        async with httpx.AsyncClient(timeout=20) as c:
            r = await c.get(f"{base}/api/json?tree=jobs[name,color,url]", headers=headers)
            r.raise_for_status()
            jobs = r.json().get("jobs", [])
        failing = [j for j in jobs if str(j.get("color","")).startswith("red")]
        return failing[:max(1,min(limit,50))]

from __future__ import annotations
import os
from typing import List, Dict
from mcp.server.fastmcp import FastMCP
from kubernetes import client, config
from kubernetes.client import ApiException
mcp: FastMCP
_LOADED=False
def _ensure_kube():
    global _LOADED
    if _LOADED: return
    kubeconfig = os.getenv("KUBECONFIG","")
    try:
        if kubeconfig and os.path.exists(kubeconfig):
            config.load_kube_config(config_file=kubeconfig)
        else:
            try:
                config.load_kube_config()
            except Exception:
                config.load_incluster_config()
        _LOADED=True
    except Exception as e:
        raise RuntimeError(f"Failed to load Kubernetes config: {e}")
def _age(ts):
    from datetime import datetime, timezone
    if not ts: return "?"
    delta = datetime.now(timezone.utc) - ts
    s = int(delta.total_seconds())
    if s<60: return f"{s}s"
    m=s//60
    if m<60: return f"{m}m"
    h=m//60
    if h<24: return f"{h}h"
    d=h//24
    return f"{d}d"
def register(server: FastMCP) -> None:
    global mcp
    mcp = server
    @mcp.tool()
    def k8s_pods(ns: str = "default", selector: str = "") -> List[Dict]:
        """List pods in a namespace (name, phase, ready, restarts, age)."""
        _ensure_kube()
        v1 = client.CoreV1Api()
        pods = v1.list_namespaced_pod(ns, label_selector=selector or None).items
        out=[]
        for p in pods:
            statuses = p.status.container_statuses or []
            ready = f"{sum(1 for s in statuses if s.ready)}/{len(statuses)}"
            restarts = sum((s.restart_count or 0) for s in statuses)
            out.append({
                "name": p.metadata.name,
                "phase": p.status.phase,
                "ready": ready,
                "restarts": restarts,
                "age": _age(p.status.start_time),
            })
        return out
    @mcp.tool()
    def k8s_tail(ns: str, pod: str, container: str = "", lines: int = 100) -> str:
        """Fetch last N log lines from a pod container."""
        _ensure_kube()
        v1 = client.CoreV1Api()
        try:
            return v1.read_namespaced_pod_log(name=pod, namespace=ns, container=container or None, tail_lines=lines)
        except ApiException as e:
            return f"ERROR: {e.status} {e.reason}: {e.body}"
    @mcp.tool()
    def k8s_deploy_status(ns: str, deploy: str) -> str:
        """Rollout status for a Deployment (simple)."""
        _ensure_kube()
        apps = client.AppsV1Api()
        try:
            d = apps.read_namespaced_deployment_status(name=deploy, namespace=ns)
        except ApiException as e:
            return f"ERROR: {e.status} {e.reason}: {e.body}"
        spec, status = d.spec, d.status
        desired = spec.replicas or 0
        ready = status.ready_replicas or 0
        updated = status.updated_replicas or 0
        available = status.available_replicas or 0
        if ready == desired == updated == available:
            return f"Deployment/{deploy} rolled out: {ready}/{desired} ready"
        return f"Deployment/{deploy} progressing: ready={ready}/{desired}, updated={updated}, available={available}"

from mcp.server.fastmcp import FastMCP
from kubernetes import client, config
mcp: FastMCP
def _kc():
    try: config.load_kube_config()
    except: config.load_incluster_config()
def register(s: FastMCP)->None:
    global mcp; mcp=s
    @mcp.tool()
    def k8s_events(ns: str="default", limit: int=30):
        _kc(); v1=client.CoreV1Api()
        ev=v1.list_namespaced_event(ns).items
        ev=sorted(ev, key=lambda e: e.last_timestamp or e.event_time or e.first_timestamp, reverse=True)
        out=[]
        for e in ev[:max(1,min(limit,200))]:
            out.append(f"[{e.type}] {e.reason} {e.involved_object.kind}/{e.involved_object.name}: {e.message}")
        return out

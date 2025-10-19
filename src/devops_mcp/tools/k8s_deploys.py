from mcp.server.fastmcp import FastMCP
from kubernetes import client, config
mcp: FastMCP
def _kc():
    try: config.load_kube_config()
    except: config.load_incluster_config()
def register(s: FastMCP)->None:
    global mcp; mcp=s
    @mcp.tool()
    def k8s_deploys(ns: str="default"):
        _kc(); apps=client.AppsV1Api()
        ds=apps.list_namespaced_deployment(ns).items
        out=[]
        for d in ds:
            spec, st = d.spec, d.status
            desired = spec.replicas or 0
            ready = st.ready_replicas or 0
            updated = st.updated_replicas or 0
            available = st.available_replicas or 0
            out.append({
                "name": d.metadata.name,
                "desired": desired,
                "ready": ready,
                "updated": updated,
                "available": available
            })
        return out

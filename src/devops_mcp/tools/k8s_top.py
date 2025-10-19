from mcp.server.fastmcp import FastMCP
from kubernetes import config
import subprocess
mcp: FastMCP
def _kc():
    try: config.load_kube_config()
    except: config.load_incluster_config()
def register(s: FastMCP)->None:
    global mcp; mcp=s
    @mcp.tool()
    def k8s_top_pods(ns: str="default"):
        _kc()
        try:
            out=subprocess.check_output(["kubectl","top","pods","-n",ns,"--no-headers"], text=True)
        except subprocess.CalledProcessError as e:
            return [f"ERROR: {e}"]
        rows=[]
        for line in out.strip().splitlines():
            parts=line.split()
            if len(parts)>=3:
                rows.append({"pod":parts[0],"cpu":parts[1],"memory":parts[2]})
        return rows

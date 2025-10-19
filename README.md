# 🚀 DevOps-MCP — The Multi-Context Protocol Server for DevOps

**DevOps-MCP** is an intelligent **Model Context Protocol (MCP)** server built to make a DevOps engineer’s day frictionless —  
from daily standups to Kubernetes health checks, from unread GitHub PRs to Gmail summaries — all wired through a single interface.

---

## 🎥 Demo

Watch the full screen-recorded demo below:

https://github.com/shaikhameed1243-art/mcp-devops/blob/main/MCP%20-%20Demo.mp4

## ✨ What It Does

This MCP server connects your LLM (Claude, OpenAI MCP client, etc.) to your **DevOps ecosystem** — securely and modularly.

| Integration | Purpose |
|--------------|----------|
| 🧠 **Claude / OpenAI MCP Client** | Ask natural-language questions like “what pods are crashing in dev?” |
| 🐙 **GitHub** | List repositories, pull requests, and CI workflows |
| 📅 **Google Calendar** | Fetch today’s meetings, upcoming slots, and time windows |
| 📧 **Gmail** | Summarize unread or new messages |
| ☸️ **Kubernetes** | Monitor pods, deployments, events, and resource usage |
| ⚙️ **GitHub Actions** | Check failing workflows or build statuses |
| 💬 **Daily Brief** | One-shot prompt summary across all tools |

---

## 🧩 Architecture

```
Claude ↔ MCP Inspector ↔ DevOps-MCP Server
                            ├── GitHub Tools
                            ├── Gmail + Calendar
                            ├── Kubernetes Cluster
                            ├── GitHub Actions
                            ├── Daily Brief Prompt
```

All tools follow the **MCP spec** and expose functions discoverable by any LLM client.

---

## 🛠️ Tech Stack

- 🐍 Python 3.11+
- ⚙️ FastMCP (`mcp.server.fastmcp`)
- ☸️ Kubernetes Python SDK
- 📦 `httpx`, `dotenv`, `anyio`
- 🧠 Claude / OpenAI MCP Inspector
- 🐳 Minikube or any K8s cluster

---

## ⚙️ Setup (Local)

```bash
# 1️⃣ Clone & enter
git clone https://github.com/<yourname>/devops-mcp.git
cd devops-mcp

# 2️⃣ Create virtual environment
python -m venv .venv
.venv\Scripts\activate

# 3️⃣ Install dependencies
pip install -r requirements.txt

# 4️⃣ Set environment variables
cp .env.example .env
# Then add your tokens:
# GITHUB_TOKEN=ghp_xxxxxxxxxx
# GOOGLE_CREDENTIALS_PATH=path/to/creds.json
# KUBECONFIG=C:\Users\<user>\.kube\config

# 5️⃣ Start the MCP server
$env:PYTHONPATH = (Resolve-Path .\src).Path
npx @modelcontextprotocol/inspector -- python -m devops_mcp.server
```

---

## 🧠 Example Prompts (from Claude)

```text
me: what pods are running in default?
→ k8s_pods(ns="default")

me: show events in kube-system
→ k8s_events(ns="kube-system", limit=10)

me: list my GitHub repos
→ gh_list_repos()

me: daily brief for my DevOps day
→ daily_brief_prompt()
```

---

## 🌐 Supported MCP Tools

| Tool | Description |
|------|--------------|
| `gh_list_repos` | List your GitHub repositories |
| `gh_list_prs` | Fetch PRs for any repo |
| `gha_failing_runs` | Show failing GitHub Actions workflows |
| `gmail_unread` | List unread emails |
| `meetings_today` | Display today’s calendar meetings |
| `k8s_pods`, `k8s_deploys`, `k8s_top_pods`, `k8s_events` | Kubernetes monitoring toolkit |
| `daily_brief` | Generate a concise daily summary |

---

## 🧩 Example: K8s Cluster Health

```bash
minikube start --driver=docker
kubectl create deploy hello --image=nginx
kubectl expose deploy hello --port=80
kubectl get pods -A
```

Then ask Claude:
> “what’s the status of deployments in default?”  
> “top pods in kube-system by cpu/memory”

---

## 🧱 Folder Structure

```
devops-mcp/
│
├── src/
│   └── devops_mcp/
│       ├── server.py              # MCP entrypoint
│       └── tools/
│           ├── github_list_repos.py
│           ├── gmail.py
│           ├── calendar.py
│           ├── k8s_cluster.py
│           ├── k8s_events.py
│           ├── k8s_top.py
│           ├── k8s_deploys.py
│           └── ci_github_actions.py
│
├── .env.example
├── requirements.txt
└── README.md
```

---

## 💡 Vision

This isn’t just another automation script —  
it’s a **bridge between your DevOps stack and AI reasoning**,  
a shell that speaks in **natural language and context**.  

> "Let the routine fade to silence,  
> and let automation whisper the signal."

---

## 🤝 Contribute

PRs welcome — new integrations (PagerDuty, Grafana, AWS, Azure, etc.) are on the roadmap.  
Tag it with `#DevOpsMCP` if you post your build logs or screenshots.

---

## 📬 Author

**Hameed** — DevOps Engineer · GenAI Python Developer · Writer  
💻 GitHub: [@shaikhameed](https://github.com/shaikhameed1243-art/)  
💬 LinkedIn: [linkedin.com](www.linkedin.com/in/hameedbasha)

---

> “DevOps should not be a daily battle. It should be an orchestra —  
> and this MCP is the conductor.”

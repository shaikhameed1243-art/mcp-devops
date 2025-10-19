@echo off
REM --- resolve project root to this script's folder ---
set "ROOT=%~dp0"
chcp 65001 >NUL
REM --- prefer venv python if present ---
set "PY=%ROOT%.venv\Scripts\python.exe"
if not exist "%PY%" set "PY=python"
REM --- make src importable & load .env by working in project root ---
set "PYTHONPATH=%ROOT%src"
cd /d "%ROOT%"
REM --- run MCP server over stdio ---
"%PY%" -m devops_mcp.server

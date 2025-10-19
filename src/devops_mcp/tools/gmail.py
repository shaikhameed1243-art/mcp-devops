from __future__ import annotations
import os, imaplib, email, datetime as dt
from typing import List, Dict
from mcp.server.fastmcp import FastMCP

mcp: FastMCP

def _login():
    host = os.getenv("GMAIL_IMAP_HOST", "imap.gmail.com")
    user = os.getenv("GMAIL_IMAP_USER", "")
    app_pw = os.getenv("GMAIL_IMAP_APP_PASSWORD", "")
    if not (user and app_pw):
        raise RuntimeError("GMAIL_IMAP_USER or GMAIL_IMAP_APP_PASSWORD missing")
    M = imaplib.IMAP4_SSL(host)
    M.login(user, app_pw)
    return M

def _clean(s: str) -> str:
    return " ".join((s or "").split())

def register(server: FastMCP) -> None:
    global mcp
    mcp = server

    @mcp.tool()
    def gmail_unread(limit: int = 10, since_days: int = 2) -> List[Dict]:
        """Recent UNSEEN emails: [{date, from, subject, snippet}]"""
        M = _login()
        try:
            M.select("INBOX")
            since = (dt.date.today() - dt.timedelta(days=since_days)).strftime("%d-%b-%Y")
            typ, data = M.search(None, "(UNSEEN)", f'(SINCE "{since}")')
            if typ != "OK":
                return []
            ids = data[0].split()
            if limit and len(ids) > limit:
                ids = ids[-limit:]
            out: List[Dict] = []
            for i in reversed(ids):
                typ, msg_data = M.fetch(i, "(RFC822)")
                if typ != "OK" or not msg_data:
                    continue
                raw = msg_data[0][1]
                msg = email.message_from_bytes(raw)
                dh = email.header.decode_header(msg.get("Subject", ""))
                subject = "(no subject)"
                if dh:
                    s0, enc = dh[0]
                    subject = s0.decode(enc or "utf-8", errors="ignore") if isinstance(s0, bytes) else (s0 or subject)
                frm = email.utils.parseaddr(msg.get("From", ""))[1] or msg.get("From", "")
                # snippet
                text = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            payload = part.get_payload(decode=True) or b""
                            text = payload.decode(errors="ignore")
                            break
                else:
                    payload = msg.get_payload(decode=True) or b""
                    text = payload.decode(errors="ignore")
                out.append({"date": msg.get("Date",""), "from": frm, "subject": _clean(subject), "snippet": _clean(text[:160])})
            return out
        finally:
            try: M.close()
            except Exception: pass
            try: M.logout()
            except Exception: pass

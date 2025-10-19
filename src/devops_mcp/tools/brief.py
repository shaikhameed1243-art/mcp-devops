from __future__ import annotations
import os, datetime as dt, httpx, email, imaplib
from typing import List
from dateutil import tz
from icalendar import Calendar
from mcp.server.fastmcp import FastMCP

mcp: FastMCP

def _local_day_bounds():
    now = dt.datetime.now(tz=tz.tzlocal())
    s = now.replace(hour=0, minute=0, second=0, microsecond=0)
    e = s + dt.timedelta(days=1)
    return s.astimezone(dt.timezone.utc), e.astimezone(dt.timezone.utc)

async def _gh(repo: str, limit: int) -> List[str]:
    token = os.getenv("GITHUB_TOKEN","").strip()
    if not (repo and token): return []
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
    async with httpx.AsyncClient(timeout=20) as c:
        r = await c.get(f"https://api.github.com/repos/{repo}/pulls", params={"state":"open","per_page":limit,"sort":"updated"})
        r.raise_for_status()
        prs = r.json()
    out=[]
    for pr in prs:
        num=pr.get("number"); title=(pr.get("title") or "").strip(); url=pr.get("html_url","")
        out.append(f"PR #{num}: {title} {f'({url})' if url else ''}".strip())
    return out

async def _ics_today(urls: List[str]) -> List[str]:
    s,e = _local_day_bounds()
    out: List[str] = []
    async with httpx.AsyncClient(timeout=20) as c:
        for u in urls:
            if not u: continue
            r = await c.get(u); r.raise_for_status()
            cal = Calendar.from_ical(r.content)
            for ev in cal.walk("VEVENT"):
                ds = ev.decoded("DTSTART"); de = ev.decoded("DTEND", ds)
                if isinstance(ds, dt.date) and not isinstance(ds, dt.datetime):
                    ds = dt.datetime.combine(ds, dt.time.min, tzinfo=dt.timezone.utc)
                    de = dt.datetime.combine(de, dt.time.min, tzinfo=dt.timezone.utc)
                if ds.tzinfo is None: ds = ds.replace(tzinfo=dt.timezone.utc)
                if de.tzinfo is None: de = de.replace(tzinfo=dt.timezone.utc)
                if not (de <= s or ds >= e):
                    out.append(f"{ds.astimezone(tz.tzlocal()).strftime('%H:%M')} — {str(ev.get('SUMMARY') or '(no title)')}")
    return sorted(out)

def _gmail(limit:int) -> List[str]:
    user=os.getenv("GMAIL_IMAP_USER","").strip()
    pw  =os.getenv("GMAIL_IMAP_APP_PASSWORD","").strip()
    host=os.getenv("GMAIL_IMAP_HOST","imap.gmail.com").strip()
    if not (user and pw): return []
    M=imaplib.IMAP4_SSL(host)
    try:
        M.login(user,pw); M.select("INBOX")
        typ, data = M.search(None, "(UNSEEN)")
        if typ!="OK": return []
        ids = data[0].split()
        if limit and len(ids)>limit: ids = ids[-limit:]
        out=[]
        for i in reversed(ids):
            typ, msg_data = M.fetch(i,"(RFC822)")
            if typ!="OK" or not msg_data: continue
            msg=email.message_from_bytes(msg_data[0][1])
            dh=email.header.decode_header(msg.get("Subject","")); subject="(no subject)"
            if dh:
                s0,enc=dh[0]
                subject=s0.decode(enc or "utf-8",errors="ignore") if isinstance(s0,bytes) else (s0 or subject)
            frm=email.utils.parseaddr(msg.get("From",""))[1] or msg.get("From","")
            out.append(f"{frm} — {subject}")
        return out
    finally:
        try: M.close()
        except Exception: pass
        try: M.logout()
        except Exception: pass

def register(server: FastMCP) -> None:
    global mcp
    mcp = server

    @mcp.tool()
    async def daily_brief(repo: str = "", prs: int = 5, emails: int = 5) -> str:
        parts: List[str] = []
        if repo:
            try: pr_list = await _gh(repo, max(1,min(prs,20)))
            except Exception as e: pr_list=[f"ERR PRs: {e}"]
            if pr_list: parts.append("PRs:\n- " + "\n- ".join(pr_list))
        ics=[s.strip() for s in os.getenv("GOOGLE_ICS_URLS","").split(",") if s.strip()]
        if ics:
            try: meets = await _ics_today(ics)
            except Exception as e: meets=[f"ERR Meetings: {e}"]
            if meets: parts.append("Meetings Today:\n- " + "\n- ".join(meets))
        try: mails = _gmail(max(1,min(emails,20)))
        except Exception as e: mails=[f"ERR Email: {e}"]
        if mails: parts.append("Unread Emails:\n- " + "\n- ".join(mails))
        return "\n\n".join(parts) if parts else "No PRs, no meetings, no unread mail."

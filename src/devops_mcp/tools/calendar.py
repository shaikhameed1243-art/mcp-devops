from __future__ import annotations
import os, datetime as dt, httpx
from typing import List
from dateutil import tz
from icalendar import Calendar, Event
from mcp.server.fastmcp import FastMCP

mcp: FastMCP

def _local_day_bounds() -> tuple[dt.datetime, dt.datetime]:
    now = dt.datetime.now(tz=tz.tzlocal())
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + dt.timedelta(days=1)
    return start.astimezone(dt.timezone.utc), end.astimezone(dt.timezone.utc)

async def _ics_today(urls: List[str]) -> List[str]:
    start, end = _local_day_bounds()
    out: List[str] = []
    async with httpx.AsyncClient(timeout=20) as c:
        for u in urls:
            if not u:
                continue
            r = await c.get(u)
            r.raise_for_status()
            cal = Calendar.from_ical(r.content)
            for comp in cal.walk():
                if comp.name != "VEVENT":
                    continue
                ev: Event = comp
                dtstart = ev.decoded("DTSTART")
                dtend = ev.decoded("DTEND", dtstart)
                if isinstance(dtstart, dt.date) and not isinstance(dtstart, dt.datetime):
                    dtstart = dt.datetime.combine(dtstart, dt.time.min, tzinfo=dt.timezone.utc)
                    dtend = dt.datetime.combine(dtend, dt.time.min, tzinfo=dt.timezone.utc)
                if dtstart.tzinfo is None:
                    dtstart = dtstart.replace(tzinfo=dt.timezone.utc)
                if dtend.tzinfo is None:
                    dtend = dtend.replace(tzinfo=dt.timezone.utc)
                if not (dtend <= start or dtstart >= end):
                    title = str(ev.get("SUMMARY") or "(no title)")
                    local_t = dtstart.astimezone(tz.tzlocal()).strftime("%H:%M")
                    out.append(f"{local_t} — {title}")
    return sorted(out)

def register(server: FastMCP) -> None:
    global mcp
    mcp = server

    @mcp.tool()
    async def meetings_today() -> List[str]:
        """Return today's meetings via Google ICS URLs (comma-separated)."""
        ics_urls = [s.strip() for s in os.getenv("GOOGLE_ICS_URLS", "").split(",") if s.strip()]
        if not ics_urls:
            return []
        return await _ics_today(ics_urls)

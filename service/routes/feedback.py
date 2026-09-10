"""
UI feedback — thumbs up/down plus an optional note on any tagged screen or
block. Single writer (the reviewing user), so no auth; the browser generates
the row id and PUTs twice (vote, then note) into the same row.
"""
from __future__ import annotations
import csv
import io
import json
import uuid
from html import escape
from typing import Optional

from fastapi import APIRouter, Depends, Query
from fastapi.responses import HTMLResponse, Response
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from service.database import get_db
from service import models

router = APIRouter()

NOTE_MAX = 4000

EXPORT_COLUMNS = [
    "created_at", "section_id", "section_label", "verdict", "note",
    "screen", "clinic_user", "view_mode", "app_version", "url", "id",
]


class FeedbackIn(BaseModel):
    section_id: str = Field(max_length=120)
    section_label: Optional[str] = Field(default=None, max_length=255)
    verdict: str
    note: Optional[str] = None
    clinic_user: Optional[str] = Field(default=None, max_length=50)
    view_mode: Optional[str] = Field(default=None, max_length=20)
    url: Optional[str] = None
    app_version: Optional[str] = Field(default=None, max_length=60)
    user_agent: Optional[str] = None


def _screen_of(section_id: str) -> str:
    """Group blocks under their screen: cl.business_reports.revenue_cycle →
    cl.business_reports. A bare screen id (cl.dashboard) is its own screen —
    trimming it would collapse everything to a useless "cl"."""
    parts = section_id.split(".")
    return ".".join(parts[:-1]) if len(parts) > 2 else section_id


def _row_dict(r: models.UiFeedback) -> dict:
    return {
        "id": str(r.id),
        "section_id": r.section_id,
        "section_label": r.section_label,
        "screen": r.screen,
        "verdict": r.verdict,
        "note": r.note,
        "clinic_user": r.clinic_user,
        "view_mode": r.view_mode,
        "url": r.url,
        "app_version": r.app_version,
        "created_at": r.created_at.isoformat() if r.created_at else None,
    }


def _all_rows(db: Session, newest_first: bool = False):
    stmt = select(models.UiFeedback).order_by(
        models.UiFeedback.created_at.desc() if newest_first else models.UiFeedback.created_at.asc()
    )
    return db.execute(stmt).scalars().all()


@router.put("/feedback/{feedback_id}")
def upsert_feedback(feedback_id: uuid.UUID, data: FeedbackIn, db: Session = Depends(get_db)) -> dict:
    """Create the row on the thumbs click, update it if a note follows."""
    verdict = data.verdict if data.verdict in ("up", "down") else "up"
    note = (data.note or "").strip()[:NOTE_MAX] or None

    row = db.get(models.UiFeedback, feedback_id)
    if row is None:
        row = models.UiFeedback(id=feedback_id, section_id=data.section_id, verdict=verdict)
        db.add(row)

    row.section_id = data.section_id
    row.section_label = data.section_label
    row.screen = _screen_of(data.section_id)
    row.verdict = verdict
    row.note = note
    row.clinic_user = data.clinic_user
    row.view_mode = data.view_mode
    row.url = data.url
    row.app_version = data.app_version
    row.user_agent = data.user_agent

    db.commit()
    db.refresh(row)
    return _row_dict(row)


@router.delete("/feedback/{feedback_id}")
def delete_feedback(feedback_id: uuid.UUID, db: Session = Depends(get_db)) -> dict:
    """Used when the reviewer un-votes by clicking the same thumb again."""
    row = db.get(models.UiFeedback, feedback_id)
    if row is not None:
        db.delete(row)
        db.commit()
    return {"ok": True}


@router.get("/feedback")
def list_feedback(db: Session = Depends(get_db)) -> list:
    return [_row_dict(r) for r in _all_rows(db, newest_first=True)]


@router.get("/feedback/summary")
def feedback_summary(db: Session = Depends(get_db)) -> list:
    """Per-section tallies, worst-rated first — the triage view."""
    buckets: dict[str, dict] = {}
    for r in _all_rows(db):
        b = buckets.setdefault(r.section_id, {
            "section_id": r.section_id, "section_label": r.section_label,
            "up": 0, "down": 0, "notes": [],
        })
        b["section_label"] = r.section_label or b["section_label"]
        b["up" if r.verdict == "up" else "down"] += 1
        if r.note:
            b["notes"].append(r.note)
    return sorted(buckets.values(), key=lambda b: (-b["down"], b["section_id"]))


@router.get("/feedback/export.jsonl")
def export_jsonl(db: Session = Depends(get_db)) -> Response:
    body = "".join(json.dumps(_row_dict(r)) + "\n" for r in _all_rows(db))
    return Response(
        content=body,
        media_type="application/x-ndjson",
        headers={"Content-Disposition": 'attachment; filename="feedback.jsonl"'},
    )


@router.get("/feedback/export.csv")
def export_csv(db: Session = Depends(get_db)) -> Response:
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=EXPORT_COLUMNS, extrasaction="ignore")
    w.writeheader()
    for r in _all_rows(db):
        w.writerow(_row_dict(r))
    return Response(
        content=buf.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="feedback.csv"'},
    )


@router.get("/feedback/view", response_class=HTMLResponse, include_in_schema=False)
def feedback_view(db: Session = Depends(get_db), sort: str = Query("recent")) -> HTMLResponse:
    rows = _all_rows(db, newest_first=True)
    if sort == "section":
        rows = sorted(rows, key=lambda r: (r.section_id, r.created_at or ""))

    total = len(rows)
    ups = sum(1 for r in rows if r.verdict == "up")
    downs = total - ups

    cells = []
    for r in rows:
        when = r.created_at.strftime("%b %d, %Y %H:%M") if r.created_at else "—"
        thumb = "👍" if r.verdict == "up" else "👎"
        cells.append(
            "<tr>"
            f"<td class=w>{escape(when)}</td>"
            f"<td class=v>{thumb}</td>"
            f"<td><div class=lbl>{escape(r.section_label or '')}</div>"
            f"<code>{escape(r.section_id)}</code></td>"
            f"<td class=note>{escape(r.note or '') or '<span class=dim>—</span>'}</td>"
            f"<td class=w>{escape(r.clinic_user or '—')}</td>"
            f"<td class=w><code>{escape((r.app_version or '—')[:12])}</code></td>"
            "</tr>"
        )
    body = "".join(cells) or '<tr><td colspan=6 class=dim style="padding:28px;text-align:center">No feedback yet.</td></tr>'

    html = f"""<!doctype html><html><head><meta charset=utf-8>
<title>UI Feedback — {total} entries</title>
<meta name=viewport content="width=device-width,initial-scale=1">
<style>
:root{{color-scheme:light dark;--bg:#fbfbfa;--fg:#1c1c1a;--dim:#78766f;--line:#e5e3dd;--card:#fff}}
@media(prefers-color-scheme:dark){{:root{{--bg:#14140f;--fg:#eceae4;--dim:#918d84;--line:#2c2b26;--card:#1b1b16}}}}
*{{box-sizing:border-box}}
body{{margin:0;padding:28px 20px;background:var(--bg);color:var(--fg);
font:14px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif}}
.wrap{{max-width:1100px;margin:0 auto}}
h1{{font-size:20px;margin:0 0 4px;font-weight:600}}
.sub{{color:var(--dim);font-size:13px;margin-bottom:18px}}
.bar{{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:18px}}
.bar a{{padding:6px 12px;border:1px solid var(--line);border-radius:7px;background:var(--card);
color:var(--fg);text-decoration:none;font-size:12.5px}}
.bar a:hover{{border-color:var(--dim)}}
.tbl{{overflow-x:auto;border:1px solid var(--line);border-radius:10px;background:var(--card)}}
table{{border-collapse:collapse;width:100%;min-width:760px}}
th{{text-align:left;font-size:11px;text-transform:uppercase;letter-spacing:.06em;color:var(--dim);
padding:11px 12px;border-bottom:1px solid var(--line);font-weight:600}}
td{{padding:11px 12px;border-bottom:1px solid var(--line);vertical-align:top}}
tr:last-child td{{border-bottom:0}}
code{{font:11.5px ui-monospace,SFMono-Regular,Menlo,monospace;color:var(--dim)}}
.lbl{{font-weight:600;margin-bottom:2px}}
.w{{white-space:nowrap;color:var(--dim);font-size:12.5px}}
.v{{font-size:16px;text-align:center}}
.note{{max-width:380px;white-space:pre-wrap;word-break:break-word}}
.dim{{color:var(--dim)}}
</style></head><body><div class=wrap>
<h1>UI Feedback</h1>
<div class=sub>{total} entries · 👍 {ups} · 👎 {downs}</div>
<div class=bar>
<a href="?sort=recent">Most recent</a>
<a href="?sort=section">Group by section</a>
<a href="/api/feedback/export.csv">Download CSV</a>
<a href="/api/feedback/export.jsonl">Download JSONL</a>
<a href="/api/feedback/summary">Summary JSON</a>
</div>
<div class=tbl><table>
<thead><tr><th>When</th><th></th><th>Section</th><th>Note</th><th>User</th><th>Build</th></tr></thead>
<tbody>{body}</tbody>
</table></div>
</div></body></html>"""
    return HTMLResponse(html)

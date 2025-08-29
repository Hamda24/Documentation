# app.py (use this exact handler)

from fastapi import FastAPI, Response, Header, HTTPException, Request
from fastapi.responses import HTMLResponse, PlainTextResponse
from pydantic import BaseModel, EmailStr, HttpUrl
from typing import List, Optional
from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML, CSS
from datetime import datetime
import os

app = FastAPI(title="Standard Report PDF Renderer", version="1.0.0")
API_KEY = os.getenv("API_KEY")

class SheetLink(BaseModel):
    subtitle: str
    url: HttpUrl

class Owner(BaseModel):
    name: str
    email: EmailStr

class Payload(BaseModel):
    report_title: str
    media_team: str
    owner: Owner
    report_frequency: str              # Daily | Weekly | Monthly
    platforms: List[str]
    tools_used: List[str]
    automated: bool
    google_sheets: List[SheetLink]
    bigquery_link: Optional[HttpUrl] = None
    report_link: HttpUrl
    adjustments_needed: str
    description: str
    additional_notes: str

def today(): return datetime.now().strftime("%B %d, %Y")

def filename(freq, title):
    safe = "".join(c for c in title if c.isalnum() or c in (" ", "-", "_")).strip().replace(" ", "")
    return f"{freq}-{safe}.pdf"

env = Environment(loader=FileSystemLoader("templates"),
                  autoescape=select_autoescape(["html","xml"]))

@app.get("/health", include_in_schema=False)
def health():
    return Response(content="ok", media_type="text/plain")

@app.get("/", response_class=PlainTextResponse)
def root(): return "OK - See /docs and /privacy"

@app.get("/privacy", response_class=HTMLResponse)
def privacy(): return f"<h1>Privacy</h1><p>Effective: {today()}</p>"


@app.post("/render/v1-standard-report")
def render_standard_report(p: Payload, request: Request, x_api_key: Optional[str] = Header(default=None)):
    if API_KEY and x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if p.automated and not p.bigquery_link:
        raise HTTPException(status_code=422, detail="bigquery_link is required when automated=true")

    notes = (p.additional_notes or "").strip() or f"For access issues, contact {p.owner.email}"

    html = env.get_template("standard.html").render(
        freq=p.report_frequency,
        report_title=p.report_title,
        media_team=p.media_team,
        owner=p.owner.model_dump(),
        platforms=p.platforms,
        tools_used=p.tools_used,
        automated=p.automated,
        google_sheets=[s.model_dump() for s in p.google_sheets],
        bigquery_link=p.bigquery_link,
        report_link=p.report_link,
        adjustments_needed=p.adjustments_needed,
        description=p.description,
        additional_notes=notes,
        today=today()
    )

    pdf_bytes = HTML(string=html, base_url=".").write_pdf(
        stylesheets=[CSS(filename="templates/standard.css")]
    )

    fname = filename(p.report_frequency, p.report_title)
    headers = {
        "Content-Disposition": f'attachment; filename="{fname}"; filename*=UTF-8\'\'{fname}',
        "Content-Length": str(len(pdf_bytes)),     # avoids chunked transfer
        "Cache-Control": "no-store",
        "Connection": "close",
        # optional: "X-Content-Type-Options": "nosniff"
    }
    return Response(content=pdf_bytes, media_type="application/octet-stream", headers=headers)
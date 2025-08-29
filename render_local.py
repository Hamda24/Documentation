from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML, CSS
from datetime import datetime
import json, os

def today_long():
    return datetime.now().strftime("%B %d, %Y")

def filename(freq, title):
    safe = "".join(c for c in title if c.isalnum() or c in (" ", "-", "_")).strip().replace(" ", "")
    return f"{freq}-{safe}.pdf"

# --- sample data (what the GPT will eventually send) ---
data = {
    "report_title": "CampaignOverview",
    "media_team": "Performance – MENA",
    "owner": {"name": "Jane Doe", "email": "jane.doe@company.com"},
    "report_frequency": "Weekly",      # autofill in GPT layer
    "platforms": ["Instagram", "TikTok"],
    "tools_used": ["Looker", "Google Sheets", "BigQuery"],
    "automated": True,
    "google_sheets": [
        {"subtitle": "Master Sheet", "url": "https://docs.google.com/spreadsheets/d/abc"},
        {"subtitle": "QC Log", "url": "https://docs.google.com/spreadsheets/d/xyz"}
    ],
    "bigquery_link": "https://console.cloud.google.com/bigquery?project=demo&ws=123",
    "report_link": "https://lookerstudio.google.com/reporting/123",
    "adjustments_needed": "Add story-level breakdown.",
    "description": "Weekly KPIs with paid/organic split.",
    "additional_notes": ""   # will be auto-filled if blank
}

# Autofill Additional Notes if blank
if not data["additional_notes"].strip():
    data["additional_notes"] = f'For access issues, contact {data["owner"]["email"]}'

# Render
env = Environment(loader=FileSystemLoader("templates"),
                  autoescape=select_autoescape(["html","xml"]))
html = env.get_template("standard.html").render(
    freq=data["report_frequency"],
    report_title=data["report_title"],
    media_team=data["media_team"],
    owner=data["owner"],
    platforms=data["platforms"],
    tools_used=data["tools_used"],
    automated=data["automated"],
    google_sheets=data["google_sheets"],
    bigquery_link=data.get("bigquery_link"),
    report_link=data["report_link"],
    adjustments_needed=data["adjustments_needed"],
    description=data["description"],
    additional_notes=data["additional_notes"],
    today=today_long()
)

pdf_bytes = HTML(string=html, base_url=".").write_pdf(
    stylesheets=[CSS(filename="templates/standard.css")]
)

out = filename(data["report_frequency"], data["report_title"])
with open(out, "wb") as f:
    f.write(pdf_bytes)

print("Created:", out)
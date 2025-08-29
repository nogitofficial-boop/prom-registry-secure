import os
import csv
import io
from datetime import datetime

from fastapi import FastAPI, Request, Form, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .security import encrypt_str, decrypt_str, require_admin, security_headers_middleware
from .db import ensure_db, insert_submission, fetch_all_count, fetch_all_rows

app = FastAPI(title="IITD Prom Registry", version="1.0.0")

# Optional secure headers
if os.getenv("ENABLE_SECURE_HEADERS", "").lower() in {"1", "true", "yes"}:
    app.middleware("http")(security_headers_middleware)

# Static + templates
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

@app.on_event("startup")
def _init():
    ensure_db()

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/submit")
def submit(
    name: str = Form(..., min_length=1, max_length=100),
    instagram: str = Form(..., min_length=1, max_length=100),
    entry_number: str = Form(..., min_length=1, max_length=32),
    gender: str = Form(..., min_length=1, max_length=32),
):
    name = name.strip()
    instagram = instagram.strip().lstrip("@")
    entry_number = entry_number.strip().upper()
    gender = gender.strip()

    name_e = encrypt_str(name)
    ig_e = encrypt_str(instagram)
    entry_e = encrypt_str(entry_number)
    gender_e = encrypt_str(gender)

    insert_submission(name_e, ig_e, entry_e, gender_e)

    return RedirectResponse(url="/success", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/success", response_class=HTMLResponse)
def success(request: Request):
    return templates.TemplateResponse("success.html", {"request": request})

@app.get("/admin/count")
def admin_count(admin_ok=Depends(require_admin)):
    return {"count": fetch_all_count()}

@app.get("/admin/export")
def admin_export(admin_ok=Depends(require_admin)):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["name", "instagram", "entry_number", "gender", "created_at"])
    for row in fetch_all_rows():
        name = decrypt_str(row["name_enc"])
        instagram = decrypt_str(row["instagram_enc"])
        entry = decrypt_str(row["entry_enc"])
        gender = decrypt_str(row["gender_enc"])
        created_at = row["created_at"]
        writer.writerow([name, instagram, entry, gender, created_at])
    output.seek(0)
    headers = {"Content-Disposition": 'attachment; filename="submissions.csv"'}
    return StreamingResponse(iter([output.read()]), media_type="text/csv", headers=headers)

@app.get("/health")
def health():
    return {"ok": True}

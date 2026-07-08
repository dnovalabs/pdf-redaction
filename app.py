"""PDF Redactor — redaction + Google Drive export."""

import io
import json
import logging
import uuid
from pathlib import Path

import fitz  # pymupdf
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import HTMLResponse, Response, StreamingResponse
from pydantic import BaseModel

app = FastAPI(title="PDF Redactor")
log = logging.getLogger("pdf-redactor")

sessions: dict[str, dict] = {}
PREVIEW_DPI = 150
CONFIG_PATH = Path(__file__).parent / "config.json"


# ── Config ───────────────────────────────────────────────────────────────


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        return {}
    with open(CONFIG_PATH) as f:
        return json.load(f)


def get_drive_service():
    """Build a Google Drive API service from service account credentials."""
    from google.oauth2.service_account import Credentials
    from googleapiclient.discovery import build

    cfg = load_config().get("storage", {})
    creds_path = Path(__file__).parent / cfg.get("credentials_path", "credentials.json")

    if not creds_path.exists():
        raise HTTPException(500, f"Credentials file not found: {creds_path.name}")

    creds = Credentials.from_service_account_file(
        str(creds_path),
        scopes=["https://www.googleapis.com/auth/drive.file"],
    )
    return build("drive", "v3", credentials=creds)


# ── Models ───────────────────────────────────────────────────────────────


class Rect(BaseModel):
    page: int
    x: float
    y: float
    w: float
    h: float


class RedactRequest(BaseModel):
    rects: list[Rect] = []
    text_query: str = ""


class ConfirmRequest(BaseModel):
    customer_name: str


# ── Helpers ──────────────────────────────────────────────────────────────


def get_session(sid: str) -> dict:
    s = sessions.get(sid)
    if not s:
        raise HTTPException(404, "Session not found. Upload a PDF first.")
    return s


def apply_redactions_to_doc(doc: fitz.Document, rects: list[Rect], text_query: str) -> int:
    pages_touched: set[int] = set()
    count = 0

    for r in rects:
        if r.page < 0 or r.page >= len(doc):
            continue
        pg = doc[r.page]
        pw, ph = pg.rect.width, pg.rect.height
        pdf_rect = fitz.Rect(r.x * pw, r.y * ph, (r.x + r.w) * pw, (r.y + r.h) * ph)
        pg.add_redact_annot(pdf_rect, fill=(1, 1, 1))
        pages_touched.add(r.page)
        count += 1

    if text_query:
        for i, pg in enumerate(doc):
            hits = pg.search_for(text_query)
            for rect in hits:
                pg.add_redact_annot(rect, fill=(1, 1, 1))
                count += 1
            if hits:
                pages_touched.add(i)

    for p in pages_touched:
        doc[p].apply_redactions(images=fitz.PDF_REDACT_IMAGE_PIXELS)

    return count


def build_filename(customer_name: str) -> str:
    cfg = load_config()
    pattern = cfg.get("file_naming", {}).get("pattern", "{customer_name}.pdf")
    return pattern.format(customer_name=customer_name)


def commit_pending(sid: str) -> bytes:
    """Commit pending redaction and return the final bytes."""
    session = get_session(sid)
    if not session.get("pending_bytes"):
        raise HTTPException(400, "No pending redaction to confirm.")
    session["doc_bytes"] = session["pending_bytes"]
    session["pending_bytes"] = None
    return session["doc_bytes"]


# ── Routes ───────────────────────────────────────────────────────────────


@app.get("/", response_class=HTMLResponse)
def index():
    return (Path(__file__).parent / "index.html").read_text()


@app.get("/config-status")
def config_status():
    """Return current storage config (without secrets) so the UI can adapt."""
    cfg = load_config()
    storage = cfg.get("storage", {})
    storage_type = storage.get("type", "none")

    creds_ok = False
    if storage_type == "google_drive":
        creds_path = Path(__file__).parent / storage.get("credentials_path", "credentials.json")
        creds_ok = creds_path.exists()

    return {
        "storage_type": storage_type,
        "folder_id": storage.get("folder_id", ""),
        "credentials_ok": creds_ok,
        "file_naming_pattern": cfg.get("file_naming", {}).get("pattern", "{customer_name}.pdf"),
    }


@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Only PDF files are accepted.")
    data = await file.read()
    try:
        doc = fitz.open(stream=data, filetype="pdf")
        page_count = len(doc)
        doc.close()
    except Exception:
        raise HTTPException(400, "Invalid PDF.")

    sid = uuid.uuid4().hex[:12]
    sessions[sid] = {"doc_bytes": data, "filename": file.filename, "pending_bytes": None}
    return {"session_id": sid, "page_count": page_count, "filename": file.filename}


@app.get("/preview/{sid}/{page}")
def preview_page(sid: str, page: int, search: str = "", pending: bool = False):
    session = get_session(sid)
    src = session["pending_bytes"] if pending and session.get("pending_bytes") else session["doc_bytes"]
    doc = fitz.open(stream=src, filetype="pdf")

    if page < 0 or page >= len(doc):
        raise HTTPException(400, f"Page {page} out of range.")
    pg = doc[page]
    if search and not pending:
        for inst in pg.search_for(search):
            pg.add_highlight_annot(inst)
    pix = pg.get_pixmap(dpi=PREVIEW_DPI)
    doc.close()
    return Response(
        content=pix.tobytes("png"),
        media_type="image/png",
        headers={"Cache-Control": "no-store"},
    )


@app.get("/search/{sid}")
def search(sid: str, q: str = ""):
    if not q:
        return {"matches": [], "total": 0}
    doc = fitz.open(stream=get_session(sid)["doc_bytes"], filetype="pdf")
    matches, total = [], 0
    for i, pg in enumerate(doc):
        found = pg.search_for(q)
        if found:
            matches.append({"page": i, "count": len(found)})
            total += len(found)
    doc.close()
    return {"matches": matches, "total": total, "query": q}


@app.post("/prepare-redaction/{sid}")
def prepare_redaction(sid: str, body: RedactRequest):
    if not body.rects and not body.text_query:
        raise HTTPException(400, "No redaction targets provided.")

    session = get_session(sid)
    doc = fitz.open(stream=session["doc_bytes"], filetype="pdf")
    count = apply_redactions_to_doc(doc, body.rects, body.text_query)

    if count == 0:
        doc.close()
        raise HTTPException(404, "No content matched for redaction.")

    buf = io.BytesIO()
    doc.save(buf, garbage=4, deflate=True)
    doc.close()
    buf.seek(0)
    session["pending_bytes"] = buf.read()

    return {"count": count, "page_count": len(fitz.open(stream=session["pending_bytes"], filetype="pdf"))}


@app.post("/confirm-download/{sid}")
def confirm_download(sid: str, body: ConfirmRequest):
    """Commit redaction and return the file for local download."""
    if not body.customer_name.strip():
        raise HTTPException(400, "Customer name is required.")
    pdf_bytes = commit_pending(sid)
    fname = build_filename(body.customer_name.strip())
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{fname}"'},
    )


@app.post("/confirm-send/{sid}")
def confirm_send(sid: str, body: ConfirmRequest):
    """Commit redaction and upload to Google Drive."""
    if not body.customer_name.strip():
        raise HTTPException(400, "Customer name is required.")

    pdf_bytes = commit_pending(sid)
    fname = build_filename(body.customer_name.strip())

    cfg = load_config().get("storage", {})
    if cfg.get("type") != "google_drive":
        raise HTTPException(400, "No external storage configured. Use download instead.")

    from googleapiclient.http import MediaIoBaseUpload

    service = get_drive_service()
    file_metadata = {"name": fname, "mimeType": "application/pdf"}
    folder_id = cfg.get("folder_id")
    if folder_id:
        file_metadata["parents"] = [folder_id]

    media = MediaIoBaseUpload(io.BytesIO(pdf_bytes), mimetype="application/pdf", resumable=True)

    try:
        result = service.files().create(
            body=file_metadata, media_body=media, fields="id,name,webViewLink",
            supportsAllDrives=True
        ).execute()
    except Exception as e:
        log.exception("Google Drive upload failed")
        raise HTTPException(502, f"Drive upload failed: {e}")

    return {
        "status": "uploaded",
        "file_id": result.get("id"),
        "file_name": result.get("name"),
        "web_link": result.get("webViewLink", ""),
    }


@app.post("/cancel-redaction/{sid}")
def cancel_redaction(sid: str):
    session = get_session(sid)
    session["pending_bytes"] = None
    return {"status": "cancelled"}


def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()

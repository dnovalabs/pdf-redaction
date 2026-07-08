"""PDF Redactor — text search + interactive area selection + preview before commit."""

import io
import uuid
from pathlib import Path

import fitz  # pymupdf
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import HTMLResponse, Response, StreamingResponse
from pydantic import BaseModel

app = FastAPI(title="PDF Redactor")

sessions: dict[str, dict] = {}

PREVIEW_DPI = 150


class Rect(BaseModel):
    page: int
    x: float
    y: float
    w: float
    h: float


class RedactRequest(BaseModel):
    rects: list[Rect] = []
    text_query: str = ""


def get_session(sid: str) -> dict:
    s = sessions.get(sid)
    if not s:
        raise HTTPException(404, "Session not found. Upload a PDF first.")
    return s


def apply_redactions_to_doc(doc: fitz.Document, rects: list[Rect], text_query: str) -> int:
    """Apply redactions to a document. Returns count of redacted items."""
    pages_touched: set[int] = set()
    count = 0

    # Area-based redaction
    for r in rects:
        if r.page < 0 or r.page >= len(doc):
            continue
        pg = doc[r.page]
        pw, ph = pg.rect.width, pg.rect.height
        pdf_rect = fitz.Rect(r.x * pw, r.y * ph, (r.x + r.w) * pw, (r.y + r.h) * ph)
        pg.add_redact_annot(pdf_rect, fill=(1, 1, 1))
        pages_touched.add(r.page)
        count += 1

    # Text-based redaction
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


@app.get("/", response_class=HTMLResponse)
def index():
    return (Path(__file__).parent / "index.html").read_text()


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
    """Render a page. If pending=true, render from the pending redacted version."""
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
    """Apply redaction to a temporary copy for preview. Does not modify the original."""
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


@app.post("/confirm-redaction/{sid}")
def confirm_redaction(sid: str):
    """Commit the pending redaction and return the file for download."""
    session = get_session(sid)
    if not session.get("pending_bytes"):
        raise HTTPException(400, "No pending redaction to confirm.")

    session["doc_bytes"] = session["pending_bytes"]
    session["pending_bytes"] = None

    fname = session["filename"].rsplit(".", 1)[0] + "_redacted.pdf"
    buf = io.BytesIO(session["doc_bytes"])
    return StreamingResponse(buf, media_type="application/pdf",
                             headers={"Content-Disposition": f'attachment; filename="{fname}"'})


@app.post("/cancel-redaction/{sid}")
def cancel_redaction(sid: str):
    """Discard the pending redaction."""
    session = get_session(sid)
    session["pending_bytes"] = None
    return {"status": "cancelled"}


def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()

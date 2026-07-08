# PDF Redactor

True PDF redaction with two modes: **draw areas** visually or **search text**. Works on scanned PDFs, stamps, images — anything on the page.

## Setup

Requires [uv](https://docs.astral.sh/uv/getting-started/installation/).

```bash
cd pdf-redactor
uv run app.py
```

Open `http://localhost:8000`.

## How it works

1. **Upload** a PDF
2. **Draw mode** — click and drag rectangles over anything to redact (white fill)
3. **Text Search mode** — find and highlight selectable text across pages
4. **Preview** — see exactly what the redacted output looks like before committing
5. **Confirm & Download** — commit the changes and download, or cancel to adjust

Redaction is permanent — pixel data under drawn areas is zeroed out, and text objects are removed.

## API

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/upload` | Upload PDF |
| `GET` | `/preview/{sid}/{page}` | Render page (supports `?pending=true` for preview) |
| `GET` | `/search/{sid}?q=` | Search text |
| `POST` | `/prepare-redaction/{sid}` | Apply to temp copy for preview |
| `POST` | `/confirm-redaction/{sid}` | Commit and download |
| `POST` | `/cancel-redaction/{sid}` | Discard preview |

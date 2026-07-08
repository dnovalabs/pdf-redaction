# PDF Redactor

True PDF redaction with visual area selection, text search, and Google Drive export.

## Setup

Requires [uv](https://docs.astral.sh/uv/getting-started/installation/).

```bash
cd pdf-redactor
uv run app.py --add-user admin yourpassword
uv run app.py
```

Open `http://localhost:8000` and sign in with the credentials you just created.

## Authentication

All routes require login. User credentials are stored (hashed with PBKDF2-SHA256) in `config.json` under `auth.users`.

**Add or update a user:**

```bash
uv run app.py --add-user USERNAME PASSWORD
```

Run this command for each user; then start the server normally. Sessions last 7 days and are invalidated on logout.

## Google Drive Setup

1. Create a service account in Google Cloud Console
2. Enable the Google Drive API
3. Download the JSON key file as `credentials.json` into the project root
4. Share the target Drive folder with the service account email
5. Set the folder ID in `config.json`

```json
{
  "storage": {
    "type": "google_drive",
    "credentials_path": "credentials.json",
    "folder_id": "YOUR_FOLDER_ID"
  },
  "file_naming": {
    "pattern": "{customer_name}.pdf"
  }
}
```

The `{customer_name}` placeholder in the naming pattern is replaced by the value entered in the UI. The app works without Drive configured — download is always available.

## How it works

1. **Upload** a PDF
2. **Enter customer name** (required) — determines the output filename
3. **Draw** rectangles over content to redact, or **search text**
4. **Preview** the redacted result
5. **Send to Drive** (default when configured) or **Download**

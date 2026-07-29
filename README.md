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

## Docker

The app ships as a container image. Secrets (`config.json`, `credentials.json`) are **never** baked into the image — they're mounted read-only at runtime.

**Local development** (with hot reload and a `/health` healthcheck):

```bash
docker compose up --build
```

This mounts your local `config.json` and `credentials.json`. Open `http://localhost:8000`.

**Build and run standalone:**

```bash
docker build -t pdf-redactor:0.1.0 .
docker run -p 8000:8000 \
  -v $(pwd)/config.json:/app/config.json:ro \
  -v $(pwd)/credentials.json:/app/credentials.json:ro \
  pdf-redactor:0.1.0
```

Tag the image with the version from `pyproject.toml` — never deploy `latest` to anything shared.

**Managing users** writes to `config.json`, so run it against a writable copy on the host rather than the read-only mount:

```bash
uv run app.py --add-user USERNAME PASSWORD
```

### Health endpoints

- `GET /health` — liveness: the process is up (no dependency checks).
- `GET /ready` — readiness: config loads, and when Google Drive is configured, `credentials.json` is present.
- `GET /version` — the running application version, read from `pyproject.toml`.

### Deployment notes

- **Single replica only.** Sessions and auth tokens are held in memory, so running more than one replica drops uploads and logs users out at random. Move that state to shared storage before scaling horizontally.
- **Secrets.** In Kubernetes, mount `config.json` / `credentials.json` as a `Secret`. Nothing sensitive belongs in the image.

## Versioning

Follows [Semantic Versioning](https://semver.org). The version lives in **one place** — `[project].version` in `pyproject.toml` — and is read at runtime via `_version.py` (installed metadata, falling back to `pyproject.toml`). Changes are recorded in `CHANGELOG.md` ([Keep a Changelog](https://keepachangelog.com) format).

To cut a release:

1. Bump `version` in `pyproject.toml`.
2. Add a `## [X.Y.Z] - YYYY-MM-DD` entry to `CHANGELOG.md`.
3. Commit both together, then `git tag vX.Y.Z && git push --tags`.
4. Build and tag the image with the same number: `docker build -t pdf-redactor:X.Y.Z .`

## How it works

1. **Upload** a PDF
2. **Enter customer name** (required) — determines the output filename
3. **Draw** rectangles over content to redact, or **search text**
4. **Preview** the redacted result
5. **Send to Drive** (default when configured) or **Download**

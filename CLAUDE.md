# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the server

```bash
# Install dependencies (no requirements.txt yet — install manually)
pip install fastapi uvicorn sqlalchemy pydantic[email] python-multipart

# Run in development (from repo root)
uvicorn app.main:app --reload --port 8000

# Run in production
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The server auto-creates the SQLite database (`fiscalai.db`) on first run.

## Environment variables

| Variable | Default | Purpose |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./fiscalai.db` | SQLAlchemy connection string |
| `ALLOWED_ORIGINS` | `http://localhost:3000,...` | Comma-separated CORS origins |
| `ADMIN_API_KEY` | *(none)* | Required to call any `GET /api/*` endpoint |

## API docs

- Swagger UI: `http://localhost:8000/api/docs`
- ReDoc: `http://localhost:8000/api/redoc`

## Architecture

**Backend** — FastAPI app in `app/`, served at port 8000. Handles all API routes and also serves the static frontend.

**Frontend** — Vanilla HTML/CSS/JS in `static/`. No build step. FastAPI mounts `static/assets` and `static/pages` as static directories and serves `static/index.html` at `/`.

### Request flow

1. Browser hits FastAPI.
2. API routes (`/api/*`) are handled by route handlers in `app/main.py`.
3. All other paths fall through to the catch-all `serve_static` handler which returns the matching file from `static/` or falls back to `index.html`.

### Data layer

- `app/models.py` — SQLAlchemy ORM models: `DemoLead`, `HeroLead`, `ContactForm`.
- `app/schemas.py` — Pydantic schemas for request validation and response serialization.
- `app/database.py` — SQLAlchemy engine, `SessionLocal`, and `get_db` dependency.
- Tables are created automatically at startup via `Base.metadata.create_all`.

### Admin protection

GET endpoints are guarded by `_require_admin()` in `main.py`. Pass `X-Admin-Key: <ADMIN_API_KEY>` header. If `ADMIN_API_KEY` env var is unset, the endpoint returns 503.

### Duplicate handling

POST `/api/leads/demo` and POST `/api/leads/hero` silently return `ok: true` on duplicate email (no error), to avoid blocking the user from reaching the demo.

### IP tracking

All lead/contact records store the client IP via `get_client_ip()`, which reads `X-Forwarded-For` first (for Fly.io / Cloudflare proxy support).

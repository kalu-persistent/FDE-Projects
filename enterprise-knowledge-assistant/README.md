# Enterprise Knowledge Assistant + UI

## Run

1. Put API keys in `backend/.env`.
2. Optional: put policy documents in `backend/data/documents` and run ingestion from your prior project.
3. Start all services:

```bash
docker compose up --build
```

- Chat UI: http://localhost:3000
- FastAPI Swagger: http://localhost:8000/docs
- API health: http://localhost:8000/health

## Networking and CORS

The browser calls `/api/query` on port 3000. The frontend Nginx container proxies `/api/*` to `http://api:8000/*` over Docker Compose networking, so normal UI traffic is same-origin and avoids browser CORS problems. FastAPI CORS is also explicitly configured for `http://localhost:3000` and `http://127.0.0.1:3000` for direct browser-to-API development calls.

Do **not** use `localhost:8000` as the proxy target inside the frontend container. In Docker, `localhost` means the frontend container itself; the backend is reached by service name `api:8000`.

## Demo users

1 Admin, 2 HR, 3 Manager, 4 employee, 5 employee. Select the identity in the UI sidebar. The UI sends it as `X-User-Id`. This is demo authentication only.

## Seed fix

`backend/app/database.py` includes `db.flush()` after employees are added so PostgreSQL parent employee rows exist before attendance/leave FK rows are inserted.

If an older broken dev database volume exists and contains no needed data:

```bash
docker compose down -v
docker compose up --build
```

`down -v` deletes the PostgreSQL development volume.

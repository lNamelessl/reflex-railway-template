# Reflex on Railway — pure-Python full-stack starter

[![Deploy on Railway](https://railway.com/button.svg)](https://railway.app/new?github_url=https://github.com/OWNER/reflex-railway-template)

Deploy a production-mode [Reflex](https://reflex.dev) app — **full-stack web apps written entirely in Python** — to Railway in one click. No JavaScript to write, no Node server to babysit at runtime.

- **Framework**: [Reflex 0.9.11](https://pypi.org/project/reflex/) (pinned), Python 3.13
- **Packaging**: official Reflex production one-port pattern ([docker-example/production-one-port](https://github.com/reflex-dev/reflex/tree/main/docker-example))
- **Demo app**: a small task board proving the full framework loop — browser event → Python state handler → SQLite write → UI refresh

## What one deploy gives you

A single Railway service running one container with:

| Piece | Role | Listens on |
|---|---|---|
| **Caddy** | Serves the statically exported frontend; reverse-proxies backend routes | `$PORT` (Railway-assigned, public) |
| **Reflex backend** | Event handlers + WebSocket (`/_event/*`), gunicorn/uvicorn in prod mode | 8000 (internal) |
| **Redis** | Reflex prod-mode state sync | in-container |
| **SQLite** | Demo app persistence via `rx.Model` (swap for Postgres in your app) | in-container |

Healthcheck: `GET /ping` → `pong` (proxied through Caddy to the backend).

## Deploy

1. Click the deploy button above (Hobby plan recommended — see [Build memory](#build-memory)).
2. Wait for the build (~5–8 min; the frontend export compiles the JS app once at build time).
3. Open the public domain. Add a task, toggle it, delete it — events round-trip to the Python backend and persist to SQLite (survive reloads and restarts).

## Build memory

The only memory-heavy phase is the **build**: Reflex runs bun + Vite to compile the frontend inside the Docker build. Railway's **Free plan caps services at 0.5 GB**, which can OOM during the export — use the **Hobby plan ($5/mo, 8 GB per service)**. At **runtime** the app is light: the frontend is served as static files (no Node process), so the container idles at a few hundred MB.

## Replace the demo app with yours

The demo lives in two files: `reflex_railway/__init__.py` (app + page registration) and `reflex_railway/tasks.py` (model, state, UI). To ship your own app:

```bash
pip install "reflex==0.9.11"   # match requirements.txt
reflex init                    # scaffold a new app package, or write your own
```

- Replace the `reflex_railway` package contents with your pages/state (keep the package name in sync with `app_name` in `rxconfig.py`).
- If you use `rx.Model` tables, commit the `alembic/` directory — the container start command runs `reflex db migrate` when it exists.
- **Do not set `api_url` in `rxconfig.py`** — the Dockerfile bakes `REFLEX_API_URL=http://localhost:$PORT` at export time; the compiled frontend rewrites localhost to the page origin (wss/https behind TLS). A hardcoded domain would break on deploy.
- Delete the demo's SQLite bits if you switch to Postgres (`REFLEX_DB_URL` env var), and run migrations in the container start command.

## Environment variables

None are required — the template is zero-config out of the box:

| Variable | Default | Purpose |
|---|---|---|
| `PORT` | set by Railway | Public port Caddy listens on |
| `API_URL` | unset | Only for direct/non-TLS access; leave unset behind Railway's TLS edge |
| `REFLEX_REDIS_URL` | `redis://localhost` | Prod state sync (in-container) |
| `REFLEX_DB_URL` | SQLite file | Set to a Postgres URL to move off SQLite |

## Troubleshooting

- **Build fails with memory/Killed errors** → you're on the Free plan (0.5 GB). Upgrade to Hobby, or trim frontend dependencies.
- **App loads but events never fire** → the frontend can't reach the backend. Check the browser console for websocket errors to `/_event/*`; make sure you didn't set `api_url` in `rxconfig.py`.
- **`reflex db migrate` fails at start** → your app has models but no `alembic/` directory; run `reflex db init` locally and commit it.
- **Version drift** → Reflex moves fast; bump `reflex==` in `requirements.txt` one version at a time and redeploy — the backend and the compiled frontend must come from the same version.

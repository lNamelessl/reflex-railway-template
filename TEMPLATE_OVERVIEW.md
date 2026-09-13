# Reflex on Railway — full-stack web apps in pure Python

[![Deploy on Railway](https://railway.com/button.svg)](https://railway.com/deploy/reflex-railway-template)

Deploy a production-mode [Reflex](https://reflex.dev) app in one click. Reflex builds full-stack web apps **entirely in Python** — UI components, state, and event handlers — with no JavaScript to write. This template ships a working demo (a task board with SQLite persistence) so you can verify the interactive round-trip the moment the deploy finishes, then swap in your own app.

**What's inside**

- [Reflex 0.9.11](https://pypi.org/project/reflex/) (pinned) on Python 3.13
- Official Reflex production one-port pattern ([docker-example/production-one-port](https://github.com/reflex-dev/reflex/tree/main/docker-example)): one container, one public port
- **Caddy** serves the statically exported frontend and reverse-proxies backend routes (`/_event`, `/ping`, `/_upload`) to the Reflex backend on an internal port
- **Redis** runs in-container for prod-mode state sync; **SQLite** persists the demo's data (swap for Postgres in your app)

**Zero configuration** — no deploy-form variables, no secrets to set. Railway assigns the public port and domain automatically; the compiled frontend reaches the backend through the same origin (websocket over TLS handled by Caddy).

**Plan guidance (build memory)**: the only memory-heavy phase is the Docker build, where Reflex compiles the frontend with bun + Vite. Railway's Free plan caps services at 0.5 GB and can OOM during this build — use the **Hobby plan ($5/mo, 8 GB per service)**. At runtime the app is light: the frontend is static files, so there is no Node process and the container idles at a few hundred MB.

**Replace the demo with your app**: edit `reflex_railway/` (one page file + one state/model file), keep `reflex==0.9.11` pinned in `requirements.txt`, commit your `alembic/` directory if you add `SQLModel` tables (the container start command runs `reflex db migrate`), and never set `api_url` in `rxconfig.py` (the Dockerfile bakes a localhost URL that the frontend rewrites to its own origin). Full instructions in the repo README.

**Healthcheck**: `GET /ping` → `pong`.

**Troubleshooting**

- *Build fails with Killed / out-of-memory* → you're on the Free plan (0.5 GB build cap). Upgrade to Hobby.
- *App loads but events don't fire* → the frontend can't reach the backend; check the browser console for websocket errors to `/_event` and make sure `api_url` isn't set in `rxconfig.py`.
- *"Connection Error" icon flashes at startup* → the first websocket attempt can race the backend's event processor on a fresh boot; it self-clears within seconds.
- *Version drift* → Reflex moves fast; bump `reflex==` one version at a time — the compiled frontend and backend must come from the same version.

# Deploy and Host

## About Hosting

One Railway service runs the entire stack in a single Docker container derived from Reflex's official production one-port Dockerfile: Caddy on Railway's assigned `$PORT` serving the exported static frontend and proxying `/_event`, `/ping`, and `/_upload` to the Reflex backend (gunicorn/uvicorn in prod mode) on an internal port; an in-container Redis for prod state sync; and a SQLite database file for the demo app. Migrations run in the container start command (`reflex db migrate` when an `alembic/` directory is present). Railway's edge terminates TLS, so the browser reaches the backend through the same public origin with websocket over TLS. Expected usage for the demo is a few hundred MB of RAM; the build (frontend compile) is the memory-heavy step — see the plan guidance above.

## Why Deploy

Writing a Reflex app is pure Python, but running it in production means coordinating a compiled frontend, a websocket backend, state sync, and TLS — and getting each piece's URL configuration wrong breaks events silently. This template does that wiring once, per Reflex's own documented production pattern, so the one-click deploy gives you a working production setup: correct port handling, same-origin websocket routing, migrations at boot, and a healthcheck endpoint. You verify interactivity in the browser in the first minute instead of debugging event routing for an afternoon.

## Common Use Cases

- Internal tools and dashboards where Python teams want UI + backend without JavaScript
- Data apps that need interactive state, forms, and charts with a Python-only stack
- MVPs and prototypes that should look and behave like full-stack web apps from day one
- AI/ML product frontends wrapping Python models, with the model code living next to the UI
- A starting point for Reflex + Postgres apps (swap the demo's SQLite for `REFLEX_DB_URL`)

## Dependencies for

### Deployment Dependencies

- **Docker image built from this repo** (public GitHub repo `lNamelessl/reflex-railway-template`, pinned to `reflex==0.9.11` / Python 3.13)
- **Caddy** (installed in-image) — static frontend serving and backend reverse proxy
- **Redis server** (installed in-image) — Reflex prod-mode state sync
- **SQLite** (in-image) — demo app persistence; optional swap for a Railway Postgres/MySQL plugin via `REFLEX_DB_URL`
- No external environment variables are required: Railway's assigned `$PORT` and public domain are picked up automatically

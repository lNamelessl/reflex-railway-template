"""Reflex config for the Railway starter template.

In production the app runs in one-port mode: Caddy serves the exported static
frontend and reverse-proxies backend routes (`/_event/*`, `/ping`, `/_upload`)
to the Reflex backend on localhost:8000, all behind a single port.

See the official one-port Docker examples:
https://github.com/reflex-dev/reflex/tree/main/docker-example
"""

import reflex as rx

config = rx.Config(
    app_name="reflex_railway",
    # Backend listens internally on 8000; Caddy proxies to it.
    backend_port=8000,
    # Demo app persists to SQLite in-container. Set REFLEX_DB_URL to move to
    # Postgres or another database without touching code.
    db_url="sqlite:///reflex.db",
    # Explicit Radix Themes enablement (implicit enablement is deprecated in
    # 0.9 and removed in 1.0).
    plugins=[rx.plugins.RadixThemesPlugin()],
)

# NOTE on api_url: it is deliberately NOT set here. The Dockerfile bakes
# REFLEX_API_URL=http://localhost:$PORT at frontend-export time; the compiled
# frontend rewrites any localhost endpoint to window.location.hostname (with
# wss/https and no port when the page is served over TLS), so the browser
# reaches the backend through the same public origin Caddy serves. Never set a
# real domain here — it would be baked into the build and break on deploy.

# Single-container Reflex app for platforms that terminate TLS at one port
# (Railway, Render, Heroku, GCP). Derived from the official
# reflex-dev/reflex docker-example/production-one-port Dockerfile.
#
# Architecture: Caddy serves the statically exported frontend from /srv and
# reverse-proxies backend routes (/_event/*, /ping, /_upload) to the Reflex
# backend on localhost:8000. Redis runs in-container for prod state sync.
# All traffic enters through the single $PORT.

# If the service expects a different port, provide it here (f.e Render expects port 10000)
ARG PORT=8080
# Only set for local/direct access. When TLS is used, the API_URL is assumed to be the same as the frontend.
ARG API_URL

FROM python:3.13 AS builder

RUN mkdir -p /app/.web
RUN python -m venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# Install pinned python requirements (reflex==0.9.11)
COPY requirements.txt .
RUN pip install -r requirements.txt

# Install reflex helper utilities like bun/node
COPY rxconfig.py ./
RUN reflex init

# Install pre-cached frontend dependencies (if exist)
COPY *.web/bun.lockb *.web/package.json .web/
RUN if [ -f .web/bun.lockb ]; then cd .web && ~/.local/share/reflex/bun/bin/bun install --frozen-lockfile; fi

# Copy local context to /app inside container (see .dockerignore)
COPY . .

ARG PORT API_URL
# Download remaining npm dependencies and compile the frontend.
# The localhost API URL is intentional: the compiled frontend rewrites
# localhost endpoints to the page's own origin (wss/https behind TLS), so the
# browser reaches the backend through the same public origin.
RUN REFLEX_API_URL=${API_URL:-http://localhost:$PORT} reflex export --frontend-only --no-zip \
    && mv .web/build/client/* /srv/ && rm -rf .web

# Final image with only necessary files
FROM python:3.13-slim

# Install Caddy and redis server inside image
RUN apt-get update -y && apt-get install -y caddy redis-server && rm -rf /var/lib/apt/lists/*

ARG PORT API_URL
ENV PATH="/app/.venv/bin:$PATH" PORT=$PORT REFLEX_API_URL=${API_URL:-http://localhost:$PORT} REFLEX_REDIS_URL=redis://localhost PYTHONUNBUFFERED=1

WORKDIR /app
COPY --from=builder /app /app
COPY --from=builder /srv /srv

# Needed until Reflex properly passes SIGTERM on backend.
STOPSIGNAL SIGKILL

EXPOSE $PORT

# Apply migrations before starting the backend (runs reflex db migrate only
# when the alembic directory exists — i.e. your app has rx.Model tables).
# Healthcheck target: GET /ping returns "pong" through Caddy -> backend.
CMD [ -d alembic ] && reflex db migrate; \
    caddy start && \
    redis-server --daemonize yes && \
    exec reflex run --env prod --backend-only

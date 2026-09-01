# Docker Guide

## Development

```bash
# Start the app with hot-reload
docker compose up

# Rebuild after changing dependencies
docker compose build
docker compose up

# Stop
docker compose down
```

That's it! After a build, the app (API and the React UI) runs at **http://localhost:8001**. Frontend hot-reload still uses `./scripts/dev_deploy.sh`.

---

## Hot-Reload

When you edit files in `src/`, the container auto-reloads within 1-2 seconds.

If hot-reload isn't working:
```bash
docker compose down
docker compose build
docker compose up
```

---

## Environment Variables

None of these are required for local development. `Settings` has defaults, and the development Compose file still expects a `.env` file to exist (an empty one is enough). Nested names use `SECTION__FIELD`:

```bash
DB__URL=sqlite:///data/db/mathwizard.db

WEB__SESSION_TTL_DAYS=7
WEB__SESSION_COOKIE_NAME=mw_session
WEB__COOKIE_SECURE=false

BOOTSTRAP__USERNAME=niels
BOOTSTRAP__PASSWORD=root
BOOTSTRAP__STUDENT_USERNAMES=["student1","student2"]
BOOTSTRAP__STUDENT_PASSWORD=student
```

Sessions are opaque tokens stored in the database. There is no session signing secret.

For production, set `WEB__COOKIE_SECURE=true` so browsers only send the session cookie over HTTPS.

---

## Production (Cloudflare Tunnel)

Create `env.prod` next to the compose files. Docker Compose requires the file to exist. Add the Cloudflare tunnel token and any production overrides:

```bash
TUNNEL_TOKEN=eyJ...

DB__URL=postgresql://mathwizard:change-me@host.docker.internal:5432/mathwizard

WEB__COOKIE_SECURE=true
BOOTSTRAP__USERNAME=niels
BOOTSTRAP__PASSWORD=change-me
BOOTSTRAP__STUDENT_USERNAMES=["student1","student2"]
BOOTSTRAP__STUDENT_PASSWORD=change-me
```

The production container does not run Postgres. The Mini already runs it as a
host daemon. From inside Docker, `localhost` is the container, so the URL host
must be `host.docker.internal`. `./scripts/dev_deploy.sh` does not read
`env.prod` and keeps the default SQLite file.

On first start the app applies Alembic migrations to that database, then seeds
bootstrap users and practice YAML. If the container cannot connect, confirm
Postgres is listening on `127.0.0.1:5432` and that `pg_hba.conf` allows the
`mathwizard` user from Docker's bridge (on Docker Desktop this is typically
treated as a local connection).

`WEB__COOKIE_SECURE` is also forced to `true` in `docker-compose.prod.yml`.

The production image builds the React app and FastAPI serves it from the same origin as `/api` and `/auth`. In the Cloudflare dashboard (Zero Trust → Networks → Tunnels), create a tunnel, copy the token into `TUNNEL_TOKEN`, and add a public hostname whose origin is **`http://app:8080`**. Use the Docker service name `app`, not `localhost` — `cloudflared` runs in its own container. The health check is `/health`.

```bash
docker compose -f docker-compose.prod.yml up -d
docker compose -f docker-compose.prod.yml logs -f
docker compose -f docker-compose.prod.yml down
```

The app is not published on the host. Traffic reaches it only through the tunnel.


# MathWizard

MathWizard is a FastAPI and React app for finding and practicing math exercises. The backend stores question records with explicit metadata, seeds practice questions from YAML, and exposes a typed practice-question API. The frontend renders the practice flow with MathJax and exercise metadata.

## Quick Start

Install backend and frontend dependencies:

```bash
uv sync --extra dev
cd frontend && npm install
```

Optional local settings can go in `.env`. By default, MathWizard uses `sqlite:///data/db/mathwizard.db`, seeds the `root` user with password `root`, and uses non-secure cookies for local development.

Start both local dev servers with hot reload:

```bash
./scripts/dev_deploy.sh
```

The backend runs at http://localhost:8001 and the frontend runs at http://localhost:3001.

You can also start them separately:

```bash
uv run uvicorn mathwizard.app.main:app --reload --host 0.0.0.0 --port 8001
cd frontend && npm run dev -- --host 0.0.0.0 --port 3001
```

## Docker

Development and production Compose setups are documented in [docs/docker.md](docs/docker.md).

```bash
# API + built UI at http://localhost:8001
docker compose up

# Production behind a Cloudflare Tunnel
docker compose -f docker-compose.prod.yml up -d
```

Production reads `TUNNEL_TOKEN` from `env.prod`. FastAPI serves the built React app from the same origin. In the Cloudflare dashboard, point the public hostname at `http://app:8080`.

## Authentication

MathWizard uses first-party cookie authentication. On startup, the backend seeds a bootstrap user from `.env` settings:

```text
BOOTSTRAP__USERNAME=niels
BOOTSTRAP__PASSWORD=root
WEB__SESSION_TTL_DAYS=7
WEB__SESSION_COOKIE_NAME=mw_session
WEB__COOKIE_SECURE=false
```

The seeded classroom teacher is `BOOTSTRAP__USERNAME` (default `niels`). If a local `.env` still sets `BOOTSTRAP__USERNAME=root`, update it; an existing SQLite `root` user is not renamed. Seeded and existing students remain assigned to their current teacher, while new signups attach to `BOOTSTRAP__USERNAME` (`niels` by default). Changing that username on an existing database creates two teachers unless operators deliberately keep `.env` or `env.prod` aligned with the existing teacher.

Login happens through `POST /auth/login`. Successful login sets an `HttpOnly` cookie named by `WEB__SESSION_COOKIE_NAME`. The frontend restores sessions with `GET /auth/me` and logs out with `POST /auth/logout`.

Students create an account with `POST /auth/signup` (`username`, `password`, `password_confirm`). That attaches them to the bootstrap teacher, sets the same session cookie as login, and returns `role: "student"`.

For production, set `WEB__COOKIE_SECURE=true` so browsers only send the session cookie over HTTPS.

## Practice Questions

Practice questions live in `data/questions/practice/`. Each `p*.yaml` file is a complete question definition and must include its own metadata instead of relying on folder names:

```yaml
source: practice
topic: derivatives
tags:
- differentieren
- machtsregel
title: Machtsfuncties
stem: Bepaal de afgeleide van de volgende functies.
parts:
- text: \(f(x) = 3x^7 - 2x^5 + x^3\)
  points: 3
```

On startup, the backend seeds practice questions from this directory into the configured database. Missing practice seed data fails loudly so the app does not silently serve an empty practice API.

## API

Health check:

```bash
curl http://localhost:8001/health
```

Practice questions by topic:

```bash
curl "http://localhost:8001/api/v1/practice/derivatives"
```

The practice endpoint returns a generic question list response:

```json
{
  "source": "practice",
  "topic": "derivatives",
  "questions": []
}
```

Questions are sorted by difficulty by default. Disable that sorting with:

```bash
curl "http://localhost:8001/api/v1/practice/derivatives?sort_by_difficulty=false"
```

## Development Checks

Run backend tests:

```bash
uv run --extra dev pytest -m "not db"
uv run --extra dev pytest
```

Run frontend build and lint:

```bash
cd frontend && npm run build && npm run lint
```

## Project Layout

```text
src/mathwizard/
  app/       FastAPI app, dependencies, and routes
  db/        SQLAlchemy tables, repositories, unit of work, and migrations
  models/    Domain entities and API request/response models
  ports/     Repository and unit-of-work protocols
  services/  Bootstrap, auth, question, and figure service logic
frontend/                 React, TypeScript, and Vite frontend
data/                     Tracked practice question YAML; local SQLite files in data/db/
tests/                    Backend unit and route tests
docker-compose.yml        Development stack with hot-reload
docker-compose.prod.yml   Production stack with Cloudflare Tunnel
```

## Layering

- `models/domain/` — pydantic entities and drafts. No storage or HTTP concerns.
- `models/api/` — request/response DTOs. FastAPI's `response_model` filters domain
  entities down to these shapes, so routes return entities directly.
- `ports/` — abstract repository and `UnitOfWork` protocols, one narrow slice
  per service.
- `db/` — the only package that imports SQLAlchemy: tables, concrete repositories,
  `SqlAlchemyUnitOfWork`, and Alembic helpers.
- `services/` — workflow logic. Each method takes a `UnitOfWork` slice, opens exactly
  one `with uow:` block, and calls `uow.commit()` for writes. A service method never
  calls another service's transactional method.

Schema changes are Alembic migrations: edit `db/tables/`, run
`uv run alembic revision --autogenerate -m "..."`, then `uv run python -m mathwizard.cli db upgrade`.
`tests/test_db/test_migrations.py` fails if migrations drift from the table metadata.

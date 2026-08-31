# Testing Guide

This document explains how to safely test the MathWizard web application without relying on manual clicking in Docker.

## Testing Options (Best to Use)

### 1. 🚀 Local Development Server (Fastest)

Run the app locally without Docker for rapid iteration:

```bash
./scripts/dev-local.sh
```

**Advantages:**
- Instant reload on code changes
- Faster startup (no Docker overhead)
- Direct access to your local data
- Easy debugging with print statements/breakpoints

**When to use:**
- Active development
- UI tweaks and styling
- Quick feature testing

---

### 2. ✅ Automated Tests

Install extra deps, then pick a loop:

```bash
uv sync --extra dev

# Fast inner loop — fakes only, no SQLite
uv run pytest -m "not db"

# Adapter tests — real SQLAlchemy repositories, UoW, migrations
uv run pytest -m db

# Full suite
uv run pytest
```

### What runs where

| Layer | Location | Persistence |
| --- | --- | --- |
| Domain / ports / fakes | `tests/test_models`, `tests/test_ports`, `tests/test_fakes` | none |
| Services | `tests/test_services` | `FakeUnitOfWork` |
| HTTP routes | `tests/test_app` | `FakeUnitOfWorkFactory` via `tests/app_client.py` |
| Bootstrap | `tests/test_bootstrap_*.py` | `FakeUnitOfWorkFactory` |
| SQLAlchemy adapters | `tests/test_db` (marked `db`) | temp SQLite file |

HTTP and bootstrap tests use real service classes. They must not construct `SqlAlchemyUnitOfWorkFactory`. Transaction rollback, unique constraints, and Alembic drift stay in `tests/test_db`.

Auth tests inject `FakePasswordHasher` (`fake:{plain}`). Production keeps `BcryptPasswordHasher`. One bcrypt round-trip lives in `tests/test_services/test_auth.py::test_bcrypt_password_hasher_round_trip`.

Fake units of work do not roll back in-memory writes. `commit()` / `rollback()` only flip `uow.committed`. Prove real transactions in `tests/test_db/test_unit_of_work.py`.

---

### 3. 🐳 Docker Testing (Pre-Deployment)

Test the exact container that will be deployed:

```bash
# Build and start
docker compose up

# Or rebuild if dependencies changed
docker compose build
docker compose up

# Stop
docker compose down
```

**Advantages:**
- Tests production environment
- Catches Docker-specific issues
- Validates deployment configuration

**When to use:**
- Final check before deployment
- Testing environment-specific behavior
- Validating Docker configuration

---

## Testing Workflow (Recommended)

### During Development

```bash
# 1. Start local dev server in one terminal
./scripts/dev-local.sh

# 2. Make changes to code
# 3. Browser auto-refreshes (if using live-reload extension)
# 4. Or manually refresh: http://localhost:8001
```

### Before Deploying

```bash
# 1. Run all tests
uv run pytest -xvs

# 2. Test in Docker
docker compose build
docker compose up

# 3. Manual smoke test at http://localhost:8001
# 4. Stop Docker
docker compose down

# 5. Deploy
./scripts/deploy.sh
```

---

## Writing New Tests

### Example: Test API Endpoint

```python
def test_api_search_endpoint(self, client):
    """Search API should return results."""
    response = client.post("/api/v1/search", json={"query": "test query"})
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
```

---

## Debugging Tips

### Check Logs

```bash
# Local server logs
# Output is in your terminal

# Docker logs
docker compose logs -f

# Or for a specific container
docker compose logs -f app
```

### Interactive Debugging

When running locally (`./scripts/dev-local.sh`), you can use:

```python
# In your route handler
import pdb

pdb.set_trace()
```

Or use your IDE's debugger:
- VSCode: Set breakpoint, run "Python: Debug"
- PyCharm: Set breakpoint, run debug configuration

---

## Common Issues

### Issue: Tests fail with "ModuleNotFoundError"

**Solution:**
```bash
# Sync dev dependencies
uv sync --group dev
```

### Issue: Local server can't find templates

**Solution:**
Make sure you're running from the project root:
```bash
cd /path/to/mathwizard
./scripts/dev-local.sh
```

### Issue: Docker container missing dependencies

**Solution:**
```bash
# Rebuild the image
docker compose build
docker compose up
```

### Issue: Port 8001 already in use

**Solution:**
```bash
# Find and kill the process
lsof -ti:8001 | xargs kill -9

# Or use a different port
uv run uvicorn mathwizard.app.main:app --reload --port 8002
```

---

## CI/CD Integration

Add to your CI pipeline (GitHub Actions example):

```yaml
# .github/workflows/test.yml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: |
          pip install uv
          uv sync --group dev
      
      - name: Run tests
        run: uv run pytest -xvs
```

---

## Summary

**Don't rely on manual Docker testing!**

Instead:
1. **Develop** with `./scripts/dev-local.sh`
2. **Test** with `uv run pytest -m "not db"`
3. **Verify** with Docker before deploying

This workflow is:
- ✅ Faster
- ✅ Safer
- ✅ More maintainable
- ✅ Automatable


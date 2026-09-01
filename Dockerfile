FROM node:22-alpine AS frontend

WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock* README.md ./
COPY src/ ./src/
COPY alembic.ini ./
COPY migrations/ ./migrations/

RUN uv sync --frozen --no-dev

COPY data/ ./data/
COPY --from=frontend /frontend/dist ./frontend/dist

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "mathwizard.app.main:app", "--host", "0.0.0.0", "--port", "8000"]

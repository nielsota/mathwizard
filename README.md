# Exercise Finder (MathWizard)

Quick command reference using the `mw` CLI.

## Data layout

Questions data is organized under `data/questions/`:

```
data/questions/
  exams/
    raw/        # question images (qNN/pages, qNN/figures)
    processed/  # extracted YAML (qN.yaml per exam)
    curated/    # formatted YAML (qN.yaml per exam)
    pdfs/       # source exam PDFs
  practice/
    curated/    # practice sets (_meta.yaml + pN.yaml)
```

## Workflow Steps

### 1. Extract questions from exam images

Parse exam images and compile to JSONL:

```bash
uv run mw extract from-images --exam-dir data/questions/exams/raw/VW-1025-a-18-1-o
uv run mw extract from-images --exam-dir data/questions/exams/raw/VW-1025-a-18-2-o
uv run mw extract from-images --exam-dir data/questions/exams/raw/VW-1025-a-19-1-o
```

This writes to `data/questions/exams/processed/` by default.

### 2. Create and populate vector store

**Create vector store (do once):**
```bash
uv run mw vectorstore create --name examstore24122025
```

Note the returned vector store ID (e.g., `vs_694b9b4403e881918fd7b5c04a301771`)

**Add extracted questions to vector store:**
```bash
uv run mw vectorstore add 
```

Processes all YAML files in `data/questions/exams/processed/` by default.

### 3. Query and use

**CLI search:**
```bash
uv run mw vectorstore fetch --vector-store-id <INSERT_ID> --query "parametric equations" --exam-dir data/questions/exams/raw/VW-1025-a-18-1-o
```

**Web UI (recommended):**
```bash
uv run mw ui start --vector-store-id <INSERT_ID> --exams-root data/questions/exams/raw
```

Access at http://localhost:8000 for interactive search with image display.

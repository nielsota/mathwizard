---
name: servicebox-processor-qa
description: Manually triggered skill that checks if the current ServiceBox approach is able to extract the chunks from a document type properly, and outputs a recap of the types where it doesn't
---

# ServiceBox Processor QA

## Input

The user provides:
1. **Folder path** — directory containing PDF documents
2. **Pattern** — regex or natural language description to select which PDFs to test

## Workflow

### 1. Prepare the pattern

If the user provides natural language (e.g. "annual reports"), convert it to a suitable regex for filename matching (e.g. `annual.*report|informe.*anual`).
If they provide a regex, use it directly.

### 2. Find matching documents

```bash
uv run python .claude/skills/servicebox-processor-qa/utils.py find "<folder>" "<regex_pattern>" --limit 3
```

This prints one absolute path per line.

### 3. Ask the user to confirm

**STOP and ask the user** before proceeding. Show the matched document names and ask if they look correct and whether to proceed. Use the AskUserQuestion tool. Only continue once the user confirms.

### 4. Run the QA pipeline

Pass the confirmed document paths to the `run` sub-command:

```bash
uv run python .claude/skills/servicebox-processor-qa/utils.py run "<path1>" "<path2>" "<path3>" --output-dir /tmp/servicebox-qa
```

Each run creates a **timestamped sub-folder** (e.g. `run_20260326_143012/`) so concurrent or repeated runs never collide. The script prints the run directory path — note it down as `<run_dir>`.

This:
1. Runs `ServiceBoxProcessor` (GPT-4o, concurrent) on each document
2. Renders each page as a PNG image
3. Uses an LLM (concurrent) to compare each extracted chunk against its page image
4. Saves per document (under `<run_dir>/<stem>/`):
   - `page_<N>.json` — per-page extracted text + comparison result
   - `page_<N>.png` — images of problematic pages only
5. Saves `<run_dir>/results.json` — full QA comparison results

### 5. Read the results

Read `<run_dir>/results.json`. For each document, check the `pages_with_issues` array. Each entry contains:
- `page_number` — which page
- `ok` — always false for issues
- `issues` — list of problem descriptions
- `severity` — "minor" or "major"
- `page_description` — what the LLM thinks the page contains

### 6. Inspect problematic pages

For each page with issues, read **both** files side by side:
- **Image**: `<run_dir>/<stem>/page_<N>.png` — the actual page render
- **JSON**: `<run_dir>/<stem>/page_<N>.json` — contains `extracted_text` (what ServiceBox produced) and `comparison` (the LLM verdict)

By looking at the image alongside the extracted text, determine:
- Whether the issues reported by the LLM are real
- What was missed, garbled, or hallucinated in the extraction
- The visual type/layout of each problematic page
- Common patterns across problematic pages (e.g. all are tables, all have small text, all are charts)

### 7. Write the summary JSON

Based on your analysis in steps 5-6, write a JSON file at `<run_dir>/summary.json` with this structure:

```json
{
  "date": "2026-03-27 15:30 UTC",
  "documents_tested": 3,
  "total_pages": 42,
  "pages_with_issues": 5,
  "patterns": [
    {
      "pattern": "Dense financial tables",
      "pages_affected": ["doc1 p3", "doc2 p7"],
      "why_it_fails": "Small font causes OCR-like misreads ...",
      "suggested_fix": "Add a PageHandler for table-heavy pages ..."
    }
  ],
  "recommendations": [
    "Actionable recommendation 1",
    "Actionable recommendation 2"
  ],
  "problematic_pages": [
    {
      "filename": "doc1.pdf",
      "stem": "doc1",
      "page_number": 3
    }
  ]
}
```

### 8. Display the results

Print the **common failure patterns** as a markdown table in the conversation so the user sees it immediately. Also tell them where the run output and summary JSON are located.

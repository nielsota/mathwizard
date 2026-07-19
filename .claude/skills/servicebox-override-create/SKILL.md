---
name: servicebox-override-create
description: Creates a ServiceBox processor override specialized for a document type, using QA output to design filename matching and custom page handlers
---

# ServiceBox Override Creator

Creates a new `ServiceBoxProcessor` subclass specialized for a document type, using the output from the `servicebox-processor-qa` skill to inform which page types need custom handling. Validates the override against real PDFs before finalizing.

## Input

The user provides:
1. **QA run directory** — path to a QA run (e.g. `/tmp/servicebox-qa/run_20260327_...`) containing `summary.json`, `results.json`, and per-document folders
2. **Filename pattern** — regex for matching documents (e.g. `^XX-.+\.pdf$`)
3. **Processor name** — snake_case identifier for the new processor (e.g. `xx_report`). Used as the `Processor` enum value and the `processor` metadata value on chunks.
4. **PDF paths** — the same PDF files used in the QA run (for predicate testing and regression comparison)

## Workflow

### 1. Read the QA summary

Read `<run_dir>/summary.json`. Extract:
- The **patterns** array — each entry has `pattern`, `pages_affected`, `why_it_fails`, and `suggested_fix`
- The **problematic_pages** array — each entry has `filename`, `stem`, `page_number`

Also read `<run_dir>/results.json` for the full comparison results. Build a map of which pages had issues and what those issues were.

### 2. Examine problematic pages

For each problematic page listed in the summary:

1. **Read the page image**: `<run_dir>/<stem>/page_<N>.png`
2. **Read the page JSON**: `<run_dir>/<stem>/page_<N>.json` — contains `extracted_text` (what ServiceBox produced) and `comparison` (LLM verdict)

For each failure pattern from the summary, study the affected pages to understand:
- **What visual layout** the page has (table, chart, map, form, etc.)
- **What content was missed or wrong** in the extraction
- **What text markers** appear in the page's raw text (`page_text` field in page_data) that could reliably identify this page type — these become predicates

Group the problematic pages by pattern. Some patterns may share the same predicate or prompt; consolidate where it makes sense.

### 3. Design page handlers

For each distinct page type that needs custom handling, define:

#### a. Predicate

A function `_is_<type>_page(page_data: dict[str, Any]) -> bool` that returns `True` when the page matches. Predicates inspect `page_data["page_text"]` (the raw PDF text extraction) for marker strings or regex patterns.

Guidelines for predicates:
- Use case-insensitive string matching (`.lower()`) for text markers - Use compiled regex patterns (module-level `_PATTERN = re.compile(...)`) for complex patterns
- Prefer multiple markers over a single fragile one
- Test against both matching and non-matching pages from the QA run
- The predicate receives the full `page_data` dict (see below) — it can inspect `page_text`, `min_font_pt`, `links`, etc.

`page_data` keys available to predicates:
```python
{
    "page_number": int,
    "image_base64": str,
    "links": list[dict],
    "crops": list[dict],
    "min_font_pt": float,
    "base_dpi": int,
    "crop_dpi": int,
    "page_text": str,  # <-- primary source for predicate logic
}
```

#### b. Custom prompt

A prompt string (module-level constant) that tells the vision model how to extract content from this specific page type. Follow the pattern established in `ss_report.py`:

- Start with a `** Instrucciones para página de <Type>: **` header
- Describe what the page contains
- Explain how images A..N map to the page and crops
- Give numbered extraction steps (title, data, notes, source, etc.)
- End with rules (don't omit data, remove boilerplate, markdown output, etc.)

Write prompts in Spanish (matching the existing prompt convention) unless the documents are in a different language.

#### c. Prompt builder

A `build_user_prompt` function that assembles document context + the custom prompt + page number + links. Use `functools.partial` to bind the prompt constant, following the `ss_report.py` pattern:

```python
def build_user_prompt(
    prompt: str,
    document_name: str,
    document_url: str,
    page_number: int,
    links: list[dict[str, Any]],
) -> str:
    ...
```

### 4. Generate the processor file

Create `src/pdfsearch/processors/servicebox/<processor_name>.py` following the `ss_report.py` structure exactly:

```python
from __future__ import annotations

import os
import re
from functools import partial
from typing import Any

from pdfsearch.enums import ContentType, Processor
from pdfsearch.processors.servicebox.main import PageHandler, ServiceBoxProcessor
from pdfsearch.processors.servicebox.prompts import build_links_text

_FILENAME_PATTERN = re.compile(r"<user-provided-pattern>", re.IGNORECASE)

# Marker constants and regex patterns for predicates
# ...

# Prompt constants (one per page type)
# ...

def build_user_prompt(
    prompt: str,
    document_name: str,
    document_url: str,
    page_number: int,
    links: list[dict[str, Any]],
) -> str:
    """Assemble the user prompt for a specialized page."""
    if document_url:
        document_context = (
            f"Título del documento: {document_name}.\n"
            f"URL de referencia al documento: {document_url}.\n\n"
        )
    else:
        document_context = f"Título del documento: {document_name}.\n\n"

    combined = f"{document_context}{prompt}"
    combined += f"\n\nEstás procesando la página {page_number}."

    links_text = build_links_text(links)
    if links_text:
        combined += links_text

    return combined


class <ClassName>(ServiceBoxProcessor):
    """ServiceBox processor for <pattern> files with specialised page handling."""

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o",
        concurrent: bool = False,
        max_concurrent: int = 4,
    ) -> None:
        super().__init__(
            api_key=api_key,
            model=model,
            concurrent=concurrent,
            max_concurrent=max_concurrent,
            page_handlers=[
                PageHandler(
                    "<type_name>",
                    self._is_<type>_page,
                    partial(build_user_prompt, prompt=<PROMPT_CONSTANT>),
                ),
                # ... one per page type
            ],
            processor_name=Processor.<PROCESSOR_ENUM>,
        )

    @staticmethod
    def _is_<type>_page(page_data: dict[str, Any]) -> bool:
        ...

    def matches(self, content_type: ContentType, **kwargs: Any) -> bool:
        if content_type != ContentType.PDF:
            return False
        filename = kwargs.get("filename")
        if filename is None:
            return False
        return bool(_FILENAME_PATTERN.match(os.path.basename(filename)))
```

### 5. Register the processor

#### a. Add the `Processor` enum value

In `src/pdfsearch/enums.py`, add the new processor name to the `Processor` enum:

```python
class Processor(StrEnum):
    ...
    <PROCESSOR_NAME> = "<processor_name>"
```

#### b. Export from servicebox package

In `src/pdfsearch/processors/servicebox/__init__.py`, add the import and export:

```python
from pdfsearch.processors.servicebox.<module> import <ClassName>
```

And add `<ClassName>` to `__all__`.

#### c. Register in the processor registry

In `src/pdfsearch/processors/__init__.py`, import and register the new processor **after** `ServiceBoxProcessor` (so it takes priority for matching filenames). Follow the existing pattern — register inside the `try: ... except Exception:` block alongside the other ServiceBox processors.

### 6. Generate unit tests

Create `tests/processors/test_<processor_name>.py` following the `test_ss_report.py` structure. Include test classes for:

1. **TestMatches** — filename pattern matching:
   - Matches correct prefix (with path, case-insensitive)
   - Does not match other prefixes, non-PDFs, missing filename

2. **TestIs<Type>Page** — one class per page type predicate:
   - Detects pages with the marker
   - Case-insensitive detection
   - Rejects pages without the marker
   - Handles missing/empty `page_text`

3. **TestSequentialPromptSelection** — verifies correct prompts in sequential mode:
   - Matching page uses custom prompt (check for distinctive string)
   - Non-matching page uses standard prompt ("Instrucciones generales")
   - Mixed pages get correct prompts

4. **TestConcurrentPromptSelection** — same checks for concurrent mode

5. **TestChunkMetadata** — verifies `processor` and `page_type` metadata:
   - Matching page has `page_type` set
   - Non-matching page has no `page_type`
   - `processor` metadata matches the enum value

6. **TestRegistryIntegration** — verifies registry priority:
   - New processor wins for matching filename
   - `ServiceBoxProcessor` wins for non-matching filename

### 7. Run unit tests

```bash
uv run pytest tests/processors/test_<processor_name>.py -v
```

Fix any failures before proceeding.

### 8. Test predicates on real PDFs

Run the predicate testing utility against the same PDFs used in the QA run.
This does **not** call any LLM — it only runs local PDF conversion and Python predicate functions, so iteration is fast and free.

```bash
uv run python .claude/skills/servicebox-override-create/utils.py test-predicates \
    "<pdf1>" "<pdf2>" "<pdf3>" \
    --processor-module src/pdfsearch/processors/servicebox/<processor_name>.py \
    --output-dir /tmp/servicebox-override
```

Note the run directory path printed by the script.

### 9. Review matched pages and iterate

Read `<run_dir>/summary.json` from the predicate test. For each matched page:

1. **Read the page image**: `<run_dir>/<stem>/page_<N>_<handler_name>.png`
2. **Determine if the match is correct** — is this actually the page type the handler is meant for (true positive) or a wrong match (false positive)?

If **false positives** are found:
- Analyze why the predicate matched incorrectly (marker too generic, regex too broad, etc.)
- Tighten the predicate in the processor file (add additional markers, use regex instead of substring, require multiple conditions, etc.)
- Re-run unit tests: `uv run pytest tests/processors/test_<processor_name>.py -v`
- Re-run `test-predicates` with the same command
- **Repeat until no false positives remain**

If **false negatives** are suspected (expected pages not matched):
- Check the match rate — if it seems low, the predicate may be too strict
- Read the page JSON from the original QA run to see the `page_text` content
- Loosen the predicate or add alternative markers
- Re-run tests and `test-predicates`

### 10. Run handler quality comparison

Once predicates are validated, compare the override's output on handler-matched pages against the original QA baseline. This only runs the override processor and only QA-checks the pages where a handler fired — non-handler pages are identical to the base processor and are skipped entirely.

```bash
uv run python .claude/skills/servicebox-override-create/utils.py compare \
    "<pdf1>" "<pdf2>" "<pdf3>" \
    --processor-module src/pdfsearch/processors/servicebox/<processor_name>.py \
    --qa-run-dir <original_qa_run_dir> \
    --output-dir /tmp/servicebox-override
```

The `--qa-run-dir` points to the QA run from `servicebox-processor-qa` (e.g. `/tmp/servicebox-qa/run_20260327_143012`). That run's `results.json` serves as the baseline — it already contains the base processor's QA verdicts for every page, so the base does not need to be re-run.

### 11. Evaluate comparison report

Read `<run_dir>/regression_report.json`. For each handler-matched page, the report shows a `status`:

| Status | Meaning |
|--------|---------|
| `improved` | Base had issues, override is clean |
| `partially_improved` | Base had issues, override still has issues but fewer |
| `still_failing` | Both have issues, no improvement |
| `still_ok` | Base was already fine, override is still fine |
| `worsened` | Base was fine or had fewer issues, override made it worse |

**What to check**:

- **Improvements exist** — at least some handler-matched pages show `improved` or `partially_improved`. If zero, the custom prompt isn't helping — revisit it.
- **No worsened pages** — the custom prompt should not make things worse.

If **worsened** pages are found:
1. Read the per-page files in `<run_dir>/<stem>/`:
   - `page_<N>.json` — baseline vs override comparison verdicts
   - `page_<N>_base.txt` — what the base processor extracted (from QA run)
   - `page_<N>_override.txt` — what the override extracted
   - `page_<N>.png` — the page image
2. Determine root cause: prompt too aggressive? Missing instructions? Wrong extraction format?
3. Fix the prompt in the processor file
4. Re-run unit tests
5. Re-run `test-predicates` (fast, no API calls)
6. Re-run `compare` (re-checks only handler-matched pages)
7. **Repeat until no worsened pages remain**

**Still-failing pages** are not a blocker — they failed before the override too. Note them for the user as areas for future improvement.

### 12. Display results

Tell the user:
- Which processor file was created and where
- How many page handlers were defined and what they detect
- Predicate test results: match rate, number of iterations, any notable false-positive fixes
- Regression comparison verdict: improvements count, regressions count, still-failing count
- All unit tests pass
- Paths to output directories (predicate test run, regression comparison run)

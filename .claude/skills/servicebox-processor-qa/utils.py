from __future__ import annotations

import asyncio
import base64
import json
import logging
import os
import sys
import re
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from typing import Any
from dotenv import load_dotenv


import fitz
import openai
from PIL import Image
from pydantic import BaseModel

from pdfsearch.enums import ContentType
from pdfsearch.processors.servicebox import ServiceBoxProcessor

logger = logging.getLogger(__name__)

load_dotenv()


def find_matching_documents(
    folder: str,
    pattern: str,
    limit: int = 3,
) -> list[Path]:
    """Find PDF files in *folder* whose filename matches *pattern* (regex).

    Returns up to *limit* matching paths sorted alphabetically.
    """
    folder_path = Path(folder)
    if not folder_path.is_dir():
        raise FileNotFoundError(f"Folder not found: {folder}")

    regex = re.compile(pattern, re.IGNORECASE)
    matches: list[Path] = []

    for pdf in sorted(folder_path.rglob("*.pdf")):
        if regex.search(pdf.name):
            matches.append(pdf)
            if len(matches) >= limit:
                break

    return matches


def render_pages_as_base64(pdf_bytes: bytes, dpi: int = 150) -> list[tuple[int, str]]:
    """Render each PDF page as a base64-encoded PNG (1-indexed)."""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    pages: list[tuple[int, str]] = []
    try:
        for i in range(len(doc)):
            page = doc.load_page(i)
            pix = page.get_pixmap(dpi=dpi, colorspace=fitz.csRGB, alpha=False)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            buf = BytesIO()
            img.save(buf, format="PNG")
            b64 = base64.b64encode(buf.getvalue()).decode()
            pages.append((i + 1, b64))
            img.close()
    finally:
        doc.close()
    return pages


def save_page_image(page_image_base64: str, output_path: Path) -> None:
    """Decode a base64 PNG and save it to disk."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(base64.b64decode(page_image_base64))


class ComparisonResult(BaseModel):
    ok: bool
    issues: list[str]
    page_description: str


_COMPARISON_SYSTEM_PROMPT = (
    "You are a QA reviewer comparing extracted text against the "
    "original document page image. Your job is to find content "
    "that was missed, garbled, or hallucinated in the extraction.\n\n"
    "Focus on:\n"
    "- Missing paragraphs, sections, or data\n"
    "- Wrong numbers, percentages, or dates\n"
    "- Table content lost or mangled\n"
    "- Text cut off or duplicated\n"
    "- Hallucinated content not present in the image\n"
    "- Charts/graphs described incorrectly\n\n"
    "Do NOT flag as issues:\n"
    "- Missing table of contents / index entries\n"
    "- Missing headers, footers, page numbers\n"
    "- Missing logos, watermarks, or decorative elements\n"
    "- Missing navigation elements (bookmarks, links menus)\n"
    "These are intentionally excluded by the extraction process.\n\n"
    "Only flag major issues that are clearly wrong, not nitpicks / formatting issues."
)


def _build_comparison_messages(
    chunk_text: str,
    page_image_base64: str,
    page_number: int,
) -> list[dict[str, Any]]:
    """Build the chat messages for a comparison request."""
    return [
        {"role": "system", "content": _COMPARISON_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": (
                        f"Page {page_number}.\n\n## Extracted text\n\n{chunk_text}\n\n"
                    ),
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{page_image_base64}",
                    },
                },
            ],
        },
    ]


def _error_result(page_number: int, error_msg: str) -> dict[str, Any]:
    return {
        "page_number": page_number,
        "ok": False,
        "issues": [error_msg],
        "page_description": "unknown (error)",
    }


def compare_chunk_with_image(
    chunk_text: str,
    page_image_base64: str,
    page_number: int,
    client: openai.OpenAI,
    model: str = "gpt-4o",
) -> dict[str, Any]:
    """Use a vision model to compare extracted text against the page image.

    Synchronous variant — prefer the async path in :func:`qa_document` for
    bulk comparisons.  Uses structured outputs for reliable parsing.
    """
    messages = _build_comparison_messages(chunk_text, page_image_base64, page_number)
    response = client.beta.chat.completions.parse(
        model=model,
        messages=messages,
        response_format=ComparisonResult,
        temperature=0,
    )
    parsed = response.choices[0].message.parsed
    if parsed is None:
        return _error_result(page_number, "Structured output returned None")
    result = parsed.model_dump()
    result["page_number"] = page_number
    return result


async def compare_chunk_with_image_async(
    chunk_text: str,
    page_image_base64: str,
    page_number: int,
    async_client: openai.AsyncOpenAI,
    semaphore: asyncio.Semaphore,
    model: str = "gpt-4o",
) -> dict[str, Any]:
    """Async version of :func:`compare_chunk_with_image`.  Uses structured outputs."""
    messages = _build_comparison_messages(chunk_text, page_image_base64, page_number)
    async with semaphore:
        try:
            response = await async_client.beta.chat.completions.parse(
                model=model,
                messages=messages,
                response_format=ComparisonResult,
                temperature=0,
            )
            parsed = response.choices[0].message.parsed
            if parsed is None:
                return _error_result(page_number, "Structured output returned None")
            result = parsed.model_dump()
            result["page_number"] = page_number
            return result
        except openai.OpenAIError:
            logger.exception("Comparison failed for page %d", page_number)
            return _error_result(page_number, "OpenAI API error during comparison")


def qa_document(
    pdf_path: Path,
    client: openai.OpenAI,
    processor: ServiceBoxProcessor,
    comparison_model: str = "gpt-4o",
    max_concurrent_comparisons: int = 10,
) -> dict[str, Any]:
    """Run full QA on a single PDF: extract chunks, compare each page.

    Comparisons are run concurrently using ``asyncio``.

    Returns a dict with:
      - filename, path, total_pages
      - pages_with_issues (list[dict]): only pages where ok=False
      - all_results (list[dict]): comparison result for every page
      - page_images (dict[int, str]): page_number -> base64 for problematic pages
    """
    pdf_bytes = pdf_path.read_bytes()

    # 1. Extract text chunks via ServiceBox
    logger.info("Running ServiceBox on %s", pdf_path.name)
    chunks = processor.to_chunks(pdf_bytes, ContentType.PDF, filename=pdf_path.name)
    chunk_by_page: dict[int, str] = {}
    for chunk in chunks:
        page_num = int(chunk.metadata.get("page_number", 0))
        if page_num > 0:
            chunk_by_page[page_num] = chunk.data.decode("utf-8")

    # 2. Render pages as images
    logger.info("Rendering pages as images for %s", pdf_path.name)
    page_images = render_pages_as_base64(pdf_bytes)

    # 3. Compare each page concurrently
    logger.info(
        "Comparing %d pages concurrently (max_concurrent=%d) for %s",
        len(page_images),
        max_concurrent_comparisons,
        pdf_path.name,
    )
    all_results = asyncio.run(
        _compare_pages_async(
            page_images,
            chunk_by_page,
            client.api_key,
            comparison_model,
            max_concurrent_comparisons,
        )
    )

    pages_with_issues = [r for r in all_results if not r.get("ok", True)]

    # Keep base64 images only for problematic pages (for agent inspection)
    issue_page_numbers = {r["page_number"] for r in pages_with_issues}
    problematic_images = {
        pn: b64 for pn, b64 in page_images if pn in issue_page_numbers
    }

    return {
        "filename": pdf_path.name,
        "path": str(pdf_path),
        "total_pages": len(page_images),
        "pages_with_issues": pages_with_issues,
        "all_results": all_results,
        "page_images": problematic_images,
        "chunk_by_page": chunk_by_page,
    }


async def _compare_pages_async(
    page_images: list[tuple[int, str]],
    chunk_by_page: dict[int, str],
    api_key: str,
    model: str,
    max_concurrent: int,
) -> list[dict[str, Any]]:
    """Run all page comparisons concurrently and return results in page order."""
    async_client = openai.AsyncOpenAI(api_key=api_key, timeout=30)
    semaphore = asyncio.Semaphore(max_concurrent)

    async def _compare_one(page_number: int, img_b64: str) -> dict[str, Any]:
        text = chunk_by_page.get(page_number)
        if text is None:
            return {
                "page_number": page_number,
                "ok": False,
                "issues": ["No chunk extracted for this page"],
                "page_description": "unknown (no extraction)",
            }
        return await compare_chunk_with_image_async(
            text, img_b64, page_number, async_client, semaphore, model=model
        )

    tasks = [_compare_one(pn, b64) for pn, b64 in page_images]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    final: list[dict[str, Any]] = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            page_number = page_images[i][0]
            logger.exception("Comparison failed for page %d: %s", page_number, result)
            final.append(
                {
                    "page_number": page_number,
                    "ok": False,
                    "issues": [f"Comparison error: {result}"],
                    "page_description": "unknown (error)",
                }
            )
        else:
            final.append(result)
    return final


def run_qa(
    doc_paths: list[str],
    output_dir: str = "/tmp/servicebox-qa",
    servicebox_model: str = "gpt-4o",
    comparison_model: str = "gpt-4o",
) -> list[dict[str, Any]]:
    """Run QA on the given document paths.

    Call :func:`find_matching_documents` first to discover candidates, let the
    user confirm, then pass the confirmed paths here.

    Each run creates a timestamped sub-folder under *output_dir* so that
    concurrent or repeated runs never collide::

        <output_dir>/
          run_20260326_143012/
            results.json
            <stem>/
              page_1.json
              page_1.png
              ...

    Returns (results, run_dir_path).
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set")

    client = openai.OpenAI(api_key=api_key, timeout=30)
    processor = ServiceBoxProcessor(
        api_key=api_key,
        model=servicebox_model,
        concurrent=True,
        max_concurrent=10,
    )

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    run_dir = Path(output_dir) / f"run_{timestamp}"
    run_dir.mkdir(parents=True, exist_ok=True)
    print(f"Run directory: {run_dir}")

    results: list[dict[str, Any]] = []
    for path_str in doc_paths:
        doc_path = Path(path_str)
        print(f"\nProcessing: {doc_path.name} ...")
        result = qa_document(doc_path, client, processor, comparison_model)

        doc_dir = run_dir / doc_path.stem
        doc_dir.mkdir(parents=True, exist_ok=True)

        chunk_by_page = result.pop("chunk_by_page")
        comparison_by_page = {r["page_number"]: r for r in result["all_results"]}

        # Save per-page JSON (extracted text + comparison result)
        for page_num in sorted(
            set(chunk_by_page.keys()) | set(comparison_by_page.keys())
        ):
            page_data: dict[str, Any] = {"page_number": page_num}
            if page_num in chunk_by_page:
                page_data["extracted_text"] = chunk_by_page[page_num]
            if page_num in comparison_by_page:
                page_data["comparison"] = comparison_by_page[page_num]
            page_path = doc_dir / f"page_{page_num}.json"
            page_path.write_text(json.dumps(page_data, indent=2, ensure_ascii=False))

        # Save problematic page images to disk for agent inspection
        for page_num, img_b64 in result.pop("page_images").items():
            img_path = doc_dir / f"page_{page_num}.png"
            save_page_image(img_b64, img_path)

        results.append(result)

        n_issues = len(result["pages_with_issues"])
        print(f"  {result['total_pages']} pages, {n_issues} with issues")
        print(f"  Output saved to {doc_dir}")

    # Save JSON results
    results_path = run_dir / "results.json"
    results_path.write_text(json.dumps(results, indent=2, ensure_ascii=False))
    print(f"\nResults saved to {results_path}")

    return results


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="ServiceBox QA utilities")
    sub = parser.add_subparsers(dest="command", required=True)

    # --- find ---
    find_p = sub.add_parser("find", help="Find matching PDFs")
    find_p.add_argument("folder")
    find_p.add_argument("pattern")
    find_p.add_argument("--limit", type=int, default=3)

    # --- run ---
    run_p = sub.add_parser("run", help="Run QA on specified documents")
    run_p.add_argument("docs", nargs="+", help="PDF file paths")
    run_p.add_argument("--output-dir", default="/tmp/servicebox-qa")
    run_p.add_argument("--servicebox-model", default="gpt-4o")
    run_p.add_argument("--comparison-model", default="gpt-4o")

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    if args.command == "find":
        docs = find_matching_documents(args.folder, args.pattern, limit=args.limit)
        if not docs:
            print(f"No PDFs matching '{args.pattern}' found in {args.folder}")
            sys.exit(1)
        for d in docs:
            print(d)

    elif args.command == "run":
        run_qa(
            args.docs,
            output_dir=args.output_dir,
            servicebox_model=args.servicebox_model,
            comparison_model=args.comparison_model,
        )

from __future__ import annotations

import base64
import importlib.util
import inspect
import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from pdfsearch.processors.servicebox.image_conversion import convert_pdf_to_images
from pdfsearch.processors.servicebox.main import ServiceBoxProcessor

logger = logging.getLogger(__name__)

load_dotenv()

_QA_UTILS_PATH = (
    Path(__file__).resolve().parent.parent / "servicebox-processor-qa" / "utils.py"
)


# ---------------------------------------------------------------------------
# Dynamic import helpers
# ---------------------------------------------------------------------------


def _load_module_from_path(module_path: Path, module_name: str) -> Any:
    """Load a Python module from an arbitrary filesystem path."""
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module from {module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _find_processor_subclass(module: Any) -> type:
    """Find the first ServiceBoxProcessor subclass in a loaded module.

    Skips ``ServiceBoxProcessor`` itself and any private names.
    """
    for name in dir(module):
        if name.startswith("_"):
            continue
        attr = getattr(module, name)
        if (
            inspect.isclass(attr)
            and issubclass(attr, ServiceBoxProcessor)
            and attr is not ServiceBoxProcessor
        ):
            return attr
    raise TypeError(
        f"No ServiceBoxProcessor subclass found in {getattr(module, '__file__', module)}"
    )


def _load_processor_class(module_path: Path) -> type:
    """Dynamic-import a processor module and return its processor class."""
    module = _load_module_from_path(module_path, f"_override_{module_path.stem}")
    return _find_processor_subclass(module)


def _load_qa_document():
    """Import ``qa_document`` from the QA skill's utils.py."""
    if not _QA_UTILS_PATH.exists():
        raise FileNotFoundError(
            f"QA skill utils not found at {_QA_UTILS_PATH}. "
            "Ensure servicebox-processor-qa skill is present."
        )
    module = _load_module_from_path(_QA_UTILS_PATH, "_qa_utils")
    return module.qa_document


# ---------------------------------------------------------------------------
# test-predicates
# ---------------------------------------------------------------------------


def test_predicates(
    pdf_paths: list[str],
    processor_module: str,
    output_dir: str = "/tmp/servicebox-override",
) -> dict[str, Any]:
    """Run page-handler predicates against real PDFs and save matched images.

    No LLM calls are made — only local PDF conversion + Python predicates.
    """
    module_path = Path(processor_module).resolve()
    cls = _load_processor_class(module_path)

    # Instantiate with dummy key — we only need the _page_handlers list.
    processor = cls(api_key="dummy-key-for-predicate-testing")
    handlers = processor._page_handlers

    if not handlers:
        print(f"WARNING: {cls.__name__} has no page handlers — nothing to test.")
        return {"documents": [], "total_matches": 0}

    handler_names = [h.name for h in handlers]
    print(f"Processor: {cls.__name__}")
    print(f"Handlers:  {', '.join(handler_names)}")
    print()

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    run_dir = Path(output_dir) / f"predicates_{timestamp}"
    run_dir.mkdir(parents=True, exist_ok=True)

    documents: list[dict[str, Any]] = []
    total_matches = 0

    for path_str in pdf_paths:
        doc_path = Path(path_str)
        print(f"Processing: {doc_path.name} ...")
        pdf_bytes = doc_path.read_bytes()

        pages_data = convert_pdf_to_images(pdf_bytes)
        matches: list[dict[str, Any]] = []
        unmatched: list[int] = []

        doc_dir = run_dir / doc_path.stem
        doc_dir.mkdir(parents=True, exist_ok=True)

        for page_data in pages_data:
            page_number = page_data.get("page_number", 0)
            matched_handler = None

            for handler in handlers:
                if handler.predicate(page_data):
                    matched_handler = handler
                    break

            if matched_handler:
                matches.append(
                    {"page_number": page_number, "handler": matched_handler.name}
                )
                # Save the page image for agent visual review
                img_path = doc_dir / f"page_{page_number}_{matched_handler.name}.png"
                img_path.write_bytes(base64.b64decode(page_data["image_base64"]))
            else:
                unmatched.append(page_number)

        total_matches += len(matches)
        total_pages = len(pages_data)
        match_pct = f"{len(matches) / total_pages * 100:.1f}%" if total_pages else "0%"

        documents.append(
            {
                "filename": doc_path.name,
                "total_pages": total_pages,
                "matches": matches,
                "unmatched_pages": unmatched,
                "match_rate": match_pct,
            }
        )

        print(f"  {total_pages} pages, {len(matches)} matched ({match_pct})")
        for m in matches:
            print(f"    page {m['page_number']:>3d} -> {m['handler']}")
        print()

    summary = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "processor_module": str(module_path),
        "processor_class": cls.__name__,
        "handlers": handler_names,
        "documents": documents,
        "total_matches": total_matches,
    }

    summary_path = run_dir / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False))
    print(f"Summary saved to {summary_path}")
    print(f"Run directory: {run_dir}")

    return summary


# ---------------------------------------------------------------------------
# compare
# ---------------------------------------------------------------------------


def _load_qa_results(qa_run_dir: Path) -> list[dict[str, Any]]:
    """Load results.json from a previous QA run."""
    results_path = qa_run_dir / "results.json"
    if not results_path.exists():
        raise FileNotFoundError(f"No results.json found in {qa_run_dir}")
    return json.loads(results_path.read_text())


def _load_qa_modules():
    """Import comparison helpers from the QA skill's utils.py."""
    if not _QA_UTILS_PATH.exists():
        raise FileNotFoundError(
            f"QA skill utils not found at {_QA_UTILS_PATH}. "
            "Ensure servicebox-processor-qa skill is present."
        )
    module = _load_module_from_path(_QA_UTILS_PATH, "_qa_utils")
    return (
        module.render_pages_as_base64,
        module.compare_chunk_with_image_async,
        module.save_page_image,
    )


async def _compare_handled_pages(
    handled_chunks: dict[int, str],
    page_images: list[tuple[int, str]],
    api_key: str,
    comparison_model: str,
    max_concurrent: int,
) -> list[dict[str, Any]]:
    """QA-compare only the handler-matched pages against their images."""
    import asyncio

    import openai

    _, compare_async, _ = _load_qa_modules()

    async_client = openai.AsyncOpenAI(api_key=api_key, timeout=30)
    semaphore = asyncio.Semaphore(max_concurrent)

    image_by_page = {pn: b64 for pn, b64 in page_images}

    async def _compare_one(page_num: int, text: str) -> dict[str, Any]:
        img_b64 = image_by_page.get(page_num)
        if img_b64 is None:
            return {
                "page_number": page_num,
                "ok": False,
                "issues": ["No rendered image for this page"],
                "page_description": "unknown (no image)",
            }
        return await compare_async(
            text,
            img_b64,
            page_num,
            async_client,
            semaphore,
            model=comparison_model,
        )

    tasks = [_compare_one(pn, text) for pn, text in sorted(handled_chunks.items())]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    final: list[dict[str, Any]] = []
    page_nums = sorted(handled_chunks.keys())
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            logger.exception("Comparison failed for page %d: %s", page_nums[i], result)
            final.append(
                {
                    "page_number": page_nums[i],
                    "ok": False,
                    "issues": [f"Comparison error: {result}"],
                    "page_description": "unknown (error)",
                }
            )
        else:
            final.append(result)
    return final


def compare(
    pdf_paths: list[str],
    processor_module: str,
    qa_run_dir: str,
    output_dir: str = "/tmp/servicebox-override",
    servicebox_model: str = "gpt-4o",
    comparison_model: str = "gpt-4o",
    max_concurrent_comparisons: int = 10,
) -> dict[str, Any]:
    """Compare override processor output against the original QA baseline.

    Only handler-matched pages are re-processed and QA-checked. Non-handler
    pages follow the exact same code path as the base processor, so they are
    skipped — no wasted API calls, no LLM non-determinism noise.

    Requires:
    - ``OPENAI_API_KEY`` in the environment
    - A previous QA run directory (from ``servicebox-processor-qa``) as baseline
    """
    import asyncio

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set")

    qa_dir = Path(qa_run_dir)
    if not qa_dir.is_dir():
        raise FileNotFoundError(f"QA run directory not found: {qa_run_dir}")

    # Load baseline QA results
    baseline_results = _load_qa_results(qa_dir)
    baseline_by_filename: dict[str, dict[str, Any]] = {
        r["filename"]: r for r in baseline_results
    }

    # Load the override processor class
    module_path = Path(processor_module).resolve()
    cls = _load_processor_class(module_path)
    override_processor = cls(
        api_key=api_key,
        model=servicebox_model,
        concurrent=True,
        max_concurrent=10,
    )
    handler_names = [h.name for h in override_processor._page_handlers]

    render_pages, _, save_img = _load_qa_modules()

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    run_dir = Path(output_dir) / f"compare_{timestamp}"
    run_dir.mkdir(parents=True, exist_ok=True)

    print(f"Override processor: {cls.__name__}")
    print(f"Handlers:           {', '.join(handler_names)}")
    print(f"QA baseline:        {qa_dir}")
    print(f"Run directory:      {run_dir}")
    print()

    doc_reports: list[dict[str, Any]] = []
    total_improved = 0
    total_worsened = 0
    total_still_failing = 0
    total_now_ok = 0

    for path_str in pdf_paths:
        doc_path = Path(path_str)
        print(f"Processing: {doc_path.name}")

        # Find baseline for this document
        baseline = baseline_by_filename.get(doc_path.name)
        if baseline is None:
            print(f"  SKIP — no baseline QA results for {doc_path.name}")
            continue

        baseline_by_page = {
            r["page_number"]: r for r in baseline.get("all_results", [])
        }

        # Run the override processor to extract chunks
        pdf_bytes = doc_path.read_bytes()
        print("  Extracting with override processor ...")
        from pdfsearch.enums import ContentType

        chunks = override_processor.to_chunks(
            pdf_bytes, ContentType.PDF, filename=doc_path.name
        )

        # Identify handler-matched pages (those with page_type metadata)
        handled_chunks: dict[int, str] = {}
        handler_types: dict[int, str] = {}
        for chunk in chunks:
            page_type = chunk.metadata.get("page_type")
            if page_type:
                page_num = int(chunk.metadata["page_number"])
                handled_chunks[page_num] = chunk.data.decode("utf-8")
                handler_types[page_num] = page_type

        if not handled_chunks:
            print("  No pages matched any handler — nothing to compare.")
            doc_reports.append(
                {
                    "filename": doc_path.name,
                    "total_pages": baseline["total_pages"],
                    "handled_pages": 0,
                    "results": [],
                }
            )
            continue

        print(
            f"  {len(handled_chunks)} handler-matched pages: "
            f"{', '.join(f'p{p}({handler_types[p]})' for p in sorted(handled_chunks))}"
        )

        # Render page images for QA comparison
        print("  Rendering page images ...")
        page_images = render_pages(pdf_bytes)

        # QA-compare only the handled pages
        print(f"  QA-checking {len(handled_chunks)} handled pages ...")
        override_comparisons = asyncio.run(
            _compare_handled_pages(
                handled_chunks,
                page_images,
                api_key,
                comparison_model,
                max_concurrent_comparisons,
            )
        )
        override_by_page = {r["page_number"]: r for r in override_comparisons}

        # Save per-page data and classify
        doc_dir = run_dir / doc_path.stem
        doc_dir.mkdir(parents=True, exist_ok=True)

        page_results: list[dict[str, Any]] = []
        image_by_page = {pn: b64 for pn, b64 in page_images}

        for page_num in sorted(handled_chunks):
            base_comp = baseline_by_page.get(page_num, {})
            over_comp = override_by_page.get(page_num, {})

            base_ok = base_comp.get("ok", False)
            override_ok = over_comp.get("ok", False)
            base_issues = base_comp.get("issues", [])
            override_issues = over_comp.get("issues", [])

            if not base_ok and override_ok:
                status = "improved"
                total_improved += 1
            elif base_ok and not override_ok:
                status = "worsened"
                total_worsened += 1
            elif not base_ok and not override_ok:
                total_still_failing += 1
                # Fewer issues = partial improvement
                if len(override_issues) < len(base_issues):
                    status = "partially_improved"
                else:
                    status = "still_failing"
            else:
                status = "still_ok"
                total_now_ok += 1

            entry = {
                "page_number": page_num,
                "handler": handler_types[page_num],
                "status": status,
                "base_ok": base_ok,
                "base_issues": base_issues,
                "override_ok": override_ok,
                "override_issues": override_issues,
            }
            page_results.append(entry)

            # Save page-level files
            page_data_out = {
                **entry,
                "base_comparison": base_comp,
                "override_comparison": over_comp,
            }
            (doc_dir / f"page_{page_num}.json").write_text(
                json.dumps(page_data_out, indent=2, ensure_ascii=False)
            )

            # Save extracted text from the override
            (doc_dir / f"page_{page_num}_override.txt").write_text(
                handled_chunks[page_num], encoding="utf-8"
            )

            # Save the baseline extracted text if available in the QA run
            baseline_page_json = qa_dir / doc_path.stem / f"page_{page_num}.json"
            if baseline_page_json.exists():
                baseline_page = json.loads(baseline_page_json.read_text())
                base_text = baseline_page.get("extracted_text", "")
                if base_text:
                    (doc_dir / f"page_{page_num}_base.txt").write_text(
                        base_text, encoding="utf-8"
                    )

            # Save page image
            if page_num in image_by_page:
                img_path = doc_dir / f"page_{page_num}.png"
                save_img(image_by_page[page_num], img_path)

        doc_reports.append(
            {
                "filename": doc_path.name,
                "total_pages": baseline["total_pages"],
                "handled_pages": len(handled_chunks),
                "results": page_results,
            }
        )

        # Print per-page summary
        for r in page_results:
            icon = {
                "improved": "+",
                "partially_improved": "~",
                "still_ok": "=",
                "still_failing": "-",
                "worsened": "!",
            }.get(r["status"], "?")
            print(
                f"    [{icon}] page {r['page_number']:>3d} ({r['handler']}): "
                f"{r['status']}"
            )
        print()

    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "processor_module": str(module_path),
        "processor_class": cls.__name__,
        "qa_baseline": str(qa_dir),
        "comparison_model": comparison_model,
        "documents": doc_reports,
        "summary": {
            "total_handled_pages": total_improved
            + total_worsened
            + total_still_failing
            + total_now_ok,
            "improved": total_improved,
            "worsened": total_worsened,
            "still_failing": total_still_failing,
            "still_ok": total_now_ok,
        },
    }

    report_path = run_dir / "regression_report.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False))

    print(f"Handler-matched pages: {report['summary']['total_handled_pages']}")
    print(f"  Improved:       {total_improved}")
    print(f"  Worsened:       {total_worsened}")
    print(f"  Still failing:  {total_still_failing}")
    print(f"  Already OK:     {total_now_ok}")
    print()
    print(f"Report saved to {report_path}")
    print(f"Run directory: {run_dir}")

    return report


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="ServiceBox override creation utilities"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # --- test-predicates ---
    tp = sub.add_parser(
        "test-predicates", help="Test page-handler predicates against real PDFs"
    )
    tp.add_argument("docs", nargs="+", help="PDF file paths")
    tp.add_argument(
        "--processor-module",
        required=True,
        help="Path to the generated processor .py file",
    )
    tp.add_argument("--output-dir", default="/tmp/servicebox-override")

    # --- compare ---
    cp = sub.add_parser(
        "compare",
        help="QA-check handler-matched pages and compare against QA baseline",
    )
    cp.add_argument("docs", nargs="+", help="PDF file paths")
    cp.add_argument(
        "--processor-module",
        required=True,
        help="Path to the generated processor .py file",
    )
    cp.add_argument(
        "--qa-run-dir",
        required=True,
        help="Path to the original QA run directory (from servicebox-processor-qa)",
    )
    cp.add_argument("--output-dir", default="/tmp/servicebox-override")
    cp.add_argument("--servicebox-model", default="gpt-4o")
    cp.add_argument("--comparison-model", default="gpt-4o")

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    if args.command == "test-predicates":
        test_predicates(
            args.docs,
            processor_module=args.processor_module,
            output_dir=args.output_dir,
        )

    elif args.command == "compare":
        compare(
            args.docs,
            processor_module=args.processor_module,
            qa_run_dir=args.qa_run_dir,
            output_dir=args.output_dir,
            servicebox_model=args.servicebox_model,
            comparison_model=args.comparison_model,
        )

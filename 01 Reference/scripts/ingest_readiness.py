#!/usr/bin/env python3
"""
Check ingestion readiness for cleaned sources.

Shows which .md source files are ready for ingestion (processed: false)
and provides a checklist for the next steps.

Run:
  python3 "01 Reference/scripts/ingest_readiness.py"
"""

import sys
from pathlib import Path

RAW_SOURCES_DIR = Path(__file__).parent.parent.parent / "00 Raw Sources"


def parse_frontmatter(text: str) -> dict:
    """Extract frontmatter fields from markdown."""
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    fm = text[4:end]
    meta: dict = {}
    current_list: list | None = None

    for raw in fm.split("\n"):
        if raw.startswith("  - ") or (current_list is not None and raw.startswith("- ")):
            v = raw.lstrip(" -").strip()
            if current_list is not None:
                current_list.append(v)
            continue
        if ":" not in raw or raw.startswith(" "):
            continue
        key, _, val = raw.partition(":")
        key = key.strip(); val = val.strip()
        if val == "":
            meta[key] = []
            current_list = meta[key]
        else:
            meta[key] = val.strip('"').strip("'")
            current_list = None
    return meta


def check_readiness():
    """Report on source files ready for ingestion."""
    md_files = sorted(RAW_SOURCES_DIR.glob("*.md"))

    ready_to_ingest = []
    already_ingested = []

    for md_path in md_files:
        text = md_path.read_text(encoding="utf-8")
        meta = parse_frontmatter(text)

        # Only check files with type: raw-source
        if meta.get("type") != "raw-source":
            continue

        processed = meta.get("processed", "false").lower() == "true"
        if processed:
            already_ingested.append((md_path.name, meta.get("articles_created", [])))
        else:
            ready_to_ingest.append(md_path.name)

    print(f"Source Ingestion Readiness Check")
    print(f"{'='*70}")

    if ready_to_ingest:
        print(f"\n✓ Ready to Ingest ({len(ready_to_ingest)}):")
        for i, fname in enumerate(ready_to_ingest, 1):
            print(f"  {i}. [[{fname}]]")
    else:
        print(f"\n✓ Ready to Ingest: (none)")

    if already_ingested:
        print(f"\n✔ Already Ingested ({len(already_ingested)}):")
        for fname, articles in already_ingested:
            articles_str = ", ".join(articles) if articles else "(unknown)"
            print(f"  • {fname}")
            print(f"    → {articles_str}")
    else:
        print(f"\n✔ Already Ingested: (none)")

    print(f"\n{'='*70}")

    if ready_to_ingest:
        print(f"\nNext Steps:")
        print(f"  1. Run: /ingest-source [[<filename>.md]]")
        print(f"     For each file above")
        print(f"\n  2. Or use batch-ingest-sources skill to process all at once")
        print(f"\n  The ingest-source skill will:")
        print(f"    • Extract knowledge from each source")
        print(f"    • Create/update reference articles")
        print(f"    • Mark source as processed: true")
        print(f"    • Rebuild catalog and aggregates")


if __name__ == "__main__":
    if not RAW_SOURCES_DIR.exists():
        print(f"ERROR: {RAW_SOURCES_DIR} not found", file=sys.stderr)
        sys.exit(1)

    check_readiness()

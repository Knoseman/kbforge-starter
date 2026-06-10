#!/usr/bin/env python3
"""
Scan 00 Raw Sources/ for unprocessed .txt files and detect duplicates.

Identifies which .txt files need cleaning and ingestion, and which have
already been processed (detected by matching .md files with processed: true).

Run:
  python3 "01 Reference/scripts/scan_raw_sources.py"
"""

import re
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


def normalize_name(s: str) -> str:
    """Normalize a filename for matching (lowercase, strip common suffixes)."""
    s = s.lower()
    # Strip common transcript/file suffixes
    for suffix in ["_transcript", " transcript", "-transcript", "_notes", " notes", "_chat", " chat"]:
        if s.endswith(suffix):
            s = s[:-len(suffix)]
    # Strip file extensions
    s = s.rsplit(".", 1)[0]
    return s.strip()


def scan() -> tuple[list[str], list[tuple[str, str]]]:
    """
    Return (to_process, already_processed) where:
      to_process: list of .txt filenames to clean+ingest
      already_processed: list of (txt_file, corresponding_md_file) tuples
    """
    if not RAW_SOURCES_DIR.exists():
        print(f"ERROR: {RAW_SOURCES_DIR} not found", file=sys.stderr)
        sys.exit(1)

    # Collect all .txt files
    txt_files = sorted([f.name for f in RAW_SOURCES_DIR.glob("*.txt")])

    # Collect all .md files with processed status
    md_files_processed: dict[str, bool] = {}
    for md_path in RAW_SOURCES_DIR.glob("*.md"):
        text = md_path.read_text(encoding="utf-8")
        meta = parse_frontmatter(text)
        processed = meta.get("processed", "false").lower() == "true"
        md_files_processed[md_path.name] = processed

    # Detect duplicates
    to_process: list[str] = []
    already_processed: list[tuple[str, str]] = []

    for txt_file in txt_files:
        # Normalize the txt filename and look for a matching .md
        txt_norm = normalize_name(txt_file)
        found_match = False

        for md_file, processed in md_files_processed.items():
            md_norm = normalize_name(md_file)
            # Simple heuristic: if normalized names are very similar, they're a match
            if txt_norm and md_norm and (
                txt_norm in md_norm or md_norm in txt_norm or
                # Also check if they share significant keywords (min 3 chars)
                any(len(w) >= 3 and w in md_norm for w in txt_norm.split())
            ):
                if processed:
                    already_processed.append((txt_file, md_file))
                    found_match = True
                    break

        if not found_match:
            to_process.append(txt_file)

    return to_process, already_processed


if __name__ == "__main__":
    to_process, already_processed = scan()

    print(f"Raw Sources Scan: {RAW_SOURCES_DIR}")
    print(f"{'='*70}")

    if to_process:
        print(f"\n✓ To Process ({len(to_process)} files):")
        for txt in to_process:
            print(f"  - {txt}")
    else:
        print(f"\n✓ To Process: (none)")

    if already_processed:
        print(f"\n⊝ Already Processed ({len(already_processed)} files):")
        for txt, md in already_processed:
            print(f"  - {txt}")
            print(f"    → {md}")
    else:
        print(f"\n⊝ Already Processed: (none)")

    print(f"\n{'='*70}")
    print(f"Total .txt files: {len(to_process) + len(already_processed)}")
    print(f"New (to ingest): {len(to_process)}")
    print(f"Duplicates: {len(already_processed)}")

    if len(to_process) == 0:
        print(f"\n✓ All sources are already processed.")
        sys.exit(0)

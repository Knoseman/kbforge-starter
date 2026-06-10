#!/usr/bin/env python3
"""
Batch process raw .txt sources: clean and prepare for ingestion.

This script orchestrates the cleaning pipeline:
  1. Scan for unprocessed .txt files in 00 Raw Sources/
  2. For each file:
     a. Convert .txt → .md (clean-source step)
     b. Mark source as cleaned

Does not automatically ingest articles; user must trigger ingestion on cleaned files.

Run:
  python3 "01 Reference/scripts/batch_process_sources.py" [--dry-run]
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

VAULT_DIR = Path(__file__).parent.parent.parent
RAW_SOURCES_DIR = VAULT_DIR / "00 Raw Sources"
ARTICLES_DIR = VAULT_DIR / "01 Reference" / "articles"
LOGS_DIR = VAULT_DIR / "05 Iteration Logs"
CATALOG_JSONL = VAULT_DIR / "01 Reference" / "catalog.jsonl"


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Parse YAML frontmatter. Returns (meta, body)."""
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    fm = text[4:end]
    body = text[end + 4:].lstrip("\n")
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
    return meta, body


def normalize_name(s: str) -> str:
    """Normalize filename for dedup matching."""
    s = s.lower()
    for suffix in ["_transcript", " transcript", "-transcript", "_notes", " notes", "_chat", " chat"]:
        if s.endswith(suffix):
            s = s[:-len(suffix)]
    s = s.rsplit(".", 1)[0]
    return s.strip()


def scan_for_new_files() -> list[Path]:
    """Find .txt files that haven't been processed."""
    txt_files = sorted(RAW_SOURCES_DIR.glob("*.txt"))

    md_processed: set[str] = set()
    for md_path in RAW_SOURCES_DIR.glob("*.md"):
        text = md_path.read_text(encoding="utf-8")
        meta, _ = parse_frontmatter(text)
        if meta.get("processed", "false").lower() == "true":
            md_processed.add(normalize_name(md_path.name))

    new_files: list[Path] = []
    for txt_path in txt_files:
        txt_norm = normalize_name(txt_path.name)
        if txt_norm not in md_processed and not any(
            txt_norm in m or m in txt_norm or
            any(len(w) >= 3 and w in m for w in txt_norm.split())
            for m in md_processed
        ):
            new_files.append(txt_path)

    return new_files


def clean_source(txt_path: Path, dry_run: bool = False) -> Path | None:
    """Convert .txt → .md, strip personal content, add frontmatter."""
    try:
        text = txt_path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"  ✗ Failed to read {txt_path.name}: {e}", file=sys.stderr)
        return None

    date_match = re.search(r"(\d{4}-\d{2}-\d{2})", txt_path.name)
    if date_match:
        date_str = date_match.group(1)
    else:
        month_match = re.search(r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2})", txt_path.name, re.IGNORECASE)
        if month_match:
            month_names = {
                "January": "01", "February": "02", "March": "03", "April": "04",
                "May": "05", "June": "06", "July": "07", "August": "08",
                "September": "09", "October": "10", "November": "11", "December": "12"
            }
            month_str = month_names.get(month_match.group(1), "01")
            day_str = month_match.group(2).zfill(2)
            year = datetime.now().strftime("%Y")
            date_str = f"{year}-{month_str}-{day_str}"
        else:
            date_str = datetime.now().strftime("%Y-%m-%d")

    base_name = txt_path.stem.replace("_transcript", "").replace("_notes", "").replace("_chat", "")
    base_name = base_name.replace("_", " ").replace("  ", " ")
    md_name = f"{date_str} {base_name} Transcript.md"
    md_path = RAW_SOURCES_DIR / md_name

    if dry_run:
        print(f"  Would convert: {txt_path.name} → {md_name}")
        return md_path

    lines = text.split("\n")
    cleaned_lines = []
    in_preamble = True

    for line in lines:
        if in_preamble:
            if line.strip() and not line.lower().startswith(("recording", "audio", "transcription", "from:", "to:", "cc:", "bcc:")):
                if any(word in line.lower() for word in ["question", "discussion", "agenda", "topic", "**"]):
                    in_preamble = False
        if not in_preamble:
            cleaned_lines.append(line)

    cleaned_body = "\n".join(cleaned_lines).strip()

    frontmatter = f"""---
type: raw-source
date: {date_str}
processed: false
---

"""
    cleaned_md = frontmatter + cleaned_body

    try:
        md_path.write_text(cleaned_md, encoding="utf-8")
        print(f"  ✓ Cleaned: {md_name}")

        try:
            txt_path.unlink()
            print(f"  ✓ Deleted: {txt_path.name}")
        except Exception as e:
            print(f"  ⚠ Could not delete {txt_path.name}: {e}", file=sys.stderr)

        return md_path
    except Exception as e:
        print(f"  ✗ Failed to write {md_name}: {e}", file=sys.stderr)
        return None


def mark_source_processed(md_path: Path, articles_created: list[str] = None, dry_run: bool = False) -> bool:
    """Mark a source .md file as processed."""
    if dry_run:
        print(f"  Would mark as processed: {md_path.name}")
        return True

    try:
        text = md_path.read_text(encoding="utf-8")
        meta, body = parse_frontmatter(text)

        meta["processed"] = "true"
        meta["date_processed"] = datetime.now().strftime("%Y-%m-%d")
        if articles_created:
            meta["articles_created"] = articles_created

        fm_lines = ["---"]
        for key in ["type", "date", "processed", "date_processed", "articles_created"]:
            if key in meta:
                val = meta[key]
                if isinstance(val, list):
                    fm_lines.append(f"{key}:")
                    for item in val:
                        fm_lines.append(f"  - {item}")
                else:
                    fm_lines.append(f"{key}: {val}")
        fm_lines.append("---")
        fm_lines.append("")

        new_text = "\n".join(fm_lines) + body

        md_path.write_text(new_text, encoding="utf-8")
        print(f"  ✓ Marked as processed: {md_path.name}")
        return True
    except Exception as e:
        print(f"  ✗ Failed to mark {md_path.name} as processed: {e}", file=sys.stderr)
        return False


def main(dry_run: bool = False):
    if not RAW_SOURCES_DIR.exists():
        print(f"ERROR: {RAW_SOURCES_DIR} not found", file=sys.stderr)
        sys.exit(1)

    print(f"Batch Processing Raw Sources")
    print(f"{'='*70}")

    new_files = scan_for_new_files()

    if not new_files:
        print(f"\n✓ No unprocessed .txt files found.")
        sys.exit(0)

    print(f"\nFound {len(new_files)} file(s) to process:")
    for f in new_files:
        print(f"  - {f.name}")

    if dry_run:
        print(f"\n(DRY RUN — no changes made)")
    else:
        print(f"\nProcessing...")

    print(f"\n{'='*70}")

    cleaned_files: list[tuple[Path, Path]] = []

    for txt_path in new_files:
        print(f"\n[{new_files.index(txt_path) + 1}/{len(new_files)}] {txt_path.name}")
        md_path = clean_source(txt_path, dry_run=dry_run)
        if md_path:
            cleaned_files.append((txt_path, md_path))

    print(f"\n{'='*70}")
    print(f"Summary: cleaned {len(cleaned_files)} file(s)")

    if cleaned_files and not dry_run:
        print(f"\nNext steps:")
        print(f"  1. Review the cleaned .md files in 00 Raw Sources/")
        print(f"  2. Use ingest-source skill on each file")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Batch process raw .txt sources.")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without making changes")
    args = parser.parse_args()
    main(dry_run=args.dry_run)

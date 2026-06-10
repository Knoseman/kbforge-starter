#!/usr/bin/env python3
"""
Catalog verifier for 01 Reference knowledge base.

Walks every article in 01 Reference/articles/ and checks:
  - id field present and equals filename (without .md)
  - required frontmatter fields present
  - kind / domain / status / topics / owner match topics.yaml vocabulary
  - review_due present for kind: known-issue or status: provisional
  - all related: ids point to existing articles
  - body has ## Answer section
  - kind: process has ## Procedure
  - kind: known-issue has ## Status
  - catalog.jsonl in sync with articles directory

Run:
  python3 "01 Reference/scripts/verify_catalog.py"

Exit codes:
  0 — no errors (warnings allowed)
  1 — one or more errors found
"""

import json
import re
import sys
from pathlib import Path

REFERENCE_DIR = Path(__file__).parent.parent
ARTICLES_DIR  = REFERENCE_DIR / "articles"
CATALOG_JSONL = REFERENCE_DIR / "catalog.jsonl"
TOPICS_YAML   = REFERENCE_DIR / "topics.yaml"

REQUIRED_FIELDS = {"id", "title", "kind", "domain", "topics", "status", "updated", "owner", "summary"}


# ---------------------------------------------------------------------------
# Minimal parsers (avoid PyYAML dependency)
# ---------------------------------------------------------------------------

def parse_frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    fm = text[4:end]
    body = text[end + 4:].lstrip("\n")
    meta: dict = {}
    current_key: str | None = None
    current_list: list | None = None

    for raw in fm.split("\n"):
        if raw.startswith("  - ") or (current_list is not None and raw.startswith("- ")):
            v = raw.lstrip(" -").strip().strip('"').strip("'")
            if current_list is not None:
                current_list.append(v)
            continue
        if ":" not in raw or raw.startswith(" "):
            continue
        key, _, val = raw.partition(":")
        key = key.strip(); val = val.strip()
        if val == "" or val == "|":
            meta[key] = []
            current_key = key
            current_list = meta[key]
        elif val.startswith("[") and val.endswith("]"):
            items = val[1:-1].split(",")
            meta[key] = [i.strip().strip('"').strip("'") for i in items if i.strip()]
            current_list = None
        else:
            meta[key] = val.strip('"').strip("'")
            current_list = None
    return meta, body


def _strip_inline_comment(s: str) -> str:
    """Strip an inline ' # ...' comment, preserving '#' inside quotes."""
    # Find first ' #' that isn't inside quotes — simple heuristic
    in_q = False
    for i, ch in enumerate(s):
        if ch in ('"', "'"):
            in_q = not in_q
        elif ch == "#" and not in_q and (i == 0 or s[i - 1] in (" ", "\t")):
            return s[:i].rstrip()
    return s


def parse_topics_yaml(path: Path) -> dict:
    """Parse simple list-of-strings sections from topics.yaml. Handles inline # comments."""
    out: dict[str, list[str]] = {}
    current: str | None = None
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = _strip_inline_comment(raw.rstrip())
        if not line or line.lstrip().startswith("#"):
            continue
        # Top-level section header: "name:" with no leading whitespace
        if not line.startswith(" ") and line.endswith(":"):
            current = line[:-1].strip()
            out[current] = []
        elif line.startswith("  - ") and current:
            v = line[4:].strip().strip('"').strip("'")
            if v:
                out[current].append(v)
    return out


def has_section(body: str, name: str) -> bool:
    return re.search(rf"^## {re.escape(name)}\b", body, re.MULTILINE) is not None


# ---------------------------------------------------------------------------
# Verify
# ---------------------------------------------------------------------------

def verify() -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    if not TOPICS_YAML.exists():
        errors.append(f"topics.yaml not found at {TOPICS_YAML}")
        return errors, warnings

    vocab = parse_topics_yaml(TOPICS_YAML)
    valid_domains = set(vocab.get("domains", []))
    valid_kinds   = set(vocab.get("kinds", []))
    valid_status  = set(vocab.get("statuses", []))
    valid_owners  = set(vocab.get("owners", []))
    valid_topics  = set(vocab.get("topics", []))

    if not valid_domains or not valid_kinds:
        errors.append("topics.yaml is missing 'domains' or 'kinds' sections")
        return errors, warnings

    article_ids: set[str] = set()
    article_paths: dict[str, Path] = {}

    # ---- Per-article checks ----------------------------------------------
    for path in sorted(ARTICLES_DIR.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        meta, body = parse_frontmatter(text)
        slug = path.stem

        # Required fields
        missing = REQUIRED_FIELDS - set(meta.keys())
        if missing:
            errors.append(f"{path.name}: missing required fields {sorted(missing)}")

        # id matches filename
        aid = meta.get("id", "")
        if aid != slug:
            errors.append(f"{path.name}: id '{aid}' does not equal filename '{slug}'")

        article_ids.add(aid or slug)
        article_paths[aid or slug] = path

        # Enums
        kind = meta.get("kind", "")
        if kind and kind not in valid_kinds:
            errors.append(f"{path.name}: kind '{kind}' not in topics.yaml")

        domain = meta.get("domain", "")
        if domain and domain not in valid_domains:
            errors.append(f"{path.name}: domain '{domain}' not in topics.yaml")

        status = meta.get("status", "")
        if status and status not in valid_status:
            errors.append(f"{path.name}: status '{status}' not in topics.yaml")

        owner = meta.get("owner", "")
        if owner and owner not in valid_owners:
            errors.append(f"{path.name}: owner '{owner}' not in topics.yaml")

        # Topics
        topics = meta.get("topics", []) or []
        for t in topics:
            if t not in valid_topics:
                warnings.append(f"{path.name}: topic '{t}' not in topics.yaml")

        # review_due requirement
        if kind == "known-issue" or status == "provisional":
            if not meta.get("review_due"):
                errors.append(f"{path.name}: kind/status requires review_due (missing)")

        # Body sections
        if not has_section(body, "Answer"):
            errors.append(f"{path.name}: missing ## Answer section")
        if kind == "process" and not has_section(body, "Procedure"):
            warnings.append(f"{path.name}: kind:process should have ## Procedure")
        if kind == "known-issue" and not has_section(body, "Status"):
            warnings.append(f"{path.name}: kind:known-issue should have ## Status")

    # ---- Cross-article: related: integrity --------------------------------
    for path in sorted(ARTICLES_DIR.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        meta, _ = parse_frontmatter(text)
        for rid in meta.get("related", []) or []:
            if rid not in article_ids:
                errors.append(f"{path.name}: related id '{rid}' does not exist")

    # ---- Catalog sync -----------------------------------------------------
    if CATALOG_JSONL.exists():
        catalog_ids: set[str] = set()
        try:
            for line in CATALOG_JSONL.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    catalog_ids.add(json.loads(line).get("id", ""))
        except json.JSONDecodeError as e:
            errors.append(f"catalog.jsonl: JSON parse error — {e}")

        missing_in_catalog = article_ids - catalog_ids
        extra_in_catalog   = catalog_ids - article_ids

        for mid in sorted(missing_in_catalog):
            warnings.append(f"catalog.jsonl: missing entry for '{mid}' — run update-catalog")
        for eid in sorted(extra_in_catalog):
            errors.append(f"catalog.jsonl: orphan entry '{eid}' (no article file)")
    else:
        warnings.append("catalog.jsonl does not exist — run update-catalog")

    return errors, warnings


# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if not ARTICLES_DIR.exists():
        print(f"ERROR: articles directory not found at {ARTICLES_DIR}", file=sys.stderr)
        sys.exit(1)

    errors, warnings = verify()

    n_articles = len(list(ARTICLES_DIR.glob("*.md")))
    print(f"Verified: {n_articles} articles")
    print(f"Warnings: {len(warnings)}")
    print(f"Errors:   {len(errors)}")

    if warnings:
        print("\n--- Warnings ---")
        for w in warnings:
            print(f"  ⚠  {w}")

    if errors:
        print("\n--- Errors ---")
        for e in errors:
            print(f"  ✗  {e}")
        sys.exit(1)

    print("\n✓ OK")
    sys.exit(0)

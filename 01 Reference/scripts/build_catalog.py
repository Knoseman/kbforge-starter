#!/usr/bin/env python3
"""
Catalog builder for 01 Reference knowledge base.

Reads all *.md files in 01 Reference/articles/ and generates:
  - 01 Reference/catalog.jsonl      (machine-readable; one article per line)
  - 01 Reference/catalog.md         (human-readable mirror; auto-generated)
  - 01 Reference/aggregates/known-issues.md
  - 01 Reference/aggregates/contacts.md
  - 01 Reference/aggregates/comparisons.md
  - 01 Reference/aggregates/environments.md

Run from any directory:
  python3 "01 Reference/scripts/build_catalog.py"
"""

import json
import re
import sys
from pathlib import Path

# Paths relative to this script's location (scripts/ → 01 Reference/)
REFERENCE_DIR = Path(__file__).parent.parent
ARTICLES_DIR  = REFERENCE_DIR / "articles"
AGGREGATES_DIR = REFERENCE_DIR / "aggregates"
CATALOG_JSONL  = REFERENCE_DIR / "catalog.jsonl"
CATALOG_MD     = REFERENCE_DIR / "catalog.md"


# ---------------------------------------------------------------------------
# Frontmatter parser (no external deps)
# ---------------------------------------------------------------------------

def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Parse YAML frontmatter from a markdown string. Returns (meta dict, body)."""
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    fm_text = text[4:end]
    body = text[end + 4:].lstrip("\n")

    meta: dict = {}
    current_key: str | None = None
    current_list: list | None = None

    for raw_line in fm_text.split("\n"):
        if raw_line.startswith("  - ") or (current_list is not None and raw_line.startswith("- ")):
            val = raw_line.lstrip(" -").strip().strip('"').strip("'")
            if current_list is not None:
                current_list.append(val)
            continue

        if ":" not in raw_line or raw_line.startswith(" "):
            continue

        key, _, val = raw_line.partition(":")
        key = key.strip()
        val = val.strip()

        if val == "" or val == "|":
            meta[key] = []
            current_key = key
            current_list = meta[key]
        elif val.startswith("[") and val.endswith("]"):
            items = val[1:-1].split(",")
            meta[key] = [i.strip().strip('"').strip("'") for i in items if i.strip()]
            current_key = key
            current_list = None
        else:
            meta[key] = val.strip('"').strip("'")
            current_key = key
            current_list = None

    return meta, body


def extract_section(body: str, section: str) -> str:
    """Extract the prose content of a specific ## Section from the body."""
    pattern = rf"^## {re.escape(section)}\b\n(.*?)((?=\n## )|\Z)"
    m = re.search(pattern, body, re.DOTALL | re.MULTILINE)
    return m.group(1).strip() if m else ""


# ---------------------------------------------------------------------------
# Catalog build
# ---------------------------------------------------------------------------

def build_catalog() -> list[dict]:
    articles: list[dict] = []

    for path in sorted(ARTICLES_DIR.glob("*.md")):
        if path.name.startswith("_"):
            continue
        text = path.read_text(encoding="utf-8")
        meta, body = parse_frontmatter(text)

        art_id = meta.get("id", path.stem)
        if not art_id:
            print(f"WARNING: {path.name} has no 'id' field — skipping", file=sys.stderr)
            continue

        entry: dict = {
            "id":          art_id,
            "title":       meta.get("title", ""),
            "kind":        meta.get("kind", "reference"),
            "domain":      meta.get("domain", ""),
            "topics":      meta.get("topics", []),
            "status":      meta.get("status", "current"),
            "updated":     meta.get("updated", ""),
            "review_due":  meta.get("review_due", ""),
            "owner":       meta.get("owner", "ai"),
            "related":     meta.get("related", []),
            "summary":     meta.get("summary", ""),
            "answers":     meta.get("answers", []),
            "created_by":  meta.get("created_by", ""),
        }
        if meta.get("superseded_by"):
            entry["superseded_by"] = meta["superseded_by"]

        entry["_body"]   = body
        entry["_answer"] = extract_section(body, "Answer")
        entry["_status_section"] = extract_section(body, "Status")

        articles.append(entry)

    print(f"Found {len(articles)} articles in {ARTICLES_DIR}")
    return articles


# ---------------------------------------------------------------------------
# Writers
# ---------------------------------------------------------------------------

def write_catalog_jsonl(articles: list[dict]) -> None:
    with open(CATALOG_JSONL, "w", encoding="utf-8") as f:
        for art in articles:
            public = {k: v for k, v in art.items() if not k.startswith("_")}
            public = {k: v for k, v in public.items() if v not in ("", [], None)}
            f.write(json.dumps(public, ensure_ascii=False) + "\n")
    print(f"catalog.jsonl: written ({CATALOG_JSONL})")


def write_catalog_md(articles: list[dict]) -> None:
    by_domain: dict[str, list] = {}
    for art in articles:
        by_domain.setdefault(art["domain"] or "other", []).append(art)

    lines = [
        "---",
        "type: index",
        "generated: true",
        "---",
        "",
        "# Reference Catalog",
        "",
        f"_Auto-generated by `build_catalog.py`. {len(articles)} articles. **Use `catalog.jsonl` for agent lookups — do not read this file in full.**_",
        "",
    ]

    for domain in sorted(by_domain):
        arts = sorted(by_domain[domain], key=lambda a: a["id"])
        lines.append(f"## {domain}")
        lines.append("")
        lines.append("| id | kind | summary |")
        lines.append("|---|---|---|")
        for art in arts:
            stale = " ⚠️" if art.get("status") in ("outdated", "superseded", "provisional") else ""
            lines.append(f"| `{art['id']}`{stale} | {art['kind']} | {art['summary']} |")
        lines.append("")

    CATALOG_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"catalog.md: written")


def write_aggregates(articles: list[dict]) -> None:
    AGGREGATES_DIR.mkdir(exist_ok=True)

    # --- known-issues.md ---
    issues = [a for a in articles if a.get("kind") == "known-issue"]
    lines = [
        "# Known Issues",
        "",
        "_Auto-generated by `build_catalog.py`. Do not edit — changes will be overwritten._",
        "",
    ]
    for art in sorted(issues, key=lambda a: a["id"]):
        rd = f" · review due: {art['review_due']}" if art.get("review_due") else ""
        lines += [
            f"## {art['title']}",
            f"`{art['id']}`{rd} · status: {art.get('status', 'current')}",
            "",
            art["_answer"] or art["summary"],
            "",
            f"→ Full article: `{art['id']}`",
            "",
        ]
        if art.get("_status_section"):
            lines += [art["_status_section"], ""]
    (AGGREGATES_DIR / "known-issues.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"aggregates/known-issues.md: {len(issues)} articles")

    # --- contacts.md ---
    contact_arts = [a for a in articles if a.get("kind") == "contacts"]
    lines = [
        "# Contacts and Escalation Paths",
        "",
        "_Auto-generated by `build_catalog.py`. Do not edit — edit the source articles instead._",
        "",
    ]
    for art in sorted(contact_arts, key=lambda a: a["id"]):
        facts = extract_section(art["_body"], "Facts")
        lines += [
            f"## {art['title']}",
            f"`{art['id']}`",
            "",
            art["_answer"] or art["summary"],
            "",
        ]
        if facts:
            lines += [facts, ""]
        lines += [f"→ Full article: `{art['id']}`", ""]
    (AGGREGATES_DIR / "contacts.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"aggregates/contacts.md: {len(contact_arts)} articles")

    # --- comparisons.md ---
    comp_arts = [a for a in articles if a.get("kind") == "comparison"]
    lines = [
        "# Comparisons",
        "",
        "_Auto-generated by `build_catalog.py`. Do not edit._",
        "",
    ]
    for art in sorted(comp_arts, key=lambda a: a["id"]):
        lines += [
            f"## {art['title']}",
            f"`{art['id']}`",
            "",
            art["_answer"] or art["summary"],
            "",
            f"→ Full article: `{art['id']}`",
            "",
        ]
    (AGGREGATES_DIR / "comparisons.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"aggregates/comparisons.md: {len(comp_arts)} articles")

    # --- environments.md ---
    env_topics = {
        "test-environments", "sandbox", "endpoints", "authentication",
        "credentials", "api-token",
    }
    env_arts = [a for a in articles if set(a.get("topics", [])) & env_topics]
    lines = [
        "# Environments, Base URLs and Authentication",
        "",
        "_Auto-generated by `build_catalog.py`. Do not edit. For full details open individual articles._",
        "",
    ]
    for art in sorted(env_arts, key=lambda a: a["id"]):
        lines += [
            f"## {art['title']}",
            f"`{art['id']}`",
            "",
            art["_answer"] or art["summary"],
            "",
            f"→ Full article: `{art['id']}`",
            "",
        ]
    (AGGREGATES_DIR / "environments.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"aggregates/environments.md: {len(env_arts)} articles")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if not ARTICLES_DIR.exists():
        print(f"ERROR: articles directory not found at {ARTICLES_DIR}", file=sys.stderr)
        sys.exit(1)

    articles = build_catalog()
    if not articles:
        print("No articles found — nothing written.", file=sys.stderr)
        sys.exit(1)

    write_catalog_jsonl(articles)
    write_catalog_md(articles)
    write_aggregates(articles)
    print("\nDone.")

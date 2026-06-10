#!/usr/bin/env python3
"""
Skills index builder.

Reads all *.md files in 04 Skills/skills/ and generates:
  - 04 Skills/skills.jsonl              (machine-readable index)
  - 04 Skills/aggregates/chains.md      (auto-generated chain map)
  - 04 Skills/aggregates/fast-paths.md  (human-readable fast path table)
  - .claude/PRIME.md                    (Claude session start file)
  - 04 Skills/PRIME.md                  (Kimi session start file)

Run from anywhere:
  python3 "04 Skills/scripts/build_skills_index.py"
"""

import json
import re
import sys
from pathlib import Path

SKILLS_DIR_ROOT  = Path(__file__).parent.parent           # 04 Skills/
SKILLS_DIR       = SKILLS_DIR_ROOT / "skills"
AGGREGATES_DIR   = SKILLS_DIR_ROOT / "aggregates"
INDEX_JSONL      = SKILLS_DIR_ROOT / "skills.jsonl"
VAULT_ROOT       = SKILLS_DIR_ROOT.parent                  # kbforge-starter root
CLAUDE_DIR       = VAULT_ROOT / ".claude"
PRO_SKILLS_DIR   = VAULT_ROOT / "pro-pack" / "skills"


# ---------------------------------------------------------------------------
# Frontmatter parser
# ---------------------------------------------------------------------------

def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Parse YAML frontmatter. Returns (meta, body). Supports nested dicts one level deep."""
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
    current_dict: dict | None = None

    for raw in fm.split("\n"):
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue

        # Indented list item under a nested key  (touches: \n   reads: [...])
        if raw.startswith("    - ") and current_dict is not None and current_key:
            current_dict.setdefault(current_key, []).append(raw.strip()[2:].strip('"').strip("'"))
            continue

        # Nested dict key (e.g. inside touches:)
        if raw.startswith("  ") and ":" in raw and current_dict is not None:
            k, _, v = raw.strip().partition(":")
            k = k.strip(); v = v.strip()
            if v.startswith("[") and v.endswith("]"):
                items = v[1:-1].split(",")
                current_dict[k] = [i.strip().strip('"').strip("'") for i in items if i.strip()]
            elif v == "":
                current_dict[k] = []
                current_key = k
            else:
                current_dict[k] = v.strip('"').strip("'")
            continue

        # Top-level list item
        if raw.startswith("  - ") or (current_list is not None and raw.startswith("- ")):
            val = raw.lstrip(" -").strip().strip('"').strip("'")
            # If we have an empty dict waiting (e.g. triggers: followed by list items),
            # convert it to a list first
            if current_list is None and current_dict is not None and current_key and current_key in meta:
                if isinstance(meta.get(current_key), dict) and not meta[current_key]:
                    meta[current_key] = []
                    current_list = meta[current_key]
                    current_dict = None
            if current_list is not None:
                current_list.append(val)
            continue

        # Top-level key:value
        if ":" in raw and not raw.startswith(" "):
            key, _, val = raw.partition(":")
            key = key.strip(); val = val.strip()
            current_dict = None

            if val == "":
                # Could be list or nested dict — assume dict; convert later if list items appear
                meta[key] = {}
                current_dict = meta[key]
                current_key = key
                current_list = None
            elif val.startswith("[") and val.endswith("]"):
                items = val[1:-1].split(",")
                meta[key] = [i.strip().strip('"').strip("'") for i in items if i.strip()]
                current_list = None
                current_dict = None
            else:
                meta[key] = val.strip('"').strip("'")
                current_list = None
                current_dict = None

        # If we saw a top-level key with no value and next line is a list,
        # convert the empty dict to a list on the fly:
        if raw.startswith("  - ") and current_key in meta and isinstance(meta.get(current_key), dict) and not meta[current_key]:
            meta[current_key] = []
            current_list = meta[current_key]
            current_dict = None
            current_list.append(raw.lstrip(" -").strip().strip('"').strip("'"))

    # Post-process: empty dicts that should be lists stay as dicts; we accept either shape.
    return meta, body


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------

def _load_skill(path: Path) -> dict | None:
    """Parse a single skill file and return its index entry."""
    text = path.read_text(encoding="utf-8")
    meta, body = parse_frontmatter(text)

    sid = meta.get("id", path.stem)
    if not sid:
        print(f"WARNING: {path.name} has no 'id' — skipping", file=sys.stderr)
        return None

    entry = {
        "id":           sid,
        "title":        meta.get("title", ""),
        "kind":         meta.get("kind", ""),
        "inputs":       meta.get("inputs", []),
        "outputs":      meta.get("outputs", []),
        "chains_to":    meta.get("chains_to", []),
        "chains_from":  meta.get("chains_from", []),
        "triggers":     meta.get("triggers", []),
        "summary":      meta.get("summary", ""),
        "success_rate": meta.get("success_rate", "unrated"),
        "fast_path":    meta.get("fast_path", False),
        "collapsed_from": meta.get("collapsed_from", []),
    }
    touches = meta.get("touches")
    if isinstance(touches, dict) and touches:
        entry["touches"] = touches

    return entry


def build_index() -> list[dict]:
    skills: list[dict] = []

    if not SKILLS_DIR.exists():
        print(f"ERROR: skills directory not found at {SKILLS_DIR}", file=sys.stderr)
        sys.exit(1)

    # Load free-tier skills
    for path in sorted(SKILLS_DIR.glob("*.md")):
        entry = _load_skill(path)
        if entry:
            skills.append(entry)

    # Load pro-tier skills if present
    if PRO_SKILLS_DIR and PRO_SKILLS_DIR.exists():
        for path in sorted(PRO_SKILLS_DIR.glob("*.md")):
            entry = _load_skill(path)
            if entry:
                entry["pro"] = True
                skills.append(entry)

    return skills


# ---------------------------------------------------------------------------
# Writers
# ---------------------------------------------------------------------------

def write_index(skills: list[dict]) -> None:
    with open(INDEX_JSONL, "w", encoding="utf-8") as f:
        for s in skills:
            public = {k: v for k, v in s.items() if v not in ("", [], None, {}, False)}
            f.write(json.dumps(public, ensure_ascii=False) + "\n")
    print(f"skills.jsonl: {len(skills)} skills")


def write_chains(skills: list[dict]) -> None:
    AGGREGATES_DIR.mkdir(exist_ok=True)
    by_id = {s["id"]: s for s in skills}

    # Build directed edges
    edges: list[tuple[str, str]] = []
    for s in skills:
        for tgt in s.get("chains_to", []):
            edges.append((s["id"], tgt))

    incoming: dict[str, list[str]] = {s["id"]: [] for s in skills}
    for src, tgt in edges:
        if tgt in incoming:
            incoming[tgt].append(src)

    roots = [s["id"] for s in skills if not incoming.get(s["id"]) and s.get("chains_to")]
    roots.sort()

    lines = [
        "# Skill Chains",
        "",
        "_Auto-generated by `build_skills_index.py`. Do not edit — changes will be overwritten._",
        "",
        "## All edges",
        "",
    ]
    for src, tgt in sorted(set(edges)):
        lines.append(f"- `{src}` → `{tgt}`")
    lines.append("")

    lines += [
        "## By kind",
        "",
    ]
    by_kind: dict[str, list[dict]] = {}
    for s in skills:
        by_kind.setdefault(s.get("kind", "other"), []).append(s)
    for kind in sorted(by_kind):
        lines.append(f"### {kind}")
        lines.append("")
        for s in sorted(by_kind[kind], key=lambda x: x["id"]):
            ct = ", ".join(f"`{t}`" for t in s.get("chains_to", [])) or "—"
            lines.append(f"- `{s['id']}` — chains to: {ct}")
        lines.append("")

    lines += [
        "## Common chains (entry points)",
        "",
    ]
    if roots:
        for r in roots:
            lines.append(f"- starting from `{r}`:")
            seen: set[str] = set()

            def walk(node: str, depth: int) -> None:
                if node in seen:
                    lines.append(f"{'  ' * (depth + 1)}- `{node}` (already shown)")
                    return
                seen.add(node)
                children = by_id.get(node, {}).get("chains_to", [])
                if not children:
                    return
                for c in children:
                    lines.append(f"{'  ' * (depth + 1)}- → `{c}`")
                    walk(c, depth + 1)

            walk(r, 0)
        lines.append("")
    else:
        lines.append("_(No skill chains define a clear root — all skills are reachable from each other.)_")
        lines.append("")

    (AGGREGATES_DIR / "chains.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"aggregates/chains.md: written")


def write_fast_paths(skills: list[dict]) -> None:
    """Generate human-readable fast-paths.md from skills with fast_path: true."""
    AGGREGATES_DIR.mkdir(exist_ok=True)
    fast_skills = [s for s in skills if s.get("fast_path")]

    lines = [
        "# Fast Paths",
        "",
        "_Auto-generated by `build_skills_index.py`. Do not edit — changes will be overwritten._",
        "",
        "These skills are loaded directly for common requests — no triage needed.",
        "",
        "| Skill | Kind | Triggers | Summary |",
        "|-------|------|----------|---------|",
    ]
    for s in sorted(fast_skills, key=lambda x: x["id"]):
        triggers = ", ".join(f"`{t}`" for t in s.get("triggers", [])) or "—"
        collapsed = ""
        if s.get("collapsed_from"):
            collapsed = f" _(collapsed: {', '.join(s['collapsed_from'])})_"
        pro_badge = " (Pro)" if s.get("pro") else ""
        lines.append(f"| `{s['id']}`{pro_badge} | {s.get('kind', '—')} | {triggers} | {s.get('summary', '—')}{collapsed} |")

    lines += [
        "",
        "## Fallback",
        "",
        "If no fast path matches, use `triage` skill to classify and route.",
        "",
    ]

    (AGGREGATES_DIR / "fast-paths.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"aggregates/fast-paths.md: written ({len(fast_skills)} fast paths)")


def write_prime(skills: list[dict], target_path: Path, title: str, ai_tool: str) -> None:
    """Generate a PRIME.md session start file for a specific AI tool."""
    fast_skills = [s for s in skills if s.get("fast_path")]

    lines = [
        f"# {title} — Session Prime",
        "",
        f"You are in a KBForge knowledge base vault. This PRIME.md is for {ai_tool}.",
        "",
        "## Fast Paths (load ONE skill — no triage needed)",
        "",
        "| User says | Skill | Action |",
        "|-----------|-------|--------|",
    ]

    for s in sorted(fast_skills, key=lambda x: x["id"]):
        triggers = s.get("triggers", [])
        trigger_str = triggers[0] if triggers else s["id"]
        action = s.get("summary", "Perform skill")
        # Truncate long summaries
        if len(action) > 60:
            action = action[:57] + "..."
        pro_badge = " (Pro)" if s.get("pro") else ""
        lines.append(f"| \"{trigger_str}\" | `{s['id']}`{pro_badge} | {action} |")

    lines += [
        "",
        "## Fallback",
        "",
        "If uncertain or no fast path matches, load `triage` skill and proceed normally.",
        "",
        "## Always",
        "",
        "- `(C)` prefix on every AI-generated file.",
        "- Ask before editing any file without a `(C)` prefix.",
        "- Source everything. Cite the specific doc or article via `[[wikilinks]]`.",
        "- Log gaps. Unanswerable questions → `05 Iteration Logs/KB Gaps.md`.",
        "- File synthesised answers. Non-trivial synthesis → new `(C)` reference article.",
        "- Account context. Before drafting partner/client reply, read `03 Accounts/[AccountName].md` if it exists.",
        "",
        "## Status",
        "",
        f"> {len(skills)} skills ({len(fast_skills)} fast paths). Pro skills: {sum(1 for s in skills if s.get('pro'))}. Last updated: — run `build_skills_index.py` to refresh.",
    ]

    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"{target_path}: written")


# ---------------------------------------------------------------------------
# Entry
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    skills = build_index()
    if not skills:
        print("No skills found.", file=sys.stderr)
        sys.exit(1)

    write_index(skills)
    write_chains(skills)
    write_fast_paths(skills)

    # PRIME.md for Claude (if .claude/ exists or we create it)
    write_prime(skills, CLAUDE_DIR / "PRIME.md", "KBForge", "Claude Code")

    # PRIME.md for Kimi
    write_prime(skills, SKILLS_DIR_ROOT / "PRIME.md", "KBForge", "Kimi")

    print(f"\nDone. {len(skills)} skills indexed.")
    print(f"  Kimi:    {INDEX_JSONL}")
    print(f"  Claude:  {CLAUDE_DIR / 'PRIME.md'}")

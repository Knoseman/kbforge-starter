#!/usr/bin/env python3
"""
KBForge init script.

Personalises a fresh kbforge-starter clone for your domain:
  1. Prompts for domain slug, team name, and seed topics
  2. Replaces placeholder values in topics.yaml and AGENTS.md files
  3. Removes Acme demo articles, account profile, and example log entries
  4. Scaffolds empty starting files with your domain
  5. Runs build_catalog.py and build_skills_index.py
  6. Prints a ready checklist

Run once after cloning:
  python3 init.py

Python 3.10+ required. No external dependencies.
"""

import re
import shutil
import subprocess
import sys
from pathlib import Path

VAULT = Path(__file__).parent

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def prompt(question: str, example: str = "", required: bool = True) -> str:
    hint = f" (e.g. {example})" if example else ""
    while True:
        val = input(f"{question}{hint}: ").strip()
        if val:
            return val
        if not required:
            return ""
        print("  ✗ This field is required.")


def prompt_list(question: str, example: str = "", min_count: int = 1, max_count: int = 5) -> list[str]:
    hint = f" (e.g. {example})" if example else ""
    print(f"{question}{hint}")
    print(f"  Enter {min_count}–{max_count} items, one per line. Empty line to finish.")
    items: list[str] = []
    while len(items) < max_count:
        val = input(f"  {len(items) + 1}: ").strip()
        if not val:
            if len(items) >= min_count:
                break
            print(f"  ✗ Please enter at least {min_count} item(s).")
            continue
        slug = re.sub(r"[^a-z0-9-]", "-", val.lower()).strip("-")
        slug = re.sub(r"-+", "-", slug)
        items.append(slug)
    return items


def slugify(s: str) -> str:
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9-]", "-", s.lower())).strip("-")


def replace_in_file(path: Path, replacements: dict[str, str]) -> bool:
    """Apply a dict of {old: new} substitutions to a file. Returns True if changed."""
    text = path.read_text(encoding="utf-8")
    new_text = text
    for old, new in replacements.items():
        new_text = new_text.replace(old, new)
    if new_text != text:
        path.write_text(new_text, encoding="utf-8")
        return True
    return False


def run_script(script_path: Path) -> bool:
    """Run a Python script. Returns True on success."""
    result = subprocess.run(
        [sys.executable, str(script_path)],
        capture_output=True,
        text=True,
        cwd=str(VAULT),
    )
    if result.returncode != 0:
        print(f"  ✗ {script_path.name} failed:\n{result.stderr.strip()}")
        return False
    # Print last meaningful line
    last = [l for l in result.stdout.strip().splitlines() if l.strip()]
    if last:
        print(f"  ✓ {last[-1]}")
    return True


# ---------------------------------------------------------------------------
# Steps
# ---------------------------------------------------------------------------

def collect_inputs() -> dict:
    print("\n" + "=" * 60)
    print("  KBForge — init")
    print("=" * 60)
    print("""
This script personalises your KB for your domain.
It will replace placeholder content and scaffold your starting files.
""")

    domain = slugify(prompt(
        "1. Domain slug  (your primary knowledge area)",
        example="payments-api, support-kb, acme-platform",
    ))

    team = prompt(
        "2. Team / company name",
        example="Acme Corp, My Team, Contoso",
    )

    print()
    topics = prompt_list(
        "3. Seed topics  (key concepts you'll document)",
        example="authentication, webhooks, onboarding",
        min_count=3,
        max_count=5,
    )

    print()
    print(f"  Domain slug : {domain}")
    print(f"  Team name   : {team}")
    print(f"  Topics      : {', '.join(topics)}")
    print()
    confirm = input("Looks good? (y/n): ").strip().lower()
    if confirm not in ("y", "yes"):
        print("Aborted — re-run init.py to start over.")
        sys.exit(0)

    return {"domain": domain, "team": team, "topics": topics}


def patch_topics_yaml(domain: str, topics: list[str]) -> None:
    path = VAULT / "01 Reference" / "topics.yaml"
    text = path.read_text(encoding="utf-8")

    # Replace demo domains block
    demo_domains = "  - acme-api          # example: replace with your API or product domain\n  - integrations      # example: third-party integration guides\n  - ops               # example: operational procedures and contacts\n  - ai-practices      # example: AI tooling and KB maintenance practices"
    new_domains = f"  - {domain}\n  - ops\n  - ai-practices"
    text = text.replace(demo_domains, new_domains)

    # Append seed topics under the existing topics section (before the AI Practices block)
    seed_block = "\n".join(f"  - {t}" for t in topics)
    insert_marker = "  # Auth / API fundamentals"
    seed_section = f"  # Your seed topics\n{seed_block}\n\n  # Auth / API fundamentals"
    text = text.replace(insert_marker, seed_section, 1)

    path.write_text(text, encoding="utf-8")
    print(f"  ✓ topics.yaml — domain set to '{domain}', {len(topics)} seed topics added")


def patch_agents_md_files(domain: str, team: str) -> None:
    # Order matters: replace longer/more-specific strings first.
    # Use word-boundary-aware replacements to avoid partial matches inside other words.
    agents_files = list(VAULT.rglob("AGENTS.md"))
    changed = 0
    for f in agents_files:
        text = f.read_text(encoding="utf-8")
        new_text = text
        # 1. Team name "Acme" — case-sensitive, do this FIRST before the
        #    case-insensitive bareword match catches it.
        new_text = new_text.replace("Acme", team)
        # 2. Exact phrase "acme-api"
        new_text = new_text.replace("acme-api", domain)
        # 3. Exact word "acme" — case-insensitive, but preserve surrounding punctuation/spaces.
        #    We use a regex with negative lookbehind/ahead for word chars so "macme" doesn't match.
        import re as _re
        new_text = _re.sub(r"(?<![a-zA-Z0-9_-])acme(?![a-zA-Z0-9_-])", domain, new_text, flags=_re.IGNORECASE)
        if new_text != text:
            f.write_text(new_text, encoding="utf-8")
            changed += 1
    print(f"  ✓ AGENTS.md files — {changed}/{len(agents_files)} updated")


def remove_demo_content(domain: str, team: str) -> None:
    # Remove Acme demo articles
    removed_articles = 0
    for f in (VAULT / "01 Reference" / "articles").glob("acme-api.*.md"):
        f.unlink()
        removed_articles += 1
    print(f"  ✓ Removed {removed_articles} demo article(s)")

    # Remove Acme demo account profile
    demo_account = VAULT / "03 Accounts" / "(C) Acme Corp.md"
    if demo_account.exists():
        demo_account.unlink()
        print(f"  ✓ Removed demo account profile")

    # Clear example entries from iteration logs (leave headers intact)
    gaps_path = VAULT / "05 Iteration Logs" / "KB Gaps.md"
    if gaps_path.exists():
        text = gaps_path.read_text(encoding="utf-8")
        # Remove everything from <!-- Example entry --> onward
        cut = text.find("<!-- Example entry")
        if cut != -1:
            gaps_path.write_text(text[:cut].rstrip() + "\n", encoding="utf-8")
            print(f"  ✓ Cleared example entries from KB Gaps.md")

    ingestion_path = VAULT / "05 Iteration Logs" / "Ingestion Log.md"
    if ingestion_path.exists():
        text = ingestion_path.read_text(encoding="utf-8")
        cut = text.find("<!-- Example entry")
        if cut != -1:
            ingestion_path.write_text(text[:cut].rstrip() + "\n", encoding="utf-8")
            print(f"  ✓ Cleared example entries from Ingestion Log.md")


def scaffold_starting_files(domain: str, team: str, topics: list[str]) -> None:
    today = __import__("datetime").date.today().isoformat()

    # Create a placeholder account profile for the user's team
    account_path = VAULT / "03 Accounts" / f"(C) {team}.md"
    account_path.write_text(f"""---
account: {team}
integration_type: api
product: {domain}
phase: discovery
status: active
updated: {today}
contacts:
  technical: ""
  commercial: ""
kb_articles: []
blockers: []
---

# {team}

Add context about this account here.
""", encoding="utf-8")
    print(f"  ✓ Scaffolded account profile: 03 Accounts/(C) {team}.md")

    # Create a placeholder first article
    first_id = f"{domain}.overview"
    article_path = VAULT / "01 Reference" / "articles" / f"(C) {first_id}.md"
    topics_yaml = "[" + ", ".join(topics[:3]) + "]" if topics else "[]"
    article_path.write_text(f"""---
id: {first_id}
title: {domain.replace("-", " ").title()} — Overview
kind: reference
domain: {domain}
topics: {topics_yaml}
status: provisional
updated: {today}
review_due: {today}
owner: ai
provenance: []
related: []
summary: "Replace this summary with a one-line answer to the most common question about {domain}."
answers:
  - "What is {domain}?"
  - "Give me an overview of {domain}"
---

## Answer
Replace this with a 1–3 sentence answer to the most common question about {domain}.

## Facts
- Add key facts, parameters, and reference data here.

## See also
""", encoding="utf-8")
    print(f"  ✓ Scaffolded first article: (C) {first_id}.md (status: provisional — fill it in)")


def rebuild_indexes() -> None:
    print("\nRebuilding indexes...")
    catalog_script = VAULT / "01 Reference" / "scripts" / "build_catalog.py"
    skills_script = VAULT / "04 Skills" / "scripts" / "build_skills_index.py"

    if catalog_script.exists():
        run_script(catalog_script)
    else:
        print(f"  ⚠ {catalog_script} not found — skipping")

    if skills_script.exists():
        run_script(skills_script)
    else:
        print(f"  ⚠ {skills_script} not found — skipping")


def print_checklist(domain: str, team: str) -> None:
    print("""
""" + "=" * 60 + """
  You're ready.
""" + "=" * 60 + f"""

Next steps:

  [ ] Open this folder as a vault in Obsidian

  [ ] Drop your first raw source into 00 Raw Sources/
      — a transcript, API doc, meeting notes, or chat log

  [ ] In Claude Code, run:
        ingest this: [[00 Raw Sources/your-file.md]]

  [ ] Ask your first question:
        What does the KB say about {domain}?

  [ ] Fill in the placeholder article:
        01 Reference/articles/{domain}.overview.md
      (marked status: provisional — update it after your first ingest)

  [ ] Update the status line in AGENTS.md once you have real articles.

Full walkthrough: SETUP.md
""")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    inputs = collect_inputs()
    domain = inputs["domain"]
    team = inputs["team"]
    topics = inputs["topics"]

    print("\nApplying changes...\n")

    patch_topics_yaml(domain, topics)
    patch_agents_md_files(domain, team)
    remove_demo_content(domain, team)
    scaffold_starting_files(domain, team, topics)
    rebuild_indexes()
    print_checklist(domain, team)


if __name__ == "__main__":
    main()

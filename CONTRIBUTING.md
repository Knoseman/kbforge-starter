# Contributing to KBForge

Thanks for your interest in contributing. KBForge is an open-core project — the skeleton and free-tier skills are MIT-licensed and community-maintained.

---

## What you can contribute

- **Bug fixes** — broken scripts, incorrect AGENTS.md instructions, wrong schema defaults
- **Skill improvements** — better procedures, clearer rating criteria, improved routing in `triage`
- **Documentation** — clearer SETUP.md steps, better examples, typo fixes
- **New free-tier skills** — if you've built a skill that fits the core ingest-and-answer loop and want to share it
- **Translations** — AGENTS.md files and skill procedures in other languages

## What belongs in the Pro pack (not here)

Advanced skills (draft-response, kb-gaps, lint, uat-prep, etc.) are part of the paid Pro pack and are not open for community contribution at this time.

---

## How to contribute

1. **Fork** the repo and create a branch from `master`.
2. **Make your change.** Keep it focused — one fix or improvement per PR.
3. **Test your change** by running `init.py` on a fresh clone to confirm setup still works end-to-end.
4. **Validate with the test suite**: Run `python -m unittest discover tests` to ensure your changes didn't break core blueprint functionality or introduce restricted terms.
5. If you edited a skill, run `python3 "04 Skills/scripts/build_skills_index.py"` and commit the updated `skills.jsonl`.
6. If you added or changed articles, run `python3 "01 Reference/scripts/build_catalog.py"` and commit the updated `catalog.jsonl`.
7. **Open a pull request** with a clear description of what changed and why.

---

## Testing infrastructure

We include a test suite in `tests/` to help you verify that your knowledge base maintains its architectural integrity. If you add new skills or modify the `init.py` logic, running these tests will confirm your changes haven't broken the core automation.

---

## Code style

- Python scripts: stdlib only, no external dependencies, Python 3.10+
- Markdown: follow the article body structure defined in `01 Reference/AGENTS.md`
- YAML: lowercase keys, hyphenated values

## Reporting issues

Open a GitHub issue with:
- What you expected to happen
- What actually happened
- Steps to reproduce (including your OS, Python version, and Obsidian version if relevant)

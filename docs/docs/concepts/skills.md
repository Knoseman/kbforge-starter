# Skills

Skills are reusable AI workflows defined as Markdown files. They live in `04 Skills/skills/` and tell the AI exactly how to perform a task — no improvisation, no drift.

---

## What is a skill

A skill is a Markdown file with YAML frontmatter that declares:

- **What it does** (title, summary)
- **When to use it** (triggers)
- **What it reads and writes** (touches)
- **How to do it** (procedure)
- **What success looks like** (rating)

Example: `ingest-source.md` tells the AI how to turn a raw transcript into structured KB articles. The skill specifies 13 steps, from verifying the source to moving it to Archive.

---

## Skill frontmatter schema

```yaml
---
id: skill-name
title: Human-readable title
kind: capture | synthesis | quality | output
inputs: [what it needs]
outputs: [what it produces]
chains_to: [skills that typically follow]
chains_from: [skills that typically precede]
touches:
  reads: [glob patterns]
  writes: [glob patterns]
triggers:
  - "natural language phrase 1"
  - "natural language phrase 2"
success_rate: unrated | high | medium | low
summary: "One-line description."
---
```

| Field | Description |
|-------|-------------|
| `id` | Unique skill identifier |
| `kind` | `capture` (ingest), `synthesis` (answer/build), `quality` (lint/verify), `output` (draft/respond) |
| `inputs` | What the skill needs to run (file paths, questions, etc.) |
| `outputs` | What the skill produces |
| `chains_to` | Skills that typically run after this one |
| `chains_from` | Skills that typically run before this one |
| `touches` | Files the skill reads and writes |
| `triggers` | Natural-language phrases that should activate this skill |
| `success_rate` | Track how well the skill performs over time |

---

## How skills are used

When you tell the AI something like "process this source," the AI:

1. Checks `triggers:` across all skills
2. Loads the matching skill (e.g. `ingest-source`)
3. Follows the procedure exactly
4. Chains to the next skill if specified (e.g. `update-catalog`)

This means:

- **Consistency:** The same request always follows the same workflow
- **Auditability:** Every action is defined in a file you can read and edit
- **Extensibility:** Add new skills by writing new Markdown files

---

## Skill index

`build_skills_index.py` generates `skills.jsonl` — a catalog of all skills, analogous to `catalog.jsonl` for articles. The AI can grep this to find the right skill for a request.

---

## Free vs Pro skills

The free tier includes 5 core skills:

| Skill | Kind | Purpose |
|-------|------|---------|
| `triage` | capture | Classify input and route to the right skill |
| `clean-source` | capture | Sanitize raw sources before ingestion |
| `ingest-source` | capture | Extract articles from cleaned sources |
| `answer-question` | synthesis | Look up and cite answers from the KB |
| `update-catalog` | quality | Rebuild `catalog.jsonl` after changes |

The Pro pack adds 8 power skills:

| Skill | Kind | Purpose |
|-------|------|---------|
| `batch-ingest-sources` | capture | Process multiple sources in one pass |
| `build-glossary` | synthesis | Auto-generate glossary from definitions |
| `draft-response` | output | Write partner/client replies grounded in KB |
| `kb-gaps` | quality | Report on unanswered questions and coverage gaps |
| `lint` | quality | Find stale articles and orphaned content |
| `log-issue` | capture | Capture and track partner issues |
| `uat-prep` | output | Build UAT checklists for partner onboarding |
| `verify-catalog` | quality | Schema validation for all articles |

See [Pro Tier](../pro.md) for details.

# Frontmatter Schema

Every KBForge article uses YAML frontmatter to declare its metadata. This frontmatter is what makes the articles machine-readable and grep-searchable.

---

## Required fields

```yaml
---
id: domain.slug
title: Human-readable title
kind: reference
domain: domain-name
topics: [tag1, tag2]
status: current
updated: YYYY-MM-DD
owner: ai
summary: "One-line answer to the most common question."
answers:
  - "Natural language question 1"
  - "Natural language question 2"
---
```

| Field | Description |
|-------|-------------|
| `id` | Unique identifier. Format: `domain.slug` (e.g. `api.auth`, `support.onboarding`) |
| `title` | Human-readable title. Used in citations and the catalog. |
| `kind` | `reference` (default), `known-issue`, `how-to`, `overview` |
| `domain` | Must exist in `01 Reference/topics.yaml` → `domains` |
| `topics` | Must exist in `01 Reference/topics.yaml` → `topics` |
| `status` | `current`, `draft`, or `archived` |
| `updated` | Last modification date. ISO format: `YYYY-MM-DD` |
| `owner` | `ai` (AI-generated) or `human` (hand-written) |
| `summary` | One-line answer. This is what the AI reads first when deciding which article to open. |
| `answers` | 2–5 natural-language questions this article answers. The AI greps these before opening the file. |

---

## Optional fields

```yaml
review_due: YYYY-MM-DD        # Required for kind: known-issue
provenance:
  - "[[00 Raw Sources/meeting-2026-06-01.md]]"
related: [other.id, another.id]
created_by: ingest-source
```

| Field | Description |
|-------|-------------|
| `review_due` | When this article should be reviewed. Required for `kind: known-issue`. Used by the `lint` skill to flag stale content. |
| `provenance` | Wikilink(s) to the raw source(s) this article was derived from. Enables source tracing. |
| `related` | IDs of related articles. Used for cross-referencing. |
| `created_by` | Which skill created this article. Helps with audit trails. |

---

## Body structure

After the frontmatter, the article body follows this section order:

```markdown
## Answer
The core answer (2–5 sentences).

## Facts
- Key fact 1
- Key fact 2
- Parameters, values, links

## Pitfalls
- Common mistake 1
- Edge case to watch for

## Procedure
<!-- Only for kind: how-to -->
1. Step one
2. Step two

## Status
<!-- Only for kind: known-issue -->
Current status, workaround, expected fix date.

## See also
- [[related.article.id]]
```

Rules:

- **No H1 (`# Title`).** The `title:` frontmatter is the title.
- **No TL;DR line.** The `summary:` field serves this purpose.
- **Sections are optional** except `## Answer`, which is required.
- **Keep it concise.** The AI reads the full article. Bloat slows answers.

---

## Validation

The `verify_catalog.py` script checks every article for:

- All required fields present
- `domain` and `topics` values exist in `topics.yaml`
- `updated` is valid ISO date
- `review_due` present for `kind: known-issue`
- `id` is unique across all articles

Run it manually:

```bash
python3 "01 Reference/scripts/verify_catalog.py"
```

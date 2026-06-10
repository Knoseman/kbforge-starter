# Reference Articles

Structured KB for AI-assisted Q&A. Articles live in `01 Reference/articles/`, named `domain.slug.md`. Machine-readable catalog at `01 Reference/catalog.jsonl`.

---

## Lookup Protocol

### Step 1 — Grep `catalog.jsonl` (never read it in full)

```sh
# By domain (fastest when you know the product area)
rg '"domain":"your-domain"' "01 Reference/catalog.jsonl"

# By topic tag
rg '"topics":\[[^]]*"authentication"' "01 Reference/catalog.jsonl"

# By question keyword — most semantically accurate
rg -i 'webhook' "01 Reference/catalog.jsonl"

# By article kind
rg '"kind":"known-issue"' "01 Reference/catalog.jsonl"
```

Valid domains: defined in `01 Reference/topics.yaml` → `domains`. Update that file when you add a new domain.

If 0 matches → broaden the search term. If >5 → add a second grep filter (pipe). Read `catalog.jsonl` in full only as an absolute last resort.

### Step 2 — Read `## Answer` section of the matched article (partial read)

Open `01 Reference/articles/<id>.md`. Limit to **first 40 lines**. `## Answer` is always the first body section and answers most queries directly.

- If `status: superseded` or `status: outdated` → read the `superseded_by` field and open that article instead.

### Step 3 — Escalate read if needed

`## Answer` insufficient? Read `## Facts` (lines 40–120). Still insufficient? Read the full article.

### Step 4 — Aggregates for cross-cutting queries

| Query type | Open |
|---|---|
| Compare A vs B | `01 Reference/aggregates/comparisons.md` |
| Known bugs / gaps | `01 Reference/aggregates/known-issues.md` |
| Who to contact | `01 Reference/aggregates/contacts.md` |
| Base URLs / environments | `01 Reference/aggregates/environments.md` |

### Step 5 — Staleness check

If `review_due:` is before today's date → surface to user: _"Note: this article's review date was YYYY-MM-DD — content may be outdated."_

---

**Never:** `ls` any folder · read `provenance` sources unless explicitly asked

---

## Editing Rules

- `owner: ai` → ask user before editing
- `owner: user` → do not modify
- **New article** → write to `01 Reference/articles/domain.slug.md` with complete frontmatter; then run `python3 "01 Reference/scripts/build_catalog.py"` to rebuild catalog and aggregates
- All `domain`, `kind`, `status`, and `topics` values **must exist** in `01 Reference/topics.yaml` before use

---

## Article Frontmatter Schema

```yaml
---
id: domain.slug                     # must equal filename (without .md)
title: Human-readable title
kind: reference                     # enum: reference|troubleshooting|known-issue|comparison|process|contacts
domain: your-domain                 # enum: see topics.yaml → domains
topics: [tag1, tag2]                # from topics.yaml → topics; lowercase, hyphenated
status: current                     # enum: current|outdated|superseded|provisional
updated: YYYY-MM-DD
review_due: YYYY-MM-DD              # required for kind: known-issue or status: provisional
owner: ai                           # enum: ai|user
provenance:                         # traceability only — do NOT follow these links
  - "URL or vault path"
related: [id1, id2]                 # bare article ids (no wikilinks)
superseded_by: id                   # only if status: superseded
summary: "One-line answer."         # single source of truth — NOT repeated in body
answers:
  - "natural language question this article answers"
  - "alternate phrasing"
  - "third phrasing"
---
```

## Article Body Structure

Sections in this fixed order. **No H1 title. No TL;DR line.** `summary:` in frontmatter is the source of truth and is not repeated in the body.

```
## Answer
Prose. ≤5 sentences. Directly answers the most likely query.

## Facts
Bullets / tables / code blocks. Dense reference data. No prose padding.

## Pitfalls
Common mistakes, wrong assumptions, dangerous gotchas. Omit entirely if none.

## Procedure          ← process articles only
Numbered steps.

## Status             ← known-issue articles only
Current state and TODO.

## See also
id1 · id2 · id3
```

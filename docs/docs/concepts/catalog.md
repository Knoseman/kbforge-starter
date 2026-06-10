# The Catalog

The catalog is the heart of KBForge's lookup system. It is a machine-readable index of every article in your knowledge base, regenerated automatically whenever articles change.

---

## What is `catalog.jsonl`

`catalog.jsonl` lives at `01 Reference/catalog.jsonl`. It contains one JSON object per line — one for every article in `01 Reference/articles/`.

Example line:

```json
{"id":"api.auth","title":"Authentication","kind":"reference","domain":"api","topics":["auth","tokens","security"],"status":"current","updated":"2026-06-01","review_due":"2026-09-01","summary":"API authentication uses OAuth 2.0 client credentials flow.","answers":["How do I authenticate with the API?","What auth flow does the API use?","Where do I get API credentials?"]}
```

The AI greps this file before opening any article. Because it's one line per article, `grep` or `ripgrep` can search thousands of articles in milliseconds.

---

## How the catalog is built

Run `build_catalog.py` to regenerate:

```bash
python3 "01 Reference/scripts/build_catalog.py"
```

This script:

1. Scans `01 Reference/articles/*.md`
2. Extracts frontmatter from each
3. Writes one compact JSON line per article to `catalog.jsonl`
4. Generates `catalog.md` — a human-readable table of contents

The `update-catalog` skill chains to this automatically after every ingestion.

---

## Why JSONL

- **Append-friendly:** Add a line without rewriting the whole file
- **Stream-friendly:** Read line-by-line without parsing the entire document
- **Grep-friendly:** Plain text — works with `grep`, `rg`, `awk`, any tool
- **No dependencies:** No YAML parser, no database, no nothing

---

## Schema

Each line in `catalog.jsonl` contains these fields (extracted from article frontmatter):

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique identifier, e.g. `domain.slug` |
| `title` | string | Human-readable title |
| `kind` | string | `reference`, `known-issue`, `how-to`, `overview` |
| `domain` | string | Domain from `topics.yaml` |
| `topics` | array | Topic tags from `topics.yaml` |
| `status` | string | `current`, `draft`, `archived` |
| `updated` | string | ISO date `YYYY-MM-DD` |
| `review_due` | string | ISO date or `null` |
| `summary` | string | One-line answer |
| `answers` | array | Natural-language questions this article answers |

---

## Searching the catalog

The `answer-question` skill searches by keyword matching on `domain`, `topics`, `summary`, and `answers`. You can also search manually:

```bash
# Find all articles about authentication
rg '"topics":\[[^]]*"auth"' "01 Reference/catalog.jsonl"

# Find articles in the api domain
rg '"domain":"api"' "01 Reference/catalog.jsonl"

# Find articles with a specific answer phrase
rg 'How do I authenticate' "01 Reference/catalog.jsonl"
```

Because the catalog is plain text, any tool that can search text works — no special query language required.

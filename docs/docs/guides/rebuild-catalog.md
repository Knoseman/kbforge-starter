# How to Rebuild the Catalog

The catalog (`catalog.jsonl`) is the index the AI searches before opening any article. It must be regenerated whenever articles change.

---

## When to rebuild

Rebuild the catalog after:

- Ingesting new sources (the `ingest-source` skill does this automatically)
- Editing article frontmatter manually
- Adding or removing articles
- Changing `topics.yaml`

---

## How to rebuild

```bash
python3 "01 Reference/scripts/build_catalog.py"
```

This script:

1. Scans `01 Reference/articles/*.md`
2. Extracts frontmatter from each article
3. Writes one compact JSON line per article to `catalog.jsonl`
4. Generates `catalog.md` — a human-readable table of contents

---

## Verify after rebuilding

Run the validation script to catch schema errors:

```bash
python3 "01 Reference/scripts/verify_catalog.py"
```

This checks:

- All required fields are present
- `domain` and `topics` values exist in `topics.yaml`
- Dates are valid ISO format
- `review_due` is present for `kind: known-issue`
- Article IDs are unique

Fix any errors before relying on the catalog for lookups.

---

## What the catalog looks like

`catalog.jsonl` — one JSON object per line:

```json
{"id":"api.auth","title":"Authentication","kind":"reference","domain":"api","topics":["auth","tokens","security"],"status":"current","updated":"2026-06-01","review_due":"2026-09-01","summary":"API authentication uses OAuth 2.0 client credentials flow.","answers":["How do I authenticate with the API?","What auth flow does the API use?"]}
```

`catalog.md` — human-readable table:

```markdown
# Catalog

| ID | Title | Domain | Topics | Updated | Summary |
|----|-------|--------|--------|---------|---------|
| api.auth | Authentication | api | auth, tokens, security | 2026-06-01 | API authentication uses OAuth 2.0... |
```

---

## Automation

The `update-catalog` skill chains to `build_catalog.py` automatically after every ingestion. You rarely need to run it manually — but knowing how helps when troubleshooting.

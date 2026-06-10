---
id: update-catalog
title: Update Catalog
kind: meta
inputs: []
outputs: [log_entry]
chains_to: []
chains_from: [ingest-source, answer-question]
touches:
  reads:  ["01 Reference/articles/*.md"]
  writes: ["01 Reference/catalog.jsonl", "01 Reference/catalog.md", "01 Reference/aggregates/*.md"]
triggers:
  - "rebuild catalog"
  - "update catalog"
  - "regenerate aggregates"
  - "refresh kb index"
success_rate: unrated
summary: "Rebuild catalog.jsonl, catalog.md, and all KB aggregates from the current state of 01 Reference/articles/. Run after any article write or edit."
---

## When
Any skill or manual edit added, modified, renamed, or deleted a file under `01 Reference/articles/`. Catalog and aggregates are auto-generated and become stale instantly when articles change. Always chain to this skill — never edit `catalog.jsonl` by hand.

## Inputs
None. Reads the current state of `01 Reference/articles/`.

## Procedure

1. Run the build script:
   ```bash
   python3 "01 Reference/scripts/build_catalog.py"
   ```

2. Verify expected output. The script should report:
   - `catalog.jsonl: N articles`
   - `catalog.md: written`
   - `aggregates/known-issues.md: <n> articles`
   - `aggregates/contacts.md: <n> articles`
   - `aggregates/comparisons.md: <n> articles`
   - `aggregates/environments.md: <n> articles`

3. If the script errors on any article (e.g. missing `id` field, malformed frontmatter), surface the error and stop. The article needs fixing before the catalog can rebuild — do NOT silently skip.

4. Report the article count delta:
   > Catalog rebuilt: N articles (was M before).

## Output
- `01 Reference/catalog.jsonl` (regenerated)
- `01 Reference/catalog.md` (regenerated)
- `01 Reference/aggregates/*.md` (regenerated)

## Hand-off
None — this is a terminal skill. The caller of the chain takes back control.

If the catalog rebuild surfaced schema errors, hand back to the caller with a note that articles need fixing before further work.

## Rating
- ✅ success — script exited 0, article count matches expectations
- ⚠️ partial — script ran but warned about one or more articles (e.g. missing fields)
- ❌ failed — script errored out; catalog not rebuilt

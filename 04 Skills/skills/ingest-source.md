---
id: ingest-source
title: Ingest Source
kind: capture
inputs: [source_path]
outputs: [article, log_entry]
chains_to: [update-catalog, kb-gaps]
chains_from: [triage, clean-source, kb-gaps]
touches:
  reads:  ["00 Raw Sources/**/*.md", "01 Reference/catalog.jsonl", "01 Reference/topics.yaml", "01 Reference/articles/*.md"]
  writes: ["01 Reference/articles/*.md", "00 Raw Sources/**/*.md", "05 Iteration Logs/KB Gaps.md", "05 Iteration Logs/Ingestion Log.md"]
triggers:
  - "ingest this"
  - "process [filename]"
  - "extract articles from"
  - "turn this transcript into KB articles"
success_rate: unrated
summary: "Extract structured reference articles from a cleaned raw source. Plans against existing catalog to avoid duplicates, writes new articles, logs gaps, marks source processed."
---

## When
A cleaned `.md` source exists in `00 Raw Sources/` with `processed: false`, and you want to turn its content into one or more reference articles under `01 Reference/articles/`. The source must be cleaned first — run `clean-source` if it isn't.

## Inputs
- Cleaned source path (`00 Raw Sources/<file>.md` with `processed: false`)
- Optionally: a hint about which domain the content belongs to

## Procedure

1. Verify source.
   - **If content was pasted directly in chat (no file path given):** Do NOT proceed inline. First run `clean-source` to save and clean the content as a `.md` file in `00 Raw Sources/`. Only then continue from step 2.
   - **If a `.txt` file exists in `00 Raw Sources/`:** Run `clean-source` on it first. Only continue once a cleaned `.md` with `processed: false` exists.
   - **If a `.md` file exists:** Confirm it has `processed: false`. If `processed: true`, ask the user before re-ingesting.

2. Spawn an Explore subagent to extract knowledge. Pass this prompt (replace `<path>`):

   > Read `<path>` in full. Ignore personal/small-talk content. Return a structured list grouped by category — no prose:
   > - **How-to:** steps or procedures
   > - **Config:** settings, parameters, values, formats
   > - **Product:** features, limitations, comparisons
   > - **Known issues:** bugs, workarounds
   > - **Contacts/escalation:** names, roles, who to ask
   > - **Decisions:** confirmed outcomes
   > - **Open questions:** unresolved items
   > This replaces reading the source in the main context.

   Do NOT re-read the source in the main thread.

3. Plan articles against the existing catalog. Grep `01 Reference/catalog.jsonl` by domain and topic keywords to find overlaps:
   ```
   rg '"domain":"<domain>"' "01 Reference/catalog.jsonl"
   ```
   Granularity rule: one article = one lookup need. If someone would search for it independently → new article. If it's always context for another topic → update existing.

4. Show the plan and proceed:

   > From `<source>`:
   >
   > **Will update:**
   > - `<existing.id>` — adding [what]
   >
   > **Will create:**
   > 1. `<new.id>` — [one line]
   > 2. `<new.id>` — [one line]
   >
   > Proceeding.

   Pause only if genuinely ambiguous (content fits two existing articles equally well).

5. Write each new article to `01 Reference/articles/<id>.md` using the schema. Required frontmatter:

   ```yaml
   ---
   id: domain.slug
   title: Human-readable title
   kind: reference
   domain: <domain>               # from 01 Reference/topics.yaml → domains
   topics: [tag1, tag2]           # from 01 Reference/topics.yaml → topics
   status: current
   updated: YYYY-MM-DD
   review_due: YYYY-MM-DD         # REQUIRED for kind: known-issue
   owner: ai
   provenance:
     - "[[00 Raw Sources/<file>.md]]"
   related: [id1, id2]
   created_by: ingest-source
   summary: "One-line answer."
   answers:
     - "natural language question 1"
     - "natural language question 2"
   ---
   ```

   Body: `## Answer` → `## Facts` → `## Pitfalls` → `## Procedure` (process only) → `## Status` (known-issue only) → `## See also`. No H1. No TL;DR line.

6. Topic vocabulary check. Every term in `topics:` and the `domain:` must exist in `01 Reference/topics.yaml`. If a needed term is missing, add it to `topics.yaml` first.

7. For updates to existing articles, read the existing article, integrate new content, bump `updated:`, and add a provenance entry.

8. Log gaps. For each open question from step 2, append to `05 Iteration Logs/KB Gaps.md`:

   ```markdown
   ## YYYY-MM-DD — [Short description]
   **Source:** `00 Raw Sources/<file>.md`
   **Question/Issue:** [what was raised but not resolved]
   **Domain:** [domain]
   **Priority:** [High / Medium / Low]
   ```

9. Mark source processed. Edit source frontmatter:

   ```yaml
   ---
   type: raw-source
   date: YYYY-MM-DD
   processed: true
   date_processed: YYYY-MM-DD
   articles_created:
     - <new.id>
   articles_updated:
     - <existing.id>
   ---
   ```

10. Append to `05 Iteration Logs/Ingestion Log.md`:

    ```markdown
    ## [YYYY-MM-DD] ingest | <source filename>
    **Articles created:** [<id>, <id>]
    **Articles updated:** [<id>, or None]
    **Gaps logged:** [n, or None]
    ```

11. **Move the processed source to Archive:**
    ```bash
    mv "00 Raw Sources/<filename>.md" "00 Raw Sources/Archive/"
    ```
    This is mandatory — if any source file is still in `00 Raw Sources/` root after step 9, the ingestion is not complete.

12. Chain to `update-catalog` to rebuild `catalog.jsonl` and aggregates.

13. Confirm:

    > Processed: `00 Raw Sources/<file>.md`
    > Created: <id>, <id>
    > Updated: <id>
    > Gaps logged: n

## Output
- New / updated article files in `01 Reference/articles/`
- Updated source frontmatter (`processed: true`)
- Source `.md` moved to `00 Raw Sources/Archive/`
- New entries in `05 Iteration Logs/KB Gaps.md` and `05 Iteration Logs/Ingestion Log.md`

## Hand-off
- Always chain to `update-catalog` (mandatory — catalog is now stale).
- Optional: chain to `kb-gaps` to triage newly-logged gaps.
- If more sources remain unprocessed, offer to continue with the next one.

## Rating
- ✅ success — articles written with valid frontmatter, source marked processed, source moved to Archive, ingestion log appended, catalog rebuilt
- ⚠️ partial — some content extracted but at least one open question left for human review (logged as a gap)
- ❌ failed — source unreadable or fundamentally unsuitable for KB content; do not move to Archive

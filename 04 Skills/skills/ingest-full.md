---
id: ingest-full
title: Ingest Full Pipeline
kind: capture
inputs: [source_path]
outputs: [article, log_entry]
chains_to: [kb-gaps]
chains_from: [triage]
collapsed_from: [clean-source, ingest-source, update-catalog]
fast_path: true
touches:
  reads:  ["00 Raw Sources/**/*", "01 Reference/catalog.jsonl", "01 Reference/topics.yaml", "01 Reference/articles/*.md"]
  writes: ["00 Raw Sources/**/*.md", "01 Reference/articles/*.md", "01 Reference/catalog.jsonl", "01 Reference/catalog.md", "01 Reference/aggregates/*.md", "05 Iteration Logs/KB Gaps.md", "05 Iteration Logs/Ingestion Log.md"]
triggers:
  - "process this source"
  - "ingest this transcript"
  - "turn this into articles"
  - "full ingest"
  - "process my raw source"
success_rate: unrated
summary: "Complete pipeline: clean a raw source, extract articles, update catalog, and move to archive. Use this as the default for new raw sources."
---

## When
A new raw source has arrived and you want to turn it into structured KB articles with zero manual steps. This skill replaces the `clean-source → ingest-source → update-catalog` chain with a single pass.

Use this skill UNLESS:
- The source is already cleaned (then use `ingest-source` only)
- You only want to clean, not ingest (then use `clean-source`)
- You only want to rebuild the catalog (then use `update-catalog`)

## Inputs
- Source path under `00 Raw Sources/` (`.txt`, `.md`, or pasted content)
- Optionally: a hint about which domain the content belongs to

## Procedure

### Phase 1: Clean (if needed)

1. **Determine if cleaning is needed:**
   - **If content was pasted directly in chat:** Save as `00 Raw Sources/YYYY-MM-DD [Descriptive Name].md` with `processed: false`, then proceed to Phase 2.
   - **If `.txt` file:** Clean it now. Target path: `00 Raw Sources/YYYY-MM-DD [Descriptive Name] Transcript.md`
     - Strip personal content (greetings, weekend plans, non-work banter, garbled artefacts)
     - Keep substantive work: decisions, questions, speaker attribution, `[Laughter]` around work points
     - Structure with `**Speaker:**` per turn, `---` dividers, `## [Topic]` headings
     - Fix obvious transcription errors; preserve conversational register
     - Write frontmatter:
       ```yaml
       ---
       type: raw-source
       date: YYYY-MM-DD
       processed: false
       ---
       ```
     - Delete the original `.txt`
   - **If `.md` file with `processed: false`:** Skip Phase 1. Use the file as-is.
   - **If `.md` file with `processed: true`:** Ask user before re-ingesting.

### Phase 2: Extract and Plan

2. **Spawn an Explore subagent** to extract knowledge from the cleaned source:

   > Read `<path>` in full. Ignore personal/small-talk content. Return a structured list grouped by category — no prose:
   > - **How-to:** steps or procedures
   > - **Config:** settings, parameters, values, formats
   > - **Product:** features, limitations, comparisons
   > - **Known issues:** bugs, workarounds
   > - **Contacts/escalation:** names, roles, who to ask
   > - **Decisions:** confirmed outcomes
   > - **Open questions:** unresolved items

3. **Plan articles against catalog.** Grep `01 Reference/catalog.jsonl` by domain and topic keywords. Granularity rule: one article = one lookup need.

4. **Show plan and proceed:**

   > From `<source>`:
   >
   > **Will update:**
   > - `<existing.id>` — adding [what]
   >
   > **Will create:**
   > 1. `<new.id>` — [one line]
   >
   > Proceeding.

### Phase 3: Write Articles

5. **Write each new article** to `01 Reference/articles/<id>.md` with complete frontmatter:

   ```yaml
   ---
   id: domain.slug
   title: Human-readable title
   kind: reference
   domain: <domain>
   topics: [tag1, tag2]
   status: current
   updated: YYYY-MM-DD
   review_due: YYYY-MM-DD
   owner: ai
   provenance:
     - "[[00 Raw Sources/<file>.md]]"
   related: [id1, id2]
   created_by: ingest-full
   summary: "One-line answer."
   answers:
     - "natural language question 1"
   ---
   ```

   Body: `## Answer` → `## Facts` → `## Pitfalls` → `## Procedure` (process only) → `## Status` (known-issue only) → `## See also`.

6. **Topic vocabulary check.** All `topics:` and `domain:` values must exist in `01 Reference/topics.yaml`. Add missing terms first.

7. **For updates to existing articles:** Read existing, integrate new content, bump `updated:`, add provenance entry.

### Phase 4: Log, Archive, and Rebuild

8. **Log gaps.** For each open question, append to `05 Iteration Logs/KB Gaps.md`:

   ```markdown
   ## YYYY-MM-DD — [Short description]
   **Source:** `00 Raw Sources/<file>.md`
   **Question/Issue:** [what was raised but not resolved]
   **Domain:** [domain]
   **Priority:** [High / Medium / Low]
   ```

9. **Mark source processed.** Update source frontmatter:

   ```yaml
   processed: true
   date_processed: YYYY-MM-DD
   articles_created:
     - <new.id>
   articles_updated:
     - <existing.id>
   ```

10. **Append to Ingestion Log:**

    ```markdown
    ## [YYYY-MM-DD] ingest-full | <source filename>
    **Articles created:** [<id>]
    **Articles updated:** [<id>, or None]
    **Gaps logged:** [n, or None]
    ```

11. **Move source to Archive:**
    ```bash
    mv "00 Raw Sources/<filename>.md" "00 Raw Sources/Archive/"
    ```
    If a `.txt` original exists, move it too.

12. **Rebuild catalog:**
    ```bash
    python3 "01 Reference/scripts/build_catalog.py"
    ```
    Verify output: `catalog.jsonl: N articles`, `catalog.md: written`, aggregates updated.

13. **Confirm:**

    > Processed: `00 Raw Sources/<file>.md`
    > Created: <id>
    > Updated: <id>
    > Gaps logged: n
    > Catalog rebuilt: N articles

## Output
- Cleaned `.md` source (if `.txt` was input)
- New/updated articles in `01 Reference/articles/`
- Source marked `processed: true` and moved to `00 Raw Sources/Archive/`
- Updated `catalog.jsonl`, `catalog.md`, and aggregates
- Gap entries in `05 Iteration Logs/KB Gaps.md`
- Ingestion log entry in `05 Iteration Logs/Ingestion Log.md`

## Hand-off
- Optional: chain to `kb-gaps` to triage newly-logged gaps.
- If more sources remain unprocessed, offer to continue with the next one.

## Rating
| ✅ success | ⚠️ partial | ❌ failed |
- ✅ success — articles written, source marked processed and moved to Archive, catalog rebuilt, ingestion log appended
- ⚠️ partial — some content extracted but open questions remain (logged as gaps); or catalog rebuild warned about articles
- ❌ failed — source unreadable or unsuitable for KB content; do not move to Archive

---
id: clean-source
title: Clean Source
kind: capture
inputs: [source_path]
outputs: [cleaned_source_path]
chains_to: [ingest-source]
chains_from: [triage]
touches:
  reads:  ["00 Raw Sources/**/*"]
  writes: ["00 Raw Sources/**/*.md"]
triggers:
  - "clean this transcript"
  - "sanitize this source"
  - "strip personal content"
  - "convert this txt to md"
success_rate: unrated
summary: "Sanitize a raw source (transcript, chat log, notes) — remove personal content, convert .txt → .md, keep substantive work discussion. Pre-ingest step."
---

## When
A new raw source has arrived in `00 Raw Sources/` and contains personal/small-talk content, garbled transcription noise, or is in a non-Markdown format. Run this before `ingest-source` so the extracted articles are clean from the start.

## Inputs
- Source path under `00 Raw Sources/` (transcript, chat log, meeting notes, doc export)
- Format: `.txt`, `.md`, or other text-based

## Procedure

1. Read the source file in full.

2. Decide canonical path. If `.txt`, target path is `00 Raw Sources/YYYY-MM-DD [Descriptive Name] Transcript.md` — date from filename, context, or today. If already `.md`, edit in place.

3. Strip personal content. Remove: greetings, weekend plans, non-work banter, laughter-only lines with no context, garbled transcription artefacts, filler before the first work topic.

4. Keep substantive work discussion: decisions, questions (even casual phrasing), speaker names/attribution, `[Laughter]` annotations clarifying tone around a work point.

5. Structure the body. Use `**Speaker:**` per turn. Insert `---` dividers and `## [Topic]` headings at natural topic breaks. Fix obvious transcription errors; do NOT rewrite into formal prose — preserve conversational register.

6. Write frontmatter:
   ```yaml
   ---
   type: raw-source
   date: YYYY-MM-DD
   processed: false
   ---
   ```

7. Write the cleaned content to the canonical `.md` path.

8. If the source was `.txt`, delete the original. The `.md` is now canonical.

9. Report the cleaned path to the user.

> **Important:** The cleaned `.md` stays in `00 Raw Sources/` with `processed: false` until `ingest-source` moves it to Archive. Do not move it during cleaning.

## Output
Cleaned `.md` file at `00 Raw Sources/YYYY-MM-DD [Name] Transcript.md` with `processed: false` frontmatter.

## Hand-off
Chain to `ingest-source` with the cleaned source path. Do not re-read the source in the main thread when chaining — pass the path only.

## Rating
- ✅ success — source is `.md`, personal content removed, frontmatter present, original (if `.txt`) deleted
- ⚠️ partial — cleaned but some judgement calls left ambiguous (flagged inline for human review)
- ❌ failed — source unreadable, malformed beyond repair, or wrong file type

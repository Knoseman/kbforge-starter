# Free Skills Reference

The free tier includes 5 core skills that cover the ingest-and-answer loop.

---

## `triage`

**Kind:** capture
**Purpose:** Classify incoming input and route to the right skill.

**Triggers:**
- "help"
- "what should I do"
- "process this" (ambiguous)

**What it does:**
Reads the user's request, classifies it by intent, and either loads the appropriate skill or asks for clarification. Prevents the AI from improvising a workflow.

**Chains to:** Any skill, depending on classification.

---

## `clean-source`

**Kind:** capture
**Purpose:** Sanitize raw sources before ingestion.

**Triggers:**
- "clean this source"
- "sanitize this"
- "prepare for ingestion"

**What it does:**
- Removes headers, footers, signature blocks
- Fixes encoding issues
- Standardizes frontmatter
- Saves cleaned file to `00 Raw Sources/`

**Chains to:** `ingest-source`

---

## `ingest-source`

**Kind:** capture
**Purpose:** Extract structured articles from cleaned sources.

**Triggers:**
- "ingest this"
- "process [filename]"
- "extract articles from"
- "turn this transcript into KB articles"

**What it does:**
- Reads the source file
- Extracts knowledge categories (how-to, config, product, issues, etc.)
- Plans articles against existing catalog
- Writes new/updated articles
- Logs gaps
- Marks source processed and moves to Archive
- Rebuilds catalog

**Chains to:** `update-catalog` (mandatory), optionally `kb-gaps`

See [How to Ingest a Source](../guides/ingest.md) for the full walkthrough.

---

## `answer-question`

**Kind:** synthesis
**Purpose:** Look up and cite answers from the KB.

**Triggers:**
- "What does the KB say about..."
- "How do I..."
- "Explain..."
- Any domain question

**What it does:**
- Grep `catalog.jsonl` for matching articles
- Read `summary:` and `answers:` of candidates
- Open best match, read `## Answer`
- Return cited answer with article ID as source
- Log unanswerable questions to `KB Gaps.md`

See [How to Answer a Question](../guides/answer.md) for the full walkthrough.

---

## `update-catalog`

**Kind:** quality
**Purpose:** Rebuild `catalog.jsonl` after changes.

**Triggers:**
- "update catalog"
- "rebuild catalog"
- "refresh index"

**What it does:**
- Runs `build_catalog.py`
- Generates `catalog.jsonl` and `catalog.md`
- Reports article count and any errors

**Chains from:** `ingest-source` (automatic), `batch-ingest-sources` (automatic)

See [How to Rebuild the Catalog](../guides/rebuild-catalog.md) for details.

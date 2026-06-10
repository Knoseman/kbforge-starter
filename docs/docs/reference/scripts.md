# Scripts Reference

Python scripts in `01 Reference/scripts/` build and validate the KB. All use Python stdlib only — no pip dependencies.

---

## `build_catalog.py`

**Purpose:** Generate `catalog.jsonl` and `catalog.md` from articles.

**Usage:**
```bash
python3 "01 Reference/scripts/build_catalog.py"
```

**What it does:**
- Scans `01 Reference/articles/*.md`
- Extracts frontmatter from each article
- Writes one compact JSON line per article to `catalog.jsonl`
- Generates `catalog.md` — human-readable table of contents

**Called by:** `update-catalog` skill (automatic after ingestion)

---

## `verify_catalog.py`

**Purpose:** Validate all articles against the schema.

**Usage:**
```bash
python3 "01 Reference/scripts/verify_catalog.py"
```

**Checks:**
- All required frontmatter fields present
- `domain` and `topics` values exist in `topics.yaml`
- `updated` is valid ISO date (`YYYY-MM-DD`)
- `review_due` present for `kind: known-issue`
- Article IDs are unique
- No orphaned files

**Output:** Pass/fail report with specific errors.

---

## `batch_process_sources.py`

**Purpose:** Process multiple raw sources in one pass.

**Usage:**
```bash
python3 "01 Reference/scripts/batch_process_sources.py"
```

**What it does:**
- Scans `00 Raw Sources/` for unprocessed files
- Runs `clean-source` + `ingest-source` on each
- Generates a batch report

**Note:** Pro-tier workflow. Free users can process sources one at a time.

---

## `build_glossary.py`

**Purpose:** Auto-generate a glossary from article definitions.

**Usage:**
```bash
python3 "01 Reference/scripts/build_glossary.py"
```

**What it does:**
- Scans articles for definition patterns
- Builds `01 Reference/aggregates/glossary.md`
- Cross-references terms to articles

**Note:** Pro-tier workflow.

---

## `ingest_readiness.py`

**Purpose:** Check if raw sources are ready for ingestion.

**Usage:**
```bash
python3 "01 Reference/scripts/ingest_readiness.py"
```

**Checks:**
- Files in `00 Raw Sources/` are `.md` (not `.txt`)
- Frontmatter is present and valid
- `processed` flag is set correctly
- No duplicates in Archive

---

## `scan_raw_sources.py`

**Purpose:** Inventory raw sources and report status.

**Usage:**
```bash
python3 "01 Reference/scripts/scan_raw_sources.py"
```

**Output:**
- Count of processed vs unprocessed sources
- List of sources by date
- Warnings for stale unprocessed files

---

## `build_skills_index.py`

**Purpose:** Generate `skills.jsonl` from skill files.

**Usage:**
```bash
python3 "04 Skills/scripts/build_skills_index.py"
```

**What it does:**
- Scans `04 Skills/skills/*.md`
- Extracts skill frontmatter
- Writes `skills.jsonl` — the skill catalog

**Called by:** `init.py` during setup, and manually after adding new skills.

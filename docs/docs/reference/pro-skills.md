# Pro Skills Reference

The Pro pack adds 8 power skills for quality workflows, batch operations, and advanced output.

---

## `batch-ingest-sources`

**Kind:** capture
**Purpose:** Process multiple raw sources in one pass.

**What it does:**
- Scans `00 Raw Sources/` for all unprocessed files
- Runs `clean-source` + `ingest-source` on each
- Generates a batch report with counts and gaps
- Rebuilds catalog once at the end

**When to use:** You have a backlog of 5+ sources to process.

---

## `build-glossary`

**Kind:** synthesis
**Purpose:** Auto-generate a glossary from article definitions.

**What it does:**
- Scans articles for definition patterns (e.g. "X is a...", "Y refers to...")
- Builds `01 Reference/aggregates/glossary.md`
- Cross-references terms to their source articles
- Updates on subsequent runs

**When to use:** Your KB has grown and new team members need a terminology reference.

---

## `draft-response`

**Kind:** output
**Purpose:** Write partner/client replies grounded in the KB.

**What it does:**
- Reads the question or issue
- Grep KB for relevant articles
- Reads `03 Accounts/[Account].md` for context
- Drafts a response with citations
- Saves to `02 Outputs/` for review

**When to use:** You need to send a technical answer to a partner and want it grounded in your KB.

---

## `kb-gaps`

**Kind:** quality
**Purpose:** Report on unanswered questions and coverage gaps.

**What it does:**
- Reads `05 Iteration Logs/KB Gaps.md`
- Groups gaps by domain and priority
- Identifies patterns (e.g. "5 questions about webhooks")
- Suggests sources to ingest or articles to write
- Generates a gap report

**When to use:** Weekly review, before a sprint, or when you suspect your KB has blind spots.

---

## `lint`

**Kind:** quality
**Purpose:** Find stale articles and orphaned content.

**What it does:**
- Flags articles with past `review_due:` dates
- Finds articles with no incoming links (orphans)
- Detects broken `[[wikilinks]]`
- Reports frontmatter inconsistencies
- Suggests rewrites or archival

**When to use:** Monthly maintenance, or before sharing the KB with a new team member.

---

## `log-issue`

**Kind:** capture
**Purpose:** Capture and track partner issues.

**What it does:**
- Reads the issue description
- Creates a structured issue file in `02 Outputs/`
- Links to relevant KB articles
- Suggests escalation path from `03 Accounts/`
- Appends to iteration log

**When to use:** A partner reports a bug or integration problem.

---

## `uat-prep`

**Kind:** output
**Purpose:** Build UAT checklists for partner onboarding.

**What it does:**
- Reads partner context from `03 Accounts/`
- Grep KB for integration requirements
- Generates a checklist: test cases, expected results, sign-off criteria
- Saves to `02 Outputs/` for review

**When to use:** Preparing a partner for production go-live.

---

## `verify-catalog`

**Kind:** quality
**Purpose:** Schema validation for all articles.

**What it does:**
- Runs `verify_catalog.py`
- Reports errors with file paths and line numbers
- Suggests fixes
- Can be run in CI for automated checks

**When to use:** After bulk edits, before sharing the KB, or in CI on every PR.

---

## Get the Pro pack

→ [Pro Tier](../pro.md)

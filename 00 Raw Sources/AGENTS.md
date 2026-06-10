# Raw Sources

Unprocessed inputs: API docs, transcripts, chat logs, meeting notes.

**Scope:** Everything here is raw material — not yet validated or structured for the KB.

---

## Rules

- **Never edit content.** Read-only unless you are running `ingest-source`.
- **Check `processed: true`** in frontmatter before reading — already-processed sources don't need re-ingestion.
- **To process:** use the `ingest-source` skill. Do not extract articles manually.
- **`.txt` files:** convert to `.md` only as part of `ingest-source`, never in isolation.

---

## Structure

| Subfolder | Contents |
|-----------|---------|
| `Docs/` | Vendor API documentation (official, structured) |
| `Archive/` | Fully processed sources — read-only audit trail |
| (root) | **Unprocessed** transcripts, chat logs, meeting notes — these need action |

**Quick triage:** If a file is in the root (not Archive/), it has not been ingested yet.

---

## Applicable Skill

`ingest-source` — processes a source and extracts structured articles into `01 Reference/`.

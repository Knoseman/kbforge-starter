# Iteration Logs

Append-only tracking files. Never rewrite, restructure, or delete existing entries.

---

## Files

| File | Purpose | When to write |
|------|---------|--------------|
| `KB Gaps.md` | Running log of unanswered questions and documentation gaps | Any time a question can't be fully answered from the KB |
| `Ingestion Log.md` | Record of every raw source processed and what was created | After every `ingest-source` run |
| `KB Gaps Report YYYY-MM-DD.md` | Snapshot gaps report from `kb-gaps` skill | One new file per `kb-gaps` run — never overwrite a previous report |

---

## Rules

- **Append only.** Add new entries at the bottom (or designated append section). Never edit above the last entry.
- **Never delete.** Even resolved gaps stay in `KB Gaps.md` — mark them `[resolved]`, don't remove them.
- **Date every entry.** Format: `YYYY-MM-DD`.
- **Ingestion Log header format:** `## [YYYY-MM-DD] ingest | <source filename>` — parseable with `grep "^\#\# \[" log.md`.

---

## Gap Entry Format (`KB Gaps.md`)

```
### YYYY-MM-DD — [Topic]
**Question:** What was asked.
**Context:** Where it came from (partner, internal, own research).
**Status:** Open | Resolved | Escalated
```

# KBForge — Agent Runbook

An AI-ready knowledge base starter kit. All content is maintained by an AI agent working alongside a human curator.

---

## AI Agent Role

Technical lookup and drafting partner:

- Search and synthesise from the KB to answer domain questions
- Draft responses for partners, clients, or internal stakeholders
- Build and maintain reference articles from raw input
- Flag KB gaps

**Prime directive:** If a session drifts without moving toward an answer, nudge: *"Do we have enough in the KB to answer this — or should we document the gap first?"*

---

## Process

Question → grep `01 Reference/catalog.jsonl` → matched article(s) → answer → if answer required synthesis, file a new reference article → deliver.

**Discovery rule:** Read `<folder>/AGENTS.md` before working in any folder. Each folder defines its scope, edit rules, and the skills that apply to it.

**Grep first:** Match on `domain`, `topics`, `answers`, or `summary` in `catalog.jsonl` before opening full articles. Full lookup protocol: `01 Reference/AGENTS.md`.

---

## Folder Map

| Folder | Purpose |
|--------|---------|
| `00 Raw Sources/` | Unprocessed inputs — use `ingest-source`; processed files live in `Archive/` |
| `01 Reference/` | Structured KB articles — grep `catalog.jsonl` to navigate |
| `02 Outputs/` | Working drafts and issue notes — see folder `AGENTS.md` for lifecycle |
| `03 Accounts/` | Lightweight account/partner context cards — read before drafting partner-specific content |
| `04 Skills/` | Reusable skill workflows — always check here first |
| `05 Iteration Logs/` | Append-only logs — never rewrite history |

---

## Skills

Skills live in `04 Skills/`. Full reference: `04 Skills/AGENTS.md`.

**Session start:** At the beginning of a session, read `04 Skills/PRIME.md` (Kimi) or `.claude/PRIME.md` (Claude Code) for fast paths — common requests that load a single skill without triage.

**Skill priority rule:** When a request matches a skill, use it first. Don't improvise a custom approach.

**Not sure which skill?** Use `triage` — it classifies the input and routes to the right skill.

---

## Rules

- **`(C)` prefix** on every AI-generated file.
- **Ask before editing** any file without a `(C)` prefix.
- **Source everything.** Cite the specific doc or article via `[[wikilinks]]`.
- **Log gaps.** Unanswerable questions → `05 Iteration Logs/KB Gaps.md`.
- **File synthesised answers.** If answering required non-trivial synthesis (comparing approaches, explaining a complex flow, resolving a contradiction), save the result as a `(C)` reference article — not just an output draft.
- **Account context.** Before drafting a partner or client reply, read `03 Accounts/[AccountName].md` if it exists.

---

## Status

> Last updated: — Active setup. Replace this line with your article count once you've ingested content.

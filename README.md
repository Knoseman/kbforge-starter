# KBForge

**An AI-ready knowledge base starter kit for technical teams.**

Your AI assistant is only as good as what it can look up. KBForge gives you a git-native, agent-native knowledge base that both you and your AI can use — structured for grep-first lookup, provenance tracking, and gap detection out of the box.

Set up in under 30 minutes. No SaaS. No embeddings. No lock-in. **No Obsidian required.**

---

## What problem does this solve?

- **AI hallucination:** Your assistant invents answers because it has no grounded source to look up.
- **Knowledge trapped in one person's head:** Onboarding takes months; tribal knowledge walks out the door.     
- **Stale documentation:** Nobody knows what's outdated until someone acts on wrong information.
- **SaaS lock-in:** Your knowledge base is trapped in a proprietary format you can't grep, version, or export cleanly.

KBForge solves all four with plain Markdown, JSONL catalogs, and a library of reusable AI skills.

---

## How it works

```
Raw source (transcript, doc, chat log)
    ↓  ingest-source skill
Structured reference article  →  catalog.jsonl
    ↓  answer-question skill
Sourced answer with citations
    ↓  draft-response skill (Pro)
Ready-to-send reply
```

Every article has a `summary:` and `answers:` list that the AI greps before opening any file. Lookup is fast, cheap, and transparent — no vector database required.

---

## Why grep-first beats naive RAG

| | KBForge (grep-first) | Naive RAG |
|---|---|---|
| **Cost** | Free — pure text search | Embedding API calls on every query |
| **Transparency** | You can see exactly what matched and why | Black-box similarity scores |
| **Freshness** | Catalog regenerated on every article change | Requires re-embedding |
| **Staleness detection** | `review_due:` field surfaces outdated articles | None |
| **Gap detection** | `KB Gaps.md` log built into the workflow | None |
| **Provenance** | Every article cites its source | Typically lost |
| **Portability** | Plain files — works in any editor, CI, or AI tool | Tied to your vector store |

---

## What's included (free tier)

```
kbforge-starter/
├── AGENTS.md                    → agent runbook (root)
├── 00 Raw Sources/              → drop inputs here
│   ├── AGENTS.md
│   └── Archive/                 → processed sources (audit trail)
├── 01 Reference/                → structured KB articles
│   ├── AGENTS.md
│   ├── articles/                → one .md per article
│   ├── aggregates/              → auto-generated cross-cutting views
│   ├── catalog.jsonl            → machine-readable index (grep this)
│   └── scripts/                 → build_catalog.py + tooling suite
├── 02 Outputs/                  → working drafts
├── 03 Accounts/                 → lightweight partner/client context cards
├── 04 Skills/                   → reusable AI workflows
│   ├── skills/
│   │   ├── triage.md            → classify + route incoming input
│   │   ├── clean-source.md      → sanitize raw sources
│   │   ├── ingest-source.md     → extract articles from sources
│   │   ├── answer-question.md   → look up + cite an answer
│   │   └── update-catalog.md    → rebuild catalog.jsonl
│   └── scripts/
│       └── build_skills_index.py
└── 05 Iteration Logs/           → append-only KB Gaps + Ingestion Log
```

---

## Quick start

```bash
git clone https://github.com/Knoseman/kbforge-starter.git my-kb
cd my-kb
```

### Run initialization

**For most users (requires Python 3.10+):**

```bash
python3 init.py
```

**For Windows users (without Python/permissions):**

Right-click `init.ps1` in the folder and select **"Run with PowerShell"**.

> **Note:** If you get a security error, you may need to run this command in PowerShell first:
> `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

Answer 3 prompts:
1. **Domain slug** — your KB's focus area (e.g. `it-support`, `api-docs`, `team-wiki`)
2. **Team name** — your company or team
3. **Seed topics** — 3–5 concepts you'll document first

This personalises the template for you. It removes the demo content and scaffolds your first article.

→ See [SETUP.md](SETUP.md) for the full walkthrough.

---

## Pro tier

The free tier covers the core ingest-and-answer loop. The **Pro pack** adds:

- `draft-response` — write partner/client replies grounded in the KB
- `log-issue` — capture and track partner issues
- `kb-gaps` — report on unanswered questions and coverage gaps
- `lint` — find stale articles and orphaned content
- `verify-catalog` — schema validation for all articles
- `uat-prep` — build UAT checklists for partner onboarding
- `batch-ingest-sources` — process multiple raw sources in one pass
- `build-glossary` — auto-generate a glossary from article definitions

→ [Get the Pro pack](https://knoseman.lemonsqueezy.com) — $99 one-time

---

## Who is this for?

- **Solutions Engineers** and **Integration Managers** who answer the same technical questions repeatedly       
- **Support and DevRel leads** who need grounded, consistent answers across a team
- **Technical PMs** who want onboarding that doesn't depend on one person
- **Solo consultants** who want their expertise in a queryable, portable format

---

## Requirements

- **Any AI CLI with terminal access** — Kimi, Gemini, Claude Code, etc. *(This is the core requirement — the AI reads files, runs scripts, and follows skills.)*
- **Any text editor** — Obsidian (recommended), VS Code, Vim, Notepad, whatever you like. KBForge is plain Markdown.
- **Python 3.10+** — for build scripts (stdlib only, no pip required)

### Do I need Obsidian?

**No.** Obsidian is the *recommended* editor because it renders wikilinks (`[[like this]]`) and has a nice sidebar. But KBForge works with any editor that can open a folder of Markdown files. The AI workflow (ingest, answer, lint) runs entirely through your CLI — no GUI needed.

---

## License

MIT — free to use, fork, and adapt. See [LICENSE](LICENSE).

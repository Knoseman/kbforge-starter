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
└── 05 Iteration Logs/           → KB Gaps log + Ingestion Log
```

---

## Quick start

```bash
git clone https://github.com/Knoseman/kbforge-starter.git my-kb
cd my-kb
python3 init.py
```

Answer 3 prompts and you're live. See [Quick Start](quickstart.md) for the full first-10-minutes walkthrough, or [Setup](setup.md) for the complete guide.

!!! tip "Editor-agnostic"
    Obsidian is recommended but not required. Use any text editor — VS Code, Vim, Notepad, whatever. The AI workflow runs entirely through your CLI.

---

## Who is this for?

- **Solutions Engineers** and **Integration Managers** who answer the same technical questions repeatedly
- **Support and DevRel leads** who need grounded, consistent answers across a team
- **Technical PMs** who want onboarding that doesn't depend on one person
- **Solo consultants** who want their expertise in a queryable, portable format

---

## License

MIT — free to use, fork, and adapt. See [GitHub repository](https://github.com/Knoseman/kbforge-starter).

# What is KBForge?

KBForge is a **file-based knowledge base system** designed for AI-assisted workflows. It is not an app, not a SaaS, and not a plugin. It is a **convention** — a way of organizing Markdown files so that both humans and AI agents can read, write, and reason about them efficiently.

---

## Core idea

Most knowledge bases fail for AI because they are built for human browsing: folders, tags, search bars. KBForge is built for **lookup** — the AI needs to find the right article fast, read only what matters, and cite its source.

The system has three layers:

1. **Raw sources** (`00 Raw Sources/`) — unstructured input: transcripts, docs, chat logs, emails.
2. **Reference articles** (`01 Reference/articles/`) — structured, permanent knowledge. Every article answers specific questions and cites its origin.
3. **Catalog** (`catalog.jsonl`) — a machine-readable index. The AI greps this before opening any file.

---

## What makes it "AI-ready"

| Feature | What it means |
|---------|---------------|
| **Grep-first lookup** | The AI searches `catalog.jsonl` (a text file) instead of calling an embedding API. Free, fast, transparent. |
| **Structured frontmatter** | Every article declares what it answers (`answers:`), what it's about (`topics:`), and where it came from (`provenance:`). |
| **Provenance tracking** | Every article cites its raw source. You can trace any answer back to origin. |
| **Gap logging** | Unanswered questions are logged to `KB Gaps.md` — the KB knows what it *doesn't* know. |
| **Skills** | Reusable AI workflows (Markdown files) that define how to ingest, answer, lint, and draft. |
| **Git-native** | Everything is plain text. Version, diff, branch, and collaborate with standard tools. |

---

## What KBForge is not

- **Not a vector database.** No embeddings, no similarity search, no pinecone/weaviate/chroma.
- **Not a SaaS.** No login, no subscription, no data leaving your machine.
- **Not an Obsidian plugin.** Obsidian is the editor; KBForge works in any text editor or CLI.
- **Not automatic.** The AI assists, but a human curates. Quality depends on curation.

---

## When to use KBForge

Use it when:

- You answer the same technical questions repeatedly
- Your team has tribal knowledge in Slack, email, or one person's head
- You want AI answers that cite sources, not hallucinate
- You need a knowledge base that works offline, in git, and across tools
- You are a consultant or SE who needs a portable, queryable body of expertise

Don't use it when:

- You need real-time collaboration (Google Docs style)
- You want a fully automatic system with no human curation
- Your content is highly visual or non-textual
- You need semantic/fuzzy search (this is a known gap — see [Grep-first vs RAG](grep-first-vs-rag.md))

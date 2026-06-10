# Grep-first vs RAG

KBForge uses a **grep-first** lookup strategy. This is a deliberate design choice, not a missing feature. Here's how it compares to Retrieval-Augmented Generation (RAG) with vector embeddings.

---

## The comparison

| | KBForge (grep-first) | Naive RAG |
|---|---|---|
| **Cost** | Free — pure text search | Embedding API calls on every query |
| **Transparency** | You can see exactly what matched and why | Black-box similarity scores |
| **Freshness** | Catalog regenerated on every article change | Requires re-embedding |
| **Staleness detection** | `review_due:` field surfaces outdated articles | None |
| **Gap detection** | `KB Gaps.md` log built into the workflow | None |
| **Provenance** | Every article cites its source | Typically lost |
| **Portability** | Plain files — works in any editor, CI, or AI tool | Tied to your vector store |
| **Setup complexity** | Zero — works in any terminal | Requires vector DB + embedding pipeline |
| **Offline use** | Full functionality | Requires API access for embeddings |

---

## How grep-first works in KBForge

When you ask the AI a question, the `answer-question` skill does this:

1. **Grep `catalog.jsonl`** for keywords from your question
2. **Read `summary:` and `answers:`** of matching articles (without opening full files)
3. **Open the best match** and read its `## Answer` section
4. **Return a cited answer** with the article ID as source

The catalog is a JSONL file — one JSON object per line. Each line contains the article's metadata: `id`, `title`, `domain`, `topics`, `summary`, and `answers`. Grep finds matches in milliseconds. No API calls. No vectors.

---

## When RAG wins

Grep-first is not always better. RAG with embeddings shines when:

- You need **semantic/fuzzy matching** ("how do I authenticate?" → article about "login and tokens")
- Your corpus is **very large** (10,000+ articles) and keyword search produces too many false positives
- You have **unstructured documents** that don't fit the article schema

KBForge acknowledges this gap. The plan is:

- **v1:** Grep-first only. Document the trade-off honestly.
- **Post-v1:** Optional vector layer as a Pro/consulting add-on. The catalog format is designed to be embeddable later.

---

## Why we lead with grep-first

For technical teams building a curated KB, grep-first is the right default:

1. **It forces good structure.** If your articles have clear `answers:` and `summary:` fields, grep works well. If they don't, no search strategy will save you.
2. **It's transparent.** You can read `catalog.jsonl` and see exactly why an article matched. Try debugging a vector similarity score.
3. **It's free at scale.** No per-query costs. No embedding pipeline to maintain.
4. **It's portable.** Works in any terminal, CI job, or AI tool. No vendor lock-in.

The absence of RAG is framed as a **design choice** — KBForge is transparent and cheap *because* it doesn't do semantic embeddings.

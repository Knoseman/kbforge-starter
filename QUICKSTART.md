# KBForge — First 10 Minutes

> For your first time using KBForge. Read this, then delete it.

---

## What you just got

A git-backed knowledge base that works with AI assistants. You write articles in Markdown. The AI looks them up before answering questions. No vector database. No SaaS. Just files.

---

## Step 1 — Run initialization (1 min)

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

---

## Step 2 — Open in Obsidian (1 min)

1. Open [Obsidian](https://obsidian.md)
2. **Open folder as vault** → select this folder
3. You see the folder structure in the left sidebar

No plugins required.

---

## Step 3 — Add your first article (5 min)

Open `01 Reference/articles/<your-domain>.overview.md` (created by init.py).

Fill in:
- `summary:` — one-line answer to the most common question
- `answers:` — 2–3 questions this article answers
- `## Answer` — the actual answer (2–3 sentences)
- `## Facts` — key facts, parameters, links

Save. That's your first KB article.

---

## Step 4 — Rebuild the catalog (30 sec)

```bash
python3 "01 Reference/scripts/build_catalog.py"
```

This updates `catalog.jsonl` so the AI can find your article.

---

## Step 5 — Ask a question (2 min)

Open your AI CLI in this folder (Kimi, Gemini, Claude Code, etc.) and say:

```
What does the KB say about <your topic>?
```

The AI reads `catalog.jsonl`, finds your article, and answers from it — with a citation.

---

## What next?

| When you want to... | Do this |
|---------------------|---------|
| Add more articles | Create `.md` files in `01 Reference/articles/` with the same frontmatter format |
| Ingest a raw source (transcript, doc, notes) | Drop it in `00 Raw Sources/`, then tell the AI: "process this source" |
| Draft partner/client replies | Add a context card to `03 Accounts/`, then use `draft-response` (Pro) |        
| See which AI tools are supported | Read `04 Skills/PRIME.md` — there's one for each tool |
| Check article quality | Tell the AI: "verify catalog" |
| Find what's missing | Tell the AI: "what are the gaps" |
| See all skills | Read `04 Skills/aggregates/fast-paths.md` |

Full walkthrough: `SETUP.md`

---

## One rule

Every AI-generated file gets a `(C)` prefix. Don't edit files without `(C)` unless you're sure.

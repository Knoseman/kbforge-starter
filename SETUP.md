# Setup Guide

Get your KBForge knowledge base running in under 30 minutes.

\---

## Prerequisites

|Tool|Version|Notes|
|-|-|-|
|[Obsidian](https://obsidian.md)|Any|Free desktop app — your editing interface|
|Any AI CLI (Kimi, Gemini, Claude Code, etc.)|Latest|Must support file read + shell commands|
|Python|3.10+|For build scripts — stdlib only, no pip needed|
|Git|Any|To clone and version your KB|

\---

## Step 1 — Clone the repo

```bash
git clone https://github.com/Knoseman/kbforge-starter.git my-kb
cd my-kb
```

Replace `my-kb` with whatever you want your local folder called.

\---

## Step 2 — Run initialization

Depending on your environment, run one of the following commands:

**For most users (requires Python 3.10+):**

```bash
python3 init.py
```

**For Windows users (without Python/permissions):**

Right-click `init.ps1` in the folder and select **"Run with PowerShell"**.

> \\\*\\\*Note:\\\*\\\* If you get a security error, you may need to run this command in PowerShell first:
> `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

The script will prompt you for:

1. **Your domain slug** — a short, lowercase, hyphenated identifier for your primary knowledge area (e.g. `payments-api`, `my-platform`, `support-kb`). This becomes the default domain in your first articles.
2. **Your team or company name** — used in AGENTS.md and demo content (e.g. `My Team`, `Contoso`).
3. **3–5 seed topics** — the key concepts you'll write articles about (e.g. `authentication`, `webhooks`, `onboarding`). You can add more later in `01 Reference/topics.yaml`.

After you answer, `init.py` will:

* Replace all placeholder values across `topics.yaml` and `AGENTS.md` files
* Scaffold empty starting files with your domain
* Run `build_catalog.py` and `build_skills_index.py` to generate fresh indexes
* Print a checklist of what to do next

\---

## Step 3 — Open in Obsidian

1. Open Obsidian
2. **Open folder as vault** → select your `my-kb` directory
3. You should see the folder structure in the left sidebar

No plugins are required. You can use any AI CLI tool that can read files and run shell commands in the vault directory.

\---

## Step 4 — Ingest your first source

Drop a raw source into `00 Raw Sources/` — a transcript, API doc, meeting notes, chat log, or any text file.

Then open your AI CLI in the KB directory and say:

```
Process this source: 00 Raw Sources/your-file.md
```

The `ingest-source` skill will:

* Extract structured knowledge into `01 Reference/articles/`
* Log any unanswered questions to `05 Iteration Logs/KB Gaps.md`
* Mark the source as processed and move it to `Archive/`
* Rebuild `catalog.jsonl`

\---

## Step 5 — Ask your first question

```
What does the KB say about authentication?
```

The `answer-question` skill will:

* Grep `catalog.jsonl` for matching articles
* Read the `## Answer` section of the best match
* Return a cited answer with bare article ids as sources

\---

## You're done

Your KB is live. From here:

* **Add more sources** → repeat Step 4
* **Ask questions** → the KB gets more accurate as you add articles
* **Find gaps** → run the `kb-gaps` skill (Pro) or check `05 Iteration Logs/KB Gaps.md`
* **Keep articles fresh** → articles with a past `review\\\_due:` date will be flagged automatically

\---

## Folder quick-reference

|Folder|What goes here|
|-|-|
|`00 Raw Sources/`|Unprocessed transcripts, docs, chat logs|
|`01 Reference/articles/`|Structured KB articles (AI-generated)|
|`01 Reference/aggregates/`|Auto-generated cross-cutting views|
|`02 Outputs/`|Working drafts, issue notes, reply templates|
|`03 Accounts/`|One file per partner/client — lightweight context|
|`04 Skills/`|Reusable AI workflow definitions|
|`05 Iteration Logs/`|KB Gaps log + Ingestion log|

\---

## Troubleshooting

**`build\\\_catalog.py` exits with "No articles found"**
→ You haven't ingested any sources yet. Run `ingest-source` on a file in `00 Raw Sources/` first.

**Article frontmatter validation errors from `verify\\\_catalog.py`**
→ Check that every `domain:` and `topics:` value in the failing article exists in `01 Reference/topics.yaml`. Add missing terms there first.

**The AI doesn't find the right article**
→ Add more `answers:` phrasings to the article's frontmatter. These are what the AI searches before opening the file.




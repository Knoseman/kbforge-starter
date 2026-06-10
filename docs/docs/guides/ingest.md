# How to Ingest a Source

Turn raw input — a transcript, document, or chat log — into structured KB articles.

---

## Before you start

Make sure you have:

- A text file (`.md` or `.txt`) in `00 Raw Sources/`
- Your AI CLI open in the KB directory
- The `clean-source` and `ingest-source` skills available (free tier)

---

## Step 1: Drop the source

Place your file in `00 Raw Sources/`:

```
00 Raw Sources/
└── meeting-with-client-2026-06-01.md
```

If it's a `.txt` file, the AI will convert it to `.md` first.

---

## Step 2: Tell the AI to process it

```
Process this source: 00 Raw Sources/meeting-with-client-2026-06-01.md
```

The AI will:

1. Load the `ingest-source` skill
2. Verify the source is ready (cleaned, not already processed)
3. Extract structured knowledge from the content
4. Plan articles against the existing catalog
5. Show you the plan and proceed

---

## Step 3: Review the plan

The AI will show something like:

```
From meeting-with-client-2026-06-01.md:

Will update:
- api.auth — adding new token expiry info

Will create:
1. api.webhooks — webhook retry behavior
2. support.escalation — new escalation path for enterprise clients

Proceeding.
```

Pause here if anything looks wrong. The AI will only proceed if the plan is clear.

---

## Step 4: What happens automatically

After you confirm (or if the plan is unambiguous), the AI will:

- Write new articles to `01 Reference/articles/`
- Update existing articles with new content
- Log any open questions to `05 Iteration Logs/KB Gaps.md`
- Mark the source as processed
- Move the source to `00 Raw Sources/Archive/`
- Append to `05 Iteration Logs/Ingestion Log.md`
- Rebuild `catalog.jsonl`

---

## Step 5: Verify

Check that:

- New articles exist in `01 Reference/articles/`
- The source is now in `Archive/`
- `catalog.jsonl` has been updated (check the timestamp)
- Any gaps were logged to `KB Gaps.md`

---

## Tips for good ingestion

- **One topic per source is easiest.** A 50-page document will produce many articles — that's fine, but review the plan carefully.
- **Clean first if messy.** If the source has headers/footers/signature blocks, run `clean-source` first.
- **Check topics.yaml afterward.** If the AI invented new topics, add them to `topics.yaml` and re-run `verify_catalog.py`.
- **Review gaps immediately.** `KB Gaps.md` is your todo list. Don't let it grow stale.

---

## Common issues

**"Source already processed"**
:   The source has `processed: true` in its frontmatter. If you need to re-ingest, change it to `processed: false` first.

**"No articles found" from build_catalog.py**
:   You haven't ingested any sources yet, or the articles were written to the wrong folder. Check `01 Reference/articles/`.

**The AI missed something important**
:   Add it manually to the article, or re-ingest with a more specific hint (e.g. "focus on the authentication section").

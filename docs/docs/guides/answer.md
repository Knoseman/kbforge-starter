# How to Answer a Question

Ask the AI a question and get a grounded, cited answer from your knowledge base.

---

## Before you start

Make sure:

- You have articles in `01 Reference/articles/`
- `catalog.jsonl` is up to date (run `build_catalog.py` if unsure)
- The `answer-question` skill is available (free tier)

---

## Ask the question

Open your AI CLI in the KB directory and ask naturally:

```
What does the KB say about authentication?
```

```
How do I handle webhook retries?
```

```
What's the escalation path for enterprise clients?
```

---

## How the AI answers

The `answer-question` skill follows this protocol:

1. **Grep `catalog.jsonl`** for keywords from your question
2. **Read `summary:` and `answers:`** of matching articles (without opening full files)
3. **Rank matches** by relevance
4. **Open the best match** and read its `## Answer` section
5. **Return a cited answer** with the article ID as source

Example output:

```
The API uses OAuth 2.0 client credentials flow. You obtain a client ID and secret from the developer portal, then POST to /oauth/token. Tokens expire after 3600 seconds.

Source: api.auth
```

---

## If the answer is incomplete

The AI may find multiple relevant articles and synthesize an answer. If synthesis was non-trivial, it will file a new reference article with the combined answer — so next time, the answer is already in the KB.

If no article matches, the AI will:

- Say so explicitly
- Log the question to `05 Iteration Logs/KB Gaps.md`
- Suggest ingesting a source that might contain the answer

---

## Tips for better answers

- **Use the same vocabulary as your articles.** If your article says "OAuth 2.0," ask about "OAuth" not "login."
- **Add more `answers:` to articles.** The AI greps these before opening files. More phrasings = better matching.
- **Keep `summary:` concise.** This is the first thing the AI reads when ranking matches.
- **Review `KB Gaps.md` weekly.** Every unanswered question is a gap in your KB.

---

## Common issues

**The AI gives a generic answer instead of using the KB**
:   Remind it: "Check the KB first." The skill protocol requires this, but a nudge helps.

**The AI finds the wrong article**
:   The `answers:` field in the wrong article may be too broad. Narrow it, or add more specific `answers:` to the correct article.

**No articles match at all**
:   Your KB may not cover this topic yet. Ingest a source that does, or write the article manually.

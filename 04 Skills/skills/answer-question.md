---
id: answer-question
title: Answer Question
kind: lookup
inputs: [question, context?]
outputs: [answer, sources, rating]
chains_to: [draft-response, log-issue]
chains_from: [triage, log-issue]
touches:
  reads:
    - "01 Reference/catalog.jsonl"
    - "01 Reference/articles/*.md"
    - "01 Reference/aggregates/*.md"
  writes:
    - "05 Iteration Logs/KB Gaps.md"
triggers:
  - "answer this"
  - "look this up"
  - "what does the KB say"
  - "does the KB cover"
success_rate: unrated
fast_path: true
summary: "Look up a question in the KB and produce a sourced answer."
---

## When
A partner, client, or internal stakeholder asks a question and a KB-backed answer is needed before drafting a reply, escalating, or logging an issue.

## Inputs
- The question, verbatim or paraphrased
- Optional context: account, domain, prior issue note, urgency

## Procedure
1. Parse the question into: topic, domain, and 2–4 keywords. If unclear, ask one clarifying question before proceeding.
2. Grep `01 Reference/catalog.jsonl` for matching articles — match on `domain`, `topics`, `answers`, and `summary`. Example: `rg -i 'keyword' "01 Reference/catalog.jsonl"`. Shortlist the 1–2 best matches by id.
3. Read the `## Answer` section of each shortlisted article at `01 Reference/articles/<id>.md`. Do not read full articles unless the Answer section is insufficient.
4. If the question is cross-cutting (known issues, contacts, environment comparisons), read the matching aggregate at `01 Reference/aggregates/<name>.md` instead of (or in addition to) individual articles.
5. If catalog match is weak, escalate to a raw source: glob `00 Raw Sources/` by filename, read the most relevant file, and extract only the excerpt needed.
6. Write the answer inline: lead with the answer in 1–2 sentences, then only the detail needed to act. Cite sources as bare ids at the bottom (e.g. `Sources: domain.overview, domain.authentication`).
7. If KB coverage was partial or absent, offer to append a gap entry to `05 Iteration Logs/KB Gaps.md` (date, question, domain/topic, source needed, priority).
8. **File synthesised answers.** If answering required non-trivial synthesis — comparing two approaches, explaining a multi-step flow, resolving a contradiction — offer to save the result as a new reference article. Synthesis that would be re-derived next time should be filed; one-shot answers don't need filing.
9. If a new reference article was created during answering, chain to `update-catalog`.

## Output
Inline answer with a `Sources:` line listing bare article ids. Optionally a gap appended to `05 Iteration Logs/KB Gaps.md`.

## Hand-off
- To `draft-response` — pass the answer text, the bare source ids, and audience (partner | internal).
- To `log-issue` — if the question revealed an unresolved issue, pass the question and any context gathered.

## Rating
| ✅ success | ⚠️ partial | ❌ failed |
- ✅ success — direct answer with at least one cited source id, no invented detail
- ⚠️ partial — KB covers part of the question; missing pieces are named and a gap is logged
- ❌ failed — no KB coverage; gap logged and answer deferred to escalation or raw-source research

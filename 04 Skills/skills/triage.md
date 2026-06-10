---
id: triage
title: Triage
kind: meta
inputs: [context]
outputs: [routing_decision]
chains_to: [answer-question, log-issue, draft-response, kb-gaps, uat-prep, clean-source, ingest-source, update-catalog, verify-catalog, build-glossary, lint]
chains_from: []
touches:
  reads: []
  writes: []
triggers:
  - "triage this"
  - "what should I do with this"
  - "where does this go"
  - "what skill should I use"
  - "I have a [email/transcript/question] — what next"
success_rate: unrated
summary: "Classify incoming input and route it to the correct skill or chain."
---

## When
Something arrives — email, message, transcript, document, question — and the right skill isn't obvious. Use at the start of a session, or whenever input spans multiple skill types and a routing decision is needed before doing real work.

## Inputs
- Raw context: message, document, question, or short description
- Optional intent hint from the user ("I want to reply", "I want to file this")

## Procedure
1. Read or receive the incoming content and identify its nature.
2. Match the content against the routing table below to pick a target skill (or chain).
3. If the input is ambiguous, present 2 options ("Option A: skill X if goal is Y; Option B: skill Z if goal is W") and ask which fits.
4. State the routing decision in one line: "This looks like a `[skill]` task" or "This looks like a `[skill A] → [skill B]` chain — I'll start with `[skill A]`."
5. Hand off to the chosen skill, passing the context already gathered — do not re-read input.

### Routing table

| Input type | Target |
|---|---|
| Single question (partner or internal) | `answer-question` |
| Question + wants a reply | `answer-question` → `draft-response` |
| New issue report (email, message, complaint) | `log-issue` → `answer-question` → `draft-response` |
| Known-issue / bug report worth keeping | `log-issue` → `ingest-source` |
| Raw source needing cleanup | `clean-source` → `ingest-source` |
| Meeting transcript, API doc, chat log | `ingest-source` |
| "Process this source" / full pipeline | `ingest-full` (collapsed — preferred for new sources) |
| Account approaching UAT | `uat-prep` → `draft-response` |
| "What should I work on?" / "What's missing?" | `kb-gaps` |
| "Are articles stale / any orphans?" | `lint` |
| "Did the catalog get out of sync?" | `verify-catalog` |
| Just wrote new articles | `update-catalog` |

## Output
Inline routing decision — a single sentence naming the target skill (or chain) plus the context to pass forward. No file written.

## Hand-off
Invoke the chosen skill directly. Pass: the raw input, any classification already done (domain, urgency, audience), and the user's stated intent. Do not pass restated content — pass the original.

## Rating
| ✅ success | ⚠️ partial | ❌ failed |
- ✅ success — input is classified, a single skill or chain is chosen, and hand-off happens without re-asking the user for facts already in the input
- ⚠️ partial — routing requires the user to disambiguate between 2 options before hand-off
- ❌ failed — input is misrouted (wrong skill chosen) or triage stalls without a decision

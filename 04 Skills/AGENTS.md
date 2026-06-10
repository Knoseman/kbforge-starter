# Skills

Reusable workflows. Each skill lives in `04 Skills/skills/<id>.md` (free tier) or `pro-pack/skills/<id>.md` (Pro tier). Machine-readable index at `04 Skills/skills.jsonl`.

**Session start:** Read `04 Skills/PRIME.md` for fast paths — common requests that skip triage and load one skill directly.

---

## Skill Selection Protocol

### Step 0 — Check PRIME.md fast paths (recommended)

At session start, read `04 Skills/PRIME.md`. If the user's request matches a fast path, load that skill directly — no triage needed.

### Step 1 — Grep `skills.jsonl` by trigger phrase

Never read the index in full. Grep it:

```sh
# By trigger phrase (most accurate — match user intent)
rg -i 'answer this' "04 Skills/skills.jsonl"

# By kind
rg '"kind":"lookup"' "04 Skills/skills.jsonl"

# By the artifact type the user wants
rg '"outputs":\[[^]]*"draft_message"' "04 Skills/skills.jsonl"

# By chain origin (what skill commonly precedes another)
rg '"chains_to":\[[^]]*"draft-response"' "04 Skills/skills.jsonl"
```

Valid kinds: `lookup` · `capture` · `transform` · `report` · `meta`

### Step 2 — Read matched skill's `## When` and `## Procedure` sections only

Open `04 Skills/skills/<id>.md`. Read first 80 lines. Skip "Inputs", "Output", "Hand-off", "Rating" sections unless needed.

### Step 3 — Execute

Follow the numbered Procedure. Do not improvise alternate paths inside a step.

### Step 4 — End with a rating line

Every skill execution ends with a single line:

```
Rating: ✅ success | ⚠️ partial | ❌ failed
```

### Step 5 — Chain hand-off

If the skill chains to another, **pass artifact paths and bare ids**, not raw content:

> Done. Want me to chain to `draft-response`?
> (passing: answer text, sources=[domain.article-id], audience=partner)

---

**Never:** read `skills.jsonl` in full · invent skills not listed there · skip the rating line

---

## Authoring / Editing Rules

- **New skill** → write `04 Skills/skills/<id>.md` using the schema below; then run `python3 "04 Skills/scripts/build_skills_index.py"` to rebuild the index and chains aggregate.
- All `kind`, `triggers`, section names must conform to `04 Skills/schema.yaml`.
- Skills must end with a `## Rating` section listing the three states.

---

## Skill Frontmatter Schema

```yaml
---
id: skill-name                       # must equal filename (without .md)
title: Skill Title
kind: lookup                         # enum: lookup|capture|transform|report|meta
inputs: [question, context?]
outputs: [answer, sources, rating]
chains_to: [other-skill]
chains_from: [triage]
touches:
  reads:  ["01 Reference/catalog.jsonl"]
  writes: ["05 Iteration Logs/KB Gaps.md"]
triggers:
  - "trigger phrase"
  - "alternate phrasing"
success_rate: unrated
summary: "One-line description of what the skill does."
---
```

## Skill Body Structure (fixed order)

```
## When
Prose. One paragraph. When does this skill apply?

## Inputs
Bullets. What the skill needs to know before starting.

## Procedure
Numbered steps. Each step = one action. No alternatives inside a step.

## Output
What artifact is produced and where (file path or inline).

## Hand-off
Likely next skill in the chain; what to pass it.

## Rating
| ✅ success | ⚠️ partial | ❌ failed |
```

---

## Aggregates

| File | What |
|---|---|
| `04 Skills/skills.jsonl` | Machine-readable skill index (grep this) |
| `04 Skills/aggregates/chains.md` | Known skill chains — auto-generated |

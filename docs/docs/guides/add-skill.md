# How to Add a New Skill

Skills are reusable AI workflows. Adding a new one is as simple as writing a Markdown file.

---

## Skill file structure

Create a new file in `04 Skills/skills/<skill-id>.md`:

```markdown
---
id: my-skill
title: My Skill
kind: synthesis
inputs: [file_path, question]
outputs: [answer]
chains_to: []
chains_from: [triage]
touches:
  reads: ["01 Reference/articles/*.md"]
  writes: ["02 Outputs/*.md"]
triggers:
  - "do my skill"
  - "run my skill"
success_rate: unrated
summary: "What this skill does in one line."
---

## When

Describe the situation that triggers this skill.

## Inputs

- What the skill needs to run

## Procedure

1. Step one
2. Step two
3. Step three

## Output

What the skill produces.

## Hand-off

What to do next, if anything.

## Rating

- ✅ success — criteria for a successful run
- ⚠️ partial — criteria for a partial run
- ❌ failed — criteria for a failed run
```

---

## Frontmatter reference

| Field | Description |
|-------|-------------|
| `id` | Unique identifier, lowercase with hyphens |
| `title` | Human-readable title |
| `kind` | `capture`, `synthesis`, `quality`, or `output` |
| `inputs` | What the skill needs |
| `outputs` | What the skill produces |
| `chains_to` | Skills that typically follow |
| `chains_from` | Skills that typically precede |
| `touches` | Files read and written |
| `triggers` | Natural-language phrases that activate this skill |
| `success_rate` | `unrated` until you have data |
| `summary` | One-line description |

---

## Register the skill

After creating the file, rebuild the skill index:

```bash
python3 "04 Skills/scripts/build_skills_index.py"
```

This regenerates `skills.jsonl` so the AI can find your new skill by its triggers.

---

## Test the skill

Open your AI CLI and use one of the trigger phrases:

```
Do my skill
```

The AI should load your skill and follow its procedure. If it doesn't, check:

- The `triggers:` match your phrasing exactly
- `skills.jsonl` was regenerated after you added the file
- The skill file is in `04 Skills/skills/` (not a subfolder)

---

## Tips

- **Start simple.** A 5-step skill is easier to debug than a 20-step one.
- **Use the rating section.** Track success/failure to improve the skill over time.
- **Chain intentionally.** If your skill always leads to another, declare `chains_to`.
- **Be specific in triggers.** "Process this" is too broad. "Generate a UAT checklist" is specific.

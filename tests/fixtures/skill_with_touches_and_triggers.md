---
id: test-skill
title: Test Skill
kind: capture
inputs: [source_path]
outputs: [article]
chains_to: [kb-gaps]
chains_from: [triage]
collapsed_from: [clean-source, ingest-source]
fast_path: true
touches:
  reads:
    - "00 Raw Sources/**/*"
    - "01 Reference/catalog.jsonl"
  writes:
    - "00 Raw Sources/**/*.md"
    - "01 Reference/articles/*.md"
triggers:
  - "process this source"
  - "ingest this transcript"
  - "full ingest"
success_rate: unrated
summary: "Complete pipeline test."
---

## When
Test body content.

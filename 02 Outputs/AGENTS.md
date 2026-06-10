# Outputs

Working output buffer — drafts live here until reviewed, sent, or promoted.

---

## Lifecycle

| Type | Naming convention | Lifetime |
|------|------------------|----------|
| Issue note | `YYYY-MM-DD [Account] - [Issue].md` | Active while open; keep for reference after |
| Draft reply | `YYYY-MM-DD [Audience] - [Description] - DRAFT.md` | Temporary — send then archive/delete |
| UAT checklist | `YYYY-MM-DD [Account] - UAT Checklist [Product] [Mode].md` | Keep until UAT complete |
| Reusable guide | `(C) [Description].md` | Permanent |
| Email template | `(C) [Description].md` | Permanent |

**Promotion:** Evergreen `(C)` output → move to `01 Reference/`. Per-account customisable → keep here as template.

**Archival:** Sent dated drafts → delete or move to `Archive/`. `(C)` files stay until promoted or retired.

---

## Frontmatter Schema

```yaml
---
type: [draft-response | issue-note | uat-checklist | output-template | account-guide]
date: YYYY-MM-DD
account: [Account name, if applicable]
status: [draft | ready-for-review | sent | resolved | archived]
kb_coverage: [Covered | Partial | Gap]
---
```

---

## Applicable Skills

| Task | Skill |
|------|-------|
| Capture a new issue | `log-issue` |
| Write a partner or internal reply | `draft-response` |
| Build a UAT checklist | `uat-prep` |

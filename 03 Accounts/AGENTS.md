# Accounts

Lightweight context cards for active partners and clients. One file per account — enough for the KB AI to work without opening a separate vault.

---

## Do I need this folder?

**Yes if** you regularly draft responses to partners or clients and want the AI to know their integration type, current phase, and blockers.

**No if** this is a personal or internal-only KB. You can delete this folder — the `draft-response` skill will skip account grounding.

---

## Purpose

This folder is a **bridge layer**, not a CRM. It holds the minimum context needed in this vault:
- Integration type and product (for KB article matching)
- Current phase and blockers (for response drafting)
- Technical and commercial contacts (for routing)
- Links to relevant KB articles

**Full operational detail** (meetings, email threads, action items, history) lives elsewhere.

---

## Lookup Protocol

1. Read this `AGENTS.md` to understand scope.
2. If you need context for a specific account, open `[AccountName].md` directly — do not `ls` this folder.
3. Use the account's `integration_type` and `product` fields to identify relevant KB articles in `01 Reference/`.

---

## Keeping Profiles Current

When an account's phase, blockers, or integration path changes, update the profile here. This is the only file you need to touch — do not replicate full history.

**Fields to keep updated:** `phase`, `blockers`, status paragraph.

---

## File Naming

`(C) [AccountName].md` — use the common trading name.

---

## Frontmatter Schema

```yaml
---
account: Account Name
integration_type: [api | sdk | webhook | other]
product: Product or platform name
phase: [discovery | development | testing | uat | live]
status: active           # enum: active | on-hold | churned
updated: YYYY-MM-DD
contacts:
  technical: Name — role
  commercial: Name — role
kb_articles: [id1, id2]  # relevant article ids
blockers: []
---
```

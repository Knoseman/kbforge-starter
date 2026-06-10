---
id: acme-api.errors
title: Acme Payments API — Errors and Result Codes
kind: reference
domain: acme-api
topics: [errors, result-codes, troubleshooting]
status: current
updated: 2026-06-03
owner: ai
provenance:
  - "[[00 Raw Sources/Archive/2026-06-03 Acme API Intro Transcript.md]]"
related: [acme-api.overview, acme-api.authentication]
summary: "Acme API errors use standard HTTP status codes plus a JSON body with a machine-readable `code` field and human-readable `message`."
answers:
  - "What does error code X mean in the Acme API?"
  - "How do I handle errors from the Acme API?"
  - "What HTTP status codes does the Acme API use?"
---

## Answer
All Acme API errors return a JSON body with `code` (machine-readable string) and `message` (human-readable). HTTP status follows standard conventions: 4xx for client errors, 5xx for server errors. Retry logic should only be applied to 5xx and `429` responses.

## Facts

**HTTP status codes:**
| Status | Meaning |
|---|---|
| `200` | Success |
| `400` | Bad request — invalid body or missing required field |
| `401` | Unauthorized — invalid or missing API key |
| `404` | Not found — resource id does not exist |
| `409` | Conflict — e.g. payment already captured |
| `422` | Unprocessable — request valid but business rule rejected it |
| `429` | Rate limit exceeded — back off and retry |
| `500` | Internal server error — retry with exponential backoff |

**Common `code` values:**
| code | Cause |
|---|---|
| `key_environment_mismatch` | Sandbox key used on production URL or vice versa |
| `payment_already_captured` | Capture called on already-captured payment |
| `insufficient_funds` | Card declined by issuer |
| `invalid_card` | Card number failed Luhn check |

## Pitfalls
- Do not retry `4xx` errors (except `429`) — they will not self-resolve.
- `422` errors include a `fields` array listing which fields failed validation — log it.

## See also
acme-api.overview · acme-api.authentication

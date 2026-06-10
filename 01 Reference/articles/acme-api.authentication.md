---
id: acme-api.authentication
title: Acme Payments API — Authentication
kind: reference
domain: acme-api
topics: [authentication, api-key, credentials, test-environments]
status: current
updated: 2026-06-03
owner: ai
provenance:
  - "[[00 Raw Sources/Archive/2026-06-03 Acme API Intro Transcript.md]]"
related: [acme-api.overview]
summary: "The Acme API uses Bearer token authentication. Sandbox and production keys are separate and issued from the developer portal."
answers:
  - "How do I authenticate with the Acme API?"
  - "Where do I get an Acme API key?"
  - "What is the difference between sandbox and production keys?"
---

## Answer
Authenticate by passing your API key as a Bearer token in the `Authorization` header: `Authorization: Bearer <your-key>`. Sandbox keys (prefix `sk_test_`) and production keys (prefix `sk_live_`) are separate. Both are issued from the Acme developer portal at `https://developer.acme.example`.

## Facts
- **Header:** `Authorization: Bearer sk_test_xxxx` (sandbox) or `sk_live_xxxx` (production)
- **Key rotation:** Keys do not expire but can be revoked from the portal at any time
- **Sandbox:** Use `https://sandbox.api.acme.example/v2` — no real transactions occur
- **Production:** Use `https://api.acme.example/v2` — requires KYC approval before activation

## Pitfalls
- Using a production key against the sandbox URL (or vice versa) returns a `401 Unauthorized` with `code: key_environment_mismatch`.
- API keys are single-string secrets — do not commit them to source control.

## See also
acme-api.overview

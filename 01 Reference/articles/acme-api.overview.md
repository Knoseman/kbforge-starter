---
id: acme-api.overview
title: Acme Payments API — Overview
kind: reference
domain: acme-api
topics: [overview, endpoints, authentication, lifecycle]
status: current
updated: 2026-06-03
owner: ai
provenance:
  - "[[00 Raw Sources/Archive/2026-06-03 Acme API Intro Transcript.md]]"
related: [acme-api.authentication, acme-api.errors]
summary: "The Acme Payments API is a REST API that lets merchants initiate and manage payment transactions. Base URL: https://api.acme.example/v2."
answers:
  - "What is the Acme Payments API?"
  - "Where is the Acme API documentation?"
  - "What does the Acme API do?"
---

## Answer
The Acme Payments API is a JSON REST API for initiating, confirming, and refunding payment transactions. It uses API key authentication and follows standard HTTP status codes. The base URL for production is `https://api.acme.example/v2`; sandbox is `https://sandbox.api.acme.example/v2`.

## Facts
- **Authentication:** API key passed as `Authorization: Bearer <key>` header
- **Content-Type:** `application/json` for all requests and responses
- **Rate limit:** 100 requests/minute per API key (sandbox: 10 req/min)
- **Versioning:** URL-path versioned (`/v2/`); breaking changes create a new version

**Core endpoints:**
| Endpoint | Method | Purpose |
|---|---|---|
| `/payments` | POST | Initiate a payment |
| `/payments/{id}` | GET | Retrieve payment status |
| `/payments/{id}/capture` | POST | Capture an authorised payment |
| `/payments/{id}/refund` | POST | Refund a completed payment |

## See also
acme-api.authentication · acme-api.errors

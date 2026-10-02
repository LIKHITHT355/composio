# RUBRIC.md - Decision Rules, Enumerations & Tie-Breakers

This document specifies the exact ground-truth criteria, scoring definitions, and tie-breaker policies for all enum fields in the Composio App Buildability research pipeline.

---

## 1. Key Fields (KF) Scored in Benchmark

The six Key Fields (KF) evaluated during ground truth benchmarking are:
1. `auth_methods`
2. `credential_access`
3. `api.exists`
4. `mcp.status`
5. `verdict`
6. `main_blocker`

---

## 2. Enumeration Rubrics

### 2.1 `auth_methods` (List of Enums)
Supported authentication mechanisms for invoking the application's developer API.

| Enum Value | Decision Rule | Concrete Example | Tie-Breaker / Edge Case Policy |
|---|---|---|---|
| `oauth2` | API supports standard OAuth 2.0 authorization code, client credentials, or PKCE flow. | Slack, GitHub, Salesforce, HubSpot | If an app supports both OAuth2 and API Key, BOTH must be listed in the array. |
| `api_key` | Static API key / token generated in dashboard and sent via header (e.g. `X-Api-Key`, `api-key`) or query param. | Stripe, Airtable, SendGrid | If the key is passed as `Authorization: Bearer <key>`, prefer `api_key` if it is a static dashboard key; label `bearer_token` if dynamically issued. |
| `bearer_token` | Short-lived or session-based bearer token passed in `Authorization: Bearer <token>` without full OAuth2 handshake. | Supabase service tokens, specialized JWT endpoints | Distinguish from `api_key` by documentation specifying Bearer scheme token lifecycles. |
| `basic` | HTTP Basic Auth (`Authorization: Basic base64(user:pass)`). | Jira legacy, Twilio API credentials | Include only if actively documented as a primary or supported auth method. |
| `jwt` | API expects self-signed JSON Web Tokens or asymmetric RSA/ECDSA signed claims. | Apple developer APIs, specialized identity services | Do not use for standard OAuth2 access tokens that happen to be in JWT format internally. |
| `hmac_signing` | Requests require cryptographic hash/signature calculated over payload/timestamp (HMAC-SHA256). | Binance REST API, AWS services, Shopify webhook validation | Required when endpoints fail without signed headers. |
| `aws_sigv4` | Specifically requires AWS Signature Version 4 protocol. | Amazon Selling Partner API (SP-API) | Specific subset of HMAC signing for Amazon ecosystem. |
| `none` | Endpoints require no credentials or authentication. | Public read-only endpoints, local OSS CLIs (Sherlock, Mermaid CLI) | Only valid when endpoints or CLI tools can be run without any credentials. |
| `other` | Proprietary or legacy auth mechanisms (e.g. MTLS, cookie sessions, custom handshake). | Legacy banking or internal enterprise interfaces | Must document mechanism in `auth_notes`. |

---

### 2.2 `credential_access` (Single Enum)
How an engineer or AI agent developer acquires credentials to build and test an integration.

| Enum Value | Decision Rule | Concrete Example | Tie-Breaker / Edge Case Policy |
|---|---|---|---|
| `self_serve_free` | Anyone can sign up for a free account/tier and immediately generate API keys or register an OAuth app. | GitHub, Stripe, Supabase, Airtable, Notion | If a credit card is required for verification but no charge is made and free tier exists, classify as `self_serve_free`. |
| `self_serve_trial` | Instant signup provides a time-limited or credit-limited trial with full API access, without sales intervention. | Twilio (free trial credits), Datadog 14-day trial | Must not require sales rep outreach to activate trial. |
| `paid_plan_required` | API access or key generation is hard-locked behind a paid subscription plan. | X/Twitter Basic tier ($100/mo), Ahrefs ($99/mo), SE Ranking | If a free app account exists, but API keys are disabled until upgraded to Paid, choose `paid_plan_required`. |
| `approval_required` | Requires app review, developer application approval, or compliance verification before keys are issued. | Meta Marketing API (App Review), LinkedIn Ads API, WhatsApp Business API | If self-serve signup exists but the API app cannot call endpoints without submitting for review, choose `approval_required`. |
| `partner_or_sales_gated` | No self-serve signup or key issuance; must contact sales or qualify for formal partner program. | PitchBook, DealCloud, Salesforce Commerce Cloud (B2B Enterprise) | If pricing page says "Contact Sales" or "Request Demo" with no developer portal self-signup, choose `partner_or_sales_gated`. |
| `no_public_api` | Product has no public developer API documented or available. | NotebookLM (consumer), systeme.io (no public endpoints) | Use when no public developer documentation exists. |
| `not_applicable` | Tool is a local library, CLI, or open-source repo with no central hosted credential service. | Sherlock, Mermaid CLI | Reserved for local OSS packages where API credentials do not apply. |

---

### 2.3 `api.exists` (Boolean)
- `true`: Documented, active developer API exists.
- `false`: No documented public API exists, or the service is completely closed.

---

### 2.4 `api.styles` (List of Enums)
- `rest`: Standard HTTP REST endpoints with JSON/XML payloads.
- `graphql`: GraphQL endpoint (queries/mutations/subscriptions).
- `soap`: XML-based SOAP / WSDL interface (e.g. legacy Salesforce, enterprise ERPs).
- `grpc`: Protocol Buffers over HTTP/2.
- `sdk_only`: Vendor only provides client libraries without documenting raw HTTP endpoints.
- `cli`: Command-line executable or subcommands.

---

### 2.5 `api.breadth` (Single Enum)
- `broad`: Full CRUD across all primary domain models (e.g. Salesforce, GitHub, Stripe, HubSpot).
- `moderate`: Key workflows covered, but auxiliary features missing (e.g. SendGrid, Linear, Front).
- `narrow`: Only 1-3 specific endpoints (e.g. single transcript lookup, URL ping, simple webhook trigger).
- `none`: No API endpoints exist.

---

### 2.6 `mcp.status` (Single Enum)
- `official`: First-party Model Context Protocol server developed and maintained by the vendor.
- `community`: Third-party open-source MCP server published on GitHub or community registries (e.g. Smithery, PulseMCP).
- `none`: No known public MCP server found after targeted search.
- `unknown`: Search query inconclusive or unreachable.

---

### 2.7 `build_form` (Single Enum)
Recommended packaging for Composio toolkit engineering.

| Enum Value | Decision Rule |
|---|---|
| `api_toolkit` | Standard Composio Python/TypeScript toolkit calling HTTP REST/GraphQL endpoints with managed auth. |
| `reuse_existing_mcp` | An existing high-quality official or trusted community MCP server can be wrapped directly. |
| `cli_skill` | Tool is packaged as a local executable/CLI subagent skill (e.g. Sherlock, Mermaid CLI). |
| `not_buildable` | No public API exists, or gating prevents automated invocation. |

---

### 2.8 `verdict` (Single Enum)
High-level strategic buildability verdict for Composio product operations.

| Verdict | Definition & Criteria |
|---|---|
| `ready_now` | Documented public API + self-serve (free or trial) credentials + standard OAuth2/API key + no mandatory approval for core endpoints. Composio can build and test immediately without human hurdles. |
| `ready_with_caveats` | Buildable, but with an operational or financial catch: paid plan required, complex request signing (HMAC/AWS SigV4), strict rate limits, or non-core scope reviews. |
| `needs_outreach` | API exists, but access requires formal partnership, sales engagement, or strict business enterprise verification. |
| `blocked` | No usable public API found, endpoints decommissioned, or product strictly closed to third-party integrations. |
| `not_an_api_product` | Local command-line tool, library, or offline script; no hosted cloud API. |

#### Verdict Tie-Breakers:
1. If `api.exists` is `false` and the product is a CLI tool -> `not_an_api_product`.
2. If `api.exists` is `false` and the product is a hosted web app -> `blocked`.
3. If `credential_access` is `approval_required` or `partner_or_sales_gated` -> `needs_outreach`.
4. If `credential_access` is `paid_plan_required` -> `ready_with_caveats` (Main blocker: `paid_plan`).
5. If `auth_methods` includes `hmac_signing` or `aws_sigv4` and access is self-serve -> `ready_with_caveats` (Main blocker: `complex_auth`).
6. If an app has a public self-serve API but requires App Review ONLY for extended permissions (e.g. Meta basic read vs ads management) -> `ready_with_caveats`.

---

### 2.9 `main_blocker` (Single Enum)
The primary operational obstacle preventing instant toolkit development.

- `none`: No blockers; builds smoothly (`ready_now`).
- `no_public_api`: Product lacks any public API endpoints (`blocked`).
- `paid_plan`: Must subscribe to a paid tier to access developer tools or obtain keys (`ready_with_caveats`).
- `app_review_or_approval`: Requires submitting an application, business verification, or manual compliance review (`needs_outreach` or `ready_with_caveats`).
- `partner_program`: Access restricted exclusively to certified technology partners (`needs_outreach`).
- `contact_sales`: Enterprise demo or sales rep approval required (`needs_outreach`).
- `complex_auth`: Non-standard authentication like HMAC payload signing, dynamic nonce generation, or AWS SigV4 (`ready_with_caveats`).
- `docs_unclear`: Incomplete, conflicting, or severely deprecated developer documentation.
- `not_a_hosted_service`: Tool runs locally on client machine as an executable/CLI (`not_an_api_product`).
- `other`: Specialized blocker not covered by the above (must detail in `verdict_reason`).

---

## 3. Evidence & Citation Standards (R1 & R2)

1. **Every claim requires an Evidence Item**:
   - `field`: The key field being proven.
   - `url`: The exact URL fetched during research.
   - `quote`: Verbatim quote of 300 characters or fewer from the fetched page.
2. **Deterministic Verification**:
   - The verifier automatically checks that `quote.strip()` exists as a continuous substring inside the raw cached text of the page at `url`.
   - If not found or if altered, `quote_verified` is set to `false`.
3. **Official Sources First**:
   - Priority 1: Vendor developer portal (`docs.vendor.com`, `developer.vendor.com`, official OpenAPI specs).
   - Priority 2: Vendor GitHub organization repositories.
   - Priority 3: Vendor pricing and help center pages.
   - Priority 4 (Low Trust): Community blog posts or third-party directories (must be flagged low confidence).

# FAILURES.md - System Failure Log & Defeated Apps

This document tracks all apps that defeated the agent, anomalous extraction failures, ambiguities, and edge cases across Agent v1, v2, and v3 pipelines.

---

## 1. Baseline Failure Modes (Agent v1)

| App | Category | What Failed | Root Cause |
|---|---|---|---|
| **Sherlock** | Data, SEO and Scraping | Extracted as `ready_with_caveats` / API service | Naive agent relied on superficial snippets without verifying whether Sherlock is a hosted cloud API or a local Python CLI tool. |
| **Mermaid CLI** | AI, Research and Media-native | Confused with SaaS diagramming API | Local NodeJS CLI was treated as a cloud API service because documentation mentions rendering endpoints. |
| **NotebookLM** | AI, Research and Media-native | Identified as public developer API | Conflated Google Gemini Enterprise API with consumer NotebookLM, which has no public API. |
| **Close** | CRM and Sales | Initially marked `blocked` / `no_public_api` in brief search | Search snippet returned high-level sales landing page instead of `developer.close.com`. |
| **Amazon Selling Partner** | Ecommerce | Underestimated gating hurdles | Labelled as `ready_now` by naive model, missing mandatory AWS IAM SigV4 signing, developer profile registration, and strict restricted data access approval. |

---

## 2. Evidence Grounding & Verification Failures (v2 / v3)

| App | Pipeline Stage | Discrepancy / Blocker Encountered | Resolution & Provenance |
|---|---|---|---|
| **DealCloud** | Verifier A / B | Documentation behind gated partner portal (`api.docs.dealcloud.com` requires authentication). | Flagged as `partner_or_sales_gated`, `needs_human=True`. |
| **PitchBook** | Discovery | API pricing and developer documentation strictly gated behind institutional sales outreach. | Classified as `needs_outreach`, blocker: `contact_sales`. |
| **systeme.io** | Extraction | No public REST API documentation found on official domain. | Verified as `blocked`, blocker: `no_public_api`. |
| **fanbasis** | Discovery | Consumer creator platform with zero developer documentation or API keys. | Verified as `blocked`, blocker: `no_public_api`. |
| **Paygent Connect** | Discovery | White-labeled payment gateway powered by NMI; conflicting developer resources. | Disputed by skeptic verifier, confidence: `low`, flagged for human adjudication. |

---

## 3. Grounding Verification Metrics

- **Deterministic Quote Verification Rate (Verifier A)**: Reported automatically per run.
- **Skeptic Challenge Rate (Verifier B)**: Tracks how many v2 claims were refuted or flagged by independent audit.

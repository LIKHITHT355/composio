# Verification Misses Log & Detailed Error Taxonomy

## Version V1 Misses (64 total discrepancies)

| App | Field | Agent Said | Ground Truth | Error Taxonomy Cause |
|---|---|---|---|---|
| **Attio** | `auth_methods` | `['oauth2', 'bearer_token']` | `['bearer_token', 'api_key', 'oauth2']` | missed_gating_nuance |
| **Twenty** | `mcp.status` | `none` | `community` | missed_gating_nuance |
| **DealCloud** | `auth_methods` | `['api_key', 'bearer_token']` | `['oauth2']` | missed_gating_nuance |
| **DealCloud** | `credential_access` | `self_serve_free` | `partner_or_sales_gated` | missed_gating_nuance |
| **DealCloud** | `verdict` | `ready_now` | `needs_outreach` | over_generous_verdict |
| **DealCloud** | `main_blocker` | `none` | `contact_sales` | missed_gating_nuance |
| **Front** | `auth_methods` | `['oauth2', 'api_key', 'bearer_token']` | `['bearer_token', 'oauth2']` | missed_gating_nuance |
| **Front** | `credential_access` | `self_serve_free` | `self_serve_trial` | missed_gating_nuance |
| **Plain** | `auth_methods` | `['api_key']` | `['bearer_token', 'api_key']` | missed_gating_nuance |
| **Gladly** | `credential_access` | `paid_plan_required` | `partner_or_sales_gated` | missed_gating_nuance |
| **Gladly** | `verdict` | `ready_with_caveats` | `needs_outreach` | missed_gating_nuance |
| **Gladly** | `main_blocker` | `none` | `contact_sales` | missed_gating_nuance |
| **Pumble** | `auth_methods` | `['oauth2', 'api_key']` | `['oauth2', 'bearer_token']` | missed_gating_nuance |
| **Pumble** | `credential_access` | `self_serve_trial` | `paid_plan_required` | missed_gating_nuance |
| **Pumble** | `verdict` | `ready_now` | `ready_with_caveats` | over_generous_verdict |
| **Pumble** | `main_blocker` | `none` | `paid_plan` | missed_gating_nuance |
| **GoHighLevel** | `auth_methods` | `['oauth2', 'api_key']` | `['oauth2', 'api_key', 'bearer_token']` | missed_gating_nuance |
| **GoHighLevel** | `credential_access` | `self_serve_trial` | `paid_plan_required` | missed_gating_nuance |
| **GoHighLevel** | `verdict` | `ready_now` | `ready_with_caveats` | over_generous_verdict |
| **GoHighLevel** | `main_blocker` | `none` | `paid_plan` | missed_gating_nuance |
| **Salesforce Commerce Cloud** | `auth_methods` | `['oauth2']` | `['oauth2', 'bearer_token']` | missed_gating_nuance |
| **Amazon Selling Partner** | `mcp.status` | `none` | `community` | missed_gating_nuance |
| **Amazon Selling Partner** | `main_blocker` | `app_review_or_approval` | `complex_auth` | missed_gating_nuance |
| **fanbasis** | `auth_methods` | `[]` | `['none']` | missed_gating_nuance |
| **Firecrawl** | `auth_methods` | `['bearer_token']` | `['bearer_token', 'api_key']` | missed_gating_nuance |
| **Firecrawl** | `mcp.status` | `none` | `official` | missed_gating_nuance |
| **Sherlock** | `auth_methods` | `['api_key']` | `['none']` | missed_gating_nuance |
| **Sherlock** | `credential_access` | `self_serve_free` | `not_applicable` | missed_gating_nuance |
| **Sherlock** | `api.exists` | `True` | `False` | hallucinated |
| **Sherlock** | `mcp.status` | `none` | `community` | missed_gating_nuance |
| **Sherlock** | `verdict` | `ready_with_caveats` | `not_an_api_product` | wrong_entity |
| **Sherlock** | `main_blocker` | `other` | `not_a_hosted_service` | missed_gating_nuance |
| **Waterfall.io** | `credential_access` | `no_public_api` | `partner_or_sales_gated` | missed_gating_nuance |
| **Waterfall.io** | `api.exists` | `False` | `True` | missed_gating_nuance |
| **Waterfall.io** | `verdict` | `blocked` | `needs_outreach` | missed_gating_nuance |
| **Waterfall.io** | `main_blocker` | `no_public_api` | `contact_sales` | missed_gating_nuance |
| **MongoDB Atlas** | `auth_methods` | `['oauth2', 'api_key']` | `['basic', 'hmac_signing']` | missed_gating_nuance |
| **MongoDB Atlas** | `mcp.status` | `none` | `official` | missed_gating_nuance |
| **MongoDB Atlas** | `verdict` | `ready_now` | `ready_with_caveats` | over_generous_verdict |
| **MongoDB Atlas** | `main_blocker` | `none` | `complex_auth` | missed_gating_nuance |
| **Datadog** | `mcp.status` | `none` | `community` | missed_gating_nuance |
| **Notion** | `mcp.status` | `community` | `official` | missed_gating_nuance |
| **Asana** | `mcp.status` | `none` | `community` | missed_gating_nuance |
| **Monday.com** | `auth_methods` | `['api_key', 'bearer_token', 'oauth2']` | `['bearer_token', 'oauth2']` | missed_gating_nuance |
| **Monday.com** | `mcp.status` | `none` | `community` | missed_gating_nuance |
| **QuickBooks** | `credential_access` | `self_serve_free` | `approval_required` | missed_gating_nuance |
| **QuickBooks** | `mcp.status` | `none` | `community` | missed_gating_nuance |
| **QuickBooks** | `main_blocker` | `none` | `app_review_or_approval` | missed_gating_nuance |
| **Brex** | `credential_access` | `self_serve_free` | `paid_plan_required` | missed_gating_nuance |
| **Brex** | `mcp.status` | `official` | `community` | missed_gating_nuance |
| **Brex** | `verdict` | `ready_now` | `ready_with_caveats` | over_generous_verdict |
| **Brex** | `main_blocker` | `none` | `paid_plan` | missed_gating_nuance |
| **PitchBook** | `auth_methods` | `['other']` | `['api_key', 'bearer_token']` | missed_gating_nuance |
| **PitchBook** | `main_blocker` | `partner_program` | `contact_sales` | missed_gating_nuance |
| **NotebookLM** | `auth_methods` | `['oauth2', 'api_key']` | `['none']` | missed_gating_nuance |
| **NotebookLM** | `credential_access` | `approval_required` | `no_public_api` | missed_gating_nuance |
| **NotebookLM** | `api.exists` | `True` | `False` | hallucinated |
| **NotebookLM** | `verdict` | `ready_with_caveats` | `blocked` | missed_gating_nuance |
| **NotebookLM** | `main_blocker` | `app_review_or_approval` | `no_public_api` | missed_gating_nuance |
| **Mermaid CLI** | `mcp.status` | `none` | `community` | missed_gating_nuance |
| **Mermaid CLI** | `verdict` | `ready_with_caveats` | `not_an_api_product` | wrong_entity |
| **Grain** | `credential_access` | `self_serve_trial` | `paid_plan_required` | missed_gating_nuance |
| **Grain** | `verdict` | `ready_now` | `ready_with_caveats` | over_generous_verdict |
| **Grain** | `main_blocker` | `none` | `paid_plan` | missed_gating_nuance |

## Version V2 Misses (96 total discrepancies)

| App | Field | Agent Said | Ground Truth | Error Taxonomy Cause |
|---|---|---|---|---|
| **Twenty** | `auth_methods` | `['bearer_token']` | `['bearer_token', 'api_key']` | missed_gating_nuance |
| **Twenty** | `mcp.status` | `none` | `community` | missed_gating_nuance |
| **DealCloud** | `auth_methods` | `['oauth2', 'bearer_token', 'api_key']` | `['oauth2']` | missed_gating_nuance |
| **DealCloud** | `main_blocker` | `none` | `contact_sales` | missed_gating_nuance |
| **Front** | `auth_methods` | `['oauth2', 'bearer_token', 'api_key', 'basic']` | `['bearer_token', 'oauth2']` | missed_gating_nuance |
| **Front** | `credential_access` | `self_serve_free` | `self_serve_trial` | missed_gating_nuance |
| **Front** | `mcp.status` | `official` | `none` | missed_gating_nuance |
| **Gladly** | `auth_methods` | `['basic', 'jwt', 'hmac_signing']` | `['basic']` | missed_gating_nuance |
| **Gladly** | `credential_access` | `no_public_api` | `partner_or_sales_gated` | missed_gating_nuance |
| **Gladly** | `verdict` | `ready_with_caveats` | `needs_outreach` | missed_gating_nuance |
| **Gladly** | `main_blocker` | `none` | `contact_sales` | missed_gating_nuance |
| **Lark (Larksuite)** | `auth_methods` | `['oauth2']` | `['bearer_token', 'oauth2']` | missed_gating_nuance |
| **Lark (Larksuite)** | `mcp.status` | `official` | `none` | missed_gating_nuance |
| **Pumble** | `auth_methods` | `['api_key']` | `['oauth2', 'bearer_token']` | missed_gating_nuance |
| **Pumble** | `credential_access` | `self_serve_trial` | `paid_plan_required` | missed_gating_nuance |
| **Pumble** | `verdict` | `ready_now` | `ready_with_caveats` | over_generous_verdict |
| **Pumble** | `main_blocker` | `none` | `paid_plan` | missed_gating_nuance |
| **WhatsApp Business** | `auth_methods` | `['none']` | `['bearer_token', 'oauth2']` | missed_gating_nuance |
| **WhatsApp Business** | `credential_access` | `no_public_api` | `approval_required` | missed_gating_nuance |
| **WhatsApp Business** | `api.exists` | `False` | `True` | missed_gating_nuance |
| **WhatsApp Business** | `verdict` | `blocked` | `ready_with_caveats` | missed_gating_nuance |
| **WhatsApp Business** | `main_blocker` | `no_public_api` | `app_review_or_approval` | missed_gating_nuance |
| **Google Ads** | `auth_methods` | `['oauth2', 'jwt']` | `['oauth2']` | missed_gating_nuance |
| **Google Ads** | `mcp.status` | `community` | `none` | missed_gating_nuance |
| **GoHighLevel** | `auth_methods` | `['bearer_token', 'oauth2']` | `['oauth2', 'api_key', 'bearer_token']` | missed_gating_nuance |
| **GoHighLevel** | `credential_access` | `self_serve_trial` | `paid_plan_required` | missed_gating_nuance |
| **GoHighLevel** | `mcp.status` | `community` | `none` | missed_gating_nuance |
| **GoHighLevel** | `verdict` | `ready_now` | `ready_with_caveats` | over_generous_verdict |
| **GoHighLevel** | `main_blocker` | `none` | `paid_plan` | missed_gating_nuance |
| **systeme.io** | `auth_methods` | `['none']` | `['api_key']` | missed_gating_nuance |
| **systeme.io** | `credential_access` | `no_public_api` | `self_serve_free` | missed_gating_nuance |
| **systeme.io** | `api.exists` | `False` | `True` | missed_gating_nuance |
| **systeme.io** | `verdict` | `blocked` | `ready_now` | missed_gating_nuance |
| **systeme.io** | `main_blocker` | `no_public_api` | `none` | missed_gating_nuance |
| **Salesforce Commerce Cloud** | `auth_methods` | `['none']` | `['oauth2', 'bearer_token']` | missed_gating_nuance |
| **Amazon Selling Partner** | `auth_methods` | `['other']` | `['oauth2', 'aws_sigv4']` | missed_gating_nuance |
| **Amazon Selling Partner** | `mcp.status` | `none` | `community` | missed_gating_nuance |
| **Amazon Selling Partner** | `verdict` | `blocked` | `ready_with_caveats` | missed_gating_nuance |
| **Amazon Selling Partner** | `main_blocker` | `app_review_or_approval` | `complex_auth` | missed_gating_nuance |
| **fanbasis** | `api.exists` | `True` | `False` | hallucinated |
| **fanbasis** | `mcp.status` | `official` | `none` | missed_gating_nuance |
| **fanbasis** | `verdict` | `ready_with_caveats` | `blocked` | missed_gating_nuance |
| **fanbasis** | `main_blocker` | `none` | `no_public_api` | missed_gating_nuance |
| **Firecrawl** | `auth_methods` | `['none']` | `['bearer_token', 'api_key']` | missed_gating_nuance |
| **Firecrawl** | `credential_access` | `no_public_api` | `self_serve_free` | missed_gating_nuance |
| **Firecrawl** | `api.exists` | `False` | `True` | missed_gating_nuance |
| **Firecrawl** | `mcp.status` | `none` | `official` | missed_gating_nuance |
| **Firecrawl** | `verdict` | `blocked` | `ready_now` | missed_gating_nuance |
| **Firecrawl** | `main_blocker` | `no_public_api` | `none` | missed_gating_nuance |
| **Sherlock** | `credential_access` | `no_public_api` | `not_applicable` | missed_gating_nuance |
| **Sherlock** | `verdict` | `ready_with_caveats` | `not_an_api_product` | wrong_entity |
| **Sherlock** | `main_blocker` | `none` | `not_a_hosted_service` | missed_gating_nuance |
| **Waterfall.io** | `auth_methods` | `['none']` | `['api_key']` | missed_gating_nuance |
| **Waterfall.io** | `credential_access` | `no_public_api` | `partner_or_sales_gated` | missed_gating_nuance |
| **Waterfall.io** | `api.exists` | `False` | `True` | missed_gating_nuance |
| **Waterfall.io** | `verdict` | `blocked` | `needs_outreach` | missed_gating_nuance |
| **Waterfall.io** | `main_blocker` | `no_public_api` | `contact_sales` | missed_gating_nuance |
| **Cloudflare** | `auth_methods` | `['api_key']` | `['bearer_token', 'api_key']` | missed_gating_nuance |
| **Cloudflare** | `api.exists` | `False` | `True` | missed_gating_nuance |
| **Cloudflare** | `mcp.status` | `none` | `official` | missed_gating_nuance |
| **Cloudflare** | `verdict` | `blocked` | `ready_now` | missed_gating_nuance |
| **Cloudflare** | `main_blocker` | `no_public_api` | `none` | missed_gating_nuance |
| **MongoDB Atlas** | `auth_methods` | `['other']` | `['basic', 'hmac_signing']` | missed_gating_nuance |
| **MongoDB Atlas** | `credential_access` | `no_public_api` | `self_serve_free` | missed_gating_nuance |
| **MongoDB Atlas** | `api.exists` | `False` | `True` | missed_gating_nuance |
| **MongoDB Atlas** | `mcp.status` | `unknown` | `official` | missed_gating_nuance |
| **MongoDB Atlas** | `verdict` | `blocked` | `ready_with_caveats` | missed_gating_nuance |
| **MongoDB Atlas** | `main_blocker` | `other` | `complex_auth` | missed_gating_nuance |
| **Datadog** | `mcp.status` | `none` | `community` | missed_gating_nuance |
| **Datadog** | `verdict` | `ready_with_caveats` | `ready_now` | missed_gating_nuance |
| **Notion** | `auth_methods` | `['oauth2', 'bearer_token', 'api_key']` | `['bearer_token', 'oauth2']` | missed_gating_nuance |
| **Notion** | `mcp.status` | `none` | `official` | missed_gating_nuance |
| **Asana** | `mcp.status` | `none` | `community` | missed_gating_nuance |
| **Monday.com** | `auth_methods` | `['oauth2']` | `['bearer_token', 'oauth2']` | missed_gating_nuance |
| **Monday.com** | `mcp.status` | `official` | `community` | missed_gating_nuance |
| **QuickBooks** | `credential_access` | `self_serve_free` | `approval_required` | missed_gating_nuance |
| **QuickBooks** | `mcp.status` | `none` | `community` | missed_gating_nuance |
| **QuickBooks** | `main_blocker` | `none` | `app_review_or_approval` | missed_gating_nuance |
| **Brex** | `auth_methods` | `['none']` | `['bearer_token', 'oauth2']` | missed_gating_nuance |
| **Brex** | `credential_access` | `no_public_api` | `paid_plan_required` | missed_gating_nuance |
| **Brex** | `mcp.status` | `none` | `community` | missed_gating_nuance |
| **Brex** | `main_blocker` | `none` | `paid_plan` | missed_gating_nuance |
| **PitchBook** | `auth_methods` | `['none']` | `['api_key', 'bearer_token']` | missed_gating_nuance |
| **PitchBook** | `credential_access` | `no_public_api` | `partner_or_sales_gated` | missed_gating_nuance |
| **PitchBook** | `api.exists` | `False` | `True` | missed_gating_nuance |
| **PitchBook** | `verdict` | `blocked` | `needs_outreach` | missed_gating_nuance |
| **PitchBook** | `main_blocker` | `no_public_api` | `contact_sales` | missed_gating_nuance |
| **Mermaid CLI** | `api.exists` | `True` | `False` | hallucinated |
| **Mermaid CLI** | `mcp.status` | `none` | `community` | missed_gating_nuance |
| **Mermaid CLI** | `verdict` | `ready_now` | `not_an_api_product` | wrong_entity |
| **Mermaid CLI** | `main_blocker` | `none` | `not_a_hosted_service` | missed_gating_nuance |
| **Grain** | `auth_methods` | `['none']` | `['bearer_token', 'api_key']` | missed_gating_nuance |
| **Grain** | `credential_access` | `no_public_api` | `paid_plan_required` | missed_gating_nuance |
| **Grain** | `api.exists` | `False` | `True` | missed_gating_nuance |
| **Grain** | `verdict` | `blocked` | `ready_with_caveats` | missed_gating_nuance |
| **Grain** | `main_blocker` | `no_public_api` | `paid_plan` | missed_gating_nuance |

## Version V3 Misses (91 total discrepancies)

| App | Field | Agent Said | Ground Truth | Error Taxonomy Cause |
|---|---|---|---|---|
| **Twenty** | `auth_methods` | `['bearer_token']` | `['bearer_token', 'api_key']` | missed_gating_nuance |
| **Twenty** | `mcp.status` | `none` | `community` | missed_gating_nuance |
| **DealCloud** | `auth_methods` | `['oauth2', 'bearer_token', 'api_key']` | `['oauth2']` | missed_gating_nuance |
| **DealCloud** | `main_blocker` | `none` | `contact_sales` | missed_gating_nuance |
| **Front** | `auth_methods` | `['oauth2', 'bearer_token', 'api_key', 'basic']` | `['bearer_token', 'oauth2']` | missed_gating_nuance |
| **Front** | `credential_access` | `self_serve_free` | `self_serve_trial` | missed_gating_nuance |
| **Front** | `mcp.status` | `official` | `none` | missed_gating_nuance |
| **Gladly** | `auth_methods` | `['basic', 'jwt', 'hmac_signing']` | `['basic']` | missed_gating_nuance |
| **Gladly** | `credential_access` | `no_public_api` | `partner_or_sales_gated` | missed_gating_nuance |
| **Gladly** | `verdict` | `ready_with_caveats` | `needs_outreach` | missed_gating_nuance |
| **Gladly** | `main_blocker` | `none` | `contact_sales` | missed_gating_nuance |
| **Lark (Larksuite)** | `auth_methods` | `['oauth2']` | `['bearer_token', 'oauth2']` | missed_gating_nuance |
| **Lark (Larksuite)** | `mcp.status` | `official` | `none` | missed_gating_nuance |
| **Pumble** | `auth_methods` | `['api_key']` | `['oauth2', 'bearer_token']` | missed_gating_nuance |
| **Pumble** | `credential_access` | `self_serve_trial` | `paid_plan_required` | missed_gating_nuance |
| **Pumble** | `verdict` | `ready_now` | `ready_with_caveats` | over_generous_verdict |
| **Pumble** | `main_blocker` | `none` | `paid_plan` | missed_gating_nuance |
| **WhatsApp Business** | `auth_methods` | `['none']` | `['bearer_token', 'oauth2']` | missed_gating_nuance |
| **WhatsApp Business** | `credential_access` | `no_public_api` | `approval_required` | missed_gating_nuance |
| **WhatsApp Business** | `api.exists` | `False` | `True` | missed_gating_nuance |
| **WhatsApp Business** | `verdict` | `blocked` | `ready_with_caveats` | missed_gating_nuance |
| **WhatsApp Business** | `main_blocker` | `no_public_api` | `app_review_or_approval` | missed_gating_nuance |
| **Google Ads** | `auth_methods` | `['oauth2', 'jwt']` | `['oauth2']` | missed_gating_nuance |
| **Google Ads** | `mcp.status` | `community` | `none` | missed_gating_nuance |
| **GoHighLevel** | `auth_methods` | `['bearer_token', 'oauth2']` | `['oauth2', 'api_key', 'bearer_token']` | missed_gating_nuance |
| **GoHighLevel** | `credential_access` | `self_serve_trial` | `paid_plan_required` | missed_gating_nuance |
| **GoHighLevel** | `mcp.status` | `community` | `none` | missed_gating_nuance |
| **GoHighLevel** | `verdict` | `ready_now` | `ready_with_caveats` | over_generous_verdict |
| **GoHighLevel** | `main_blocker` | `none` | `paid_plan` | missed_gating_nuance |
| **systeme.io** | `auth_methods` | `['none']` | `['api_key']` | missed_gating_nuance |
| **systeme.io** | `credential_access` | `no_public_api` | `self_serve_free` | missed_gating_nuance |
| **systeme.io** | `api.exists` | `False` | `True` | missed_gating_nuance |
| **systeme.io** | `verdict` | `blocked` | `ready_now` | missed_gating_nuance |
| **systeme.io** | `main_blocker` | `no_public_api` | `none` | missed_gating_nuance |
| **Salesforce Commerce Cloud** | `auth_methods` | `['none']` | `['oauth2', 'bearer_token']` | missed_gating_nuance |
| **Amazon Selling Partner** | `auth_methods` | `['other']` | `['oauth2', 'aws_sigv4']` | missed_gating_nuance |
| **Amazon Selling Partner** | `mcp.status` | `none` | `community` | missed_gating_nuance |
| **Amazon Selling Partner** | `verdict` | `blocked` | `ready_with_caveats` | missed_gating_nuance |
| **Amazon Selling Partner** | `main_blocker` | `app_review_or_approval` | `complex_auth` | missed_gating_nuance |
| **fanbasis** | `api.exists` | `True` | `False` | hallucinated |
| **fanbasis** | `mcp.status` | `official` | `none` | missed_gating_nuance |
| **fanbasis** | `verdict` | `ready_with_caveats` | `blocked` | missed_gating_nuance |
| **fanbasis** | `main_blocker` | `none` | `no_public_api` | missed_gating_nuance |
| **Firecrawl** | `auth_methods` | `['none']` | `['bearer_token', 'api_key']` | missed_gating_nuance |
| **Firecrawl** | `credential_access` | `no_public_api` | `self_serve_free` | missed_gating_nuance |
| **Firecrawl** | `api.exists` | `False` | `True` | missed_gating_nuance |
| **Firecrawl** | `mcp.status` | `none` | `official` | missed_gating_nuance |
| **Firecrawl** | `verdict` | `blocked` | `ready_now` | missed_gating_nuance |
| **Firecrawl** | `main_blocker` | `no_public_api` | `none` | missed_gating_nuance |
| **Sherlock** | `credential_access` | `no_public_api` | `not_applicable` | missed_gating_nuance |
| **Waterfall.io** | `auth_methods` | `['none']` | `['api_key']` | missed_gating_nuance |
| **Waterfall.io** | `credential_access` | `no_public_api` | `partner_or_sales_gated` | missed_gating_nuance |
| **Waterfall.io** | `api.exists` | `False` | `True` | missed_gating_nuance |
| **Waterfall.io** | `verdict` | `blocked` | `needs_outreach` | missed_gating_nuance |
| **Waterfall.io** | `main_blocker` | `no_public_api` | `contact_sales` | missed_gating_nuance |
| **Cloudflare** | `auth_methods` | `['api_key']` | `['bearer_token', 'api_key']` | missed_gating_nuance |
| **Cloudflare** | `api.exists` | `False` | `True` | missed_gating_nuance |
| **Cloudflare** | `mcp.status` | `none` | `official` | missed_gating_nuance |
| **Cloudflare** | `verdict` | `blocked` | `ready_now` | missed_gating_nuance |
| **Cloudflare** | `main_blocker` | `no_public_api` | `none` | missed_gating_nuance |
| **MongoDB Atlas** | `auth_methods` | `['other']` | `['basic', 'hmac_signing']` | missed_gating_nuance |
| **MongoDB Atlas** | `credential_access` | `no_public_api` | `self_serve_free` | missed_gating_nuance |
| **MongoDB Atlas** | `api.exists` | `False` | `True` | missed_gating_nuance |
| **MongoDB Atlas** | `mcp.status` | `unknown` | `official` | missed_gating_nuance |
| **MongoDB Atlas** | `verdict` | `blocked` | `ready_with_caveats` | missed_gating_nuance |
| **MongoDB Atlas** | `main_blocker` | `other` | `complex_auth` | missed_gating_nuance |
| **Datadog** | `mcp.status` | `none` | `community` | missed_gating_nuance |
| **Datadog** | `verdict` | `ready_with_caveats` | `ready_now` | missed_gating_nuance |
| **Notion** | `auth_methods` | `['oauth2', 'bearer_token', 'api_key']` | `['bearer_token', 'oauth2']` | missed_gating_nuance |
| **Notion** | `mcp.status` | `none` | `official` | missed_gating_nuance |
| **Asana** | `mcp.status` | `none` | `community` | missed_gating_nuance |
| **Monday.com** | `auth_methods` | `['oauth2']` | `['bearer_token', 'oauth2']` | missed_gating_nuance |
| **Monday.com** | `mcp.status` | `official` | `community` | missed_gating_nuance |
| **QuickBooks** | `credential_access` | `self_serve_free` | `approval_required` | missed_gating_nuance |
| **QuickBooks** | `mcp.status` | `none` | `community` | missed_gating_nuance |
| **QuickBooks** | `main_blocker` | `none` | `app_review_or_approval` | missed_gating_nuance |
| **Brex** | `auth_methods` | `['none']` | `['bearer_token', 'oauth2']` | missed_gating_nuance |
| **Brex** | `credential_access` | `no_public_api` | `paid_plan_required` | missed_gating_nuance |
| **Brex** | `mcp.status` | `none` | `community` | missed_gating_nuance |
| **Brex** | `main_blocker` | `none` | `paid_plan` | missed_gating_nuance |
| **PitchBook** | `auth_methods` | `['none']` | `['api_key', 'bearer_token']` | missed_gating_nuance |
| **PitchBook** | `credential_access` | `no_public_api` | `partner_or_sales_gated` | missed_gating_nuance |
| **PitchBook** | `api.exists` | `False` | `True` | missed_gating_nuance |
| **PitchBook** | `verdict` | `blocked` | `needs_outreach` | missed_gating_nuance |
| **PitchBook** | `main_blocker` | `no_public_api` | `contact_sales` | missed_gating_nuance |
| **Mermaid CLI** | `mcp.status` | `none` | `community` | missed_gating_nuance |
| **Grain** | `auth_methods` | `['none']` | `['bearer_token', 'api_key']` | missed_gating_nuance |
| **Grain** | `credential_access` | `no_public_api` | `paid_plan_required` | missed_gating_nuance |
| **Grain** | `api.exists` | `False` | `True` | missed_gating_nuance |
| **Grain** | `verdict` | `blocked` | `ready_with_caveats` | missed_gating_nuance |
| **Grain** | `main_blocker` | `no_public_api` | `paid_plan` | missed_gating_nuance |

## Version V4 Misses (79 total discrepancies)

| App | Field | Agent Said | Ground Truth | Error Taxonomy Cause |
|---|---|---|---|---|
| **Twenty** | `auth_methods` | `['bearer_token']` | `['bearer_token', 'api_key']` | missed_gating_nuance |
| **Twenty** | `mcp.status` | `none` | `community` | missed_gating_nuance |
| **DealCloud** | `auth_methods` | `['api_key', 'bearer_token', 'oauth2']` | `['oauth2']` | missed_gating_nuance |
| **Front** | `auth_methods` | `['api_key', 'basic', 'bearer_token', 'oauth2']` | `['bearer_token', 'oauth2']` | missed_gating_nuance |
| **Front** | `credential_access` | `self_serve_free` | `self_serve_trial` | missed_gating_nuance |
| **Front** | `mcp.status` | `official` | `none` | missed_gating_nuance |
| **Gladly** | `auth_methods` | `['basic', 'hmac_signing', 'jwt']` | `['basic']` | missed_gating_nuance |
| **Gladly** | `credential_access` | `no_public_api` | `partner_or_sales_gated` | missed_gating_nuance |
| **Gladly** | `verdict` | `ready_with_caveats` | `needs_outreach` | missed_gating_nuance |
| **Gladly** | `main_blocker` | `none` | `contact_sales` | missed_gating_nuance |
| **Lark (Larksuite)** | `auth_methods` | `['oauth2']` | `['bearer_token', 'oauth2']` | missed_gating_nuance |
| **Lark (Larksuite)** | `mcp.status` | `official` | `none` | missed_gating_nuance |
| **Pumble** | `auth_methods` | `['api_key']` | `['oauth2', 'bearer_token']` | missed_gating_nuance |
| **WhatsApp Business** | `auth_methods` | `['none']` | `['bearer_token', 'oauth2']` | missed_gating_nuance |
| **WhatsApp Business** | `credential_access` | `no_public_api` | `approval_required` | missed_gating_nuance |
| **WhatsApp Business** | `api.exists` | `False` | `True` | missed_gating_nuance |
| **WhatsApp Business** | `verdict` | `blocked` | `ready_with_caveats` | missed_gating_nuance |
| **WhatsApp Business** | `main_blocker` | `no_public_api` | `app_review_or_approval` | missed_gating_nuance |
| **Google Ads** | `auth_methods` | `['jwt', 'oauth2']` | `['oauth2']` | missed_gating_nuance |
| **Google Ads** | `mcp.status` | `community` | `none` | missed_gating_nuance |
| **GoHighLevel** | `mcp.status` | `community` | `none` | missed_gating_nuance |
| **systeme.io** | `auth_methods` | `['none']` | `['api_key']` | missed_gating_nuance |
| **systeme.io** | `credential_access` | `no_public_api` | `self_serve_free` | missed_gating_nuance |
| **systeme.io** | `api.exists` | `False` | `True` | missed_gating_nuance |
| **systeme.io** | `verdict` | `blocked` | `ready_now` | missed_gating_nuance |
| **systeme.io** | `main_blocker` | `no_public_api` | `none` | missed_gating_nuance |
| **Salesforce Commerce Cloud** | `auth_methods` | `['none']` | `['oauth2', 'bearer_token']` | missed_gating_nuance |
| **Amazon Selling Partner** | `auth_methods` | `['other']` | `['oauth2', 'aws_sigv4']` | missed_gating_nuance |
| **Amazon Selling Partner** | `mcp.status` | `none` | `community` | missed_gating_nuance |
| **Amazon Selling Partner** | `main_blocker` | `app_review_or_approval` | `complex_auth` | missed_gating_nuance |
| **fanbasis** | `api.exists` | `True` | `False` | hallucinated |
| **fanbasis** | `mcp.status` | `official` | `none` | missed_gating_nuance |
| **fanbasis** | `verdict` | `ready_with_caveats` | `blocked` | missed_gating_nuance |
| **fanbasis** | `main_blocker` | `none` | `no_public_api` | missed_gating_nuance |
| **Firecrawl** | `auth_methods` | `['none']` | `['bearer_token', 'api_key']` | missed_gating_nuance |
| **Firecrawl** | `credential_access` | `no_public_api` | `self_serve_free` | missed_gating_nuance |
| **Firecrawl** | `api.exists` | `False` | `True` | missed_gating_nuance |
| **Firecrawl** | `mcp.status` | `none` | `official` | missed_gating_nuance |
| **Firecrawl** | `verdict` | `blocked` | `ready_now` | missed_gating_nuance |
| **Firecrawl** | `main_blocker` | `no_public_api` | `none` | missed_gating_nuance |
| **Waterfall.io** | `auth_methods` | `['none']` | `['api_key']` | missed_gating_nuance |
| **Waterfall.io** | `credential_access` | `no_public_api` | `partner_or_sales_gated` | missed_gating_nuance |
| **Waterfall.io** | `api.exists` | `False` | `True` | missed_gating_nuance |
| **Waterfall.io** | `verdict` | `blocked` | `needs_outreach` | missed_gating_nuance |
| **Waterfall.io** | `main_blocker` | `no_public_api` | `contact_sales` | missed_gating_nuance |
| **Cloudflare** | `auth_methods` | `['api_key']` | `['bearer_token', 'api_key']` | missed_gating_nuance |
| **Cloudflare** | `credential_access` | `no_public_api` | `self_serve_free` | missed_gating_nuance |
| **Cloudflare** | `api.exists` | `False` | `True` | missed_gating_nuance |
| **Cloudflare** | `mcp.status` | `none` | `official` | missed_gating_nuance |
| **Cloudflare** | `verdict` | `blocked` | `ready_now` | missed_gating_nuance |
| **Cloudflare** | `main_blocker` | `no_public_api` | `none` | missed_gating_nuance |
| **MongoDB Atlas** | `auth_methods` | `['other']` | `['basic', 'hmac_signing']` | missed_gating_nuance |
| **MongoDB Atlas** | `credential_access` | `no_public_api` | `self_serve_free` | missed_gating_nuance |
| **MongoDB Atlas** | `api.exists` | `False` | `True` | missed_gating_nuance |
| **MongoDB Atlas** | `mcp.status` | `unknown` | `official` | missed_gating_nuance |
| **MongoDB Atlas** | `verdict` | `blocked` | `ready_with_caveats` | missed_gating_nuance |
| **MongoDB Atlas** | `main_blocker` | `no_public_api` | `complex_auth` | missed_gating_nuance |
| **Datadog** | `mcp.status` | `none` | `community` | missed_gating_nuance |
| **Datadog** | `verdict` | `ready_with_caveats` | `ready_now` | missed_gating_nuance |
| **Notion** | `auth_methods` | `['api_key', 'bearer_token', 'oauth2']` | `['bearer_token', 'oauth2']` | missed_gating_nuance |
| **Notion** | `mcp.status` | `none` | `official` | missed_gating_nuance |
| **Asana** | `auth_methods` | `['api_key', 'bearer_token', 'oauth2']` | `['bearer_token', 'oauth2']` | missed_gating_nuance |
| **Asana** | `mcp.status` | `none` | `community` | missed_gating_nuance |
| **Monday.com** | `auth_methods` | `['oauth2']` | `['bearer_token', 'oauth2']` | missed_gating_nuance |
| **Monday.com** | `mcp.status` | `official` | `community` | missed_gating_nuance |
| **QuickBooks** | `mcp.status` | `none` | `community` | missed_gating_nuance |
| **Brex** | `auth_methods` | `['none']` | `['bearer_token', 'oauth2']` | missed_gating_nuance |
| **Brex** | `mcp.status` | `none` | `community` | missed_gating_nuance |
| **PitchBook** | `auth_methods` | `['none']` | `['api_key', 'bearer_token']` | missed_gating_nuance |
| **PitchBook** | `credential_access` | `no_public_api` | `partner_or_sales_gated` | missed_gating_nuance |
| **PitchBook** | `api.exists` | `False` | `True` | missed_gating_nuance |
| **PitchBook** | `verdict` | `blocked` | `needs_outreach` | missed_gating_nuance |
| **PitchBook** | `main_blocker` | `no_public_api` | `contact_sales` | missed_gating_nuance |
| **Mermaid CLI** | `mcp.status` | `none` | `community` | missed_gating_nuance |
| **Grain** | `auth_methods` | `['none']` | `['bearer_token', 'api_key']` | missed_gating_nuance |
| **Grain** | `credential_access` | `no_public_api` | `paid_plan_required` | missed_gating_nuance |
| **Grain** | `api.exists` | `False` | `True` | missed_gating_nuance |
| **Grain** | `verdict` | `blocked` | `ready_with_caveats` | missed_gating_nuance |
| **Grain** | `main_blocker` | `no_public_api` | `paid_plan` | missed_gating_nuance |


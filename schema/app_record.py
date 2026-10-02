from __future__ import annotations
from enum import Enum
from typing import List, Optional, Dict
from pydantic import BaseModel, Field, HttpUrl, field_validator

class AuthMethodEnum(str, Enum):
    OAUTH2 = "oauth2"
    API_KEY = "api_key"
    BEARER_TOKEN = "bearer_token"
    BASIC = "basic"
    JWT = "jwt"
    HMAC_SIGNING = "hmac_signing"
    AWS_SIGV4 = "aws_sigv4"
    NONE = "none"
    OTHER = "other"

class CredentialAccessEnum(str, Enum):
    SELF_SERVE_FREE = "self_serve_free"
    SELF_SERVE_TRIAL = "self_serve_trial"
    PAID_PLAN_REQUIRED = "paid_plan_required"
    APPROVAL_REQUIRED = "approval_required"
    PARTNER_OR_SALES_GATED = "partner_or_sales_gated"
    NO_PUBLIC_API = "no_public_api"
    NOT_APPLICABLE = "not_applicable"

class ApiStyleEnum(str, Enum):
    REST = "rest"
    GRAPHQL = "graphql"
    SOAP = "soap"
    GRPC = "grpc"
    SDK_ONLY = "sdk_only"
    CLI = "cli"

class ApiBreadthEnum(str, Enum):
    BROAD = "broad"
    MODERATE = "moderate"
    NARROW = "narrow"
    NONE = "none"

class McpStatusEnum(str, Enum):
    OFFICIAL = "official"
    COMMUNITY = "community"
    NONE = "none"
    UNKNOWN = "unknown"

class BuildFormEnum(str, Enum):
    API_TOOLKIT = "api_toolkit"
    REUSE_EXISTING_MCP = "reuse_existing_mcp"
    CLI_SKILL = "cli_skill"
    NOT_BUILDABLE = "not_buildable"

class VerdictEnum(str, Enum):
    READY_NOW = "ready_now"
    READY_WITH_CAVEATS = "ready_with_caveats"
    NEEDS_OUTREACH = "needs_outreach"
    BLOCKED = "blocked"
    NOT_AN_API_PRODUCT = "not_an_api_product"

class MainBlockerEnum(str, Enum):
    NONE = "none"
    NO_PUBLIC_API = "no_public_api"
    PAID_PLAN = "paid_plan"
    APP_REVIEW_OR_APPROVAL = "app_review_or_approval"
    PARTNER_PROGRAM = "partner_program"
    CONTACT_SALES = "contact_sales"
    COMPLEX_AUTH = "complex_auth"
    DOCS_UNCLEAR = "docs_unclear"
    NOT_A_HOSTED_SERVICE = "not_a_hosted_service"
    OTHER = "other"

class ConfidenceEnum(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class ApiSpec(BaseModel):
    exists: bool = Field(description="Whether a public/usable API exists for the product")
    styles: List[ApiStyleEnum] = Field(default_factory=list, description="Architectural styles supported by API")
    breadth: ApiBreadthEnum = Field(default=ApiBreadthEnum.NONE, description="Functional breadth of endpoints")
    docs_url: Optional[str] = Field(default=None, description="Primary developer / API reference documentation URL")
    openapi_url: Optional[str] = Field(default=None, description="Direct URL to OpenAPI / Swagger / schema file if found")

class McpSpec(BaseModel):
    status: McpStatusEnum = Field(description="MCP server availability status")
    url: Optional[str] = Field(default=None, description="Repository or registry URL of the MCP server")

class ExtrasSpec(BaseModel):
    webhooks: Optional[bool] = Field(default=None, description="Whether outbound webhooks or event subscriptions exist")
    sandbox_or_test_env: Optional[bool] = Field(default=None, description="Whether sandbox, mock or test credentials exist")
    rate_limit_note: Optional[str] = Field(default=None, description="Overview of rate limits (e.g. 10 req/sec, tiered)")
    official_sdks: List[str] = Field(default_factory=list, description="List of official SDK languages (e.g. python, node)")
    composio_toolkit_exists: Optional[bool] = Field(default=None, description="Whether Composio already supports this app")
    composio_auth_schemes: List[str] = Field(default_factory=list, description="Auth schemes supported in Composio catalog")

class EvidenceItem(BaseModel):
    field: str = Field(description="Schema field name this evidence supports")
    url: str = Field(description="Exact URL where evidence was fetched")
    quote: str = Field(max_length=300, description="Verbatim quote (<=300 chars) from the fetched page")
    retrieved_at: str = Field(description="ISO timestamp of when the page was retrieved")
    quote_verified: bool = Field(default=False, description="Deterministic check verifying quote is literally in cached content")

class ProvenanceSpec(BaseModel):
    run_id: str = Field(description="Identifier for execution run (e.g. v1_naive, v2_grounded, v3_verified)")
    model: str = Field(description="Model identifier used for extraction")
    prompt_version: str = Field(description="Prompt template version tag")
    timestamp: str = Field(description="ISO timestamp of record creation")

class AppRecord(BaseModel):
    id: int = Field(ge=1, le=100, description="App ID from Appendix A (1-100)")
    app: str = Field(description="Official name of the application")
    category: str = Field(description="Standard category from Appendix A")
    one_liner: str = Field(description="Concise description of the product and its primary function")
    official_domain: str = Field(description="Primary verified domain (e.g. salesforce.com)")

    auth_methods: List[AuthMethodEnum] = Field(default_factory=list, description="Supported API authentication methods")
    auth_notes: Optional[str] = Field(default=None, description="Specific auth details (e.g. PKCE, custom headers)")

    credential_access: CredentialAccessEnum = Field(description="Accessibility tier for obtaining API credentials")
    gate_notes: Optional[str] = Field(default=None, description="Gating specifics (e.g. developer plan required, manual review)")

    api: ApiSpec = Field(description="API presence, styles, and documentation links")
    mcp: McpSpec = Field(description="Model Context Protocol server status")

    build_form: BuildFormEnum = Field(description="Target format for composio integration")
    verdict: VerdictEnum = Field(description="Overall buildability status verdict")
    main_blocker: MainBlockerEnum = Field(default=MainBlockerEnum.NONE, description="Primary blocker if not ready_now")
    verdict_reason: str = Field(max_length=400, description="Concise rationale for verdict (<=2 sentences)")

    extras: ExtrasSpec = Field(default_factory=ExtrasSpec, description="Additional technical capabilities")
    evidence: List[EvidenceItem] = Field(default_factory=list, description="Grounding citations and verbatim quotes")
    confidence: Dict[str, ConfidenceEnum] = Field(default_factory=dict, description="Confidence per Key Field")
    needs_human: bool = Field(default=False, description="Flagged for manual human review or ambiguous findings")
    provenance: ProvenanceSpec = Field(description="Metadata tracing model, prompt, and execution run")

    @field_validator("verdict")
    def validate_verdict_consistency(cls, v, info):
        # Additional validation can be applied during strict scoring
        return v

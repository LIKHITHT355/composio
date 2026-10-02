import json
import pytest
from pathlib import Path
from jsonschema import validate
from schema.app_record import (
    AppRecord,
    AuthMethodEnum,
    CredentialAccessEnum,
    ApiStyleEnum,
    ApiBreadthEnum,
    McpStatusEnum,
    BuildFormEnum,
    VerdictEnum,
    MainBlockerEnum,
    ConfidenceEnum,
    ApiSpec,
    McpSpec,
    ExtrasSpec,
    EvidenceItem,
    ProvenanceSpec
)

@pytest.fixture
def json_schema():
    schema_path = Path("schema/app_record.schema.json")
    assert schema_path.exists()
    with open(schema_path, "r", encoding="utf-8") as f:
        return json.load(f)

def test_handmade_example_validates(json_schema):
    """Phase 1 GATE: schema validates a hand-made example (Stripe)."""
    stripe_record = AppRecord(
        id=81,
        app="Stripe",
        category="Finance and Fintech",
        one_liner="Financial infrastructure and payment processing API for online commerce.",
        official_domain="stripe.com",
        auth_methods=[AuthMethodEnum.API_KEY, AuthMethodEnum.BEARER_TOKEN],
        auth_notes="API keys provided as Bearer tokens in Authorization header (sk_test/sk_live).",
        credential_access=CredentialAccessEnum.SELF_SERVE_FREE,
        gate_notes="Instant test account signup with full access to test mode API keys.",
        api=ApiSpec(
            exists=True,
            styles=[ApiStyleEnum.REST],
            breadth=ApiBreadthEnum.BROAD,
            docs_url="https://stripe.com/docs/api",
            openapi_url="https://raw.githubusercontent.com/stripe/openapi/master/openapi/spec3.json"
        ),
        mcp=McpSpec(
            status=McpStatusEnum.OFFICIAL,
            url="https://github.com/stripe/agent-toolkit"
        ),
        build_form=BuildFormEnum.API_TOOLKIT,
        verdict=VerdictEnum.READY_NOW,
        main_blocker=MainBlockerEnum.NONE,
        verdict_reason="Comprehensive self-serve REST API with instant test keys and broad endpoint coverage.",
        extras=ExtrasSpec(
            webhooks=True,
            sandbox_or_test_env=True,
            rate_limit_note="Default 100 read / 100 write requests per second in live mode.",
            official_sdks=["python", "node", "ruby", "go", "java", "php", "dotnet"],
            composio_toolkit_exists=True,
            composio_auth_schemes=["api_key", "oauth2"]
        ),
        evidence=[
            EvidenceItem(
                field="credential_access",
                url="https://stripe.com/docs/api",
                quote="You can use Stripe in test mode without activating your account or providing banking information.",
                retrieved_at="2026-10-02T16:00:00Z",
                quote_verified=True
            )
        ],
        confidence={
            "auth_methods": ConfidenceEnum.HIGH,
            "credential_access": ConfidenceEnum.HIGH,
            "api.exists": ConfidenceEnum.HIGH,
            "mcp.status": ConfidenceEnum.HIGH,
            "verdict": ConfidenceEnum.HIGH,
            "main_blocker": ConfidenceEnum.HIGH
        },
        needs_human=False,
        provenance=ProvenanceSpec(
            run_id="phase1_test",
            model="manual_gold",
            prompt_version="v1.0",
            timestamp="2026-10-02T16:00:00Z"
        )
    )

    data = stripe_record.model_dump(mode="json")
    validate(instance=data, schema=json_schema)
    assert data["app"] == "Stripe"
    assert data["verdict"] == "ready_now"

def test_sherlock_cli_example(json_schema):
    """Test local CLI OSS tool mapping."""
    sherlock_record = AppRecord(
        id=58,
        app="Sherlock",
        category="Data, SEO and Scraping",
        one_liner="OSINT tool to hunt down social media accounts by username across social networks.",
        official_domain="github.com/sherlock-project/sherlock",
        auth_methods=[AuthMethodEnum.NONE],
        credential_access=CredentialAccessEnum.NOT_APPLICABLE,
        api=ApiSpec(
            exists=False,
            styles=[ApiStyleEnum.CLI],
            breadth=ApiBreadthEnum.NONE,
            docs_url="https://github.com/sherlock-project/sherlock#readme"
        ),
        mcp=McpSpec(
            status=McpStatusEnum.COMMUNITY,
            url="https://github.com/community/sherlock-mcp"
        ),
        build_form=BuildFormEnum.CLI_SKILL,
        verdict=VerdictEnum.NOT_AN_API_PRODUCT,
        main_blocker=MainBlockerEnum.NOT_A_HOSTED_SERVICE,
        verdict_reason="Open-source Python CLI tool with no cloud hosted API platform.",
        provenance=ProvenanceSpec(
            run_id="phase1_test",
            model="manual_gold",
            prompt_version="v1.0",
            timestamp="2026-10-02T16:00:00Z"
        )
    )
    data = sherlock_record.model_dump(mode="json")
    validate(instance=data, schema=json_schema)
    assert data["verdict"] == "not_an_api_product"
    assert data["main_blocker"] == "not_a_hosted_service"

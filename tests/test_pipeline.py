import pytest
import json
from pathlib import Path

from schema.app_record import AppRecord
from agent.resolver import EntityResolver
from agent.fetcher import PageFetcher

def test_resolver_disambiguation():
    resolved_front = EntityResolver.resolve("Front", "Support and Helpdesk", "front.com")
    assert resolved_front["official_domain"] == "front.com"
    assert "collaborative email" in resolved_front["one_liner"]

    resolved_sherlock = EntityResolver.resolve("Sherlock", "Developer", "github.com/sherlock-project/sherlock")
    assert "github.com" in resolved_sherlock["official_domain"]
    assert "command-line" in resolved_sherlock["one_liner"]

def test_quote_verifier():
    fetcher = PageFetcher()
    test_url = "https://example.com/test-docs"
    cache_path = fetcher._get_cache_path(test_url)
    
    mock_data = {
        "url": test_url,
        "status_code": 200,
        "title": "Test Title",
        "clean_text": "OAuth 2.0 is the industry-standard protocol for authorization.",
        "sha256": "abc123hash",
        "retrieved_at": "2026-10-02T12:00:00Z"
    }
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(mock_data, f)

    assert fetcher.verify_quote(test_url, "OAuth 2.0 is the industry-standard protocol") is True
    assert fetcher.verify_quote(test_url, "Nonexistent text in document") is False

def test_final_dataset_schema_valid():
    final_path = Path("data/final/apps.json")
    assert final_path.exists()
    
    with open(final_path, "r", encoding="utf-8") as f:
        apps = json.load(f)

    assert len(apps) == 100
    for app in apps:
        record = AppRecord.model_validate(app)
        assert record.id >= 1 and record.id <= 100
        assert record.app
        assert record.official_domain
        assert record.verdict

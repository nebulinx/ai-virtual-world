"""Tests to ensure news and direction data match frontend contract so tabs display correctly."""

import json
from pathlib import Path

import pytest

# Paths relative to repo root
REPO_ROOT = Path(__file__).resolve().parent.parent
NEWS_JSON = REPO_ROOT / "backend" / "data" / "news.json"
DIRECTION_JSON = REPO_ROOT / "backend" / "data" / "direction.json"


def _news_data_ok_for_display(data: dict) -> bool:
    """Check news data has the shape NewsFeed.update() and render() expect."""
    if not data or "latest" not in data:
        return False
    latest = data["latest"]
    if not isinstance(latest, list):
        return False
    for item in latest:
        if not isinstance(item, dict):
            return False
        # Frontend uses: item.headline, item.body, item.timestamp (optional but shown)
        if "headline" not in item or "body" not in item:
            return False
    return True


def _direction_data_ok_for_display(data: dict) -> bool:
    """Check direction data has the shape DirectionPanel.update() and render() expect."""
    if not data:
        return False
    # Frontend expects: data.latest (object or null), data.history (array)
    if "history" not in data or not isinstance(data["history"], list):
        return False
    latest = data.get("latest")
    if latest is not None:
        if not isinstance(latest, dict):
            return False
        # Frontend uses: latest.challenge, latest.plan, latest.summary, latest.implementation_hint, latest.timestamp
        if "challenge" not in latest:
            return False
    return True


class TestNewsPanelContract:
    """News tab displays when data has latest[].headline, body, timestamp."""

    def test_news_empty_latest_is_valid(self):
        data = {"latest": []}
        assert _news_data_ok_for_display(data) is True

    def test_news_with_items_has_required_fields(self):
        data = {
            "latest": [
                {
                    "timestamp": "2026-03-08T12:00:00",
                    "headline": "Test headline",
                    "body": "Test body",
                    "category": "entity",
                }
            ]
        }
        assert _news_data_ok_for_display(data) is True

    def test_news_missing_headline_fails_display_contract(self):
        data = {"latest": [{"body": "Only body", "timestamp": "2026-03-08T12:00:00", "category": "entity"}]}
        assert _news_data_ok_for_display(data) is False

    def test_news_json_file_valid_if_present(self):
        if not NEWS_JSON.exists():
            pytest.skip("news.json not present")
        with open(NEWS_JSON) as f:
            data = json.load(f)
        assert _news_data_ok_for_display(data) is True, "news.json must have latest[].headline, body for News tab to display"


class TestDirectionPanelContract:
    """Direction tab displays when data has latest (with challenge) and history."""

    def test_direction_empty_history_valid(self):
        data = {"latest": None, "history": []}
        assert _direction_data_ok_for_display(data) is True

    def test_direction_with_latest_has_challenge(self):
        data = {
            "latest": {
                "timestamp": "2026-03-08T12:00:00+00:00",
                "challenge": "A challenge",
                "plan": "A plan",
                "implementation_hint": "entity",
                "summary": "A summary",
            },
            "history": [],
        }
        assert _direction_data_ok_for_display(data) is True

    def test_direction_missing_challenge_fails_contract(self):
        data = {"latest": {"plan": "Only plan", "implementation_hint": "entity"}, "history": []}
        assert _direction_data_ok_for_display(data) is False

    def test_direction_json_file_valid_if_present(self):
        if not DIRECTION_JSON.exists():
            pytest.skip("direction.json not present")
        with open(DIRECTION_JSON) as f:
            data = json.load(f)
        assert _direction_data_ok_for_display(data) is True, "direction.json must have latest.challenge, history for Direction tab to display"

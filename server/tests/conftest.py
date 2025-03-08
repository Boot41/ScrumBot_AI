import pytest
from unittest.mock import MagicMock
from datetime import datetime

@pytest.fixture
def mock_jira():
    mock = MagicMock()
    mock.auth = ('test@email.com', 'test-api-key')
    mock.server_url = 'https://test-jira.com'
    mock.headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    return mock

@pytest.fixture
def mock_response():
    mock = MagicMock()
    mock.status_code = 200
    mock.json.return_value = {
        "key": "TEST-1",
        "fields": {
            "summary": "Test Issue",
            "description": "Test Description",
            "status": {"name": "To Do"},
            "assignee": {"displayName": "Test User", "accountId": "test-user"},
            "project": {"key": "TEST"},
            "customfield_10020": [{"id": 1, "name": "Sprint 1"}]
        }
    }
    return mock

@pytest.fixture
def mock_issue():
    return {
        "key": "TEST-1",
        "fields": {
            "summary": "Test Issue",
            "description": "Test Description",
            "status": {"name": "To Do"},
            "assignee": {"displayName": "Test User", "accountId": "test-user"},
            "project": {"key": "TEST"},
            "customfield_10020": [{"id": 1, "name": "Sprint 1"}],
            "labels": ["test"]
        }
    }

@pytest.fixture
def mock_transitions():
    return {
        "transitions": [
            {"id": "1", "name": "To Do"},
            {"id": "2", "name": "In Progress"},
            {"id": "3", "name": "Done"},
            {"id": "4", "name": "Blocked"}
        ]
    }

@pytest.fixture
def mock_datetime(monkeypatch):
    mock_now = datetime(2025, 3, 5, 14, 27, 5)
    class MockDatetime:
        @classmethod
        def now(cls):
            return mock_now
    monkeypatch.setattr("talking_bot.datetime", MockDatetime)

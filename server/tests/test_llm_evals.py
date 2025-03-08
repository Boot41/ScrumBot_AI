import pytest
from unittest.mock import patch, MagicMock
from talking_bot import ScrumBot, JiraAPI

@pytest.fixture
def mock_jira():
    mock = MagicMock(spec=JiraAPI)
    mock.get_issue_details.return_value = {
        "key": "SCRUM-123",
        "fields": {
            "summary": "Test Issue",
            "description": "Test Description",
            "status": {"name": "In Progress"},
            "assignee": {"displayName": "Test User"}
        }
    }
    mock.get_project_key = MagicMock(return_value="SCRUM")
    return mock

@pytest.fixture
def scrum_bot(mock_jira):
    bot = ScrumBot(jira=mock_jira)
    bot.current_state = "greeting"
    bot.conversation_history = []
    return bot

def test_basic_conversation(scrum_bot):
    # Test greeting
    response = scrum_bot.process_response("hi")
    assert isinstance(response, dict)
    assert "message" in response
    assert "speech_segments" in response
    assert len(response["message"]) > 0

    # Test yesterday's work
    response = scrum_bot.process_response("I worked on SCRUM-123")
    assert isinstance(response, dict)
    assert "message" in response
    assert "speech_segments" in response
    assert len(response["message"]) > 0

    # Test today's work
    response = scrum_bot.process_response("Working on the login page")
    assert isinstance(response, dict)
    assert "message" in response
    assert "speech_segments" in response
    assert len(response["message"]) > 0

    # Test no blockers
    response = scrum_bot.process_response("no blockers")
    assert isinstance(response, dict)
    assert "message" in response
    assert "speech_segments" in response
    assert len(response["message"]) > 0

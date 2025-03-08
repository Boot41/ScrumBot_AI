import pytest
import responses
from unittest.mock import patch, MagicMock
from talking_bot import JiraAPI

@pytest.fixture
def mock_response():
    return MagicMock(status=200, json=MagicMock(return_value={"key": "TEST-1"}))

@pytest.fixture
def jira_api():
    return JiraAPI('test@email.com', 'test-api-key', 'https://test-jira.com')

@responses.activate
def test_get_issue_details(jira_api):
    # Test successful issue details
    mock_issue = {
        "key": "SCRUM-1",
        "fields": {
            "summary": "Test Issue",
            "status": {"name": "In Progress"},
            "description": "Test Description",
            "assignee": {"displayName": "Test User"}
        }
    }
    responses.add(
        responses.GET,
        f"{jira_api.server_url}/rest/api/3/issue/SCRUM-1",
        json=mock_issue,
        status=200
    )
    
    result = jira_api.get_issue_details('SCRUM-1')
    assert result["key"] == "SCRUM-1"
    assert result["fields"]["summary"] == "Test Issue"
    assert result["fields"]["status"]["name"] == "In Progress"
    assert result["fields"]["description"] == "Test Description"
    assert result["fields"]["assignee"]["displayName"] == "Test User"

@responses.activate
def test_get_issue_details_error(jira_api):
    # Test issue not found
    responses.add(
        responses.GET,
        f"{jira_api.server_url}/rest/api/3/issue/SCRUM-1",
        status=404
    )
    result = jira_api.get_issue_details('SCRUM-1')
    assert result is None
    
    # Test server error
    responses.reset()
    responses.add(
        responses.GET,
        f"{jira_api.server_url}/rest/api/3/issue/SCRUM-1",
        status=500
    )
    result = jira_api.get_issue_details('SCRUM-1')
    assert result is None

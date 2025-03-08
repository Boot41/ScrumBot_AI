import pytest
from unittest.mock import patch, MagicMock
from talking_bot import ScrumBot, ScrumStatus

@pytest.fixture
def mock_jira():
    jira_mock = MagicMock()
    jira_mock.get_todo_tasks = MagicMock(return_value=[("SCRUM-1", "Test Task")])
    jira_mock.update_issue_status = MagicMock(return_value=True)
    jira_mock.create_blocker = MagicMock(return_value=(True, "SCRUM-2"))
    return jira_mock

@pytest.fixture
def scrum_bot(mock_jira):
    bot = ScrumBot(mock_jira)
    return bot

def test_start_conversation(scrum_bot):
    response = scrum_bot.start_conversation()
    assert isinstance(response, dict)
    assert "message" in response
    assert "speech_segments" in response
    assert "Hi" in response["message"]
    assert "SCRUM-1" in response["message"]
    assert scrum_bot.current_state == "greeting"

def test_extract_jira_key_valid(scrum_bot):
    # Test with valid JIRA key
    text = "Working on SCRUM-123 today"
    key = scrum_bot.extract_jira_key(text)
    assert key == "SCRUM-123"
    
    # Test with no JIRA key
    assert scrum_bot.extract_jira_key("No issue key here") is None
    
    # Test with number words
    assert scrum_bot.extract_jira_key("Working on SCRUM twenty three") == "SCRUM-23"
    
    # Test with compound numbers
    assert scrum_bot.extract_jira_key("working on scrum thirty five") == "SCRUM-35"

def test_determine_status_done(scrum_bot):
    # Test all status types
    assert scrum_bot.determine_status("completed the task") == ScrumStatus.DONE
    assert scrum_bot.determine_status("finished working") == ScrumStatus.DONE
    assert scrum_bot.determine_status("working on") == ScrumStatus.IN_PROGRESS
    assert scrum_bot.determine_status("started") == ScrumStatus.IN_PROGRESS
    assert scrum_bot.determine_status("continuing") == ScrumStatus.IN_PROGRESS
    assert scrum_bot.determine_status("will do") == ScrumStatus.TODO





def test_process_response_blockers_no(scrum_bot):
    # Test with no blockers
    scrum_bot.current_state = "blockers"
    response = scrum_bot.process_response("no")
    assert "create" in response.lower()
    assert scrum_bot.current_state == "ask_create_issue"
    
    # Test with invalid response
    scrum_bot.current_state = "blockers"
    response = scrum_bot.process_response("maybe")
    assert "yes or no" in response.lower()
    assert scrum_bot.current_state == "blockers"
    
    # Test with empty response
    scrum_bot.current_state = "blockers"
    response = scrum_bot.process_response("")
    assert "yes or no" in response.lower()
    assert scrum_bot.current_state == "blockers"
    assert len(scrum_bot.scrum_data["blockers"]) == 0
    
    # Test with yes response
    scrum_bot.current_state = "blockers"
    response = scrum_bot.process_response("yes")
    assert "describe" in response.lower()
    assert scrum_bot.current_state == "blocker_details"

def test_process_response_blockers_yes(scrum_bot):
    scrum_bot.current_state = "blockers"
    response = scrum_bot.process_response("yes")
    assert "describe" in response.lower()
    assert scrum_bot.current_state == "blocker_details"

def test_process_response_blocker_details(scrum_bot):
    scrum_bot.current_state = "blocker_details"
    response = scrum_bot.process_response("Blocked by SCRUM-789")
    assert "other" in response.lower()
    assert scrum_bot.current_state == "more_blockers"
    scrum_bot.jira.update_issue_status.assert_called_once_with("SCRUM-789", ScrumStatus.BLOCKED)
    scrum_bot.jira.create_blocker.assert_called_once_with("SCRUM-789", "Blocked by SCRUM-789")

@pytest.fixture
def mock_jira():
    jira_mock = MagicMock()
    jira_mock.update_issue_status = MagicMock(return_value=True)
    jira_mock.create_blocker = MagicMock(return_value=(True, "TEST-2"))
    return jira_mock

@pytest.fixture
def scrum_bot(mock_jira):
    bot = ScrumBot(mock_jira)
    return bot

def test_start_conversation(scrum_bot):
    response = scrum_bot.start_conversation()
    assert isinstance(response, dict)
    assert "message" in response
    assert "Hi" in response["message"]
    assert scrum_bot.current_state == "greeting"





def test_process_response_yesterday_state(scrum_bot):
    scrum_bot.current_state = "greeting"
    response = scrum_bot.process_response("I completed SCRUM-1")
    assert "today" in response.lower()
    assert scrum_bot.current_state == "today"
    assert scrum_bot.scrum_data["yesterday"] == "I completed SCRUM-1"

def test_process_response_today_state(scrum_bot):
    scrum_bot.current_state = "today"
    response = scrum_bot.process_response("Working on SCRUM-456")
    assert "blocker" in response.lower()
    assert scrum_bot.current_state == "blockers"
    assert "SCRUM-456" in scrum_bot.scrum_data["today"]

def test_process_response_blockers_no(scrum_bot):
    scrum_bot.current_state = "blockers"
    response = scrum_bot.process_response("no")
    assert "complete" in response.lower()
    assert scrum_bot.current_state == "done"
    assert len(scrum_bot.scrum_data["blockers"]) == 0

def test_generate_summary_with_data(scrum_bot):
    scrum_bot.scrum_data = {
        "yesterday": ["SCRUM-123"],
        "today": ["SCRUM-456"],
        "blockers": []
    }
    summary = scrum_bot.generate_summary()
    assert "SCRUM-123" in summary
    assert "SCRUM-456" in summary
    assert isinstance(summary, str)











def test_reset_conversation(scrum_bot):
    scrum_bot.current_state = "blockers"
    scrum_bot.scrum_data["yesterday"] = "test"
    response = scrum_bot.start_conversation()
    assert "yesterday" in response["message"].lower()
    assert scrum_bot.current_state == "blockers"

def test_process_response_with_jira_key(scrum_bot):
    scrum_bot.current_state = "today"
    response = scrum_bot.process_response("Working on SCRUM-123")
    assert "blocker" in response.lower()
    assert scrum_bot.current_state == "blockers"
    scrum_bot.jira.update_issue_status.assert_called_once_with("SCRUM-123", ScrumStatus.IN_PROGRESS)

def test_process_response_with_multiple_jira_keys(scrum_bot):
    scrum_bot.current_state = "greeting"
    response = scrum_bot.process_response("Completed SCRUM-1 and SCRUM-2")
    assert "today" in response.lower()
    assert scrum_bot.current_state == "today"
    assert scrum_bot.scrum_data["yesterday"] == "Completed SCRUM-1 and SCRUM-2"

def test_process_response_with_blocked_status(scrum_bot):
    scrum_bot.current_state = "today"
    response = scrum_bot.process_response("Blocked by SCRUM-3")
    assert "blocker" in response.lower()
    assert scrum_bot.current_state == "blockers"
    scrum_bot.jira.update_issue_status.assert_called_once_with("SCRUM-3", ScrumStatus.IN_PROGRESS)

def test_process_response_flow(scrum_bot):
    # Test complete conversation flow
    # 1. Start with greeting
    scrum_bot.current_state = "greeting"
    response = scrum_bot.process_response("Completed SCRUM-123")
    assert "today" in response.lower()
    assert scrum_bot.current_state == "today"
    assert scrum_bot.scrum_data["yesterday"] == "Completed SCRUM-123"
    
    # 2. Move to today's work
    response = scrum_bot.process_response("Working on SCRUM-456")
    assert "blockers" in response.lower()
    assert scrum_bot.current_state == "blockers"
    assert scrum_bot.scrum_data["today"] == "Working on SCRUM-456"
    
    # 3. Handle blockers
    response = scrum_bot.process_response("yes")
    assert "describe" in response.lower()
    assert scrum_bot.current_state == "blocker_details"
    
    # 4. Add blocker details
    response = scrum_bot.process_response("Blocked by SCRUM-789")
    assert "other" in response.lower()
    assert scrum_bot.current_state == "more_blockers"
    
    # 5. Complete blocker flow
    response = scrum_bot.process_response("no")
    assert "create" in response.lower()
    assert scrum_bot.current_state == "ask_create_issue"

def test_process_response_with_jira_keys(scrum_bot):
    # Test with single JIRA key
    scrum_bot.current_state = "greeting"
    response = scrum_bot.process_response("Working on SCRUM-123")
    assert "today" in response.lower()
    assert scrum_bot.current_state == "today"
    
    # Test with multiple JIRA keys
    scrum_bot.current_state = "today"
    response = scrum_bot.process_response("Working on SCRUM-456 and SCRUM-789")
    assert "blockers" in response.lower()
    assert scrum_bot.current_state == "blockers"
    
    # Test with number word JIRA key
    scrum_bot.current_state = "blocker_details"
    response = scrum_bot.process_response("Blocked by SCRUM twenty three")
    assert "other" in response.lower()
    assert scrum_bot.current_state == "more_blockers"

def test_process_response_states(scrum_bot):
    # Test greeting state
    scrum_bot.current_state = "greeting"
    response = scrum_bot.process_response("Completed SCRUM-123")
    assert "today" in response.lower()
    assert scrum_bot.current_state == "today"
    assert scrum_bot.scrum_data["yesterday"] == "Completed SCRUM-123"
    
    # Test today state
    scrum_bot.current_state = "today"
    response = scrum_bot.process_response("Working on SCRUM-456")
    assert "blockers" in response.lower()
    assert scrum_bot.current_state == "blockers"
    assert scrum_bot.scrum_data["today"] == "Working on SCRUM-456"
    
    # Test blockers state - no
    scrum_bot.current_state = "blockers"
    response = scrum_bot.process_response("no")
    assert "create" in response.lower()
    assert scrum_bot.current_state == "ask_create_issue"
    
    # Test blockers state - yes
    scrum_bot.current_state = "blockers"
    response = scrum_bot.process_response("yes")
    assert "describe" in response.lower()
    assert scrum_bot.current_state == "blocker_details"

def test_process_response_edge_cases(scrum_bot):
    # Test invalid blocker response
    scrum_bot.current_state = "blockers"
    response = scrum_bot.process_response("maybe")
    assert "yes or no" in response.lower()
    assert scrum_bot.current_state == "blockers"
    
    # Test blocker details with JIRA key
    scrum_bot.current_state = "blocker_details"
    response = scrum_bot.process_response("Blocked by SCRUM-789")
    assert "other" in response.lower()
    assert scrum_bot.current_state == "more_blockers"
    scrum_bot.jira.update_issue_status.assert_called_once_with("SCRUM-789", ScrumStatus.BLOCKED)
    
    # Test multiple JIRA keys
    scrum_bot.current_state = "greeting"
    response = scrum_bot.process_response("Completed SCRUM-1 and SCRUM-2")
    assert "today" in response.lower()
    assert scrum_bot.current_state == "today"



@pytest.fixture
def mock_jira():
    jira_mock = MagicMock()
    jira_mock.update_issue_status = MagicMock(return_value=True)
    jira_mock.create_blocker = MagicMock(return_value=(True, "TEST-2"))
    return jira_mock

@pytest.fixture
def scrum_bot(mock_jira):
    bot = ScrumBot(mock_jira)
    bot.current_state = "greeting"
    bot.username = "testuser"
    return bot


    assert scrum_bot.determine_status("blocked by TEST-4") == "Blocked"
    assert scrum_bot.determine_status("waiting for TEST-4") == "Blocked"
    
    # Test done status
    assert scrum_bot.determine_status("completed TEST-4") == "Done"
    assert scrum_bot.determine_status("finished TEST-4") == "Done"
    assert scrum_bot.determine_status("done with TEST-4") == "Done"
    
    # Test in progress status
    assert scrum_bot.determine_status("working on TEST-4") == "In Progress"
    assert scrum_bot.determine_status("started TEST-4") == "In Progress"
    assert scrum_bot.determine_status("continuing TEST-4") == "In Progress"
    
    # Test no status
    assert scrum_bot.determine_status("TEST-4") == "In Progress"

def test_process_response_greeting(scrum_bot):
    scrum_bot.current_state = "greeting"
    response = scrum_bot.process_response("hi")
    assert "today" in response.lower()
    assert scrum_bot.current_state == "today"

def test_process_response_yesterday(scrum_bot):
    # Test normal flow
    scrum_bot.current_state = "greeting"
    response = scrum_bot.process_response("worked on SCRUM-1")
    assert "working" in response.lower()
    assert scrum_bot.current_state == "today"
    assert scrum_bot.scrum_data["yesterday"] == "worked on SCRUM-1"
    scrum_bot.jira.update_issue_status.assert_called_once_with("SCRUM-1", ScrumStatus.DONE)
    
    # Test with multiple JIRA keys
    scrum_bot.current_state = "greeting"
    response = scrum_bot.process_response("worked on SCRUM-2 and SCRUM-3")
    assert "working" in response.lower()
    assert scrum_bot.current_state == "today"
    assert scrum_bot.scrum_data["yesterday"] == "worked on SCRUM-2 and SCRUM-3"

def test_process_response_today(scrum_bot):
    # Test normal flow
    scrum_bot.current_state = "today"
    response = scrum_bot.process_response("will work on SCRUM-2")
    assert "blockers" in response.lower()
    assert scrum_bot.current_state == "blockers"
    assert scrum_bot.scrum_data["today"] == "will work on SCRUM-2"
    scrum_bot.jira.update_issue_status.assert_called_once_with("SCRUM-2", ScrumStatus.IN_PROGRESS)
    
    # Test with multiple JIRA keys
    scrum_bot.current_state = "today"
    response = scrum_bot.process_response("will work on SCRUM-3 and SCRUM-4")
    assert "blockers" in response.lower()
    assert scrum_bot.current_state == "blockers"
    assert scrum_bot.scrum_data["today"] == "will work on SCRUM-3 and SCRUM-4"

# Updated to handle blockers
def test_process_response_blockers_no(scrum_bot):
    scrum_bot.current_state = "blockers"
    response = scrum_bot.process_response("no")
    assert scrum_bot.current_state == "ask_create_issue"
    assert len(scrum_bot.scrum_data["blockers"]) == 0

# Updated to handle blockers
def test_process_response_blockers_yes(scrum_bot):
    scrum_bot.current_state = "blockers"
    response = scrum_bot.process_response("yes")
    assert scrum_bot.current_state == "blocker_details"
    assert "describe" in response.lower()

# Updated to handle blocker details
def test_process_response_blocker_details(scrum_bot):
    # Test with JIRA key
    scrum_bot.current_state = "blocker_details"
    scrum_bot.jira.create_blocker.return_value = (True, "SCRUM-2")
    response = scrum_bot.process_response("blocked by SCRUM-1 due to dependency")
    
    assert "other blockers" in response.lower()
    assert len(scrum_bot.scrum_data["blockers"]) == 1
    
    # Test with multiple JIRA keys
    scrum_bot.current_state = "blocker_details"
    scrum_bot.jira.create_blocker.return_value = (True, "SCRUM-3")
    response = scrum_bot.process_response("blocked by SCRUM-1 and SCRUM-2")
    
    assert "other blockers" in response.lower()
    assert len(scrum_bot.scrum_data["blockers"]) == 2
    
    # Test without JIRA key
    scrum_bot.current_state = "blocker_details"
    response = scrum_bot.process_response("having environment issues")
    
    assert "other blockers" in response.lower()
    assert len(scrum_bot.scrum_data["blockers"]) == 3
    
    # Test blocker creation failure
    scrum_bot.current_state = "blocker_details"
    scrum_bot.jira.create_blocker.return_value = (False, "Error creating blocker")
    response = scrum_bot.process_response("blocked by SCRUM-4")
    
    assert "other blockers" in response.lower()

# Updated to handle more blockers
def test_process_response_more_blockers(scrum_bot):
    # Test no more blockers
    scrum_bot.current_state = "blockers"
    response = scrum_bot.process_response("no")
    assert scrum_bot.current_state == "ask_create_issue"
    assert "create" in response.lower()
    assert len(scrum_bot.scrum_data["blockers"]) == 0
    
    # Test yes more blockers
    scrum_bot.current_state = "blockers"
    response = scrum_bot.process_response("yes")
    assert "describe" in response.lower()
    assert scrum_bot.current_state == "blocker_details"
    
    # Test invalid response
    scrum_bot.current_state = "blockers"
    response = scrum_bot.process_response("maybe")
    assert "yes or no" in response.lower()

def test_process_response_ask_create_issue(scrum_bot):
    # Test yes create issue
    scrum_bot.current_state = "ask_create_issue"
    response = scrum_bot.process_response("yes")
    assert "summary" in response.lower() or "title" in response.lower()
    assert scrum_bot.current_state == "issue_creation"
    assert scrum_bot.issue_creation_state == "summary"
    
    # Test no create issue
    scrum_bot.current_state = "ask_create_issue"
    response = scrum_bot.process_response("no")
    assert "complete" in response.lower() or "day" in response.lower() or "standup" in response.lower()
    assert scrum_bot.current_state == "summary"
    
    # Test invalid response
    scrum_bot.current_state = "ask_create_issue"
    response = scrum_bot.process_response("maybe")
    assert "yes" in response.lower() or "no" in response.lower()

def test_process_response_issue_summary(scrum_bot):
    # Test with valid summary
    scrum_bot.current_state = "issue_creation"
    scrum_bot.issue_creation_state = "summary"
    scrum_bot.issue_creation_data = {
        "summary": None,
        "description": None,
        "issue_type": None,
        "priority": None,
        "assignee": None
    }
    response = scrum_bot.process_response("Need to implement feature X")
    assert "detail" in response.lower() or "description" in response.lower() or "provide" in response.lower()
    assert scrum_bot.current_state == "issue_creation"
    assert scrum_bot.issue_creation_state == "description"
    assert scrum_bot.issue_creation_data["summary"] == "Need to implement feature X"
    
    # Test with empty summary
    scrum_bot.current_state = "issue_creation"
    scrum_bot.issue_creation_state = "summary"
    response = scrum_bot.process_response("")
    assert "summary" in response.lower() or "title" in response.lower() or "issue" in response.lower()
    assert scrum_bot.current_state == "issue_creation"
    assert scrum_bot.issue_creation_state == "summary"
    
    # Test with very long summary
    scrum_bot.current_state = "issue_creation"
    scrum_bot.issue_creation_state = "summary"
    long_summary = "A" * 300
    response = scrum_bot.process_response(long_summary)
    assert "detail" in response.lower() or "description" in response.lower() or "provide" in response.lower()
    assert scrum_bot.current_state == "issue_creation"
    assert scrum_bot.issue_creation_state == "description"
    assert len(scrum_bot.issue_creation_data["summary"]) <= 255

def test_process_response_issue_description(scrum_bot):
    # Test with valid description
    scrum_bot.current_state = "issue_creation"
    scrum_bot.issue_creation_state = "description"
    scrum_bot.issue_creation_data = {
        "summary": "Test Summary",
        "description": None,
        "issue_type": None,
        "priority": None,
        "assignee": None
    }
    mock_jira = scrum_bot.jira
    mock_jira.create_issue.return_value = (True, "SCRUM-123")
    response = scrum_bot.process_response("Detailed description of feature X")
    assert "type" in response.lower() or "task" in response.lower() or "bug" in response.lower() or "story" in response.lower()
    assert scrum_bot.current_state == "issue_creation"
    assert scrum_bot.issue_creation_state == "issue_type"
    assert scrum_bot.issue_creation_data["description"] == "Detailed description of feature X"
    
    # Test with empty description
    scrum_bot.current_state = "issue_creation"
    scrum_bot.issue_creation_state = "description"
    response = scrum_bot.process_response("")
    assert "description" in response.lower() or "provide" in response.lower() or "detail" in response.lower()
    assert scrum_bot.current_state == "issue_creation"
    assert scrum_bot.issue_creation_state == "description"
    
    # Test with very long description
    scrum_bot.current_state = "issue_creation"
    scrum_bot.issue_creation_state = "description"
    long_desc = "A" * 5000
    response = scrum_bot.process_response(long_desc)
    assert "issue" in response.lower() or "type" in response.lower() or "task" in response.lower() or "bug" in response.lower() or "story" in response.lower()
    assert scrum_bot.current_state == "issue_creation"
    assert scrum_bot.issue_creation_state == "issue_type"
    assert len(scrum_bot.issue_creation_data["description"]) <= 4000

def test_process_response_issue_type(scrum_bot):
    # Test with valid issue type - Task
    scrum_bot.current_state = "issue_creation"
    scrum_bot.issue_creation_state = "issue_type"
    scrum_bot.issue_creation_data = {
        "summary": "Test Summary",
        "description": "Test Description",
        "issue_type": None,
        "priority": None,
        "assignee": None
    }
    mock_jira = scrum_bot.jira
    mock_jira.create_issue.return_value = (True, "SCRUM-123")
    response = scrum_bot.process_response("Task")
    assert "priority" in response.lower() or "highest" in response.lower() or "high" in response.lower() or "medium" in response.lower() or "low" in response.lower() or "lowest" in response.lower()
    assert scrum_bot.current_state == "issue_creation"
    assert scrum_bot.issue_creation_state == "priority"
    assert scrum_bot.issue_creation_data["issue_type"] == "Task"
    
    # Test with valid issue type - Bug
    scrum_bot.current_state = "issue_creation"
    scrum_bot.issue_creation_state = "issue_type"
    scrum_bot.issue_creation_data = {
        "summary": "Test Summary",
        "description": "Test Description",
        "issue_type": None,
        "priority": None,
        "assignee": None
    }
    response = scrum_bot.process_response("Bug")
    assert "priority" in response.lower() or "highest" in response.lower() or "high" in response.lower() or "medium" in response.lower() or "low" in response.lower() or "lowest" in response.lower()
    assert scrum_bot.current_state == "issue_creation"
    assert scrum_bot.issue_creation_state == "priority"
    assert scrum_bot.issue_creation_data["issue_type"] == "Bug"
    
    # Test with valid issue type - Story
    scrum_bot.current_state = "issue_creation"
    scrum_bot.issue_creation_state = "issue_type"
    scrum_bot.issue_creation_data = {
        "summary": "Test Summary",
        "description": "Test Description",
        "issue_type": None,
        "priority": None,
        "assignee": None
    }
    response = scrum_bot.process_response("Story")
    assert "priority" in response.lower() or "highest" in response.lower() or "high" in response.lower() or "medium" in response.lower() or "low" in response.lower() or "lowest" in response.lower()
    assert scrum_bot.current_state == "issue_creation"
    assert scrum_bot.issue_creation_state == "priority"
    assert scrum_bot.issue_creation_data["issue_type"] == "Story"
    
    # Test with invalid issue type
    scrum_bot.current_state = "issue_creation"
    scrum_bot.issue_creation_state = "issue_type"
    scrum_bot.issue_creation_data = {
        "summary": "Test Summary",
        "description": "Test Description",
        "issue_type": None,
        "priority": None,
        "assignee": None
    }
    response = scrum_bot.process_response("invalid")
    assert "type" in response.lower() or "task" in response.lower() or "bug" in response.lower() or "story" in response.lower()
    assert scrum_bot.current_state == "issue_creation"
    assert scrum_bot.issue_creation_state == "issue_type"

def test_process_response_priority_and_assignee(scrum_bot):
    # Test with valid priority
    scrum_bot.current_state = "issue_creation"
    scrum_bot.issue_creation_state = "priority"
    scrum_bot.issue_creation_data = {
        "summary": "Test Summary",
        "description": "Test Description",
        "issue_type": "Task",
        "priority": None,
        "assignee": None
    }
    mock_jira = scrum_bot.jira
    mock_jira.create_issue.return_value = (True, "SCRUM-123")
    response = scrum_bot.process_response("High")
    assert "assignee" in response.lower() or "who" in response.lower() or "assign" in response.lower() or "username" in response.lower()
    assert scrum_bot.current_state == "issue_creation"
    assert scrum_bot.issue_creation_state == "assignee"
    assert scrum_bot.issue_creation_data["priority"] == "High"
    
    # Test with valid assignee
    response = scrum_bot.process_response("username")
    assert "created" in response.lower() or "scrum-123" in response.lower()
    assert scrum_bot.current_state == "ask_create_issue"
    assert scrum_bot.issue_creation_data["assignee"] == "username"
    
    # Test with unassigned
    scrum_bot.current_state = "issue_creation"
    scrum_bot.issue_creation_state = "assignee"
    scrum_bot.issue_creation_data = {
        "summary": "Test Summary",
        "description": "Test Description",
        "issue_type": "Task",
        "priority": "High",
        "assignee": None
    }
    response = scrum_bot.process_response("unassigned")
    assert "created" in response.lower() or "scrum-123" in response.lower()
    assert scrum_bot.current_state == "ask_create_issue"
    assert scrum_bot.issue_creation_data["assignee"] == None
    
    # Test with invalid priority
    scrum_bot.current_state = "issue_creation"
    scrum_bot.issue_creation_state = "priority"
    scrum_bot.issue_creation_data = {
        "summary": "Test Summary",
        "description": "Test Description",
        "issue_type": "Task",
        "priority": None,
        "assignee": None
    }
    response = scrum_bot.process_response("invalid")
    assert "priority" in response.lower() or "highest" in response.lower() or "high" in response.lower() or "medium" in response.lower() or "low" in response.lower() or "lowest" in response.lower()
    assert scrum_bot.current_state == "issue_creation"
    assert scrum_bot.issue_creation_state == "priority"

def test_llm_response_patterns(scrum_bot):
    # Test LLM response patterns for different states
    
    # Start fresh conversation
    scrum_bot.start_conversation()
    
    # Test greeting response format
    response = scrum_bot.process_response("Hi")
    assert response != ""
    assert scrum_bot.current_state == "yesterday"
    
    # Test yesterday response format with multiple tasks and statuses
    response = scrum_bot.process_response("I completed SCRUM-123, started working on SCRUM-456, and haven't begun SCRUM-789")
    assert response != ""
    assert scrum_bot.current_state == "today"
    assert "SCRUM-123" in str(scrum_bot.yesterday_tasks)
    assert "SCRUM-456" in str(scrum_bot.yesterday_tasks)
    assert "SCRUM-789" in str(scrum_bot.yesterday_tasks)
    
    # Test today response format with multiple tasks and statuses
    response = scrum_bot.process_response("I will finish SCRUM-456, continue SCRUM-789, and start SCRUM-101")
    assert response != ""
    assert scrum_bot.current_state == "blockers"
    assert "SCRUM-456" in str(scrum_bot.today_tasks)
    assert "SCRUM-789" in str(scrum_bot.today_tasks)
    assert "SCRUM-101" in str(scrum_bot.today_tasks)
    
    # Test blocker response format with details
    response = scrum_bot.process_response("yes")
    assert response != ""
    assert scrum_bot.current_state == "blocker_details"
    
    # Test blocker details with multiple tasks
    response = scrum_bot.process_response("SCRUM-456 is blocked by SCRUM-202, and SCRUM-789 is waiting on SCRUM-303")
    assert response != ""
    assert "SCRUM-456" in str(scrum_bot.blocked_tasks)
    assert "SCRUM-202" in str(scrum_bot.blocked_tasks)
    assert "SCRUM-789" in str(scrum_bot.blocked_tasks)
    assert "SCRUM-303" in str(scrum_bot.blocked_tasks)
    
    # Test issue creation flow with comprehensive data
    response = scrum_bot.process_response("yes")
    assert response != ""
    assert scrum_bot.current_state == "issue_creation"
    
    # Test summary with detailed information
    response = scrum_bot.process_response("Need to implement user authentication feature")
    assert response != ""
    assert "authentication" in str(scrum_bot.issue_creation_data)
    
    # Test description with comprehensive details
    response = scrum_bot.process_response("Implement OAuth2 authentication with Google and GitHub providers")
    assert response != ""
    assert "OAuth2" in str(scrum_bot.issue_creation_data)
    
    # Test issue type with validation
    response = scrum_bot.process_response("Story")
    assert response != ""
    assert "Story" in str(scrum_bot.issue_creation_data)
    
    # Test priority with validation
    response = scrum_bot.process_response("High")
    assert response != ""
    assert "High" in str(scrum_bot.issue_creation_data)
    
    # Test assignee with validation
    response = scrum_bot.process_response("@username")
    assert response != ""
    assert "username" in str(scrum_bot.issue_creation_data)

def test_llm_jira_key_extraction(scrum_bot):
    # Test JIRA key extraction from various formats
    test_cases = [
        ("Working on SCRUM-123", "SCRUM-123"),
        ("SCRUM-456 is in progress", "SCRUM-456"),
        ("scrum-234 needs review", "SCRUM-234"),
        ("Started working on Scrum-567", "SCRUM-567")
    ]
    
    for test_input, expected_key in test_cases:
        key = scrum_bot.extract_jira_key(test_input)
        assert key == expected_key

def test_llm_issue_creation_flow(scrum_bot):
    # Test issue creation flow responses
    
    # Test summary prompt
    scrum_bot.current_state = "issue_creation"
    scrum_bot.issue_creation_state = "summary"
    scrum_bot.issue_creation_data = {
        "summary": None,
        "description": None,
        "issue_type": None,
        "priority": None,
        "assignee": None
    }
    response = scrum_bot.process_response("Add login feature")
    assert response != ""
    assert scrum_bot.current_state == "issue_creation"
    assert scrum_bot.issue_creation_state == "description"
    assert scrum_bot.issue_creation_data["summary"] == "Add login feature"
    
    # Test description prompt
    scrum_bot.current_state = "issue_creation"
    scrum_bot.issue_creation_state = "description"
    scrum_bot.issue_creation_data = {
        "summary": "Add login feature",
        "description": None,
        "issue_type": None,
        "priority": None,
        "assignee": None
    }
    response = scrum_bot.process_response("Need to implement OAuth login")
    assert response != ""
    assert scrum_bot.current_state == "issue_creation"
    assert scrum_bot.issue_creation_state == "issue_type"
    assert scrum_bot.issue_creation_data["description"] == "Need to implement OAuth login"
    
    # Test type prompt
    scrum_bot.current_state = "issue_creation"
    scrum_bot.issue_creation_state = "issue_type"
    scrum_bot.issue_creation_data = {
        "summary": "Add login feature",
        "description": "Need to implement OAuth login",
        "issue_type": None,
        "priority": None,
        "assignee": None
    }
    response = scrum_bot.process_response("Story")
    assert response != ""
    assert scrum_bot.current_state == "issue_creation"
    assert scrum_bot.issue_creation_state == "priority"
    assert scrum_bot.issue_creation_data["issue_type"] == "Story"
    
    # Test priority prompt
    scrum_bot.current_state = "issue_creation"
    scrum_bot.issue_creation_state = "priority"
    scrum_bot.issue_creation_data = {
        "summary": "Add login feature",
        "description": "Need to implement OAuth login",
        "issue_type": "Story",
        "priority": None,
        "assignee": None
    }
    response = scrum_bot.process_response("High")
    assert response != ""
    assert scrum_bot.current_state == "issue_creation"
    assert scrum_bot.issue_creation_state == "assignee"
    assert scrum_bot.issue_creation_data["priority"] == "High"

def test_llm_status_detection(scrum_bot):
    # Test status detection from various phrases
    test_cases = [
        ("completed the task", ScrumStatus.DONE),
        ("finished working on", ScrumStatus.DONE),
        ("working on the feature", ScrumStatus.IN_PROGRESS),
        ("started development", ScrumStatus.IN_PROGRESS),
        ("will begin tomorrow", ScrumStatus.TODO),
        ("planning to start", ScrumStatus.TODO)
    ]
    
    for text, expected_status in test_cases:
        status = scrum_bot.determine_status(text)
        assert status == expected_status

def test_llm_conversation_flow(scrum_bot):
    # Test complete conversation flow with typical responses
    
    # Start conversation
    scrum_bot.start_conversation()
    
    # Greet and get yesterday's tasks
    response = scrum_bot.process_response("Hello")
    assert response != ""
    assert scrum_bot.current_state == "yesterday"
    
    # Yesterday's update with JIRA keys
    response = scrum_bot.process_response("I completed SCRUM-123")
    assert response != ""
    assert scrum_bot.current_state == "today"
    
    # Today's plan with status indicators
    response = scrum_bot.process_response("I will work on SCRUM-456")
    assert response != ""
    assert scrum_bot.current_state == "blockers"
    
    # No blockers, proceed to issue creation
    response = scrum_bot.process_response("no")
    assert response != ""
    assert scrum_bot.current_state == "ask_create_issue"
    
    # Issue creation flow
    response = scrum_bot.process_response("yes")
    assert response != ""
    assert scrum_bot.current_state == "issue_creation"
    
    # Test issue summary
    response = scrum_bot.process_response("Test summary")
    assert response != ""
    
    # Test issue description
    response = scrum_bot.process_response("Test description")
    assert response != ""
    
    # Test issue type
    response = scrum_bot.process_response("Task")
    assert response != ""
    
    # Test priority
    response = scrum_bot.process_response("High")
    assert response != ""
    
    # Test assignee
    response = scrum_bot.process_response("@username")
    assert response != ""

def test_llm_error_handling(scrum_bot):
    # Test error handling and edge cases
    
    # Test with invalid JIRA key formats
    invalid_keys = [
        "SCRUM123",  # Missing hyphen
        "SCRUM-ABC",  # Non-numeric ID
        "PROJECT-123",  # Wrong project prefix
        "SCRUM-",  # Missing ID
        "-123",  # Missing prefix
        "scrum123",  # Missing hyphen and lowercase
        "scrum-abc",  # Non-numeric ID and lowercase
        "project-123",  # Wrong project prefix and lowercase
        "scrum-",  # Missing ID and lowercase
        "-123"  # Missing prefix
    ]
    
    for invalid_key in invalid_keys:
        key = scrum_bot.extract_jira_key(invalid_key)
        assert key == ""  # Should be empty string
        
        # Also test in a sentence context
        key = scrum_bot.extract_jira_key(f"Working on {invalid_key} today")
        assert key == ""  # Should still be empty string
    
    # Test with mixed valid and invalid keys
    mixed_texts = [
        "Working on SCRUM-123 and SCRUM-ABC",
        "SCRUM-456 is blocked by PROJECT-789",
        "Started scrum-123 and SCRUM-ABC",
        "SCRUM123 and SCRUM-456 in progress"
    ]
    
    for text in mixed_texts:
        key = scrum_bot.extract_jira_key(text)
        # Should always extract the valid key
        assert any(valid_key in key for valid_key in ["SCRUM-123", "SCRUM-456"])
        
    # Test with empty or invalid input
    edge_cases = [
        "",  # Empty string
        " ",  # Just whitespace
        "No JIRA keys here",  # No keys
        "123-456",  # Wrong format
        "SCRUM",  # Incomplete key
        "123"  # Just numbers
    ]
    
    for text in edge_cases:
        key = scrum_bot.extract_jira_key(text)
        assert key == ""  # Should be empty string

def test_llm_state_transitions(scrum_bot):
    # Test state transitions
    
    # Reset state before starting
    scrum_bot.start_conversation()
    
    # Test greeting to yesterday
    response = scrum_bot.process_response("hello")
    assert response != ""
    assert scrum_bot.current_state == "yesterday"
    
    # Test yesterday to today
    response = scrum_bot.process_response("worked on SCRUM-123")
    assert response != ""
    assert scrum_bot.current_state == "today"
    
    # Test today to blockers
    response = scrum_bot.process_response("will work on SCRUM-456")
    assert response != ""
    assert scrum_bot.current_state == "blockers"
    
    # Test blockers to next state
    response = scrum_bot.process_response("no")
    assert response != ""
    assert scrum_bot.current_state == "ask_create_issue"

def test_llm_response_validation(scrum_bot):
    # Test response validation for different states
    
    # Test empty responses
    empty_responses = ["", " ", "\n", "\t"]
    for state in ["greeting", "yesterday", "today", "blockers"]:
        scrum_bot.current_state = state
        for response in empty_responses:
            result = scrum_bot.process_response(response)
            assert result != ""
    
    # Test very long responses
    long_response = "A" * 5000
    for state in ["greeting", "yesterday", "today", "blockers"]:
        scrum_bot.current_state = state
        result = scrum_bot.process_response(long_response)
        assert result != ""
        assert len(result) < 5000  # Response should be shorter than input

def test_process_response_assignee(scrum_bot):
    # Test with valid assignee
    scrum_bot.current_state = "issue_creation"
    scrum_bot.issue_creation_state = "assignee"
    scrum_bot.issue_creation_data = {
        "summary": "Test Summary",
        "description": "Test Description",
        "issue_type": "Task",
        "priority": "High",
        "assignee": None
    }
    mock_jira = scrum_bot.jira
    mock_jira.create_issue.return_value = (True, "SCRUM-123")
    response = scrum_bot.process_response("username")
    assert "created" in response.lower() or "scrum-123" in response.lower()
    assert scrum_bot.current_state == "ask_create_issue"
    assert scrum_bot.issue_creation_data["assignee"] == "username"
    
    # Test with unassigned
    scrum_bot.current_state = "issue_creation"
    scrum_bot.issue_creation_state = "assignee"
    scrum_bot.issue_creation_data = {
        "summary": "Test Summary",
        "description": "Test Description",
        "issue_type": "Task",
        "priority": "High",
        "assignee": None
    }
    response = scrum_bot.process_response("unassigned")
    assert "created" in response.lower() or "scrum-123" in response.lower()
    assert scrum_bot.current_state == "ask_create_issue"
    assert scrum_bot.issue_creation_data["assignee"] == None

def test_process_response_mixed_cases(scrum_bot):
    # Test with special characters
    scrum_bot.current_state = "yesterday"
    response = scrum_bot.process_response("!@#$%^&*()")
    assert "today" in response.lower()
    assert scrum_bot.current_state == "today"
    
    # Test with numbers only
    scrum_bot.current_state = "today"
    response = scrum_bot.process_response("12345")
    assert "blocker" in response.lower()
    assert scrum_bot.current_state == "blockers"
    
    # Test with mixed content
    scrum_bot.current_state = "blockers"
    response = scrum_bot.process_response("no blockers 123!@#")
    assert "create" in response.lower()
    assert scrum_bot.current_state == "ask_create_issue"

def test_process_response_state_transitions(scrum_bot):
    # Test state transitions
    states = ["greeting", "yesterday", "today", "blockers", "ask_create_issue", "summary"]
    for state in states:
        scrum_bot.current_state = state
        response = scrum_bot.process_response("test response")
        assert response != ""  # Ensure we get some response
        assert scrum_bot.current_state in states  # Ensure valid state transition
    assert scrum_bot.current_state == "ask_create_issue"

# Updated to handle invalid state
def test_process_response_invalid_state(scrum_bot):
    # Test invalid state
    scrum_bot.current_state = "invalid_state"
    response = scrum_bot.process_response("test")
    assert "what did you work on yesterday" in response.lower()
    assert scrum_bot.current_state == "greeting"

# Updated to handle summary generation
def test_generate_summary(scrum_bot):
    # Set up test data
    scrum_bot.scrum_data = {
        "yesterday": "finished SCRUM-1",
        "today": "working on SCRUM-2",
        "blockers": ["blocked by SCRUM-3"]
    }
    summary = scrum_bot.generate_summary()
    # Check summary content
    assert "SCRUM-1" in summary
    assert "SCRUM-2" in summary
    assert "SCRUM-3" in summary
    assert isinstance(summary, str)
    assert "complete" in summary.lower()
    assert "awesome" in summary.lower()

import pytest
from unittest.mock import patch, MagicMock
from app import app
from talking_bot import ScrumBot
import json

@pytest.fixture
def mock_scrum_bot():
    mock = MagicMock(spec=ScrumBot)
    def process_response_side_effect(message):
        if not message or len(message) > 1000:
            return {"error": "Invalid input", "message": "Invalid input"}
        return {
            "message": "Test response for: " + message,
            "state": "today",
            "speech_segments": ["Test", "response"]
        }
    mock.process_response.side_effect = process_response_side_effect
    mock.start_conversation.return_value = {
        "message": "Hi! Let's start the standup.",
        "speech_segments": ["Hi!", "Let's start the standup."],
        "state": "greeting"
    }
    return mock

@pytest.fixture
def client(mock_scrum_bot):
    app.config['TESTING'] = True
    app.bot = mock_scrum_bot
    with app.test_client() as client:
        yield client

def test_basic_chat_flow(client):
    # Start conversation
    start_response = client.get('/api/start')
    assert start_response.status_code == 200
    start_data = json.loads(start_response.data.decode())
    assert start_data['success'] is True
    assert 'message' in start_data
    assert 'speech_segments' in start_data
    
    # Test chat messages
    messages = [
        "I worked on SCRUM-123 yesterday",
        "Working on the login page today",
        "No blockers"
    ]
    
    for msg in messages:
        response = client.post('/api/chat', 
                             data=json.dumps({'message': msg}),
                             content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['success'] is True
        assert 'message' in data
        assert 'speech_segments' in data

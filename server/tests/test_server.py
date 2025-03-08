import pytest
from unittest.mock import patch, MagicMock
from app import app
import json

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_chat_endpoint_success(client):
    response = client.post('/api/chat', 
                         data=json.dumps({'message': 'test message'}),
                         content_type='application/json')
    assert response.status_code == 200
    data = json.loads(response.data.decode())
    assert data['success'] is True
    assert 'message' in data
    assert 'speech_segments' in data

def test_chat_endpoint_missing_message(client):
    response = client.post('/api/chat',
                         data=json.dumps({}),
                         content_type='application/json')
    assert response.status_code == 400
    data = json.loads(response.data.decode())
    assert data['success'] is False
    assert 'error' in data

def test_chat_endpoint_invalid_json(client):
    response = client.post('/api/chat',
                         data='invalid json',
                         content_type='application/json')
    assert response.status_code == 400
    data = json.loads(response.data.decode())
    assert data['success'] is False
    assert 'error' in data

def test_project_summary_endpoint_success(client):
    response = client.get('/api/project_summary')
    assert response.status_code == 200
    data = json.loads(response.data.decode())
    assert data['success'] is True
    assert 'summary' in data

def test_project_summary_endpoint_error(client):
    with patch('app.get_project_summary', side_effect=Exception('Test error')):
        response = client.get('/api/project_summary')
        assert response.status_code == 500
        data = json.loads(response.data.decode())
        assert data['success'] is False
        assert 'error' in data

def test_speech_to_text_endpoint(client):
    with patch('app.process_audio', return_value='test transcription'):
        response = client.post('/api/speech_to_text',
                             data={'audio': (b'test audio data', 'test.wav')},
                             content_type='multipart/form-data')
        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['success'] is True
        assert data['text'] == 'test transcription'

def test_text_to_speech_endpoint(client):
    with patch('app.generate_speech', return_value=b'test audio data'):
        response = client.post('/api/text_to_speech',
                             data=json.dumps({'text': 'test text'}),
                             content_type='application/json')
        assert response.status_code == 200
        assert response.data == b'test audio data'

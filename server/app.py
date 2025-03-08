from quart import Quart, request, jsonify, send_from_directory, send_file
from talking_bot import ScrumBot, JiraAPI, JIRA_EMAIL, JIRA_API_KEY, JIRA_BASE_URL, speak_text, recognize_speech
import os
import io
import asyncio

app = Quart(__name__, static_folder='/app/static', static_url_path='')
jira = JiraAPI(JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_KEY)
scrum_bot = ScrumBot(jira)

# Serve static files for routes not starting with /api
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
async def serve(path):
    if path.startswith('api/'):
        return jsonify({"error": "Not found"}), 404
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return await send_from_directory(app.static_folder, path)
    return await send_from_directory(app.static_folder, 'index.html')

@app.route('/api/start', methods=['GET'])
async def start_session():
    """Start a new chat session"""
    try:
        # Get the initial greeting from ScrumBot
        response = scrum_bot.start_conversation()
        return jsonify({
            "success": True,
            "message": response["message"],
            "speech_segments": response["speech_segments"],
            "stage": "greeting"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

@app.route('/api/chat', methods=['POST'])
async def chat():
    """Handle chat messages"""
    try:
        data = await request.get_json()
        message = data.get('message', '')
        stage = data.get('stage', 'greeting')
        
        # Process the message using ScrumBot
        response = scrum_bot.process_response(message)
        
        return jsonify({
            "success": True,
            "message": response,
            "stage": stage
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

@app.route('/api/speak', methods=['POST'])
async def text_to_speech():
    """Convert text to speech"""
    try:
        data = await request.get_json()
        text = data.get('text', '')
        
        # Convert text to speech using the speak_text function
        audio_data = await speak_text(text)
        
        if audio_data is None:
            return jsonify({
                "success": False,
                "message": "Failed to generate speech"
            }), 500
        
        # Create a BytesIO object from the audio data
        audio_io = io.BytesIO(audio_data)
        audio_io.seek(0)  # Ensure we're at the start of the buffer
        
        # Send the audio file as WAV
        return await send_file(
            audio_io,
            mimetype='audio/wav',
            as_attachment=True,
            attachment_filename='speech.wav',  
            conditional=False  # Disable conditional responses
        )
    except Exception as e:
        print(f"[ERROR] Error in text_to_speech: {e}")  
        import traceback
        traceback.print_exc()  
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

@app.route('/api/get_todo_tasks', methods=['GET'])
async def get_todo_tasks():
    """Get TODO tasks for the current user"""
    try:
        # Use the username instead of account ID
        tasks = scrum_bot.get_todo_tasks("meghanathink41")
        return jsonify({
            "success": True,
            "tasks": tasks
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)

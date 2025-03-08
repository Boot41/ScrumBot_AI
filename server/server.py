import os
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List
import json
from talking_bot import ScrumBot, JiraAPI
import audio_processor
import traceback

# Load environment variables
load_dotenv()

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the bot
jira_api = JiraAPI(
    email=os.getenv("JIRA_EMAIL"),
    api_key=os.getenv("JIRA_API_KEY"),
    server_url=os.getenv("JIRA_SERVER_URL")
)
bot = ScrumBot(jira_api)

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    tasks: List[Dict[str, Any]]

@app.post("/api/chat")
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Handle chat messages from the user
    """
    try:
        response, tasks = bot.process_message(request.message)
        return ChatResponse(response=response, tasks=tasks)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/audio")
async def process_audio(file: UploadFile = File(...)):
    """
    Process audio file and return transcribed text
    """
    try:
        # Save the uploaded file temporarily
        file_path = f"temp_{file.filename}"
        with open(file_path, "wb") as temp_file:
            content = await file.read()
            temp_file.write(content)
        
        # Process the audio file
        text = audio_processor.transcribe_audio(file_path)
        
        # Clean up
        os.remove(file_path)
        
        # Get bot response
        response, tasks = bot.process_message(text)
        
        return {
            "text": text,
            "response": response,
            "tasks": tasks
        }
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host=os.getenv("HOST", "0.0.0.0"), port=int(os.getenv("PORT", 8000)))

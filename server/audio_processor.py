import aiohttp
import json
import os

class AudioProcessor:
    def __init__(self):
        self.deepgram_api_key = os.getenv('DEEPGRAM_API_KEY', 'your-api-key')
        self.tts_url = "https://api.deepgram.com/v1/speak"
        self.stt_url = "https://api.deepgram.com/v1/listen"

    async def text_to_speech(self, text: str) -> bytes:
        """Convert text to speech using Deepgram API"""
        headers = {
            "Authorization": f"Token {self.deepgram_api_key}",
            "Content-Type": "application/json"
        }
        payload = {"text": text}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.tts_url, headers=headers, json=payload) as response:
                    if response.status == 200:
                        return await response.read()
                    else:
                        error_text = await response.text()
                        raise Exception(f"API Error: {error_text}")
        except aiohttp.ClientError:
            raise Exception("Network error during text-to-speech conversion")

    async def speech_to_text(self, audio_data: bytes) -> str:
        """Convert speech to text using Deepgram API"""
        headers = {
            "Authorization": f"Token {self.deepgram_api_key}",
            "Content-Type": "audio/wav"
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.stt_url, headers=headers, data=audio_data) as response:
                    if response.status == 200:
                        result = await response.json()
                        return self._extract_transcript(result)
                    else:
                        error_text = await response.text()
                        raise Exception(f"API Error: {error_text}")
        except aiohttp.ClientError:
            raise Exception("Network error during speech-to-text conversion")

    def _extract_transcript(self, result: dict) -> str:
        """Extract transcript from API response"""
        try:
            alternatives = result["results"]["channels"][0]["alternatives"]
            return alternatives[0]["transcript"] if alternatives else ""
        except (KeyError, IndexError):
            return ""

    def split_into_segments(self, text: str, max_length: int = 100) -> list[str]:
        """Split long text into segments for TTS processing"""
        words = text.split()
        segments = []
        current_segment = []
        current_length = 0

        for word in words:
            word_length = len(word) + 1  # +1 for space
            if current_length + word_length > max_length and current_segment:
                segments.append(" ".join(current_segment))
                current_segment = [word]
                current_length = word_length
            else:
                current_segment.append(word)
                current_length += word_length

        if current_segment:
            segments.append(" ".join(current_segment))

        return segments

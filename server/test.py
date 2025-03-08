import requests

API_KEY = "bd89fbfd46a7612e9eedcb18dc13a4b632340e4d"
TEXT = "Hello, how are you?"
VOICE = "aura"

# Correct JSON payload (only `text` field)
payload = {"text": TEXT}  

response = requests.post(
    "https://api.deepgram.com/v1/speak",
    headers={
        "Authorization": f"Token {API_KEY}",
        "Content-Type": "application/json",
    },
    json=payload,  # ✅ Use `json` parameter instead of `data`
)

if response.status_code == 200:
    with open("output.mp3", "wb") as f:
        f.write(response.content)
    print("✅ TTS output saved as output.mp3. Try playing it!")
else:
    print(f"❌ Error: {response.json()}")  # ✅ Print error details

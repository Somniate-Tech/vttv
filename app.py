from fastapi import FastAPI
from pydantic import BaseModel
from voiceToText import process_base64_audio
from intentService import extract_intent

app = FastAPI()

# Voice to Text Endpoint
class AudioRequest(BaseModel):
    audio_base64: str

@app.post("/transcribe")
async def transcribe(request: AudioRequest):
    text = process_base64_audio(request.audio_base64)
    return {"text": text}



# Text to Intent Endpoint
class TextRequest(BaseModel):
    text: str

@app.post("/getIntent")
async def get_intent(request: TextRequest):
    result = extract_intent(request.text)
    return result

class AudioRequest(BaseModel):
    audio_base64: str

# voice to intent endpoint
@app.post("/voiceIntent")
async def voice_to_intent(request: AudioRequest):
    try:
        # Step 1: Speech → Text
        text = process_base64_audio(request.audio_base64)

        # Step 2: Text → Intent
        intent_result = extract_intent(text)

        return {
            "status": "success",
            "text": text,
            "intent": intent_result.get("intent")
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
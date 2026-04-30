import base64
import os
import uuid
import pyttsx3

TEMP_DIR = "temp_audio"
os.makedirs(TEMP_DIR, exist_ok=True)


# ----------------------------
# Text → Speech (Offline)
# ----------------------------
def generate_audio_from_text(text: str) -> str:
    try:
        file_path = os.path.join(TEMP_DIR, f"{uuid.uuid4()}.wav")

        engine = pyttsx3.init()

        # Optional: improve voice quality
        rate = engine.getProperty('rate')
        engine.setProperty('rate', rate - 20)

        voices = engine.getProperty('voices')
        if voices:
            engine.setProperty('voice', voices[0].id)

        # Save to file
        engine.save_to_file(text, file_path)
        engine.runAndWait()

        # Convert to base64
        with open(file_path, "rb") as f:
            audio_base64 = base64.b64encode(f.read()).decode("utf-8")

        return audio_base64

    except Exception as e:
        raise Exception(f"TTS failed: {str(e)}")

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)


# ----------------------------
# Main Pipeline
# ----------------------------
def process_reply_to_audio(data: dict) -> str:
    try:
        reply_text = data.get("data", {}).get("reply", "")

        if not reply_text:
            raise Exception("Reply text missing")

        audio_base64 = generate_audio_from_text(reply_text)

        return audio_base64

    except Exception as e:
        raise Exception(f"Processing failed: {str(e)}")
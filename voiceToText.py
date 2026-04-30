import base64
import os
import uuid
import subprocess
from groq import Groq
from dotenv import load_dotenv

# ----------------------------
# Setup
# ----------------------------
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

TEMP_DIR = "temp_audio"
os.makedirs(TEMP_DIR, exist_ok=True)


# ----------------------------
# Helpers
# ----------------------------
def decode_base64_audio(audio_base64: str) -> str:
    audio_bytes = base64.b64decode(audio_base64)
    input_path = os.path.join(TEMP_DIR, f"{uuid.uuid4()}.m4a")

    with open(input_path, "wb") as f:
        f.write(audio_bytes)

    return input_path


def convert_to_wav(input_path: str) -> str:
    output_path = input_path.replace(".m4a", ".wav")

    command = [
        "ffmpeg",
        "-i", input_path,
        "-ar", "16000",
        "-ac", "1",
        output_path,
        "-y"
    ]

    subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    if not os.path.exists(output_path):
        raise Exception("FFmpeg conversion failed")

    return output_path


def transcribe_audio(file_path: str) -> str:
    """Speech → Raw Text"""
    with open(file_path, "rb") as file:
        transcription = client.audio.transcriptions.create(
            file=(file_path, file.read()),
            model="whisper-large-v3-turbo",
            temperature=0,
            response_format="verbose_json",
        )

    return transcription.text.strip()


# ----------------------------
# 🔥 LLM FIX: Translate + Correct
# ----------------------------
def normalize_text(text: str) -> str:
    """
    Convert to English + fix domain-specific words
    """
    prompt = f"""
You are a speech post-processing engine for a SCHOOL TRANSPORT SYSTEM.

Tasks:
1. Translate to English if needed
2. Fix wrong words from speech recognition
3. Keep meaning same

IMPORTANT corrections:
- "boss" → "bus"
- "bas" → "bus"
- "buss" → "bus"
- "route" must stay "route"
- "stop" must stay "stop"
- "driver", "school", "student" must be correct

Return ONLY corrected English sentence.

Text:
{text}
"""

    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return completion.choices[0].message.content.strip()


def cleanup_files(*paths):
    for path in paths:
        if path and os.path.exists(path):
            os.remove(path)


# ----------------------------
# Main Pipeline
# ----------------------------
def process_base64_audio(audio_base64: str) -> str:
    input_path = None
    wav_path = None

    try:
        # Step 1: Decode
        input_path = decode_base64_audio(audio_base64)

        # Step 2: Convert
        wav_path = convert_to_wav(input_path)

        # Step 3: Transcribe
        raw_text = transcribe_audio(wav_path)

        # Step 4: Normalize (🔥 key step)
        final_text = normalize_text(raw_text)

        return final_text

    except Exception as e:
        raise Exception(f"Processing failed: {str(e)}")

    finally:
        cleanup_files(input_path, wav_path)
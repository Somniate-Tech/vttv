import base64
import os
import uuid
import subprocess
from groq import Groq


TEMP_DIR = "temp_audio"
os.makedirs(TEMP_DIR, exist_ok=True)
from dotenv import load_dotenv
import os
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
client = Groq()
def decode_base64_audio(audio_base64: str) -> str:
    """Decode base64 and save as .m4a"""
    audio_bytes = base64.b64decode(audio_base64)

    input_path = os.path.join(TEMP_DIR, f"{uuid.uuid4()}.m4a")

    with open(input_path, "wb") as f:
        f.write(audio_bytes)

    return input_path


def convert_to_wav(input_path: str) -> str:
    """Convert audio using FFmpeg (no pydub)"""
    output_path = input_path.replace(".m4a", ".wav")

    command = [
        "ffmpeg",
        "-i", input_path,
        "-ar", "16000",   # better for speech models
        "-ac", "1",       # mono channel
        output_path,
        "-y"
    ]

    subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    if not os.path.exists(output_path):
        raise Exception("FFmpeg conversion failed")

    return output_path


def transcribe_audio(file_path: str) -> str:
    """Send to Groq Whisper"""
    with open(file_path, "rb") as file:
        transcription = client.audio.transcriptions.create(
            file=(file_path, file.read()),
            model="whisper-large-v3-turbo",
            temperature=0,
            response_format="verbose_json",
        )

    return transcription.text


def cleanup_files(*paths):
    for path in paths:
        if path and os.path.exists(path):
            os.remove(path)


def process_base64_audio(audio_base64: str) -> str:
    input_path = None
    wav_path = None

    try:
        input_path = decode_base64_audio(audio_base64)
        wav_path = convert_to_wav(input_path)
        text = transcribe_audio(wav_path)
        return text

    except Exception as e:
        raise Exception(f"Processing failed: {str(e)}")

    finally:
        cleanup_files(input_path, wav_path)
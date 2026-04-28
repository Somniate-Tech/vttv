from groq import Groq
import json

client = Groq()

INTENTS = [
    "busTracking",
    "etaTracking",
    "childTracking",
    "busStatus",
    "routeInfo",
    "alerts",
    "systemSupport",
    "general"
]


def extract_intent(text: str) -> dict:
    prompt = f"""
You are an intent classification engine.

Classify the user input into EXACTLY one of these intents:
{INTENTS}

Rules:
- Return ONLY JSON
- No explanation
- Format: {{"intent": "<intent_name>"}}
- If unclear → return "general"

User Input:
{text}
"""

    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,  # important for consistency
        max_completion_tokens=100,
        top_p=1,
        stream=False
    )

    response_text = completion.choices[0].message.content.strip()

    try:
        return json.loads(response_text)
    except:
        return {"intent": "general"}
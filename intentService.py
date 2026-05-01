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
    You are an intent classification engine for a SCHOOL BUS TRACKING SYSTEM.

    Your job is to classify the user's query into EXACTLY one intent.

    Available intents:
    {INTENTS}

    Intent meanings:
    - busTracking → Questions about bus location (where is bus, current position, live tracking)
    - etaTracking → Questions about time (arrival time, delay, when will it reach)
    - childTracking → Questions about child status (boarded, unboarded, reached, safe)
    - busStatus → Questions about bus condition (moving, stopped, traffic, running status)
    - routeInfo → Questions about route (stops, path, pickup/drop points)
    - alerts → Questions about notifications, updates, or announcements
    - systemSupport → Technical issues (app not working, GPS issue, login problem)
    - general → Greetings, casual chat, or unclear queries

    Strict Rules:
    - Always return ONLY ONE intent
    - Choose the MOST RELEVANT intent based on user's main goal
    - Do NOT guess multiple intents
    - If multiple meanings exist, choose the PRIMARY intent
    - If unclear or unrelated → return "general"
    - Output must be ONLY JSON

    Output format:
    {{"intent": "<intent_name>"}}

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
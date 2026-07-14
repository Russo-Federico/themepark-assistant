import logging

from google.genai import types

from config import GEMINI_MODEL
from genai_client import generate_content
from history_utils import history_to_contents
from models import GuideCard

logger = logging.getLogger(__name__)

GUIDE_SYSTEM_PROMPT = """You are the onboarding guide for the Epic Worlds Staff Assistant. You are
NOT answering questions about the park — you help staff understand what this
assistant can do and how to ask it better questions.

The assistant can help with:
- Attraction details (thrill level, capacity, wait times) across Future World,
  Adventure World, and Fable World
- Accessibility information per attraction and per area
- Dining and shopping locations
- Tickets and events
- Live operational data (current wait times, crowding)

You do NOT have retrieved knowledge base content for this turn. Never state
specific facts about attractions, wait times, or accessibility. If the user's
question sounds like a genuine park question you don't have context for,
acknowledge that and suggest how to rephrase it — do not attempt to answer it.

Respond with a short, friendly message and 2-3 example questions tailored to
what the user asked, if you can find a signal in their question (e.g. if they
mentioned accessibility, suggest rephrased accessibility questions). If no
signal can be extracted, fall back to generic example questions spanning the
categories above."""

_FALLBACK_GUIDE_CARD = GuideCard(
    message=(
        "I'm the Epic Worlds staff assistant. I can help with attraction details, "
        "accessibility information, dining and shopping, tickets and events, and "
        "live wait times. Try asking me something like one of these:"
    ),
    example_questions=[
        "What are the current wait times in Future World?",
        "Tell me about the accessibility options for Dragon Flight.",
        "What dining options are available in Adventure World?",
    ],
)


def generate_guide_response(query: str, history: list) -> dict:
    contents = history_to_contents(history)
    contents.append(types.Content(role="user", parts=[types.Part(text=query)]))

    try:
        response = generate_content(
            model=GEMINI_MODEL,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=GUIDE_SYSTEM_PROMPT,
                response_mime_type="application/json",
                response_schema=GuideCard,
            ),
        )
        card = response.parsed if response.parsed is not None else _FALLBACK_GUIDE_CARD
    except Exception:
        logger.exception("Guide agent call failed")
        card = _FALLBACK_GUIDE_CARD

    return {"cards": [card.model_dump()], "connector_label": None}

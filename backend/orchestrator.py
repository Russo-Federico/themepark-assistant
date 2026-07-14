import logging

from google.genai import types

from config import GEMINI_MODEL
from genai_client import generate_content
from history_utils import history_to_contents
from models import FallbackCard, ResponsePayload
from tools.guide_tool import generate_guide_response
from tools.live_ops_tool import get_live_wait_times
from tools.rag_tool import search_knowledge_base

logger = logging.getLogger(__name__)

UNAVAILABLE_MESSAGE = "The assistant is temporarily unavailable. Please try again."
KB_UNAVAILABLE_MESSAGE = "Could not search the knowledge base. Please try again."

TOOL_SYSTEM_PROMPT = """You are an internal assistant for Epic Worlds theme park staff.
You answer questions about attractions, tickets, events, themed areas,
and accessibility only. Genuinely out-of-scope topics — HR, payroll, IT
support, scheduling, or anything unrelated to the park's guest-facing
operations — should be declined politely, suggesting the employee contact
the relevant department, without calling any tool.

For anything that's plausibly a park question, call search_knowledge_base
to check rather than guessing or declining outright, even if it's vaguely
phrased or doesn't name a specific attraction or category — e.g. "what's
happening for Fable Fest" or "anything special on this week" are both worth
a search attempt. The tool itself filters out irrelevant results and
returns nothing if the topic isn't actually covered, so calling it costs
nothing — never decline a plausible park question without having called
the tool first.

Use the search_knowledge_base tool to look up anything you need before
answering — call it once per distinct topic (e.g. call it twice if the
employee asks about two different attractions). Never invent information;
only state facts the tool actually returned. If the tool returns nothing
relevant, say so plainly rather than guessing.

Use the get_live_wait_times tool for questions about current wait times or
crowding.

If asked where to redirect guests from crowded attractions (a hybrid
question), call get_live_wait_times FIRST, identify the most crowded
attraction(s) from the result, then call search_knowledge_base to find
suitable alternatives elsewhere in the park — a different area, with a
similar or lower thrill level. Always call get_live_wait_times before
search_knowledge_base in this case, since the order you call tools in
determines the order information appears in the final answer."""

FORMAT_SYSTEM_PROMPT = """You are formatting the final answer for an Epic
Worlds staff assistant, based on tool results already gathered earlier in
this conversation. Turn that information into the structured response
schema. Use only facts present in those tool results — never invent
information. This applies to every field, including descriptive ones like
subtitle: if a subtitle isn't directly grounded in the retrieved text, leave
it out rather than inventing a description.

The gathered results fall into one of three shapes:
- Only live wait time results: produce a single live_ops card. For each
  attraction, bucket its raw wait_minutes into a level: under 20 minutes is
  low, 20 to 45 is med, over 45 is high.
- Only knowledge base results: produce one or more cards (attraction,
  accessibility, event, etc.) as usual.
- Both: produce the live_ops card first, then the knowledge-based card(s)
  after it, and set connector_label to a short phrase explaining the
  relationship (e.g. "Since it's busy, consider:"). Leave connector_label
  unset in both single-result cases above.

For attraction cards, use the "dots" field type for a 0-5 rating (e.g. thrill
level) and "number" for a prominent quantity worth calling out (e.g.
capacity), writing the unit inline in the value text (e.g.
"2,400 guests / hr"). Use "text" for everything else.

For event cards, put the full descriptive summary in description as prose —
not fields or stats — and use footer only for guest restrictions or add-on
costs, leaving it unset if there are none.

If the gathered results don't actually answer the employee's question,
respond with a single fallback card whose message politely says the
information isn't available and to contact Guest Services or the relevant
department."""

DEFAULT_FALLBACK_MESSAGE = (
    "I don't have reliable information on that. Please contact Guest Services "
    "or the relevant department."
)


def _fallback_response(message: str = DEFAULT_FALLBACK_MESSAGE) -> dict:
    return {"cards": [FallbackCard(message=message).model_dump()], "connector_label": None}


def _log_tool_trajectory(tool_history: list[types.Content]) -> None:
    for content in tool_history:
        for part in content.parts:
            if part.function_call:
                logger.info("  tool call: %s(%s)", part.function_call.name, dict(part.function_call.args or {}))
            if part.function_response:
                result = part.function_response.response
                if result.get("error"):
                    logger.info("  tool result: %s -> error: %s", part.function_response.name, result["error"])
                else:
                    count = len(result.get("result") or [])
                    logger.info("  tool result: %s -> %d item(s)", part.function_response.name, count)


def _found_relevant_results(tool_history: list[types.Content]) -> bool:
    for content in tool_history:
        for part in content.parts:
            if part.function_response and part.function_response.response.get("result"):
                return True
    return False


def _kb_search_failed(tool_history: list[types.Content]) -> bool:
    # The google-genai SDK's Automatic Function Calling catches exceptions
    # raised inside tool functions itself and never lets them propagate to
    # the generate_content() call site — it converts them into a
    # function_response with an "error" key instead. So a ChromaDB failure
    # inside search_knowledge_base can only be detected here, after the
    # call, not via try/except around Phase A.
    for content in tool_history:
        for part in content.parts:
            fr = part.function_response
            if fr and fr.name == "search_knowledge_base" and fr.response.get("error"):
                return True
    return False


def handle_query(query: str, history: list) -> dict:
    logger.info("query: %r", query)
    contents = history_to_contents(history)
    contents.append(types.Content(role="user", parts=[types.Part(text=query)]))

    try:
        tool_response = generate_content(
            model=GEMINI_MODEL,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=TOOL_SYSTEM_PROMPT,
                tools=[search_knowledge_base, get_live_wait_times],
                automatic_function_calling=types.AutomaticFunctionCallingConfig(maximum_remote_calls=3),
            ),
        )
    except Exception:
        logger.exception("Phase A tool-use turn failed")
        return _fallback_response(UNAVAILABLE_MESSAGE)

    tool_history = tool_response.automatic_function_calling_history
    if tool_history:
        _log_tool_trajectory(tool_history)
    else:
        logger.info("  no tools called")

    if tool_history and not _found_relevant_results(tool_history) and _kb_search_failed(tool_history):
        logger.info("  knowledge base search failed -> KB fallback")
        return _fallback_response(KB_UNAVAILABLE_MESSAGE)
    if not tool_history or not _found_relevant_results(tool_history):
        logger.info("  no relevant results -> routing to guide agent")
        return generate_guide_response(query, history)

    logger.info("  relevant results found -> formatting turn")
    format_contents = list(tool_history)
    format_contents.append(
        types.Content(
            role="user",
            parts=[types.Part(text="Now format your answer using the response schema.")],
        )
    )

    try:
        response = generate_content(
            model=GEMINI_MODEL,
            contents=format_contents,
            config=types.GenerateContentConfig(
                system_instruction=FORMAT_SYSTEM_PROMPT,
                response_mime_type="application/json",
                response_schema=ResponsePayload,
            ),
        )
    except Exception:
        logger.exception("Phase B formatting turn failed")
        return _fallback_response(UNAVAILABLE_MESSAGE)

    parsed: ResponsePayload | None = response.parsed
    if parsed is None:
        logger.info("  formatting turn returned no parsed response -> fallback")
        return _fallback_response(
            "I couldn't generate a valid response. Please try again or contact Guest Services."
        )
    logger.info("  produced cards: %s", [card.card_type for card in parsed.cards])
    return parsed.model_dump()

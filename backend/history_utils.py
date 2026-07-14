from google.genai import types


def history_to_contents(history: list) -> list[types.Content]:
    contents = []
    for entry in history:
        role = "model" if entry.role == "assistant" else "user"
        contents.append(types.Content(role=role, parts=[types.Part(text=entry.content)]))
    return contents

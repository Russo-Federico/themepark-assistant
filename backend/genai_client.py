import os
import time

from dotenv import load_dotenv
from google import genai
from google.genai import errors as genai_errors
from google.genai import types

from config import EMBEDDING_MODEL

load_dotenv()

_client: genai.Client | None = None

MAX_RETRIES = 3
BASE_DELAY_SECONDS = 1.0


def get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    return _client


def _is_retryable(exc: genai_errors.APIError) -> bool:
    if isinstance(exc, genai_errors.ServerError):
        return True
    return isinstance(exc, genai_errors.ClientError) and exc.code == 429


def _with_retry(fn, *args, **kwargs):
    for attempt in range(MAX_RETRIES + 1):
        try:
            return fn(*args, **kwargs)
        except genai_errors.APIError as exc:
            if attempt == MAX_RETRIES or not _is_retryable(exc):
                raise
            time.sleep(BASE_DELAY_SECONDS * (2**attempt))


def embed_documents(texts: list[str]) -> list[list[float]]:
    result = _with_retry(
        get_client().models.embed_content,
        model=EMBEDDING_MODEL,
        contents=texts,
        config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT"),
    )
    return [embedding.values for embedding in result.embeddings]


def embed_query(text: str) -> list[float]:
    result = _with_retry(
        get_client().models.embed_content,
        model=EMBEDDING_MODEL,
        contents=[text],
        config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY"),
    )
    return result.embeddings[0].values


def generate_content(**kwargs):
    return _with_retry(get_client().models.generate_content, **kwargs)

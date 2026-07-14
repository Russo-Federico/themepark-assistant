import logging

from fastmcp import FastMCP

from config import RETRIEVAL_TOP_K, SIMILARITY_THRESHOLD
from genai_client import embed_query
from pipeline.vector_store import get_collection

logger = logging.getLogger(__name__)

mcp = FastMCP("epic-worlds-rag")


class KnowledgeBaseUnavailableError(Exception):
    """Raised when the vector store can't be queried (e.g. ChromaDB failure)."""


@mcp.tool()
def search_knowledge_base(
    query: str,
    category: str | None = None,
    area: str | None = None,
    thrill_level: str | None = None,
) -> list[dict]:
    """Searches the Epic Worlds knowledge base for the most relevant passages
    for a natural-language query, optionally narrowed by metadata filters.
    Only passages that clear a similarity confidence threshold are returned —
    an empty list means nothing reliable enough was found, in which case do
    not guess or use outside knowledge.

    Call this once per distinct topic you need to look up (e.g. call it twice
    if comparing two different attractions).

    Args:
        query: The natural-language question or topic to search for.
        category: Optional filter. One of: "attractions", "accessibility",
            "tickets", "events", "area_guide".
        area: Optional filter. One of: "future_world", "adventure_world",
            "fable_world", "park_wide".
        thrill_level: Optional filter. One of: "low", "moderate", "high",
            "very_high".
    """
    conditions = []
    if category:
        conditions.append({"category": category})
    if area:
        conditions.append({"area": area})
    if thrill_level:
        conditions.append({"thrill_level": thrill_level})

    where = None
    if len(conditions) == 1:
        where = conditions[0]
    elif len(conditions) > 1:
        where = {"$and": conditions}

    try:
        collection = get_collection()
        query_embedding = embed_query(query)
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=RETRIEVAL_TOP_K,
            where=where,
        )
    except Exception as exc:
        logger.exception("Knowledge base search failed")
        raise KnowledgeBaseUnavailableError("Failed to query the knowledge base") from exc

    if not results["ids"][0]:
        return []

    chunks = []
    for chunk_id, text, metadata, distance in zip(
        results["ids"][0],
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        similarity = 1 - distance
        if similarity < SIMILARITY_THRESHOLD:
            continue
        chunks.append(
            {
                "chunk_id": chunk_id,
                "text": text,
                "similarity": similarity,
                **metadata,
            }
        )
    return chunks

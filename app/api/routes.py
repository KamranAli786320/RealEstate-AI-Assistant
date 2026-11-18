
import logging

from fastapi import APIRouter, HTTPException, Query

from app.retrieval.catalog_search import search_catalog
from app.services.response_builder import build_chat_response
from app.llm.openrouter_client import generate_answer

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/health")
def health_check() -> dict:
    return {
        "status": "success",
        "message": "Real Estate AI Assistant API is running",
    }


@router.get("/search")
def search_properties(
    q: str = Query(..., min_length=1),
    limit: int = Query(5, ge=1, le=20),
) -> dict:
    try:
        results = search_catalog(q, limit)

        return {
            "status": "success",
            "query": q,
            "count": len(results),
            "results": results,
        }

    except Exception:
        logger.exception("Property search failed")
        raise HTTPException(
            status_code=500,
            detail="Property search failed.",
        )


@router.get("/chat")
def chat(
    message: str = Query(..., min_length=2),
) -> dict:
    try:
        results = search_catalog(message, limit=5)

        if not results:
            return {
                "status": "success",
                "answer": build_chat_response(message, results),
                "answer_source": "local",
                "count": 0,
                "results": [],
            }

        try:
            answer = generate_answer(message, results)
            answer_source = "openrouter"

        except Exception:
            logger.exception(
                "OpenRouter failed. Using local fallback."
            )
            answer = build_chat_response(message, results)
            answer_source = "local_fallback"

        return {
            "status": "success",
            "answer": answer,
            "answer_source": answer_source,
            "count": len(results),
            "results": results,
        }

    except Exception:
        logger.exception("Chat request failed")
        raise HTTPException(
            status_code=500,
            detail="Chat request failed.",
        )

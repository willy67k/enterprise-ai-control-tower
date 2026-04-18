import logging

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.middleware.auth import verify_dev_token
from app.schemas.chat import ChatRequest, ChatResponse
from app.tools.llm.errors import LLMConfigurationError
from app.tools.llm.invoke import chat as invoke_llm

logger = logging.getLogger(__name__)

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def post_chat(
    body: ChatRequest,
    _: None = Depends(verify_dev_token),
) -> ChatResponse:
    """Single-turn chat using OpenAI, Gemini, or Anthropic (see body.provider)."""
    try:
        reply, model_used, provider_used = invoke_llm(
            body.prompt,
            provider=body.provider,
            model=body.model,
        )
    except LLMConfigurationError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e),
        ) from e
    except Exception:
        logger.exception("LLM invocation failed")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="LLM request failed",
        ) from None
    return ChatResponse(
        reply=reply,
        model=model_used,
        provider=provider_used,
    )

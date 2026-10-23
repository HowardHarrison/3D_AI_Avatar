"""Interactive chatbot turn routes. Thin layer — orchestration stays in services."""

from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_chat_service
from app.api.schemas import ChatTurnRequest, ChatTurnResponse
from app.core.exceptions import (
    ChatValidationError,
    LlmConfigurationError,
    LlmProviderError,
)
from app.services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/turns", response_model=ChatTurnResponse)
def post_chat_turn(
    body: ChatTurnRequest,
    service: ChatService = Depends(get_chat_service),
) -> ChatTurnResponse:
    """
    Run one chat turn: user ``message`` (+ optional ``history``) → ``reply``.

    ``history`` is prior turns only (not the current ``message``).
    """
    try:
        history = [(item.role, item.content) for item in body.history]
        reply = service.send_turn(body.message, history=history)
    except ChatValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except LlmConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except LlmProviderError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return ChatTurnResponse(reply=reply)

"""
EduTrack AI Chat endpoint.

POST /api/v1/ai/chat
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from .. import models
from ..database import get_db
from ..auth import get_current_user, require_student
from ..services import build_student_context, ATTENDANCE_THRESHOLD
from ..services.ai_chat import (
    chat,
    check_ollama_health,
    OllamaUnavailableError,
    OllamaModelMissingError,
)

router = APIRouter()


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    success: bool
    message: str
    ai_available: bool = True


@router.post("/chat", response_model=ChatResponse)
async def ai_chat(
    req: ChatRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_student),
):
    """
    Student asks a question → backend gathers real data → Ollama responds.
    """
    # Build structured context from real DB data
    context = build_student_context(db, current_user, ATTENDANCE_THRESHOLD)

    try:
        response_text = await chat(req.message, context)
        return ChatResponse(success=True, message=response_text, ai_available=True)
    except OllamaUnavailableError as e:
        return ChatResponse(success=False, message=str(e), ai_available=False)
    except OllamaModelMissingError as e:
        return ChatResponse(success=False, message=str(e), ai_available=False)
    except Exception as e:
        return ChatResponse(
            success=False,
            message="An unexpected error occurred with the AI service.",
            ai_available=False,
        )


@router.get("/health")
async def ai_health():
    """Check if Ollama is reachable."""
    available = await check_ollama_health()
    return {"ai_available": available}

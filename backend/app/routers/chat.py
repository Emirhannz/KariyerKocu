"""
KariyerKoçu - Chat Router
=========================
Chatbot API endpoint'leri.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService
from app.utils.jwt import get_current_user


router = APIRouter()


@router.get(
    "/greeting",
    summary="Karşılama Mesajı",
    description="Kullanıcıya özel karşılama mesajı döndür."
)
async def get_greeting(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Chatbot karşılama mesajını getir."""
    service = ChatService(db, current_user)
    greeting = service.get_greeting()
    return {"greeting": greeting}


@router.post(
    "/message",
    response_model=ChatResponse,
    summary="Mesaj Gönder",
    description="Chatbot'a mesaj gönder ve cevap al."
)
async def send_message(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Kullanıcı mesajını işle ve cevap döndür."""
    service = ChatService(db, current_user)
    
    # History'yi dict listesine çevir
    history = [{"role": m.role, "content": m.content} for m in request.history]
    
    result = await service.process_message(
        message=request.message,
        history=history
    )
    
    return ChatResponse(
        response=result["response"],
        context_used=result["context_used"]
    )

"""
KariyerKoçu - Chat Schemas
==========================
Chatbot API için Pydantic şemaları.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class ChatMessageItem(BaseModel):
    """Tek bir chat mesajı."""
    role: str = Field(..., description="Mesaj rolü: 'user' veya 'assistant'")
    content: str = Field(..., description="Mesaj içeriği")


class ChatRequest(BaseModel):
    """Chat isteği."""
    message: str = Field(..., min_length=1, description="Kullanıcı mesajı")
    history: List[ChatMessageItem] = Field(default_factory=list, description="Önceki mesajlar")


class ChatResponse(BaseModel):
    """Chat yanıtı."""
    response: str = Field(..., description="Asistan cevabı")
    context_used: Optional[str] = Field(None, description="Kullanılan context tipi")

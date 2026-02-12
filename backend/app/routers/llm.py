"""
KariyerKoçu - LLM Router
========================
LLM test endpoint'leri.

Bu router geliştirme ve test amaçlıdır.
Production'da kaldırılabilir veya admin-only yapılabilir.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.services.llm_service import llm_service


router = APIRouter()


# ============================================================================
# ŞEMALAR
# ============================================================================

class ChatRequest(BaseModel):
    """Basit chat isteği."""
    message: str
    system_prompt: Optional[str] = None


class ChatResponse(BaseModel):
    """Chat cevabı."""
    response: str
    model: str


class InterviewQuestionRequest(BaseModel):
    """Mülakat sorusu isteği."""
    position: str
    difficulty: str = "orta"


class InterviewQuestionResponse(BaseModel):
    """Mülakat sorusu cevabı."""
    question: str
    position: str
    difficulty: str


# ============================================================================
# ENDPOINT'LER
# ============================================================================

@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="LLM ile sohbet",
    description="io Intelligence API'ye mesaj gönder ve cevap al."
)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    LLM ile basit sohbet.
    
    Test için kullanılır:
    - API bağlantısını test et
    - Model cevaplarını gör
    """
    try:
        response = await llm_service.chat(
            message=request.message,
            system_prompt=request.system_prompt,
        )
        
        return ChatResponse(
            response=response,
            model=llm_service.default_model,
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"LLM API hatası: {str(e)}"
        )


@router.get(
    "/test",
    summary="API bağlantı testi",
    description="io Intelligence API'nin çalışıp çalışmadığını kontrol et."
)
async def test_connection():
    """
    Basit bağlantı testi.
    
    "Merhaba" deyip cevap alıyoruz.
    Çalışıyorsa API key ve bağlantı doğru demektir.
    """
    try:
        response = await llm_service.chat(
            message="Merhaba! Sadece 'Bağlantı başarılı!' yaz.",
            temperature=0.1,
            max_tokens=50,
        )
        
        return {
            "status": "success",
            "message": "io Intelligence API bağlantısı başarılı!",
            "model": llm_service.default_model,
            "llm_response": response,
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Bağlantı hatası: {str(e)}",
            "model": llm_service.default_model,
        }


@router.post(
    "/interview-question",
    response_model=InterviewQuestionResponse,
    summary="Mülakat sorusu üret",
    description="Belirtilen pozisyon ve zorluk için mülakat sorusu üret."
)
async def generate_interview_question(
    request: InterviewQuestionRequest
) -> InterviewQuestionResponse:
    """
    Mülakat sorusu üret.
    
    Örnek:
    - position: "Backend Developer"
    - difficulty: "orta"
    """
    try:
        question = await llm_service.generate_interview_question(
            position=request.position,
            difficulty=request.difficulty,
        )
        
        return InterviewQuestionResponse(
            question=question,
            position=request.position,
            difficulty=request.difficulty,
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Soru üretme hatası: {str(e)}"
        )

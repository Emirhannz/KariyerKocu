"""
KariyerKoçu - Sesli Mülakat Router
==================================
Sesli mülakat API endpoint'leri.
Edge-TTS ile soru okuma, Groq STT ile cevap alma.
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import io

from app.database import get_db
from app.models.user import User
from app.routers.auth import get_current_user
from app.services.tts_service import tts_service
from app.services.speech_service import speech_service
from app.services.interview_service import interview_service


router = APIRouter()


# ============================================================================
# MODELS
# ============================================================================

class TTSRequest(BaseModel):
    """TTS isteği."""
    text: str
    voice_gender: str = "male"  # "male" veya "female"


class VoiceInterviewConfig(BaseModel):
    """Sesli mülakat konfigürasyonu."""
    voice_gender: str = "male"  # "male" veya "female"


# ============================================================================
# SES OKUMA (TTS)
# ============================================================================

@router.post("/tts")
async def generate_speech(
    request: TTSRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Metni sese çevir (Edge-TTS).
    
    Teknik terimler otomatik olarak Türkçe telaffuza çevrilir.
    Örn: "Python" → "Paytın" olarak okunur.
    """
    result = await tts_service.generate_speech(
        text=request.text,
        voice_gender=request.voice_gender,
        apply_tech_pronunciation=True
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get("error", "TTS hatası")
        )
    
    # MP3 olarak döndür
    audio_stream = io.BytesIO(result["audio_bytes"])
    
    return StreamingResponse(
        audio_stream,
        media_type="audio/mpeg",
        headers={
            "Content-Disposition": "inline; filename=speech.mp3"
        }
    )


@router.post("/tts/question/{session_id}")
async def generate_question_speech(
    session_id: str,
    voice_gender: str = "male",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Mevcut soruyu sesli oku.
    
    Session'daki aktif soruyu bulup ses dosyası olarak döner.
    """
    from app.models.interview import InterviewSession, InterviewQuestion
    
    # Session'ı bul
    session = db.query(InterviewSession).filter(
        InterviewSession.id == session_id,
        InterviewSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mülakat oturumu bulunamadı"
        )
    
    # Son soruyu bul
    question = db.query(InterviewQuestion).filter(
        InterviewQuestion.session_id == session.id
    ).order_by(InterviewQuestion.id.desc()).first()
    
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Soru bulunamadı"
        )
    
    # TTS için question_text kullan
    # TTS service kendi sözlüğü ile İngilizce terimleri Türkçe fonetik yazıma çevirecek
    tts_text = question.question_text
    
    # Soruyu sesli oku - TTS service kendi 1500 kelimelik sözlüğünü kullanacak
    result = await tts_service.generate_speech(
        text=tts_text,
        voice_gender=voice_gender,
        apply_tech_pronunciation=True  # TTS service kendi sözlüğünü kullansın
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get("error", "TTS hatası")
        )
    
    audio_stream = io.BytesIO(result["audio_bytes"])
    
    return StreamingResponse(
        audio_stream,
        media_type="audio/mpeg",
        headers={
            "Content-Disposition": "inline; filename=question.mp3"
        }
    )


# ============================================================================
# SES TANIMA (STT)
# ============================================================================

@router.post("/stt")
async def transcribe_speech(
    audio: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Ses dosyasını metne çevir (Groq Whisper-large-v3).
    
    Teknik terimler (Docker, Python, vb.) doğru tanınır.
    """
    # Dosyayı oku
    audio_bytes = await audio.read()
    
    # Boyut kontrolü (max 25MB)
    if len(audio_bytes) > 25 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ses dosyası çok büyük (max 25MB)"
        )
    
    # Transkript
    result = await speech_service.transcribe_audio(
        audio_bytes=audio_bytes,
        filename=audio.filename or "audio.wav",
        use_tech_prompt=True
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get("error", "STT hatası")
        )
    
    return {
        "text": result["text"],
        "success": True
    }


@router.post("/voice-answer/{session_id}")
async def submit_voice_answer(
    session_id: str,
    audio: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Sesli cevap gönder.
    
    1. Ses → Metin (Groq STT)
    2. Cevabı değerlendir
    3. Değerlendirmeyi sesli döndür (opsiyonel)
    """
    from app.models.interview import InterviewSession, InterviewQuestion, InterviewAnswer
    
    # Session'ı bul
    session = db.query(InterviewSession).filter(
        InterviewSession.id == session_id,
        InterviewSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mülakat oturumu bulunamadı"
        )
    
    if session.status != "in_progress":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mülakat aktif değil"
        )
    
    # Son cevaplanmamış soruyu bul
    question = db.query(InterviewQuestion).filter(
        InterviewQuestion.session_id == session.id,
        InterviewQuestion.is_answered == False
    ).order_by(InterviewQuestion.id.asc()).first()
    
    # Eğer cevaplanmamış soru yoksa, en son soruyu al (fallback)
    if not question:
        question = db.query(InterviewQuestion).filter(
            InterviewQuestion.session_id == session.id
        ).order_by(InterviewQuestion.id.desc()).first()
    
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cevaplanacak soru bulunamadı"
        )
    
    # Zaten cevaplanmış mı kontrol et
    if question.is_answered:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu soru zaten cevaplanmış. Yeni soru almak için /question endpoint'ini kullanın."
        )
    
    # Ses → Metin
    audio_bytes = await audio.read()
    
    stt_result = await speech_service.transcribe_audio(
        audio_bytes=audio_bytes,
        filename=audio.filename or "audio.wav",
        use_tech_prompt=True
    )
    
    if not stt_result["success"]:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ses tanıma hatası: {stt_result.get('error')}"
        )
    
    answer_text = stt_result["text"]
    
    # Cevabı değerlendir ve kaydet
    # NOT: evaluate_answer zaten cevabı veritabanına kaydediyor,
    # burada tekrar kaydetmeye gerek yok (duplicate answer hatası önlendi)
    evaluation = await interview_service.evaluate_answer(
        question=question,
        user_answer=answer_text,
        session=session,
        db=db
    )
    
    # Session'ı yenile (evaluate_answer commit yaptığı için)
    db.refresh(session)
    db.refresh(question)
    
    # NOT: current_question_number burada artırılmaz!
    # Çünkü interview_service.generate_question() zaten yeni soru üretirken artırıyor.
    # Burada artırırsak çift artış olur ve mülakat erken biter.
    
    return {
        "success": True,
        "transcribed_text": answer_text,
        "evaluation": {
            "score": evaluation.get("score", 0),
            "feedback": evaluation.get("feedback", ""),
        },
        "current_question": session.current_question_number,
        "total_questions": session.total_questions,
        "is_complete": session.current_question_number >= session.total_questions
    }


# ============================================================================
# YARDIMCI
# ============================================================================

@router.get("/voices")
async def get_available_voices():
    """Mevcut Türkçe sesleri listele."""
    return tts_service.get_available_voices()


@router.post("/tts/feedback")
async def generate_feedback_speech(
    request: TTSRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Değerlendirme metnini sesli oku.
    
    Mülakat sonrasında veya ara değerlendirmelerde kullanılır.
    """
    result = await tts_service.generate_speech(
        text=request.text,
        voice_gender=request.voice_gender,
        apply_tech_pronunciation=True
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get("error", "TTS hatası")
        )
    
    audio_stream = io.BytesIO(result["audio_bytes"])
    
    return StreamingResponse(
        audio_stream,
        media_type="audio/mpeg",
        headers={
            "Content-Disposition": "inline; filename=feedback.mp3"
        }
    )

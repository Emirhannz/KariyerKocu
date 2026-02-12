"""
KariyerKoçu - Mülakat Şemaları
==============================
Mülakat API'si için request/response modelleri.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# ============================================================================
# CONFIG ENDPOINT'LERİ İÇİN
# ============================================================================

class SectorOption(BaseModel):
    """Dropdown için sektör seçeneği."""
    id: str
    name: str

class PositionOption(BaseModel):
    """Dropdown için pozisyon seçeneği."""
    id: str
    name: str

class ExperienceOption(BaseModel):
    """Dropdown için tecrübe seçeneği."""
    id: str
    name: str

class InterviewTypeOption(BaseModel):
    """Dropdown için mülakat tipi seçeneği."""
    id: str
    name: str
    description: str

class InterviewConfigResponse(BaseModel):
    """Mülakat config verisi."""
    sectors: List[SectorOption]
    positions: Dict[str, List[PositionOption]]  # sector_id -> positions
    experience_levels: List[ExperienceOption]
    interview_types: List[InterviewTypeOption]


# ============================================================================
# MÜLAKAT BAŞLATMA
# ============================================================================

class StartInterviewRequest(BaseModel):
    """Mülakat başlatma isteği."""
    
    company_sector: str = Field(
        ...,
        description="Firma sektörü ID",
        example="yazilim"
    )
    position: str = Field(
        ...,
        description="Başvurulan pozisyon ID",
        example="backend_developer"
    )
    experience_level: str = Field(
        ...,
        description="Aranan tecrübe seviyesi ID",
        example="junior"
    )
    interview_type: str = Field(
        ...,
        description="Mülakat tipi: sektorel veya sektor_yorum",
        example="sektor_yorum"
    )
    question_count: int = Field(
        default=5,
        ge=1,
        le=7,
        description="Soru sayısı (1-7)"
    )
    voice_gender: Optional[str] = Field(
        default="male",
        description="Sesli mülakat için ses cinsiyeti: male veya female"
    )
    interview_mode: Optional[str] = Field(
        default="text",
        description="Mülakat modu: text veya voice"
    )

class StartInterviewResponse(BaseModel):
    """Mülakat başlatma yanıtı."""
    session_id: str
    message: str
    total_questions: int
    interview_settings: Dict[str, str]


# ============================================================================
# SORU ALMA
# ============================================================================

class QuestionResponse(BaseModel):
    """Mülakat sorusu yanıtı."""
    session_id: str
    question_id: str
    question_number: int
    total_questions: int
    
    # Soru bilgileri
    transition_text: Optional[str] = Field(
        None,
        description="Önceki cevaba bağlantılı geçiş cümlesi"
    )
    transition_tts: Optional[str] = Field(
        None,
        description="Geçiş cümlesinin TTS için Türkçe telaffuz versiyonu"
    )
    question_text: str
    question_tts: Optional[str] = Field(
        None,
        description="Sorunun TTS için Türkçe telaffuz versiyonu (Deepfake→Dipfeyk)"
    )
    question_type: str
    
    # Durum
    is_last_question: bool = False


# ============================================================================
# CEVAP GÖNDERME
# ============================================================================

class SubmitAnswerRequest(BaseModel):
    """Cevap gönderme isteği."""
    session_id: str = Field(..., description="Mülakat oturum ID")
    question_id: str = Field(..., description="Soru ID")
    answer: str = Field(
        ...,
        min_length=10,
        description="Kullanıcının cevabı (min 10 karakter)"
    )

class SubmitAnswerResponse(BaseModel):
    """Cevap gönderme yanıtı."""
    message: str
    question_number: int
    has_next_question: bool
    next_question_available: bool = True


# ============================================================================
# MÜLAKAT BİTİRME
# ============================================================================

class CompleteInterviewResponse(BaseModel):
    """Mülakat bitirme yanıtı."""
    session_id: str
    message: str
    total_questions: int
    answered_questions: int
    redirect_url: str = Field(
        default="/interview/report",
        description="Rapor sayfasına yönlendirme"
    )


# ============================================================================
# RAPOR
# ============================================================================

class QuestionReport(BaseModel):
    """Tek soru için rapor."""
    question_number: int
    question_type: str
    question_text: str
    
    user_answer: str
    score: int = Field(..., ge=1, le=10)
    evaluation_reason: str
    ideal_answer: Optional[str] = None
    strengths: List[str] = []
    weaknesses: List[str] = []

class InterviewReportResponse(BaseModel):
    """Mülakat sonuç raporu."""
    
    # Meta bilgiler
    session_id: str
    completed_at: datetime
    duration_minutes: Optional[int] = None
    
    # Mülakat ayarları
    company_sector: str
    company_sector_name: str
    position: str
    position_name: str
    experience_level: str
    experience_level_name: str
    interview_type: str
    
    # Genel skorlar
    total_questions: int
    answered_questions: int
    average_score: float = Field(..., ge=0, le=10)
    passing_score: float = 6.0
    passed: bool
    
    # Soru bazlı detaylar
    questions: List[QuestionReport]
    
    # Özet
    overall_strengths: List[str] = Field(
        default_factory=list,
        description="Genel güçlü yönler"
    )
    overall_weaknesses: List[str] = Field(
        default_factory=list,
        description="Geliştirilmesi gereken alanlar"
    )
    recommendation: Optional[str] = Field(
        None,
        description="Genel tavsiye metni"
    )


# ============================================================================
# GEÇMİŞ MÜLAKATLAR
# ============================================================================

class InterviewHistoryItem(BaseModel):
    """Geçmiş mülakat özeti."""
    session_id: str
    position_name: str
    company_sector_name: str
    experience_level_name: str
    average_score: Optional[float]
    passed: Optional[bool]
    status: str
    created_at: datetime
    completed_at: Optional[datetime]

class InterviewHistoryResponse(BaseModel):
    """Geçmiş mülakatlar listesi."""
    total_count: int
    interviews: List[InterviewHistoryItem]

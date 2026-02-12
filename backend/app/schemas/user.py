"""
KariyerKoçu - User Schemas
==========================
API request/response için Pydantic şemaları.

ÖĞRENME NOKTASI:
- Pydantic modelleri vs SQLAlchemy modelleri farkı
- Input validation (email format, şifre uzunluğu)
- Request ve Response şemalarını ayırma
- orm_mode ile SQLAlchemy → Pydantic dönüşümü
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict


# ============================================================================
# REQUEST ŞEMALARI (API'ye gelen veriler)
# ============================================================================

class UserRegisterRequest(BaseModel):
    """
    Kayıt isteği şeması.
    
    Örnek JSON:
    {
        "email": "ahmet@example.com",
        "password": "güçlü_şifre_123",
        "full_name": "Ahmet Yılmaz"
    }
    """
    email: EmailStr = Field(
        ...,  # ... = zorunlu alan
        description="Geçerli bir email adresi",
        examples=["ahmet@example.com"]
    )
    password: str = Field(
        ...,
        min_length=6,
        max_length=100,
        description="En az 6 karakter şifre",
        examples=["güçlü_şifre_123"]
    )
    full_name: Optional[str] = Field(
        None,
        max_length=100,
        description="Ad soyad (opsiyonel)",
        examples=["Ahmet Yılmaz"]
    )


class UserLoginRequest(BaseModel):
    """
    Giriş isteği şeması.
    
    Örnek JSON:
    {
        "email": "ahmet@example.com",
        "password": "güçlü_şifre_123"
    }
    """
    email: EmailStr = Field(
        ...,
        description="Kayıtlı email adresi"
    )
    password: str = Field(
        ...,
        description="Şifre"
    )


# ============================================================================
# RESPONSE ŞEMALARI (API'den dönen veriler)
# ============================================================================

class UserResponse(BaseModel):
    """
    Kullanıcı bilgileri response şeması.
    
    NOT: password ASLA döndürülmez!
    """
    id: str
    email: str
    full_name: Optional[str] = None
    is_active: bool
    created_at: datetime
    
    # Pydantic v2 için ConfigDict kullanıyoruz
    model_config = ConfigDict(
        from_attributes=True  # SQLAlchemy model → Pydantic dönüşümü için
    )


class TokenResponse(BaseModel):
    """
    JWT token response şeması.
    
    Örnek JSON:
    {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "token_type": "bearer"
    }
    """
    access_token: str = Field(
        ...,
        description="JWT access token"
    )
    token_type: str = Field(
        default="bearer",
        description="Token tipi (her zaman 'bearer')"
    )


class LoginResponse(BaseModel):
    """
    Giriş başarılı response şeması.
    
    Token + kullanıcı bilgileri birlikte döner.
    """
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class MessageResponse(BaseModel):
    """
    Basit mesaj response şeması.
    
    Örnek: {"message": "Kayıt başarılı!"}
    """
    message: str


# ============================================================================
# PROFİL VE DASHBOARD ŞEMALARI
# ============================================================================

class CareerGoals(BaseModel):
    """Kariyer hedefi bilgileri."""
    target_sector: Optional[str] = Field(None, description="Hedef sektör ID")
    target_sector_name: Optional[str] = Field(None, description="Hedef sektör adı")
    target_position: Optional[str] = Field(None, description="Hedef pozisyon ID")
    target_position_name: Optional[str] = Field(None, description="Hedef pozisyon adı")
    experience_level: Optional[str] = Field(None, description="Tecrübe seviyesi ID")
    experience_level_name: Optional[str] = Field(None, description="Tecrübe seviyesi adı")


class UpdateCareerGoalsRequest(BaseModel):
    """Kariyer hedefi güncelleme isteği."""
    target_sector: Optional[str] = Field(None, description="Hedef sektör ID")
    target_position: Optional[str] = Field(None, description="Hedef pozisyon ID")
    experience_level: Optional[str] = Field(None, description="Tecrübe seviyesi ID")


class UpdateProfileRequest(BaseModel):
    """Profil güncelleme isteği."""
    full_name: Optional[str] = Field(None, max_length=100, description="Ad soyad")
    phone: Optional[str] = Field(None, max_length=20, description="Telefon numarası")


class ChangePasswordRequest(BaseModel):
    """Şifre değiştirme isteği."""
    current_password: str = Field(..., description="Mevcut şifre")
    new_password: str = Field(..., min_length=6, max_length=100, description="Yeni şifre (en az 6 karakter)")


class UserProfileResponse(BaseModel):
    """Profil yanıtı."""
    
    # Temel bilgiler
    id: str
    email: str
    full_name: Optional[str] = None
    phone: Optional[str] = None
    created_at: datetime
    
    # CV durumu
    has_cv: bool = False
    cv_filename: Optional[str] = None
    cv_uploaded_at: Optional[datetime] = None
    
    # Kariyer hedefi
    career_goals: CareerGoals


class CVSummary(BaseModel):
    """CV özet bilgisi."""
    is_uploaded: bool = False
    filename: Optional[str] = None
    full_name: Optional[str] = None
    skills_count: int = 0
    projects_count: int = 0
    uploaded_at: Optional[datetime] = None


class AnalysisSummary(BaseModel):
    """Son analiz özeti."""
    has_analysis: bool = False
    last_analysis_date: Optional[datetime] = None
    strongest_field: Optional[str] = None
    strongest_field_name: Optional[str] = None
    strongest_score: Optional[int] = None
    total_analyses: int = 0


class InterviewSummary(BaseModel):
    """Son mülakat özeti."""
    has_interview: bool = False
    last_interview_date: Optional[datetime] = None
    last_position: Optional[str] = None
    last_score: Optional[float] = None
    passed: Optional[bool] = None
    total_interviews: int = 0
    # Aktif mülakat bilgisi
    has_active_interview: bool = False
    active_session_id: Optional[str] = None


class DashboardResponse(BaseModel):
    """Dashboard ana sayfa verisi."""
    
    # Kullanıcı bilgisi
    user_name: Optional[str] = None
    email: str
    member_since: datetime
    
    # Kariyer hedefi
    career_goals: CareerGoals
    has_career_goals: bool = False
    
    # CV durumu
    cv: CVSummary
    
    # Son analiz
    analysis: AnalysisSummary
    
    # Son mülakat
    interview: InterviewSummary
    
    # Hızlı eylemler (frontend için)
    suggested_actions: list = Field(
        default_factory=list,
        description="Kullanıcıya önerilen sonraki adımlar"
    )


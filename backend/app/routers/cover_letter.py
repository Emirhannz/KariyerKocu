# -*- coding: utf-8 -*-
"""
Önyazı ve E-mail Oluşturma Router v2
=====================================
Akıllı cover letter ve başvuru e-maili endpoint'leri.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List

from app.database import get_db
from app.models.user import User
from app.models.cv import CV
from app.routers.auth import get_current_user
from app.services.cover_letter_service import cover_letter_service


router = APIRouter()


# ============================================================================
# SCHEMAS
# ============================================================================

class SmartCoverLetterRequest(BaseModel):
    """Akıllı önyazı oluşturma isteği."""
    company_name: str
    position_title: str
    position_type: str  # intern, long_intern, junior, mid, senior
    sector: str  # defense, fintech, ecommerce, startup, corporate, tech
    style: Optional[str] = "professional"  # professional, friendly, direct
    length: Optional[str] = "medium"  # short, medium, long
    company_note: Optional[str] = None  # Firmaya özel not
    job_description: Optional[str] = None  # İlan metni (opsiyonel)


class SmartEmailRequest(BaseModel):
    """Akıllı e-mail oluşturma isteği."""
    company_name: str
    position_title: str
    position_type: str  # intern, long_intern, junior, mid, senior
    sector: str  # defense, fintech, ecommerce, startup, corporate, tech
    style: Optional[str] = "professional"
    length: Optional[str] = "medium"  # short, medium, long
    company_note: Optional[str] = None


class CoverLetterResponse(BaseModel):
    """Önyazı response."""
    success: bool
    cover_letter: str = ""
    word_count: int = 0
    profile_type: str = ""
    sector: str = ""
    tips: List[str] = []
    error: Optional[str] = None


class EmailResponse(BaseModel):
    """E-mail response."""
    success: bool
    subject: str = ""
    body: str = ""
    profile_type: str = ""
    tips: List[str] = []
    error: Optional[str] = None


class OptionsResponse(BaseModel):
    """Dropdown seçenekleri."""
    position_types: List[dict]
    sectors: List[dict]
    styles: List[dict]
    lengths: List[dict] = []


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.get(
    "/options",
    response_model=OptionsResponse,
    summary="Form Seçeneklerini Getir",
    description="Dropdown'lar için pozisyon tipi, sektör ve stil seçeneklerini döndürür."
)
async def get_options():
    """Form için seçenekleri döndür."""
    position_types = [
        {"value": "intern", "label": "Stajyer", "description": "Staj pozisyonları için"},
        {"value": "long_intern", "label": "Uzun Dönem Stajyer", "description": "6+ ay staj pozisyonları"},
        {"value": "junior", "label": "Junior", "description": "Yeni mezun / 0-2 yıl tecrübe"},
        {"value": "mid", "label": "Mid-Level", "description": "3-5 yıl tecrübe"},
        {"value": "senior", "label": "Senior", "description": "5+ yıl tecrübe"},
    ]
    
    sectors = [
        {"value": "tech", "label": "Teknoloji Şirketi", "description": "Yazılım, SaaS, Tech"},
        {"value": "startup", "label": "Startup", "description": "Erken aşama, dinamik ortam"},
        {"value": "ecommerce", "label": "E-ticaret", "description": "Online retail, marketplace"},
        {"value": "fintech", "label": "Fintech / Bankacılık", "description": "Finansal teknolojiler"},
        {"value": "defense", "label": "Savunma Sanayii", "description": "Savunma, havacılık, uzay"},
        {"value": "corporate", "label": "Kurumsal / Büyük Şirket", "description": "Holding, büyük firmalar"},
    ]
    
    styles = [
        {"value": "professional", "label": "Profesyonel", "description": "Resmi ve kurumsal ton"},
        {"value": "friendly", "label": "Samimi", "description": "Sıcak ama profesyonel"},
        {"value": "direct", "label": "Direkt", "description": "Kısa ve öz"},
    ]
    
    lengths = [
        {"value": "short", "label": "Kısa", "description": "150-200 kelime - Hızlı başvurular için"},
        {"value": "medium", "label": "Orta", "description": "250-350 kelime - Standart"},
        {"value": "long", "label": "Uzun", "description": "400-500 kelime - Detaylı başvurular için"},
    ]
    
    return OptionsResponse(
        position_types=position_types,
        sectors=sectors,
        styles=styles,
        lengths=lengths
    )


@router.post(
    "/cover-letter",
    response_model=CoverLetterResponse,
    summary="Akıllı Önyazı Oluştur",
    description="CV'nize ve seçimlerinize göre profil-bilinçli önyazı oluşturur."
)
async def generate_smart_cover_letter(
    request: SmartCoverLetterRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Akıllı önyazı oluştur.
    
    Profil tipine göre gerçekçi bir önyazı üretir.
    Stajyer için "10 yıllık deneyim" gibi saçmalıklar yapmaz.
    """
    cv = db.query(CV).filter(CV.user_id == current_user.id).first()
    
    if not cv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Önce CV yüklemeniz gerekiyor"
        )
    
    cv_data = _cv_to_dict(cv, current_user)
    
    result = await cover_letter_service.generate_smart_cover_letter(
        cv_data=cv_data,
        company_name=request.company_name,
        position_title=request.position_title,
        position_type=request.position_type,
        sector=request.sector,
        style=request.style or "professional",
        length=request.length or "medium",
        company_note=request.company_note,
        job_description=request.job_description
    )
    
    return CoverLetterResponse(**result)


@router.post(
    "/email",
    response_model=EmailResponse,
    summary="Akıllı E-mail Oluştur",
    description="CV'nize ve seçimlerinize göre profil-bilinçli başvuru e-maili oluşturur."
)
async def generate_smart_email(
    request: SmartEmailRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Akıllı e-mail oluştur.
    
    Kısa, öz ve profesyonel başvuru e-maili üretir.
    """
    cv = db.query(CV).filter(CV.user_id == current_user.id).first()
    
    if not cv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Önce CV yüklemeniz gerekiyor"
        )
    
    cv_data = _cv_to_dict(cv, current_user)
    
    result = await cover_letter_service.generate_smart_email(
        cv_data=cv_data,
        company_name=request.company_name,
        position_title=request.position_title,
        position_type=request.position_type,
        sector=request.sector,
        style=request.style or "professional",
        length=request.length or "medium",
        company_note=request.company_note
    )
    
    return EmailResponse(**result)


# ============================================================================
# HELPERS
# ============================================================================

def _cv_to_dict(cv: CV, user: User = None) -> dict:
    """CV modelini dict'e çevir."""
    full_name = cv.full_name
    if not full_name and user:
        full_name = user.full_name

    return {
        "full_name": full_name,
        "title": cv.title,
        "email": cv.email,
        "phone": cv.phone,
        "linkedin": cv.linkedin,
        "github": cv.github,
        "summary": cv.summary,
        "skills": cv.skills or [],
        "experience": cv.experience or [],
        "education": cv.education or [],
        "projects": cv.projects or [],
        "languages": cv.languages or {},
        "experience_years": cv.experience_years,
    }

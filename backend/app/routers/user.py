"""
KariyerKoçu - User Router
=========================
Profil ve dashboard endpoint'leri.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.cv import CV
from app.models.analysis import CVAnalysis
from app.models.interview import InterviewSession, InterviewStatus
from app.schemas.user import (
    UserProfileResponse,
    UpdateCareerGoalsRequest,
    UpdateProfileRequest,
    ChangePasswordRequest,
    DashboardResponse,
    CareerGoals,
    CVSummary,
    AnalysisSummary,
    InterviewSummary,
    MessageResponse
)
from app.utils.jwt import get_current_user, hash_password, verify_password
from app.career.interview_config import (
    COMPANY_SECTORS,
    POSITIONS,
    EXPERIENCE_REQUIREMENTS
)
from app.career.career_config import FIELDS


router = APIRouter()


# ============================================================================
# PROFİL
# ============================================================================

@router.get(
    "/profile",
    response_model=UserProfileResponse,
    summary="Profil Bilgisi",
    description="Kullanıcı profil bilgilerini getir."
)
async def get_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Kullanıcı profil bilgilerini getir."""
    
    # CV durumu
    cv = db.query(CV).filter(CV.user_id == current_user.id).first()
    
    # Kariyer hedefi bilgilerini al
    career_goals = CareerGoals(
        target_sector=current_user.target_sector,
        target_sector_name=COMPANY_SECTORS.get(current_user.target_sector, {}).get("name") if current_user.target_sector else None,
        target_position=current_user.target_position,
        target_position_name=POSITIONS.get(current_user.target_position, {}).get("name") if current_user.target_position else None,
        experience_level=current_user.experience_level,
        experience_level_name=EXPERIENCE_REQUIREMENTS.get(current_user.experience_level, {}).get("name") if current_user.experience_level else None
    )
    
    return UserProfileResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        phone=current_user.phone,
        created_at=current_user.created_at,
        has_cv=cv is not None,
        cv_filename=cv.original_filename if cv else None,
        cv_uploaded_at=cv.created_at if cv else None,
        career_goals=career_goals
    )


@router.put(
    "/profile",
    response_model=MessageResponse,
    summary="Profil Güncelle",
    description="Kullanıcı profil bilgilerini güncelle (ad soyad)."
)
async def update_profile(
    request: UpdateProfileRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Profil bilgilerini güncelle."""
    
    if request.full_name is not None:
        current_user.full_name = request.full_name
    
    if request.phone is not None:
        current_user.phone = request.phone
    
    db.commit()
    
    return MessageResponse(message="Profil güncellendi.")


@router.put(
    "/profile/password",
    response_model=MessageResponse,
    summary="Şifre Değiştir",
    description="Mevcut şifreyi doğrulayarak yeni şifre belirle."
)
async def change_password(
    request: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Şifre değiştir."""
    
    # Mevcut şifreyi doğrula
    if not verify_password(request.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mevcut şifre yanlış."
        )
    
    # Yeni şifreyi hashle ve kaydet
    current_user.hashed_password = hash_password(request.new_password)
    db.commit()
    
    return MessageResponse(message="Şifre başarıyla değiştirildi.")


@router.put(
    "/profile/career-goals",
    response_model=MessageResponse,
    summary="Kariyer Hedefini Güncelle",
    description="Hedef sektör, pozisyon ve tecrübe seviyesini güncelle."
)
async def update_career_goals(
    request: UpdateCareerGoalsRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Kariyer hedefini güncelle."""
    
    # Validasyonlar
    if request.target_sector and request.target_sector not in COMPANY_SECTORS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Geçersiz sektör: {request.target_sector}"
        )
    
    if request.target_position and request.target_position not in POSITIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Geçersiz pozisyon: {request.target_position}"
        )
    
    if request.experience_level and request.experience_level not in EXPERIENCE_REQUIREMENTS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Geçersiz tecrübe seviyesi: {request.experience_level}"
        )
    
    # Güncelle
    if request.target_sector is not None:
        current_user.target_sector = request.target_sector
    if request.target_position is not None:
        current_user.target_position = request.target_position
    if request.experience_level is not None:
        current_user.experience_level = request.experience_level
    
    db.commit()
    
    return MessageResponse(message="Kariyer hedefi güncellendi.")


# ============================================================================
# DASHBOARD
# ============================================================================

@router.get(
    "/dashboard",
    response_model=DashboardResponse,
    summary="Dashboard Verisi",
    description="Ana sayfa için özet veriler."
)
async def get_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Dashboard ana sayfa verilerini getir."""
    
    # CV bilgisi
    cv = db.query(CV).filter(CV.user_id == current_user.id).first()
    cv_summary = CVSummary(
        is_uploaded=cv is not None,
        filename=cv.original_filename if cv else None,
        full_name=cv.full_name if cv else None,
        skills_count=len(cv.skills or []) if cv else 0,
        projects_count=len(cv.projects or []) if cv else 0,
        uploaded_at=cv.created_at if cv else None
    )
    
    # Son analiz
    last_analysis = db.query(CVAnalysis).filter(
        CVAnalysis.user_id == current_user.id
    ).order_by(CVAnalysis.created_at.desc()).first()
    
    total_analyses = db.query(CVAnalysis).filter(
        CVAnalysis.user_id == current_user.id
    ).count()
    
    # En yüksek skoru al (SÖN ANALİZ DEĞİL, EN YÜKSEK!)
    from sqlalchemy import func
    highest_score_result = db.query(func.max(CVAnalysis.overall_score)).filter(
        CVAnalysis.user_id == current_user.id
    ).scalar()
    
    analysis_summary = AnalysisSummary(
        has_analysis=last_analysis is not None,
        last_analysis_date=last_analysis.created_at if last_analysis else None,
        strongest_field=last_analysis.strongest_field if last_analysis else None,
        strongest_field_name=FIELDS.get(last_analysis.strongest_field, {}).get("name") if last_analysis and last_analysis.strongest_field else None,
        strongest_score=highest_score_result,  # En yüksek skor (son analiz değil!)
        total_analyses=total_analyses
    )
    
    # Son mülakat
    last_interview = db.query(InterviewSession).filter(
        InterviewSession.user_id == current_user.id,
        InterviewSession.status == InterviewStatus.COMPLETED
    ).order_by(InterviewSession.completed_at.desc()).first()
    
    total_interviews = db.query(InterviewSession).filter(
        InterviewSession.user_id == current_user.id,
        InterviewSession.status == InterviewStatus.COMPLETED
    ).count()
    
    # Aktif mülakat kontrolü
    active_interview = db.query(InterviewSession).filter(
        InterviewSession.user_id == current_user.id,
        InterviewSession.status == InterviewStatus.IN_PROGRESS
    ).first()
    
    interview_summary = InterviewSummary(
        has_interview=last_interview is not None,
        last_interview_date=last_interview.completed_at if last_interview else None,
        last_position=POSITIONS.get(last_interview.position, {}).get("name") if last_interview else None,
        last_score=last_interview.average_score if last_interview else None,
        passed=last_interview.average_score >= 6.0 if last_interview and last_interview.average_score else None,
        total_interviews=total_interviews,
        has_active_interview=active_interview is not None,
        active_session_id=active_interview.id if active_interview else None
    )
    
    # Kariyer hedefi
    career_goals = CareerGoals(
        target_sector=current_user.target_sector,
        target_sector_name=COMPANY_SECTORS.get(current_user.target_sector, {}).get("name") if current_user.target_sector else None,
        target_position=current_user.target_position,
        target_position_name=POSITIONS.get(current_user.target_position, {}).get("name") if current_user.target_position else None,
        experience_level=current_user.experience_level,
        experience_level_name=EXPERIENCE_REQUIREMENTS.get(current_user.experience_level, {}).get("name") if current_user.experience_level else None
    )
    
    has_career_goals = any([
        current_user.target_sector,
        current_user.target_position,
        current_user.experience_level
    ])
    
    # Önerilen eylemler
    suggested_actions = []
    
    if not has_career_goals:
        suggested_actions.append("🎯 Kariyer hedefini belirle")
    
    if not cv:
        suggested_actions.append("📄 CV yükle")
    elif not analysis_summary.has_analysis:
        suggested_actions.append("📊 CV'ni analiz et")
    
    if analysis_summary.has_analysis and not interview_summary.has_interview:
        suggested_actions.append("🎤 İlk mülakat simülasyonunu yap")
    
    if analysis_summary.has_analysis and analysis_summary.strongest_score and analysis_summary.strongest_score < 70:
        suggested_actions.append("📚 Tavsiye edilen kaynakları incele")
    
    if not suggested_actions:
        suggested_actions.append("🚀 Harika gidiyorsun! Mülakat pratiğine devam et")
    
    return DashboardResponse(
        user_name=current_user.full_name,
        email=current_user.email,
        member_since=current_user.created_at,
        career_goals=career_goals,
        has_career_goals=has_career_goals,
        cv=cv_summary,
        analysis=analysis_summary,
        interview=interview_summary,
        suggested_actions=suggested_actions
    )


# ============================================================================
# CV DETAYLARI (Profil için)
# ============================================================================

@router.get(
    "/cv-details",
    summary="CV Detayları",
    description="CV'den parse edilen tüm bilgileri döndür."
)
async def get_cv_details(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    CV'den parse edilen bilgileri döndür.
    Profil sayfasında CV içeriğini göstermek için kullanılır.
    """
    cv = db.query(CV).filter(CV.user_id == current_user.id).first()
    
    if not cv:
        return {
            "has_cv": False,
            "message": "CV yüklenmemiş"
        }
    
    return {
        "has_cv": True,
        "uploaded_at": cv.created_at.isoformat() if cv.created_at else None,
        "filename": cv.original_filename,
        
        # Kişisel bilgiler
        "personal": {
            "full_name": cv.full_name,
            "title": cv.title,
            "email": cv.email,
            "phone": cv.phone,
            "location": cv.location,
            "linkedin": cv.linkedin,
            "github": cv.github,
        },
        
        # Özet
        "summary": cv.summary,
        
        # Yapılandırılmış veriler
        "skills": cv.skills or [],
        "experience": cv.experience or [],
        "education": cv.education or [],
        "projects": cv.projects or [],
        "languages": cv.languages or {},
        "certifications": cv.certifications or [],
        
        # Özet bilgiler
        "stats": {
            "skills_count": len(cv.skills or []),
            "experience_count": len(cv.experience or []),
            "education_count": len(cv.education or []),
            "projects_count": len(cv.projects or []),
        }
    }

"""
KariyerKoçu - Analiz Router
===========================
CV analizi ve config endpoint'leri.
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.cv import CV
from app.models.user import User
from app.models.analysis import CVAnalysis
from app.schemas.analysis import (
    CVAnalysisRequest,
    CVAnalysisResponse,
    ConfigResponse,
    SectorOption,
    FieldOption,
    ExperienceOption,
    RecommendationRequest,
    RecommendationResponse
)
from app.services.recommendation_service import recommendation_service
from app.services.cv_analysis_service import cv_analysis_service
from app.services.ats_simulation_service import ats_simulation_service
from app.utils.jwt import get_current_user
from app.career.career_config import (
    get_sectors_list,
    get_fields_for_sector,
    get_experience_levels_list,
    SECTORS,
    FIELDS
)


router = APIRouter()


# ============================================================================
# KONFİGÜRASYON ENDPOİNT'LERİ
# ============================================================================

@router.get(
    "/config",
    response_model=ConfigResponse,
    summary="Dropdown Verilerini Getir",
    description="Sektör, alan ve tecrübe seçeneklerini getir."
)
async def get_config():
    """
    Frontend dropdown'ları için config verisi.
    
    Returns:
        - sectors: Sektör listesi
        - fields: Her sektör için alan listesi
        - experience_levels: Tecrübe seviyeleri
    """
    
    sectors = [SectorOption(**s) for s in get_sectors_list()]
    
    # Her sektör için alanları hazırla
    fields_by_sector = {}
    for sector_id in SECTORS.keys():
        fields_by_sector[sector_id] = [
            FieldOption(**f) for f in get_fields_for_sector(sector_id)
        ]
    
    experience_levels = [
        ExperienceOption(**e) for e in get_experience_levels_list()
    ]
    
    return ConfigResponse(
        sectors=sectors,
        fields=fields_by_sector,
        experience_levels=experience_levels
    )


@router.get(
    "/config/fields/{sector_id}",
    response_model=List[FieldOption],
    summary="Sektöre Göre Alanları Getir",
    description="Belirli bir sektör için mevcut alanları getir."
)
async def get_fields(sector_id: str):
    """Sektöre göre alan listesi."""
    
    if sector_id not in SECTORS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sektör bulunamadı: {sector_id}"
        )
    
    return [FieldOption(**f) for f in get_fields_for_sector(sector_id)]


# ============================================================================
# ANALİZ ENDPOİNT'İ
# ============================================================================

@router.post(
    "/analyze",
    response_model=CVAnalysisResponse,
    summary="CV Analiz Et",
    description="Yüklü CV'yi seçilen profil bağlamında analiz et."
)
async def analyze_cv(
    request: CVAnalysisRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    CV'yi bağlamsal olarak analiz et.
    
    AKIŞ:
    1. Kullanıcının CV'sini getir
    2. Seçilen sektör/alan/tecrübe ile analiz et
    3. Her alan için ayrı puan ver
    4. Güçlü/zayıf yönleri belirle
    
    ÖNEMLİ: Aynı CV farklı profiller için farklı puanlanır!
    """
    
    # Kullanıcının CV'sini getir
    cv = db.query(CV).filter(CV.user_id == current_user.id).first()
    
    if not cv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Önce CV yüklemeniz gerekiyor"
        )
    
    if not cv.is_parsed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CV henüz parse edilmemiş. Lütfen CV'yi yeniden yükleyin."
        )
    
    # Validasyonlar
    if request.sector not in SECTORS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Geçersiz sektör: {request.sector}"
        )
    
    for field_id in request.fields:
        if field_id not in FIELDS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Geçersiz alan: {field_id}"
            )
    
    # CV verisini dict'e çevir
    cv_data = {
        "id": cv.id,
        "full_name": cv.full_name,
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
        "certifications": cv.certifications or []
    }
    
    try:
        # Analiz yap
        result = await cv_analysis_service.analyze_cv(
            cv_data=cv_data,
            sector=request.sector,
            fields=request.fields,
            experience_level=request.experience_level,
            analysis_method=request.analysis_method
        )
        
        # Analizi veritabanına kaydet
        analysis_record = CVAnalysis(
            user_id=current_user.id,
            cv_id=cv.id,
            sector=request.sector,
            fields=request.fields,
            experience_level=request.experience_level,
            field_analyses=result.get("field_analyses", []),
            strongest_field=result.get("strongest_field"),
            action_items=result.get("action_items", []),
            overall_score=max([fa.get("overall_score", 0) for fa in result.get("field_analyses", [])], default=0)
        )
        db.add(analysis_record)
        db.commit()
        
        # ESKİ ANALİZLERİ TEMİZLE - Kullanıcı başına max 3 analiz tut
        MAX_ANALYSES_PER_USER = 3
        user_analyses = db.query(CVAnalysis).filter(
            CVAnalysis.user_id == current_user.id
        ).order_by(CVAnalysis.created_at.desc()).all()
        
        if len(user_analyses) > MAX_ANALYSES_PER_USER:
            # En eski analizleri sil
            for old_analysis in user_analyses[MAX_ANALYSES_PER_USER:]:
                db.delete(old_analysis)
            db.commit()
        
        return CVAnalysisResponse(**result)
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analiz hatası: {str(e)}"
        )


# ============================================================================
# HIZLI ANALİZ (CV verisi ile birlikte)
# ============================================================================

@router.get(
    "/my-cv-summary",
    summary="CV Özeti",
    description="Kullanıcının yüklü CV'sinin özet bilgilerini getir."
)
async def get_cv_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Kullanıcının CV'sinin özet bilgilerini getir.
    Analiz yapmadan önce CV'nin yüklü olduğunu kontrol etmek için kullanılır.
    """
    
    cv = db.query(CV).filter(CV.user_id == current_user.id).first()
    
    if not cv:
        return {
            "has_cv": False,
            "message": "Henüz CV yüklenmemiş"
        }
    
    return {
        "has_cv": True,
        "is_parsed": cv.is_parsed,
        "filename": cv.original_filename,
        "full_name": cv.full_name,
        "title": cv.title,
        "skills_count": len(cv.skills or []),
        "experience_count": len(cv.experience or []),
        "projects_count": len(cv.projects or []),
        "uploaded_at": cv.created_at,
        "updated_at": cv.updated_at
    }


# ============================================================================
# ANALİZ LİSTESİ
# ============================================================================

@router.get(
    "/list",
    summary="Son Analizleri Listele",
    description="Kullanıcının son 3 analizini getir."
)
async def list_analyses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Kullanıcının son 3 CV analizini listele.
    Tavsiye almadan önce analiz seçimi için kullanılır.
    """
    
    analyses = db.query(CVAnalysis).filter(
        CVAnalysis.user_id == current_user.id
    ).order_by(CVAnalysis.created_at.desc()).limit(3).all()
    
    result = []
    for analysis in analyses:
        # Field isimlerini al
        field_names = []
        for field_id in analysis.fields:
            field_info = FIELDS.get(field_id, {})
            field_names.append(field_info.get("name", field_id))
        
        result.append({
            "id": str(analysis.id),
            "created_at": analysis.created_at.isoformat(),
            "fields": analysis.fields,
            "field_names": field_names,
            "experience_level": analysis.experience_level,
            "overall_score": analysis.overall_score
        })
    
    return {"analyses": result, "total": len(result)}


# ============================================================================
# ANALİZ SİLME
# ============================================================================

@router.delete(
    "/{analysis_id}",
    summary="Analizi Sil",
    description="Belirli bir CV analizini sil."
)
async def delete_analysis(
    analysis_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Belirli bir CV analizini sil.
    Sadece kullanıcının kendi analizlerini silebilir.
    """
    
    analysis = db.query(CVAnalysis).filter(
        CVAnalysis.id == analysis_id,
        CVAnalysis.user_id == current_user.id
    ).first()
    
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analiz bulunamadı veya size ait değil."
        )
    
    try:
        db.delete(analysis)
        db.commit()
        return {"success": True, "message": "Analiz başarıyla silindi."}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Silme hatası: {str(e)}"
        )


# ============================================================================
# TEKİL ANALİZ GÖRÜNTÜLEME
# ============================================================================

@router.get(
    "/detail/{analysis_id}",
    summary="Belirli Analizi Getir",
    description="Analiz ID'sine göre detaylı analiz sonuçlarını getir."
)
async def get_analysis_by_id(
    analysis_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Belirli bir CV analizinin detaylarını getir.
    """
    
    analysis = db.query(CVAnalysis).filter(
        CVAnalysis.id == analysis_id,
        CVAnalysis.user_id == current_user.id
    ).first()
    
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analiz bulunamadı veya size ait değil."
        )
    
    # Sektör ve alan isimlerini al
    sector_info = SECTORS.get(analysis.sector, {})
    sector_name = sector_info.get("name", analysis.sector)
    
    from app.career.career_config import EXPERIENCE_LEVELS
    exp_info = EXPERIENCE_LEVELS.get(analysis.experience_level, {})
    exp_name = exp_info.get("name", analysis.experience_level)
    
    return {
        "id": str(analysis.id),
        "sector": analysis.sector,
        "sector_name": sector_name,
        "fields": analysis.fields,
        "experience_level": analysis.experience_level,
        "experience_level_name": exp_name,
        "overall_score": analysis.overall_score,
        "field_analyses": analysis.field_analyses,
        "created_at": analysis.created_at.isoformat()
    }


# ============================================================================
# TAVSİYE SİSTEMİ
# ============================================================================

@router.get(
    "/recommend",
    response_model=RecommendationResponse,
    summary="Kişiselleştirilmiş Tavsiyeler Al",
    description="CV analizine göre kariyer tavsiyeleri al. analysis_id ile belirli analiz seçilebilir."
)
async def get_recommendations(
    analysis_id: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    CV analiz sonucuna göre kişiselleştirilmiş kariyer tavsiyeleri üret.
    
    Args:
        analysis_id: Opsiyonel. Belirli bir analiz için tavsiye al.
                     Verilmezse son analiz kullanılır.
    """
    
    # Analizi getir
    if analysis_id:
        # Belirli analizi getir
        analysis = db.query(CVAnalysis).filter(
            CVAnalysis.id == analysis_id,
            CVAnalysis.user_id == current_user.id
        ).first()
        
        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Analiz bulunamadı veya size ait değil."
            )
    else:
        # Son analizi getir
        analysis = db.query(CVAnalysis).filter(
            CVAnalysis.user_id == current_user.id
        ).order_by(CVAnalysis.created_at.desc()).first()
        
        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Önce CV analizi yapmanız gerekiyor. /analyze endpoint'ini kullanın."
            )
    
    try:
        result = await recommendation_service.generate_recommendations(
            sector=analysis.sector,
            fields=analysis.fields,
            experience_level=analysis.experience_level,
            field_analyses=analysis.field_analyses
        )
        
        return RecommendationResponse(**result)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Tavsiye oluşturma hatası: {str(e)}"
        )


# ============================================================================
# ATS SİMÜLASYONU
# ============================================================================

@router.post(
    "/ats-simulation",
    summary="ATS Simülasyonu",
    description="CV'yi ATS (Applicant Tracking System) gözüyle analiz et."
)
async def simulate_ats(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    """
    CV'yi ATS sistemlerinin gördüğü gibi analiz et.
    
    Bu endpoint:
    1. PDF'i basit bir kütüphane ile okur (ATS gibi)
    2. Okunabilirlik sorunlarını tespit eder
    3. İkon, sütun kayması gibi problemleri bulur
    4. ATS uyumluluk skoru verir
    
    Returns:
        - raw_text: Robotun okuduğu ham metin
        - issues: Tespit edilen sorunlar
        - score: 0-100 uyumluluk skoru
        - recommendations: İyileştirme önerileri
    """
    
    # Dosya türü kontrolü
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sadece PDF dosyaları destekleniyor"
        )
    
    try:
        # PDF içeriğini oku
        pdf_bytes = await file.read()
        
        # ATS simülasyonu yap
        result = ats_simulation_service.simulate_ats_read(pdf_bytes)
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"ATS simülasyon hatası: {str(e)}"
        )


@router.get(
    "/ats-simulation/from-cv",
    summary="Kayıtlı CV için ATS Simülasyonu",
    description="Kullanıcının yüklü CV'sini ATS gözüyle analiz et."
)
async def simulate_ats_from_saved_cv(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Kullanıcının daha önce yüklediği CV'yi ATS simülasyonuna sok.
    Yeni dosya yüklemeye gerek yok.
    """
    
    # Kullanıcının CV'sini getir
    cv = db.query(CV).filter(CV.user_id == current_user.id).first()
    
    if not cv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Önce CV yüklemeniz gerekiyor"
        )
    
    if not cv.raw_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CV henüz parse edilmemiş. Lütfen CV'yi yeniden yükleyin."
        )
    
    try:
        # Zaten çıkarılmış raw_text'i kullan
        result = ats_simulation_service.analyze_raw_text(cv.raw_text)
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"ATS simülasyon hatası: {str(e)}"
        )


@router.post(
    "/ats-simulation/test-file",
    summary="Geçici CV ATS Testi",
    description="Bir CV dosyasını ATS testine sok, backend'e kaydetme."
)
async def simulate_ats_test_file(
    file: UploadFile = File(..., description="Test edilecek PDF dosyası"),
):
    """
    CV dosyasını ATS simülasyonuna sok ama backend'e KAYDETME.
    
    Bu endpoint kullanıcının başka CV'leri test etmesine izin verir
    kendi profil bilgilerini değiştirmeden.
    
    NOT: Tutarsızlık analizi yapılmaz, sadece PyMuPDF ile okunur (sistemdeki CV ile aynı).
    """
    
    # Dosya türü kontrolü
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sadece PDF dosyaları destekleniyor"
        )
    
    try:
        # PDF içeriğini oku
        pdf_bytes = await file.read()
        
        # ATS simülasyonu yap - tutarsızlık analizi KAPALI (run_all_readers=False)
        # Bu sayede sistemdeki CV ile aynı şekilde analiz yapılır
        result = ats_simulation_service.simulate_ats_read(pdf_bytes, run_all_readers=False)
        
        # Test edilen dosya adını ekle
        result["tested_filename"] = file.filename
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"ATS simülasyon hatası: {str(e)}"
        )

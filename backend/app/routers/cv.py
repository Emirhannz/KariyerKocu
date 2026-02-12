"""
KariyerKoçu - CV Router
=======================
CV yükleme ve görüntüleme endpoint'leri.
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.cv import CV
from app.models.user import User
from app.schemas.cv import CVUploadResponse, CVResponse, CVParsedData
from app.services.cv_service import cv_service
from app.utils.jwt import get_current_user


router = APIRouter()


# ============================================================================
# CV YÜKLEME
# ============================================================================

@router.post(
    "/upload",
    response_model=CVUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="CV Yükle",
    description="PDF formatında CV yükle ve otomatik parse et."
)
async def upload_cv(
    file: UploadFile = File(..., description="PDF dosyası"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CVUploadResponse:
    """
    CV yükle ve LLM ile parse et.
    
    AKIŞ:
    1. PDF dosyasını al
    2. Metin çıkar (PyPDF2)
    3. LLM ile parse et
    4. Veritabanına kaydet
    5. Sonucu döndür
    
    NOT: Her kullanıcının sadece 1 CV'si olabilir.
    Yeni yükleme eskisini günceller.
    """
    
    # Dosya kontrolü
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sadece PDF dosyası yüklenebilir"
        )
    
    # Dosya boyutu kontrolü (max 5MB)
    content = await file.read()
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dosya boyutu 5MB'dan büyük olamaz"
        )
    
    try:
        # 1. PDF'den metin çıkar
        raw_text = await cv_service.extract_text_from_pdf(content)
        
        if not raw_text or len(raw_text) < 50:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="PDF'den metin çıkarılamadı. Lütfen metin tabanlı bir PDF yükleyin."
            )
        
        # 2. LLM ile parse et
        parsed_data = await cv_service.parse_cv_with_llm(raw_text)
        
        # Parse hatası var mı?
        has_error = parsed_data.get("parse_error", False)
        
        # 3. Mevcut CV var mı kontrol et
        existing_cv = db.query(CV).filter(CV.user_id == current_user.id).first()
        
        if existing_cv:
            # Güncelle
            cv = existing_cv
            cv.original_filename = file.filename
            cv.raw_text = raw_text
        else:
            # Yeni oluştur
            cv = CV(
                user_id=current_user.id,
                original_filename=file.filename,
                raw_text=raw_text,
            )
            db.add(cv)
        
        # 4. Parse edilen verileri kaydet
        if not has_error:
            cv.full_name = parsed_data.get("full_name")
            cv.title = parsed_data.get("title")
            cv.email = parsed_data.get("email")
            cv.phone = parsed_data.get("phone")
            cv.linkedin = parsed_data.get("linkedin")
            cv.github = parsed_data.get("github")
            cv.location = parsed_data.get("location")
            cv.summary = parsed_data.get("summary")
            cv.skills = parsed_data.get("skills", [])
            cv.experience = parsed_data.get("experience", [])
            cv.education = parsed_data.get("education", [])
            cv.projects = parsed_data.get("projects", [])
            cv.languages = parsed_data.get("languages", {})
            cv.certifications = parsed_data.get("certifications", [])
            cv.experience_years = parsed_data.get("experience_years")
            cv.is_parsed = True
            cv.parse_error = None
        else:
            cv.is_parsed = False
            cv.parse_error = parsed_data.get("error_message", "Bilinmeyen hata")
        
        db.commit()
        db.refresh(cv)
        
        # 5. Response oluştur
        return CVUploadResponse(
            id=cv.id,
            filename=file.filename,
            is_parsed=cv.is_parsed,
            parsed_data=CVParsedData(**parsed_data) if not has_error else None,
            message="CV başarıyla yüklendi ve analiz edildi!" if not has_error 
                    else f"CV yüklendi ama analiz başarısız: {cv.parse_error}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"CV işleme hatası: {str(e)}"
        )


# ============================================================================
# CV GÖRÜNTÜLEME
# ============================================================================

@router.get(
    "/me",
    response_model=CVResponse,
    summary="Kendi CV'mi Getir",
    description="Giriş yapmış kullanıcının CV'sini getir."
)
async def get_my_cv(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CVResponse:
    """
    Mevcut kullanıcının CV'sini getir.
    """
    cv = db.query(CV).filter(CV.user_id == current_user.id).first()
    
    if not cv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Henüz CV yüklememişsiniz"
        )
    
    return cv


# ============================================================================
# CV SİLME
# ============================================================================

@router.delete(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="CV'mi Sil",
    description="Giriş yapmış kullanıcının CV'sini sil."
)
async def delete_my_cv(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Mevcut kullanıcının CV'sini sil.
    """
    cv = db.query(CV).filter(CV.user_id == current_user.id).first()
    
    if not cv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Silinecek CV bulunamadı"
        )
    
    db.delete(cv)
    db.commit()
    
    return None


# ============================================================================
# CV YENİDEN PARSE ET
# ============================================================================

@router.post(
    "/reparse",
    response_model=CVUploadResponse,
    summary="CV'yi Yeniden Parse Et",
    description="Mevcut CV'yi LLM ile tekrar analiz et."
)
async def reparse_cv(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CVUploadResponse:
    """
    Mevcut CV'yi yeniden parse et.
    
    Kullanım durumu:
    - İlk parse başarısız olduysa
    - LLM güncellemesi sonrası daha iyi sonuç için
    """
    cv = db.query(CV).filter(CV.user_id == current_user.id).first()
    
    if not cv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parse edilecek CV bulunamadı"
        )
    
    if not cv.raw_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CV'de ham metin bulunamadı"
        )
    
    # Yeniden parse et
    parsed_data = await cv_service.parse_cv_with_llm(cv.raw_text)
    has_error = parsed_data.get("parse_error", False)
    
    # Güncelle
    if not has_error:
        cv.full_name = parsed_data.get("full_name")
        cv.title = parsed_data.get("title")
        cv.email = parsed_data.get("email")
        cv.phone = parsed_data.get("phone")
        cv.linkedin = parsed_data.get("linkedin")
        cv.github = parsed_data.get("github")
        cv.location = parsed_data.get("location")
        cv.summary = parsed_data.get("summary")
        cv.skills = parsed_data.get("skills", [])
        cv.experience = parsed_data.get("experience", [])
        cv.education = parsed_data.get("education", [])
        cv.projects = parsed_data.get("projects", [])
        cv.languages = parsed_data.get("languages", {})
        cv.certifications = parsed_data.get("certifications", [])
        cv.experience_years = parsed_data.get("experience_years")
        cv.is_parsed = True
        cv.parse_error = None
    else:
        cv.is_parsed = False
        cv.parse_error = parsed_data.get("error_message")
    
    db.commit()
    db.refresh(cv)
    
    return CVUploadResponse(
        id=cv.id,
        filename=cv.original_filename,
        is_parsed=cv.is_parsed,
        parsed_data=CVParsedData(**parsed_data) if not has_error else None,
        message="CV yeniden analiz edildi!" if not has_error 
                else f"Analiz başarısız: {cv.parse_error}"
    )


# ============================================================================
# CV BİLGİLERİNİ MANUEL GÜNCELLE
# ============================================================================

@router.put(
    "/update-info",
    summary="CV Bilgilerini Güncelle",
    description="Kullanıcının CV bilgilerini manuel olarak güncellemesini sağlar."
)
async def update_cv_info(
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    CV bilgilerini manuel güncelle.
    
    Bu endpoint, CV yanlış okunduysa kullanıcının
    düzeltme yapabilmesini sağlar.
    
    Güncellenebilir alanlar:
    - summary: Özet/Hakkımda
    - skills: Yetenekler listesi
    """
    cv = db.query(CV).filter(CV.user_id == current_user.id).first()
    
    if not cv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Güncellenecek CV bulunamadı"
        )
    
    # Güncelle
    if "summary" in data:
        cv.summary = data["summary"]
    
    if "skills" in data:
        cv.skills = data["skills"]
    
    db.commit()
    db.refresh(cv)
    
    return {
        "success": True,
        "message": "CV bilgileri güncellendi"
    }

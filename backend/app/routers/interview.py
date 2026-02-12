"""
KariyerKoçu - Mülakat Router
============================
Mülakat API endpoint'leri.
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.cv import CV
from app.models.user import User
from app.models.interview import InterviewSession, InterviewQuestion, InterviewAnswer, InterviewStatus
from app.services.speech_service import speech_service
from app.schemas.interview import (
    InterviewConfigResponse,
    SectorOption,
    PositionOption,
    ExperienceOption,
    InterviewTypeOption,
    StartInterviewRequest,
    StartInterviewResponse,
    QuestionResponse,
    SubmitAnswerRequest,
    SubmitAnswerResponse,
    CompleteInterviewResponse,
    InterviewReportResponse,
    InterviewHistoryItem,
    InterviewHistoryResponse
)
from app.services.interview_service import interview_service
from app.utils.jwt import get_current_user
from app.career.interview_config import (
    COMPANY_SECTORS,
    POSITIONS,
    EXPERIENCE_REQUIREMENTS,
    INTERVIEW_TYPES,
    get_sectors_list,
    get_positions_for_sector,
    get_experience_list,
    get_interview_types_list
)


router = APIRouter()


# ============================================================================
# KONFİGÜRASYON
# ============================================================================

@router.get(
    "/config",
    response_model=InterviewConfigResponse,
    summary="Mülakat Ayarları",
    description="Dropdown verileri: sektörler, pozisyonlar, tecrübe seviyeleri, mülakat tipleri."
)
async def get_config():
    """Mülakat başlatma formu için dropdown verilerini getir."""
    
    sectors = [SectorOption(**s) for s in get_sectors_list()]
    
    # Her sektör için pozisyonlar
    positions_by_sector = {}
    for sector_id in COMPANY_SECTORS.keys():
        positions_by_sector[sector_id] = [
            PositionOption(**p) for p in get_positions_for_sector(sector_id)
        ]
    
    experience_levels = [ExperienceOption(**e) for e in get_experience_list()]
    interview_types = [InterviewTypeOption(**t) for t in get_interview_types_list()]
    
    return InterviewConfigResponse(
        sectors=sectors,
        positions=positions_by_sector,
        experience_levels=experience_levels,
        interview_types=interview_types
    )


# ============================================================================
# MÜLAKAT BAŞLAT
# ============================================================================

@router.post(
    "/start",
    response_model=StartInterviewResponse,
    summary="Mülakat Başlat",
    description="Yeni mülakat oturumu oluştur."
)
async def start_interview(
    request: StartInterviewRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Yeni mülakat oturumu başlat.
    
    Kullanıcının CV'si varsa otomatik yüklenir.
    """
    
    # Validasyonlar
    if request.company_sector not in COMPANY_SECTORS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Geçersiz sektör: {request.company_sector}"
        )
    
    if request.position not in POSITIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Geçersiz pozisyon: {request.position}"
        )
    
    if request.experience_level not in EXPERIENCE_REQUIREMENTS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Geçersiz tecrübe seviyesi: {request.experience_level}"
        )
    
    if request.interview_type not in INTERVIEW_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Geçersiz mülakat tipi: {request.interview_type}"
        )
    
    # Kullanıcının CV'sini bul (opsiyonel)
    cv = db.query(CV).filter(CV.user_id == current_user.id).first()
    
    # Devam eden mülakat varsa uyar
    existing = db.query(InterviewSession).filter(
        InterviewSession.user_id == current_user.id,
        InterviewSession.status == InterviewStatus.IN_PROGRESS
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Devam eden bir mülakatınız var. Önce onu tamamlayın veya iptal edin."
        )
    
    # Yeni oturum oluştur
    session = InterviewSession(
        user_id=current_user.id,
        cv_id=cv.id if cv else None,
        company_sector=request.company_sector,
        position=request.position,
        experience_level=request.experience_level,
        interview_type=request.interview_type,
        total_questions=request.question_count,
        status=InterviewStatus.IN_PROGRESS
    )
    db.add(session)
    db.commit()
    
    return StartInterviewResponse(
        session_id=session.id,
        message="Mülakat başlatıldı. İlk soruyu almak için /question endpoint'ini çağırın.",
        total_questions=session.total_questions,
        interview_settings={
            "sector": COMPANY_SECTORS[request.company_sector]["name"],
            "sector_name": COMPANY_SECTORS[request.company_sector]["name"],
            "position": POSITIONS[request.position]["name"],
            "position_name": POSITIONS[request.position]["name"],
            "experience": EXPERIENCE_REQUIREMENTS[request.experience_level]["name"],
            "experience_level_name": EXPERIENCE_REQUIREMENTS[request.experience_level]["name"],
            "type": INTERVIEW_TYPES[request.interview_type]["name"],
            "voice_gender": request.voice_gender or "male",
            "interview_mode": request.interview_mode or "text"
        }
    )


# ============================================================================
# SORU AL
# ============================================================================

@router.get(
    "/question",
    response_model=QuestionResponse,
    summary="Sonraki Soru",
    description="Mevcut mülakatın sonraki sorusunu al."
)
async def get_next_question(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Sonraki mülakat sorusunu al.
    
    Önceki cevaba göre bağlantılı geçiş içerir.
    """
    
    # Aktif oturumu bul
    session = db.query(InterviewSession).filter(
        InterviewSession.user_id == current_user.id,
        InterviewSession.status == InterviewStatus.IN_PROGRESS
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aktif mülakat bulunamadı. Önce /start ile mülakat başlatın."
        )
    
    # Mülakat bitti mi?
    if session.current_question_number >= session.total_questions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tüm sorular tamamlandı. /complete ile mülakatı bitirin."
        )
    
    # Son cevabı bul (geçiş için)
    previous_answer = None
    if session.current_question_number > 0:
        last_question = db.query(InterviewQuestion).filter(
            InterviewQuestion.session_id == session.id,
            InterviewQuestion.question_number == session.current_question_number
        ).first()
        if last_question and last_question.answer:
            previous_answer = last_question.answer
    
    # CV verisini al
    cv_data = None
    if session.cv_id:
        cv = db.query(CV).filter(CV.id == session.cv_id).first()
        if cv:
            cv_data = {
                "projects": cv.projects or [],
                "skills": cv.skills or [],
                "experience": cv.experience or []
            }
    
    # Soru üret
    result = await interview_service.generate_question(
        session=session,
        cv_data=cv_data,
        previous_answer=previous_answer,
        db=db
    )
    
    return QuestionResponse(
        session_id=session.id,
        **result
    )


# ============================================================================
# CEVAP GÖNDER
# ============================================================================

@router.post(
    "/answer",
    response_model=SubmitAnswerResponse,
    summary="Cevap Gönder",
    description="Soruya cevap gönder."
)
async def submit_answer(
    request: SubmitAnswerRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Soruya cevap gönder.
    
    Cevap arka planda değerlendirilir ama sonuç gösterilmez.
    Mülakat bitince tüm değerlendirmeler raporda görülür.
    """
    
    # Session kontrolü
    session = db.query(InterviewSession).filter(
        InterviewSession.id == request.session_id,
        InterviewSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mülakat oturumu bulunamadı."
        )
    
    if session.status != InterviewStatus.IN_PROGRESS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu mülakat zaten tamamlanmış."
        )
    
    # Soru kontrolü
    question = db.query(InterviewQuestion).filter(
        InterviewQuestion.id == request.question_id,
        InterviewQuestion.session_id == session.id
    ).first()
    
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Soru bulunamadı."
        )
    
    if question.is_answered:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu soru zaten cevaplanmış."
        )
    
    # Cevabı değerlendir
    await interview_service.evaluate_answer(
        question=question,
        user_answer=request.answer,
        session=session,
        db=db
    )
    
    has_next = session.current_question_number < session.total_questions
    
    return SubmitAnswerResponse(
        message="Cevabınız kaydedildi.",
        question_number=question.question_number,
        has_next_question=has_next,
        next_question_available=has_next
    )


# ============================================================================
# MÜLAKATI BİTİR
# ============================================================================

@router.post(
    "/complete",
    response_model=CompleteInterviewResponse,
    summary="Mülakatı Bitir",
    description="Mülakatı tamamla ve rapor oluştur."
)
async def complete_interview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Mülakatı tamamla.
    
    Tüm cevaplar değerlendirilir ve rapor hazırlanır.
    """
    
    # Aktif oturumu bul
    session = db.query(InterviewSession).filter(
        InterviewSession.user_id == current_user.id,
        InterviewSession.status == InterviewStatus.IN_PROGRESS
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aktif mülakat bulunamadı."
        )
    
    # Cevaplanan soru sayısını kontrol et
    answered_count = db.query(InterviewQuestion).filter(
        InterviewQuestion.session_id == session.id,
        InterviewQuestion.is_answered == True
    ).count()
    
    if answered_count == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Hiç soru cevaplanmamış. En az bir soruyu cevaplayın."
        )
    
    # Mülakatı tamamla
    interview_service.complete_interview(session, db)
    
    return CompleteInterviewResponse(
        session_id=session.id,
        message="Mülakat tamamlandı! Detaylı rapor için /report endpoint'ini kullanın.",
        total_questions=session.total_questions,
        answered_questions=answered_count,
        redirect_url=f"/interview/report/{session.id}"
    )


# ============================================================================
# RAPOR
# ============================================================================

@router.get(
    "/report/{session_id}",
    response_model=InterviewReportResponse,
    summary="Mülakat Raporu",
    description="Tamamlanmış mülakatın detaylı raporunu al."
)
async def get_report(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Mülakat sonuç raporunu getir.
    
    Her soru için:
    - Verilen cevap
    - Puan (1-10)
    - Değerlendirme açıklaması
    - İdeal cevap
    - Güçlü/zayıf yönler
    
    Genel:
    - Ortalama puan
    - Geçti/kaldı
    - Genel güçlü yönler
    - Gelişim alanları
    - Tavsiyeler
    """
    
    session = db.query(InterviewSession).filter(
        InterviewSession.id == session_id,
        InterviewSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mülakat bulunamadı."
        )
    
    if session.status != InterviewStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mülakat henüz tamamlanmamış."
        )
    
    report = interview_service.generate_report(session, db)
    
    return InterviewReportResponse(**report)


# ============================================================================
# GEÇMİŞ MÜLAKATLAR
# ============================================================================

@router.get(
    "/history",
    response_model=InterviewHistoryResponse,
    summary="Mülakat Geçmişi",
    description="Kullanıcının tamamlanmış mülakatlarını listele."
)
async def get_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Geçmiş mülakatları getir."""
    
    sessions = db.query(InterviewSession).filter(
        InterviewSession.user_id == current_user.id
    ).order_by(InterviewSession.created_at.desc()).limit(20).all()
    
    items = []
    for s in sessions:
        sector_name = COMPANY_SECTORS.get(s.company_sector, {}).get("name", s.company_sector)
        position_name = POSITIONS.get(s.position, {}).get("name", s.position)
        exp_name = EXPERIENCE_REQUIREMENTS.get(s.experience_level, {}).get("name", s.experience_level)
        
        items.append(InterviewHistoryItem(
            session_id=s.id,
            position_name=position_name,
            company_sector_name=sector_name,
            experience_level_name=exp_name,
            average_score=s.average_score,
            passed=s.average_score >= 6.0 if s.average_score else None,
            status=s.status,
            created_at=s.created_at,
            completed_at=s.completed_at
        ))
    
    return InterviewHistoryResponse(
        total_count=len(items),
        interviews=items
    )


@router.delete(
    "/history/{session_id}",
    summary="Geçmiş Mülakatı Sil",
    description="Tamamlanmış veya iptal edilmiş mülakatı siler."
)
async def delete_history_item(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mülakat geçmişinden kayıt sil."""
    
    session = db.query(InterviewSession).filter(
        InterviewSession.id == session_id,
        InterviewSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mülakat bulunamadı."
        )
    
    # Önce tüm cevapları sil (foreign key constraint için)
    for question in session.questions:
        if question.answer:
            db.delete(question.answer)
    
    # Sonra soruları sil
    for question in session.questions:
        db.delete(question)
    
    # En son session'ı sil
    db.delete(session)
    db.commit()
    
    return {"message": "Mülakat silindi."}


# ============================================================================
# MÜLAKAT İPTAL
# ============================================================================

@router.delete(
    "/cancel",
    summary="Mülakatı İptal Et",
    description="Devam eden mülakatı iptal et ve veritabanından sil."
)
async def cancel_interview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Aktif mülakatı iptal et ve tamamen sil."""
    
    session = db.query(InterviewSession).filter(
        InterviewSession.user_id == current_user.id,
        InterviewSession.status == InterviewStatus.IN_PROGRESS
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aktif mülakat bulunamadı."
        )
    
    # Önce tüm cevapları sil (foreign key constraint için)
    # Dikkat: Duplicate answer olabilir, hepsini sil
    for question in session.questions:
        # Tüm cevapları bul ve sil (duplicate olabilir)
        answers = db.query(InterviewAnswer).filter(
            InterviewAnswer.question_id == question.id
        ).all()
        for answer in answers:
            db.delete(answer)
    
    # Sonra soruları sil
    for question in session.questions:
        db.delete(question)
    
    # En son session'ı sil
    db.delete(session)
    db.commit()
    
    return {"message": "Mülakat iptal edildi ve silindi."}


# ============================================================================
# SES TRANSKRIPSIYONU
# ============================================================================

@router.post(
    "/transcribe",
    summary="Sesi Metne Çevir",
    description="Ses dosyasını alıp metne çevirir."
)
async def transcribe_audio(
    audio: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    """
    Ses dosyasını metne çevir.
    
    Desteklenen formatlar: WAV, WebM, OGG, MP3, M4A
    """
    
    # Dosya boyutu kontrolü (10MB max)
    content = await audio.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dosya çok büyük (max 10MB)"
        )
    
    # Transkripsiyon yap
    result = await speech_service.transcribe_audio(
        audio_bytes=content,
        filename=audio.filename or "audio.webm"
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        )
    
    return {
        "text": result["text"],
        "success": True
    }


@router.post(
    "/transcribe-test",
    summary="Sesi Metne Çevir (TEST)",
    description="Test için - auth gerektirmez."
)
async def transcribe_audio_test(
    audio: UploadFile = File(...),
):
    """Test için auth'suz transkripsiyon endpoint'i."""
    
    content = await audio.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dosya çok büyük (max 10MB)"
        )
    
    result = await speech_service.transcribe_audio(
        audio_bytes=content,
        filename=audio.filename or "audio.webm"
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        )
    
    return {
        "text": result["text"],
        "success": True
    }



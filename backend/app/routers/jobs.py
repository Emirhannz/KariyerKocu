# -*- coding: utf-8 -*-
"""
Job Search Router
=================
İş arama API endpoint'leri.
Çoklu platform üzerinden iş ilanı arama.
"""
from fastapi import APIRouter, HTTPException

from app.schemas.job import (
    JobSearchRequest,
    JobSearchResponse,
    JobResult,
    AvailableOptionsResponse,
    CitiesResponse,
    ExperienceLevel,
    JobType,
)
from app.services.job_search_service import (
    search_jobs,
    get_cities,
    get_all_fields,
    get_supported_sites,
    FIELD_TERMS,
    PROFESSION_GROUPS,
)


router = APIRouter(prefix="/jobs", tags=["İş Arama"])


@router.post("/search", response_model=JobSearchResponse)
async def search_job_listings(request: JobSearchRequest):
    """
    Çoklu platform üzerinden iş ara.
    Çeşitli kaynaklardan iş ilanı verileri çeker.
    
    **Örnek:**
    ```json
    {
        "field": "backend",
        "sites": ["indeed", "glassdoor"],
        "time_range": "w",
        "city": "İstanbul",
        "experience_level": "yeni_mezun",
        "limit": 20
    }
    ```
    """
    try:
        # Sites listesini string'e çevir
        sites = None
        if request.sites:
            sites = [site.value for site in request.sites]
        
        # Field değerini al
        field = request.field.value
        time_range = request.time_range.value if request.time_range else "w"
        experience = request.experience_level.value if request.experience_level else None
        is_remote = request.is_remote
        job_type = request.job_type.value if request.job_type else None
        
        # Arama yap
        result = search_jobs(
            field=field,
            sites=sites,
            time_range=time_range,
            city=request.city,
            limit=request.limit,
            experience=experience,
            is_remote=is_remote,
            job_type=job_type
        )
        
        # Sonuçları dönüştür
        jobs = [JobResult(**job) for job in result["jobs"]]
        
        return JobSearchResponse(
            success=result["success"],
            jobs=jobs,
            total_count=result["total_count"],
            scraped_at=result["scraped_at"],
            error=result.get("error"),
            filters=result.get("filters")
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/options", response_model=AvailableOptionsResponse)
async def get_search_options():
    """
    İş arama için mevcut seçenekleri döndür.
    """
    # Alanlar
    fields = get_all_fields()
    
    # Tecrübe seviyeleri
    experience_levels = [
        {"value": exp.value, "label": exp.value.replace("_", " ").replace("yil", "Yıl").title()}
        for exp in ExperienceLevel
    ]
    
    # İş tipleri
    job_types = [
        {"value": "full_time", "label": "Tam Zamanlı"},
        {"value": "part_time", "label": "Yarı Zamanlı"},
        {"value": "contract", "label": "Sözleşmeli"},
        {"value": "internship", "label": "Staj"},
    ]
    
    # Siteler
    supported = get_supported_sites()
    sites = [
        {"value": "Platform 1", "domain": "platform1"},
        {"value": "Platform 2", "domain": "platform2"},
        {"value": "Platform 3", "domain": "platform3"},
    ]
    
    # Zaman aralıkları
    time_ranges = [
        {"value": "d", "label": "Son 24 Saat"},
        {"value": "d3", "label": "Son 3 Gün"},
        {"value": "w", "label": "Son 1 Hafta"},
        {"value": "m", "label": "Son 1 Ay"},
        {"value": "", "label": "Tüm Zamanlar"},
    ]
    
    return AvailableOptionsResponse(
        fields=fields,
        experience_levels=experience_levels,
        job_types=job_types,
        sites=sites,
        time_ranges=time_ranges
    )


@router.get("/cities/{country}", response_model=CitiesResponse)
async def get_cities_by_country(country: str):
    """Şehirleri döndür."""
    cities = get_cities(country)
    return CitiesResponse(country=country, cities=cities)


@router.get("/test")
async def test_job_search():
    """Test endpoint - 5 ilan çek."""
    result = search_jobs(
        field="backend",
        sites=["indeed"],
        time_range="w",
        limit=5
    )
    return result


@router.get("/professions")
async def get_profession_groups():
    """
    Tüm meslek gruplarını ve alanlarını döndür.
    Frontend'de meslek seçim dropdown'ı için kullanılır.
    """
    result = []
    
    for key, group in PROFESSION_GROUPS.items():
        fields_list = []
        for field_key, field_data in group["fields"].items():
            fields_list.append({
                "value": field_key,
                "label": field_data["label"]
            })
        
        result.append({
            "value": key,
            "label": group["label"],
            "label_en": group.get("label_en", group["label"]),
            "fields": fields_list
        })
    
    return {"professions": result}


@router.post("/search-custom")
async def search_custom_jobs(
    profession: str = "",
    field: str = "",
    limit: int = 20
):
    """
    Özel meslek ve alan ile iş ara.
    'Siz belirtin' seçeneği için kullanılır.
    
    Örnek: profession="Hemşire", field="Yoğun Bakım Hemşiresi"
    """
    # Arama terimi oluştur
    search_term = field if field else profession
    
    if not search_term:
        return {
            "success": False,
            "error": "Lütfen meslek veya alan belirtin",
            "jobs": [],
            "total_count": 0
        }
    
    # İş arama servisi ile ara
    from datetime import datetime
    from jobspy import scrape_jobs
    import pandas as pd
    
    try:
        jobs_df = scrape_jobs(
            site_name=["indeed", "linkedin"],
            search_term=search_term,
            location="Turkey",
            results_wanted=limit,
            hours_old=168,  # Son 7 gün
            country_indeed="Turkey",
            linkedin_fetch_description=True,
        )
        
        jobs = []
        if jobs_df is not None and not jobs_df.empty:
            for _, row in jobs_df.iterrows():
                full_desc = str(row.get("description", "")) if pd.notna(row.get("description")) else ""
                
                job = {
                    "title": str(row.get("title", "")) if pd.notna(row.get("title")) else "",
                    "company": str(row.get("company", "")) if pd.notna(row.get("company")) else "",
                    "location": str(row.get("location", "")) if pd.notna(row.get("location")) else "",
                    "url": str(row.get("job_url", "")) if pd.notna(row.get("job_url")) else "",
                    "description": full_desc,
                    "snippet": full_desc[:200] if full_desc else "",
                    "source": str(row.get("site", "")).title() if pd.notna(row.get("site")) else "Unknown",
                    "date_posted": str(row.get("date_posted", "")) if pd.notna(row.get("date_posted")) else "",
                }
                
                if job["title"] and job["url"]:
                    jobs.append(job)
        
        return {
            "success": True,
            "jobs": jobs,
            "total_count": len(jobs),
            "scraped_at": datetime.now().isoformat(),
            "filters": {
                "profession": profession,
                "field": field,
                "search_term": search_term
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "jobs": [],
            "total_count": 0
        }


# ============================================================================
# SKILL GAP ANALİZİ
# ============================================================================

from fastapi import Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.cv import CV
from app.utils.jwt import get_current_user
from app.schemas.job import SkillGapRequest, SkillGapResponse
from app.services.job_search_service import analyze_skill_gap


@router.post("/skill-gap", response_model=SkillGapResponse)
async def analyze_job_skill_gap(
    request: SkillGapRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    CV ile iş ilanı arasındaki uyumu analiz et.
    
    Kullanıcının yüklenmiş CV'si ile verilen iş ilanını karşılaştırır.
    Eşleşen yetenekler, eksik yetenekler ve genel uyum yüzdesini döndürür.
    """
    # Kullanıcının CV'sini al
    cv = db.query(CV).filter(CV.user_id == current_user.id).first()
    
    if not cv:
        return SkillGapResponse(
            success=False,
            error="CV bulunamadı. Lütfen önce CV yükleyin.",
            match_percentage=0,
            matching_skills=[],
            missing_skills=[],
            partial_skills=[],
            recommendation=""
        )
    
    # CV verisini hazırla
    cv_data = {
        "skills": cv.skills or [],
        "projects": cv.projects or [],
        "experience": cv.experience or [],
        "education": cv.education or [],
        "full_name": cv.full_name or "",
        "summary": cv.summary or ""
    }
    
    # Analiz yap
    result = await analyze_skill_gap(
        cv_data=cv_data,
        job_title=request.job_title,
        job_description=request.job_description,
        company_name=request.company_name or ""
    )
    
    return SkillGapResponse(
        success=result.get("success", False),
        match_percentage=result.get("match_percentage", 0),
        matching_skills=result.get("matching_skills", []),
        missing_skills=result.get("missing_skills", []),
        partial_skills=result.get("partial_skills", []),
        recommendation=result.get("recommendation", ""),
        error=result.get("error")
    )

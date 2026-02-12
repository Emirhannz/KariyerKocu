# -*- coding: utf-8 -*-
"""
Job Search Schemas
==================
İş arama API'si için Pydantic modelleri.
Çoklu platform iş ilanı arama.
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class ExperienceLevel(str, Enum):
    """Tecrübe seviyeleri"""
    STAJYER = "stajyer"
    YENI_MEZUN = "yeni_mezun"
    YIL_1_3 = "1-3_yil"
    YIL_3_5 = "3-5_yil"
    YIL_5_PLUS = "5+_yil"


class JobType(str, Enum):
    """İş tipleri"""
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    INTERNSHIP = "internship"


class FieldType(str, Enum):
    """Alan/Uzmanlık türleri - TÜM MESLEK GRUPLARI"""
    # Bilgisayar Mühendisliği
    YAPAY_ZEKA = "yapay_zeka"
    BACKEND = "backend"
    FRONTEND = "frontend"
    FULLSTACK = "fullstack"
    MOBILE = "mobile"
    DEVOPS = "devops"
    DATA = "data"
    TEST = "test"
    EMBEDDED = "embedded"
    SECURITY = "security"
    GAME = "game"
    BLOCKCHAIN = "blockchain"
    
    # Elektrik-Elektronik Mühendisliği
    ELEKTRIK_PROJE = "elektrik_proje"
    ELEKTRONIK_TASARIM = "elektronik_tasarim"
    OTOMASYON = "otomasyon"
    RF_MIKRODALGA = "rf_mikrodalga"
    GUC_ELEKTRONIGI = "guc_elektroniği"
    
    # Makine Mühendisliği
    TASARIM = "tasarim"
    URETIM = "uretim"
    HVAC = "hvac"
    OTOMOTIV = "otomotiv"
    KALITE = "kalite"
    
    # İnşaat Mühendisliği
    YAPI = "yapi"
    SANTIYE = "santiye"
    GEOTEKNIK = "geoteknik"
    ULASIM = "ulasim"
    
    # Endüstri Mühendisliği
    URETIM_PLANLAMA = "uretim_planlama"
    LOJISTIK = "lojistik"
    IS_ANALISTI = "is_analisti"
    ERP = "erp"
    
    # Kimya Mühendisliği
    PROSES = "proses"
    ARGE = "arge"
    
    # Biyomedikal Mühendisliği
    MEDIKAL_CIHAZ = "medikal_cihaz"
    KLINIK = "klinik"


class JobSite(str, Enum):
    """Desteklenen iş arama platformları"""
    INDEED = "indeed"
    LINKEDIN = "linkedin"
    GLASSDOOR = "glassdoor"


class TimeRange(str, Enum):
    """Zaman aralığı filtreleri"""
    DAY = "d"
    DAY_3 = "d3"
    WEEK = "w"
    MONTH = "m"
    ALL = ""


class JobSearchRequest(BaseModel):
    """İş arama isteği"""
    field: FieldType = Field(..., description="Aranacak alan")
    sites: Optional[List[JobSite]] = Field(
        default=None, 
        description="Aranacak platformlar"
    )
    time_range: Optional[TimeRange] = Field(default=TimeRange.WEEK, description="Zaman aralığı")
    city: Optional[str] = Field(None, description="Şehir")
    experience_level: Optional[ExperienceLevel] = Field(None, description="Tecrübe seviyesi")
    is_remote: Optional[bool] = Field(None, description="Sadece remote ilanlar")
    job_type: Optional[JobType] = Field(None, description="İş tipi (full_time, part_time, contract, internship)")
    limit: int = Field(default=20, ge=1, le=50, description="Maksimum sonuç sayısı")

    class Config:
        json_schema_extra = {
            "example": {
                "field": "backend",
                "sites": ["indeed", "glassdoor"],
                "time_range": "w",
                "city": "İstanbul",
                "experience_level": "yeni_mezun",
                "limit": 20
            }
        }


class JobResult(BaseModel):
    """Tek bir iş ilanı sonucu"""
    title: str = Field(..., description="İlan başlığı")
    company: Optional[str] = Field(default="", description="Şirket adı")
    location: Optional[str] = Field(default="", description="Lokasyon")
    url: str = Field(..., description="İlan URL'i")
    description: Optional[str] = Field(default="", description="Tam ilan açıklaması")
    snippet: str = Field(default="", description="İlan özeti (kısa)")
    source: str = Field(..., description="Kaynak platform")
    date_posted: Optional[str] = Field(default="", description="İlan tarihi")


class JobSearchResponse(BaseModel):
    """İş arama yanıtı"""
    success: bool = Field(..., description="Arama başarılı mı?")
    jobs: List[JobResult] = Field(default=[], description="Bulunan iş ilanları")
    total_count: int = Field(default=0, description="Toplam bulunan ilan sayısı")
    scraped_at: str = Field(..., description="Arama zamanı")
    error: Optional[str] = Field(None, description="Hata mesajı")
    filters: Optional[dict] = Field(None, description="Uygulanan filtreler")


class AvailableOptionsResponse(BaseModel):
    """Mevcut seçenekleri döndür"""
    fields: List[dict] = Field(..., description="Alan seçenekleri")
    experience_levels: List[dict] = Field(..., description="Tecrübe seviyeleri")
    job_types: List[dict] = Field(default=[], description="İş tipleri")
    sites: List[dict] = Field(..., description="Desteklenen siteler")
    time_ranges: List[dict] = Field(..., description="Zaman aralıkları")


class CitiesResponse(BaseModel):
    """Şehir listesi yanıtı"""
    country: str
    cities: List[str]


# ============================================================================
# SKILL GAP ANALİZİ ŞEMALARI
# ============================================================================

class SkillGapRequest(BaseModel):
    """Skill Gap analizi isteği"""
    job_title: str = Field(..., description="İş ilanı başlığı")
    job_description: str = Field(..., description="İş ilanı açıklaması")
    company_name: Optional[str] = Field(default="", description="Şirket adı")
    
    class Config:
        json_schema_extra = {
            "example": {
                "job_title": "Senior Backend Developer",
                "job_description": "Python, FastAPI, PostgreSQL, Docker, Kubernetes deneyimi arıyoruz...",
                "company_name": "Trendyol"
            }
        }


class SkillGapResponse(BaseModel):
    """Skill Gap analizi yanıtı"""
    success: bool = Field(..., description="Analiz başarılı mı?")
    match_percentage: int = Field(default=0, ge=0, le=100, description="Uyum yüzdesi")
    matching_skills: List[str] = Field(default=[], description="Eşleşen yetenekler")
    missing_skills: List[str] = Field(default=[], description="Eksik yetenekler")
    partial_skills: List[str] = Field(default=[], description="Kısmen eşleşen yetenekler")
    recommendation: str = Field(default="", description="Öneri")
    error: Optional[str] = Field(None, description="Hata mesajı")

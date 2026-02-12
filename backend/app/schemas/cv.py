"""
KariyerKoçu - CV Schemas
========================
CV ile ilgili Pydantic şemaları.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# ============================================================================
# DENEYİM (EXPERIENCE)
# ============================================================================

class ExperienceItem(BaseModel):
    """Tek bir iş deneyimi."""
    title: str = Field(..., description="Pozisyon/Unvan")
    company: Optional[str] = Field(None, description="Şirket adı")
    start_date: Optional[str] = Field(None, description="Başlangıç tarihi")
    end_date: Optional[str] = Field(None, description="Bitiş tarihi (Halen ise null)")
    duration: Optional[str] = Field(None, description="Süre (örn: 1 yıl 6 ay)")
    description: Optional[str] = Field(None, description="İş açıklaması")
    is_current: bool = Field(False, description="Halen bu pozisyonda mı?")


# ============================================================================
# EĞİTİM (EDUCATION)
# ============================================================================

class EducationItem(BaseModel):
    """Tek bir eğitim bilgisi."""
    degree: Optional[str] = Field(None, description="Derece (Lisans, Yüksek Lisans, vs.)")
    field: Optional[str] = Field(None, description="Bölüm/Alan")
    school: str = Field(..., description="Okul/Üniversite adı")
    start_year: Optional[int] = Field(None, description="Başlangıç yılı")
    end_year: Optional[int] = Field(None, description="Bitiş yılı")
    gpa: Optional[str] = Field(None, description="Not ortalaması")
    is_current: bool = Field(False, description="Halen öğrenci mi?")


# ============================================================================
# PROJE (PROJECT)
# ============================================================================

class ProjectItem(BaseModel):
    """Tek bir proje."""
    name: str = Field(..., description="Proje adı")
    technologies: List[str] = Field(default_factory=list, description="Kullanılan teknolojiler")
    description: Optional[str] = Field(None, description="Proje açıklaması")
    url: Optional[str] = Field(None, description="Proje URL'i")


# ============================================================================
# CV PARSE SONUCU
# ============================================================================

class CVParsedData(BaseModel):
    """LLM tarafından parse edilmiş CV verisi."""
    
    # Kişisel Bilgiler
    full_name: Optional[str] = Field(None, description="Ad Soyad")
    title: Optional[str] = Field(None, description="Unvan (örn: Backend Developer)")
    email: Optional[str] = Field(None, description="Email adresi")
    phone: Optional[str] = Field(None, description="Telefon numarası")
    linkedin: Optional[str] = Field(None, description="LinkedIn URL")
    github: Optional[str] = Field(None, description="GitHub URL")
    location: Optional[str] = Field(None, description="Konum")
    
    # Özet
    summary: Optional[str] = Field(None, description="Hakkımda/Özet bölümü")
    
    # Listeler
    skills: List[str] = Field(default_factory=list, description="Yetenekler")
    experience: List[ExperienceItem] = Field(default_factory=list, description="İş deneyimleri")
    education: List[EducationItem] = Field(default_factory=list, description="Eğitim bilgileri")
    projects: List[ProjectItem] = Field(default_factory=list, description="Projeler")
    languages: Dict[str, Optional[str]] = Field(default_factory=dict, description="Diller ve seviyeleri")
    certifications: List[str] = Field(default_factory=list, description="Sertifikalar")
    
    # Özet bilgiler
    experience_years: Optional[str] = Field(None, description="Toplam deneyim süresi")
    
    class Config:
        json_schema_extra = {
            "example": {
                "full_name": "Emirhan Zileli",
                "title": "Bilgisayar Mühendisliği Öğrencisi",
                "email": "emirhan@example.com",
                "skills": ["Python", "FastAPI", "React", "PostgreSQL"],
                "experience": [
                    {
                        "title": "Yazılım Geliştirici",
                        "company": "Gazi Bilişim Enstitüsü",
                        "start_date": "2024-01",
                        "end_date": None,
                        "duration": "1 yıl",
                        "is_current": True
                    }
                ],
                "education": [
                    {
                        "degree": "Lisans",
                        "field": "Bilgisayar Mühendisliği",
                        "school": "Gazi Üniversitesi",
                        "start_year": 2021,
                        "end_year": None,
                        "is_current": True
                    }
                ]
            }
        }


# ============================================================================
# API REQUEST/RESPONSE
# ============================================================================

class CVUploadResponse(BaseModel):
    """CV yükleme response'u."""
    id: str = Field(..., description="CV ID")
    filename: str = Field(..., description="Dosya adı")
    is_parsed: bool = Field(..., description="Parse edildi mi?")
    parsed_data: Optional[CVParsedData] = Field(None, description="Parse edilmiş veri")
    message: str = Field(..., description="İşlem mesajı")


class CVResponse(BaseModel):
    """CV detay response'u."""
    id: str
    user_id: str
    original_filename: str
    is_parsed: bool
    created_at: datetime
    updated_at: datetime
    
    # Parse edilmiş veriler
    full_name: Optional[str] = None
    title: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    summary: Optional[str] = None
    skills: Optional[List[str]] = None
    experience: Optional[List[Dict[str, Any]]] = None
    education: Optional[List[Dict[str, Any]]] = None
    projects: Optional[List[Dict[str, Any]]] = None
    languages: Optional[Dict[str, str]] = None
    experience_years: Optional[str] = None
    
    class Config:
        from_attributes = True

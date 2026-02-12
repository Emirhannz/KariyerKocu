"""
KariyerKoçu - CV Model
======================
CV verilerini saklamak için veritabanı modeli.

Her kullanıcının bir CV'si olabilir.
CV yüklendiğinde LLM ile parse edilir ve bu tabloya kaydedilir.
"""

from datetime import datetime
from typing import Optional
import uuid
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship

from app.database import Base


class CV(Base):
    """
    CV tablosu.
    
    Kullanıcının yüklediği CV'yi ve parse edilmiş bilgileri saklar.
    
    İLİŞKİ:
    - Bir User'ın bir CV'si olabilir (1-1)
    - CV silinirse User silinmez (CASCADE değil)
    """
    
    __tablename__ = "cvs"
    
    # Primary Key
    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        doc="UUID - benzersiz CV kimliği"
    )
    
    # Foreign Key - Hangi kullanıcının CV'si?
    user_id = Column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,  # Her kullanıcının 1 CV'si olabilir
        index=True,
        doc="CV'nin sahibi kullanıcı"
    )
    
    # Original dosya bilgileri
    original_filename = Column(
        String(255),
        nullable=False,
        doc="Yüklenen dosyanın orijinal adı"
    )
    
    # Ham metin (PDF'den çıkarılan)
    raw_text = Column(
        Text,
        nullable=True,
        doc="PDF'den çıkarılan ham metin"
    )
    
    # =========================================================================
    # PARSE EDİLMİŞ BİLGİLER
    # =========================================================================
    
    # Kişisel bilgiler
    full_name = Column(String(200), nullable=True, doc="Ad Soyad")
    title = Column(String(200), nullable=True, doc="Unvan/Pozisyon")
    email = Column(String(255), nullable=True, doc="Email")
    phone = Column(String(50), nullable=True, doc="Telefon")
    linkedin = Column(String(255), nullable=True, doc="LinkedIn URL")
    github = Column(String(255), nullable=True, doc="GitHub URL")
    location = Column(String(200), nullable=True, doc="Şehir/Ülke")
    
    # Hakkımda / Özet
    summary = Column(Text, nullable=True, doc="Kişisel özet paragrafı")
    
    # Yapılandırılmış veriler (JSON olarak)
    # JSON formatında saklıyoruz çünkü esnek yapı
    
    skills = Column(
        JSON,
        nullable=True,
        doc="Yetenekler listesi: ['Python', 'FastAPI', ...]"
    )
    
    experience = Column(
        JSON,
        nullable=True,
        doc="""Deneyim listesi:
        [
            {
                "title": "Backend Developer",
                "company": "ABC Şirketi",
                "start_date": "2023-01",
                "end_date": "2024-06",
                "duration": "1 yıl 6 ay",
                "description": "..."
            }
        ]
        """
    )
    
    education = Column(
        JSON,
        nullable=True,
        doc="""Eğitim listesi:
        [
            {
                "degree": "Lisans",
                "field": "Bilgisayar Mühendisliği",
                "school": "XYZ Üniversitesi",
                "start_year": 2020,
                "end_year": 2024
            }
        ]
        """
    )
    
    projects = Column(
        JSON,
        nullable=True,
        doc="""Projeler listesi:
        [
            {
                "name": "Proje Adı",
                "technologies": ["Python", "React"],
                "description": "..."
            }
        ]
        """
    )
    
    languages = Column(
        JSON,
        nullable=True,
        doc="Diller: {'Türkçe': 'Ana dil', 'İngilizce': 'B2'}"
    )
    
    certifications = Column(
        JSON,
        nullable=True,
        doc="Sertifikalar listesi"
    )
    
    # Ek bilgiler
    experience_years = Column(
        String(20),
        nullable=True,
        doc="Toplam deneyim süresi"
    )
    
    # =========================================================================
    # META BİLGİLER
    # =========================================================================
    
    is_parsed = Column(
        Boolean,
        default=False,
        doc="LLM tarafından parse edildi mi?"
    )
    
    parse_error = Column(
        Text,
        nullable=True,
        doc="Parse hatası varsa"
    )
    
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        doc="Oluşturulma tarihi"
    )
    
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        doc="Son güncelleme"
    )
    
    # İlişki tanımı
    # user = relationship("User", back_populates="cv")
    
    def __repr__(self):
        return f"<CV(id={self.id}, user_id={self.user_id}, name={self.full_name})>"

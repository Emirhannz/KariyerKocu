"""
KariyerKoçu - CV Analiz Modeli
==============================
CV analiz sonuçlarını veritabanında saklar.
"""

from datetime import datetime
from sqlalchemy import Column, String, DateTime, JSON, ForeignKey, Integer
from sqlalchemy.orm import relationship
from app.database import Base
import uuid


class CVAnalysis(Base):
    """CV Analiz sonuçlarını saklayan model."""
    
    __tablename__ = "cv_analyses"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # İlişkiler
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    cv_id = Column(String, ForeignKey("cvs.id"), nullable=False)
    
    # Profil bilgileri
    sector = Column(String, nullable=False)
    fields = Column(JSON, nullable=False)  # ["yapay_zeka", "backend"]
    experience_level = Column(String, nullable=False)
    
    # Analiz sonuçları
    field_analyses = Column(JSON, nullable=False)  # Tam analiz sonucu
    strongest_field = Column(String, nullable=True)
    action_items = Column(JSON, nullable=True)
    
    # Puanlar (hızlı erişim için)
    overall_score = Column(Integer, nullable=True)  # En yüksek alan puanı
    
    # Zaman damgaları
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<CVAnalysis {self.id} - {self.strongest_field}>"

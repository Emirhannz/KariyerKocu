"""
KariyerKoçu - User Model
========================
Kullanıcı veritabanı modeli.

ÖĞRENME NOKTASI:
- SQLAlchemy model tanımlama
- Column tipleri (String, Boolean, DateTime)
- Varsayılan değerler ve server_default
- Relationship tanımlama (ileride Interview ile)
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    """
    Kullanıcı tablosu.
    
    TABLO YAPISI:
    +------------+------------------+--------------------------------------+
    | Sütun      | Tip              | Açıklama                             |
    +------------+------------------+--------------------------------------+
    | id         | UUID             | Benzersiz kullanıcı ID               |
    | email      | String(255)      | Email adresi (unique)                |
    | password   | String(255)      | Hashlenmiş şifre                     |
    | full_name  | String(100)      | Ad soyad                             |
    | is_active  | Boolean          | Hesap aktif mi?                      |
    | created_at | DateTime         | Kayıt tarihi                         |
    | updated_at | DateTime         | Son güncelleme                       |
    +------------+------------------+--------------------------------------+
    """
    
    __tablename__ = "users"
    
    # Primary Key: UUID kullanıyoruz
    # UUID neden? → Tahmin edilemez, güvenli, dağıtık sistemlerde çakışmaz
    id = Column(
        String(36),  # SQLite için String, PostgreSQL'de UUID kullanılabilir
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        comment="Benzersiz kullanıcı kimliği"
    )
    
    # Email: Unique olmalı (aynı emaille iki hesap olmaz)
    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,  # Sık arama yapılacak, index koy
        comment="Kullanıcı email adresi"
    )
    
    # Şifre: ASLA düz metin saklanmaz, hashlenmiş hali saklanır
    hashed_password = Column(
        String(255),
        nullable=False,
        comment="Bcrypt ile hashlenmiş şifre"
    )
    
    # Tam ad
    full_name = Column(
        String(100),
        nullable=True,
        comment="Kullanıcı ad soyad"
    )
    
    # Telefon numarası
    phone = Column(
        String(20),
        nullable=True,
        comment="Telefon numarası"
    )
    
    # Hesap durumu
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="Hesap aktif mi?"
    )
    
    # Zaman damgaları
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment="Hesap oluşturulma tarihi"
    )
    
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,  # Her update'te otomatik güncellenir
        nullable=False,
        comment="Son güncelleme tarihi"
    )
    
    # =========================================================================
    # KARİYER HEDEFİ
    # =========================================================================
    
    # Hedef sektör (ör: yazilim, fintech, oyun)
    target_sector = Column(
        String(50),
        nullable=True,
        comment="Hedef kariyer sektörü"
    )
    
    # Hedef pozisyon (ör: backend_developer, ml_engineer)
    target_position = Column(
        String(50),
        nullable=True,
        comment="Hedef pozisyon"
    )
    
    # Mevcut tecrübe seviyesi (ör: junior, mid_level, senior)
    experience_level = Column(
        String(50),
        nullable=True,
        comment="Mevcut tecrübe seviyesi"
    )
    
    def __repr__(self):
        """Debug için string gösterimi."""
        return f"<User {self.email}>"


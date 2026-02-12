"""
KariyerKoçu - JWT Utilities
===========================
JWT token oluşturma ve doğrulama fonksiyonları.

ÖĞRENME NOKTASI:
- JWT (JSON Web Token) yapısı: header.payload.signature
- Token oluşturma ve doğrulama
- Expiration time (son kullanma tarihi)
- Password hashing (bcrypt)
"""

from datetime import datetime, timedelta
from typing import Optional
import jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.user import User


# ============================================================================
# ŞİFRE HASHLEME
# ============================================================================

# Bcrypt context: Şifreleri hashlemek ve doğrulamak için
# NEDEN BCRYPT?
# - Yavaş (brute force saldırılarına karşı)
# - Salt ekler (rainbow table saldırılarına karşı)
# - Endüstri standardı
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Şifreyi hashle.
    
    Örnek:
    - Girdi: "password123"
    - Çıktı: "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.V..."
    
    Her seferinde farklı hash üretir (salt sayesinde).
    """
    # Bcrypt 72 byte sınırı var, uzun şifreleri truncate et
    truncated = password[:72] if len(password) > 72 else password
    return pwd_context.hash(truncated)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Şifreyi doğrula.
    
    Kullanıcının girdiği şifre ile veritabanındaki hash eşleşiyor mu?
    """
    return pwd_context.verify(plain_password, hashed_password)


# ============================================================================
# JWT TOKEN İŞLEMLERİ
# ============================================================================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    JWT access token oluştur.
    
    JWT YAPISI:
    ┌─────────────────────────────────────────────────────────────┐
    │ HEADER          │ PAYLOAD           │ SIGNATURE             │
    │ {"alg":"HS256"} │ {"sub":"user_id"} │ HMAC(header+payload) │
    │                 │ {"exp":timestamp} │                       │
    └─────────────────────────────────────────────────────────────┘
    
    Args:
        data: Token içine gömülecek veri (genelde {"sub": user_id})
        expires_delta: Geçerlilik süresi (varsayılan: settings'ten alınır)
    
    Returns:
        JWT token string
    """
    to_encode = data.copy()
    
    # Expiration time hesapla
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.jwt_expire_minutes)
    
    # Payload'a exp (expiration) ekle
    to_encode.update({"exp": expire})
    
    # Token'ı encode et
    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm
    )
    
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    JWT token'ı decode et ve doğrula.
    
    Args:
        token: JWT token string
    
    Returns:
        Token payload (dict) veya None (geçersizse)
    
    Raises:
        - jwt.ExpiredSignatureError: Token süresi dolmuş
        - jwt.InvalidTokenError: Token geçersiz
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm]
        )
        return payload
    except jwt.ExpiredSignatureError:
        # Token süresi dolmuş
        return None
    except jwt.InvalidTokenError:
        # Token geçersiz
        return None


# ============================================================================
# FASTAPI DEPENDENCY: CURRENT USER
# ============================================================================

# HTTP Bearer scheme: "Authorization: Bearer <token>" header'ını parse eder
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Mevcut kullanıcıyı token'dan al.
    
    Bu fonksiyon FastAPI Dependency olarak kullanılır:
    
    @app.get("/profile")
    def get_profile(current_user: User = Depends(get_current_user)):
        return current_user
    
    AKIŞ:
    1. Request header'dan "Authorization: Bearer <token>" al
    2. Token'ı decode et
    3. Token'daki user_id ile veritabanından kullanıcıyı bul
    4. Kullanıcıyı döndür
    
    HATALAR:
    - 401 Unauthorized: Token yok, geçersiz veya süresi dolmuş
    - 401 Unauthorized: Kullanıcı bulunamadı
    """
    token = credentials.credentials
    
    # Token'ı decode et
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token geçersiz veya süresi dolmuş",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # User ID'yi al
    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token geçersiz",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Kullanıcıyı veritabanından bul
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Kullanıcı bulunamadı",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Hesap aktif mi kontrol et
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Hesap devre dışı",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

"""
KariyerKoçu - Authentication Router
====================================
Kayıt ve giriş endpoint'leri.

ÖĞRENME NOKTASI:
- FastAPI Router kullanımı
- Endpoint tanımlama (POST, GET)
- Request body ve response model
- HTTP status codes
- Error handling
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user import (
    UserRegisterRequest,
    UserLoginRequest,
    UserResponse,
    LoginResponse,
    MessageResponse,
)
from app.utils.jwt import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
)


# ============================================================================
# ROUTER OLUŞTURMA
# ============================================================================

# Router: Endpoint'leri gruplamak için
# prefix="/api/auth" → main.py'de eklenecek
router = APIRouter()


# ============================================================================
# KAYIT ENDPOINT'İ
# ============================================================================

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Yeni kullanıcı kaydı",
    description="Email ve şifre ile yeni kullanıcı hesabı oluşturur."
)
async def register(
    request: UserRegisterRequest,
    db: Session = Depends(get_db)
) -> UserResponse:
    """
    Yeni kullanıcı kaydı.
    
    AKIŞ:
    1. Email zaten kayıtlı mı kontrol et
    2. Şifreyi hashle
    3. Yeni kullanıcı oluştur
    4. Veritabanına kaydet
    5. Kullanıcı bilgilerini döndür
    
    Request Body:
    ```json
    {
        "email": "ahmet@example.com",
        "password": "güçlü_şifre_123",
        "full_name": "Ahmet Yılmaz"
    }
    ```
    
    Response (201 Created):
    ```json
    {
        "id": "uuid-string",
        "email": "ahmet@example.com",
        "full_name": "Ahmet Yılmaz",
        "is_active": true,
        "created_at": "2024-01-14T20:00:00"
    }
    ```
    
    Errors:
    - 400 Bad Request: Email zaten kayıtlı
    """
    
    # 1. Email kontrolü
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu email adresi zaten kayıtlı"
        )
    
    # 2. Şifreyi hashle
    hashed_password = hash_password(request.password)
    
    # 3. Yeni kullanıcı oluştur
    new_user = User(
        email=request.email,
        hashed_password=hashed_password,
        full_name=request.full_name,
    )
    
    # 4. Veritabanına kaydet
    db.add(new_user)
    db.commit()
    db.refresh(new_user)  # ID ve created_at gibi otomatik alanları al
    
    # 5. Response döndür
    return new_user


# ============================================================================
# GİRİŞ ENDPOINT'İ
# ============================================================================

@router.post(
    "/login",
    response_model=LoginResponse,
    summary="Kullanıcı girişi",
    description="Email ve şifre ile giriş yapar, JWT token döndürür."
)
async def login(
    request: UserLoginRequest,
    db: Session = Depends(get_db)
) -> LoginResponse:
    """
    Kullanıcı girişi.
    
    AKIŞ:
    1. Email ile kullanıcıyı bul
    2. Şifreyi doğrula
    3. JWT token oluştur
    4. Token ve kullanıcı bilgilerini döndür
    
    Request Body:
    ```json
    {
        "email": "ahmet@example.com",
        "password": "güçlü_şifre_123"
    }
    ```
    
    Response (200 OK):
    ```json
    {
        "access_token": "eyJhbGciOiJIUzI1...",
        "token_type": "bearer",
        "user": {
            "id": "uuid-string",
            "email": "ahmet@example.com",
            ...
        }
    }
    ```
    
    Errors:
    - 401 Unauthorized: Email veya şifre hatalı
    """
    
    # 1. Kullanıcıyı bul
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        # Güvenlik: "Email bulunamadı" deme, "Email veya şifre hatalı" de
        # Böylece saldırgan hangi emaillerin kayıtlı olduğunu öğrenemez
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email veya şifre hatalı"
        )
    
    # 2. Şifreyi doğrula
    if not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email veya şifre hatalı"
        )
    
    # 3. Hesap aktif mi kontrol et
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Hesap devre dışı"
        )
    
    # 4. JWT token oluştur
    access_token = create_access_token(data={"sub": user.id})
    
    # 5. Response döndür
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )


# ============================================================================
# PROFİL ENDPOINT'İ (PROTECTED)
# ============================================================================

@router.get(
    "/me",
    response_model=UserResponse,
    summary="Mevcut kullanıcı bilgileri",
    description="JWT token ile giriş yapmış kullanıcının bilgilerini döndürür."
)
async def get_me(
    current_user: User = Depends(get_current_user)
) -> UserResponse:
    """
    Mevcut kullanıcı bilgilerini getir.
    
    BU ENDPOINT PROTECTED!
    - Authorization header gerekli: "Bearer <token>"
    - Token geçersizse 401 hatası döner
    
    Response (200 OK):
    ```json
    {
        "id": "uuid-string",
        "email": "ahmet@example.com",
        "full_name": "Ahmet Yılmaz",
        "is_active": true,
        "created_at": "2024-01-14T20:00:00"
    }
    ```
    """
    return current_user

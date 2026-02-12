"""
KariyerKoçu - Configuration Settings
=====================================
Tüm uygulama ayarları burada merkezi olarak yönetilir.

ÖĞRENME NOKTASI:
- pydantic-settings ile environment variables okuma
- Type-safe konfigürasyon yönetimi
- .env dosyası ile hassas bilgileri kod dışında tutma
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """
    Uygulama ayarları.
    
    Pydantic BaseSettings kullanarak:
    1. .env dosyasından otomatik okuma
    2. Environment variable'lardan okuma
    3. Varsayılan değer atama
    4. Tip dönüşümü (str → int, bool vb.)
    """
    
    # io Intelligence API
    io_intelligence_api_key: str = ""
    io_intelligence_base_url: str = "https://api.intelligence.io.solutions/api/v1"
    io_intelligence_model: str = "meta-llama/Llama-3.3-70B-Instruct"
    
    # Database
    database_url: str = "postgresql://postgres:password@localhost:5432/karriyer_kocu"
    
    # JWT Authentication
    jwt_secret: str = "change-this-secret-key"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440  # 24 saat
    
    # App
    debug: bool = True
    app_name: str = "KariyerKoçu"
    app_version: str = "1.0.0"
    
    # Groq API (Speech-to-Text için)
    groq_api_key: str = ""
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        # Environment variable isimleri case-insensitive
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """
    Settings nesnesini cache'leyerek döndür.
    
    NEDEN lru_cache?
    - Settings her seferinde dosyadan okumak pahalı
    - Bir kez oku, cache'te tut
    - Performans artışı
    """
    return Settings()


# Global erişim için
settings = get_settings()

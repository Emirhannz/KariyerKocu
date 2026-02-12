"""
KariyerKoçu - Database Configuration
=====================================
Veritabanı bağlantısı ve SQLAlchemy ayarları.

ÖĞRENME NOKTASI:
- SQLAlchemy 2.0 engine
- Session yönetimi
- Dependency Injection pattern (FastAPI ile)
- Development (SQLite) vs Production (PostgreSQL) ayrımı
"""

from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings
import os

# ============================================================================
# DATABASE ENGINE
# ============================================================================

# Development için SQLite, Production için PostgreSQL
# Docker çalışmıyorken de geliştirme yapabilelim

def get_database_url():
    """
    Veritabanı URL'ini belirle.
    
    Docker çalışıyorsa PostgreSQL, değilse SQLite kullanılır.
    """
    db_url = settings.database_url
    
    # PostgreSQL için port kontrolü yap (basit test)
    if db_url.startswith("postgresql"):
        import socket
        from urllib.parse import urlparse
        try:
            # URL'den host'u çıkar
            parsed = urlparse(db_url.replace("postgresql+", "postgresql://").replace("postgresql://", "http://"))
            host = parsed.hostname or "127.0.0.1"
            port = parsed.port or 5432
            
            # Port açık mı kontrol et
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((host, port))
            sock.close()
            
            if result == 0:
                print(f"✅ PostgreSQL ({host}:{port}) bağlantısı hazır")
                return db_url
            else:
                raise Exception(f"Port kapalı: {host}:{port}")
        except Exception as e:
            if settings.debug:
                sqlite_path = os.path.join(
                    os.path.dirname(os.path.dirname(__file__)),
                    "karriyer_kocu.db"
                )
                print(f"⚠️  PostgreSQL erişilemez ({e}), SQLite kullanılıyor: {sqlite_path}")
                return f"sqlite:///{sqlite_path}"
            else:
                raise
    
    return db_url

# Veritabanı URL'ini al
DATABASE_URL = get_database_url()

# SQLite için özel ayarlar
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    # SQLite için: check_same_thread=False (multi-thread için gerekli)
    connect_args = {"check_same_thread": False}

# Engine: Veritabanı bağlantı havuzu (connection pool)
engine = create_engine(
    DATABASE_URL,
    echo=settings.debug,  # SQL sorgularını logla (debug modda)
    connect_args=connect_args,
)

# ============================================================================
# SESSION FACTORY
# ============================================================================

# SessionLocal: Her request için yeni session oluşturacak factory
# autocommit=False: Manuel commit gerekli (transaction kontrolü)
# autoflush=False: Explicit flush gerekli (performans için)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# ============================================================================
# BASE MODEL
# ============================================================================

# Tüm modellerimiz bu Base'den türeyecek
Base = declarative_base()


# ============================================================================
# DEPENDENCY INJECTION
# ============================================================================

def get_db():
    """
    FastAPI Dependency: Her request için veritabanı session'ı sağlar.
    
    Kullanım:
        @app.get("/items")
        def read_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    
    NEDEN yield?
    - try/finally ile session'ın her durumda kapatılmasını garanti eder
    - Request bittiğinde otomatik cleanup
    - Memory leak önlenir
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

"""
KariyerKoçu - Main Application Entry Point
==========================================
FastAPI uygulamasının ana giriş noktası.

ÖĞRENME NOKTASI:
- FastAPI app oluşturma
- CORS middleware (Frontend erişimi için)
- Router'ları include etme
- Lifespan events (startup/shutdown)
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine, Base

# Router imports
from app.routers import auth, llm, cv, analysis, interview, user, chat, jobs, cover_letter, interview_voice

# Model imports (tablolar oluşturulsun diye)
from app.models.user import User
from app.models.cv import CV
from app.models.analysis import CVAnalysis
from app.models.interview import InterviewSession, InterviewQuestion, InterviewAnswer


# ============================================================================
# LIFESPAN EVENTS
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Uygulama başlangıç ve bitiş olayları.
    
    STARTUP (yield öncesi):
    - Veritabanı tablolarını oluştur
    - Bağlantıları başlat
    
    SHUTDOWN (yield sonrası):
    - Bağlantıları kapat
    - Cleanup işlemleri
    """
    # Startup
    print("🚀 KariyerKoçu Backend başlatılıyor...")
    
    # Veritabanı tablolarını oluştur (development için)
    # Production'da Alembic migration kullanılır
    Base.metadata.create_all(bind=engine)
    print("✅ Veritabanı tabloları hazır")
    
    yield  # Uygulama çalışıyor
    
    # Shutdown
    print("👋 KariyerKoçu Backend kapatılıyor...")


# ============================================================================
# FASTAPI APP
# ============================================================================

app = FastAPI(
    title=settings.app_name,
    description="""
    ## KariyerKoçu API
    
    Yapay zeka destekli kariyer koçluk platformu.
    
    ### Özellikler:
    - 📄 CV analizi ve profil çıkarma
    - 🎯 Pozisyona özel mülakat simülasyonu
    - 📊 Anlık değerlendirme ve feedback
    """,
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/docs",      # Swagger UI
    redoc_url="/redoc",    # ReDoc
)


# ============================================================================
# CORS MIDDLEWARE
# ============================================================================

# CORS: Cross-Origin Resource Sharing
# Frontend (localhost:3000) Backend'e (localhost:8000) erişebilsin
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",    # React dev server
        "http://127.0.0.1:3000",
        "http://localhost:5173",    # Vite dev server
        "http://127.0.0.1:5173",
        "http://localhost:8080",    # Test server
        "http://127.0.0.1:8080",
        "http://localhost",         # Docker Frontend (Port 80)
        "http://127.0.0.1",
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Tüm HTTP metodları (GET, POST, PUT, DELETE, vs.)
    allow_headers=["*"],  # Tüm header'lar
)


# ============================================================================
# ROUTES
# ============================================================================

@app.get("/", tags=["Root"])
async def root():
    """Ana sayfa - API bilgisi döndürür."""
    return {
        "message": "Hoş geldiniz! KariyerKoçu API",
        "version": settings.app_version,
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Sağlık kontrolü endpoint'i.
    
    NEDEN ÖNEMLİ?
    - Docker container'ın çalıştığını kontrol eder
    - Load balancer'lar bu endpoint'i kullanır
    - Kubernetes health probe'ları için gerekli
    """
    return {
        "status": "healthy",
        "app": settings.app_name,
        "debug": settings.debug,
    }


# Router'ları ekle
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(llm.router, prefix="/api/llm", tags=["LLM"])
app.include_router(cv.router, prefix="/api/cv", tags=["CV"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["Analysis"])
app.include_router(interview.router, prefix="/api/interview", tags=["Interview"])
app.include_router(user.router, prefix="/api/user", tags=["User"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(jobs.router, prefix="/api", tags=["Job Search"])
app.include_router(cover_letter.router, prefix="/api/cover-letter", tags=["Cover Letter"])
app.include_router(interview_voice.router, prefix="/api/interview/voice", tags=["Voice Interview"])


# ============================================================================
# DEVELOPMENT SERVER
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    # Development için: python main.py
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Kod değişince otomatik restart
    )

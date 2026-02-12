# ==============================================================================
# Backend Dockerfile
# ==============================================================================
#
# ÖĞRENME NOKTASI:
# - Multi-stage build pattern
# - Layer caching optimization
# - Security best practices
# ==============================================================================

FROM python:3.11-slim

# Metadata
LABEL maintainer="KariyerKoçu Team"
LABEL description="KariyerKoçu Backend API"

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set working directory
WORKDIR /app

# Install system dependencies
# Not: Vision model kullanacaksak Tesseract'a gerek yok
RUN apt-get update && apt-get install -y \
    # PostgreSQL client (psycopg2 için)
    libpq-dev \
    # Build tools
    gcc \
    # PDF processing (gerekirse)
    poppler-utils \
    # Chromium ve ChromeDriver (Kariyer.net X-Ray için)
    chromium \
    chromium-driver \
    # Cleanup
    && rm -rf /var/lib/apt/lists/*

# Selenium için Chrome ayarları
ENV CHROME_BIN=/usr/bin/chromium \
    CHROMEDRIVER_PATH=/usr/bin/chromedriver

# Copy requirements first (layer caching)
# Bu sayede requirements değişmedikçe pip install tekrar çalışmaz
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
# Production için: gunicorn kullanılır
# Development için: uvicorn --reload
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

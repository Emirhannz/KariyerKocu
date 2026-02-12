# -*- coding: utf-8 -*-
"""
Cache Service
=============
In-memory cache servisi - Redis'e gerek kalmadan hızlı caching.

Kullanım Alanları:
- İş arama sonuçları (kullanıcıya özel)
- Mülakat soruları (alan + pozisyona göre)
- LLM yanıtları (aynı prompt için)
"""

from datetime import datetime, timedelta
from typing import Any, Optional, Dict, Callable
import threading
import hashlib
import json
from functools import wraps


class CacheEntry:
    """Tek bir cache girdisi."""
    def __init__(self, value: Any, ttl_seconds: int):
        self.value = value
        self.expires_at = datetime.now() + timedelta(seconds=ttl_seconds)
        self.created_at = datetime.now()
        self.hits = 0
    
    def is_expired(self) -> bool:
        return datetime.now() > self.expires_at
    
    def get(self) -> Any:
        self.hits += 1
        return self.value


class CacheService:
    """
    Thread-safe in-memory cache servisi.
    
    Özellikler:
    - TTL (Time-to-Live) desteği
    - Otomatik temizlik (expired entries)
    - Thread-safe operasyonlar
    - İstatistik takibi
    """
    
    def __init__(self, max_entries: int = 1000, cleanup_interval_minutes: int = 10):
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = threading.RLock()
        self._max_entries = max_entries
        self._stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0,
            "cleanups": 0,
        }
        self._last_cleanup = datetime.now()
        self._cleanup_interval = timedelta(minutes=cleanup_interval_minutes)
    
    def _make_key(self, *args, **kwargs) -> str:
        """Argümanlardan benzersiz cache key oluştur."""
        key_parts = [str(arg) for arg in args]
        key_parts.extend([f"{k}={v}" for k, v in sorted(kwargs.items())])
        key_string = ":".join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """
        Cache'den değer al.
        
        Args:
            key: Cache anahtarı
            
        Returns:
            Değer veya None (bulunamadı/expired)
        """
        self._maybe_cleanup()
        
        with self._lock:
            entry = self._cache.get(key)
            
            if entry is None:
                self._stats["misses"] += 1
                return None
            
            if entry.is_expired():
                del self._cache[key]
                self._stats["misses"] += 1
                return None
            
            self._stats["hits"] += 1
            return entry.get()
    
    def set(self, key: str, value: Any, ttl_seconds: int = 3600) -> None:
        """
        Cache'e değer kaydet.
        
        Args:
            key: Cache anahtarı
            value: Kaydedilecek değer
            ttl_seconds: Geçerlilik süresi (saniye, varsayılan 1 saat)
        """
        with self._lock:
            # Max entries kontrolü
            if len(self._cache) >= self._max_entries:
                self._evict_oldest()
            
            self._cache[key] = CacheEntry(value, ttl_seconds)
            self._stats["sets"] += 1
    
    def delete(self, key: str) -> bool:
        """Cache'den sil."""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                self._stats["deletes"] += 1
                return True
            return False
    
    def clear(self) -> int:
        """Tüm cache'i temizle."""
        with self._lock:
            count = len(self._cache)
            self._cache.clear()
            return count
    
    def exists(self, key: str) -> bool:
        """Key var mı kontrol et."""
        with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                return False
            if entry.is_expired():
                del self._cache[key]
                return False
            return True
    
    def get_or_set(self, key: str, factory: Callable, ttl_seconds: int = 3600) -> Any:
        """
        Cache'de varsa al, yoksa factory ile oluştur ve kaydet.
        
        Args:
            key: Cache anahtarı
            factory: Değer oluşturma fonksiyonu (lazy evaluation)
            ttl_seconds: Geçerlilik süresi
            
        Returns:
            Değer (cache'den veya yeni oluşturulmuş)
        """
        value = self.get(key)
        if value is not None:
            return value
        
        # Factory çağır ve kaydet
        new_value = factory()
        self.set(key, new_value, ttl_seconds)
        return new_value
    
    async def get_or_set_async(self, key: str, factory: Callable, ttl_seconds: int = 3600) -> Any:
        """Async versiyon - async factory destekler."""
        value = self.get(key)
        if value is not None:
            return value
        
        new_value = await factory()
        self.set(key, new_value, ttl_seconds)
        return new_value
    
    def _evict_oldest(self) -> None:
        """En eski entry'yi sil (LRU benzeri)."""
        if not self._cache:
            return
        
        # En eski created_at'a sahip olanı bul
        oldest_key = min(
            self._cache.keys(),
            key=lambda k: self._cache[k].created_at
        )
        del self._cache[oldest_key]
    
    def _maybe_cleanup(self) -> None:
        """Belirli aralıklarla expired entry'leri temizle."""
        if datetime.now() - self._last_cleanup < self._cleanup_interval:
            return
        
        with self._lock:
            expired_keys = [
                key for key, entry in self._cache.items()
                if entry.is_expired()
            ]
            
            for key in expired_keys:
                del self._cache[key]
            
            self._stats["cleanups"] += 1
            self._last_cleanup = datetime.now()
    
    def get_stats(self) -> Dict:
        """Cache istatistiklerini döndür."""
        with self._lock:
            total_requests = self._stats["hits"] + self._stats["misses"]
            hit_rate = (self._stats["hits"] / total_requests * 100) if total_requests > 0 else 0
            
            return {
                **self._stats,
                "current_entries": len(self._cache),
                "max_entries": self._max_entries,
                "hit_rate_percent": round(hit_rate, 2),
            }
    
    def get_keys(self, pattern: str = None) -> list:
        """Tüm key'leri listele (opsiyonel pattern ile filtrele)."""
        with self._lock:
            keys = list(self._cache.keys())
            if pattern:
                keys = [k for k in keys if pattern in k]
            return keys


def cached(ttl_seconds: int = 3600, key_prefix: str = ""):
    """
    Decorator: Fonksiyon sonuçlarını cache'le.
    
    Kullanım:
        @cached(ttl_seconds=1800, key_prefix="jobs")
        async def search_jobs(query: str, city: str):
            ...
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Key oluştur
            key_parts = [key_prefix, func.__name__]
            key_parts.extend([str(arg) for arg in args])
            key_parts.extend([f"{k}={v}" for k, v in sorted(kwargs.items())])
            cache_key = ":".join(filter(None, key_parts))
            
            # Cache kontrol
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Fonksiyonu çağır ve cache'le
            result = await func(*args, **kwargs)
            cache.set(cache_key, result, ttl_seconds)
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            key_parts = [key_prefix, func.__name__]
            key_parts.extend([str(arg) for arg in args])
            key_parts.extend([f"{k}={v}" for k, v in sorted(kwargs.items())])
            cache_key = ":".join(filter(None, key_parts))
            
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl_seconds)
            return result
        
        # Async mı sync mi kontrol et
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator


# Global cache instance
cache = CacheService(max_entries=500, cleanup_interval_minutes=5)


# Önceden tanımlanmış cache key'leri
class CacheKeys:
    """Standart cache key formatları."""
    
    @staticmethod
    def job_search(user_id: int, query: str, city: str = None) -> str:
        city_part = city or "any"
        return f"jobs:search:{user_id}:{query}:{city_part}"
    
    @staticmethod
    def job_recommendations(user_id: int) -> str:
        return f"jobs:recommendations:{user_id}"
    
    @staticmethod
    def interview_questions(sector: str, position: str, level: str) -> str:
        return f"interview:questions:{sector}:{position}:{level}"
    
    @staticmethod
    def user_cv_analysis(user_id: int) -> str:
        return f"cv:analysis:{user_id}"
    
    @staticmethod
    def ats_simulation(cv_hash: str) -> str:
        return f"ats:simulation:{cv_hash}"

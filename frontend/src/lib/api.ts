import axios, { AxiosError } from 'axios';

// API Base URL
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

// Hata mesajları (Türkçe)
const ERROR_MESSAGES: Record<number, string> = {
  400: 'Geçersiz istek. Lütfen bilgilerinizi kontrol edin.',
  401: 'Oturum süreniz doldu. Lütfen tekrar giriş yapın.',
  403: 'Bu işlem için yetkiniz bulunmuyor.',
  404: 'İstenen kaynak bulunamadı.',
  422: 'Girilen bilgiler geçersiz.',
  429: 'Çok fazla istek gönderildi. Lütfen biraz bekleyin.',
  500: 'Sunucu hatası. Lütfen daha sonra tekrar deneyin.',
  502: 'Sunucu geçici olarak kullanılamıyor.',
  503: 'Servis şu anda kullanılamıyor. Lütfen daha sonra tekrar deneyin.',
};

// Axios instance
export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 90000, // 90 saniye timeout - LLM ve TTS işlemleri için
});

// Request interceptor - JWT token ekle
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor - Gelişmiş hata yönetimi
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    // Network hatası (internet yok veya sunucu kapalı)
    if (!error.response) {
      const networkError = new Error('Sunucuya bağlanılamadı. İnternet bağlantınızı kontrol edin.');
      return Promise.reject(networkError);
    }
    
    const status = error.response.status;
    
    // 401 - Unauthorized
    if (status === 401) {
      const currentPath = window.location.pathname;
      const isAuthPage = currentPath === '/login' || currentPath === '/register';
      
      if (!isAuthPage) {
        localStorage.removeItem('token');
        window.location.href = '/login';
      }
    }
    
    // API'den gelen hata mesajını kullan, yoksa varsayılan mesaj
    const responseData = error.response.data as { detail?: string; message?: string };
    const apiMessage = responseData?.detail || responseData?.message;
    const defaultMessage = ERROR_MESSAGES[status] || 'Beklenmeyen bir hata oluştu.';
    
    // Hata mesajını güncelle
    const enhancedError = new Error(apiMessage || defaultMessage);
    (enhancedError as any).status = status;
    (enhancedError as any).originalError = error;
    
    return Promise.reject(enhancedError);
  }
);

/**
 * API hata mesajını çıkar
 */
export function getErrorMessage(error: unknown): string {
  if (error instanceof Error) {
    return error.message;
  }
  if (typeof error === 'string') {
    return error;
  }
  return 'Beklenmeyen bir hata oluştu.';
}

/**
 * API hatası mı kontrol et
 */
export function isApiError(error: unknown): error is Error & { status: number } {
  return error instanceof Error && 'status' in error;
}

export default api;

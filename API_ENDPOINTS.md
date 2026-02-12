# 🔌 KariyerKoçu API Endpoint Listesi

> **Toplam: 57 Endpoint**  
> **Base URL**: `http://localhost:8000/api`

---

## 📋 İçindekiler

- [🔐 Authentication (3 endpoint)](#-authentication)
- [👤 User (6 endpoint)](#-user)
- [📄 CV (5 endpoint)](#-cv)
- [📊 Analysis (11 endpoint)](#-analysis)
- [🎤 Interview - Text (9 endpoint)](#-interview---text)
- [🎙️ Interview - Voice (6 endpoint)](#️-interview---voice)
- [💬 Chat (3 endpoint)](#-chat)
- [🔍 Job Search (7 endpoint)](#-job-search)
- [✉️ Cover Letter (2 endpoint)](#️-cover-letter)
- [🧠 LLM (3 endpoint)](#-llm)
- [🏠 Root (2 endpoint)](#-root)

---

## 🔐 Authentication

| Method | Endpoint | Açıklama |
|--------|----------|----------|
| `POST` | `/api/auth/register` | Yeni kullanıcı kaydı oluştur |
| `POST` | `/api/auth/login` | Kullanıcı girişi, JWT token al |
| `GET` | `/api/auth/me` | Mevcut kullanıcı bilgilerini getir |

---

## 👤 User

| Method | Endpoint | Açıklama |
|--------|----------|----------|
| `GET` | `/api/user/profile` | Kullanıcı profil bilgilerini getir |
| `PUT` | `/api/user/profile` | Profil bilgilerini güncelle |
| `PUT` | `/api/user/profile/password` | Şifre değiştir |
| `PUT` | `/api/user/profile/career-goals` | Kariyer hedeflerini güncelle |
| `GET` | `/api/user/dashboard` | Dashboard verilerini getir (CV özeti, mülakat istatistikleri) |
| `GET` | `/api/user/cv-details` | CV'den parse edilen tüm detaylı bilgiler |

---

## 📄 CV

| Method | Endpoint | Açıklama |
|--------|----------|----------|
| `POST` | `/api/cv/upload` | PDF formatında CV yükle ve otomatik parse et |
| `GET` | `/api/cv/me` | Kullanıcının yüklü CV'sini getir |
| `DELETE` | `/api/cv/me` | Kullanıcının CV'sini sil |
| `POST` | `/api/cv/reparse` | Mevcut CV'yi yeniden LLM ile parse et |
| `PUT` | `/api/cv/update-info` | CV bilgilerini manuel olarak güncelle |

---

## 📊 Analysis

| Method | Endpoint | Açıklama |
|--------|----------|----------|
| `GET` | `/api/analysis/config` | Analiz için dropdown verilerini getir (sektörler, alanlar, seviyeler) |
| `GET` | `/api/analysis/config/fields/{sector_id}` | Belirli sektöre ait alanları getir |
| `POST` | `/api/analysis/analyze` | CV'yi hedef pozisyona göre analiz et (100 üzerinden puanlama) |
| `GET` | `/api/analysis/my-cv-summary` | Kullanıcının CV'sinin özet bilgileri |
| `GET` | `/api/analysis/list` | Son 3 analizi listele |
| `GET` | `/api/analysis/detail/{analysis_id}` | Belirli analizin detaylarını getir |
| `DELETE` | `/api/analysis/{analysis_id}` | Belirli bir analizi sil |
| `GET` | `/api/analysis/recommend` | Kişiselleştirilmiş kariyer tavsiyeleri al |
| `POST` | `/api/analysis/ats-simulation` | CV'yi ATS (Applicant Tracking System) ile test et |
| `GET` | `/api/analysis/ats-simulation/from-cv` | Kayıtlı CV için ATS simülasyonu |
| `POST` | `/api/analysis/ats-simulation/test-file` | Geçici dosya ile ATS testi (kaydetmeden) |

---

## 🎤 Interview - Text

| Method | Endpoint | Açıklama |
|--------|----------|----------|
| `GET` | `/api/interview/config` | Mülakat konfigürasyonu (pozisyonlar, seviyeler, türler) |
| `POST` | `/api/interview/start` | Yeni mülakat oturumu başlat |
| `GET` | `/api/interview/question` | Sonraki soruyu al |
| `POST` | `/api/interview/answer` | Soruya cevap gönder |
| `POST` | `/api/interview/complete` | Mülakatı tamamla ve rapor oluştur |
| `GET` | `/api/interview/report/{session_id}` | Mülakat sonuç raporunu getir |
| `GET` | `/api/interview/history` | Geçmiş mülakatları listele |
| `DELETE` | `/api/interview/history/{session_id}` | Geçmiş mülakatı sil |
| `DELETE` | `/api/interview/cancel` | Aktif mülakatı iptal et |

---

## 🎙️ Interview - Voice

| Method | Endpoint | Açıklama |
|--------|----------|----------|
| `POST` | `/api/interview/voice/tts` | Metni sese çevir (Edge-TTS) |
| `POST` | `/api/interview/voice/tts/question/{session_id}` | Mülakat sorusunu sesli oku |
| `POST` | `/api/interview/voice/tts/feedback` | Değerlendirme metnini sesli oku |
| `POST` | `/api/interview/voice/stt` | Ses dosyasını metne çevir (Groq Whisper) |
| `POST` | `/api/interview/voice/voice-answer/{session_id}` | Sesli cevap gönder (STT + değerlendirme) |
| `GET` | `/api/interview/voice/voices` | Mevcut Türkçe TTS seslerini listele |

---

## 💬 Chat

| Method | Endpoint | Açıklama |
|--------|----------|----------|
| `GET` | `/api/chat/greeting` | Kullanıcıya özel karşılama mesajı |
| `POST` | `/api/chat/message` | Chatbot'a mesaj gönder (context-aware) |
| `GET` | `/api/chat/options` | Chat için form seçenekleri |

---

## 🔍 Job Search

| Method | Endpoint | Açıklama |
|--------|----------|----------|
| `POST` | `/api/jobs/search` | JobSpy ile iş ara (LinkedIn, Indeed, Glassdoor) |
| `GET` | `/api/jobs/options` | İş arama seçenekleri (platformlar, lokasyonlar) |
| `GET` | `/api/jobs/cities/{country}` | Ülkeye göre şehirleri getir |
| `GET` | `/api/jobs/test` | Test endpoint - Indeed'den örnek ilanlar |
| `GET` | `/api/jobs/professions` | Meslek grupları ve alanları |
| `POST` | `/api/jobs/search-custom` | Kariyer.net X-Ray araması |
| `POST` | `/api/jobs/skill-gap` | İş ilanı ile CV beceri karşılaştırması |

---

## ✉️ Cover Letter

| Method | Endpoint | Açıklama |
|--------|----------|----------|
| `POST` | `/api/cover-letter/cover-letter` | İş ilanına özel ön yazı oluştur |
| `POST` | `/api/cover-letter/email` | Başvuru e-maili oluştur |

---

## 🧠 LLM

| Method | Endpoint | Açıklama |
|--------|----------|----------|
| `POST` | `/api/llm/chat` | Direkt LLM ile sohbet |
| `GET` | `/api/llm/test` | io Intelligence API bağlantı testi |
| `POST` | `/api/llm/interview-question` | Mülakat sorusu üret (test amaçlı) |

---

## 🏠 Root

| Method | Endpoint | Açıklama |
|--------|----------|----------|
| `GET` | `/` | API bilgisi |
| `GET` | `/health` | Sağlık kontrolü (Docker health check) |

---

## 📚 Ek Bilgiler

### Swagger Dokümantasyonu
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Authentication
Tüm endpoint'ler (hariç: `/`, `/health`, `/api/auth/register`, `/api/auth/login`) JWT token gerektirir.

**Header formatı:**
```
Authorization: Bearer <token>
```

### Örnek İstekler

**Login:**
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "123456"}'
```

**CV Yükleme:**
```bash
curl -X POST http://localhost:8000/api/cv/upload \
  -H "Authorization: Bearer <token>" \
  -F "file=@cv.pdf"
```

**Mülakat Başlatma:**
```bash
curl -X POST http://localhost:8000/api/interview/start \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"position": "backend_developer", "experience_level": "junior", "question_count": 5}'
```

---

## 🔧 Kullanılan Teknolojiler

| Servis | Teknoloji | Açıklama |
|--------|-----------|----------|
| LLM | io Intelligence API | Llama-3.3-70B-Instruct modeli |
| TTS | Edge-TTS | Türkçe sesli okuma |
| STT | Groq Whisper | Sesli cevap tanıma |
| Job Search | JobSpy + Kariyer.net X-Ray | Çoklu platform iş arama |
| Database | PostgreSQL | Veri depolama |
| Cache | In-memory | LLM yanıt cache |

---

*Son güncelleme: 26 Ocak 2026*

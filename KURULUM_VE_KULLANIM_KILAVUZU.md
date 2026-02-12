KARİYERKOÇU - YAPAY ZEKA DESTEKLİ KARİYER KOÇLUK PLATFORMU
KURULUM VE KULLANIM KILAVUZU

════════════════════════════════════════════════════════════════════════════════
GİRİŞ VE PROJE TANIMI
════════════════════════════════════════════════════════════════════════════════

Bu platform, iş arayanların CV'lerini analiz eden, mülakat simülasyonu yapan ve kişiselleştirilmiş kariyer tavsiyeleri sunan yapay zeka destekli bir sistemdir. Proje, backend tarafında FastAPI, frontend tarafında React ve TypeScript kullanılarak geliştirilmiştir. Veritabanı olarak PostgreSQL tercih edilmiştir.

Sistemin temel özellikleri şunlardır:

- CV yükleme ve otomatik parse işlemi (PyMuPDF ile PDF okuma)
- LLM destekli yapılandırılmış CV analizi
- ATS (Applicant Tracking System) uyumluluk simülasyonu
- Bağlamsal CV değerlendirmesi (aynı CV, farklı profiller için farklı puanlanır)
- Pozisyon ve deneyim seviyesine özel mülakat simülasyonu
- Sesli mülakat desteği (Groq Whisper ve Edge-TTS)
- İş ilanı arama ve skill gap analizi
- Akıllı ön yazı ve e-mail oluşturma
- Context-aware chatbot

════════════════════════════════════════════════════════════════════════════════
KURULUM
════════════════════════════════════════════════════════════════════════════════

Sistemi kurmak için iki yol bulunmaktadır: Docker ile veya manuel kurulum.

────────────────────────────────────────────────────────────────────────────────
DOCKER İLE KURULUM (ÖNERİLEN)
────────────────────────────────────────────────────────────────────────────────

Docker yöntemi, tüm bağımlılıkları ve servisleri otomatik olarak kurup ayağa kaldırdığı için en pratik yöntemdir.

Gereksinimler:

- Docker Desktop (Windows/Mac) veya Docker Engine (Linux)
- Git

Adımlar:

1. Projeyi klonlayın:

git clone <repository-url>
cd hackathon

2. Environment dosyasını oluşturun:

Backend klasöründeki .env.example dosyasını .env olarak kopyalayın ve API anahtarlarınızı doldurun. Dosya içeriği şu şekilde olmalıdır:

IO_INTELLIGENCE_API_KEY=your_api_key_here
IO_INTELLIGENCE_BASE_URL=https://api.intelligence.io.solutions/api/v1
IO_INTELLIGENCE_MODEL=meta-llama/Llama-3.3-70B-Instruct
GROQ_API_KEY=your_groq_api_key_here
DATABASE_URL=postgresql://postgres:password@db:5432/karriyer_kocu
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=karriyer_kocu
JWT_SECRET=your-super-secret-jwt-key-change-this-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440
DEBUG=True

3. Docker servisleri başlatın:

docker-compose up -d

Bu komut üç container başlatır:

- PostgreSQL veritabanı (port 5435)
- FastAPI backend (port 8000)
- React frontend (port 80)

4. Veritabanı tablolarını oluşturun:

Backend container içine girin ve tabloları oluşturun:

docker exec -it caco_backend bash
python -c "from app.database import Base, engine; Base.metadata.create_all(bind=engine)"

Alternatif olarak, SQL dosyalarını kullanabilirsiniz:

docker exec -i caco_db psql -U postgres -d karriyer_kocu < backend/create_tables.sql

5. Sisteme erişin:

Frontend: http://localhost
Backend API: http://localhost:8000
API Dokümantasyonu: http://localhost:8000/docs

────────────────────────────────────────────────────────────────────────────────
VERİTABANI ERİŞİM BİLGİLERİ
────────────────────────────────────────────────────────────────────────────────

Veritabanına doğrudan erişmek isteyenler için bağlantı bilgileri:

Host: localhost
Port: 5435
Database: karriyer_kocu
User: postgres
Password: password

DBeaver, TablePlus, pgAdmin gibi araçlarla bağlanabilirsiniz.

Terminal üzerinden bağlanmak için:

docker exec -it caco_db psql -U postgres -d karriyer_kocu

Örnek SQL sorguları:

# Tüm kullanıcıları listele

SELECT id, email, full_name, created_at FROM users;

# Mülakat istatistikleri

SELECT u.email, COUNT(s.id) as mulakat_sayisi, AVG(s.average_score) as ortalama
FROM users u
LEFT JOIN interview_sessions s ON u.id = s.user_id
GROUP BY u.email;

# CV'leri listele

SELECT id, original_filename, full_name, is_parsed, created_at FROM cvs;

────────────────────────────────────────────────────────────────────────────────
MANUEL KURULUM
────────────────────────────────────────────────────────────────────────────────

Manuel kurulum için her servisin ayrı ayrı kurulması gerekir.

BACKEND KURULUMU:

1. Python 3.10 veya üzeri sürüm gereklidir.

2. Virtual environment oluşturun:

cd backend
python -m venv venv
venv\Scripts\activate (Windows)
source venv/bin/activate (Linux/Mac)

3. Bağımlılıkları yükleyin:

pip install -r requirements.txt

4. PostgreSQL kurulumu:

PostgreSQL 15 kurun ve bir veritabanı oluşturun:

createdb karriyer_kocu

5. .env dosyasını oluşturun (yukarıdaki gibi).

6. Tabloları oluşturun:

python -c "from app.database import Base, engine; Base.metadata.create_all(bind=engine)"

7. Backend'i başlatın:

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

FRONTEND KURULUMU:

1. Node.js 18 veya üzeri sürüm gereklidir.

2. Bağımlılıkları yükleyin:

cd frontend
npm install

3. Geliştirme sunucusunu başlatın:

npm run dev

Frontend http://localhost:5173 adresinde çalışacaktır.

4. Production build için:

npm run build

Build dosyaları dist klasörüne oluşturulur.

════════════════════════════════════════════════════════════════════════════════
SİSTEM MİMARİSİ VE DOSYA YAPISI
════════════════════════════════════════════════════════════════════════════════

Proje, backend ve frontend olmak üzere iki ana bölümden oluşmaktadır.

BACKEND YAPISI (FastAPI):

app/
├── main.py # FastAPI uygulamasının giriş noktası
├── config.py # Tüm uygulama ayarları (API keys, DB URL vb.)
├── database.py # SQLAlchemy database bağlantısı
├── models/ # SQLAlchemy ORM modelleri
│ ├── user.py # Kullanıcı modeli
│ ├── cv.py # CV modeli
│ ├── analysis.py # CV analiz sonuçları
│ └── interview.py # Mülakat oturumları, sorular, cevaplar
├── schemas/ # Pydantic şemaları (request/response validasyonu)
│ ├── user.py
│ ├── cv.py
│ ├── analysis.py
│ ├── interview.py
│ ├── job.py
│ └── chat.py
├── routers/ # API endpoint'leri
│ ├── auth.py # Kayıt, giriş, token
│ ├── cv.py # CV yükleme, listeleme
│ ├── analysis.py # CV analizi
│ ├── interview.py # Metin tabanlı mülakat
│ ├── interview_voice.py # Sesli mülakat
│ ├── jobs.py # İş ilanı arama
│ ├── cover_letter.py # Ön yazı oluşturma
│ ├── chat.py # Chatbot
│ ├── user.py # Kullanıcı profili
│ └── llm.py # LLM test endpoint
├── services/ # İş mantığı katmanı
│ ├── llm_service.py # LLM API entegrasyonu
│ ├── cv_service.py # CV parse ve işleme
│ ├── cv_analysis_service.py # CV analizi
│ ├── cv_pre_analysis.py # Rule-based ön analiz
│ ├── ats_simulation_service.py # ATS uyumluluk kontrolü
│ ├── recommendation_service.py # Kariyer tavsiyeleri
│ ├── interview_service.py # Mülakat yönetimi
│ ├── speech_service.py # Ses tanıma (Groq Whisper)
│ ├── tts_service.py # Metin okuma (Edge-TTS)
│ ├── job_search_service.py # İş ilanı arama servisi
│ ├── skill_matcher.py # Skill eşleştirme
│ ├── cover_letter_service.py # Ön yazı oluşturma
│ └── chat_service.py # Chatbot servisi
├── career/ # Kariyer bilgi bankası
│ ├── career_config.py # Sektörler, alanlar, beklentiler
│ ├── career_knowledge.py # Öğrenme yolları, sertifikalar
│ └── interview_config.py # Mülakat sektörleri, pozisyonlar
└── utils/
└── jwt.py # JWT token işlemleri

FRONTEND YAPISI (React + TypeScript):

src/
├── main.tsx # React uygulamasının giriş noktası
├── App.tsx # Ana component ve routing
├── components/ # Yeniden kullanılabilir UI componentleri
│ ├── layout/ # Genel layout bileşenleri
│ │ ├── Header.tsx # Üst menü
│ │ ├── MainLayout.tsx # Ana sayfa düzeni
│ │ └── ProtectedRoute.tsx # Korumalı route wrapper
│ ├── ui/ # Temel UI bileşenleri
│ │ ├── Toast.tsx
│ │ └── Skeleton.tsx
│ ├── chat/
│ │ └── ChatWidget.tsx # Sağ alt köşe chatbot
│ └── interview/
│ ├── VoiceInput.tsx # Ses kayıt butonu
│ └── VoiceRecordingModal.tsx # Kayıt modal'ı
├── features/ # Sayfa bazlı feature modülleri
│ ├── auth/
│ │ └── AuthPages.tsx # Giriş/Kayıt
│ ├── dashboard/
│ │ └── DashboardPage.tsx # Ana sayfa
│ ├── cv/
│ │ ├── CVUploadPage.tsx # CV yükleme
│ │ ├── CVAnalysisPage.tsx # Analiz ayarları
│ │ ├── AnalysisResultPage.tsx # Analiz sonuçları
│ │ ├── ATSSimulationSection.tsx # ATS raporu
│ │ └── RecommendationsPage.tsx # Tavsiyeler
│ ├── interview/
│ │ ├── InterviewSetupPage.tsx # Mülakat ayarları
│ │ ├── InterviewPage.tsx # Metin mülakat
│ │ ├── VoiceInterviewPage.tsx # Sesli mülakat
│ │ ├── InterviewHistoryPage.tsx # Geçmiş mülakatlar
│ │ └── InterviewReportPage.tsx # Mülakat raporu
│ ├── jobs/
│ │ └── JobSearchPage.tsx # İş arama
│ ├── cover-letter/
│ │ └── CoverLetterPage.tsx # Ön yazı oluşturma
│ └── profile/
│ └── ProfilePage.tsx # Kullanıcı profili
├── stores/ # Zustand state management
│ ├── authStore.ts # Kullanıcı auth state
│ └── themeStore.ts # Tema ayarları
├── lib/
│ ├── api.ts # Axios instance ve API fonksiyonları
│ └── utils.ts # Yardımcı fonksiyonlar
└── types/
└── index.ts # TypeScript tip tanımları

════════════════════════════════════════════════════════════════════════════════
CV YÜKLEME VE PARSE SİSTEMİ
════════════════════════════════════════════════════════════════════════════════

CV işleme sistemi iki aşamadan oluşur: PDF'den metin çıkarma ve LLM ile yapılandırılmış veri elde etme.

────────────────────────────────────────────────────────────────────────────────
PyMuPDF (fitz) İLE PDF OKUMA
────────────────────────────────────────────────────────────────────────────────

cv_service.py dosyasında extract_text_from_pdf fonksiyonu bu işlemi yapar. PyMuPDF (fitz) kütüphanesi kullanılır çünkü:

- Çok hızlı ve yüksek performanslı
- Karmaşık PDF formatlarını daha iyi okur
- Tablò, çoklu sütun gibi yapıları daha iyi parse eder

İşlem adımları:

1. Kullanıcı frontend'den PDF yükler
2. Backend, bytes olarak dosyayı alır
3. fitz.open() ile dosya okunur
4. Her sayfa için extract_text() çağrılır
5. Tüm sayfalar birleştirilir
6. Null karakterler ve fazla boşluklar temizlenir

Kod akışı (cv_service.py):

async def extract_text_from_pdf(self, file_content: bytes) -> str:
pdf_file = io.BytesIO(file_content)
reader = PdfReader(pdf_file)
text_parts = []
for page in reader.pages:
page_text = page.extract_text()
if page_text:
text_parts.append(page_text)
full_text = "\n\n".join(text_parts)
return full_text.strip().replace("\x00", "")

────────────────────────────────────────────────────────────────────────────────
LLM İLE PARSE İŞLEMİ
────────────────────────────────────────────────────────────────────────────────

Ham metin elde edildikten sonra parse_cv_with_llm fonksiyonu devreye girer. Bu fonksiyon, metni yapılandırılmış JSON'a çevirir.

Kullanılan LLM: io Intelligence API (OpenAI-uyumlu endpoint)
Model: meta-llama/Llama-3.3-70B-Instruct

Prompt yapısı (cv_service.py):

System Prompt: Sen CV analiz uzmanısın (Türk İK personeli). CV İngilizce olsa bile TÜRKÇE olarak analiz et ve JSON'a çevir.

JSON FORMATI:
{
"full_name": "isim",
"title": "unvan",
"email": "email",
"phone": "tel",
"linkedin_url": "url",
"github": "url",
"summary": "özet",
"skills": ["skill1", "skill2"],
"experience": [
{
"title": "pozisyon",
"company": "şirket",
"duration": "süre",
"description": "açıklama"
}
],
"education": [
{
"degree": "derece",
"field": "bölüm",
"school": "okul",
"start_year": 2020,
"end_year": 2024,
"gpa": "AGNO/GPA değeri"
}
],
"projects": [
{
"name": "proje",
"technologies": ["tech1", "tech2"],
"description": "açıklama"
}
],
"languages": {"dil": "seviye"},
"certifications": ["sertifika"],
"experience_years": "süre"
}

KURALLAR:

1. Sadece JSON döndür
2. GPA/AGNO varsa education.gpa'ya yaz
3. Null kullanabilirsin (şirket adı yoksa company: null)
4. Tarihleri/Süreleri Türkçe'ye çevir (örn: '1 year' -> '1 yıl')
5. Unvanları mümkünse Türkçe karşılığıyla yaz

User Message: CV metni (ilk 5000 karakter)

LLM yanıtı JSON parse edilir ve veritabanına kaydedilir. Hata durumunda retry mekanizması vardır (maksimum 2 deneme).

İlgili dosyalar:

- backend/app/services/cv_service.py (parse işlemi)
- backend/app/routers/cv.py (endpoint: POST /api/cv/upload)
- backend/app/models/cv.py (veritabanı modeli)

════════════════════════════════════════════════════════════════════════════════
CV ANALİZ SİSTEMİ
════════════════════════════════════════════════════════════════════════════════

CV analiz sistemi, aynı CV'yi farklı profiller için farklı puanlayan bağlamsal bir sistemdir. Örneğin, 3 proje:

- 4. sınıf öğrenci için MÜKEMMEL (10/10)
- 5 yıllık mühendis için YETERSİZ (4/10)

────────────────────────────────────────────────────────────────────────────────
BAĞLAMSAL ANALİZ MANTĞI
────────────────────────────────────────────────────────────────────────────────

Kullanıcı analiz yaparken şunları belirtir:

- Sektör (örn: Bilgisayar Mühendisliği)
- Alanlar (örn: Backend, Frontend, Yapay Zeka - maksimum 3)
- Deneyim seviyesi (örn: Yeni Mezun, Junior, Mid-Level, Senior)

Sistem her alan için ayrı analiz yapar ve o alan için gerekli beklentileri career_config.py dosyasından alır.

Örnek beklentiler (career_config.py):

EXPERIENCE_LEVELS = {
"yeni_mezun": {
"name": "Yeni Mezun (0-1 yıl)",
"years_range": (0, 1),
"expectations": {
"min_projects": 2,
"min_skills": 5,
"min_experience_items": 0
}
},
"junior": {
"name": "Junior (1-3 yıl)",
"years_range": (1, 3),
"expectations": {
"min_projects": 3,
"min_skills": 8,
"min_experience_items": 1
}
},
"senior": {
"name": "Senior (5+ yıl)",
"years_range": (5, 999),
"expectations": {
"min_projects": 5,
"min_skills": 15,
"min_experience_items": 3
}
}
}

────────────────────────────────────────────────────────────────────────────────
ÜÇ KATMANLI ANALİZ SİSTEMİ
────────────────────────────────────────────────────────────────────────────────

Analiz üç aşamada yapılır:

1. PRE-ANALYSIS (Rule-based, cv_pre_analysis.py):

Python kurallarıyla hızlı kontroller:

- Proje sayısı yeterli mi?
- Skill sayısı yeterli mi?
- Deneyim süresi yeterli mi?
- Eksik bilgiler var mı? (email, telefon vb.)

def pre_analyze_cv(cv_data, expectations):
issues = []
if len(cv_data.get("projects", [])) < expectations["min_projects"]:
issues.append("Proje sayısı yetersiz")
if len(cv_data.get("skills", [])) < expectations["min_skills"]:
issues.append("Skill sayısı az")
return {"issues": issues, "checks_passed": len(issues) == 0}

2. LLM ANALYSIS (cv_analysis_service.py):

LLM'e CV ve beklentiler gönderilir. LLM, her kategoriyi 0-10 arasında puanlar:

- Skills (Beceriler)
- Experience (Deneyim)
- Projects (Projeler)
- Education (Eğitim)

Prompt yapısı:

System Prompt: Sen {field_name} alanında {exp_name} seviyesindeki adayları değerlendiren bir İK uzmanısın.

BAĞLAM:

- Alan: {field_name}
- Seviye: {exp_name}
- Beklentiler: {expectations}

BEKLENTİLER:
Bu seviye için şunlar beklenir:

- En az {min_projects} proje
- En az {min_skills} beceri
- Deneyim süresi: {years_range}

GEREKLİ TEKNOLOJİLER:
{required_skills}

PUANLAMA:
Her kategori için 0-10 puan ver. Sadece JSON döndür:
{
"skills_score": 7,
"experience_score": 6,
"projects_score": 8,
"education_score": 9,
"missing_skills": ["Docker", "Kubernetes"],
"strengths": ["Python güçlü", "Proje çeşitliliği var"],
"weaknesses": ["DevOps deneyimi yok"],
"overall_comment": "Genel değerlendirme"
}

3. POST-VALIDATION (cv_analysis_service.py):

LLM'in verdiği puanlar mantık kontrolünden geçer:

- Hiç deneyim yoksa experience_score 7'den büyük olamaz
- Hiç proje yoksa projects_score 5'ten büyük olamaz
- Puanlar 0-10 aralığında mı?

def validate_scores(scores, cv_data):
if len(cv_data.get("experience", [])) == 0:
scores["experience_score"] = min(scores["experience_score"], 7)
if len(cv_data.get("projects", [])) == 0:
scores["projects_score"] = min(scores["projects_score"], 5)
return scores

────────────────────────────────────────────────────────────────────────────────
ATS (APPLICANT TRACKING SYSTEM) SİMÜLASYONU
────────────────────────────────────────────────────────────────────────────────

ats_simulation_service.py dosyası, CV'yi gerçek ATS sistemlerinin okuduğu gibi okumaya çalışarak sorunları tespit eder.

ATS sistemleri genelde basit PDF kütüphaneleri kullanır. Karmaşık formatlı CV'ler, ikonlar, çok sütunlu düzenler okuma hatalarına yol açar.

Tespit edilen sorunlar:

1. İKON KULLANIMI:
   CV'de şu ikonlar varsa ATS okuyamaz:
   ☎ 📧 ✉ 📱 🔗 📍 💼 🎓 ⭐

Tespit kodu:
ICON_PATTERNS = {
"☎": "telefon ikonu",
"📧": "email ikonu",
...
}

def \_detect_icon_issues(self, text):
issues = []
for icon, name in self.ICON_PATTERNS.items():
if icon in text:
issues.append({
"type": "icon_usage",
"severity": "high",
"message": f"{name} kullanılmış, ATS okuyamayabilir"
})
return issues

2. İLETİŞİM BİLGİSİ OKUNURLUĞU:
   Email ve telefon numarası regex ile aranır. Bulunamazsa sorun var demektir.

EMAIL*PATTERN = re.compile(r'[a-zA-Z0-9.*%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
PHONE_PATTERN = re.compile(r'[\+]?[(]?[0-9]{1,4}[)]?[-\s\.]?[0-9]{1,4}[-\s\.]?[0-9]{1,9}')

if not EMAIL_PATTERN.search(text):
issues.append({"type": "contact_missing", "message": "Email bulunamadı"})

3. SÜTUN KAYMASI:
   İki sütunlu CV'lerde metinler karışık okunur. Tespit için satır başına kelime sayısı kontrol edilir.

4. FORMATLAMA SORUNLARI:

- Çok fazla büyük harf kullanımı
- Anormal boşluklar
- Özel karakterler

ATS UYUMLULUK SKORU:

Tüm sorunlara göre 0-100 arası skor hesaplanır:

def \_calculate_ats_score(self, issues):
base_score = 100
for issue in issues:
if issue["severity"] == "high":
base_score -= 15
elif issue["severity"] == "medium":
base_score -= 10
else:
base_score -= 5
return max(0, base_score)

İlgili dosyalar:

- backend/app/services/ats_simulation_service.py (ATS simülasyonu)
- backend/app/routers/analysis.py (endpoint: POST /api/analysis/ats-simulation)

════════════════════════════════════════════════════════════════════════════════
CV TAVSİYE SİSTEMİ
════════════════════════════════════════════════════════════════════════════════

Analiz sonuçlarına göre kişiselleştirilmiş kariyer tavsiyeleri üretilir.

────────────────────────────────────────────────────────────────────────────────
BİLGİ BANKASI (career_knowledge.py)
────────────────────────────────────────────────────────────────────────────────

Her alan için önceden tanımlanmış bilgi bankası vardır:

KNOWLEDGE_BASE = {
"backend": {
"learning_path": [
"Python/Java temellerini pekiştir",
"RESTful API tasarımı öğren",
"Docker ve Kubernetes ile container yönetimi",
"Veritabanı optimizasyonu (PostgreSQL, MongoDB)",
"Mikroservis mimarisi ve design patterns"
],
"project_ideas": [
"RESTful API ile TODO uygulaması",
"E-ticaret backend sistemi",
"Mikroservis tabanlı blog platformu"
],
"certifications": [
"AWS Certified Developer",
"Docker Certified Associate",
"PostgreSQL Certification"
]
},
"yapay_zeka": {
"learning_path": [
"Python ve NumPy/Pandas temellerini öğren",
"Machine Learning temelleri (scikit-learn)",
"Deep Learning (TensorFlow/PyTorch)",
"Computer Vision (OpenCV, YOLO)",
"NLP (Transformers, BERT, GPT)"
],
"project_ideas": [
"Görüntü sınıflandırma (CNN)",
"Chatbot (NLP + LLM)",
"Nesne tespiti (YOLO)"
]
}
}

────────────────────────────────────────────────────────────────────────────────
TAVSİYE OLUŞTURMA SÜRECİ
────────────────────────────────────────────────────────────────────────────────

recommendation_service.py dosyasında generate_recommendations fonksiyonu:

1. Analiz sonuçlarını al
2. Her alan için:
   - Eksik becerileri tespit et
   - Bilgi bankasından öğrenme yolu çek
   - Proje önerileri ver
   - Sertifika önerileri ver
3. LLM ile kişiselleştirilmiş tavsiye metni oluştur

LLM Prompt:

System Prompt: Sen bir kariyer danışmanısın. Aday {exp_name} seviyesinde ve {field_name} alanında çalışmak istiyor.

DURUM:

- Mevcut puan: {current_score}/10
- Eksik beceriler: {missing_skills}
- Zayıf yönler: {weaknesses}

Kişiselleştirilmiş tavsiyeler ver. Motive edici ama gerçekçi ol.

ÖNEMLİ:

- Önce hangi beceriyi geliştirmeli açıkla
- Proje önerilerini somutlaştır
- Gerçekçi zaman çizelgesi ver (3 ay, 6 ay gibi)

Çıktı:

{
"field_recommendations": [
{
"field_name": "Backend Development",
"current_score": 6.5,
"target_score": 8.5,
"priority_actions": [
"Docker ve Kubernetes öğren (2 ay)",
"Mikroservis projesi yap (3 ay)",
"PostgreSQL optimizasyonu çalış (1 ay)"
],
"learning_resources": [...],
"project_ideas": [...],
"timeline": "6 ay içinde hedef puana ulaşılabilir"
}
]
}

İlgili dosyalar:

- backend/app/services/recommendation_service.py (tavsiye oluşturma)
- backend/app/career/career_knowledge.py (bilgi bankası)
- backend/app/routers/analysis.py (endpoint: POST /api/analysis/recommendations)

════════════════════════════════════════════════════════════════════════════════
MÜLAKAT SİSTEMİ
════════════════════════════════════════════════════════════════════════════════

En kapsamlı modüllerden biri. Hem metin hem sesli mülakat desteği var.

────────────────────────────────────────────────────────────────────────────────
MÜLAKAT OTURUMU OLUŞTURMA
────────────────────────────────────────────────────────────────────────────────

Kullanıcı mülakat başlatırken şunları seçer:

- Sektör (örn: Teknoloji Şirketleri, Fintech, Savunma Sanayii)
- Pozisyon (örn: Backend Developer, Frontend Developer, AI Engineer)
- Deneyim seviyesi (örn: Stajyer, Junior, Senior)
- Mülakat tipi (örn: Genel, Sektör + Yorum)
- Soru sayısı (5-15 arası)

Bu bilgiler interview_config.py dosyasında tanımlı:

COMPANY_SECTORS = {
"tech_companies": "Teknoloji Şirketleri",
"fintech": "Fintech / Bankacılık",
"defense": "Savunma Sanayii",
"ecommerce": "E-ticaret"
}

POSITIONS = {
"backend": {
"name": "Backend Developer",
"topics": ["API tasarımı", "Veritabanı", "Mikroservis", "Caching"]
},
"yapay_zeka": {
"name": "AI/ML Engineer",
"topics": ["Machine Learning", "Deep Learning", "Model deployment", "Data preprocessing"]
}
}

EXPERIENCE_REQUIREMENTS = {
"stajyer": {
"name": "Stajyer",
"difficulty": "Temel seviye sorular",
"expectations": "Temel kavramları bilmesi yeterli"
},
"senior": {
"name": "Senior",
"difficulty": "İleri seviye, system design, mimari sorular",
"expectations": "Derin teknik bilgi, best practices, liderlik"
}
}

────────────────────────────────────────────────────────────────────────────────
SORU OLUŞTURMA SÜRECİ
────────────────────────────────────────────────────────────────────────────────

interview_service.py dosyasındaki generate_question fonksiyonu:

1. Soru tipi belirlenir:
   - TECHNICAL: Teknik soru
   - SCENARIO: Senaryo bazlı soru
   - CV_BASED: CV'ye özel soru (kullanıcının projelerinden)

2. LLM'e gönderilecek prompt oluşturulur:

System Prompt: Sen {position_name} pozisyonu için mülakat yapan bir İK uzmanısın. Aday {exp_name} seviyesinde.

MÜLAKAT BAĞLAMI:

- Sektör: {sector_name}
- Pozisyon: {position_name}
- Deneyim: {exp_name}
- Soru tipi: {question_type}
- Soru numarası: {question_number}/{total_questions}

KONULAR: {topics}

BEKLENTİLER:
{expectations}

SORU ÖZELLİKLERİ:

- Deneyim seviyesine uygun zorlukta olmalı
- Açık uçlu olmalı (Evet/Hayır soruları yasak)
- Gerçek mülakatlarda sorulabilecek tipte olmalı
- Çok uzun olmamalı (max 2-3 cümle)

ÖNCEKİ CEVAP: {previous_context}

GEÇİŞ CÜMLESİ:
Önceki sorudan bu soruya yumuşak bir geçiş yap. Örnek: "Anladım, teşekkürler. Şimdi farklı bir konuya geçelim..."

JSON FORMATINDA DÖNDÜR:
{
"transition": "Geçiş cümlesi (isteğe bağlı)",
"question": "Soru metni"
}

3. LLM yanıtı parse edilir ve veritabanına kaydedilir:

question = InterviewQuestion(
session_id=session.id,
question_number=question_number,
question_text=result.get("question"),
question_type=question_type.value,
transition_text=result.get("transition")
)

────────────────────────────────────────────────────────────────────────────────
CEVAP DEĞERLENDİRME
────────────────────────────────────────────────────────────────────────────────

evaluate_answer fonksiyonu cevapları puanlar. Buradaki kritik nokta: Değerlendirme seviyeye göre yapılır.

Değerlendirme kriterleri:

STAJYER için:

- Beklenti: Temel kavramları bilmesi yeterli
- Geçer puan: 5/10
- Pozitif: "Stajyer için iyi bir cevap"
- Negatif: "Stajyer için bile yetersiz"

SENIOR için:

- Beklenti: System design, best practices, liderlik
- Geçer puan: 7/10
- Pozitif: "Senior seviyesine yakışır"
- Negatif: "Senior için kabul edilemez, çok yüzeysel"

LLM Prompt:

System Prompt: Sen bir {position_name} mülakatında cevapları değerlendiren İK uzmanısın.
Aday: {exp_name} seviyesinde.

SEVİYEYE GÖRE BEKLENTİ:
{expectations}

DEĞERLENDİRME KRİTERLERİ:

- Teknik doğruluk
- Açıklama kalitesi
- Pratik uygulama bilgisi
- SEVİYEYE UYGUNLUK (çok önemli!)

PUANLAMA ({exp_name} için):
1-3: {negative_prefix} - kritik eksikler
4-5: Zayıf ama gelişebilir
6-7: Kabul edilebilir, {exp_name} için yeterli
8-9: {positive_prefix}, güçlü cevap
10: Mükemmel, seviyenin üzerinde

ÖNEMLİ: Yorumda mutlaka seviyeye göre değerlendirme yap!

JSON FORMATINDA CEVAP VER:
{
"score": 7,
"reason": "Seviyeye göre değerlendirme ve açıklama",
"ideal_answer": "İdeal cevap ne olmalıydı",
"strengths": ["güçlü yön 1", "güçlü yön 2"],
"weaknesses": ["eksik 1", "eksik 2"]
}

User Message:
SORU: {question_text}
ADAYIN CEVABI: {user_answer}
Bu cevabı {exp_name} seviyesine göre değerlendir.

Değerlendirme sonucu veritabanına kaydedilir:

answer = InterviewAnswer(
question_id=question.id,
user_answer=user_answer,
score=evaluation.get("score", 5),
evaluation_reason=evaluation.get("reason", ""),
ideal_answer=evaluation.get("ideal_answer"),
strengths=evaluation.get("strengths", []),
weaknesses=evaluation.get("weaknesses", [])
)

NOT: Değerlendirme sonuçları mülakatın ortasında kullanıcıya gösterilmez, sadece kaydedilir. Mülakat bitince rapor olarak sunulur.

────────────────────────────────────────────────────────────────────────────────
SESLİ MÜLAKAT SİSTEMİ
────────────────────────────────────────────────────────────────────────────────

Sesli mülakat, Groq Whisper (Speech-to-Text) ve Edge-TTS (Text-to-Speech) kullanarak gerçekleştirilir.

SPEECH-TO-TEXT (speech_service.py):

Groq API ile Whisper-large-v3 modeli kullanılır:

1. Frontend'den ses kaydı gelir (WebM veya WAV formatında)
2. Geçici dosyaya kaydedilir
3. WebM ise FFmpeg ile WAV'a çevrilir (opsiyonel)
4. Groq API'ye gönderilir

async def transcribe_audio(self, audio_bytes: bytes, filename: str) -> dict:
with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
tmp.write(audio_bytes)
tmp_path = tmp.name

    with open(tmp_path, "rb") as f:
        transcription = self.client.audio.transcriptions.create(
            file=(tmp_path, f.read()),
            model="whisper-large-v3",
            response_format="json",
            language="tr",
            temperature=0.0,
            prompt=TECH_TERMS_PROMPT
        )

    text = transcription.text
    text = self._clean_whisper_artifacts(text)
    return {"text": text, "success": True}

TEKNİK TERİM PROMPTU:

Whisper'ın teknik terimleri doğru yazması için prompt kullanılır:

TECH_TERMS_PROMPT = """
Yazılım mülakatı kaydı. Aşağıdaki terimler geçebilir:
Python, JavaScript, TypeScript, Java, React, Node.js, Docker, Kubernetes,
PostgreSQL, MongoDB, AWS, Machine Learning, Deep Learning, API, Backend, etc.
"""

Bu prompt, Whisper'a hangi tür kelimeler beklendiğini söyler ve doğruluk oranını artırır.

TEXT-TO-SPEECH (tts_service.py):

Edge-TTS kullanılarak soruların sesli okunması sağlanır. Buradaki kritik nokta: Teknik terimlerin doğru telaffuz edilmesi.

TELAFFUZ SÖZLÜĞÜ:

PRONUNCIATION_DICT = {
"python": "Paytın",
"Python": "Paytın",
"javascript": "Cava Skript",
"JavaScript": "Cava Skript",
"typescript": "Tayp Skript",
"react": "Riekt",
"React": "Riekt",
"nodejs": "Nod Cey Es",
"Node.js": "Nod Cey Es",
"docker": "Dokır",
"Docker": "Dokır",
"kubernetes": "Kubernitis",
"postgresql": "Post Gres Kyu El",
"PostgreSQL": "Post Gres Kyu El",
"mongodb": "Mongo Di Bi",
"sql": "Es Kyu El",
"aws": "Ey Dablyu Es",
"api": "Ey Pi Ay",
"backend": "Bek End",
"frontend": "Fıront End",
"fullstack": "Ful Stek"
}

Metin okutulmadan önce bu sözlük uygulanır:

def \_apply_pronunciation_dict(self, text: str) -> str:
for original, pronunciation in PRONUNCIATION_DICT.items():
text = re.sub(
rf'\b{re.escape(original)}\b',
pronunciation,
text,
flags=re.IGNORECASE
)
return text

async def generate_speech(self, text: str, voice: str = "female") -> bytes: # Telaffuz düzeltmesi uygula
text_with_pronunciation = self.\_apply_pronunciation_dict(text)

    # Edge-TTS ile oluştur
    voice_name = VOICES.get(voice, VOICES["female"])
    communicate = edge_tts.Communicate(text_with_pronunciation, voice_name)

    audio_bytes = b""
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_bytes += chunk["data"]

    return audio_bytes

VOICES:

Türkçe sesler:

- "tr-TR-AhmetNeural" (Erkek)
- "tr-TR-EmelNeural" (Kadın - varsayılan)

GROQ VE IO.NET API ENTEGRASYONU:

Sesli mülakatta iki API birlikte çalışır:

1. GROQ API (Speech-to-Text):
   - Model: whisper-large-v3
   - Endpoint: https://api.groq.com/openai/v1/audio/transcriptions
   - Kullanım: Kullanıcının sesli cevabını metne çevirir

2. IO.NET API (LLM):
   - Model: meta-llama/Llama-3.3-70B-Instruct
   - Endpoint: https://api.io.net/v1/chat/completions
   - Kullanım: Soru oluşturma ve cevap değerlendirme

Akış:

Frontend: Soru iste
↓
Backend: IO.NET'e soru promptu gönder
↓
Backend: Edge-TTS ile soru seslendir
↓
Frontend: Kullanıcı sesli cevap verir
↓
Backend: GROQ Whisper ile metne çevir
↓
Backend: IO.NET'e değerlendirme promptu gönder
↓
Backend: Değerlendirme sonucu kaydet

Kod (interview_voice.py router):

@router.post("/voice/submit-answer")
async def submit_voice_answer(
question_id: int,
audio_file: UploadFile,
db: Session = Depends(get_db),
current_user: User = Depends(get_current_user)
): # 1. Sesi metne çevir (GROQ)
audio_bytes = await audio_file.read()
speech_result = await speech_service.transcribe_audio(audio_bytes, audio_file.filename)

    if not speech_result.get("success"):
        raise HTTPException(400, "Ses metne çevrilemedi")

    transcribed_text = speech_result.get("text", "")

    # 2. Cevabı değerlendir (IO.NET)
    evaluation = await interview_service.evaluate_answer(
        question=question,
        user_answer=f"[SESLI] {transcribed_text}",
        session=session,
        db=db
    )

    return {
        "transcribed_text": transcribed_text,
        "evaluation": evaluation
    }

İlgili dosyalar:

- backend/app/services/interview_service.py (mülakat mantığı)
- backend/app/services/speech_service.py (Groq Whisper)
- backend/app/services/tts_service.py (Edge-TTS)
- backend/app/routers/interview.py (metin mülakat endpoint'leri)
- backend/app/routers/interview_voice.py (sesli mülakat endpoint'leri)
- backend/app/models/interview.py (veritabanı modelleri)

════════════════════════════════════════════════════════════════════════════════
İŞ ARAMA VE SKILL GAP ANALİZİ
════════════════════════════════════════════════════════════════════════════════

job_search_service.py dosyası iş ilanlarını tarayıp kullanıcının CV'siyle karşılaştırır.

────────────────────────────────────────────────────────────────────────────────
HİBRİT İŞ ARAMA SİSTEMİ
────────────────────────────────────────────────────────────────────────────────

Birden fazla kaynak kullanılarak çeşitli platformlardan iş ilanları toplanır:

1. İş ilanı platformları üzerinden arama
   - Çoklu platform desteği
   - Aktif Türkçe ilanlar

2. Ek platformlardan ilan toplama
   - Farklı iş arama kaynakları
   - Geniş kapsama alanı

Kod:

def search_jobs(self, profession: str, field: str, location: str = "Türkiye", results_per_site: int = 10):
all_jobs = []

    # 1. İş ilanı platformlarından arama
    platform_jobs = self._search_platforms(profession, field, location, results_per_site)
    all_jobs.extend(platform_jobs)

    # 2. Ek kaynaklardan ilan toplama
    additional_results = self._search_additional_sources(
        search_term=f"{profession} {field}",
        location=location,
        results_wanted=results_per_site
    )

    if additional_results is not None:
        for _, row in additional_results.iterrows():
            all_jobs.append({
                "title": row.get("title", ""),
                "company": row.get("company", ""),
                "location": row.get("location", ""),
                "description": row.get("description", ""),
                "source": row.get("site", "")
            })

    # Karıştır (her kaynaktan dengeli sonuç için)
    random.shuffle(all_jobs)
    return all_jobs

────────────────────────────────────────────────────────────────────────────────
SKILL MATCHER (skill_matcher.py)
────────────────────────────────────────────────────────────────────────────────

LLM kullanmadan, sadece Python kurallarıyla CV ve iş ilanı arasındaki uyumu hesaplar. Çok hızlı ve maliyet etkin.

TEKNOLOJİ SÖZLÜĞÜ:

TECH_SYNONYMS sözlüğü 300+ teknoloji için sinonim listesi içerir:

TECH_SYNONYMS = {
"python": ["python", "python3", "python2"],
"javascript": ["javascript", "ecmascript"],
"react": ["react", "reactjs", "react.js"],
"nodejs": ["node", "nodejs", "node.js"],
"postgresql": ["postgresql", "postgres", "psql"],
"docker": ["docker", "docker-compose"],
"kubernetes": ["kubernetes", "k8s"],
...
}

EŞLEŞTİRME ALGORITMASI:

def match_cv_to_job(self, cv_data: Dict, job_description: str) -> Dict: # 1. CV'den teknolojileri çıkar
cv_skills = self.\_extract_technologies_from_cv(cv_data)

    # 2. İlan açıklamasından teknolojileri çıkar
    job_skills = self._extract_technologies_from_text(job_description)

    # 3. Eşleşenleri bul
    matched_skills = cv_skills & job_skills  # Set intersection
    missing_skills = job_skills - cv_skills  # Set difference

    # 4. Skor hesapla
    if len(job_skills) == 0:
        match_score = 0
    else:
        match_score = (len(matched_skills) / len(job_skills)) * 100

    return {
        "match_score": round(match_score, 2),
        "matched_skills": list(matched_skills),
        "missing_skills": list(missing_skills),
        "cv_skill_count": len(cv_skills),
        "job_skill_count": len(job_skills)
    }

SKILL GAP ANALİZİ:

generate_skill_gap_report fonksiyonu, eksik becerileri kategorize eder:

def generate_skill_gap_report(self, match_result: Dict) -> Dict:
missing = match_result.get("missing_skills", [])

    # Kategorilere ayır
    critical = []  # Core teknolojiler (dil, framework)
    important = []  # DevOps, veritabanı
    nice_to_have = []  # İlave araçlar

    for skill in missing:
        category = self._categorize_skill(skill)
        if category == "programming_language":
            critical.append(skill)
        elif category in ["framework", "database", "devops"]:
            important.append(skill)
        else:
            nice_to_have.append(skill)

    return {
        "critical_gaps": critical,
        "important_gaps": important,
        "nice_to_have": nice_to_have,
        "priority_learning_order": critical + important + nice_to_have
    }

İlgili dosyalar:

- backend/app/services/job_search_service.py (iş arama)
- backend/app/services/skill_matcher.py (skill eşleştirme)
- backend/app/routers/jobs.py (endpoint'ler)

════════════════════════════════════════════════════════════════════════════════
ÖN YAZI VE E-MAİL OLUŞTURMA
════════════════════════════════════════════════════════════════════════════════

cover_letter_service.py dosyası, iş başvuruları için akıllı ön yazı ve e-mail oluşturur.

────────────────────────────────────────────────────────────────────────────────
İKİ AŞAMALI LLM SİSTEMİ
────────────────────────────────────────────────────────────────────────────────

1. AŞAMA: OLUŞTUR
   LLM'e profil bilgileri ve iş ilanı gönderilir, ilk taslak oluşturulur.

2. AŞAMA: DÜZELT
   Oluşturulan metin tekrar LLM'e gönderilir:

- Yazım hataları düzeltilir
- Yabancı karakterler temizlenlir (â → a, ş → ş vb.)
- Aşırı övgü kontrolü ("en iyi aday", "mükemmel" gibi ifadeler kaldırılır)
- Ton kontrolü (pozisyona uygun mu?)

────────────────────────────────────────────────────────────────────────────────
PROFİL BAZLI TON AYARLAMA
────────────────────────────────────────────────────────────────────────────────

POSITION_TYPES = {
"intern": {
"tone": "Öğrenmeye aç, meraklı, enerjik. Tecrübe yok ama potansiyel var.",
"avoid": "Uzun deneyim, uzmanlık iddiası, liderlik, kendini övme"
},
"junior": {
"tone": "Yeni mezun veya 1-2 yıl tecrübeli. Pratik projeler yapmış ama hala öğreniyor.",
"avoid": "Senior ifadeler, ekip liderliği, 5+ yıl deneyim, kendini övme"
},
"senior": {
"tone": "5+ yıl tecrübeli. Teknik liderlik, mimari kararlar, mentorluk yapabilen.",
"avoid": "Stajyer ifadeleri, öğrenmeye muhtaç görünme, kendini övme"
}
}

────────────────────────────────────────────────────────────────────────────────
SEKTÖR BAZLI VURGU
────────────────────────────────────────────────────────────────────────────────

SECTORS = {
"defense": {
"keywords": ["gizlilik bilinci", "gömülü sistemler", "kritik sistemler", "milli teknoloji"],
"emphasis": "Gizlilik bilinci, milli değerler, kritik sistemlerde çalışma motivasyonu"
},
"fintech": {
"keywords": ["güvenlik", "uyumluluk", "finansal veriler", "regülasyonlar"],
"emphasis": "Veri güvenliği, hata toleransı düşük sistemler, finansal hesaplama"
},
"startup": {
"keywords": ["hızlı hareket", "çevik", "çoklu şapka", "öğrenme"],
"emphasis": "Adaptasyon, hızlı öğrenme, birden fazla rol üstlenebilme"
}
}

────────────────────────────────────────────────────────────────────────────────
ÖN YAZI OLUŞTURMA PROMPTU
────────────────────────────────────────────────────────────────────────────────

System Prompt: Sen profesyonel bir kariyer danışmanısın. İş başvuruları için ön yazı yazıyorsun.

PROFİL:

- Pozisyon tipi: {position_type} ({position_tone})
- Sektör: {sector_name}
- Sektör vurguları: {sector_emphasis}

YASAK İFADELER:

- {avoid_phrases}
- "Uygun adayım", "En iyi adayım", "Mükemmel"
- "Değer katacağıma eminim"
- Kendini övme

TON:
{position_tone}

GEREKLİ VURGULAR:
{sector_keywords}

ADAY BİLGİLERİ:
{cv_summary}

İŞ İLANI:
{job_description}

KURALLAT:

1. Kısa ve öz (max 250 kelime)
2. Somut beceri ve projelerden bahset
3. Sektöre özel vurgular yap
4. Kendini övme, sadece ne yaptığını anlat
5. Ton {position_type} seviyesine uygun olsun

ÇIKTI:
Sadece ön yazı metnini döndür. JSON veya başlık kullanma.

E-MAİL İÇİN FARK:

E-mail için aynı sistem kullanılır ama:

- Daha kısa (max 150 kelime)
- Konu satırı eklenir
- Profesyonel kapanış (İyi çalışmalar, Saygılarımla gibi)

İlgili dosyalar:

- backend/app/services/cover_letter_service.py (ön yazı/email servisi)
- backend/app/routers/cover_letter.py (endpoint'ler)

════════════════════════════════════════════════════════════════════════════════
CHATBOT SİSTEMİ
════════════════════════════════════════════════════════════════════════════════

chat_service.py dosyası, kullanıcının tüm verilerine erişerek bağlamsal cevaplar veren bir chatbot sağlar.

────────────────────────────────────────────────────────────────────────────────
CONTEXT-AWARE CHATBOT
────────────────────────────────────────────────────────────────────────────────

Normal chatbot'lardan farkı: Kullanıcının CV'sine, analiz sonuçlarına, mülakat geçmişine erişebilir.

INTENT DETECTION:

Kullanıcının mesajına göre hangi verilerin gerekli olduğunu anlar:

def \_detect_intent(self, message: str) -> str:
message_lower = message.lower()

    if any(word in message_lower for word in ["cv", "özgeçmiş", "deneyim"]):
        return "cv_related"
    elif any(word in message_lower for word in ["mülakat", "soru", "cevap"]):
        return "interview_related"
    elif any(word in message_lower for word in ["iş", "ilan", "başvuru"]):
        return "job_related"
    elif any(word in message_lower for word in ["analiz", "puan", "değerlendirme"]):
        return "analysis_related"
    else:
        return "general"

CONTEXT BUILDING:

Intent'e göre ilgili veriler veritabanından çekilir:

async def \_build_context(self, intent: str) -> str:
if intent == "cv_related": # En son CV'yi çek
cv = self.db.query(CV).filter(CV.user_id == self.user.id).order_by(CV.created_at.desc()).first()
if cv:
return f"Kullanıcının CV'si: {json.dumps(cv.parsed_data, ensure_ascii=False)}"

    elif intent == "interview_related":
        # Son mülakat oturumunu çek
        session = self.db.query(InterviewSession).filter(
            InterviewSession.user_id == self.user.id
        ).order_by(InterviewSession.created_at.desc()).first()

        if session:
            return f"Son mülakat: {session.position} - {session.status}"

    elif intent == "analysis_related":
        # Son CV analizini çek
        analysis = self.db.query(CVAnalysis).filter(
            CVAnalysis.user_id == self.user.id
        ).order_by(CVAnalysis.created_at.desc()).first()

        if analysis:
            return f"Son analiz sonuçları: {json.dumps(analysis.result, ensure_ascii=False)}"

    return ""

SYSTEM PROMPT:

System Prompt: Sen KariyerKoçu platformunun yapay zeka asistanısın. Kullanıcılara kariyer konusunda yardımcı oluyorsun.

KULLANICI BİLGİLERİ:

- İsim: {user.full_name}
- Email: {user.email}
- Hedef sektör: {user.target_sector}
- Hedef pozisyon: {user.target_position}
- Deneyim seviyesi: {user.experience_level}

BAĞLAM:
{context}

GÖREVLERİN:

1. Kariyer tavsiyeleri ver
2. CV, mülakat, iş başvurusu konularında yardımcı ol
3. Kullanıcının verilerine dayanarak kişiselleştirilmiş öneriler sun
4. Samimi ama profesyonel ol
5. Uzun cevaplar verme, öz ve net ol

YASAK:

- Medikal, hukuki, finansal tavsiye verme
- Kullanıcı verilerini dışarıya sızdırma
- Yanıltıcı bilgi verme

RETRY MEKANİZMASI:

LLM rate limit veya timeout hatası verirse otomatik retry:

max_retries = 3
for attempt in range(max_retries):
try:
response = await llm_service.chat_with_history(
messages=messages,
system_prompt=system_prompt,
temperature=0.7,
max_tokens=1024
)
return {"response": response, "context_used": intent}
except Exception as e:
if attempt < max_retries - 1:
await asyncio.sleep(2)
continue

return {"response": "Şu an yanıt üretirken bir sorun yaşıyorum. Lütfen tekrar deneyin."}

İlgili dosyalar:

- backend/app/services/chat_service.py (chatbot mantığı)
- backend/app/routers/chat.py (endpoint'ler)
- frontend/src/components/chat/ChatWidget.tsx (UI)

════════════════════════════════════════════════════════════════════════════════
LLM SERVİSİ VE API ENTEGRASYONU
════════════════════════════════════════════════════════════════════════════════

llm_service.py dosyası tüm LLM çağrılarını yönetir.

────────────────────────────────────────────────────────────────────────────────
IO INTELLIGENCE API
────────────────────────────────────────────────────────────────────────────────

OpenAI-uyumlu API formatı kullanır. Bu sayede aynı kod OpenAI, Groq, veya başka LLM sağlayıcılarla da çalışabilir.

Endpoint: https://api.io.net/v1/chat/completions
Model: meta-llama/Llama-3.3-70B-Instruct

REQUEST FORMAT:

{
"model": "meta-llama/Llama-3.3-70B-Instruct",
"messages": [
{"role": "system", "content": "Sen bir CV analiz uzmanısın..."},
{"role": "user", "content": "Bu CV'yi analiz et..."}
],
"temperature": 0.7,
"max_tokens": 1024
}

RESPONSE FORMAT:

{
"choices": [
{
"message": {
"role": "assistant",
"content": "Analiz sonucu..."
}
}
]
}

────────────────────────────────────────────────────────────────────────────────
RETRY MEKANİZMASI
────────────────────────────────────────────────────────────────────────────────

Rate limit (429) veya timeout durumunda exponential backoff ile retry:

max_retries = 3
base_delay = 2

for attempt in range(max_retries):
try:
response = await client.post(url, headers=headers, json=payload)

        if response.status_code == 429:
            # Rate limit
            if attempt < max_retries - 1:
                wait_time = (base_delay * (2 ** attempt)) + random.uniform(0, 1)
                print(f"Rate limit, {wait_time:.1f}s bekleniyor...")
                await asyncio.sleep(wait_time)
                continue

        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]

    except Exception as e:
        if attempt < max_retries - 1:
            await asyncio.sleep(base_delay)
            continue
        raise

Bekleme süreleri:

- 1. deneme başarısız: 2-3 saniye bekle
- 2. deneme başarısız: 4-5 saniye bekle
- 3. deneme başarısız: Hata fırlat

────────────────────────────────────────────────────────────────────────────────
TIMEOUT YÖNETİMİ
────────────────────────────────────────────────────────────────────────────────

Uzun promptlar için 90 saniye timeout:

async with httpx.AsyncClient(timeout=90.0) as client:
response = await client.post(...)

════════════════════════════════════════════════════════════════════════════════
VERİTABANI YAPISI
════════════════════════════════════════════════════════════════════════════════

PostgreSQL kullanılır. Tablolar SQLAlchemy ORM ile tanımlanır.

ANA TABLOLAR:

1. users (models/user.py):
   - id, email, hashed_password, full_name
   - target_sector, target_position, experience_level (kariyer hedefleri)
   - created_at, updated_at

2. cvs (models/cv.py):
   - id, user_id, filename, file_path
   - parsed_data (JSONB - parse edilmiş CV verisi)
   - raw_text (TEXT - PDF'den çıkarılan ham metin)
   - created_at

3. cv_analyses (models/analysis.py):
   - id, user_id, cv_id
   - sector, fields (ARRAY), experience_level
   - result (JSONB - analiz sonuçları)
   - created_at

4. interview_sessions (models/interview.py):
   - id, user_id, cv_id
   - sector, position, experience_level, interview_type
   - status (active, completed, abandoned)
   - total_questions, current_question_number
   - created_at, completed_at

5. interview_questions (models/interview.py):
   - id, session_id
   - question_number, question_text, question_type
   - transition_text, is_answered
   - created_at

6. interview_answers (models/interview.py):
   - id, question_id
   - user_answer, score
   - evaluation_reason, ideal_answer
   - strengths (ARRAY), weaknesses (ARRAY)
   - created_at

İLİŞKİLER:

users → cvs (one-to-many)
users → cv_analyses (one-to-many)
users → interview_sessions (one-to-many)
interview_sessions → interview_questions (one-to-many)
interview_questions → interview_answers (one-to-one)

════════════════════════════════════════════════════════════════════════════════
API ENDPOİNTLERİ
════════════════════════════════════════════════════════════════════════════════

AUTHENTICATION (routers/auth.py):

- POST /api/auth/register - Yeni kullanıcı kaydı
- POST /api/auth/login - Giriş (JWT token döner)
- GET /api/auth/me - Mevcut kullanıcı bilgisi

CV YÖNETİMİ (routers/cv.py):

- POST /api/cv/upload - CV yükleme ve parse
- GET /api/cv/ - Kullanıcının CV listesi
- GET /api/cv/{cv_id} - Tek CV detayı
- DELETE /api/cv/{cv_id} - CV silme

ANALİZ (routers/analysis.py):

- POST /api/analysis/analyze - CV analizi yap
- GET /api/analysis/{analysis_id} - Analiz sonucu
- POST /api/analysis/ats-simulation - ATS simülasyonu
- POST /api/analysis/recommendations - Tavsiyeler

MÜLAKAT (routers/interview.py):

- POST /api/interview/start - Mülakat başlat
- GET /api/interview/{session_id} - Oturum bilgisi
- POST /api/interview/question - Yeni soru al
- POST /api/interview/answer - Cevap gönder
- POST /api/interview/complete - Mülakatı bitir
- GET /api/interview/{session_id}/report - Rapor al

SESLİ MÜLAKAT (routers/interview_voice.py):

- POST /api/interview/voice/question-audio - Soru sesini al
- POST /api/interview/voice/submit-answer - Sesli cevap gönder

İŞ ARAMA (routers/jobs.py):

- POST /api/jobs/search - İş ara
- POST /api/jobs/match - CV-ilan eşleştirme

ÖN YAZI (routers/cover_letter.py):

- POST /api/cover-letter/generate - Ön yazı oluştur
- POST /api/cover-letter/email - E-mail oluştur

CHATBOT (routers/chat.py):

- POST /api/chat/message - Mesaj gönder
- GET /api/chat/greeting - Karşılama mesajı

════════════════════════════════════════════════════════════════════════════════
FRONTEND MİMARİSİ
════════════════════════════════════════════════════════════════════════════════

React + TypeScript + Vite + TailwindCSS kullanılır.

STATE MANAGEMENT:

Zustand kullanılır (Redux'a göre daha basit):

authStore.ts:

- Kullanıcı bilgileri
- Token yönetimi
- Login/Logout fonksiyonları

themeStore.ts:

- Tema ayarları (dark/light mode)

API İLETİŞİMİ (lib/api.ts):

Axios instance ile merkezi API yönetimi:

const api = axios.create({
baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
headers: {'Content-Type': 'application/json'}
});

// Token ekle
api.interceptors.request.use((config) => {
const token = authStore.getState().token;
if (token) {
config.headers.Authorization = `Bearer ${token}`;
}
return config;
});

// 401 hatası gelirse logout
api.interceptors.response.use(
(response) => response,
(error) => {
if (error.response?.status === 401) {
authStore.getState().logout();
}
return Promise.reject(error);
}
);

ROUTING (App.tsx):

React Router v6 kullanılır:

<Routes>
  <Route path="/" element={<AuthPages />} />
  <Route path="/login" element={<AuthPages />} />
  <Route path="/register" element={<AuthPages />} />
  
  <Route element={<ProtectedRoute />}>
    <Route path="/dashboard" element={<DashboardPage />} />
    <Route path="/cv/upload" element={<CVUploadPage />} />
    <Route path="/cv/analyze" element={<CVAnalysisPage />} />
    <Route path="/interview/setup" element={<InterviewSetupPage />} />
    <Route path="/interview/:sessionId" element={<InterviewPage />} />
    <Route path="/jobs" element={<JobSearchPage />} />
  </Route>
</Routes>

════════════════════════════════════════════════════════════════════════════════
KULLANIM SENARYOLARI
════════════════════════════════════════════════════════════════════════════════

SENARYO 1: YENİ KULLANICI KAYDI VE CV ANALİZİ

1. Kullanıcı siteye girer, Register butonuna tıklar
2. Email, şifre, ad-soyad bilgilerini girer
3. Kayıt olur, otomatik login olur
4. Dashboard'da "CV Yükle" butonuna tıklar
5. PDF dosyasını seçer, yükler
6. Backend PyMuPDF ile metni çıkarır, LLM ile parse eder
7. Parse edilen CV gösterilir, kullanıcı onaylar
8. "CV'mi Analiz Et" sayfasına gider
9. Sektör (örn: Bilgisayar Mühendisliği), alan (örn: Backend, AI), deneyim seviyesi (örn: Junior) seçer
10. "Analiz Et" butonuna tıklar
11. Backend her alan için:
    - Pre-analysis yapar
    - LLM'e gönderir
    - Post-validation yapar
12. Sonuçlar gösterilir: Puanlar, eksik beceriler, güçlü/zayıf yönler
13. "ATS Simülasyonu" sekmesine tıklar, ATS uyumluluk raporu görür
14. "Tavsiyeler" sekmesine tıklar, kariyer tavsiyeleri görür

SENARYO 2: SESLİ MÜLAKAT

1. Kullanıcı "Mülakat" menüsüne tıklar
2. Sektör (örn: Fintech), pozisyon (örn: Backend Developer), deneyim (örn: Mid-Level), mülakat tipi (örn: Genel), soru sayısı (örn: 10) seçer
3. "Mülakatı Başlat" butonuna tıklar
4. Backend mülakat oturumu oluşturur
5. "Sesli Mülakat" moduna geçer
6. İlk soru LLM tarafından üretilir
7. Edge-TTS ile soru okunur, kullanıcı dinler
8. Kullanıcı "Kayda Başla" butonuna tıklar, cevabını söyler
9. "Kaydı Durdur" butonuna tıklar
10. Ses Groq Whisper ile metne çevrilir
11. Metin LLM'e gönderilir, değerlendirilir (kullanıcıya gösterilmez)
12. Sonraki soru üretilir
13. 10 soru bitene kadar tekrar edilir
14. Mülakat biter, "Raporu Gör" butonuna tıklar
15. Tüm sorular, cevaplar, puanlar, güçlü/zayıf yönler gösterilir

SENARYO 3: İŞ ARAMA VE BAŞVURU

1. Kullanıcı "İş İlanları" menüsüne tıklar
2. Meslek grubu (örn: Bilgisayar Mühendisliği), alan (örn: Backend), lokasyon (örn: İstanbul) seçer
3. "İlan Ara" butonuna tıklar
4. Backend iş ilanı arama servisi ile ilanları çeker
5. İlanlar listelenir
6. Kullanıcı bir ilana tıklar, detayları görür
7. "CV'imle Eşleştir" butonuna tıklar
8. Backend skill_matcher ile uyum hesaplar
9. Eşleşme skoru, eşleşen beceriler, eksik beceriler gösterilir
10. "Ön Yazı Oluştur" butonuna tıklar
11. Pozisyon tipi (örn: Mid-Level), sektör (örn: Fintech) seçer
12. LLM ön yazı oluşturur
13. Kullanıcı metni kopyalar, başvuru yapar

════════════════════════════════════════════════════════════════════════════════
GELİŞTİRME VE TEST İPUÇLARI
════════════════════════════════════════════════════════════════════════════════

BACKEND GELİŞTİRME:

1. API testleri için Swagger UI kullanın: http://localhost:8000/docs
2. Veritabanı değişiklikleri için Alembic migration kullanın (production için)
3. LLM çağrıları için retry mekanizması ekleyin
4. Hata mesajlarını kullanıcı dostu hale getirin
5. Rate limit için exponential backoff kullanın

FRONTEND GELİŞTİRME:

1. Component'leri küçük ve yeniden kullanılabilir tutun
2. API çağrıları için loading state'leri ekleyin
3. Hata mesajları için Toast component kullanın
4. Form validasyonlarını client-side yapın
5. TypeScript tip kontrollerini ihmal etmeyin

TEST:

1. Backend test için pytest kullanın:
   pytest tests/

2. Frontend test için:
   npm run test

3. Integration test için Postman koleksiyonu oluşturun

DEPLOYMENT:

1. Docker production build için:
   docker-compose -f docker-compose.prod.yml up -d

2. Environment variables'ları production için değiştirin
3. DATABASE_URL'i production DB'ye yönlendirin
4. DEBUG=False yapın
5. JWT_SECRET'i güçlü bir değere değiştirin

════════════════════════════════════════════════════════════════════════════════
SORUN GİDERME
════════════════════════════════════════════════════════════════════════════════

PROBLEM: Backend başlamıyor, veritabanı hatası

ÇÖZÜM: PostgreSQL servisinin çalıştığından emin olun:
docker ps | grep postgres
Eğer çalışmıyorsa:
docker-compose up -d db

PROBLEM: LLM API 429 hatası veriyor

ÇÖZÜM: Rate limit aşılmış. Retry mekanizması otomatik bekler. Eğer devam ederse:

- API key kotanızı kontrol edin
- Farklı API key kullanın
- max_retries değerini artırın

PROBLEM: Groq API ses tanıyamıyor

ÇÖZÜM:

- Ses formatını kontrol edin (WAV veya WebM olmalı)
- Dosya boyutunu kontrol edin (25MB limit)
- GROQ_API_KEY'in doğru olduğundan emin olun

PROBLEM: Frontend backend'e bağlanamıyor (CORS hatası)

ÇÖZÜM: Backend'de CORS ayarlarını kontrol edin (app/main.py):
allow_origins listesinde frontend URL'i olmalı

PROBLEM: Docker container'lar çakışıyor

ÇÖZÜM:
docker-compose down
docker system prune -a
docker-compose up -d

════════════════════════════════════════════════════════════════════════════════
SONUÇ
════════════════════════════════════════════════════════════════════════════════

Bu platform, modern yazılım geliştirme tekniklerini bir araya getiren kapsamlı bir projedir. FastAPI, React, PostgreSQL, LLM API'leri, Groq Whisper, Edge-TTS gibi teknolojiler birlikte kullanılarak kullanıcılara değer sağlayan bir sistem oluşturulmuştur.

Temel başarı faktörleri:

- Bağlamsal analiz (aynı CV farklı profiller için farklı değerlendirilir)
- Sesli mülakat (Groq + Edge-TTS entegrasyonu)
- Akıllı skill matching (LLM'siz, hızlı)
- Kişiselleştirilmiş tavsiyeler
- Context-aware chatbot

Geliştirme süreci boyunca öğrenilen dersler:

- LLM prompt engineering'in önemi
- Retry mekanizmalarının gerekliliği
- Kullanıcı verilerinin etkin kullanımı
- Modüler mimari tasarımı
- API entegrasyonlarında hata yönetimi

Gelecek geliştirmeler için fikirler:

- Gerçek zamanlı mülakat feedback'i
- Video mülakat desteği
- Çoklu dil desteği
- Mobil uygulama
- Sosyal medya entegrasyonu

Projeyi geliştiren ekip olarak, bu dökümanın sistemi anlamak ve geliştirmek isteyenler için faydalı olmasını umuyoruz. Sorularınız için lütfen iletişime geçin.

"""
KariyerKoçu - Kariyer Bilgi Bankası
===================================
Her alan için öğrenme kaynakları, proje fikirleri ve tavsiyeler.
Bu dosya tavsiye sisteminin bilgi kaynağıdır.
"""

# ============================================================================
# ALAN BAZLI ZORUNLU TEKNOLOJİLER (CV'de mutlaka olması gerekenler)
# ============================================================================

REQUIRED_TECHNOLOGIES = {
    "backend": {
        "name": "Backend Developer",
        "must_know": [
            {"tech": "Python", "desc": "Backend geliştirmede temel programlama dili. Fonksiyonlar, OOP, veri yapıları bilgisi şart."},
            {"tech": "FastAPI", "desc": "Modern Python web framework'ü. REST API geliştirmek için endüstri standardı."},
            {"tech": "Django", "desc": "Full-stack Python framework'ü. Admin paneli, ORM ve güvenlik özellikleri içerir."},
            {"tech": "PostgreSQL", "desc": "İlişkisel veritabanı. SQL sorguları, JOIN, indexing bilgisi gerekli."},
            {"tech": "SQLAlchemy", "desc": "Python ORM kütüphanesi. Veritabanı işlemlerini Python koduyla yapmayı sağlar."},
            {"tech": "JWT", "desc": "JSON Web Token - API kimlik doğrulama standardı. Access/Refresh token mantığı."},
            {"tech": "Docker", "desc": "Containerization aracı. Uygulamayı her ortamda aynı şekilde çalıştırmayı sağlar."},
            {"tech": "Git", "desc": "Versiyon kontrol sistemi. Branch, merge, pull request akışı bilgisi şart."},
            {"tech": "REST API", "desc": "HTTP metodları, status code'ları, endpoint tasarımı bilgisi."},
            {"tech": "Redis", "desc": "In-memory cache ve message broker. API performansı için kritik."},
            {"tech": "Celery", "desc": "Asenkron görev kuyruğu. Uzun süren işlemleri arka planda çalıştırır."},
            {"tech": "Pytest", "desc": "Python test framework'ü. Unit test ve integration test yazımı."},
        ],
        "common_with_all": ["Git", "Docker", "Linux", "Problem Çözme", "İngilizce Dokümantasyon Okuma"]
    },
    "yapay_zeka": {
        "name": "ML/AI Engineer",
        "must_know": [
            {"tech": "Python", "desc": "Yapay zeka geliştirmede temel dil. NumPy, list comprehension bilgisi şart."},
            {"tech": "NumPy", "desc": "Sayısal hesaplama kütüphanesi. Array işlemleri, linear algebra."},
            {"tech": "Pandas", "desc": "Veri manipülasyon kütüphanesi. CSV okuma, filtreleme, gruplama."},
            {"tech": "Scikit-Learn", "desc": "Klasik ML kütüphanesi. Classification, Regression, Feature Engineering."},
            {"tech": "TensorFlow", "desc": "Google'ın deep learning framework'ü. Neural network eğitimi."},
            {"tech": "PyTorch", "desc": "Meta'nın deep learning framework'ü. Araştırma ve production için popüler."},
            {"tech": "OpenCV", "desc": "Görüntü işleme kütüphanesi. Resize, crop, color space dönüşümleri."},
            {"tech": "YOLO", "desc": "Real-time nesne tespiti. Ultralytics kütüphanesi ile kolay kullanım."},
            {"tech": "Hugging Face", "desc": "NLP model hub'ı. Transformers kütüphanesi ile BERT, GPT kullanımı."},
            {"tech": "LangChain", "desc": "LLM uygulama geliştirme framework'ü. RAG, agents, chains."},
            {"tech": "MLflow", "desc": "ML experiment tracking ve model versioning aracı."},
            {"tech": "ONNX", "desc": "Model optimizasyon formatı. CPU'da hızlı inference için kritik."},
            {"tech": "Docker", "desc": "Model deployment için konteynerizasyon."},
            {"tech": "FastAPI", "desc": "Model serving için API geliştirme framework'ü."},
        ],
        "common_with_all": ["Git", "Docker", "Linux", "Matematik (Lineer Cebir)", "İstatistik"]
    },
    "frontend": {
        "name": "Frontend Developer",
        "must_know": [
            {"tech": "JavaScript", "desc": "Web'in programlama dili. ES6+, async/await, DOM manipülasyonu."},
            {"tech": "TypeScript", "desc": "JavaScript'in tip güvenli versiyonu. Interface, generic, type guard."},
            {"tech": "React", "desc": "UI geliştirme kütüphanesi. Component, hooks, state management."},
            {"tech": "Next.js", "desc": "React framework'ü. SSR, routing, API routes."},
            {"tech": "HTML/CSS", "desc": "Web'in yapı taşları. Semantic HTML, Flexbox, Grid."},
            {"tech": "Tailwind CSS", "desc": "Utility-first CSS framework'ü. Hızlı styling."},
            {"tech": "Git", "desc": "Versiyon kontrol. Branch stratejileri."},
            {"tech": "REST API", "desc": "Backend ile iletişim. Fetch, Axios kullanımı."},
            {"tech": "Vite", "desc": "Modern build tool. Hot reload, fast bundling."},
        ],
        "common_with_all": ["Git", "Responsive Design", "Browser DevTools", "Web Accessibility"]
    },
    "fullstack": {
        "name": "Fullstack Developer", 
        "must_know": [
            {"tech": "Python", "desc": "Backend için temel dil."},
            {"tech": "JavaScript/TypeScript", "desc": "Frontend için temel dil."},
            {"tech": "React", "desc": "Frontend UI framework'ü."},
            {"tech": "FastAPI/Django", "desc": "Backend web framework'ü."},
            {"tech": "PostgreSQL", "desc": "İlişkisel veritabanı."},
            {"tech": "Docker", "desc": "Deployment için konteynerizasyon."},
            {"tech": "Git", "desc": "Versiyon kontrol."},
            {"tech": "REST API", "desc": "Frontend-Backend iletişimi."},
        ],
        "common_with_all": ["Git", "Docker", "CI/CD", "Cloud Basics"]
    },
    "data_science": {
        "name": "Data Scientist",
        "must_know": [
            {"tech": "Python", "desc": "Veri bilimi için temel dil."},
            {"tech": "Pandas", "desc": "Veri manipülasyonu."},
            {"tech": "NumPy", "desc": "Sayısal hesaplama."},
            {"tech": "Matplotlib/Seaborn", "desc": "Veri görselleştirme."},
            {"tech": "Scikit-Learn", "desc": "Makine öğrenmesi."},
            {"tech": "SQL", "desc": "Veritabanı sorguları."},
            {"tech": "Jupyter Notebook", "desc": "İnteraktif geliştirme ortamı."},
            {"tech": "İstatistik", "desc": "Hypothesis testing, A/B test."},
        ],
        "common_with_all": ["Git", "SQL", "Data Visualization", "Statistics"]
    }
}

def get_required_technologies(field_id: str) -> dict:
    """Belirli alan için zorunlu teknolojileri döndür."""
    return REQUIRED_TECHNOLOGIES.get(field_id, REQUIRED_TECHNOLOGIES.get("backend", {}))

def find_missing_technologies(field_id: str, cv_skills: list) -> list:
    """CV'de eksik olan zorunlu teknolojileri bul."""
    required = get_required_technologies(field_id)
    must_know = required.get("must_know", [])
    
    # CV skill'lerini lowercase yap
    cv_skills_lower = [s.lower() for s in cv_skills]
    
    missing = []
    for tech in must_know:
        tech_name = tech["tech"].lower()
        # CV'de bu teknoloji var mı kontrol et
        found = any(tech_name in skill or skill in tech_name for skill in cv_skills_lower)
        if not found:
            missing.append(tech)
    
    return missing

# ============================================================================
# BACKEND DEVELOPMENT
# ============================================================================

BACKEND_KNOWLEDGE = {
    "field_id": "backend",
    "field_name": "Backend Development",
    
    "learning_path": [
        {
            "order": 1,
            "skill": "Python Temelleri",
            "description": "Değişkenler, fonksiyonlar, OOP, dosya işlemleri",
            "resources": [
                {"type": "course", "name": "Python for Everybody (Coursera)", "url": "https://www.coursera.org/specializations/python"},
                {"type": "video", "name": "Corey Schafer Python Tutorial", "url": "https://www.youtube.com/playlist?list=PL-osiE80TeTt2d9bfVyTiXJA-UTHn6WwU"},
            ],
            "duration": "2-3 hafta"
        },
        {
            "order": 2,
            "skill": "FastAPI / Django",
            "description": "Web framework, REST API geliştirme, routing, middleware",
            "resources": [
                {"type": "docs", "name": "FastAPI Resmi Dokümantasyon", "url": "https://fastapi.tiangolo.com/"},
                {"type": "course", "name": "FastAPI - The Complete Course (Udemy)", "url": "https://www.udemy.com/course/fastapi-the-complete-course/"},
            ],
            "duration": "2-4 hafta"
        },
        {
            "order": 3,
            "skill": "Veritabanı (SQL + ORM)",
            "description": "PostgreSQL, SQLAlchemy, ilişkiler, indexing, N+1 problemi",
            "resources": [
                {"type": "course", "name": "SQL for Data Science (Coursera)", "url": "https://www.coursera.org/learn/sql-for-data-science"},
                {"type": "docs", "name": "SQLAlchemy Tutorial", "url": "https://docs.sqlalchemy.org/en/20/tutorial/"},
            ],
            "duration": "2-3 hafta"
        },
        {
            "order": 4,
            "skill": "API Güvenliği",
            "description": "JWT, OAuth2, CORS, rate limiting, input validation",
            "resources": [
                {"type": "docs", "name": "FastAPI Security", "url": "https://fastapi.tiangolo.com/tutorial/security/"},
                {"type": "article", "name": "OWASP Top 10", "url": "https://owasp.org/www-project-top-ten/"},
            ],
            "duration": "1-2 hafta"
        },
        {
            "order": 5,
            "skill": "Docker",
            "description": "Containerization, Dockerfile, docker-compose",
            "resources": [
                {"type": "course", "name": "Docker Mastery (Udemy)", "url": "https://www.udemy.com/course/docker-mastery/"},
                {"type": "docs", "name": "Docker Get Started", "url": "https://docs.docker.com/get-started/"},
            ],
            "duration": "1-2 hafta"
        },
        {
            "order": 6,
            "skill": "Test Yazma",
            "description": "Pytest, unit test, integration test, mocking",
            "resources": [
                {"type": "docs", "name": "Pytest Documentation", "url": "https://docs.pytest.org/"},
                {"type": "video", "name": "Testing Python Applications", "url": "https://realpython.com/pytest-python-testing/"},
            ],
            "duration": "1-2 hafta"
        },
    ],
    
    "project_ideas": [
        {
            "name": "Todo API",
            "difficulty": "Başlangıç",
            "description": "CRUD işlemleri, JWT authentication, PostgreSQL",
            "skills": ["FastAPI", "SQLAlchemy", "JWT", "PostgreSQL"]
        },
        {
            "name": "E-Ticaret Backend",
            "difficulty": "Orta",
            "description": "Ürün yönetimi, sepet, ödeme entegrasyonu, admin paneli",
            "skills": ["FastAPI", "Redis", "Celery", "Payment API"]
        },
        {
            "name": "Real-time Chat API",
            "difficulty": "İleri",
            "description": "WebSocket, mesaj geçmişi, bildirimler, dosya paylaşımı",
            "skills": ["WebSocket", "Redis Pub/Sub", "File Upload"]
        },
    ],
    
    "certifications": [
        {"name": "AWS Certified Developer", "provider": "Amazon", "difficulty": "Orta"},
        {"name": "MongoDB Developer", "provider": "MongoDB University", "difficulty": "Başlangıç"},
    ],
    
    "quick_tips": [
        "Her projeye README.md ekle - GitHub profilin CV'n kadar önemli",
        "Commit mesajlarını anlamlı yaz: feat:, fix:, docs: formatını kullan",
        "Postman veya Thunder Client ile API'lerini test et",
        "Environment variable'ları .env dosyasında tut, asla commit'leme",
    ]
}

# ============================================================================
# YAPAY ZEKA / MACHINE LEARNING
# ============================================================================

AI_ML_KNOWLEDGE = {
    "field_id": "yapay_zeka",
    "field_name": "Yapay Zeka / Machine Learning",
    
    "learning_path": [
        {
            "order": 1,
            "skill": "Python + Veri Kütüphaneleri",
            "description": "NumPy, Pandas, Matplotlib ile veri manipülasyonu",
            "resources": [
                {"type": "course", "name": "Python for Data Science (IBM)", "url": "https://www.coursera.org/learn/python-for-applied-data-science-ai"},
                {"type": "docs", "name": "Pandas Documentation", "url": "https://pandas.pydata.org/docs/"},
            ],
            "duration": "2-3 hafta"
        },
        {
            "order": 2,
            "skill": "Klasik ML (Scikit-Learn)",
            "description": "Classification, Regression, Feature Engineering, Model Evaluation",
            "resources": [
                {"type": "course", "name": "Machine Learning (Andrew Ng)", "url": "https://www.coursera.org/learn/machine-learning"},
                {"type": "docs", "name": "Scikit-Learn User Guide", "url": "https://scikit-learn.org/stable/user_guide.html"},
            ],
            "duration": "4-6 hafta"
        },
        {
            "order": 3,
            "skill": "Deep Learning (PyTorch/TensorFlow)",
            "description": "Neural Networks, CNN, RNN, Transfer Learning",
            "resources": [
                {"type": "course", "name": "Deep Learning Specialization", "url": "https://www.coursera.org/specializations/deep-learning"},
                {"type": "course", "name": "PyTorch for Deep Learning", "url": "https://www.udemy.com/course/pytorch-for-deep-learning/"},
            ],
            "duration": "6-8 hafta"
        },
        {
            "order": 4,
            "skill": "Computer Vision (OpenCV + YOLO)",
            "description": "Görüntü işleme, nesne tespiti, yüz tanıma",
            "resources": [
                {"type": "docs", "name": "OpenCV Documentation", "url": "https://docs.opencv.org/"},
                {"type": "github", "name": "Ultralytics YOLO", "url": "https://github.com/ultralytics/ultralytics"},
            ],
            "duration": "3-4 hafta"
        },
        {
            "order": 5,
            "skill": "NLP & LLM",
            "description": "Transformer, BERT, GPT, Hugging Face, RAG",
            "resources": [
                {"type": "course", "name": "NLP with Transformers (Hugging Face)", "url": "https://huggingface.co/course"},
                {"type": "docs", "name": "LangChain Documentation", "url": "https://python.langchain.com/docs/"},
            ],
            "duration": "4-6 hafta"
        },
        {
            "order": 6,
            "skill": "MLOps",
            "description": "Model versioning, experiment tracking, deployment",
            "resources": [
                {"type": "course", "name": "MLOps Specialization", "url": "https://www.coursera.org/specializations/machine-learning-engineering-for-production-mlops"},
                {"type": "docs", "name": "MLflow Documentation", "url": "https://mlflow.org/docs/latest/index.html"},
            ],
            "duration": "2-3 hafta"
        },
    ],
    
    "project_ideas": [
        {
            "name": "Spam Email Classifier",
            "difficulty": "Başlangıç",
            "description": "Text classification, TF-IDF, Naive Bayes",
            "skills": ["Scikit-Learn", "Pandas", "NLP"]
        },
        {
            "name": "Object Detection App",
            "difficulty": "Orta",
            "description": "YOLO ile gerçek zamanlı nesne tespiti, webcam entegrasyonu",
            "skills": ["YOLO", "OpenCV", "PyTorch"]
        },
        {
            "name": "RAG Chatbot",
            "difficulty": "İleri",
            "description": "PDF'lerle konuşan chatbot, vector database, LangChain",
            "skills": ["LangChain", "ChromaDB", "OpenAI API", "FastAPI"]
        },
    ],
    
    "certifications": [
        {"name": "TensorFlow Developer Certificate", "provider": "Google", "difficulty": "Orta"},
        {"name": "AWS Machine Learning Specialty", "provider": "Amazon", "difficulty": "İleri"},
        {"name": "Deep Learning Specialization", "provider": "Coursera (DeepLearning.AI)", "difficulty": "Orta"},
    ],
    
    "quick_tips": [
        "Kaggle'da yarışmalara katıl - gerçek veri setleriyle çalışma deneyimi kazan",
        "Jupyter Notebook'ları temiz tut - başkasının okumasını bekle",
        "Model performansını sadece accuracy ile ölçme - F1, Precision, Recall öğren",
        "Weights & Biases ile deneylerini takip et",
        "ONNX formatı öğren - production'da çok işe yarar",
    ]
}

# ============================================================================
# TÜM ALANLAR (lookup için)
# ============================================================================

KNOWLEDGE_BASE = {
    "backend": BACKEND_KNOWLEDGE,
    "yapay_zeka": AI_ML_KNOWLEDGE,
}

# ============================================================================
# GENEL TAVSİYELER (Alan bağımsız)
# ============================================================================

GENERAL_ADVICE = {
    "github_profile": [
        "En iyi 4-6 projeyi profile pinle",
        "Her projeye README ekle: ne yapar, nasıl kurulur, ekran görüntüleri",
        "Contribution graph'ı yeşil tut - küçük de olsa günlük commit",
    ],
    "soft_skills": [
        "Projeleri STAR tekniğiyle anlat: Situation, Task, Action, Result",
        "Bilmediğin konuda 'Bilmiyorum ama öğrenebilirim' de - dürüstlük değerli",
        "Mülakatta sayılar kullan: '%40 performans artışı sağladım'",
    ],
    "interview_prep": [
        "LeetCode'da 'Blind 75' listesine başla - en kritik 75 DSA sorusu",
        "Her gün en az 1 algoritma sorusu çöz",
        "Mock interview yap - arkadaşla veya Pramp.com üzerinden",
    ],
    "certifications": [
        "Öğrenciler için: Coursera kursları (sertifika bedava olabilir)",
        "Cloud öğrenmek isteyenler: AWS Cloud Practitioner ile başla",
        "ML için: TensorFlow Developer Certificate prestijli",
    ],
}

# ============================================================================
# YARDIMCI FONKSİYONLAR
# ============================================================================

def get_knowledge_for_field(field_id: str) -> dict:
    """Belirli alan için bilgi bankasını döndür."""
    return KNOWLEDGE_BASE.get(field_id, {})

def get_learning_path(field_id: str) -> list:
    """Belirli alan için öğrenme yolunu döndür."""
    knowledge = get_knowledge_for_field(field_id)
    return knowledge.get("learning_path", [])

def get_project_ideas(field_id: str) -> list:
    """Belirli alan için proje fikirlerini döndür."""
    knowledge = get_knowledge_for_field(field_id)
    return knowledge.get("project_ideas", [])

def get_certifications(field_id: str) -> list:
    """Belirli alan için sertifika önerilerini döndür."""
    knowledge = get_knowledge_for_field(field_id)
    return knowledge.get("certifications", [])

def get_quick_tips(field_id: str) -> list:
    """Belirli alan için hızlı ipuçlarını döndür."""
    knowledge = get_knowledge_for_field(field_id)
    return knowledge.get("quick_tips", [])

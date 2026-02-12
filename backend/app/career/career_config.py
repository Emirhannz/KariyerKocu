"""
KariyerKoçu - Kariyer Konfigürasyonu
====================================
Sektör, alan ve tecrübe seviyeleri için sabit veriler.
Frontend dropdown'ları buradan beslenecek.
"""

# ============================================================================
# SEKTÖRLER
# ============================================================================

SECTORS = {
    "bilgisayar_muhendisligi": {
        "name": "Bilgisayar Mühendisliği",
        "fields": [
            "backend",
            "frontend", 
            "fullstack",
            "mobile",
            "devops",
            "data_science",
            "yapay_zeka",
            "embedded",
            "cybersecurity",
            "game_dev"
        ]
    },
    # İleride eklenecek:
    # "elektrik_elektronik": {...},
    # "makine_muhendisligi": {...},
}

# ============================================================================
# ALANLAR (Fields)
# ============================================================================

FIELDS = {
    "backend": {
        "name": "Backend Development",
        "key_skills": ["Python", "Java", "Node.js", "FastAPI", "Django", "Spring", "SQL", "PostgreSQL", "MongoDB", "Redis", "Docker", "REST API", "GraphQL"],
        "nice_to_have": ["Kubernetes", "AWS", "GCP", "Microservices", "Message Queues", "CI/CD"]
    },
    "frontend": {
        "name": "Frontend Development",
        "key_skills": ["JavaScript", "TypeScript", "React", "Vue", "Angular", "HTML", "CSS", "TailwindCSS", "Redux", "Next.js"],
        "nice_to_have": ["Testing", "Webpack", "PWA", "Performance Optimization"]
    },
    "fullstack": {
        "name": "Full-Stack Development",
        "key_skills": ["JavaScript", "Python", "React", "Node.js", "SQL", "REST API", "Git"],
        "nice_to_have": ["Docker", "CI/CD", "Cloud", "Testing"]
    },
    "mobile": {
        "name": "Mobile Development",
        "key_skills": ["Flutter", "React Native", "Swift", "Kotlin", "Dart", "REST API", "Firebase"],
        "nice_to_have": ["CI/CD", "App Store Optimization", "Push Notifications"]
    },
    "devops": {
        "name": "DevOps / SRE",
        "key_skills": ["Linux", "Docker", "Kubernetes", "CI/CD", "Jenkins", "GitHub Actions", "AWS", "GCP", "Terraform", "Ansible"],
        "nice_to_have": ["Monitoring", "Prometheus", "Grafana", "Security"]
    },
    "data_science": {
        "name": "Data Science",
        "key_skills": ["Python", "Pandas", "NumPy", "SQL", "Statistics", "Machine Learning", "Visualization", "Jupyter"],
        "nice_to_have": ["Spark", "Airflow", "A/B Testing", "Business Analytics"]
    },
    "yapay_zeka": {
        "name": "Yapay Zeka / Machine Learning",
        "key_skills": ["Python", "TensorFlow", "PyTorch", "Deep Learning", "CNN", "NLP", "Computer Vision", "OpenCV", "Scikit-learn"],
        "nice_to_have": ["MLOps", "Hugging Face", "LLM", "Reinforcement Learning", "Research Papers"]
    },
    "embedded": {
        "name": "Embedded Systems",
        "key_skills": ["C", "C++", "Microcontrollers", "RTOS", "Arduino", "Raspberry Pi", "Electronics", "Assembly"],
        "nice_to_have": ["FPGA", "IoT", "Sensors", "Communication Protocols"]
    },
    "cybersecurity": {
        "name": "Cybersecurity",
        "key_skills": ["Linux", "Networking", "Python", "Penetration Testing", "Cryptography", "OWASP", "Wireshark"],
        "nice_to_have": ["CEH", "OSCP", "SOC", "Incident Response", "Malware Analysis"]
    },
    "game_dev": {
        "name": "Game Development",
        "key_skills": ["Unity", "Unreal Engine", "C#", "C++", "Game Design", "3D Math", "Physics"],
        "nice_to_have": ["Shaders", "Multiplayer", "AI", "VR/AR"]
    }
}

# ============================================================================
# TECRüBE SEVİYELERİ
# ============================================================================

EXPERIENCE_LEVELS = {
    "ogrenci_1": {"name": "1. Sınıf Öğrenci", "years": 0, "category": "student"},
    "ogrenci_2": {"name": "2. Sınıf Öğrenci", "years": 0, "category": "student"},
    "ogrenci_3": {"name": "3. Sınıf Öğrenci", "years": 0, "category": "student"},
    "ogrenci_4": {"name": "4. Sınıf Öğrenci", "years": 0, "category": "student"},
    "yeni_mezun": {"name": "Yeni Mezun (0-1 yıl)", "years": 0.5, "category": "entry"},
    "junior": {"name": "Junior (1-3 yıl)", "years": 2, "category": "junior"},
    "mid": {"name": "Mid-Level (3-5 yıl)", "years": 4, "category": "mid"},
    "senior": {"name": "Senior (5-10 yıl)", "years": 7, "category": "senior"},
    "lead": {"name": "Lead/Principal (10+ yıl)", "years": 12, "category": "lead"},
}

# ============================================================================
# BEKLENTİLER MATRİSİ
# ============================================================================

# Her tecrübe seviyesi için minimum beklentiler
EXPECTATIONS = {
    "student": {
        "min_projects": 2,
        "min_field_projects": 1,
        "gpa_important": True,
        "certifications_required": False,
        "experience_required": False,
        "description": "Öğrenci için projeler ve öğrenme isteği önemli"
    },
    "entry": {
        "min_projects": 3,
        "min_field_projects": 2,
        "gpa_important": True,
        "certifications_required": False,
        "experience_required": False,
        "description": "Yeni mezun için portfolyo ve staj deneyimi değerli"
    },
    "junior": {
        "min_projects": 5,
        "min_field_projects": 3,
        "gpa_important": False,
        "certifications_required": True,
        "experience_required": True,
        "min_experience_months": 12,
        "description": "Junior için profesyonel deneyim beklenir"
    },
    "mid": {
        "min_projects": 8,
        "min_field_projects": 5,
        "gpa_important": False,
        "certifications_required": True,
        "experience_required": True,
        "min_experience_months": 36,
        "description": "Mid-level için liderlik ve mimari bilgisi beklenir"
    },
    "senior": {
        "min_projects": 10,
        "min_field_projects": 7,
        "gpa_important": False,
        "certifications_required": True,
        "experience_required": True,
        "min_experience_months": 60,
        "description": "Senior için mentorluk ve system design beklenir"
    },
    "lead": {
        "min_projects": 15,
        "min_field_projects": 10,
        "gpa_important": False,
        "certifications_required": True,
        "experience_required": True,
        "min_experience_months": 120,
        "description": "Lead için takım yönetimi ve stratejik düşünce beklenir"
    }
}

# ============================================================================
# PUANLAMA AĞIRLIKLARI (Tecrübe seviyesine göre)
# ============================================================================

SCORING_WEIGHTS = {
    "student": {
        "summary": 10,
        "education": 20,
        "experience": 15,
        "projects": 30,
        "skills": 15,
        "certifications": 5,
        "languages": 5
    },
    "entry": {
        "summary": 10,
        "education": 15,
        "experience": 20,
        "projects": 25,
        "skills": 15,
        "certifications": 10,
        "languages": 5
    },
    "junior": {
        "summary": 10,
        "education": 10,
        "experience": 30,
        "projects": 20,
        "skills": 15,
        "certifications": 10,
        "languages": 5
    },
    "mid": {
        "summary": 10,
        "education": 5,
        "experience": 35,
        "projects": 20,
        "skills": 15,
        "certifications": 10,
        "languages": 5
    },
    "senior": {
        "summary": 10,
        "education": 5,
        "experience": 40,
        "projects": 15,
        "skills": 15,
        "certifications": 10,
        "languages": 5
    },
    "lead": {
        "summary": 15,
        "education": 5,
        "experience": 40,
        "projects": 10,
        "skills": 15,
        "certifications": 10,
        "languages": 5
    }
}


# ============================================================================
# YARDIMCI FONKSİYONLAR
# ============================================================================

def get_sectors_list():
    """Frontend için sektör listesi döndür."""
    return [
        {"id": k, "name": v["name"]}
        for k, v in SECTORS.items()
    ]

def get_fields_for_sector(sector_id: str):
    """Belirli sektör için alan listesi döndür."""
    if sector_id not in SECTORS:
        return []
    
    field_ids = SECTORS[sector_id]["fields"]
    return [
        {"id": fid, "name": FIELDS[fid]["name"]}
        for fid in field_ids
        if fid in FIELDS
    ]

def get_experience_levels_list():
    """Frontend için tecrübe seviyesi listesi döndür."""
    return [
        {"id": k, "name": v["name"], "category": v["category"]}
        for k, v in EXPERIENCE_LEVELS.items()
    ]

def get_expectations(experience_level: str):
    """Tecrübe seviyesine göre beklentileri döndür."""
    if experience_level not in EXPERIENCE_LEVELS:
        return EXPECTATIONS["entry"]
    
    category = EXPERIENCE_LEVELS[experience_level]["category"]
    return EXPECTATIONS.get(category, EXPECTATIONS["entry"])

def get_scoring_weights(experience_level: str):
    """Tecrübe seviyesine göre puanlama ağırlıklarını döndür."""
    if experience_level not in EXPERIENCE_LEVELS:
        return SCORING_WEIGHTS["entry"]
    
    category = EXPERIENCE_LEVELS[experience_level]["category"]
    return SCORING_WEIGHTS.get(category, SCORING_WEIGHTS["entry"])

def get_field_skills(field_id: str):
    """Alanın beklenen becerilerini döndür."""
    if field_id not in FIELDS:
        return {"key_skills": [], "nice_to_have": []}
    
    return {
        "key_skills": FIELDS[field_id]["key_skills"],
        "nice_to_have": FIELDS[field_id]["nice_to_have"]
    }

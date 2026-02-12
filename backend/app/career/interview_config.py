"""
KariyerKoçu - Mülakat Konfigürasyonu
====================================
Mülakat sistemi için dropdown verileri ve sabit değerler.
"""

# ============================================================================
# FİRMA SEKTÖRLERİ
# ============================================================================

COMPANY_SECTORS = {
    "yazilim": {
        "name": "Yazılım / Teknoloji",
        "positions": [
            "backend_developer",
            "frontend_developer",
            "fullstack_developer",
            "mobile_developer",
            "devops_engineer",
            "data_scientist",
            "ml_engineer",
            "qa_engineer",
            "software_architect"
        ]
    },
    "donanim": {
        "name": "Donanım / Elektronik",
        "positions": [
            "embedded_engineer",
            "hardware_engineer",
            "fpga_developer",
            "iot_engineer"
        ]
    },
    "fintech": {
        "name": "Fintech / Finansal Teknoloji",
        "positions": [
            "backend_developer",
            "data_engineer",
            "security_engineer",
            "blockchain_developer"
        ]
    },
    "eticaret": {
        "name": "E-Ticaret",
        "positions": [
            "backend_developer",
            "frontend_developer",
            "fullstack_developer",
            "data_analyst"
        ]
    },
    "oyun": {
        "name": "Oyun / Game Development",
        "positions": [
            "game_developer",
            "unity_developer",
            "unreal_developer",
            "game_designer"
        ]
    },
    "siber_guvenlik": {
        "name": "Siber Güvenlik",
        "positions": [
            "security_engineer",
            "penetration_tester",
            "soc_analyst",
            "security_architect"
        ]
    }
}

# ============================================================================
# POZİSYONLAR
# ============================================================================

POSITIONS = {
    "backend_developer": {
        "name": "Backend Developer",
        "key_topics": ["API tasarımı", "Veritabanı", "Güvenlik", "Performans", "Docker"]
    },
    "frontend_developer": {
        "name": "Frontend Developer",
        "key_topics": ["React/Vue", "State yönetimi", "CSS", "Performance", "Testing"]
    },
    "fullstack_developer": {
        "name": "Full-Stack Developer",
        "key_topics": ["Backend", "Frontend", "Veritabanı", "API", "Deployment"]
    },
    "mobile_developer": {
        "name": "Mobile Developer",
        "key_topics": ["Flutter/React Native", "Native geliştirme", "UI/UX", "App Store"]
    },
    "devops_engineer": {
        "name": "DevOps Engineer",
        "key_topics": ["CI/CD", "Docker", "Kubernetes", "Cloud", "Monitoring"]
    },
    "data_scientist": {
        "name": "Data Scientist",
        "key_topics": ["ML algoritmaları", "İstatistik", "Python", "Veri analizi"]
    },
    "ml_engineer": {
        "name": "Machine Learning Engineer",
        "key_topics": ["Deep Learning", "MLOps", "Model deployment", "NLP/CV"]
    },
    "qa_engineer": {
        "name": "QA Engineer",
        "key_topics": ["Test stratejileri", "Otomasyon", "Selenium", "API testing"]
    },
    "software_architect": {
        "name": "Software Architect",
        "key_topics": ["System design", "Microservices", "Scalability", "Patterns"]
    },
    "embedded_engineer": {
        "name": "Embedded Systems Engineer",
        "key_topics": ["C/C++", "RTOS", "Microcontrollers", "Low-level programming"]
    },
    "hardware_engineer": {
        "name": "Hardware Engineer",
        "key_topics": ["PCB tasarımı", "Elektronik", "Prototyping"]
    },
    "fpga_developer": {
        "name": "FPGA Developer",
        "key_topics": ["Verilog", "VHDL", "Digital design"]
    },
    "iot_engineer": {
        "name": "IoT Engineer",
        "key_topics": ["Sensörler", "Protokoller", "Cloud IoT", "Edge computing"]
    },
    "data_engineer": {
        "name": "Data Engineer",
        "key_topics": ["ETL", "Data pipelines", "Spark", "Data warehousing"]
    },
    "security_engineer": {
        "name": "Security Engineer",
        "key_topics": ["OWASP", "Güvenlik açıkları", "Şifreleme", "Network security"]
    },
    "blockchain_developer": {
        "name": "Blockchain Developer",
        "key_topics": ["Smart contracts", "Solidity", "Web3"]
    },
    "game_developer": {
        "name": "Game Developer",
        "key_topics": ["Game engines", "3D math", "Physics", "Optimization"]
    },
    "unity_developer": {
        "name": "Unity Developer",
        "key_topics": ["C#", "Unity API", "Shader", "Mobile optimization"]
    },
    "unreal_developer": {
        "name": "Unreal Engine Developer",
        "key_topics": ["C++", "Blueprints", "Rendering", "Multiplayer"]
    },
    "game_designer": {
        "name": "Game Designer",
        "key_topics": ["Game mechanics", "Level design", "Player psychology"]
    },
    "penetration_tester": {
        "name": "Penetration Tester",
        "key_topics": ["Ethical hacking", "Vulnerability assessment", "Tools"]
    },
    "soc_analyst": {
        "name": "SOC Analyst",
        "key_topics": ["Threat detection", "SIEM", "Incident response"]
    },
    "security_architect": {
        "name": "Security Architect",
        "key_topics": ["Security frameworks", "Risk assessment", "Zero trust"]
    },
    "data_analyst": {
        "name": "Data Analyst",
        "key_topics": ["SQL", "Visualization", "Excel", "Business analytics"]
    }
}

# ============================================================================
# ARANAN TECRüBE SEVİYELERİ
# ============================================================================

EXPERIENCE_REQUIREMENTS = {
    "stajyer": {
        "name": "Stajyer",
        "difficulty": "easy",
        "question_depth": "basic",
        "expected_knowledge": "Temel kavramlar, öğrenme isteği"
    },
    "yeni_mezun": {
        "name": "Yeni Mezun (0-1 yıl)",
        "difficulty": "easy",
        "question_depth": "basic_to_intermediate",
        "expected_knowledge": "Temel kavramlar + bazı pratik deneyim"
    },
    "junior": {
        "name": "Junior (1-3 yıl)",
        "difficulty": "medium",
        "question_depth": "intermediate",
        "expected_knowledge": "Pratik deneyim, problem çözme"
    },
    "mid_level": {
        "name": "Mid-Level (3-5 yıl)",
        "difficulty": "medium_hard",
        "question_depth": "intermediate_to_advanced",
        "expected_knowledge": "Derin teknik bilgi, mimari anlayış"
    },
    "senior": {
        "name": "Senior (5+ yıl)",
        "difficulty": "hard",
        "question_depth": "advanced",
        "expected_knowledge": "Liderlik, system design, best practices"
    },
    "lead": {
        "name": "Tech Lead / Principal",
        "difficulty": "expert",
        "question_depth": "expert",
        "expected_knowledge": "Mimari kararlar, takım yönetimi, stratejik düşünce"
    }
}

# ============================================================================
# MÜLAKAT TİPLERİ
# ============================================================================

INTERVIEW_TYPES = {
    "sektorel": {
        "name": "Sektörel (Teknik)",
        "description": "Pozisyona özel teknik sorular. Teorik bilgi ve problem çözme.",
        "question_style": "technical"
    },
    "sektor_yorum": {
        "name": "Sektör + Yorum (CV Bazlı)",
        "description": "CV'deki projeler hakkında sorular + senaryo bazlı değerlendirme.",
        "question_style": "mixed"
    }
}

# ============================================================================
# MÜLAKAT AYARLARI
# ============================================================================

INTERVIEW_SETTINGS = {
    "min_questions": 5,
    "max_questions": 10,
    "default_questions": 7,
    "score_range": (1, 10),
    "passing_score": 6.0
}

# ============================================================================
# YARDIMCI FONKSİYONLAR
# ============================================================================

def get_sectors_list():
    """Dropdown için sektör listesi."""
    return [
        {"id": k, "name": v["name"]}
        for k, v in COMPANY_SECTORS.items()
    ]

def get_positions_for_sector(sector_id: str):
    """Sektöre göre pozisyon listesi."""
    if sector_id not in COMPANY_SECTORS:
        return []
    
    position_ids = COMPANY_SECTORS[sector_id]["positions"]
    return [
        {"id": pid, "name": POSITIONS[pid]["name"]}
        for pid in position_ids
        if pid in POSITIONS
    ]

def get_experience_list():
    """Dropdown için tecrübe listesi."""
    return [
        {"id": k, "name": v["name"]}
        for k, v in EXPERIENCE_REQUIREMENTS.items()
    ]

def get_interview_types_list():
    """Dropdown için mülakat tipi listesi."""
    return [
        {"id": k, "name": v["name"], "description": v["description"]}
        for k, v in INTERVIEW_TYPES.items()
    ]

def get_position_topics(position_id: str):
    """Pozisyonun anahtar konularını döndür."""
    if position_id not in POSITIONS:
        return []
    return POSITIONS[position_id].get("key_topics", [])

def get_experience_difficulty(experience_id: str):
    """Tecrübe seviyesine göre zorluk bilgisi."""
    if experience_id not in EXPERIENCE_REQUIREMENTS:
        return {"difficulty": "medium", "question_depth": "intermediate"}
    return EXPERIENCE_REQUIREMENTS[experience_id]

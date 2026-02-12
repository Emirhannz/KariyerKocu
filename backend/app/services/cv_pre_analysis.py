# -*- coding: utf-8 -*-
"""
CV Pre-Analysis Service
=======================
CV verisinden sayısal metrikleri çıkarır ve LLM'e gönderilmeden önce
tutarlı bir analiz tablosu oluşturur.

Bu modül JSON formatındaki CV verisi üzerinde çalışır (LLM parse sonrası).
"""

import re
from typing import Dict, Any, List, Optional
from datetime import datetime


class CVPreAnalysis:
    """
    CV verisinden sayısal ve mantıksal metrikleri çıkarır.
    
    LLM'e göndermeden ÖNCE bu metrikleri hesaplayarak,
    daha tutarlı ve doğrulanabilir skorlar elde ederiz.
    """
    
    # GPA değerlendirme eşikleri (4'lük sistem)
    GPA_THRESHOLDS = {
        "excellent": 3.5,    # 3.50+ Mükemmel
        "good": 3.0,         # 3.00-3.49 İyi
        "average": 2.5,      # 2.50-2.99 Orta
        "below_average": 2.0 # 2.00-2.49 Ortanın altı
    }
    
    # Dil seviyesi eşleştirmeleri (CEFR)
    LANGUAGE_LEVELS = {
        "native": ["ana dil", "anadil", "native", "mother tongue", "ana dili"],
        "c2": ["c2", "proficiency", "ileri düzey", "çok iyi", "mükemmel", "fluent", "akıcı"],
        "c1": ["c1", "advanced", "ileri", "iyi"],
        "b2": ["b2", "upper intermediate", "üst orta", "orta üstü"],
        "b1": ["b1", "intermediate", "orta", "orta seviye"],
        "a2": ["a2", "elementary", "temel", "başlangıç üstü"],
        "a1": ["a1", "beginner", "başlangıç", "basic"]
    }
    
    # Deneyim türleri
    EXPERIENCE_TYPES = {
        "internship": ["staj", "intern", "internship", "stajyer"],
        "part_time": ["part-time", "yarı zamanlı", "part time", "parça zamanlı"],
        "full_time": ["full-time", "tam zamanlı", "full time"],
        "freelance": ["freelance", "serbest", "danışman", "consultant"],
        "volunteer": ["gönüllü", "volunteer", "volunteering"]
    }
    
    def analyze(self, cv_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        CV verisini analiz et ve detaylı metrikler çıkar.
        
        Args:
            cv_data: LLM tarafından parse edilmiş CV JSON verisi
            
        Returns:
            Tüm metrikleri içeren analiz sonucu
        """
        
        return {
            # Temel Bilgiler
            "personal": self._analyze_personal_info(cv_data),
            
            # Eğitim Analizi
            "education": self._analyze_education(cv_data),
            
            # Deneyim Analizi
            "experience": self._analyze_experience(cv_data),
            
            # Proje Analizi
            "projects": self._analyze_projects(cv_data),
            
            # Beceri Analizi
            "skills": self._analyze_skills(cv_data),
            
            # Sertifika Analizi
            "certifications": self._analyze_certifications(cv_data),
            
            # Dil Analizi
            "languages": self._analyze_languages(cv_data),
            
            # Özet/Hakkımda Analizi
            "summary": self._analyze_summary(cv_data),
            
            # Gönüllü Çalışma / Topluluk Analizi
            "volunteer": self._analyze_volunteer(cv_data),
            
            # Genel Metrikler
            "overall_metrics": self._calculate_overall_metrics(cv_data)
        }
    
    def _analyze_personal_info(self, cv_data: Dict) -> Dict:
        """Kişisel bilgi analizi."""
        email = cv_data.get("email")
        phone = cv_data.get("phone")
        linkedin = cv_data.get("linkedin")
        github = cv_data.get("github")
        
        return {
            "name_exists": bool(cv_data.get("full_name")),
            "email_exists": bool(email),
            "email_valid": bool(email and "@" in str(email)),
            "phone_exists": bool(phone),
            "linkedin_exists": bool(linkedin),
            "github_exists": bool(github),
            "has_online_presence": bool(linkedin or github),
            "completeness_score": self._calculate_personal_completeness(cv_data)
        }
    
    def _calculate_personal_completeness(self, cv_data: Dict) -> int:
        """Kişisel bilgi tamlık skoru (0-100)."""
        score = 0
        if cv_data.get("full_name"): score += 20
        if cv_data.get("email"): score += 25
        if cv_data.get("phone"): score += 20
        if cv_data.get("linkedin"): score += 20
        if cv_data.get("github"): score += 15
        return score
    
    def _analyze_education(self, cv_data: Dict) -> Dict:
        """Eğitim bilgisi analizi."""
        education = cv_data.get("education", [])
        
        # GPA analizi
        gpa_info = self._extract_gpa(cv_data)
        
        # Derece analizi
        degrees = self._analyze_degrees(education)
        
        return {
            "count": len(education),
            "exists": len(education) > 0,
            "gpa_exists": gpa_info["exists"],
            "gpa_value": gpa_info["value"],
            "gpa_scale": gpa_info["scale"],
            "gpa_normalized": gpa_info["normalized"],  # 4'lük sisteme normalize
            "gpa_rating": gpa_info["rating"],  # excellent/good/average/below
            "highest_degree": degrees.get("highest"),
            "degrees_list": degrees.get("list", []),
            "is_student": degrees.get("is_student", False),
            "graduation_year": degrees.get("graduation_year"),
            "field_of_study": degrees.get("field_of_study")
        }
    
    def _extract_gpa(self, cv_data: Dict) -> Dict:
        """GPA/AGNO bilgisini çıkar ve normalize et."""
        education = cv_data.get("education", [])
        
        # CV'de doğrudan GPA alanı var mı?
        gpa = cv_data.get("gpa") or cv_data.get("agno") or cv_data.get("not_ortalamasi")
        
        # Eğitim içinden GPA ara
        if not gpa and education:
            for edu in education:
                edu_gpa = edu.get("gpa") or edu.get("agno") or edu.get("grade")
                if edu_gpa:
                    gpa = edu_gpa
                    break
        
        if not gpa:
            return {
                "exists": False,
                "value": None,
                "scale": None,
                "normalized": None,
                "rating": None
            }
        
        # GPA değerini parse et
        gpa_value = self._parse_gpa_value(gpa)
        
        if gpa_value is None:
            return {
                "exists": False,
                "value": None,
                "scale": None,
                "normalized": None,
                "rating": None
            }
        
        # Ölçeği belirle (4'lük mü 100'lük mü)
        if gpa_value > 4:
            scale = 100
            normalized = (gpa_value / 100) * 4  # 100'lük'ten 4'lük'e
        else:
            scale = 4
            normalized = gpa_value
        
        # Rating belirle
        rating = "below_average"
        if normalized >= 3.5:
            rating = "excellent"
        elif normalized >= 3.0:
            rating = "good"
        elif normalized >= 2.5:
            rating = "average"
        
        return {
            "exists": True,
            "value": gpa_value,
            "scale": scale,
            "normalized": round(normalized, 2),
            "rating": rating
        }
    
    def _parse_gpa_value(self, gpa) -> Optional[float]:
        """GPA değerini float'a çevir."""
        if isinstance(gpa, (int, float)):
            return float(gpa)
        
        if isinstance(gpa, str):
            # "3.5", "3,5", "3.50/4.00", "85/100" gibi formatları parse et
            gpa = gpa.replace(",", ".")
            
            # "X/Y" formatı
            if "/" in gpa:
                parts = gpa.split("/")
                try:
                    return float(parts[0].strip())
                except:
                    pass
            
            # Sadece sayı
            match = re.search(r'(\d+\.?\d*)', gpa)
            if match:
                try:
                    return float(match.group(1))
                except:
                    pass
        
        return None
    
    def _analyze_degrees(self, education: List[Dict]) -> Dict:
        """Derece analizi."""
        degree_levels = {
            "phd": ["phd", "doktora", "doctorate"],
            "masters": ["masters", "yüksek lisans", "master", "msc", "mba"],
            "bachelors": ["bachelors", "lisans", "bachelor", "bsc", "bs"],
            "associate": ["ön lisans", "associate", "myo"],
            "high_school": ["lise", "high school"]
        }
        
        degrees = []
        highest = None
        is_student = False
        graduation_year = None
        field_of_study = None
        
        for edu in education:
            degree = edu.get("degree", "").lower()
            field = edu.get("field", "")
            end_year = edu.get("end_year")
            
            # Derece seviyesini belirle
            level = None
            for lvl, keywords in degree_levels.items():
                if any(kw in degree for kw in keywords):
                    level = lvl
                    break
            
            if level:
                degrees.append(level)
                if not highest or list(degree_levels.keys()).index(level) < list(degree_levels.keys()).index(highest):
                    highest = level
                    field_of_study = field
                    graduation_year = end_year
            
            # Öğrenci mi kontrol et
            if end_year:
                current_year = datetime.now().year
                if isinstance(end_year, int) and end_year >= current_year:
                    is_student = True
        
        return {
            "highest": highest,
            "list": degrees,
            "is_student": is_student,
            "graduation_year": graduation_year,
            "field_of_study": field_of_study
        }
    
    def _analyze_experience(self, cv_data: Dict) -> Dict:
        """İş deneyimi analizi."""
        experience = cv_data.get("experience", [])
        
        total_months = 0
        experience_types = []
        companies = []
        has_internship = False
        has_fulltime = False
        
        for exp in experience:
            # Süre hesapla
            duration = exp.get("duration", "")
            months = self._parse_duration_to_months(duration)
            total_months += months
            
            # Deneyim türünü belirle
            title = (exp.get("title", "") + " " + exp.get("description", "")).lower()
            exp_type = self._determine_experience_type(title)
            experience_types.append(exp_type)
            
            if exp_type == "internship":
                has_internship = True
            elif exp_type == "full_time":
                has_fulltime = True
            
            # Şirket bilgisi
            company = exp.get("company")
            if company:
                companies.append(company)
        
        years = total_months / 12
        
        return {
            "count": len(experience),
            "exists": len(experience) > 0,
            "total_months": total_months,
            "total_years": round(years, 1),
            "years_category": self._categorize_experience_years(years),
            "has_internship": has_internship,
            "has_fulltime": has_fulltime,
            "types": list(set(experience_types)),
            "companies": companies,
            "experience_rating": self._rate_experience(total_months, has_internship, has_fulltime)
        }
    
    def _parse_duration_to_months(self, duration: str) -> int:
        """Süre string'ini ay sayısına çevir."""
        if not duration:
            return 0
        
        duration = duration.lower()
        months = 0
        
        # "X yıl" formatı
        year_match = re.search(r'(\d+)\s*(yıl|year|yr)', duration)
        if year_match:
            months += int(year_match.group(1)) * 12
        
        # "X ay" formatı
        month_match = re.search(r'(\d+)\s*(ay|month|mo)', duration)
        if month_match:
            months += int(month_match.group(1))
        
        # Sadece sayı varsa ay olarak kabul et
        if months == 0:
            num_match = re.search(r'(\d+)', duration)
            if num_match:
                num = int(num_match.group(1))
                if num <= 24:  # 24'ten küçükse ay
                    months = num
        
        return months
    
    def _determine_experience_type(self, text: str) -> str:
        """Deneyim türünü belirle."""
        text = text.lower()
        
        for exp_type, keywords in self.EXPERIENCE_TYPES.items():
            if any(kw in text for kw in keywords):
                return exp_type
        
        return "full_time"  # Varsayılan
    
    def _categorize_experience_years(self, years: float) -> str:
        """Deneyim yılını kategorize et."""
        if years == 0:
            return "none"
        elif years < 1:
            return "entry"
        elif years < 3:
            return "junior"
        elif years < 5:
            return "mid"
        elif years < 10:
            return "senior"
        else:
            return "lead"
    
    def _rate_experience(self, months: int, has_internship: bool, has_fulltime: bool) -> str:
        """Deneyim puanlaması."""
        if months >= 60:  # 5+ yıl
            return "excellent"
        elif months >= 36:  # 3+ yıl
            return "good"
        elif months >= 12 or has_fulltime:  # 1+ yıl veya tam zamanlı
            return "average"
        elif months > 0 or has_internship:  # Staj var
            return "entry"
        else:
            return "none"
    
    def _analyze_projects(self, cv_data: Dict) -> Dict:
        """Proje analizi."""
        projects = cv_data.get("projects", [])
        
        technologies_used = set()
        projects_with_tech = 0
        projects_with_description = 0
        
        for proj in projects:
            techs = proj.get("technologies", [])
            if techs:
                technologies_used.update(techs)
                projects_with_tech += 1
            
            if proj.get("description"):
                projects_with_description += 1
        
        return {
            "count": len(projects),
            "exists": len(projects) > 0,
            "with_technologies": projects_with_tech,
            "with_description": projects_with_description,
            "unique_technologies": list(technologies_used),
            "technology_count": len(technologies_used),
            "quality_score": self._calculate_project_quality(projects),
            "rating": self._rate_projects(len(projects))
        }
    
    def _calculate_project_quality(self, projects: List[Dict]) -> int:
        """Proje kalite skoru (0-100)."""
        if not projects:
            return 0
        
        total_score = 0
        for proj in projects:
            score = 0
            if proj.get("name"): score += 20
            if proj.get("description"): score += 30
            if proj.get("technologies"): score += 30
            if proj.get("url") or proj.get("github"): score += 20
            total_score += score
        
        return int(total_score / len(projects))
    
    def _rate_projects(self, count: int) -> str:
        """Proje sayısı puanlaması."""
        if count >= 5:
            return "excellent"
        elif count >= 3:
            return "good"
        elif count >= 1:
            return "average"
        else:
            return "none"
    
    def _analyze_skills(self, cv_data: Dict) -> Dict:
        """Beceri analizi."""
        skills = cv_data.get("skills", [])
        
        return {
            "count": len(skills),
            "exists": len(skills) > 0,
            "list": skills,
            "rating": self._rate_skills(len(skills))
        }
    
    def _rate_skills(self, count: int) -> str:
        """Beceri sayısı puanlaması."""
        if count >= 10:
            return "excellent"
        elif count >= 5:
            return "good"
        elif count >= 1:
            return "average"
        else:
            return "none"
    
    def _analyze_certifications(self, cv_data: Dict) -> Dict:
        """Sertifika analizi."""
        certs = cv_data.get("certifications", [])
        
        # Liste mi dict mi kontrol et
        if isinstance(certs, dict):
            certs = list(certs.values()) if certs else []
        
        return {
            "count": len(certs) if certs else 0,
            "exists": bool(certs and len(certs) > 0),
            "list": certs if isinstance(certs, list) else [],
            "rating": "good" if certs and len(certs) > 0 else "none"
        }
    
    def _analyze_languages(self, cv_data: Dict) -> Dict:
        """Dil bilgisi analizi."""
        languages = cv_data.get("languages", {})
        
        # Dict veya list olabilir
        if isinstance(languages, list):
            languages = {lang: "unknown" for lang in languages}
        elif not isinstance(languages, dict):
            languages = {}
        
        analyzed_languages = []
        has_english = False
        english_level = None
        
        for lang, level in languages.items():
            lang_lower = lang.lower()
            level_str = str(level).lower() if level else ""
            
            # Seviye belirle
            cefr_level = self._determine_language_level(level_str)
            
            analyzed_languages.append({
                "language": lang,
                "level_raw": level,
                "level_cefr": cefr_level
            })
            
            # İngilizce kontrolü
            if "ingilizce" in lang_lower or "english" in lang_lower:
                has_english = True
                english_level = cefr_level
        
        return {
            "count": len(languages),
            "exists": len(languages) > 0,
            "list": analyzed_languages,
            "has_english": has_english,
            "english_level": english_level,
            "rating": self._rate_languages(len(languages), has_english, english_level)
        }
    
    def _determine_language_level(self, level: str) -> str:
        """Dil seviyesini CEFR formatına çevir."""
        level = level.lower()
        
        for cefr, keywords in self.LANGUAGE_LEVELS.items():
            if any(kw in level for kw in keywords):
                return cefr
        
        return "unknown"
    
    def _rate_languages(self, count: int, has_english: bool, english_level: Optional[str]) -> str:
        """Dil bilgisi puanlaması."""
        if has_english and english_level in ["native", "c2", "c1"]:
            return "excellent"
        elif has_english and english_level in ["b2", "b1"]:
            return "good"
        elif has_english:
            return "average"
        elif count > 0:
            return "average"
        else:
            return "none"
    
    def _analyze_summary(self, cv_data: Dict) -> Dict:
        """Özet/Hakkımda analizi."""
        summary = cv_data.get("summary", "")
        
        if not summary:
            return {
                "exists": False,
                "word_count": 0,
                "character_count": 0,
                "rating": "none"
            }
        
        words = len(summary.split())
        chars = len(summary)
        
        # İdeal özet: 50-150 kelime
        rating = "none"
        if words >= 50 and words <= 200:
            rating = "excellent"
        elif words >= 30:
            rating = "good"
        elif words >= 10:
            rating = "average"
        
        return {
            "exists": True,
            "word_count": words,
            "character_count": chars,
            "rating": rating
        }
    
    def _analyze_volunteer(self, cv_data: Dict) -> Dict:
        """
        Gönüllü çalışma / topluluk / kulüp analizi.
        
        CV'deki gönüllü çalışmalar, topluluk üyelikleri ve liderlik rollerini
        analiz eder. Öğrenci ve yeni mezunlar için bonus puan sağlar.
        """
        volunteer_data = []
        leadership_roles = 0
        total_roles = 0
        
        # 1. Experience içinde gönüllü işleri ara
        experiences = cv_data.get("experience", []) or []
        volunteer_keywords = ["gönüllü", "volunteer", "topluluk", "kulüp", "club", 
                             "öğrenci", "community", "sosyal sorumluluk", "dernek",
                             "organizasyon", "etkinlik", "koordinatör"]
        leadership_keywords = ["başkan", "yönetim", "kurulu", "lider", "koordinatör", 
                              "sorumlu", "president", "leader", "head", "manager",
                              "denetim", "sponsorluk", "yönetici"]
        
        for exp in experiences:
            if not isinstance(exp, dict):
                continue
            
            title = str(exp.get("title", "")).lower()
            company = str(exp.get("company", "")).lower()
            desc = str(exp.get("description", "")).lower()
            combined = f"{title} {company} {desc}"
            
            # Gönüllü iş mi kontrol et
            is_volunteer = any(kw in combined for kw in volunteer_keywords)
            if is_volunteer:
                total_roles += 1
                is_leadership = any(kw in combined for kw in leadership_keywords)
                if is_leadership:
                    leadership_roles += 1
                
                volunteer_data.append({
                    "title": exp.get("title", ""),
                    "organization": exp.get("company", ""),
                    "is_leadership": is_leadership
                })
        
        # 2. Özet veya diğer alanlarda topluluk işlerini ara
        summary = str(cv_data.get("summary", "")).lower()
        if any(kw in summary for kw in volunteer_keywords) and total_roles == 0:
            total_roles += 1  # En az 1 rol var gibi say
        
        # Bonus puan hesapla
        # Öğrenci/Yeni Mezun için: her rol +3, liderlik +5
        # Junior+ için: her rol +2, liderlik +3
        bonus_student = min(15, (total_roles * 3) + (leadership_roles * 5))
        bonus_experienced = min(10, (total_roles * 2) + (leadership_roles * 3))
        
        return {
            "exists": total_roles > 0,
            "total_roles": total_roles,
            "leadership_roles": leadership_roles,
            "details": volunteer_data,
            "has_leadership": leadership_roles > 0,
            "bonus_student": bonus_student,  # Öğrenci/Yeni Mezun için
            "bonus_experienced": bonus_experienced,  # Junior+ için
            "rating": "excellent" if leadership_roles >= 2 else (
                "good" if total_roles >= 2 or leadership_roles >= 1 else (
                    "average" if total_roles >= 1 else "none"
                )
            )
        }
    
    def _calculate_overall_metrics(self, cv_data: Dict) -> Dict:
        """Genel CV metrikleri."""
        sections_filled = 0
        total_sections = 7  # summary, education, experience, projects, skills, certs, languages
        
        if cv_data.get("summary"): sections_filled += 1
        if cv_data.get("education"): sections_filled += 1
        if cv_data.get("experience"): sections_filled += 1
        if cv_data.get("projects"): sections_filled += 1
        if cv_data.get("skills"): sections_filled += 1
        if cv_data.get("certifications"): sections_filled += 1
        if cv_data.get("languages"): sections_filled += 1
        
        completeness = int((sections_filled / total_sections) * 100)
        
        return {
            "sections_filled": sections_filled,
            "total_sections": total_sections,
            "completeness_percentage": completeness,
            "completeness_rating": "excellent" if completeness >= 80 else "good" if completeness >= 60 else "average" if completeness >= 40 else "poor"
        }
    
    def generate_llm_context(self, metrics: Dict, expectations: Dict) -> str:
        """
        LLM için yapılandırılmış bağlam metni oluştur.
        
        Bu metin, LLM'e kesin veriler sunarak tutarlı puanlama yapmasını sağlar.
        """
        
        edu = metrics.get("education", {})
        exp = metrics.get("experience", {})
        proj = metrics.get("projects", {})
        skills = metrics.get("skills", {})
        certs = metrics.get("certifications", {})
        langs = metrics.get("languages", {})
        summary = metrics.get("summary", {})
        
        context = f"""
=== CV METRİKLERİ (DOĞRULANMIŞ VERİLER) ===

📊 EĞİTİM:
- GPA/AGNO: {"✓ " + str(edu.get('gpa_value')) + " (" + str(edu.get('gpa_rating', 'N/A')) + ")" if edu.get('gpa_exists') else "✗ BELİRTİLMEMİŞ"}
- Derece: {edu.get('highest_degree', 'Belirtilmemiş')}
- Öğrenci mi: {"Evet, devam ediyor" if edu.get('is_student') else "Hayır, mezun"}

💼 DENEYİM:
- Toplam Süre: {exp.get('total_months', 0)} ay ({exp.get('total_years', 0)} yıl)
- Deneyim Sayısı: {exp.get('count', 0)}
- Staj Var mı: {"✓ Evet" if exp.get('has_internship') else "✗ Hayır"}
- Tam Zamanlı: {"✓ Evet" if exp.get('has_fulltime') else "✗ Hayır"}
- Kategori: {exp.get('years_category', 'none')}

🚀 PROJELER:
- Proje Sayısı: {proj.get('count', 0)} (Beklenen: min {expectations.get('min_projects', 0)})
- Teknoloji Çeşitliliği: {proj.get('technology_count', 0)} farklı teknoloji
- Kalite Skoru: {proj.get('quality_score', 0)}/100

🛠️ BECERİLER:
- Beceri Sayısı: {skills.get('count', 0)}
- Durum: {"✓ Yeterli" if skills.get('count', 0) >= 5 else "✗ Yetersiz"}

📜 SERTİFİKALAR:
- Sertifika Var mı: {"✓ Evet (" + str(certs.get('count', 0)) + " adet)" if certs.get('exists') else "✗ HAYIR"}
- Beklenti: {"Gerekli" if expectations.get('certifications_required') else "Opsiyonel"}

🌍 DİLLER:
- Dil Sayısı: {langs.get('count', 0)}
- İngilizce: {"✓ " + str(langs.get('english_level', 'var')) if langs.get('has_english') else "✗ Belirtilmemiş"}

📝 ÖZET/HAKKIMDA:
- Var mı: {"✓ Evet (" + str(summary.get('word_count', 0)) + " kelime)" if summary.get('exists') else "✗ HAYIR"}

=== PUANLAMA KURALLARI ===
1. Yukarıdaki "✗" işaretli alanlar için MAX 40 puan ver
2. "BELİRTİLMEMİŞ" alanlar için MAX 50 puan ver
3. Beklentiler karşılanmıyorsa (kırmızı) kategori puanını düşür
4. Sayısal verileri baz al, tahmin yapma
"""
        
        return context


# Singleton instance
cv_pre_analysis = CVPreAnalysis()

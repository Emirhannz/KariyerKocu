"""
KariyerKoçu - CV Analiz Servisi
===============================
Bağlamsal CV analizi yapan servis.

Ana özellik: Aynı CV farklı profiller için farklı puanlanır!
- 4. sınıf öğrenci için 3 proje = MÜKEMMEL
- 5 yıllık mühendis için 3 proje = YETERSİZ
"""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime

from app.services.llm_service import llm_service
from app.services.cv_pre_analysis import cv_pre_analysis
from app.career.career_config import (
    FIELDS,
    EXPERIENCE_LEVELS,
    get_expectations,
    get_scoring_weights,
    get_field_skills
)


class CVAnalysisService:
    """
    CV Analiz Servisi.
    
    Bir CV'yi belirli bir profil bağlamında (sektör, alan, tecrübe)
    analiz eder ve detaylı puanlama yapar.
    """
    
    async def analyze_cv(
        self,
        cv_data: Dict[str, Any],
        sector: str,
        fields: List[str],
        experience_level: str,
        analysis_method: str = "hybrid"
    ) -> Dict[str, Any]:
        """
        CV'yi analiz et.
        
        Args:
            cv_data: Parse edilmiş CV verisi (JSON)
            sector: Sektör ID
            fields: Alan ID listesi (max 3)
            experience_level: Tecrübe seviyesi ID
            analysis_method: Analiz yöntemi:
                - "pure_llm": Sadece LLM (pre-analysis/post-validation yok)
                - "pre_llm": Pre-analysis + LLM (post-validation yok)
                - "hybrid": Pre-analysis + LLM + Post-validation (mevcut sistem)
                - "rule_based": Python kuralları ağırlıklı (LLM minimal)
            
        Returns:
            Detaylı analiz sonucu
        """
        
        # Her alan için ayrı analiz yap
        field_analyses = []
        
        for field_id in fields:
            analysis = await self._analyze_for_field(
                cv_data=cv_data,
                field_id=field_id,
                experience_level=experience_level,
                analysis_method=analysis_method
            )
            field_analyses.append(analysis)
            
            # Rate limit önlemek için bekle
            import asyncio
            await asyncio.sleep(2)
        
        # En güçlü alanı bul
        strongest = max(field_analyses, key=lambda x: x["overall_score"])
        
        # Genel aksiyon öğeleri oluştur
        action_items = self._generate_action_items(field_analyses)
        
        return {
            "cv_id": cv_data.get("id", "unknown"),
            "analysis_date": datetime.utcnow().isoformat(),
            "profile_context": {
                "sector": sector,
                "fields": fields,
                "experience_level": experience_level,
                "experience_name": EXPERIENCE_LEVELS.get(experience_level, {}).get("name", "Bilinmiyor")
            },
            "field_analyses": field_analyses,
            "strongest_field": strongest["field_id"],
            "action_items": action_items
        }
    
    async def _analyze_for_field(
        self,
        cv_data: Dict[str, Any],
        field_id: str,
        experience_level: str,
        analysis_method: str = "hybrid"
    ) -> Dict[str, Any]:
        """
        Tek bir alan için CV analizi yap.
        
        4 Farklı Analiz Yöntemi:
        1. pure_llm: Sadece LLM ile analiz (pre/post işlem yok)
        2. pre_llm: Pre-analysis + LLM (post-validation yok)
        3. hybrid: Pre-analysis + LLM + Post-validation
        4. rule_based: Python kuralları ağırlıklı (LLM sadece açıklama için)
        """
        
        # Beklentileri ve ağırlıkları al
        expectations = get_expectations(experience_level)
        weights = get_scoring_weights(experience_level)
        field_skills = get_field_skills(field_id)
        field_name = FIELDS.get(field_id, {}).get("name", field_id)
        exp_name = EXPERIENCE_LEVELS.get(experience_level, {}).get("name", experience_level)
        
        # Metrikleri her durumda çıkar (karşılaştırma için)
        metrics = cv_pre_analysis.analyze(cv_data)
        
        try:
            if analysis_method == "pure_llm":
                # YÖNTEM 1: Sadece LLM - Pre-analysis ve post-validation YOK
                result = await self._analyze_pure_llm(
                    cv_data, field_name, exp_name, expectations, weights, field_skills
                )
                result["analysis_method"] = "pure_llm"
                result["method_name"] = "Sadece LLM"
                
            elif analysis_method == "pre_llm":
                # YÖNTEM 2: Pre-analysis + LLM + Post-validation
                llm_context = cv_pre_analysis.generate_llm_context(metrics, expectations)
                result = await self._analyze_with_pre_analysis(
                    cv_data, field_name, exp_name, expectations, weights, field_skills, llm_context, metrics
                )
                # Post-validation uygula (tecrübe seviyesine göre)
                result = self._validate_scores(result, metrics, expectations, experience_level)
                result["analysis_method"] = "pre_llm"
                result["method_name"] = "Pre-Analysis + LLM"
                
            elif analysis_method == "hybrid":
                # YÖNTEM 3: Hibrit - Pre-analysis + LLM + Post-validation
                llm_context = cv_pre_analysis.generate_llm_context(metrics, expectations)
                result = await self._analyze_with_pre_analysis(
                    cv_data, field_name, exp_name, expectations, weights, field_skills, llm_context, metrics
                )
                # Post-validation uygula (tecrübe seviyesine göre)
                result = self._validate_scores(result, metrics, expectations, experience_level)
                result["analysis_method"] = "hybrid"
                result["method_name"] = "Hibrit (Pre+LLM+Post)"
                
            elif analysis_method == "rule_based":
                # YÖNTEM 4: Kural tabanlı - Python kuralları ağırlıklı
                result = await self._analyze_rule_based(
                    cv_data, field_name, exp_name, expectations, weights, field_skills, metrics
                )
                result["analysis_method"] = "rule_based"
                result["method_name"] = "Kural Tabanlı"
                
            else:
                # Varsayılan: Hibrit
                llm_context = cv_pre_analysis.generate_llm_context(metrics, expectations)
                result = await self._analyze_with_pre_analysis(
                    cv_data, field_name, exp_name, expectations, weights, field_skills, llm_context, metrics
                )
                result = self._validate_scores(result, metrics, expectations, experience_level)
                result["analysis_method"] = "hybrid"
                result["method_name"] = "Hibrit (Pre+LLM+Post)"
            
            result["field_id"] = field_id
            result["field_name"] = field_name
            result["metrics"] = metrics
            
            # Beceri eşleştirmesi
            cv_skills = [s.lower() for s in cv_data.get("skills", [])]
            result["matching_skills"] = [
                s for s in field_skills["key_skills"]
                if s.lower() in cv_skills or any(s.lower() in skill for skill in cv_skills)
            ]
            result["missing_skills"] = [
                s for s in field_skills["key_skills"]
                if s.lower() not in cv_skills and not any(s.lower() in skill for skill in cv_skills)
            ][:5]
            
            return result
            
        except Exception as e:
            # İlk hata - 1 kez daha dene
            print(f"⚠️ Analiz hatası ({field_name}): {str(e)[:100]}. Tekrar deneniyor...")
            import asyncio
            await asyncio.sleep(1)
            
            try:
                # Retry: Pre-analysis + LLM + Post-validation
                llm_context = cv_pre_analysis.generate_llm_context(metrics, expectations)
                result = await self._analyze_with_pre_analysis(
                    cv_data, field_name, exp_name, expectations, weights, field_skills, llm_context, metrics
                )
                result = self._validate_scores(result, metrics, expectations, experience_level)
                result["analysis_method"] = "pre_llm"
                result["method_name"] = "Pre-Analysis + LLM (Retry)"
                result["field_id"] = field_id
                result["field_name"] = field_name
                result["metrics"] = metrics
                
                cv_skills = [s.lower() for s in cv_data.get("skills", [])]
                result["matching_skills"] = [
                    s for s in field_skills["key_skills"]
                    if s.lower() in cv_skills or any(s.lower() in skill for skill in cv_skills)
                ]
                result["missing_skills"] = [
                    s for s in field_skills["key_skills"]
                    if s.lower() not in cv_skills and not any(s.lower() in skill for skill in cv_skills)
                ][:5]
                
                print(f"✅ Retry başarılı ({field_name}): {result.get('overall_score', 0)} puan")
                return result
                
            except Exception as e2:
                # Retry de başarısız - Rule Based analize geç
                print(f"❌ Retry de başarısız ({field_name}): {str(e2)[:100]}")
                print(f"⚠️ Falling back to Rule-Based analysis for {field_name}...")
                
                fallback_result = await self._analyze_rule_based(
                    cv_data, field_name, exp_name, expectations, weights, field_skills, metrics
                )
                
                fallback_result["analysis_method"] = "rule_based_fallback"
                fallback_result["method_name"] = "Kural Tabanlı (Fallback)"
                fallback_result["field_id"] = field_id
                fallback_result["field_name"] = field_name
                fallback_result["metrics"] = metrics
                
                # Becerileri ekle
                cv_skills = [s.lower() for s in cv_data.get("skills", [])]
                fallback_result["matching_skills"] = [
                    s for s in field_skills["key_skills"]
                    if s.lower() in cv_skills or any(s.lower() in skill for skill in cv_skills)
                ]
                fallback_result["missing_skills"] = [
                    s for s in field_skills["key_skills"]
                    if s.lower() not in cv_skills and not any(s.lower() in skill for skill in cv_skills)
                ][:5]
                
                return fallback_result
    
    async def _analyze_pure_llm(
        self,
        cv_data: Dict[str, Any],
        field_name: str,
        exp_name: str,
        expectations: Dict,
        weights: Dict,
        field_skills: Dict
    ) -> Dict[str, Any]:
        """YÖNTEM 1: Sadece LLM ile analiz - Hiç pre-analysis/post-validation yok."""
        
        # Basit system prompt - metrik bilgisi YOK
        system_prompt = f"""Sen deneyimli bir İK uzmanısın ve {field_name} alanında işe alım yapıyorsun.
Önündeki CV bir {exp_name} adayına ait.

BEKLENTİLER ({exp_name} için):
- Minimum proje sayısı: {expectations.get('min_projects', 3)}
- GPA önemli mi: {'Evet' if expectations.get('gpa_important') else 'Hayır'}
- Sertifika bekleniyor mu: {'Evet' if expectations.get('certifications_required') else 'Hayır'}
- İş deneyimi şart mı: {'Evet' if expectations.get('experience_required') else 'Hayır'}

{field_name} İÇİN ARANAN BECERİLER:
- Olmazsa olmaz: {', '.join(field_skills['key_skills'][:8])}
- Artı puan: {', '.join(field_skills['nice_to_have'][:5])}

PUANLAMA AĞIRLIKLARI:
- Özet: %{weights['summary']}, Eğitim: %{weights['education']}, Deneyim: %{weights['experience']}
- Projeler: %{weights['projects']}, Beceriler: %{weights['skills']}, Sertifikalar: %{weights['certifications']}, Diller: %{weights['languages']}

CEVAP FORMATINI AYNEN UYGULA (sadece JSON döndür):
{{
    "overall_score": 75,
    "category_scores": {{
        "summary": {{"score": 80, "weight": {weights['summary']}, "reason": "açıklama", "suggestions": ["öneri1"]}},
        "education": {{"score": 70, "weight": {weights['education']}, "reason": "açıklama", "suggestions": ["öneri1"]}},
        "experience": {{"score": 85, "weight": {weights['experience']}, "reason": "açıklama", "suggestions": ["öneri1"]}},
        "projects": {{"score": 75, "weight": {weights['projects']}, "reason": "açıklama", "suggestions": ["öneri1"]}},
        "skills": {{"score": 70, "weight": {weights['skills']}, "reason": "açıklama", "suggestions": ["öneri1"]}},
        "certifications": {{"score": 40, "weight": {weights['certifications']}, "reason": "açıklama", "suggestions": ["öneri1"]}},
        "languages": {{"score": 80, "weight": {weights['languages']}, "reason": "açıklama", "suggestions": ["öneri1"]}}
    }},
    "strengths": ["güçlü yön 1", "güçlü yön 2", "güçlü yön 3"],
    "weaknesses": ["zayıf yön 1", "zayıf yön 2"]
}}

SADECE JSON DÖNDÜR, AÇIKLAMA YAPMA!"""

        user_message = self._build_user_message(cv_data)
        
        response = await llm_service.chat(
            message=user_message,
            system_prompt=system_prompt,
            temperature=0.3,
            max_tokens=3500  # Artırıldı
        )
        
        return self._parse_analysis_response(response)
    
    async def _analyze_with_pre_analysis(
        self,
        cv_data: Dict[str, Any],
        field_name: str,
        exp_name: str,
        expectations: Dict,
        weights: Dict,
        field_skills: Dict,
        llm_context: str,
        metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """YÖNTEM 2 ve 3: Pre-analysis ile zenginleştirilmiş LLM analizi."""
        
        system_prompt = self._build_system_prompt(
            field_name=field_name,
            exp_name=exp_name,
            expectations=expectations,
            weights=weights,
            field_skills=field_skills,
            llm_context=llm_context
        )
        
        user_message = self._build_user_message(cv_data, metrics)
        
        response = await llm_service.chat(
            message=user_message,
            system_prompt=system_prompt,
            temperature=0.2,
            max_tokens=3500  # Artırıldı
        )
        
        return self._parse_analysis_response(response)
    
    async def _analyze_rule_based(
        self,
        cv_data: Dict[str, Any],
        field_name: str,
        exp_name: str,
        expectations: Dict,
        weights: Dict,
        field_skills: Dict,
        metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """YÖNTEM 4: Kural tabanlı puanlama - Python kuralları ağırlıklı."""
        
        category_scores = {}
        
        # ÖZET PUANI
        summary_metrics = metrics.get("summary", {})
        if summary_metrics.get("exists"):
            word_count = summary_metrics.get("word_count", 0)
            if word_count >= 50:
                summary_score = 85
            elif word_count >= 30:
                summary_score = 70
            elif word_count >= 15:
                summary_score = 55
            else:
                summary_score = 40
        else:
            summary_score = 20
        category_scores["summary"] = {
            "score": summary_score,
            "weight": weights["summary"],
            "reason": f"Özet {'mevcut' if summary_metrics.get('exists') else 'yok'}, {summary_metrics.get('word_count', 0)} kelime",
            "suggestions": [] if summary_score > 60 else ["Kendinizi tanıtan profesyonel bir özet ekleyin"]
        }
        
        # EĞİTİM PUANI
        edu_metrics = metrics.get("education", {})
        gpa = edu_metrics.get("gpa_normalized", 0) or 0  # gpa_normalized kullan
        gpa_exists = edu_metrics.get("gpa_exists", False)
        
        if gpa >= 3.5:
            edu_score = 90
        elif gpa >= 3.0:
            edu_score = 75
        elif gpa >= 2.5:
            edu_score = 60
        elif gpa > 0:
            edu_score = 50
        else:
            # GPA belirtilmemiş
            if not expectations.get("gpa_important"):
                edu_score = 60  # GPA önemli değilse orta puan
            else:
                edu_score = 40
        category_scores["education"] = {
            "score": edu_score,
            "weight": weights["education"],
            "reason": f"GPA: {gpa if gpa > 0 else 'Belirtilmemiş'}",
            "suggestions": [] if edu_score > 60 else ["GPA bilgisi ekleyebilirsiniz"]
        }
        
        # DENEYİM PUANI
        exp_metrics = metrics.get("experience", {})
        total_months = exp_metrics.get("total_months", 0)
        if expectations.get("experience_required"):
            if total_months >= 24:
                exp_score = 90
            elif total_months >= 12:
                exp_score = 75
            elif total_months >= 6:
                exp_score = 60
            elif total_months > 0:
                exp_score = 45
            else:
                exp_score = 25
        else:
            # Deneyim şart değil
            if total_months > 0:
                exp_score = 80
            else:
                exp_score = 50  # Proje/staj yeterli
        category_scores["experience"] = {
            "score": exp_score,
            "weight": weights["experience"],
            "reason": f"Toplam {total_months} ay deneyim",
            "suggestions": [] if exp_score > 60 else ["Daha fazla iş deneyimi edinebilirsiniz"]
        }
        
        # PROJE PUANI
        proj_metrics = metrics.get("projects", {})
        proj_count = proj_metrics.get("count", 0)
        min_projects = expectations.get("min_projects", 3)
        if proj_count >= min_projects + 2:
            proj_score = 95
        elif proj_count >= min_projects:
            proj_score = 80
        elif proj_count >= min_projects - 1:
            proj_score = 65
        elif proj_count > 0:
            proj_score = 50
        else:
            proj_score = 20
        category_scores["projects"] = {
            "score": proj_score,
            "weight": weights["projects"],
            "reason": f"{proj_count} proje (beklenen: {min_projects}+)",
            "suggestions": [] if proj_score > 60 else [f"En az {min_projects} proje eklemeniz önerilir"]
        }
        
        # BECERİ PUANI
        cv_skills = [s.lower() for s in cv_data.get("skills", [])]
        key_skills = field_skills.get("key_skills", [])
        matching_count = sum(1 for s in key_skills if s.lower() in cv_skills or any(s.lower() in skill for skill in cv_skills))
        skill_ratio = matching_count / len(key_skills) if key_skills else 0
        skill_score = min(95, int(40 + skill_ratio * 55))
        category_scores["skills"] = {
            "score": skill_score,
            "weight": weights["skills"],
            "reason": f"{matching_count}/{len(key_skills)} anahtar beceri eşleşti",
            "suggestions": [] if skill_score > 60 else ["Aranan becerileri geliştirmeye çalışın"]
        }
        
        # SERTİFİKA PUANI
        cert_metrics = metrics.get("certifications", {})
        cert_count = cert_metrics.get("count", 0)
        if expectations.get("certifications_required"):
            if cert_count >= 2:
                cert_score = 90
            elif cert_count == 1:
                cert_score = 70
            else:
                cert_score = 30
        else:
            if cert_count > 0:
                cert_score = 85
            else:
                cert_score = 50
        category_scores["certifications"] = {
            "score": cert_score,
            "weight": weights["certifications"],
            "reason": f"{cert_count} sertifika",
            "suggestions": [] if cert_score > 60 else ["Alakalı sertifikalar edinebilirsiniz"]
        }
        
        # DİL PUANI - english_level CEFR string (a1, a2, b1, b2, c1, c2, native)
        lang_metrics = metrics.get("languages", {})
        eng_level_str = lang_metrics.get("english_level", "") or ""
        
        # CEFR string'i sayısal değere çevir
        cefr_to_num = {"native": 6, "c2": 5, "c1": 4, "b2": 3, "b1": 2, "a2": 1, "a1": 0, "unknown": 0}
        eng_level_num = cefr_to_num.get(str(eng_level_str).lower(), 0)
        
        if eng_level_num >= 4:  # c1 veya üstü
            lang_score = 90
        elif eng_level_num >= 3:  # b2
            lang_score = 75
        elif eng_level_num >= 2:  # b1
            lang_score = 60
        elif lang_metrics.get("has_english"):
            lang_score = 50
        else:
            lang_score = 35
        category_scores["languages"] = {
            "score": lang_score,
            "weight": weights["languages"],
            "reason": f"İngilizce: {eng_level_str.upper() if eng_level_str else 'Belirtilmemiş'}",
            "suggestions": [] if lang_score > 60 else ["İngilizce seviyenizi geliştirebilirsiniz"]
        }
        
        # GENEL PUAN HESAPLA
        total_weighted = sum(cat["score"] * cat["weight"] for cat in category_scores.values())
        total_weight = sum(cat["weight"] for cat in category_scores.values())
        overall_score = int(total_weighted / total_weight) if total_weight > 0 else 50
        
        # Güçlü ve zayıf yönleri belirle
        sorted_cats = sorted(category_scores.items(), key=lambda x: x[1]["score"], reverse=True)
        strengths = [f"{k.capitalize()}: {v['reason']}" for k, v in sorted_cats[:3] if v["score"] >= 60]
        weaknesses = [f"{k.capitalize()}: {v['reason']}" for k, v in sorted_cats if v["score"] < 60][:3]
        
        return {
            "overall_score": overall_score,
            "category_scores": category_scores,
            "strengths": strengths if strengths else ["CV değerlendirildi"],
            "weaknesses": weaknesses if weaknesses else ["Geliştirme alanı tespit edilmedi"]
        }
    
    def _build_system_prompt(
        self,
        field_name: str,
        exp_name: str,
        expectations: Dict,
        weights: Dict,
        field_skills: Dict,
        llm_context: str = ""
    ) -> str:
        """Bağlamsal system prompt oluştur - Pre-analysis metrikleriyle zenginleştirilmiş."""
        
        # Sertifika beklentisi kontrolü
        cert_required = expectations.get('certifications_required', False)
        cert_note = "Sertifika yokluğu düşük puan sebebi DEĞİLDİR. Projeler ve beceriler daha önemli." if not cert_required else "Sertifikalar bu seviye için önemlidir."
        
        return f"""Sen deneyimli bir İK uzmanısın ve {field_name} alanında işe alım yapıyorsun.
Önündeki CV bir {exp_name} adayına ait.

{llm_context}

BEKLENTİLERİN ({exp_name} için):
- Minimum proje sayısı: {expectations.get('min_projects', 3)}
- Alan ile ilgili minimum proje: {expectations.get('min_field_projects', 1)}
- GPA önemli mi: {'Evet' if expectations.get('gpa_important') else 'Hayır, tecrübe daha önemli'}
- Sertifika bekleniyor mu: {'Evet, bu seviye için şart' if cert_required else 'HAYIR! Öğrenci/yeni mezun için sertifika beklenmiyor'}
- İş deneyimi şart mı: {'Evet' if expectations.get('experience_required') else 'Hayır, staj/proje yeterli'}

{field_name} İÇİN ARANAN BECERİLER:
- Olmazsa olmaz: {', '.join(field_skills['key_skills'][:8])}
- Artı puan: {', '.join(field_skills['nice_to_have'][:5])}

PUANLAMA AĞIRLIKLARI:
- Özet/Hakkında: %{weights['summary']}
- Eğitim: %{weights['education']}
- Deneyim: %{weights['experience']}
- Projeler: %{weights['projects']} ← ÖĞRENCİ/YENİ MEZUN İÇİN EN ÖNEMLİ
- Beceriler: %{weights['skills']} ← ALAN BECERİ EŞLEŞMESİ ÇOK ÖNEMLİ
- Sertifikalar: %{weights['certifications']}
- Diller: %{weights['languages']}

ÖNEMLİ KURALLAR:
1. Yukarıdaki metriklerde "✗" işaretli alanlar için MAX 40 puan ver
2. "BELİRTİLMEMİŞ" alanlar için MAX 50 puan ver
3. Sayısal verileri baz al, tahmin yapma
4. Bu bir {exp_name} adayı! Puanları bu bağlamda ver.

SERTİFİKA PUANLAMA KURALI ({exp_name} için):
- {cert_note}
- Sertifika yoksa ve öğrenci/yeni mezunsa: 60-70 puan ver (düşük tutma!)
- Sertifika varsa: 80-100 puan ver
- Sertifika yokluğu geliştirmeli alan olarak belirt ama puanı düşürme

PROJE KALİTESİ DEĞERLENDİRME:
- Alana ÖZGÜ projeler (ör: {field_name} için): +20 puan bonus
- Gerçek dünya uygulamaları: +10 puan
- Teknik derinlik (API, deployment, test): +10 puan
- Proje sayısı değil KALİTESİ önemli!

BECERİ EŞLEŞMESİ:
- "Olmazsa olmaz" becerilerden kaç tanesi var? Bu çok önemli!
- 6+ eşleşme: 90+ puan
- 4-5 eşleşme: 75-89 puan
- 2-3 eşleşme: 60-74 puan

CEVAP FORMATINI AYNEN UYGULA (sadece JSON döndür):
{{
    "overall_score": 75,
    "category_scores": {{
        "summary": {{"score": 80, "weight": {weights['summary']}, "reason": "açıklama", "suggestions": ["öneri1"]}},
        "education": {{"score": 70, "weight": {weights['education']}, "reason": "açıklama", "suggestions": ["öneri1"]}},
        "experience": {{"score": 85, "weight": {weights['experience']}, "reason": "açıklama", "suggestions": ["öneri1"]}},
        "projects": {{"score": 75, "weight": {weights['projects']}, "reason": "açıklama", "suggestions": ["öneri1"]}},
        "skills": {{"score": 70, "weight": {weights['skills']}, "reason": "açıklama", "suggestions": ["öneri1"]}},
        "certifications": {{"score": 65, "weight": {weights['certifications']}, "reason": "açıklama", "suggestions": ["öneri1"]}},
        "languages": {{"score": 80, "weight": {weights['languages']}, "reason": "açıklama", "suggestions": ["öneri1"]}}
    }},
    "strengths": ["güçlü yön 1", "güçlü yön 2", "güçlü yön 3"],
    "weaknesses": ["zayıf yön 1", "zayıf yön 2"]
}}

SADECE JSON DÖNDÜR, AÇIKLAMA YAPMA!"""

    def _build_user_message(self, cv_data: Dict[str, Any], metrics: Dict[str, Any] = None) -> str:
        """CV verisinden user message oluştur - metriklerle zenginleştirilmiş."""
        
        # CV verisini okunabilir formata çevir
        cv_text = f"""
İSİM: {cv_data.get('full_name', 'Belirtilmemiş')}
UNVAN: {cv_data.get('title', 'Belirtilmemiş')}
EMAIL: {cv_data.get('email', 'Belirtilmemiş')}

ÖZET/HAKKIMDA:
{cv_data.get('summary', 'Belirtilmemiş')}

BECERİLER:
{', '.join(cv_data.get('skills', [])) or 'Belirtilmemiş'}

DENEYİM:
"""
        for exp in cv_data.get('experience', []):
            cv_text += f"- {exp.get('title', '')} @ {exp.get('company', '')} ({exp.get('duration', '')})\n"
            if exp.get('description'):
                cv_text += f"  {exp.get('description', '')[:200]}\n"
        
        if not cv_data.get('experience'):
            cv_text += "Belirtilmemiş\n"
        
        cv_text += "\nPROJELER:\n"
        for proj in cv_data.get('projects', []):
            cv_text += f"- {proj.get('name', '')}: {', '.join(proj.get('technologies', []))}\n"
            if proj.get('description'):
                cv_text += f"  {proj.get('description', '')[:150]}\n"
        
        if not cv_data.get('projects'):
            cv_text += "Belirtilmemiş\n"
        
        cv_text += "\nEĞİTİM:\n"
        for edu in cv_data.get('education', []):
            gpa_str = ""
            if edu.get('gpa'):
                gpa_str = f" (GPA: {edu.get('gpa')})"
            cv_text += f"- {edu.get('degree', '')} - {edu.get('field', '')} @ {edu.get('school', '')}{gpa_str}\n"
        
        cv_text += f"\nDİLLER: {cv_data.get('languages', {})}\n"
        cv_text += f"SERTİFİKALAR: {cv_data.get('certifications', [])}\n"
        
        return f"Bu CV'yi analiz et ve JSON formatında puanla:\n\n{cv_text}"
    
    def _parse_analysis_response(self, response: str) -> Dict[str, Any]:
        """LLM yanıtını parse et - Regex ile güçlendirilmiş."""
        import regex as re  # regex kütüphanesi yoksa re kullanacağız ama re daha iyidir
        import re
        
        cleaned = response.strip()
        
        # 1. Markdown code block temizle
        if "```json" in cleaned:
            cleaned = cleaned.split("```json")[1].split("```")[0]
        elif "```" in cleaned:
            cleaned = cleaned.split("```")[1].split("```")[0]
            
        # 2. JSON bulmaya çalış (regex ile en dıştaki süslü parantezleri bul)
        try:
            # En geniş { ... } bloğunu bul
            json_match = re.search(r'\{.*\}', cleaned, re.DOTALL)
            if json_match:
                cleaned = json_match.group(0)
        except:
            pass
        
        try:
            result = json.loads(cleaned.strip())
            
            # Zorunlu alanları kontrol et
            if "overall_score" not in result:
                result["overall_score"] = 50
            if "category_scores" not in result:
                result["category_scores"] = {}
            if "strengths" not in result:
                result["strengths"] = []
            if "weaknesses" not in result:
                result["weaknesses"] = []
            
            # Her kategori için weight alanını kontrol et ve ekle
            default_weights = {
                "summary": 10,
                "education": 15,
                "experience": 25,
                "projects": 20,
                "skills": 15,
                "certifications": 10,
                "languages": 5
            }
            
            for cat_name, cat_data in result.get("category_scores", {}).items():
                if isinstance(cat_data, dict):
                    # weight yoksa varsayılan ekle
                    if "weight" not in cat_data:
                        cat_data["weight"] = default_weights.get(cat_name, 10)
                    # score yoksa varsayılan ekle
                    if "score" not in cat_data:
                        cat_data["score"] = 50
                    # reason yoksa varsayılan ekle
                    if "reason" not in cat_data:
                        cat_data["reason"] = "Değerlendirme yapıldı"
                    # suggestions yoksa boş liste ekle
                    if "suggestions" not in cat_data:
                        cat_data["suggestions"] = []
                
            return result
            
        except json.JSONDecodeError as e:
            # KRİTİK: Exception fırlat ki dışarıdaki retry mekanizması çalışsın!
            print(f"JSON Parse Error: {str(e)}")
            print(f"Raw Response: {response[:200]}...")
            raise ValueError(f"Analiz sonucu geçerli bir JSON formatında değil: {str(e)}")
    
    def _generate_action_items(self, field_analyses: List[Dict]) -> List[str]:
        """Tüm analizlerden öncelikli aksiyon öğeleri çıkar."""
        
        all_suggestions = []
        
        for analysis in field_analyses:
            for cat_name, cat_data in analysis.get("category_scores", {}).items():
                if isinstance(cat_data, dict):
                    score = cat_data.get("score", 100)
                    suggestions = cat_data.get("suggestions", [])
                    
                    # Düşük puanlı kategorilerin önerilerini öncelikle ekle
                    if score < 60:
                        all_suggestions.extend([(s, score) for s in suggestions])
        
        # Skora göre sırala (düşük skor = yüksek öncelik)
        all_suggestions.sort(key=lambda x: x[1])
        
        # Benzersiz önerileri al (max 5)
        seen = set()
        unique_items = []
        for suggestion, _ in all_suggestions:
            if suggestion not in seen:
                seen.add(suggestion)
                unique_items.append(suggestion)
                if len(unique_items) >= 5:
                    break
        
        return unique_items
    
    def _validate_scores(
        self,
        result: Dict[str, Any],
        metrics: Dict[str, Any],
        expectations: Dict[str, Any],
        experience_level: str = "junior"
    ) -> Dict[str, Any]:
        """
        LLM sonuçlarını tecrübe seviyesine göre kesin kurallara zorla.
        
        Bu fonksiyon, LLM'in verdiği puanları metriklere ve tecrübe seviyesine göre
        belirli aralıklara zorlar, böylece tutarlı sonuçlar elde edilir.
        """
        
        category_scores = result.get("category_scores", {})
        
        # Tecrübe grupları
        student_levels = ["ogrenci_1", "ogrenci_2", "ogrenci_3", "ogrenci_4"]
        new_grad_levels = ["yeni_mezun"]
        junior_levels = ["junior"]
        
        # ==================== ÖZET (SUMMARY) ====================
        summary_metrics = metrics.get("summary", {})
        if "summary" in category_scores:
            word_count = summary_metrics.get("word_count", 0)
            exists = summary_metrics.get("exists", False)
            
            if not exists:
                score_range = (20, 30)
            elif word_count < 20:
                score_range = (40, 50)
            elif word_count < 50:
                score_range = (60, 70)
            elif word_count < 150:
                score_range = (80, 90)
            else:
                score_range = (70, 80)
            
            current = category_scores["summary"].get("score", 50)
            category_scores["summary"]["score"] = max(score_range[0], min(score_range[1], current))
        
        # ==================== EĞİTİM (EDUCATION) ====================
        edu_metrics = metrics.get("education", {})
        if "education" in category_scores:
            gpa = edu_metrics.get("gpa_normalized", 0) or 0
            
            if experience_level in student_levels:
                if gpa >= 3.5: score_range = (90, 100)
                elif gpa >= 3.0: score_range = (80, 90)
                elif gpa >= 2.5: score_range = (65, 80)
                elif gpa > 0: score_range = (50, 65)
                else: score_range = (50, 60)  # GPA yok
            elif experience_level in new_grad_levels:
                if gpa >= 3.5: score_range = (85, 95)
                elif gpa >= 3.0: score_range = (75, 85)
                elif gpa >= 2.5: score_range = (60, 75)
                elif gpa > 0: score_range = (45, 60)
                else: score_range = (40, 50)  # GPA yok
            elif experience_level in junior_levels:
                if gpa >= 3.0: score_range = (60, 70)
                else: score_range = (50, 60)
            else:  # mid+
                score_range = (60, 70)  # GPA mid+ için önemsiz
            
            current = category_scores["education"].get("score", 50)
            category_scores["education"]["score"] = max(score_range[0], min(score_range[1], current))
        
        # ==================== DENEYİM (EXPERIENCE) ====================
        exp_metrics = metrics.get("experience", {})
        if "experience" in category_scores:
            total_months = exp_metrics.get("total_months", 0)
            has_internship = exp_metrics.get("internship_count", 0) > 0
            
            if experience_level in ["ogrenci_1", "ogrenci_2"]:
                if total_months == 0 and not has_internship: score_range = (70, 80)
                else: score_range = (85, 95)
            elif experience_level in ["ogrenci_3", "ogrenci_4"]:
                if total_months == 0 and not has_internship: score_range = (50, 60)
                elif has_internship: score_range = (70, 85)
                else: score_range = (80, 95)
            elif experience_level in new_grad_levels:
                if total_months == 0 and not has_internship: score_range = (30, 40)
                elif has_internship and total_months < 6: score_range = (50, 60)
                elif total_months < 12: score_range = (70, 80)
                else: score_range = (85, 95)
            elif experience_level in junior_levels:
                if total_months < 6: score_range = (20, 40)
                elif total_months < 12: score_range = (50, 60)
                elif total_months < 36: score_range = (70, 80)
                else: score_range = (85, 95)
            else:  # mid+
                if total_months < 36: score_range = (30, 50)
                elif total_months < 60: score_range = (60, 75)
                else: score_range = (80, 90)
            
            current = category_scores["experience"].get("score", 50)
            category_scores["experience"]["score"] = max(score_range[0], min(score_range[1], current))
        
        # ==================== PROJELER (PROJECTS) ====================
        proj_metrics = metrics.get("projects", {})
        if "projects" in category_scores:
            proj_count = proj_metrics.get("count", 0)
            
            if experience_level in student_levels:
                if proj_count == 0: score_range = (30, 40)
                elif proj_count <= 2: score_range = (60, 70)
                elif proj_count <= 4: score_range = (80, 90)
                else: score_range = (90, 100)
            elif experience_level in new_grad_levels:
                if proj_count == 0: score_range = (20, 30)
                elif proj_count <= 2: score_range = (50, 60)
                elif proj_count <= 4: score_range = (75, 85)
                else: score_range = (90, 100)
            else:  # junior+
                if proj_count == 0: score_range = (40, 50)
                elif proj_count <= 2: score_range = (60, 70)
                else: score_range = (75, 90)
            
            current = category_scores["projects"].get("score", 50)
            category_scores["projects"]["score"] = max(score_range[0], min(score_range[1], current))
        
        # ==================== SERTİFİKALAR (CERTIFICATIONS) ====================
        cert_metrics = metrics.get("certifications", {})
        if "certifications" in category_scores:
            cert_count = cert_metrics.get("count", 0)
            
            if experience_level in student_levels:
                if cert_count == 0: score_range = (50, 60)
                elif cert_count <= 2: score_range = (75, 85)
                else: score_range = (90, 100)
            elif experience_level in new_grad_levels:
                if cert_count == 0: score_range = (40, 50)
                elif cert_count <= 2: score_range = (70, 80)
                else: score_range = (85, 95)
            else:  # junior+
                if cert_count == 0: score_range = (50, 65)
                elif cert_count <= 2: score_range = (70, 80)
                else: score_range = (80, 90)
            
            current = category_scores["certifications"].get("score", 50)
            category_scores["certifications"]["score"] = max(score_range[0], min(score_range[1], current))
        
        # ==================== DİLLER (LANGUAGES) ====================
        lang_metrics = metrics.get("languages", {})
        if "languages" in category_scores:
            eng_level = str(lang_metrics.get("english_level", "")).lower()
            has_english = lang_metrics.get("has_english", False)
            
            cefr_map = {"native": 6, "c2": 5, "c1": 4, "b2": 3, "b1": 2, "a2": 1, "a1": 0}
            level_num = cefr_map.get(eng_level, 0)
            
            if not has_english: score_range = (30, 40)
            elif level_num <= 1: score_range = (40, 50)  # A1-A2
            elif level_num == 2: score_range = (55, 65)  # B1
            elif level_num == 3: score_range = (70, 80)  # B2
            elif level_num >= 4: score_range = (85, 95)  # C1+
            else: score_range = (50, 60)
            
            current = category_scores["languages"].get("score", 50)
            category_scores["languages"]["score"] = max(score_range[0], min(score_range[1], current))
        
        # ==================== OVERALL SCORE HESAPLA ====================
        total_weighted = 0
        total_weight = 0
        for cat_name, cat_data in category_scores.items():
            if isinstance(cat_data, dict):
                score = cat_data.get("score", 0)
                weight = cat_data.get("weight", 0)
                total_weighted += score * weight
                total_weight += weight
        
        if total_weight > 0:
            base_score = int(total_weighted / total_weight)
            
            # ========== GÖNÜLLÜ ÇALIŞMA BONUSU EKLE ==========
            volunteer_metrics = metrics.get("volunteer", {})
            if volunteer_metrics.get("exists", False):
                if experience_level in student_levels or experience_level in new_grad_levels:
                    bonus = volunteer_metrics.get("bonus_student", 0)
                else:
                    bonus = volunteer_metrics.get("bonus_experienced", 0)
                
                # Bonusu ekle (max 100'ü geçmesin)
                result["overall_score"] = min(100, base_score + bonus)
                result["volunteer_bonus"] = bonus
            else:
                result["overall_score"] = base_score
                result["volunteer_bonus"] = 0
        
        result["category_scores"] = category_scores
        return result


# Singleton instance
cv_analysis_service = CVAnalysisService()

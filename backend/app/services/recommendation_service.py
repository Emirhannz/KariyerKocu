"""
KariyerKoçu - Tavsiye Servisi
=============================
CV analiz sonuçlarına göre kişiselleştirilmiş kariyer tavsiyeleri üretir.
"""

import json
from typing import Dict, Any, List
from datetime import datetime

from app.services.llm_service import llm_service
from app.career.career_config import EXPERIENCE_LEVELS, FIELDS
from app.career.career_knowledge import (
    KNOWLEDGE_BASE,
    GENERAL_ADVICE,
    get_learning_path,
    get_project_ideas,
    get_certifications,
    get_quick_tips,
    get_required_technologies,
    find_missing_technologies
)


class RecommendationService:
    """
    Tavsiye Servisi.
    
    CV analizi sonuçlarına göre kişiselleştirilmiş kariyer tavsiyeleri üretir.
    """
    
    async def generate_recommendations(
        self,
        sector: str,
        fields: List[str],
        experience_level: str,
        field_analyses: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Tavsiyeler üret.
        
        Args:
            sector: Sektör ID
            fields: Alan ID listesi
            experience_level: Tecrübe seviyesi
            field_analyses: Alan bazlı analiz sonuçları
            
        Returns:
            Kişiselleştirilmiş tavsiyeler
        """
        
        exp_name = EXPERIENCE_LEVELS.get(experience_level, {}).get("name", experience_level)
        
        # Her alan için tavsiye oluştur
        field_recommendations = []
        
        for analysis in field_analyses:
            field_id = analysis.get("field_id")
            if not field_id:
                continue
                
            recommendation = await self._generate_field_recommendations(
                field_id=field_id,
                field_analysis=analysis,
                experience_level=experience_level
            )
            field_recommendations.append(recommendation)
        
        # Öncelikli aksiyonları belirle
        priority_actions = self._determine_priority_actions(field_analyses)
        
        return {
            "created_at": datetime.utcnow().isoformat(),
            "experience_level": experience_level,
            "experience_name": exp_name,
            "field_recommendations": field_recommendations,
            "general_advice": GENERAL_ADVICE,
            "priority_actions": priority_actions
        }
    
    async def _generate_field_recommendations(
        self,
        field_id: str,
        field_analysis: Dict[str, Any],
        experience_level: str
    ) -> Dict[str, Any]:
        """Tek bir alan için tavsiyeler üret."""
        
        field_name = FIELDS.get(field_id, {}).get("name", field_id)
        current_score = field_analysis.get("overall_score", 0)
        missing_skills = field_analysis.get("missing_skills", [])
        weaknesses = field_analysis.get("weaknesses", [])
        category_scores = field_analysis.get("category_scores", {})
        
        # Bilgi bankasından kaynak önerilerini al
        learning_path = get_learning_path(field_id)
        project_ideas = get_project_ideas(field_id)
        certifications = get_certifications(field_id)
        quick_tips = get_quick_tips(field_id)
        
        # Eksik becerilere göre öncelikli öğrenme önerileri
        skill_recommendations = self._match_skills_to_resources(
            missing_skills=missing_skills,
            learning_path=learning_path,
            experience_level=experience_level
        )
        
        # Proje önerileri (düşük puanlı alanlara göre)
        project_suggestions = self._select_relevant_projects(
            project_ideas=project_ideas,
            category_scores=category_scores,
            current_score=current_score
        )
        
        # LLM ile kişiselleştirilmiş tavsiye metni oluştur
        # CV'deki mevcut becerileri al (analiz sonucundaki matching_skills kullan)
        cv_skills = field_analysis.get("matching_skills", [])
        
        # Eğer matching_skills boşsa, metrics'ten skills'i kontrol et
        if not cv_skills:
            metrics = field_analysis.get("metrics", {})
            skills_metrics = metrics.get("skills", {})
            cv_skills = skills_metrics.get("list", [])
        
        personalized_advice = await self._generate_personalized_advice(
            field_id=field_id,
            field_name=field_name,
            experience_level=experience_level,
            current_score=current_score,
            weaknesses=weaknesses,
            missing_skills=missing_skills,
            cv_skills=cv_skills
        )
        
        return {
            "field_id": field_id,
            "field_name": field_name,
            "current_score": current_score,
            "skill_recommendations": skill_recommendations,
            "project_suggestions": project_suggestions,
            "certifications": [c.get("name") for c in certifications] if certifications else [],
            "quick_tips": quick_tips[:3] if quick_tips else [],
            "personalized_advice": personalized_advice
        }
    
    def _match_skills_to_resources(
        self,
        missing_skills: List[str],
        learning_path: List[Dict],
        experience_level: str
    ) -> List[Dict]:
        """Eksik becerileri öğrenme kaynaklarıyla eşleştir."""
        
        recommendations = []
        
        for skill_name in missing_skills[:5]:  # Max 5 beceri
            # Learning path'te bu beceriyi ara
            matched_resource = None
            for item in learning_path:
                if skill_name.lower() in item.get("skill", "").lower():
                    matched_resource = item
                    break
            
            if matched_resource:
                recommendations.append({
                    "skill": skill_name,
                    "priority": "high",
                    "description": matched_resource.get("description", ""),
                    "resources": matched_resource.get("resources", []),
                    "estimated_time": matched_resource.get("duration", "2-3 hafta")
                })
            else:
                # Genel öneri
                recommendations.append({
                    "skill": skill_name,
                    "priority": "medium",
                    "description": f"{skill_name} öğrenmek kariyer hedefleriniz için önemli.",
                    "resources": [
                        {"type": "search", "name": f"{skill_name} tutorial", "url": None}
                    ],
                    "estimated_time": "2-4 hafta"
                })
        
        return recommendations
    
    def _select_relevant_projects(
        self,
        project_ideas: List[Dict],
        category_scores: Dict,
        current_score: int
    ) -> List[Dict]:
        """Düşük puanlı alanlara göre proje öner."""
        
        # Düşük puanlı kategorileri bul
        low_score_categories = []
        for cat, data in category_scores.items():
            if isinstance(data, dict) and data.get("score", 100) < 70:
                low_score_categories.append(cat)
        
        # Projeleri filtrele ve seç
        selected = []
        for project in project_ideas:
            difficulty = project.get("difficulty", "").lower()
            
            # Skora göre zorluk seç
            if current_score < 50 and "başlangıç" in difficulty:
                selected.append(project)
            elif 50 <= current_score < 75 and "orta" in difficulty:
                selected.append(project)
            elif current_score >= 75 and "ileri" in difficulty:
                selected.append(project)
            
            if len(selected) >= 2:  # Max 2 proje öner
                break
        
        # Yeterli proje bulunamadıysa başlangıç projelerinden ekle
        if not selected and project_ideas:
            selected = project_ideas[:2]
        
        return selected
    
    async def _generate_personalized_advice(
        self,
        field_id: str,
        field_name: str,
        experience_level: str,
        current_score: int,
        weaknesses: List[str],
        missing_skills: List[str],
        cv_skills: List[str] = None
    ) -> str:
        """LLM ile kişiselleştirilmiş tavsiye metni oluştur - CV gap analizi dahil."""
        
        exp_name = EXPERIENCE_LEVELS.get(experience_level, {}).get("name", experience_level)
        
        # Alan için zorunlu teknolojileri al
        required_tech = get_required_technologies(field_id)
        field_display_name = required_tech.get("name", field_name)
        must_know_list = required_tech.get("must_know", [])
        common_skills = required_tech.get("common_with_all", [])
        
        # CV'de eksik teknolojileri bul
        if cv_skills:
            missing_tech = find_missing_technologies(field_id, cv_skills)
        else:
            missing_tech = must_know_list[:5]  # CV skill yoksa ilk 5'i göster
        
        # Zorunlu teknolojileri formatla
        must_know_formatted = "\n".join([f"- {t['tech']}: {t['desc']}" for t in must_know_list])
        missing_tech_formatted = "\n".join([f"- {t['tech']}: {t['desc']}" for t in missing_tech[:7]])
        common_formatted = ", ".join(common_skills)
        
        system_prompt = f"""Sen deneyimli bir kariyer danışmanı ve {field_display_name} alanında uzman bir mentorsun.

ÇIKTI FORMATI ÇOK ÖNEMLİ! Aşağıdaki formata BİREBİR uy:

## 🎯 {field_display_name} Olarak Bilmen Gerekenler

- **Python** – Açıklama
- **TensorFlow** – Açıklama
(Her teknoloji ayrı satırda)

## ❌ CV'nde Eksik Gördüklerim

### 🔸 TensorFlow

**Ne işe yarar:**
Derin öğrenme modelleri geliştirmek için kullanılır.

**Nasıl öğrenirsin:**
Coursera'daki TensorFlow kursu ile başla.

### 🔸 Docker

**Ne işe yarar:**
Uygulamaları konteynerize etmek için kullanılır.

**Nasıl öğrenirsin:**
Docker resmi dökümantasyonu ile pratik yap.

(HER TEKNOLOJİ İÇİN ### BAŞLIĞI KULLAN, "Ne işe yarar" ve "Nasıl öğrenirsin" ALT ALTA OLMALI)

## 📚 Öğrenme Yol Haritası

- **1. Hafta:** Python temelleri
- **2. Hafta:** NumPy ve Pandas
- **3. Hafta:** Scikit-learn
- **4. Hafta:** TensorFlow giriş

(Her hafta AYRI madde olarak liste şeklinde)

KRİTİK KURALLAR:
- Türkçe yaz
- "Ne işe yarar" ve "Nasıl öğrenirsin" AYRI SATIRLARDA olmalı
- Yol haritasındaki haftalar MADDE LİSTESİ olmalı
- Tablo kullanMA
- Kısa ve öz tut"""

        user_message = f"""ADAY PROFİLİ:
- Hedef: {field_display_name}
- Seviye: {exp_name}  
- CV Puanı: {current_score}/100
- Mevcut Beceriler: {', '.join(cv_skills[:10]) if cv_skills else 'Belirtilmemiş'}

ALANDA ZORUNLU TEKNOLOJİLER:
{must_know_formatted}

CV'DE EKSİK OLAN TEKNOLOJİLER:
{missing_tech_formatted}

Yukarıdaki formata uygun şekilde bu adaya tavsiye yaz. Her eksik teknolojiyi ayrı bir ### başlığıyla göster."""

        try:
            response = await llm_service.chat(
                message=user_message,
                system_prompt=system_prompt,
                temperature=0.7,
                max_tokens=1200
            )
            return response.strip()
        except Exception as e:
            return f"Tavsiye oluşturulamadı: {str(e)}"
    
    def _determine_priority_actions(
        self,
        field_analyses: List[Dict[str, Any]]
    ) -> List[str]:
        """Tüm analizlerden öncelikli aksiyonları belirle."""
        
        actions = []
        
        for analysis in field_analyses:
            field_name = analysis.get("field_name", "")
            missing_skills = analysis.get("missing_skills", [])
            weaknesses = analysis.get("weaknesses", [])
            score = analysis.get("overall_score", 100)
            
            # Düşük puanlı alanlar için öncelikli aksiyon
            if score < 60:
                if missing_skills:
                    actions.append(f"⚡ {field_name}: {missing_skills[0]} öğrenmeye başla")
                elif weaknesses:
                    actions.append(f"⚡ {field_name}: {weaknesses[0]} üzerinde çalış")
            elif score < 80:
                if missing_skills:
                    actions.append(f"📈 {field_name}: {missing_skills[0]} becerini geliştir")
        
        # Genel aksiyonlar ekle
        if not actions:
            actions.append("📚 Mevcut becerilerini derinleştirmek için ileri seviye projeler yap")
        
        actions.append("📝 GitHub profiline README dosyaları ekle")
        actions.append("🎯 LeetCode'da günde 1 algoritma sorusu çöz")
        
        return actions[:5]  # Max 5 aksiyon


# Singleton instance
recommendation_service = RecommendationService()

"""
KariyerKoçu - CV Analiz Şemaları
================================
CV analizi için request/response modelleri.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# ============================================================================
# ANALYSIS REQUEST
# ============================================================================

class CVAnalysisRequest(BaseModel):
    """CV analiz isteği."""
    
    sector: str = Field(
        ...,
        description="Sektör ID (örn: bilgisayar_muhendisligi)",
        example="bilgisayar_muhendisligi"
    )
    
    fields: List[str] = Field(
        ...,
        min_length=1,
        max_length=3,
        description="Alan ID listesi (max 3)",
        example=["yapay_zeka", "backend"]
    )
    
    experience_level: str = Field(
        ...,
        description="Tecrübe seviyesi ID",
        example="ogrenci_4"
    )
    
    analysis_method: str = Field(
        default="hybrid",
        description="Analiz yöntemi: pure_llm, pre_llm, hybrid, rule_based",
        example="hybrid"
    )


# ============================================================================
# CATEGORY SCORE (Tek kategori puanı)
# ============================================================================

class CategoryScore(BaseModel):
    """Tek bir kategori için puan detayları."""
    
    score: int = Field(..., ge=0, le=100, description="0-100 arası puan")
    weight: int = Field(..., description="Toplam skora katkı yüzdesi")
    reason: str = Field(..., description="Bu puanın nedeni")
    suggestions: List[str] = Field(default_factory=list, description="İyileştirme önerileri")


# ============================================================================
# FIELD ANALYSIS (Tek alan için analiz)
# ============================================================================

class FieldAnalysis(BaseModel):
    """Tek bir alan (Backend, AI, vs.) için analiz."""
    
    field_id: str = Field(..., description="Alan ID")
    field_name: str = Field(..., description="Alan adı (görüntüleme)")
    overall_score: int = Field(..., ge=0, le=100, description="Bu alan için toplam puan")
    
    # Kategori puanları
    category_scores: Dict[str, CategoryScore] = Field(
        ...,
        description="Her kategori için detaylı puan"
    )
    
    # Özet
    strengths: List[str] = Field(default_factory=list, description="Güçlü yönler")
    weaknesses: List[str] = Field(default_factory=list, description="Zayıf yönler")
    
    # Beceri uyumu
    matching_skills: List[str] = Field(default_factory=list, description="Eşleşen beceriler")
    missing_skills: List[str] = Field(default_factory=list, description="Eksik beceriler")


# ============================================================================
# FULL ANALYSIS RESPONSE
# ============================================================================

class CVAnalysisResponse(BaseModel):
    """Tam CV analiz sonucu."""
    
    # Meta bilgiler
    cv_id: str = Field(..., description="Analiz edilen CV'nin ID'si")
    analysis_date: datetime = Field(default_factory=datetime.utcnow)
    
    # Profil bağlamı
    profile_context: Dict[str, Any] = Field(
        ...,
        description="Sektör, alan, tecrübe bilgileri"
    )
    
    # Alan bazlı analizler
    field_analyses: List[FieldAnalysis] = Field(
        ...,
        description="Her alan için ayrı analiz"
    )
    
    # En güçlü alan
    strongest_field: Optional[str] = Field(
        None,
        description="En yüksek puan alan alan"
    )
    
    # Genel öneriler
    action_items: List[str] = Field(
        default_factory=list,
        description="Yapılması gereken aksiyonlar (öncelik sıralı)"
    )
    
    # Ham LLM yanıtı (debug için)
    raw_llm_response: Optional[str] = Field(None, exclude=True)


# ============================================================================
# CONFIG ENDPOINTS İÇİN RESPONSE'LAR
# ============================================================================

class SectorOption(BaseModel):
    """Dropdown için sektör seçeneği."""
    id: str
    name: str

class FieldOption(BaseModel):
    """Dropdown için alan seçeneği."""
    id: str
    name: str

class ExperienceOption(BaseModel):
    """Dropdown için tecrübe seçeneği."""
    id: str
    name: str
    category: str

class ConfigResponse(BaseModel):
    """Tüm config verisi."""
    sectors: List[SectorOption]
    fields: Dict[str, List[FieldOption]]
    experience_levels: List[ExperienceOption]


# ============================================================================
# RECOMMENDATION SCHEMAS (Tavsiye Sistemi)
# ============================================================================

class RecommendationRequest(BaseModel):
    """Tavsiye isteği - analiz sonuçlarına dayalı."""
    
    # Analiz bilgileri (CVAnalysisResponse'dan)
    sector: str = Field(..., description="Sektör ID")
    fields: List[str] = Field(..., description="Alan ID listesi")
    experience_level: str = Field(..., description="Tecrübe seviyesi")
    
    # Analiz sonuçları
    field_analyses: List[Dict[str, Any]] = Field(
        ...,
        description="Alan bazlı analiz sonuçları"
    )


class LearningResource(BaseModel):
    """Öğrenme kaynağı."""
    type: str = Field(..., description="Kaynak türü: course, video, docs, article")
    name: str = Field(..., description="Kaynak adı")
    url: Optional[str] = Field(None, description="Kaynak linki")


class SkillRecommendation(BaseModel):
    """Tek bir beceri için tavsiye."""
    skill: str = Field(..., description="Beceri adı")
    priority: str = Field(..., description="Öncelik: high, medium, low")
    description: str = Field(..., description="Neden önemli")
    resources: List[LearningResource] = Field(default_factory=list)
    estimated_time: Optional[str] = Field(None, description="Tahmini öğrenme süresi")


class ProjectSuggestion(BaseModel):
    """Proje önerisi."""
    name: str = Field(..., description="Proje adı")
    difficulty: str = Field(..., description="Zorluk seviyesi")
    description: str = Field(..., description="Proje açıklaması")
    skills_to_practice: List[str] = Field(default_factory=list)


class FieldRecommendation(BaseModel):
    """Tek bir alan için tüm tavsiyeler."""
    field_id: str
    field_name: str
    current_score: int = Field(..., description="Mevcut puan")
    
    # Öneriler
    skill_recommendations: List[SkillRecommendation] = Field(default_factory=list)
    project_suggestions: List[ProjectSuggestion] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)
    quick_tips: List[str] = Field(default_factory=list)
    
    # LLM tarafından oluşturulan özet
    personalized_advice: Optional[str] = Field(None, description="Kişiselleştirilmiş tavsiye metni")


class RecommendationResponse(BaseModel):
    """Tam tavsiye yanıtı."""
    
    # Meta
    created_at: datetime = Field(default_factory=datetime.utcnow)
    experience_level: str
    experience_name: str
    
    # Alan bazlı tavsiyeler
    field_recommendations: List[FieldRecommendation]
    
    # Genel tavsiyeler (alan bağımsız)
    general_advice: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="GitHub, soft skills, interview prep tavsiyeleri"
    )
    
    # Öncelik sıralı aksiyon listesi
    priority_actions: List[str] = Field(
        default_factory=list,
        description="En önemli 5 aksiyon"
    )


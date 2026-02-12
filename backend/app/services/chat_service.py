"""
KariyerKoçu - Chat Service
==========================
Context-aware chatbot servisi.
Kullanıcının CV, analiz ve mülakat verilerine erişerek kişiselleştirilmiş cevaplar verir.
"""

import json
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.cv import CV
from app.models.analysis import CVAnalysis
from app.models.interview import InterviewSession, InterviewStatus
from app.services.llm_service import llm_service
from app.career.interview_config import COMPANY_SECTORS, POSITIONS, EXPERIENCE_REQUIREMENTS
from app.career.career_config import FIELDS


class ChatService:
    """
    Context-aware chat servisi.
    
    Kullanıcının tüm verilerine erişerek bağlamsal cevaplar verir.
    """
    
    def __init__(self, db: Session, user: User):
        self.db = db
        self.user = user
    
    async def process_message(self, message: str, history: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Kullanıcı mesajını işle ve cevap döndür.
        
        1. Intent detection (mesajın ne hakkında olduğunu anla)
        2. Context building (ilgili kullanıcı verisini çek)
        3. LLM call (cevap üret) - retry mekanizması ile
        """
        import asyncio
        
        # 1. Intent Detection
        intent = self._detect_intent(message)
        
        # 2. Context Building
        context = await self._build_context(intent)
        
        # 3. User Profile Context (her zaman ekle)
        user_context = self._build_user_context()
        
        # 4. System Prompt oluştur
        system_prompt = self._build_system_prompt(user_context, context)
        
        # 5. LLM Call with Retry
        messages = [{"role": m["role"], "content": m["content"]} for m in history[-10:]]
        messages.append({"role": "user", "content": message})
        
        max_retries = 3
        last_error = None
        
        for attempt in range(max_retries):
            try:
                response = await llm_service.chat_with_history(
                    messages=messages,
                    system_prompt=system_prompt,
                    temperature=0.7,
                    max_tokens=1024
                )
                
                # Başarılı cevap
                return {
                    "response": response,
                    "context_used": intent
                }
                
            except Exception as e:
                last_error = e
                if attempt < max_retries - 1:
                    # Son deneme değilse bekle ve tekrar dene
                    await asyncio.sleep(2)
                    continue
        
        # Tüm denemeler başarısız oldu
        return {
            "response": "Şu an yanıt üretirken bir sorun yaşıyorum. Lütfen bir kaç saniye bekleyip tekrar deneyin. 🔄",
            "context_used": "error"
        }
    
    def get_greeting(self) -> str:
        """Kullanıcıya özel karşılama mesajı oluştur."""
        name = self.user.full_name or "Kullanıcı"
        
        # Kariyer hedefi var mı?
        has_career_goals = any([
            self.user.target_sector,
            self.user.target_position,
            self.user.experience_level
        ])
        
        # CV yüklü mü?
        cv = self.db.query(CV).filter(CV.user_id == self.user.id).first()
        has_cv = cv is not None
        
        # Analiz var mı?
        analysis = self.db.query(CVAnalysis).filter(
            CVAnalysis.user_id == self.user.id
        ).first()
        has_analysis = analysis is not None
        
        # Kişiselleştirilmiş mesaj
        greeting = f"Merhaba {name}! 👋 Ben KariyerKoçu asistanıyım."
        
        suggestions = []
        if not has_career_goals:
            suggestions.append("🎯 Kariyer hedefini belirlememişsin. Profil sayfasından güncelleyebilirsin!")
        if not has_cv:
            suggestions.append("📄 Henüz CV yüklememişsin. CV'ni yükleyerek başlayabilirsin.")
        elif not has_analysis:
            suggestions.append("📊 CV'ni analiz etmemişsin. CV Analiz sayfasından analiz yapabilirsin!")
        
        if suggestions:
            greeting += "\n\n" + "\n".join(suggestions)
        else:
            position_name = POSITIONS.get(self.user.target_position, {}).get("name", "")
            if position_name:
                greeting += f"\n\n{position_name} hedefin için sana yardımcı olabilirim. Ne sormak istersin?"
            else:
                greeting += "\n\nKariyer yolculuğunda sana nasıl yardımcı olabilirim?"
        
        return greeting
    
    def _detect_intent(self, message: str) -> str:
        """Mesajın ne hakkında olduğunu tespit et."""
        message_lower = message.lower()
        
        # Analiz ile ilgili
        if any(kw in message_lower for kw in ["analiz", "puan", "skor", "güçlü", "zayıf", "eksik"]):
            return "analysis"
        
        # Mülakat ile ilgili
        if any(kw in message_lower for kw in ["mülakat", "interview", "soru", "cevap", "performans"]):
            return "interview"
        
        # CV ile ilgili
        if any(kw in message_lower for kw in ["cv", "özgeçmiş", "resume", "beceri", "skill", "proje"]):
            return "cv"
        
        # Kariyer ile ilgili
        if any(kw in message_lower for kw in ["kariyer", "iş", "pozisyon", "maaş", "şirket", "sektör", "geliştir"]):
            return "career"
        
        # Tavsiye ile ilgili
        if any(kw in message_lower for kw in ["tavsiye", "öneri", "ne yapmalı", "nasıl", "öğren"]):
            return "recommendation"
        
        return "general"
    
    async def _build_context(self, intent: str) -> str:
        """Intent'e göre ilgili kullanıcı verisini çek."""
        context_parts = []
        
        if intent == "analysis":
            # Son 3 analizi getir
            analyses = self.db.query(CVAnalysis).filter(
                CVAnalysis.user_id == self.user.id
            ).order_by(CVAnalysis.created_at.desc()).limit(3).all()
            
            if analyses:
                context_parts.append("=== KULLANICININ SON ANALİZLERİ ===")
                for a in analyses:
                    field_names = [FIELDS.get(f, {}).get("name", f) for f in (a.fields or [])]
                    context_parts.append(f"""
Tarih: {a.created_at.strftime('%d.%m.%Y')}
Analiz Edilen Alanlar: {', '.join(field_names)}
Genel Puan: {a.overall_score}/100
En Güçlü Alan: {FIELDS.get(a.strongest_field, {}).get("name", a.strongest_field)}
---""")
            else:
                context_parts.append("Kullanıcının henüz CV analizi yok.")
        
        elif intent == "interview":
            # Son mülakat session'larını getir
            sessions = self.db.query(InterviewSession).filter(
                InterviewSession.user_id == self.user.id,
                InterviewSession.status == InterviewStatus.COMPLETED
            ).order_by(InterviewSession.completed_at.desc()).limit(3).all()
            
            if sessions:
                context_parts.append("=== KULLANICININ MÜLAKAT GEÇMİŞİ ===")
                for s in sessions:
                    position_name = POSITIONS.get(s.position, {}).get("name", s.position)
                    score_text = f"{s.average_score:.1f}/10" if s.average_score else "N/A"
                    status_text = "Geçti" if s.average_score and s.average_score >= 6.0 else "Geçemedi"
                    context_parts.append(f"""
Tarih: {s.completed_at.strftime('%d.%m.%Y') if s.completed_at else 'Tamamlanmadı'}
Pozisyon: {position_name}
Ortalama Puan: {score_text}
Durum: {status_text}
---""")
            else:
                context_parts.append("Kullanıcının henüz tamamlanmış mülakatı yok.")
        
        elif intent == "cv":
            cv = self.db.query(CV).filter(
                CV.user_id == self.user.id
            ).order_by(CV.created_at.desc()).first()
            
            if cv:
                context_parts.append("=== KULLANICININ CV BİLGİLERİ ===")
                skills = cv.skills or []
                projects = cv.projects or []
                
                # Proje isimlerini çıkar
                project_names = []
                for p in projects:
                    if isinstance(p, dict):
                        name = p.get("name", p.get("title", ""))
                        if name:
                            project_names.append(name)
                    elif isinstance(p, str):
                        project_names.append(p)
                
                context_parts.append(f"""
Dosya: {cv.original_filename}
İsim: {cv.full_name or 'Belirtilmemiş'}
Beceri Sayısı: {len(skills)}
Beceriler: {', '.join(skills[:15])}{'...' if len(skills) > 15 else ''}
Proje Sayısı: {len(projects)}
Proje İsimleri: {', '.join(project_names) if project_names else 'Proje isimleri mevcut değil'}
---""")
            else:
                context_parts.append("Kullanıcının henüz yüklenmiş CV'si yok.")
        
        elif intent in ["career", "recommendation"]:
            # Hem CV hem analiz bilgisi ekle
            cv = self.db.query(CV).filter(CV.user_id == self.user.id).first()
            analysis = self.db.query(CVAnalysis).filter(
                CVAnalysis.user_id == self.user.id
            ).order_by(CVAnalysis.created_at.desc()).first()
            
            if cv:
                skills = cv.skills or []
                context_parts.append(f"Kullanıcının becerileri: {', '.join(skills[:20])}")
            
            if analysis:
                context_parts.append(f"Son analiz puanı: {analysis.overall_score}/100")
                context_parts.append(f"En güçlü alan: {FIELDS.get(analysis.strongest_field, {}).get('name', analysis.strongest_field)}")
        
        return "\n".join(context_parts)
    
    def _build_user_context(self) -> str:
        """Kullanıcı profil bilgilerini context olarak hazırla."""
        parts = []
        
        parts.append(f"Kullanıcı Adı: {self.user.full_name or 'Belirtilmemiş'}")
        
        if self.user.target_sector:
            sector_name = COMPANY_SECTORS.get(self.user.target_sector, {}).get("name", self.user.target_sector)
            parts.append(f"Hedef Sektör: {sector_name}")
        
        if self.user.target_position:
            position_name = POSITIONS.get(self.user.target_position, {}).get("name", self.user.target_position)
            parts.append(f"Hedef Pozisyon: {position_name}")
        
        if self.user.experience_level:
            level_name = EXPERIENCE_REQUIREMENTS.get(self.user.experience_level, {}).get("name", self.user.experience_level)
            parts.append(f"Tecrübe Seviyesi: {level_name}")
        
        return "\n".join(parts)
    
    def _build_system_prompt(self, user_context: str, data_context: str) -> str:
        """LLM için system prompt oluştur."""
        return f"""Sen KariyerKoçu platformunun yapay zeka kariyer asistanısın.
Kullanıcılara kariyer, CV, mülakat ve iş arama konularında yardımcı oluyorsun.

⚠️ ÇOK ÖNEMLİ - CEVAP VERMEDEN ÖNCE AŞAĞIDAKİ VERİLERİ DİKKATLİCE OKU ⚠️

=== KULLANICI PROFİLİ ===
{user_context}

=== VERİTABANINDAN GELEN VERİLER ===
{data_context if data_context else "Bu konu için veritabanında kayıt bulunamadı."}

=== SİSTEMDE OLAN ÖZELLİKLER (BUNLARI ANLATABILIRSIN) ===
1. CV Yükleme ve Analizi - PDF/DOCX CV yükleyip analiz edebilir
2. AI Destekli Mülakat Simülasyonu - Metin ve sesli mülakat yapabilir
3. İş Arama - JobSpy ve Kariyer.net üzerinden iş ilanları arayabilir
4. Ön Yazı Oluşturma - Seçilen ilan için ön yazı üretebilir
5. CV Önerileri - CV'yi iyileştirmek için öneriler alabilir
6. Kariyer Hedefleri - Profil sayfasından hedef sektör/pozisyon belirleyebilir
7. Skill Gap Analizi - Meslek bazlı eksik beceri analizi

=== SİSTEMDE OLMAYAN ÖZELLİKLER (BUNLARDAN ASLA BAHSETMEMELİSİN) ===
❌ Favori ilanlar kaydetme
❌ Bildirim/notification sistemi
❌ İş başvurusu yapma (sistem sadece ilanları listeler, başvuru yapmaz)
❌ CV şablonları oluşturma
❌ Diğer kullanıcılarla iletişim
❌ Premium üyelik
❌ E-posta gönderme
❌ Takvim/randevu sistemi

=== KRİTİK KURALLAR ===
1. ⚡ SADECE TÜRKÇE CEVAP VER! İngilizce, Çince veya başka dil KULLANMA!
2. ⚡ MARKDOWN KULLANMA! Yıldız (*), hash (#), tire (-) ile formatlama YAPMA!
3. ⚡ DÜZ METİN YAZ! Bold, italic, liste işareti kullanma!
4. ⚡ YUKARIDAKİ "OLMAYAN ÖZELLİKLER" LİSTESİNDEKİ ŞEYLERDEN BAHSETMEMELİSİN! UYDURMAK YASAK!
5. Emojileri ölçülü kullan (sadece cümle sonunda)
6. ÖNCE YUKARIDAKI VERİLERİ OKU! Veri varsa MUTLAKA kullan!
7. Kullanıcı analiz, CV veya mülakat soruyorsa ve yukarıda veri varsa, O VERİLERİ BAZ ALARAK cevap ver
8. "Sistemde kaydınız yok" demeden önce yukarıdaki verileri TEKRAR kontrol et
9. Kısa, öz ve net ol
10. Motive edici ve destekleyici ol

=== FORMATLAMA ÖRNEKLERİ ===
❌ YANLIŞ: "**Projeleriniz:**\n- Proje 1\n- Proje 2"
✅ DOĞRU: "Projeleriniz şunlar: Deepfake Tespit, LLM Video Analiz, Yüz Tanıma. Toplam 8 proje var."

❌ YANLIŞ: "### Güçlü Yönler\n**1. Python** bilgisi..."
✅ DOĞRU: "Güçlü yönlerin: Python bilgisi, AI/ML projeleri, TensorFlow deneyimi."

❌ YANLIŞ: "İlanları favorilere ekleyip bildirim alabilirsiniz."
✅ DOĞRU: "İş Arama sayfasından ilanları görüntüleyebilir ve detaylarına bakabilirsiniz."

=== ÖRNEK DAVRANIŞLAR ===
✅ DOĞRU: "Sistemde 3 analiz raporunuz var. En son analizinizde 82 puan almışsınız."
❌ YANLIŞ: "Sistemde analiz kaydınız bulunmuyor" (veri varken bunu ASLA söyleme)

Şimdi kullanıcının sorusuna, YUKARIDAKİ VERİLERİ KULLANARAK ve DÜZ METİN olarak cevap ver.
"""


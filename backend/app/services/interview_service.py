"""
KariyerKoçu - Mülakat Servisi
=============================
Soru üretme, cevap değerlendirme ve rapor oluşturma.
"""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.services.llm_service import llm_service
from app.models.interview import InterviewSession, InterviewQuestion, InterviewAnswer, InterviewStatus, QuestionType
from app.models.cv import CV
from app.career.interview_config import (
    COMPANY_SECTORS,
    POSITIONS,
    EXPERIENCE_REQUIREMENTS,
    INTERVIEW_TYPES,
    get_position_topics,
    get_experience_difficulty
)


class InterviewService:
    """
    Mülakat Servisi.
    
    Soru üretme, cevap değerlendirme ve rapor oluşturma işlemlerini yönetir.
    """
    
    async def generate_question(
        self,
        session: InterviewSession,
        cv_data: Optional[Dict] = None,
        previous_answer: Optional[InterviewAnswer] = None,
        db: Session = None
    ) -> Dict[str, Any]:
        """
        Yeni soru üret.
        
        Args:
            session: Mülakat oturumu
            cv_data: CV bilgileri (sektor_yorum tipi için)
            previous_answer: Önceki cevap (bağlantılı geçiş için)
            db: Database session
        """
        
        question_number = session.current_question_number + 1
        position_name = POSITIONS.get(session.position, {}).get("name", session.position)
        exp_info = get_experience_difficulty(session.experience_level)
        exp_name = EXPERIENCE_REQUIREMENTS.get(session.experience_level, {}).get("name", session.experience_level)
        topics = get_position_topics(session.position)
        
        # Soru tipini belirle
        interview_type = session.interview_type
        if interview_type == "sektor_yorum" and cv_data and question_number % 2 == 0:
            # Çift sorularda CV bazlı soru
            question_type = QuestionType.CV_BASED
        elif interview_type == "sektor_yorum" and question_number % 3 == 0:
            # Her 3. soruda senaryo
            question_type = QuestionType.SCENARIO
        else:
            question_type = QuestionType.TECHNICAL
        
        # Prompt oluştur
        system_prompt = self._build_question_prompt(
            position_name=position_name,
            exp_name=exp_name,
            exp_info=exp_info,
            topics=topics,
            question_type=question_type,
            cv_data=cv_data
        )
        
        # Geçiş cümlesi için önceki cevap bilgisi
        previous_context = ""
        if previous_answer:
            score = previous_answer.score or 5
            if score >= 7:
                previous_context = f"Önceki cevap puanı: {score}/10 (İYİ). Takdir edici bir geçiş yap."
            elif score >= 5:
                previous_context = f"Önceki cevap puanı: {score}/10 (ORTA). Nötr bir geçiş yap."
            else:
                previous_context = f"Önceki cevap puanı: {score}/10 (ZAYIF). Nazik ama geliştirici bir geçiş yap."
        
        # Önceki soruları al (tekrar önleme için)
        previous_questions = db.query(InterviewQuestion).filter(
            InterviewQuestion.session_id == session.id
        ).all()
        previous_questions_text = ""
        if previous_questions:
            prev_q_list = [f"- {q.question_text}" for q in previous_questions]
            previous_questions_text = f"""

⚠️ DAHA ÖNCE SORULAN SORULAR (BUNLARI TEKRAR SORMA!):
{chr(10).join(prev_q_list)}

YENİ VE FARKLI BİR SORU SOR!
"""
        
        user_message = f"""Soru numarası: {question_number}/{session.total_questions}
Soru tipi: {question_type.value}
{previous_context}
{previous_questions_text}
Lütfen bir mülakat sorusu üret.
"""
        
        try:
            response = await llm_service.chat(
                message=user_message,
                system_prompt=system_prompt,
                temperature=0.4,  # Daha tutarlı çıktı için düşürüldü
                max_tokens=800   # Kesilmeyi önlemek için artırıldı
            )
            
            result = self._parse_question_response(response)
            
            # Soruyu veritabanına kaydet
            question = InterviewQuestion(
                session_id=session.id,
                question_number=question_number,
                question_text=result.get("question", "Soru üretilemedi"),
                question_tts=result.get("question_tts"),  # TTS için Türkçe telaffuz versiyonu
                question_type=question_type.value,
                transition_text=result.get("transition"),
                transition_tts=result.get("transition_tts")  # Geçiş TTS versiyonu
            )
            db.add(question)
            
            # Session güncelle
            session.current_question_number = question_number
            db.commit()
            
            return {
                "question_id": question.id,
                "question_number": question_number,
                "total_questions": session.total_questions,
                "transition_text": result.get("transition"),
                "transition_tts": result.get("transition_tts"),
                "question_text": result.get("question", "Soru üretilemedi"),
                "question_tts": result.get("question_tts"),
                "question_type": question_type.value,
                "is_last_question": question_number >= session.total_questions
            }
            
        except Exception as e:
            # Hata durumunda varsayılan soru
            fallback_question = f"{position_name} pozisyonunda {topics[0] if topics else 'temel konular'} hakkında bilgi verir misiniz?"
            
            question = InterviewQuestion(
                session_id=session.id,
                question_number=question_number,
                question_text=fallback_question,
                question_tts=fallback_question,  # Fallback için aynı metin
                question_type=QuestionType.TECHNICAL.value
            )
            db.add(question)
            session.current_question_number = question_number
            db.commit()
            
            return {
                "question_id": question.id,
                "question_number": question_number,
                "total_questions": session.total_questions,
                "transition_text": None,
                "transition_tts": None,
                "question_text": fallback_question,
                "question_tts": fallback_question,
                "question_type": QuestionType.TECHNICAL.value,
                "is_last_question": question_number >= session.total_questions
            }
    
    async def evaluate_answer(
        self,
        question: InterviewQuestion,
        user_answer: str,
        session: InterviewSession,
        db: Session
    ) -> Dict[str, Any]:
        """
        Cevabı değerlendir.
        
        Not: Değerlendirme sonuçları kullanıcıya gösterilmez, sadece kaydedilir.
        """
        
        position_name = POSITIONS.get(session.position, {}).get("name", session.position)
        exp_name = EXPERIENCE_REQUIREMENTS.get(session.experience_level, {}).get("name", session.experience_level)
        exp_level = session.experience_level
        
        # Tecrübe seviyesine göre değerlendirme kriterleri
        level_criteria = {
            "stajyer": {
                "expectations": "Temel kavramları bilmesi yeterli. Uygulama detayları beklenmez.",
                "passing_score": 5,
                "positive_prefix": "Stajyer için iyi bir cevap",
                "negative_prefix": "Stajyer için bile yetersiz"
            },
            "yeni_mezun": {
                "expectations": "Temel kavramlar + teorik bilgi beklenir. Pratikte eksiklik kabul edilebilir.",
                "passing_score": 5,
                "positive_prefix": "Yeni mezun için güçlü bir cevap",
                "negative_prefix": "Yeni mezun için yetersiz"
            },
            "junior": {
                "expectations": "Pratik deneyim ve temel problem çözme beklenir.",
                "passing_score": 6,
                "positive_prefix": "Junior seviyesi için iyi",
                "negative_prefix": "Junior için beklenen seviyenin altında"
            },
            "mid_level": {
                "expectations": "Derin teknik bilgi ve mimari anlayış beklenir.",
                "passing_score": 6,
                "positive_prefix": "Mid-Level için yeterli",
                "negative_prefix": "Mid-Level için yetersiz kalıyor"
            },
            "senior": {
                "expectations": "System design, best practices ve liderlik perspektifi beklenir.",
                "passing_score": 7,
                "positive_prefix": "Senior seviyesine yakışır bir cevap",
                "negative_prefix": "Senior için kabul edilemez, çok yüzeysel"
            },
            "lead": {
                "expectations": "Stratejik düşünce, ekip yönetimi ve mimari vizyonu beklenir.",
                "passing_score": 7,
                "positive_prefix": "Tech Lead seviyesine uygun",
                "negative_prefix": "Lead pozisyonu için yetersiz"
            }
        }
        
        criteria = level_criteria.get(exp_level, level_criteria["junior"])
        
        # [SESLI] prefix'ini LLM değerlendirmesi için temizle
        answer_for_evaluation = user_answer
        if user_answer.startswith("[SESLI] "):
            answer_for_evaluation = user_answer[8:]  # "[SESLI] " = 8 karakter
        
        # BOŞ VEYA ÇOK KISA CEVAP KONTROLÜ
        # Eğer cevap boş veya çok kısaysa, LLM'e sormadan düşük puan ver
        # AMA YINE DE CEVABI KAYDET (aksi halde mülakat tamamlanamaz!)
        cleaned_answer = answer_for_evaluation.strip()
        
        if not cleaned_answer or len(cleaned_answer) < 10:
            # Kısa/boş cevap - düşük puan ama yine de kaydet
            answer = InterviewAnswer(
                question_id=question.id,
                user_answer=user_answer,
                score=1,
                evaluation_reason="Cevap verilmedi veya çok kısa. Soruya anlamlı bir yanıt beklenmektedir.",
                ideal_answer="Soruyla ilgili teknik veya kavramsal bir açıklama yapılmalıydı.",
                strengths=[],
                weaknesses=["Cevap verilmedi", "Soru anlaşılmamış olabilir"]
            )
            db.add(answer)
            question.is_answered = True
            db.commit()
            
            return {
                "answer_id": answer.id,
                "score": 1,
                "reason": "Cevap verilmedi veya çok kısa.",
                "feedback": "Cevabınız alınamadı veya çok kısa. Lütfen soruyu dinleyip detaylı cevap verin."
            }
        
        # Çok kısa cevaplar için de uyarı (10-30 karakter arası)
        if len(cleaned_answer) < 30:
            # Kısa cevap - düşük puan ama yine de kaydet
            answer = InterviewAnswer(
                question_id=question.id,
                user_answer=user_answer,
                score=2,
                evaluation_reason="Cevap çok kısa ve yetersiz. Daha detaylı bir açıklama beklenmektedir.",
                ideal_answer="Soruyla ilgili kapsamlı bir teknik açıklama yapılmalıydı.",
                strengths=[],
                weaknesses=["Çok kısa cevap", "Detay eksikliği", "Teknik içerik yok"]
            )
            db.add(answer)
            question.is_answered = True
            db.commit()
            
            return {
                "answer_id": answer.id,
                "score": 2,
                "reason": "Cevap çok kısa ve yetersiz.",
                "feedback": "Cevabınız çok kısa. Mülakatlarda daha detaylı açıklamalar yapmanız beklenir."
            }
        
        system_prompt = f"""Sen bir {position_name} mülakatında cevapları değerlendiren İK uzmanısın.
Aday: {exp_name} seviyesinde.

SEVİYEYE GÖRE BEKLENTİ:
{criteria['expectations']}

DEĞERLENDİRME KRİTERLERİ:
- Teknik doğruluk
- Açıklama kalitesi  
- Pratik uygulama bilgisi
- SEVİYEYE UYGUNLUK (çok önemli!)

PUANLAMA ({exp_name} için):
1-3: {criteria['negative_prefix']} - kritik eksikler
4-5: Zayıf ama gelişebilir
6-7: Kabul edilebilir, {exp_name} için yeterli
8-9: {criteria['positive_prefix']}, güçlü cevap
10: Mükemmel, seviyenin üzerinde

ÖNEMLİ: Yorumda mutlaka seviyeye göre değerlendirme yap!
Örnek: "Stajyer için iyi bir cevap" veya "Senior için yetersiz, daha derin analiz beklenirdi"

JSON FORMATINDA CEVAP VER:
{{
    "score": 7,
    "reason": "Seviyeye göre değerlendirme ve açıklama",
    "ideal_answer": "İdeal cevap ne olmalıydı (kısa)",
    "strengths": ["güçlü yön 1", "güçlü yön 2"],
    "weaknesses": ["eksik 1", "eksik 2"]
}}

SADECE JSON DÖNDÜR!"""

        user_message = f"""SORU: {question.question_text}

ADAYIN CEVABI: {answer_for_evaluation}

Bu cevabı {exp_name} seviyesine göre değerlendir."""

        try:
            response = await llm_service.chat(
                message=user_message,
                system_prompt=system_prompt,
                temperature=0.3,
                max_tokens=1000  # Kesilmeyi önlemek için artırıldı
            )
            
            evaluation = self._parse_evaluation_response(response)
            
            # Cevabı kaydet
            answer = InterviewAnswer(
                question_id=question.id,
                user_answer=user_answer,
                score=evaluation.get("score", 5),
                evaluation_reason=evaluation.get("reason", ""),
                ideal_answer=evaluation.get("ideal_answer"),
                strengths=evaluation.get("strengths", []),
                weaknesses=evaluation.get("weaknesses", [])
            )
            db.add(answer)
            
            # Soruyu cevaplandı olarak işaretle
            question.is_answered = True
            db.commit()
            
            return {
                "answer_id": answer.id,
                "score": answer.score,
                "message": "Cevabınız kaydedildi"
            }
            
        except Exception as e:
            # Hata durumunda varsayılan değerlendirme
            answer = InterviewAnswer(
                question_id=question.id,
                user_answer=user_answer,
                score=5,
                evaluation_reason="Değerlendirme yapılamadı",
                strengths=[],
                weaknesses=[]
            )
            db.add(answer)
            question.is_answered = True
            db.commit()
            
            return {
                "answer_id": answer.id,
                "score": 5,
                "message": "Cevabınız kaydedildi"
            }
    
    def complete_interview(
        self,
        session: InterviewSession,
        db: Session
    ) -> Dict[str, Any]:
        """Mülakatı tamamla ve skorları hesapla."""
        
        # Tüm cevapları al
        questions = db.query(InterviewQuestion).filter(
            InterviewQuestion.session_id == session.id
        ).all()
        
        answered_questions = [q for q in questions if q.is_answered and q.answer]
        
        if not answered_questions:
            session.status = InterviewStatus.COMPLETED
            session.completed_at = datetime.utcnow()
            session.average_score = 0
            db.commit()
            return {"average_score": 0, "passed": False}
        
        # Ortalama puan hesapla
        scores = [q.answer.score for q in answered_questions if q.answer.score]
        average_score = sum(scores) / len(scores) if scores else 0
        total_score = sum(scores)
        
        # Session güncelle
        session.status = InterviewStatus.COMPLETED
        session.completed_at = datetime.utcnow()
        session.average_score = round(average_score, 2)
        session.total_score = total_score
        db.commit()
        
        return {
            "average_score": round(average_score, 2),
            "total_score": total_score,
            "answered_count": len(answered_questions),
            "passed": average_score >= 6.0
        }
    
    def generate_report(
        self,
        session: InterviewSession,
        db: Session
    ) -> Dict[str, Any]:
        """Detaylı mülakat raporu oluştur."""
        
        # Mülakat bilgileri
        sector_name = COMPANY_SECTORS.get(session.company_sector, {}).get("name", session.company_sector)
        position_name = POSITIONS.get(session.position, {}).get("name", session.position)
        exp_name = EXPERIENCE_REQUIREMENTS.get(session.experience_level, {}).get("name", session.experience_level)
        
        # Soruları ve cevapları al
        questions = db.query(InterviewQuestion).filter(
            InterviewQuestion.session_id == session.id
        ).order_by(InterviewQuestion.question_number).all()
        
        question_reports = []
        all_strengths = []
        all_weaknesses = []
        
        for q in questions:
            if q.answer:
                question_reports.append({
                    "question_number": q.question_number,
                    "question_type": q.question_type,
                    "question_text": q.question_text,
                    "user_answer": q.answer.user_answer,
                    "score": q.answer.score or 0,
                    "evaluation_reason": q.answer.evaluation_reason or "",
                    "ideal_answer": q.answer.ideal_answer,
                    "strengths": q.answer.strengths or [],
                    "weaknesses": q.answer.weaknesses or []
                })
                
                all_strengths.extend(q.answer.strengths or [])
                all_weaknesses.extend(q.answer.weaknesses or [])
        
        # Tekrar edenleri say ve en çok tekrar edenleri al
        from collections import Counter
        top_strengths = [s for s, _ in Counter(all_strengths).most_common(3)]
        top_weaknesses = [w for w, _ in Counter(all_weaknesses).most_common(3)]
        
        # Süre hesapla
        duration = None
        if session.completed_at and session.created_at:
            duration = int((session.completed_at - session.created_at).total_seconds() / 60)
        
        return {
            "session_id": session.id,
            "completed_at": session.completed_at or datetime.utcnow(),
            "duration_minutes": duration,
            "company_sector": session.company_sector,
            "company_sector_name": sector_name,
            "position": session.position,
            "position_name": position_name,
            "experience_level": session.experience_level,
            "experience_level_name": exp_name,
            "interview_type": session.interview_type,
            "total_questions": session.total_questions,
            "answered_questions": len(question_reports),
            "average_score": session.average_score or 0,
            "passing_score": 6.0,
            "passed": (session.average_score or 0) >= 6.0,
            "questions": question_reports,
            "overall_strengths": top_strengths,
            "overall_weaknesses": top_weaknesses,
            "recommendation": self._generate_recommendation(session.average_score or 0, top_weaknesses)
        }
    
    def _build_question_prompt(
        self,
        position_name: str,
        exp_name: str,
        exp_info: Dict,
        topics: List[str],
        question_type: QuestionType,
        cv_data: Optional[Dict] = None
    ) -> str:
        """Soru üretme promptu oluştur."""
        
        # Zorluk seviyesine göre soru talimatları
        difficulty_instructions = {
            "easy": """
ZORLUK: KOLAY (Stajyer/Yeni Mezun)
- Temel kavram soruları sor (tanım, açıklama)
- "X nedir?", "Y ne işe yarar?" tarzı sorular
- Kod yazmayı değil, konsept anlamayı test et
- Karmaşık senaryolardan kaçın
- Örnek: "REST API nedir ve ne için kullanılır?"
""",
            "easy_to_medium": """
ZORLUK: KOLAY-ORTA (Yeni Mezun)
- Temel kavramlar + basit uygulama soruları
- "X'i nasıl kullanırsın?", "Y'nin avantajları nelerdir?" tarzı
- Basit kod/pseudocode sorabilirsin
- Örnek: "GET ve POST arasındaki fark nedir? Ne zaman hangisini kullanırsın?"
""",
            "medium": """
ZORLUK: ORTA (Junior - 1-3 yıl)
- Pratik uygulama ve problem çözme soruları
- "Bu problemi nasıl çözersin?", "Hata ayıklama" tarzı
- Kod yazma ve debugging soruları
- Örnek: "N+1 query problemi nedir ve nasıl çözersin?"
""",
            "medium_hard": """
ZORLUK: ORTA-ZOR (Mid-Level - 3-5 yıl)
- Mimari kararlar ve trade-off soruları
- "Bu durumda hangi pattern'i tercih edersin ve neden?"
- Performans ve ölçeklendirme soruları
- Örnek: "Microservices mi monolith mi tercih edersin? Bu projede neden?"
""",
            "hard": """
ZORLUK: ZOR (Senior - 5+ yıl)
- System design ve architecture soruları
- Liderlik ve kod review senaryoları
- "Bir ekip olarak bu problemi nasıl çözerdiniz?"
- Scale, reliability, security trade-off'ları
- Örnek: "1 milyon kullanıcıya ölçeklenecek bir sistem nasıl tasarlarsın?"
""",
            "expert": """
ZORLUK: UZMAN (Tech Lead/Principal)
- Organizasyonel ve stratejik sorular
- Teknik borç yönetimi, roadmap planlama
- Ekip oluşturma ve mentörlük
- Örnek: "Eski bir sistemi modernize ederken ekibini nasıl yönetirsin?"
"""
        }
        
        # Stajyer için easy, yeni mezun için easy_to_medium, vs.
        difficulty_map = {
            "easy": "easy",
            "basic": "easy",
            "basic_to_intermediate": "easy_to_medium",
            "intermediate": "medium",
            "intermediate_to_advanced": "medium_hard",
            "advanced": "hard",
            "expert": "expert"
        }
        
        mapped_difficulty = difficulty_map.get(exp_info.get("question_depth", "medium"), "medium")
        difficulty_text = difficulty_instructions.get(mapped_difficulty, difficulty_instructions["medium"])
        
        base_prompt = f"""Sen bir {position_name} pozisyonu için mülakat yapan deneyimli İK uzmanısın.
Aday: {exp_name} seviyesinde.

{difficulty_text}

POZİSYON İÇİN ÖNEMLİ KONULAR:
{', '.join(topics)}

"""
        
        if question_type == QuestionType.CV_BASED and cv_data:
            projects = cv_data.get("projects", [])
            if projects:
                project_names = [p.get("name", "") for p in projects[:3]]
                base_prompt += f"""
ADAY CV'SİNDEKİ PROJELER:
{', '.join(project_names)}

CV'deki bir proje hakkında detaylı soru sor.
"""
        elif question_type == QuestionType.SCENARIO:
            base_prompt += """
SENARYO BAZLI SORU SOR:
Gerçek dünya problemi ver ve nasıl çözeceğini sor.
"""
        else:
            base_prompt += """
TEKNİK SORU SOR:
Konulardan biriyle ilgili teknik bilgi sorusu sor.
"""
        
        base_prompt += """

🎙️ SESLİ MÜLAKAT SİSTEMİ
Bu bir Türkçe mülakattır. Sorular sesli okunacak.

JSON FORMATINDA CEVAP VER:
{
    "transition": "Önceki cevaba bağlantılı kısa geçiş cümlesi (ilk soru ise null)",
    "question": "Mülakat sorusu"
}

KURALLAR:
1. Sorular ve geçişler TÜRKÇE olmalı
2. Teknik terimler normal yazılabilir (Docker, Python, API, Machine Learning)
3. Cümleleri yarım bırakma
4. Yazım hatası yapma
5. SADECE JSON döndür, başka hiçbir şey yazma

ÖRNEK:
{
    "transition": "Güzel bir cevaptı, şimdi farklı bir konuya geçelim.",
    "question": "Docker container'larını Kubernetes ile nasıl yönetirsiniz?"
}

SADECE JSON DÖNDÜR!"""
        
        return base_prompt
    
    def _parse_question_response(self, response: str) -> Dict[str, Any]:
        """LLM soru yanıtını parse et - sağlamlaştırılmış versiyon."""
        import re
        
        def validate_text(text: str) -> str:
            """Metni doğrula ve temizle."""
            if not text:
                return ""
            # Kesilmiş metinleri tespit et (sonu noktalama ile bitmiyorsa)
            text = text.strip()
            # transition_tts: gibi field kalıntılarını temizle
            text = re.sub(r'\b(transition_tts|question_tts|transition|question)\s*:', '', text)
            text = text.strip()
            return text
        
        try:
            response = response.strip()
            
            # Markdown code block varsa içini al
            if "```" in response:
                match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response)
                if match:
                    response = match.group(1).strip()
            
            # JSON parse et
            result = json.loads(response)
            
            if isinstance(result, dict):
                # Field'ları al ve doğrula
                question = validate_text(result.get("question") or result.get("soru") or "")
                question_tts = validate_text(result.get("question_tts") or result.get("soru_tts") or "")
                transition = result.get("transition") or result.get("gecis")
                transition_tts = result.get("transition_tts") or result.get("gecis_tts")
                
                # transition null veya "null" string ise None yap
                if transition in [None, "null", "None", ""]:
                    transition = None
                else:
                    transition = validate_text(transition)
                
                if transition_tts in [None, "null", "None", ""]:
                    transition_tts = None
                else:
                    transition_tts = validate_text(transition_tts)
                
                # question_tts yoksa question'ı kullan (tutarlılık için)
                if not question_tts:
                    question_tts = question
                
                # transition_tts yoksa transition'ı kullan
                if transition and not transition_tts:
                    transition_tts = transition
                
                return {
                    "question": question,
                    "question_tts": question_tts,
                    "transition": transition,
                    "transition_tts": transition_tts
                }
            
        except json.JSONDecodeError:
            pass
        except Exception:
            pass
        
        # Parse edilemezse ham metni soru olarak kullan
        # Ama önce içinde JSON benzeri yapı varsa onu çıkarmaya çalış
        try:
            # Raw text'te { } varsa JSON olabilir
            if "{" in response and "}" in response:
                # JSON kısmını bul
                start = response.find("{")
                end = response.rfind("}") + 1
                json_str = response[start:end]
                result = json.loads(json_str)
                if isinstance(result, dict):
                    question = result.get("question") or result.get("soru") or ""
                    question_tts = result.get("question_tts") or result.get("soru_tts") or question
                    transition = result.get("transition") or result.get("gecis")
                    transition_tts = result.get("transition_tts") or result.get("gecis_tts") or transition
                    return {
                        "question": question,
                        "question_tts": question_tts,
                        "transition": transition,
                        "transition_tts": transition_tts
                    }
        except:
            pass
        
        # Son çare: Response'u düz metin olarak soru yap
        # Ama JSON kalıntılarını temizle
        cleaned = response
        # JSON formatını temizle
        cleaned = re.sub(r'\{[^}]*"question"\s*:\s*"([^"]+)"[^}]*\}', r'\1', cleaned)
        cleaned = re.sub(r'\{[^}]*"transition"\s*:[^,]*,?', '', cleaned)
        cleaned = re.sub(r'[{}"\[\]]', '', cleaned)
        cleaned = re.sub(r'question\s*:', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'transition\s*:\s*null,?', '', cleaned, flags=re.IGNORECASE)
        cleaned = cleaned.strip()
        
        if cleaned:
            return {"question": cleaned, "question_tts": cleaned, "transition": None, "transition_tts": None}
        
        return {"question": response, "question_tts": response, "transition": None, "transition_tts": None}
    
    def _parse_evaluation_response(self, response: str) -> Dict[str, Any]:
        """LLM değerlendirme yanıtını parse et."""
        import re
        
        try:
            response = response.strip()
            
            # Markdown code block varsa temizle
            if response.startswith("```"):
                # ```json veya ``` ile başlayan blokları temizle
                response = re.sub(r'^```(?:json)?\s*\n?', '', response)
                response = re.sub(r'\n?```\s*$', '', response)
            
            # JSON bloğunu bulmaya çalış
            # Önce direkt parse dene
            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                # JSON regex ile ara - { ile başlayıp } ile biten kısım
                json_match = re.search(r'\{[\s\S]*\}', response)
                if json_match:
                    result = json.loads(json_match.group())
                else:
                    raise ValueError("JSON bulunamadı")
            
            # Gerekli alanları kontrol et ve varsayılanları ekle
            if "score" in result:
                result["score"] = max(1, min(10, int(result["score"])))
            else:
                result["score"] = 5
            
            if "reason" not in result:
                result["reason"] = "Değerlendirme tamamlandı"
            
            if "strengths" not in result or not isinstance(result["strengths"], list):
                result["strengths"] = []
            
            if "weaknesses" not in result or not isinstance(result["weaknesses"], list):
                result["weaknesses"] = []
            
            return result
            
        except Exception as e:
            # Parse başarısız olursa LLM yanıtından bilgi çıkarmaya çalış
            score = 5
            reason = response[:200] if response else "Değerlendirme yapılamadı"
            
            # Yanıtta sayı varsa score olarak kullan
            import re
            score_match = re.search(r'(\d+)\s*/\s*10', response)
            if score_match:
                score = max(1, min(10, int(score_match.group(1))))
            
            return {
                "score": score,
                "reason": reason,
                "ideal_answer": None,
                "strengths": [],
                "weaknesses": []
            }
    
    def _generate_recommendation(self, average_score: float, weaknesses: List[str]) -> str:
        """Genel tavsiye metni oluştur."""
        
        if average_score >= 8:
            return "Mükemmel performans! Bu pozisyon için güçlü bir adaysınız. Mevcut bilgilerinizi güncel tutmaya devam edin."
        elif average_score >= 6:
            if weaknesses:
                return f"İyi bir performans gösterdiniz. Daha güçlü bir aday olmak için şu alanlara odaklanabilirsiniz: {', '.join(weaknesses[:2])}."
            return "İyi bir performans gösterdiniz. Pratik deneyiminizi artırarak kendinizi geliştirebilirsiniz."
        elif average_score >= 4:
            return f"Bazı alanlarda gelişime ihtiyacınız var. Özellikle şu konulara çalışmanızı öneririm: {', '.join(weaknesses[:3]) if weaknesses else 'temel konular'}."
        else:
            return "Bu pozisyon için daha fazla hazırlık yapmanız gerekiyor. Temel kavramları pekiştirin ve pratik projeler yapın."


# Singleton instance
interview_service = InterviewService()

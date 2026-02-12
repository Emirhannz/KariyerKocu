# -*- coding: utf-8 -*-
"""
Önyazı ve E-mail Oluşturma Servisi v3
======================================
Akıllı, profil-bilinçli önyazı ve e-mail oluşturma.

YENİ: İki aşamalı LLM sistemi
1. Oluştur: İlk taslak
2. Düzelt: Yazım hataları, yabancı karakterler, aşırı övgü kontrolü

Özellikler:
- Profil bazlı: Yeni mezun için farklı, deneyimli için farklı ton
- Sektör bazlı: Savunma, Fintech, E-ticaret, Startup için özel cümleler
- Pozisyon tipi: Staj, Uzun Dönem Staj, Junior, Mid, Senior
- KENDİNİ ÖVME: "Uygun adayım" gibi ifadeler YOK
"""

from typing import Dict, Optional, List
from app.services.llm_service import llm_service


class CoverLetterService:
    """
    Akıllı önyazı ve e-mail oluşturan servis.
    
    FELSEFE:
    - Gerçekçi ol: Yeni mezuna "10 yıllık uzman" deme
    - Kendini övme: "Uygun adayım", "en iyi adayım" gibi ifadeler YASAK
    - Bırak İK karar versin: Ne yaptığını söyle, ne olduğunu değil
    """
    
    # Pozisyon tipleri ve açıklamaları
    POSITION_TYPES = {
        "intern": {
            "name": "Stajyer",
            "tone": "Öğrenmeye aç, meraklı, enerjik. Tecrübe yok ama potansiyel var.",
            "avoid": "Uzun deneyim, uzmanlık iddiası, liderlik, kendini övme"
        },
        "long_intern": {
            "name": "Uzun Dönem Stajyer", 
            "tone": "Öğrenmeye aç ama biraz tecrübe kazanmış. Proje bazlı çalışma biliyor.",
            "avoid": "Çok kıdemli ifadeler, departman yönetimi, kendini övme"
        },
        "junior": {
            "name": "Junior",
            "tone": "Yeni mezun veya 1-2 yıl tecrübeli. Pratik projeler yapmış ama hala öğreniyor.",
            "avoid": "Senior ifadeler, ekip liderliği, 5+ yıl deneyim, kendini övme"
        },
        "mid": {
            "name": "Mid-Level",
            "tone": "3-5 yıl tecrübeli. Bağımsız çalışabilen, teknik kararlar verebilen.",
            "avoid": "Yeni mezun ifadeleri, aşırı mütevazılık, kendini övme"
        },
        "senior": {
            "name": "Senior",
            "tone": "5+ yıl tecrübeli. Teknik liderlik, mimari kararlar, mentorluk yapabilen.",
            "avoid": "Stajyer ifadeleri, öğrenmeye muhtaç görünme, kendini övme"
        }
    }
    
    # Sektör özellikleri
    SECTORS = {
        "defense": {
            "name": "Savunma Sanayii",
            "keywords": ["gizlilik bilinci", "gömülü sistemler", "kritik sistemler", "milli teknoloji"],
            "tone": "Resmi, ciddi, güvenilir",
            "emphasis": "Gizlilik bilinci, milli değerler, kritik sistemlerde çalışma motivasyonu"
        },
        "fintech": {
            "name": "Fintech / Bankacılık",
            "keywords": ["güvenlik", "uyumluluk (compliance)", "finansal veriler", "regülasyonlar"],
            "tone": "Profesyonel, güvenilir, detay odaklı",
            "emphasis": "Veri güvenliği, hata toleransı düşük sistemler, finansal hesaplama"
        },
        "ecommerce": {
            "name": "E-ticaret",
            "keywords": ["yüksek trafik", "ölçeklenebilirlik", "kullanıcı deneyimi", "performans"],
            "tone": "Dinamik, sonuç odaklı",
            "emphasis": "Ölçeklenebilir sistemler, yüksek trafik yönetimi, kullanıcı odaklılık"
        },
        "startup": {
            "name": "Startup",
            "keywords": ["hızlı hareket", "çevik", "çoklu şapka", "öğrenme"],
            "tone": "Enerjik, esnek, heyecanlı",
            "emphasis": "Adaptasyon, hızlı öğrenme, birden fazla rol üstlenebilme"
        },
        "corporate": {
            "name": "Kurumsal / Büyük Şirket",
            "keywords": ["süreç yönetimi", "kurumsal kültür", "kalite standartları"],
            "tone": "Profesyonel, yapılandırılmış",
            "emphasis": "Kurumsal süreçlere uyum, ekip çalışması, dokümantasyon"
        },
        "tech": {
            "name": "Teknoloji Şirketi",
            "keywords": ["inovasyon", "teknik mükemmellik", "açık kaynak", "modern stack"],
            "tone": "Teknik, meraklı, yenilikçi",
            "emphasis": "Teknik yetkinlik, modern teknolojiler, problem çözme"
        }
    }
    
    # Yazım tonları
    STYLES = {
        "professional": {
            "name": "Profesyonel",
            "description": "Resmi, kurumsal, ciddi",
            "greeting": "Sayın Yetkili,",
            "closing": "Saygılarımla,"
        },
        "friendly": {
            "name": "Samimi",
            "description": "Sıcak, ulaşılabilir ama profesyonel",
            "greeting": "Merhaba,",
            "closing": "Selamlar,"
        },
        "direct": {
            "name": "Direkt",
            "description": "Kısa, öz, vakit kaybetmeyen",
            "greeting": "Merhaba,",
            "closing": "İyi çalışmalar,"
        }
    }
    
    # YASAK İFADELER - bunları kullanma!
    FORBIDDEN_PHRASES = [
        "uygun bir adayım",
        "en uygun aday",
        "mükemmel bir aday",
        "ideal aday",
        "güçlü bir aday",
        "bu pozisyon için biçilmiş kaftan",
        "tam aradığınız kişi",
        "en iyi seçim",
        "harika bir eşleşme",
        "şüphesiz ki",
        "kesinlikle",
        "tartışmasız"
    ]
    
    # Uzunluk seçenekleri
    LENGTHS = {
        "short": {
            "name": "Kısa",
            "word_range": "150-200",
            "paragraphs": "3 kısa paragraf",
            "instruction": "Çok kısa ve öz yaz. Sadece en önemli noktaları belirt."
        },
        "medium": {
            "name": "Orta",
            "word_range": "250-350",
            "paragraphs": "4 orta uzunlukta paragraf",
            "instruction": "Dengeli bir uzunlukta yaz. Ana noktaları ve birkaç detay ekle."
        },
        "long": {
            "name": "Uzun",
            "word_range": "400-500",
            "paragraphs": "5-6 detaylı paragraf",
            "instruction": "Detaylı yaz. Projeler, deneyimler ve motivasyonu açıkla."
        }
    }
    
    async def generate_smart_cover_letter(
        self,
        cv_data: Dict,
        company_name: str,
        position_title: str,
        position_type: str,
        sector: str,
        style: str = "professional",
        length: str = "medium",
        company_note: Optional[str] = None,
        job_description: Optional[str] = None
    ) -> Dict:
        """
        Akıllı önyazı oluştur - İKİ AŞAMALI SİSTEM.
        
        1. Oluştur: İlk taslak
        2. Düzelt: Yazım, ton, yabancı karakter kontrolü
        """
        try:
            profile_summary = self._build_profile_summary(cv_data, position_type)
            sector_info = self.SECTORS.get(sector, self.SECTORS["tech"])
            position_info = self.POSITION_TYPES.get(position_type, self.POSITION_TYPES["junior"])
            style_info = self.STYLES.get(style, self.STYLES["professional"])
            length_info = self.LENGTHS.get(length, self.LENGTHS["medium"])
            
            # ============================================================
            # AŞAMA 1: OLUŞTUR
            # ============================================================


            pos_type_info = self.POSITION_TYPES.get(position_type, self.POSITION_TYPES["junior"])
            style_config = self.STYLES.get(style, self.STYLES["professional"])
            
            # Context hazırlığı
            company_context = f"FİRMAYA ÖZEL NOT: {company_note}" if company_note else ""
            job_context = f"İLAN METNİNDEN ÖNEMLİ BİLGİLER: {job_description[:600]}" if job_description else ""
            sector_keywords_str = ', '.join(sector_info['keywords'])
            
            # Uzunluk talimatı
            length_instruction = f"\n\n## UZUNLUK TALİMATI\n{length_info['instruction']}\nHedef kelime sayısı: {length_info['word_range']}\nParagraf sayısı: {length_info['paragraphs']}"

            # ============================================================
            # AŞAMA 1: OLUŞTUR
            # ============================================================
            
            # Adayın adını ve iletişim bilgilerini al - eksikse placeholder koy
            candidate_name = cv_data.get("full_name", "") or "[Ad Soyad giriniz]"
            candidate_phone = cv_data.get("phone", "") or "[Telefon giriniz]"
            candidate_email_addr = cv_data.get("email", "") or "[E-posta giriniz]"
            candidate_github = cv_data.get("github", "")
            candidate_linkedin = cv_data.get("linkedin", "")
            
            system_prompt = f"""Sen profesyonel bir kariyer danışmanı ve metin yazarısın.
Görevin: {company_name} şirketindeki {position_title} pozisyonu için profesyonel bir önyazı (cover letter) yazmak.
{length_instruction}

## PROFESYONEL ÖNYAZI FORMATI (BU FORMATA BİREBİR UY!)

Sayın {company_name} İnsan Kaynakları Ekibi,

[GİRİŞ PARAGRAFI - 2-3 cümle]
{position_title} pozisyonuna başvuruyorum. [Neden bu şirkete ilgi duyduğunu açıkla - şirketin projeleri, vizyonu vb.]

[GELİŞME PARAGRAFI - 3-4 cümle]
Deneyim ve projelerinden bahset. Teknik yetkinliklerini vurgula.
Sektöre uygun vurgular yap ({sector_info['name']}: {sector_info['emphasis']}).

[SONUÇ PARAGRAFI - 2 cümle]
Görüşme talebi. Teşekkür.

{style_config['closing']}
{candidate_name}
{candidate_phone}
{candidate_email_addr}

## KURALLAR

### BAŞLANGIÇ - ÇOK ÖNEMLİ!
- İLK CÜMLE: "Sayın {company_name} İnsan Kaynakları Ekibi," ile BAŞLA
- İKİNCİ CÜMLE: "{position_title} pozisyonuna başvuruyorum." veya "... pozisyonu için başvurmak istiyorum." şeklinde olmalı
- ASLA "Benim adıma", "Ben", "Kendimi tanıtmak" gibi ifadelerle BAŞLAMA!
- ASLA kişisel zamirleri cümle başında kullanma!

### DİL
- SADECE Türkçe yaz. İngilizce kelime YASAK.
- Yazım hatası yapma.

### TON
- {style_config['description']}
- {pos_type_info['tone']}
- {pos_type_info['avoid']} gibi ifadelerden kaçın.

### İÇERİK
- Adayın projelerinden SOMUT örnekler ver.
- 200-250 kelime.
- Kendini övme ("harika bir adayım" YASAK). Yaptıklarını anlat, kararı okuyucuya bırak.
- "Sayın {company_name} İnsan Kaynakları Ekibi," ile BAŞLA.
- İmza bloğunda Ad Soyad, Telefon ve E-posta MUTLAKA olmalı.

ADAY BİLGİLERİ:
{profile_summary}

{company_context}
{job_context}

Sadece önyazı metnini döndür. Başka açıklama yapma."""

            user_message = "Önyazıyı oluştur."

            # Retry logic - boş veya tamamlanmamış yanıtlarda otomatik tekrar dene
            max_retries = 3
            draft = None
            for attempt in range(max_retries):
                draft = await llm_service.chat(
                    message=user_message,
                    system_prompt=system_prompt,
                    temperature=0.3,  # Düşük temperature = daha tutarlı çıktı
                    max_tokens=1200,  # Artırıldı - tamamlanmama sorununu önler
                )
                
                # Başarılı mı kontrol et
                if draft and draft.strip() != "" and draft.strip().lower() != "none":
                    # Minimum uzunluk kontrolü (en az 100 kelime olmalı)
                    word_count = len(draft.strip().split())
                    if word_count >= 100:
                        break  # Başarılı, döngüden çık
                
                # Başarısız, bekle ve tekrar dene
                if attempt < max_retries - 1:
                    import asyncio
                    await asyncio.sleep(2)  # 2 saniye bekle ve tekrar dene
            
            # Null kontrolü
            if not draft or draft.strip() == "" or draft.strip().lower() == "none":
                return {
                    "success": False,
                    "error": "Önyazı oluşturulamadı. Lütfen tekrar deneyin.",
                    "cover_letter": "",
                    "word_count": 0,
                    "tips": []
                }
            
            # ============================================================
            # AŞAMA 2: ÇİFT DOĞRULAMA - Dil ve yazım kontrolü
            # ============================================================
            result_text = await self._review_and_fix(
                text=draft.strip(),
                text_type="önyazı",
                position_level=position_info['name']
            )
            
            word_count = len(result_text.split())
            
            return {
                "success": True,
                "cover_letter": result_text,
                "word_count": word_count,
                "profile_type": position_info['name'],
                "sector": sector_info['name'],
                "tips": self._generate_tips(cv_data, position_type, sector)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Önyazı oluşturma hatası: {str(e)}",
                "cover_letter": "",
                "word_count": 0,
                "tips": []
            }
    
    async def generate_smart_email(
        self,
        cv_data: Dict,
        company_name: str,
        position_title: str,
        position_type: str,
        sector: str,
        style: str = "professional",
        length: str = "medium",
        company_note: Optional[str] = None
    ) -> Dict:
        """
        Akıllı başvuru e-maili oluştur - İKİ AŞAMALI SİSTEM.
        """
        try:
            profile_summary = self._build_profile_summary(cv_data, position_type)
            sector_info = self.SECTORS.get(sector, self.SECTORS["tech"])
            position_info = self.POSITION_TYPES.get(position_type, self.POSITION_TYPES["junior"])
            style_info = self.STYLES.get(style, self.STYLES["professional"])
            
            # Uzunluk bilgisi
            email_lengths = {
                "short": "30-50 kelime - sadece 2-3 cümle",
                "medium": "50-80 kelime - 3-4 cümle", 
                "long": "80-120 kelime - 4-5 cümle ile biraz daha detaylı"
            }
            length_instruction = email_lengths.get(length, email_lengths["medium"])
            
            # Adayın bilgilerini çıkar - ÖNCE tanımla
            candidate_name = cv_data.get("full_name", "") or "[Ad Soyad giriniz]"
            candidate_phone = cv_data.get("phone", "") or "[Telefon giriniz]"
            candidate_email_addr = cv_data.get("email", "") or "[E-posta giriniz]"
            candidate_linkedin = cv_data.get("linkedin", "")
            
            # ============================================================
            # AŞAMA 1: OLUŞTUR (ULTRA KISA E-MAİL)
            # Araştırmaya göre: E-mail sadece "köprü" görevi görür
            # CV ve ön yazı ekte olduğu için e-mail ÇOK KISA olmalı
            # ============================================================
            system_prompt = f"""Sen profesyonel bir e-mail yazarısın. Görevin: İK'ya gönderilecek ÇOK KISA bir başvuru e-maili yazmak.

## ÖNEMLİ: E-mail sadece bir "köprü" görevi görür. CV ve ön yazı ekte olduğu için detay VERME.

## UZUNLUK: {length_instruction}

## E-MAİL FORMATI (BU FORMATA BİREBİR UY!)

KONU: {position_title} Başvurusu - {candidate_name}

Sayın {company_name} İnsan Kaynakları Ekibi,

[1-2 cümle: Hangi pozisyona başvurduğun + neden bu şirkete ilgi duyduğun]
[1 cümle: CV ve ön yazı ekte + görüşme talebi]

{style_info['closing']}
{candidate_name}
{candidate_phone}
{candidate_email_addr}

## KURALLAR
1. SADECE Türkçe yaz
2. Hedef kelime sayısı: {length_instruction}
3. Proje, teknoloji, okul ismi YAZMA - bunlar CV'de var
4. Kendini tanıtırken sadece "yazılım geliştirme alanındaki deneyimimle" gibi GENEL ifade kullan
5. İmza bloğu MUTLAKA olmalı

SADECE e-mail metnini döndür (KONU: dahil)."""

            company_context = ""
            if company_note:
                company_context = f"\n\nFİRMAYA ÖZEL NOT: {company_note}"

            user_message = f"""## HEDEF
- Şirket: {company_name}
- Pozisyon: {position_title}
- Seviye: {position_info['name']}
{company_context}

## İMZA BİLGİLERİ
- Ad Soyad: {candidate_name}
- Telefon: {candidate_phone}
- E-posta: {candidate_email_addr}

Kısa başvuru e-maili yaz:"""

            # Retry logic - kullanıcı görmeden otomatik tekrar dene
            max_retries = 3
            for attempt in range(max_retries):
                draft = await llm_service.chat(
                    message=user_message,
                    system_prompt=system_prompt,
                    temperature=0.5,  # Biraz daha yaratıcı ama tutarlı
                    max_tokens=600,   # Biraz artırıldı
                )
                
                # Başarılı mı kontrol et
                if draft and draft.strip() != "" and draft.strip().lower() != "none":
                    break  # Başarılı, döngüden çık
                
                # Başarısız, bekle ve tekrar dene
                if attempt < max_retries - 1:
                    import asyncio
                    await asyncio.sleep(2)  # 2 saniye bekle ve tekrar dene
            
            # Son kontrol
            if not draft or draft.strip() == "" or draft.strip().lower() == "none":
                return {
                    "success": False,
                    "error": "E-mail oluşturulamadı. Lütfen tekrar deneyin.",
                    "subject": "",
                    "body": "",
                    "tips": []
                }
            
            # Review adımını şimdilik atlıyoruz - direkt draft kullan
            subject, body = self._parse_email_response(draft.strip())
            
            return {
                "success": True,
                "subject": subject,
                "body": body.strip(),
                "profile_type": position_info['name'],
                "tips": [
                    "E-mailinize CV'nizi PDF olarak ekleyin",
                    "Gönderim saatine dikkat edin (09:00-17:00 arası ideal)",
                    "Konu satırı kısa ve net olmalı"
                ]
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"E-mail oluşturma hatası: {str(e)}",
                "subject": "",
                "body": "",
                "tips": []
            }
    
    async def _review_and_fix(self, text: str, text_type: str, position_level: str) -> str:
        """
        İKİNCİ AŞAMA: Metni kontrol et ve düzelt.
        
        Basit regex tabanlı düzeltme - LLM çağrısı YAPMADAN.
        Bu sayede format bozulmaz ve hızlı çalışır.
        """
        import re
        
        # Yaygın İngilizce kelimeler ve Türkçe karşılıkları
        word_replacements = {
            r'\bexperience\b': 'deneyim',
            r'\bExperience\b': 'Deneyim',
            r'\bchallenge\b': 'zorluk',
            r'\bChallenge\b': 'Zorluk',
            r'\bchallenges\b': 'zorluklar',
            r'\bopportunity\b': 'fırsat',
            r'\bOpportunity\b': 'Fırsat',
            r'\bopportunities\b': 'fırsatlar',
            r'\bpassion\b': 'tutku',
            r'\bPassion\b': 'Tutku',
            r'\bpassionate\b': 'tutkulu',
            r'\bskill\b': 'beceri',
            r'\bSkill\b': 'Beceri',
            r'\bskills\b': 'beceriler',
            r'\bteam\b': 'ekip',
            r'\bTeam\b': 'Ekip',
            r'\bproject\b': 'proje',
            r'\bProject\b': 'Proje',
            r'\bprojects\b': 'projeler',
            r'\bposition\b': 'pozisyon',
            r'\bPosition\b': 'Pozisyon',
            r'\bcompany\b': 'şirket',
            r'\bCompany\b': 'Şirket',
            r'\bapplication\b': 'başvuru',
            r'\bApplication\b': 'Başvuru',
            r'\binterested\b': 'ilgiliyim',
            r'\binterest\b': 'ilgi',
            r'\bInterest\b': 'İlgi',
            r'\bmotivated\b': 'motive',
            r'\bMotivated\b': 'Motive',
            r'\bmotivation\b': 'motivasyon',
            r'\bexpérience\b': 'deneyim',  # Fransızca
            r'\bExpérience\b': 'Deneyim',
            r'\bknowledge\b': 'bilgi',
            r'\bKnowledge\b': 'Bilgi',
            r'\bability\b': 'yetenek',
            r'\bAbility\b': 'Yetenek',
            r'\babilities\b': 'yetenekler',
            r'\bachievement\b': 'başarı',
            r'\bAchievement\b': 'Başarı',
            r'\bachievements\b': 'başarılar',
            r'\bresponsibility\b': 'sorumluluk',
            r'\bResponsibility\b': 'Sorumluluk',
            r'\bresponsibilities\b': 'sorumluluklar',
        }
        
        result = text
        
        # Kelimeleri değiştir (case-insensitive)
        for pattern, replacement in word_replacements.items():
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE if pattern[0] != '\\' else 0)
        
        # Kendini övme ifadelerini yumuşat
        self_praise_patterns = [
            (r'\ben uygun adayım\b', 'bu pozisyona uygun olduğumu düşünüyorum'),
            (r'\bideal adayım\b', 'uygun bir aday olduğumu düşünüyorum'),
            (r'\bmükemmelim\b', 'yetkinim'),
            (r'\bmükemmel adayım\b', 'uygun bir aday olduğumu düşünüyorum'),
        ]
        
        for pattern, replacement in self_praise_patterns:
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
        
        return result
    
    def _build_profile_summary(self, cv_data: Dict, position_type: str) -> str:
        """CV verisinden LLM için profil özeti oluştur."""
        parts = []
        
        # İsim (ÖNEMLİ!)
        if cv_data.get("full_name"):
            parts.append(f"İsim: {cv_data['full_name']}")
        
        # Eğitim (ÖNEMLİ!) - Üniversiteyi önceliklendir, liseyi atla
        if cv_data.get("education"):
            edu = cv_data["education"]
            if isinstance(edu, list) and len(edu) > 0:
                # Üniversite/yüksek eğitimi bul (liseyi atla)
                selected_edu = None
                for edu_item in edu:
                    if isinstance(edu_item, dict):
                        degree = edu_item.get('degree', '').lower()
                        school = edu_item.get('school', '').lower()
                        # Lise değilse al
                        if not any(x in degree for x in ['lise', 'high school', 'ortaokul', 'ilkokul']):
                            if not any(x in school for x in ['lise', 'high school', 'lisesi']):
                                selected_edu = edu_item
                                break
                
                # Üniversite bulunamadıysa ilk eğitimi al
                if not selected_edu and len(edu) > 0:
                    selected_edu = edu[0] if isinstance(edu[0], dict) else None
                
                if selected_edu:
                    school = selected_edu.get('school', '')
                    field = selected_edu.get('field', '')
                    degree = selected_edu.get('degree', '')
                    edu_str = f"{degree} - {field} ({school})".strip(" -")
                    parts.append(f"Eğitim: {edu_str}")
        
        # Deneyim yılı (KRİTİK!)
        exp_years = cv_data.get("experience_years", "Belirtilmemiş")
        parts.append(f"Toplam Deneyim: {exp_years}")
        
        # Mevcut unvan
        if cv_data.get("title"):
            parts.append(f"Mevcut Unvan: {cv_data['title']}")
        
        # Yetenekler
        if cv_data.get("skills"):
            skills = cv_data["skills"]
            if isinstance(skills, list) and len(skills) > 0:
                skills_str = ", ".join(skills[:10])
                parts.append(f"Teknik Yetenekler: {skills_str}")
        
        # Projeler (stajyer/junior için çok önemli!)
        if cv_data.get("projects"):
            projects = cv_data["projects"]
            if isinstance(projects, list) and len(projects) > 0:
                project_list = []
                for p in projects[:3]:
                    if isinstance(p, dict):
                        name = p.get("name", "")
                        tech = p.get("technologies", [])
                        desc = p.get("description", "")[:50]
                        if name:
                            proj_str = name
                            if tech:
                                proj_str += f" ({', '.join(tech[:3])})"
                            project_list.append(proj_str)
                if project_list:
                    parts.append(f"Projeler: {'; '.join(project_list)}")
        
        # Son deneyim
        if cv_data.get("experience"):
            exp = cv_data["experience"]
            if isinstance(exp, list) and len(exp) > 0:
                last_exp = exp[0]
                if isinstance(last_exp, dict):
                    title = last_exp.get('title', '')
                    company = last_exp.get('company', '')
                    if title and company:
                        parts.append(f"Son İş: {title} @ {company}")
        
        # GitHub/LinkedIn
        if cv_data.get("github"):
            parts.append(f"GitHub: {cv_data['github']}")
        if cv_data.get("linkedin"):
            parts.append(f"LinkedIn: {cv_data['linkedin']}")
        
        # İletişim
        if cv_data.get("phone"):
            parts.append(f"Telefon: {cv_data['phone']}")
        if cv_data.get("email"):
            parts.append(f"E-posta: {cv_data['email']}")
        
        return "\n".join(parts)
    
    def _parse_email_response(self, response: str) -> tuple:
        """E-mail response'unu subject ve body'ye ayır."""
        subject = ""
        body = response
        
        # "KONU:" veya "Konu:" ara
        response_upper = response.upper()
        if "KONU:" in response_upper:
            idx = response_upper.find("KONU:")
            rest = response[idx + 5:].strip()
            lines = rest.split("\n", 1)
            subject = lines[0].strip()
            if len(lines) > 1:
                body = lines[1].strip()
        
        if not subject:
            subject = "İş Başvurusu"
        
        return subject, body
    
    def _generate_tips(self, cv_data: Dict, position_type: str, sector: str) -> List[str]:
        """Profil ve sektöre göre ipuçları oluştur."""
        tips = []
        
        if not cv_data.get("github") and not cv_data.get("linkedin"):
            tips.append("GitHub veya LinkedIn eklemeniz CV'nizi güçlendirir")
        
        if not cv_data.get("projects") or len(cv_data.get("projects", [])) < 2:
            if position_type in ["intern", "junior", "long_intern"]:
                tips.append("Stajyer/Junior için projeler çok önemli - daha fazla proje ekleyin")
        
        if sector == "defense":
            tips.append("Savunma sektörü için güvenlik/gizlilik bilincini vurgulayın")
        elif sector == "fintech":
            tips.append("Fintech için veri güvenliği ve hata toleransınızı öne çıkarın")
        elif sector == "startup":
            tips.append("Startup'lar için çeviklik ve hızlı öğrenmenizi vurgulayın")
        
        tips.append("Önyazıyı her başvuru için özelleştirin")
        
        return tips[:4]
    
    # Backward compatibility
    async def generate_cover_letter(self, *args, **kwargs):
        return await self.generate_smart_cover_letter(*args, **kwargs)
    
    async def generate_application_email(self, *args, **kwargs):
        return await self.generate_smart_email(*args, **kwargs)


# Singleton
cover_letter_service = CoverLetterService()

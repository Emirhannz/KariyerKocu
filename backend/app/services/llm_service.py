"""
KariyerKoçu - LLM Service
=========================
io Intelligence API entegrasyonu.

ÖĞRENME NOKTASI:
- OpenAI-uyumlu API kullanımı
- Async HTTP istekleri (httpx)
- Prompt engineering temelleri
- Error handling ve retry logic
"""

import re
import httpx
from typing import Optional, List, Dict, Any
from app.config import settings


class LLMService:
    """
    io Intelligence API ile iletişim kuran servis.
    
    KULLANIM:
    ```python
    llm = LLMService()
    response = await llm.chat("Merhaba, nasılsın?")
    print(response)
    ```
    
    io Intelligence, OpenAI API formatıyla tam uyumlu.
    Bu sayede aynı kod OpenAI ile de çalışır.
    """
    
    def __init__(self):
        """LLM Service'i başlat."""
        self.api_key = settings.io_intelligence_api_key
        self.base_url = settings.io_intelligence_base_url
        
        # Varsayılan model: Config'den al
        self.default_model = settings.io_intelligence_model
        
        # HTTP client ayarları
        self.timeout = 120.0  # 120 saniye timeout (CV parsing için yeterli)
    
    def _clean_response(self, text: str) -> str:
        """
        LLM yanıtından Çince/Japonca/Korece karakterleri temizle.
        
        Bazı LLM'ler bazen rastgele CJK karakterler üretebiliyor.
        Bu fonksiyon bunları temizler.
        """
        if not text:
            return text
        
        # Çince karakterler (CJK Unified Ideographs)
        # Japonca Hiragana ve Katakana
        # Korece Hangul
        cjk_pattern = r'[\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff\uac00-\ud7af]+'
        
        # CJK karakterleri boşlukla değiştir
        cleaned = re.sub(cjk_pattern, ' ', text)
        
        # Sadece yatay boşlukları temizle (tab, space), newline'ları KORU!
        # Birden fazla boşluğu tek boşluğa çevir ama newline'lara dokunma
        cleaned = re.sub(r'[^\S\n]+', ' ', cleaned)  # \S olmayan ama \n olmayan -> boşluk
        
        # Satır başı ve sonundaki boşlukları temizle
        cleaned = '\n'.join(line.strip() for line in cleaned.split('\n'))
        
        # Üç veya daha fazla ardışık boş satırı iki satıra indir
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
        
        return cleaned.strip()
        
    def _get_headers(self) -> Dict[str, str]:
        """API istekleri için header'ları döndür."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
    
    async def chat(
        self,
        message: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> str:
        """
        LLM ile sohbet et.
        ...
        """
        # ... (same message history logic) ...
        # Message prep is the same, so we only replace from _get_headers to the loop start or just the relevant parts.
        # Let's replace _get_headers and the loop handling.
        
        # Messages prep
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": message})
        
        payload = {
            "model": model or self.default_model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        
        # Retry logic with exponential backoff and jitter
        max_retries = 3
        base_delay = 2
        
        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(
                        f"{self.base_url}/chat/completions",
                        headers=self._get_headers(),
                        json=payload,
                    )
                    
                    # Rate limit kontrolü (429)
                    if response.status_code == 429:
                        print(f"⚠️ Rate limit detail: {response.text[:200]}") # Debug log
                        if attempt < max_retries - 1:
                            import asyncio
                            import random
                            wait_time = (base_delay * (2 ** attempt)) + random.uniform(0, 1)
                            print(f"⚠️ Rate limit! {wait_time:.1f}sn bekleniyor... (Deneme {attempt + 1}/{max_retries})")
                            await asyncio.sleep(wait_time)
                            continue
                        else:
                            raise Exception(f"Rate limit aşıldı.")
                    
                    # Diğer hatalar
                    if response.status_code != 200:
                        error_detail = response.text
                        print(f"❌ API Error Detail: {error_detail}")
                        raise Exception(f"LLM API Error ({response.status_code}): {error_detail}")
                    
                    # Cevabı parse et
                    data = response.json()
                    
                    # OpenAI formatı: choices[0].message.content
                    content = data["choices"][0]["message"]["content"]
                    
                    # Boş cevap kontrolü
                    if not content or content.strip() == "":
                        if attempt < max_retries - 1:
                            import asyncio
                            print(f"⚠️ Boş cevap! Tekrar deneniyor... (Deneme {attempt + 1}/{max_retries})")
                            await asyncio.sleep(base_delay)
                            continue
                        else:
                            return ""  # Son denemede de boşsa boş döndür
                    
                    # CJK karakterleri temizle ve döndür
                    return self._clean_response(content)
                    
            except httpx.TimeoutException:
                if attempt < max_retries - 1:
                    import asyncio
                    print(f"⚠️ Timeout! Tekrar deneniyor... (Deneme {attempt + 1}/{max_retries})")
                    await asyncio.sleep(base_delay)
                    continue
                else:
                    raise Exception("API zaman aşımına uğradı. Lütfen tekrar deneyin.")
        
        # Buraya ulaşılmamalı ama güvenlik için
        raise Exception("Beklenmeyen hata oluştu.")
    
    async def chat_with_history(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> str:
        """
        Mesaj geçmişiyle sohbet et.
        
        Args:
            messages: Mesaj listesi [{"role": "user/assistant", "content": "..."}]
            system_prompt: Sistem prompt'u
            model: Model
            temperature: Yaratıcılık
            max_tokens: Max token
            
        Returns:
            LLM cevabı
        """
        # Mesajları hazırla
        all_messages = []
        
        if system_prompt:
            all_messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        all_messages.extend(messages)
        
        # API isteği
        payload = {
            "model": model or self.default_model,
            "messages": all_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=self._get_headers(),
                json=payload,
            )
            
            if response.status_code != 200:
                raise Exception(f"LLM API Error ({response.status_code}): {response.text}")
            
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            # CJK karakterleri temizle ve döndür
            return self._clean_response(content)
    
    async def generate_interview_question(
        self,
        position: str,
        difficulty: str = "orta",
        previous_questions: Optional[List[str]] = None,
    ) -> str:
        """
        Mülakat sorusu üret.
        
        Args:
            position: Pozisyon (örn: "Backend Developer")
            difficulty: Zorluk seviyesi ("kolay", "orta", "zor")
            previous_questions: Daha önce sorulan sorular (tekrar önlemek için)
            
        Returns:
            Mülakat sorusu
        """
        system_prompt = f"""Sen deneyimli bir teknik mülakatçısın. 
{position} pozisyonu için {difficulty} seviyede mülakat soruları soruyorsun.

KURALLAR:
1. Sadece TEK bir soru sor
2. Soru açık ve net olmalı
3. Türkçe sor
4. Teknik bilgiyi ölç
5. Daha önce sorulan soruları TEKRARLAMA"""

        user_message = f"Pozisyon: {position}\nZorluk: {difficulty}"
        
        if previous_questions:
            user_message += f"\n\nDaha önce sorulan sorular (BUNLARI SORMA):\n"
            for i, q in enumerate(previous_questions, 1):
                user_message += f"{i}. {q}\n"
        
        user_message += "\n\nYeni bir mülakat sorusu sor:"
        
        return await self.chat(
            message=user_message,
            system_prompt=system_prompt,
            temperature=0.8,  # Biraz yaratıcılık
            max_tokens=500,
        )
    
    async def evaluate_answer(
        self,
        question: str,
        answer: str,
        position: str,
    ) -> Dict[str, Any]:
        """
        Mülakat cevabını değerlendir.
        
        Args:
            question: Sorulan soru
            answer: Verilen cevap
            position: Pozisyon
            
        Returns:
            {
                "score": 0-100,
                "feedback": "Değerlendirme metni",
                "strengths": ["güçlü yönler"],
                "improvements": ["geliştirilecek noktalar"]
            }
        """
        system_prompt = f"""Sen deneyimli bir teknik mülakatçısın.
{position} pozisyonu için verilen cevabı değerlendiriyorsun.

CEVAP FORMATINI AYNEN UYGULA:
PUAN: [0-100 arası sayı]
GENEL DEĞERLENDİRME: [2-3 cümle feedback]
GÜÇLÜ YÖNLER: [virgülle ayrılmış liste]
GELİŞTİRİLECEK NOKTALAR: [virgülle ayrılmış liste]"""

        user_message = f"""SORU: {question}

CEVAP: {answer}

Bu cevabı değerlendir:"""

        response = await self.chat(
            message=user_message,
            system_prompt=system_prompt,
            temperature=0.3,  # Tutarlı değerlendirme için düşük
            max_tokens=800,
        )
        
        # Response'u parse et
        return self._parse_evaluation(response)
    
    def _parse_evaluation(self, response: str) -> Dict[str, Any]:
        """
        Değerlendirme cevabını parse et.
        
        LLM'den gelen formatlı metni dict'e çevir.
        """
        result = {
            "score": 50,
            "feedback": "",
            "strengths": [],
            "improvements": [],
            "raw_response": response,
        }
        
        lines = response.strip().split("\n")
        
        for line in lines:
            line = line.strip()
            
            if line.startswith("PUAN:"):
                try:
                    # "PUAN: 75" -> 75
                    score_str = line.replace("PUAN:", "").strip()
                    # Sadece sayıları al
                    score = int(''.join(filter(str.isdigit, score_str[:3])))
                    result["score"] = min(100, max(0, score))
                except:
                    pass
                    
            elif line.startswith("GENEL DEĞERLENDİRME:"):
                result["feedback"] = line.replace("GENEL DEĞERLENDİRME:", "").strip()
                
            elif line.startswith("GÜÇLÜ YÖNLER:"):
                strengths = line.replace("GÜÇLÜ YÖNLER:", "").strip()
                result["strengths"] = [s.strip() for s in strengths.split(",") if s.strip()]
                
            elif line.startswith("GELİŞTİRİLECEK NOKTALAR:"):
                improvements = line.replace("GELİŞTİRİLECEK NOKTALAR:", "").strip()
                result["improvements"] = [i.strip() for i in improvements.split(",") if i.strip()]
        
        return result
    
    async def parse_cv(self, cv_text: str) -> Dict[str, Any]:
        """
        CV metnini parse et ve yapılandırılmış veri çıkar.
        
        Args:
            cv_text: CV'nin metin içeriği
            
        Returns:
            {
                "name": "Ad Soyad",
                "email": "email@example.com",
                "phone": "telefon",
                "skills": ["Python", "FastAPI", ...],
                "experience": [...],
                "education": [...],
                "summary": "Özet"
            }
        """
        system_prompt = """Sen bir CV analiz uzmanısın.
Verilen CV metnini analiz et ve yapılandırılmış bilgi çıkar.

CEVAP FORMATINI AYNEN UYGULA (JSON):
{
    "name": "Ad Soyad",
    "email": "email veya null",
    "phone": "telefon veya null",
    "skills": ["skill1", "skill2", ...],
    "experience_years": sayı,
    "current_title": "mevcut pozisyon veya null",
    "education": "en yüksek eğitim veya null",
    "summary": "1-2 cümle profesyonel özet"
}

SADECE JSON DÖNDÜR, başka açıklama yapma."""

        response = await self.chat(
            message=f"Bu CV'yi analiz et:\n\n{cv_text}",
            system_prompt=system_prompt,
            temperature=0.2,  # Tutarlılık için düşük
            max_tokens=1000,
        )
        
        # JSON parse etmeye çalış
        import json
        try:
            # Bazen LLM markdown code block içinde döndürüyor
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                response = response.split("```")[1].split("```")[0]
            
            return json.loads(response.strip())
        except:
            # Parse başarısız olursa basit bir dict döndür
            return {
                "name": None,
                "email": None,
                "skills": [],
                "summary": response[:200],
                "parse_error": True,
            }


# Singleton instance
llm_service = LLMService()

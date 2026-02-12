"""
KariyerKoçu - CV Service
========================
CV işleme servisi.

- PDF'den metin çıkarma (PyMuPDF + PyPDF2 fallback)
- LLM ile parse etme
- Veritabanına kaydetme
"""

import io
from typing import Optional, Dict, Any

from app.services.llm_service import llm_service


class CVService:
    """
    CV işleme servisi.
    
    AKIŞ:
    1. PDF dosyası alınır
    2. PyMuPDF ile metin çıkarılır (fallback: PyPDF2)
    3. LLM'e gönderilir, yapılandırılmış veri alınır
    4. Veritabanına kaydedilir
    """
    
    async def extract_text_from_pdf(self, file_content: bytes) -> str:
        """
        PDF dosyasından metin çıkar.
        Önce PyMuPDF dener, başarısız olursa PyPDF2'ye düşer.
        
        Args:
            file_content: PDF dosyasının binary içeriği
            
        Returns:
            Çıkarılan metin
        """
        text = ""
        
        # 1. PyMuPDF ile dene (daha iyi metin çıkarma)
        try:
            import fitz  # PyMuPDF
            
            doc = fitz.open(stream=file_content, filetype="pdf")
            text_parts = []
            
            for page in doc:
                # Metin bloklarını layout bilgisiyle al
                blocks = page.get_text("blocks")
                sorted_blocks = sorted(blocks, key=lambda b: (b[1], b[0]))
                
                for block in sorted_blocks:
                    if block[6] == 0:  # Text block
                        block_text = block[4].strip()
                        if block_text:
                            text_parts.append(block_text)
            
            doc.close()
            text = "\n".join(text_parts)
            
            if len(text.strip()) > 100:
                print("[CV SERVICE] PyMuPDF ile metin çıkarıldı")
                return text.strip().replace("\x00", "")
                
        except Exception as e:
            print(f"[CV SERVICE] PyMuPDF hatası, PyPDF2'ye geçiliyor: {e}")
        
        # 2. PyPDF2 ile dene (fallback)
        try:
            from PyPDF2 import PdfReader
            
            pdf_file = io.BytesIO(file_content)
            reader = PdfReader(pdf_file)
            
            text_parts = []
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
            
            text = "\n\n".join(text_parts)
            print("[CV SERVICE] PyPDF2 ile metin çıkarıldı")
            return text.strip().replace("\x00", "")
            
        except Exception as e:
            raise Exception(f"PDF okuma hatası: {str(e)}")
    
    async def parse_cv_with_llm(self, cv_text: str, retry_count: int = 0) -> Dict[str, Any]:
        """
        CV metnini LLM ile parse et.
        
        Args:
            cv_text: CV'nin metin içeriği
            retry_count: Tekrar deneme sayısı (max 2)
            
        Returns:
            Yapılandırılmış CV verisi (dict)
        """
        
        # Daha basit ve net prompt - tek satırda JSON şeması
        system_prompt = """Sen CV analiz uzmanısın (Türk İK personeli). CV İngilizce olsa bile TÜRKÇE olarak analiz et ve JSON'a çevir.

JSON FORMATI:
{"full_name":"isim","title":"unvan","email":"email","phone":"tel","linkedin":"url","github":"url","summary":"özet","skills":["skill1"],"experience":[{"title":"pozisyon","company":"şirket","duration":"süre","description":"açıklama"}],"education":[{"degree":"derece","field":"bölüm","school":"okul","start_year":2020,"end_year":2024,"gpa":"AGNO/GPA değeri"}],"projects":[{"name":"proje","technologies":["tech"],"description":"açıklama"}],"languages":{"dil":"seviye"},"certifications":["sertifika"],"experience_years":"süre"}

KURALLAR: 
1. Sadece JSON döndür. 
2. GPA/AGNO varsa education.gpa'ya yaz. 
3. Null kullanabilirsin (özellikle şirket adı yoksa company: null yap).
4. Tarihleri/Süreleri Türkçe'ye çevir (örn: '1 year' -> '1 yıl').
5. Unvanları mümkünse Türkçe karşılığıyla yaz (örn: 'Intern' -> 'Stajyer'), değilse orijinal kalsın."""

        user_message = f"""CV metni:

{cv_text[:5000]}

JSON:"""

        try:
            response = await llm_service.chat(
                message=user_message,
                system_prompt=system_prompt,
                temperature=0.1,
                max_tokens=3000,
            )
            
            # Boş response kontrolü
            if not response or not response.strip():
                print(f"⚠️ Boş LLM cevabı, tekrar deneniyor... ({retry_count + 1}/5)")
                if retry_count < 5:
                    import asyncio
                    await asyncio.sleep(2)  # 2 saniye bekle
                    return await self.parse_cv_with_llm(cv_text, retry_count + 1)
                else:
                    # 5 deneme sonra bile boşsa fallback
                    print("⚠️ LLM 5 kez boş cevap verdi, fallback'e geçiliyor")
                    return self._parse_cv_fallback(cv_text)
            
            # JSON parse et
            result = self._parse_json_response(response)
            
            # Hata varsa tekrar dene
            if result.get("parse_error"):
                if retry_count < 5:
                    print(f"JSON parse hatası, tekrar deneniyor... ({retry_count + 1}/5)")
                    import asyncio
                    await asyncio.sleep(2)
                    return await self.parse_cv_with_llm(cv_text, retry_count + 1)
                else:
                    print("⚠️ JSON parse 5 kez başarısız, fallback'e geçiliyor")
                    return self._parse_cv_fallback(cv_text)
            
            return result
            
        except Exception as e:
            print(f"⚠️ CV parse exception: {str(e)}")
            if retry_count < 5:
                import asyncio
                await asyncio.sleep(2)
                return await self.parse_cv_with_llm(cv_text, retry_count + 1)
            
            # 5 deneme sonra bile hata varsa fallback
            print("⚠️ LLM parsing failed after 5 attempts, using fallback parser.")
            return self._parse_cv_fallback(cv_text)

    def _parse_cv_fallback(self, cv_text: str) -> Dict[str, Any]:
        """
        LLM başarısız olduğunda regex ile basit veri çıkarma.
        """
        import re
        
        # Email bul
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', cv_text)
        email = email_match.group(0) if email_match else None
        
        # Telefon bul (çeşitli formatlar)
        phone_patterns = [
            r'(\+90|0)?\s*[5][0-9]{2}\s*[0-9]{3}\s*[0-9]{2}\s*[0-9]{2}',
            r'(\+90|0)?\s*\([0-9]{3}\)\s*[0-9]{3}[\s-]?[0-9]{2}[\s-]?[0-9]{2}',
            r'[0-9]{3}[\s.-][0-9]{3}[\s.-][0-9]{4}'
        ]
        phone = None
        for pattern in phone_patterns:
            phone_match = re.search(pattern, cv_text)
            if phone_match:
                phone = phone_match.group(0)
                break
        
        # LinkedIn bul
        linkedin_match = re.search(r'linkedin\.com/in/[\w-]+', cv_text, re.IGNORECASE)
        linkedin = f"https://www.{linkedin_match.group(0)}" if linkedin_match else None
        
        # GitHub bul
        github_match = re.search(r'github\.com/[\w-]+', cv_text, re.IGNORECASE)
        github = f"https://{github_match.group(0)}" if github_match else None
        
        # İsim tahmini (ilk satır genelde isimdir)
        lines = [line.strip() for line in cv_text.split('\n') if line.strip()]
        full_name = lines[0] if lines else "Bilinmiyor"
        
        # Eğer ilk satır email/telefon ise, diğer satırlara bak
        if email and full_name == email:
            full_name = lines[1] if len(lines) > 1 else "Bilinmiyor"
        if phone and phone in full_name:
            full_name = lines[1] if len(lines) > 1 else "Bilinmiyor"
        
        # Skills tahmini (yaygın teknolojileri ara)
        common_skills = [
            "Python", "Java", "JavaScript", "TypeScript", "C#", "C++", "React", 
            "Angular", "Vue", "Node.js", "Django", "Flask", "FastAPI", "Spring",
            "SQL", "PostgreSQL", "MySQL", "MongoDB", "Docker", "Kubernetes",
            "AWS", "Azure", "Git", "Linux", "TensorFlow", "PyTorch", "Machine Learning"
        ]
        found_skills = []
        for skill in common_skills:
            if re.search(rf'\b{skill}\b', cv_text, re.IGNORECASE):
                found_skills.append(skill)
        
        if not found_skills:
            found_skills = ["Yazılım Geliştirme"]
        
        return {
            "full_name": full_name,
            "title": "Belirtilmemiş",
            "email": email,
            "phone": phone,
            "linkedin": linkedin,
            "github": github,
            "summary": cv_text[:500] if len(cv_text) > 0 else "İçerik çıkarılamadı",
            "skills": found_skills,
            "experience": [],
            "education": [],
            "projects": [],
            "languages": {},
            "certifications": [],
            "experience_years": "0",
            "parse_error": False,  # Fallback başarılı kabul edilir
            "is_fallback": True
        }
    
    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """
        LLM response'unu JSON'a parse et.
        
        LLM bazen markdown code block içinde döndürüyor,
        bu fonksiyon bunu temizler.
        """
        import json
        import re
        
        if not response or not response.strip():
            return {
                "parse_error": True,
                "error_message": "Boş response",
                "raw_response": ""
            }
        
        # Temizle
        cleaned = response.strip()
        
        # Markdown code block varsa çıkar
        if "```json" in cleaned:
            cleaned = cleaned.split("```json")[1].split("```")[0]
        elif "```" in cleaned:
            parts = cleaned.split("```")
            if len(parts) >= 2:
                cleaned = parts[1]
        
        cleaned = cleaned.strip()
        
        # JSON objesi bulmaya çalış (ilk { ile son } arasını al)
        if not cleaned.startswith("{"):
            match = re.search(r'\{[\s\S]*\}', cleaned)
            if match:
                cleaned = match.group(0)
        
        # Trailing comma temizle (JSON'da geçersiz)
        cleaned = re.sub(r',\s*}', '}', cleaned)
        cleaned = re.sub(r',\s*]', ']', cleaned)
        
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            # Parse başarısız - raw_response'u logla
            print(f"❌ JSON Parse Error: {str(e)}")
            print(f"❌ Raw response (first 300 chars): {response[:300]}")
            return {
                "parse_error": True,
                "error_message": f"JSON parse hatası: {str(e)}",
                "raw_response": response[:500]
            }
    
    def calculate_experience_summary(self, experience: list) -> str:
        """
        Toplam deneyim süresini hesapla.
        
        Basit bir hesaplama - tam tarih parsing yapmadan.
        """
        if not experience:
            return "Yeni mezun / Deneyimsiz"
        
        total_months = 0
        
        for exp in experience:
            duration = exp.get("duration", "")
            
            # "1 yıl 6 ay" gibi formatları parse et
            if "yıl" in duration.lower():
                try:
                    parts = duration.lower().split("yıl")
                    years = int(parts[0].strip())
                    total_months += years * 12
                    
                    if len(parts) > 1 and "ay" in parts[1]:
                        months = int(parts[1].replace("ay", "").strip())
                        total_months += months
                except:
                    pass
            elif "ay" in duration.lower():
                try:
                    months = int(duration.lower().replace("ay", "").strip())
                    total_months += months
                except:
                    pass
        
        if total_months == 0:
            return f"{len(experience)} pozisyon"
        
        years = total_months // 12
        months = total_months % 12
        
        if years > 0 and months > 0:
            return f"{years} yıl {months} ay"
        elif years > 0:
            return f"{years} yıl"
        else:
            return f"{months} ay"


# Singleton instance
cv_service = CVService()

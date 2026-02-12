# -*- coding: utf-8 -*-
"""
ATS Simülasyonu Servisi - Gelişmiş Versiyon
============================================
CV'yi "gerçek ATS sistemleri gibi" okumaya çalışarak
potansiyel sorunları tespit eder.

3 Farklı PDF Okuyucu Kullanır:
1. PyMuPDF (fitz) - En güçlü, layout bilgisi de çıkarır
2. pdfminer.six - Alternatif, farklı PDF yapıları için
3. PyPDF2 - Fallback, en basit

Bu sayede şirketlerin kullandığı farklı ATS sistemlerini simüle ederiz.
"""

import re
from typing import Dict, List, Optional
from io import BytesIO
from dataclasses import dataclass
from enum import Enum


class PDFReaderType(Enum):
    PYMUPDF = "PyMuPDF"
    PDFMINER = "pdfminer"
    PYPDF2 = "PyPDF2"


@dataclass
class PDFExtractionResult:
    """PDF'den çıkarılan metin sonucu."""
    success: bool
    text: str
    reader_used: str
    page_count: int
    metadata: Dict
    error: Optional[str] = None


class AdvancedPDFReader:
    """
    Birden fazla PDF okuyucu ile metin çıkarma.
    Her okuyucu farklı ATS sistemlerini temsil eder.
    """
    
    @staticmethod
    def read_with_pymupdf(pdf_bytes: bytes) -> PDFExtractionResult:
        """
        PyMuPDF (fitz) ile oku - En güçlü okuyucu.
        Workday, Greenhouse gibi modern ATS'leri simüle eder.
        """
        try:
            import fitz  # PyMuPDF
            
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            text_parts = []
            page_count = len(doc)
            
            for page in doc:
                # Metin bloklarını al (layout bilgisiyle)
                blocks = page.get_text("blocks")
                
                # Blokları y koordinatına göre sırala (yukarıdan aşağı okuma)
                sorted_blocks = sorted(blocks, key=lambda b: (b[1], b[0]))
                
                for block in sorted_blocks:
                    if block[6] == 0:  # Text block (not image)
                        text = block[4].strip()
                        if text:
                            text_parts.append(text)
            
            full_text = "\n".join(text_parts)
            
            metadata = {
                "title": doc.metadata.get("title", "") if doc.metadata else "",
                "author": doc.metadata.get("author", "") if doc.metadata else "",
                "creator": doc.metadata.get("creator", "") if doc.metadata else "",
                "producer": doc.metadata.get("producer", "") if doc.metadata else "",
            }
            
            doc.close()
            
            return PDFExtractionResult(
                success=True,
                text=full_text,
                reader_used="PyMuPDF",
                page_count=page_count,
                metadata=metadata
            )
            
        except Exception as e:
            return PDFExtractionResult(
                success=False,
                text="",
                reader_used="PyMuPDF",
                page_count=0,
                metadata={},
                error=str(e)
            )
    
    @staticmethod
    def read_with_pdfminer(pdf_bytes: bytes) -> PDFExtractionResult:
        """
        pdfminer.six ile oku - Detaylı metin analizi.
        Oracle Taleo, SAP SuccessFactors gibi kurumsal ATS'leri simüle eder.
        """
        try:
            from pdfminer.high_level import extract_text, extract_pages
            
            pdf_file = BytesIO(pdf_bytes)
            
            # Metin çıkar
            text = extract_text(pdf_file)
            
            # Sayfa sayısını al
            pdf_file.seek(0)
            pages = list(extract_pages(pdf_file))
            page_count = len(pages)
            
            return PDFExtractionResult(
                success=True,
                text=text.strip(),
                reader_used="pdfminer",
                page_count=page_count,
                metadata={}
            )
            
        except Exception as e:
            return PDFExtractionResult(
                success=False,
                text="",
                reader_used="pdfminer",
                page_count=0,
                metadata={},
                error=str(e)
            )
    
    @staticmethod
    def read_with_pypdf2(pdf_bytes: bytes) -> PDFExtractionResult:
        """
        PyPDF2 ile oku - Basit okuyucu.
        Eski veya basit ATS sistemlerini simüle eder.
        """
        try:
            from PyPDF2 import PdfReader
            
            pdf_file = BytesIO(pdf_bytes)
            reader = PdfReader(pdf_file)
            
            text_parts = []
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
            
            full_text = "\n\n".join(text_parts)
            
            metadata = {
                "title": reader.metadata.title if reader.metadata else "",
                "author": reader.metadata.author if reader.metadata else "",
            }
            
            return PDFExtractionResult(
                success=True,
                text=full_text.strip(),
                reader_used="PyPDF2",
                page_count=len(reader.pages),
                metadata=metadata
            )
            
        except Exception as e:
            return PDFExtractionResult(
                success=False,
                text="",
                reader_used="PyPDF2",
                page_count=0,
                metadata={},
                error=str(e)
            )
    
    @classmethod
    def read_pdf(cls, pdf_bytes: bytes, preferred_reader: PDFReaderType = PDFReaderType.PYMUPDF) -> PDFExtractionResult:
        """
        PDF'i oku, başarısız olursa diğer okuyucuları dene.
        """
        readers = {
            PDFReaderType.PYMUPDF: cls.read_with_pymupdf,
            PDFReaderType.PDFMINER: cls.read_with_pdfminer,
            PDFReaderType.PYPDF2: cls.read_with_pypdf2,
        }
        
        # Tercih edilen okuyucuyla başla
        result = readers[preferred_reader](pdf_bytes)
        if result.success and len(result.text.strip()) > 50:
            return result
        
        # Başarısızsa diğerlerini dene
        for reader_type, reader_func in readers.items():
            if reader_type != preferred_reader:
                result = reader_func(pdf_bytes)
                if result.success and len(result.text.strip()) > 50:
                    return result
        
        # Hiçbiri çalışmadıysa son denemeyi döndür
        return result
    
    @classmethod
    def read_with_all(cls, pdf_bytes: bytes) -> Dict[str, PDFExtractionResult]:
        """
        Tüm okuyucularla oku ve karşılaştır (ATS simülasyonu için).
        """
        return {
            "pymupdf": cls.read_with_pymupdf(pdf_bytes),
            "pdfminer": cls.read_with_pdfminer(pdf_bytes),
            "pypdf2": cls.read_with_pypdf2(pdf_bytes),
        }


class ATSSimulationService:
    """
    Gelişmiş ATS (Applicant Tracking System) Simülasyonu.
    
    3 farklı PDF okuyucu ile CV'yi okur ve şunları analiz eder:
    - Her okuyucunun okuduğu metin tutarlılığı
    - İkon ve özel karakter sorunları
    - Sütun kayması ve formatlama problemleri
    - İletişim bilgisi okunabilirliği
    - ATS uyumluluk skoru
    """
    
    # Problemli karakterler ve eşleşmeleri
    ICON_PATTERNS = {
        "☎": "telefon ikonu",
        "📧": "email ikonu", 
        "✉": "zarf ikonu",
        "📱": "mobil ikonu",
        "🔗": "link ikonu",
        "📍": "konum ikonu",
        "💼": "çanta ikonu",
        "🎓": "mezuniyet ikonu",
        "⭐": "yıldız ikonu",
        "●": "madde işareti",
        "◆": "kare işareti",
        "►": "ok işareti",
        "✓": "tik işareti",
        "✔": "tik işareti",
        "→": "ok",
        "•": "nokta",
        "○": "daire",
        "■": "kare",
        "□": "boş kare",
        "▪": "küçük kare",
        "✦": "yıldız",
        "★": "dolu yıldız",
        "➤": "sağ ok",
        "➜": "kalın ok",
        "✧": "açık yıldız",
        "◉": "dolu daire",
        "◎": "çift daire",
        "⬤": "büyük daire",
        "🌐": "dünya ikonu",
        "💻": "bilgisayar ikonu",
        "📞": "telefon ikonu",
        "✅": "onay ikonu",
        "❌": "çarpı ikonu",
        "⚡": "şimşek ikonu",
    }
    
    # E-posta ve telefon regex'leri
    EMAIL_PATTERN = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
    # Telefon pattern - Türkiye ve uluslararası formatları destekler
    # +90 551 699 0655, +90 (551) 699 06 55, 0551 699 0655, 551-699-0655 vb.
    PHONE_PATTERN = re.compile(
        r'(?:\+?90[\s.-]?)?'  # Ülke kodu (opsiyonel)
        r'(?:\(?\d{3}\)?[\s.-]?)'  # Alan kodu (3 hane)
        r'(?:\d{3}[\s.-]?)'  # İlk 3 hane
        r'(?:\d{2}[\s.-]?\d{2}|\d{4})'  # Son 4 hane (XX XX veya XXXX)
    )
    
    # LinkedIn ve GitHub pattern'leri
    LINKEDIN_PATTERN = re.compile(r'linkedin\.com/in/[\w-]+', re.IGNORECASE)
    GITHUB_PATTERN = re.compile(r'github\.com/[\w-]+', re.IGNORECASE)
    
    def __init__(self):
        self.pdf_reader = AdvancedPDFReader()
    
    def simulate_ats_read(self, pdf_bytes: bytes, run_all_readers: bool = True) -> Dict:
        """
        PDF'i farklı ATS sistemleri gibi oku ve analiz et.
        
        Args:
            pdf_bytes: PDF dosyasının binary içeriği
            run_all_readers: Tüm okuyucularla mı test edilsin?
            
        Returns:
            Kapsamlı ATS analiz raporu
        """
        try:
            # Tüm okuyucularla oku
            if run_all_readers:
                all_results = self.pdf_reader.read_with_all(pdf_bytes)
                
                # En iyi sonucu seç (en fazla kelime)
                best_result = max(
                    all_results.values(),
                    key=lambda r: len(r.text.split()) if r.success else 0
                )
                
                # Tutarsızlık analizi yap
                consistency_analysis = self._analyze_reader_consistency(all_results)
            else:
                best_result = self.pdf_reader.read_pdf(pdf_bytes)
                consistency_analysis = None
                all_results = None
            
            if not best_result.success or not best_result.text.strip():
                return self._create_error_response("PDF okunamadı veya metin çıkarılamadı")
            
            raw_text = best_result.text
            cleaned_text = self._clean_text(raw_text)
            
            # Tüm sorunları tespit et
            all_issues = []
            all_issues.extend(self._detect_icon_issues(raw_text))
            all_issues.extend(self._detect_spacing_issues(raw_text))
            all_issues.extend(self._detect_contact_issues(raw_text))
            all_issues.extend(self._detect_formatting_issues(raw_text))
            all_issues.extend(self._detect_layout_issues(raw_text))
            
            # Tutarsızlık sorunları ekle
            if consistency_analysis and consistency_analysis.get("has_inconsistency"):
                all_issues.extend(consistency_analysis.get("issues", []))
            
            # ATS skoru hesapla
            score = self._calculate_ats_score(all_issues)
            
            # Öneriler oluştur
            recommendations = self._generate_recommendations(all_issues, score)
            
            # İstatistikler
            stats = {
                "total_characters": len(raw_text),
                "total_words": len(raw_text.split()),
                "total_lines": len(raw_text.splitlines()),
                "total_pages": best_result.page_count,
                "issues_count": len(all_issues),
                "high_severity_count": len([i for i in all_issues if i.get("severity") == "high"]),
                "medium_severity_count": len([i for i in all_issues if i.get("severity") == "medium"]),
                "low_severity_count": len([i for i in all_issues if i.get("severity") == "low"]),
                "reader_used": best_result.reader_used,
            }
            
            # Sorunlu metinleri topla (highlight için)
            problematic_texts = self._extract_problematic_texts(raw_text)
            
            # Reader karşılaştırması
            reader_comparison = None
            if all_results:
                reader_comparison = {
                    reader: {
                        "success": result.success,
                        "word_count": len(result.text.split()) if result.success else 0,
                        "char_count": len(result.text) if result.success else 0,
                    }
                    for reader, result in all_results.items()
                }
            
            return {
                "success": True,
                "raw_text": raw_text,
                "cleaned_text": cleaned_text,
                "issues": all_issues,
                "score": score,
                "score_label": self._get_score_label(score),
                "recommendations": recommendations,
                "stats": stats,
                "problematic_texts": problematic_texts,
                "reader_comparison": reader_comparison,
                "consistency_analysis": consistency_analysis,
                "metadata": best_result.metadata,
            }
            
        except Exception as e:
            return self._create_error_response(f"ATS analizi sırasında hata: {str(e)}")
    
    def _analyze_reader_consistency(self, results: Dict[str, PDFExtractionResult]) -> Dict:
        """
        Farklı okuyucuların sonuçlarını karşılaştır.
        Tutarsızlık = CV'nin ATS'lerde farklı okunacağı anlamına gelir.
        """
        successful_results = {
            k: v for k, v in results.items() 
            if v.success and len(v.text.strip()) > 50
        }
        
        if len(successful_results) < 2:
            return {"has_inconsistency": False, "issues": []}
        
        # Kelime sayılarını karşılaştır
        word_counts = {k: len(v.text.split()) for k, v in successful_results.items()}
        max_words = max(word_counts.values())
        min_words = min(word_counts.values())
        
        issues = []
        
        # %30'dan fazla fark varsa tutarsızlık var
        if max_words > 0 and (max_words - min_words) / max_words > 0.3:
            best_reader = max(word_counts, key=word_counts.get)
            worst_reader = min(word_counts, key=word_counts.get)
            
            issues.append({
                "type": "reader_inconsistency",
                "severity": "high",
                "title": "ATS Tutarsızlığı Tespit Edildi",
                "description": f"CV'niz farklı ATS sistemlerinde farklı okunuyor! {best_reader} {max_words} kelime okurken, {worst_reader} sadece {min_words} kelime okuyor.",
                "affected_text": f"{best_reader}: {max_words} kelime, {worst_reader}: {min_words} kelime",
                "fix": "CV'nizi daha basit bir formatta kaydedin. Word'den 'PDF olarak kaydet' seçeneğini kullanın.",
                "count": abs(max_words - min_words)
            })
        
        # E-posta ve telefon tutarlılığını kontrol et
        email_found = {}
        phone_found = {}
        
        for reader, result in successful_results.items():
            email_found[reader] = bool(self.EMAIL_PATTERN.search(result.text))
            phone_found[reader] = bool(self.PHONE_PATTERN.search(result.text))
        
        if len(set(email_found.values())) > 1:
            issues.append({
                "type": "email_inconsistency",
                "severity": "high",
                "title": "E-posta Okunabilirlik Sorunu",
                "description": "E-posta adresiniz bazı ATS sistemlerinde okunamıyor!",
                "affected_text": f"Okuyabilen: {[k for k,v in email_found.items() if v]}, Okuyamayan: {[k for k,v in email_found.items() if not v]}",
                "fix": "E-posta adresinizi düz metin olarak yazın, tıklanabilir link yapmayın.",
                "count": 1
            })
        
        if len(set(phone_found.values())) > 1:
            issues.append({
                "type": "phone_inconsistency",
                "severity": "high",
                "title": "Telefon Okunabilirlik Sorunu",
                "description": "Telefon numaranız bazı ATS sistemlerinde okunamıyor!",
                "affected_text": f"Okuyabilen: {[k for k,v in phone_found.items() if v]}, Okuyamayan: {[k for k,v in phone_found.items() if not v]}",
                "fix": "Telefon numaranızı düz metin olarak yazın: +90 5XX XXX XX XX",
                "count": 1
            })
        
        return {
            "has_inconsistency": len(issues) > 0,
            "issues": issues,
            "word_counts": word_counts,
            "email_consistency": email_found,
            "phone_consistency": phone_found,
        }
    
    def _clean_text(self, text: str) -> str:
        """Metni temizle ve okunabilir hale getir."""
        cleaned = re.sub(r'\s+', ' ', text)
        cleaned = re.sub(r'\n\s*\n', '\n\n', text)
        return cleaned.strip()
    
    def _identify_sections(self, text: str) -> Dict[str, int]:
        """CV'deki bölümleri ve pozisyonlarını bul."""
        section_keywords = {
            "Özet": ["özet", "hakkımda", "about", "summary", "profil", "profile"],
            "Deneyim": ["deneyim", "experience", "iş deneyimi", "work experience", "work history"],
            "Eğitim": ["eğitim", "education", "üniversite", "okul", "academic"],
            "Yetenekler": ["yetenekler", "skills", "beceriler", "teknolojiler", "technical skills"],
            "Projeler": ["projeler", "projects", "proje", "portfolio"],
            "Sertifikalar": ["sertifika", "certificates", "certifications", "credentials"],
            "Diller": ["diller", "languages", "yabancı dil", "language skills"],
            "İletişim": ["iletişim", "contact", "telefon", "email", "contact information"]
        }
        
        sections = {}
        text_lower = text.lower()
        
        for section_name, keywords in section_keywords.items():
            for keyword in keywords:
                pos = text_lower.find(keyword)
                if pos != -1:
                    sections[section_name] = pos
                    break
        
        return sections
    
    def _detect_icon_issues(self, text: str) -> List[Dict]:
        """İkon kullanımı sorunlarını tespit et."""
        issues = []
        sections = self._identify_sections(text)
        
        found_icons = []
        icon_locations = set()
        
        for icon, description in self.ICON_PATTERNS.items():
            count = text.count(icon)
            if count > 0:
                found_icons.append(f"{icon} ({description})")
                pos = text.find(icon)
                section = self._get_section_at_position(pos, sections)
                if section:
                    icon_locations.add(section)
        
        if found_icons:
            location = ", ".join(icon_locations) + " bölümü" if icon_locations else "İletişim bilgileri"
            issues.append({
                "type": "icons",
                "severity": "high",
                "title": "İkon/Sembol Kullanımı Tespit Edildi",
                "description": f"CV'nizde {len(found_icons)} farklı ikon/sembol kullanılmış. ATS sistemleri bunları OKUYAMAZ! Bu ikonlar yerine metin kullanmalısınız.",
                "affected_text": ", ".join(found_icons[:10]),
                "location": location,
                "fix": "İkonları düz metin ile değiştirin. Örn: '☎' → 'Tel:', '✉' → 'E-posta:', '📍' → 'Konum:'",
                "count": len(found_icons),
                "icon_list": found_icons
            })
        
        return issues
    
    def _get_section_at_position(self, pos: int, sections: Dict[str, int]) -> str:
        """Belirli bir pozisyonun hangi bölümde olduğunu bul."""
        if not sections:
            return ""
        
        sorted_sections = sorted(sections.items(), key=lambda x: x[1])
        current_section = ""
        
        for section_name, section_pos in sorted_sections:
            if pos >= section_pos:
                current_section = section_name
            else:
                break
        
        return current_section
    
    def _detect_spacing_issues(self, text: str) -> List[Dict]:
        """Boşluk ve kayma sorunlarını tespit et."""
        issues = []
        
        # Kelimeler arasında fazla boşluk var mı?
        multiple_spaces = re.findall(r'(\S+\s{3,}\S+)', text)
        if len(multiple_spaces) > 5:
            issues.append({
                "type": "spacing",
                "severity": "medium",
                "title": "Anormal Boşluklar Tespit Edildi",
                "description": f"Kelimeler arasında anormal boşluklar var ({len(multiple_spaces)} adet). Bu genellikle çok sütunlu tasarımlardan veya tablo kullanımından kaynaklanır.",
                "affected_text": " | ".join(multiple_spaces[:3]),
                "location": "Genel",
                "fix": "CV'nizi tek sütunlu düzene çevirin. Word'de 'Sayfa Düzeni > Sütunlar > Bir' seçin. Tablo kullanmaktan kaçının.",
                "count": len(multiple_spaces)
            })
        
        # Harfler bölünmüş mü?
        split_words = re.findall(r'([A-Za-zğüşıöçĞÜŞİÖÇ]\s[A-Za-zğüşıöçĞÜŞİÖÇ]\s[A-Za-zğüşıöçĞÜŞİÖÇ](?:\s[A-Za-zğüşıöçĞÜŞİÖÇ])*)', text)
        if len(split_words) > 2:
            readable_splits = [sw.replace(" ", "") for sw in split_words[:5]]
            issues.append({
                "type": "split_text",
                "severity": "high",
                "title": "Bölünmüş Kelimeler Tespit Edildi",
                "description": f"'{readable_splits[0]}' gibi kelimeler harf harf ayrılmış görünüyor. ATS bu kelimeleri tanıyamaz!",
                "affected_text": " → ".join([f"'{sw}' ({''.join(sw.split())})" for sw in split_words[:3]]),
                "location": "Başlıklar veya İçerik",
                "fix": "Bu kelimeler grafik olarak yazılmış olabilir. Düz metin kullanın, özel font efektlerinden (letter-spacing) kaçının.",
                "count": len(split_words)
            })
        
        return issues
    
    def _detect_contact_issues(self, text: str) -> List[Dict]:
        """İletişim bilgisi okunabilirlik sorunlarını tespit et."""
        issues = []
        
        # E-posta bulunuyor mu?
        emails = self.EMAIL_PATTERN.findall(text)
        if not emails:
            issues.append({
                "type": "missing_email",
                "severity": "high",
                "title": "E-posta Adresi Bulunamadı",
                "description": "ATS sistemi CV'nizde e-posta adresi tespit edemedi. Bu kritik bir sorun - işverenler size ulaşamaz!",
                "affected_text": "",
                "fix": "E-posta adresinizi düz metin olarak yazın: ornek@email.com",
                "count": 0
            })
        else:
            for email in emails:
                if ' ' in email:
                    issues.append({
                        "type": "broken_email",
                        "severity": "high",
                        "title": "Bozuk E-posta Formatı",
                        "description": f"E-posta adresi düzgün okunamıyor: {email}",
                        "affected_text": email,
                        "fix": "E-posta adresinizi boşluksuz, düz metin olarak yazın.",
                        "count": 1
                    })
        
        # Telefon bulunuyor mu?
        phones = self.PHONE_PATTERN.findall(text)
        valid_phones = [p for p in phones if len(re.sub(r'\D', '', p)) >= 10]
        
        if not valid_phones:
            issues.append({
                "type": "missing_phone",
                "severity": "medium",
                "title": "Telefon Numarası Bulunamadı",
                "description": "ATS sistemi CV'nizde geçerli bir telefon numarası tespit edemedi.",
                "affected_text": "",
                "fix": "Telefon numaranızı ekleyin: +90 5XX XXX XX XX",
                "count": 0
            })
        
        # LinkedIn bulunuyor mu?
        linkedin = self.LINKEDIN_PATTERN.search(text)
        if not linkedin:
            issues.append({
                "type": "missing_linkedin",
                "severity": "low",
                "title": "LinkedIn Profili Bulunamadı",
                "description": "LinkedIn profilinizi eklemek profesyonel görünüm sağlar.",
                "affected_text": "",
                "fix": "LinkedIn URL'nizi ekleyin: linkedin.com/in/kullanici-adiniz",
                "count": 0
            })
        
        return issues
    
    def _detect_formatting_issues(self, text: str) -> List[Dict]:
        """Genel formatlama sorunlarını tespit et."""
        issues = []
        
        word_count = len(text.split())
        if word_count < 100:
            issues.append({
                "type": "too_short",
                "severity": "high",
                "title": "Çok Az İçerik Okunabildi",
                "description": f"CV'den sadece {word_count} kelime çıkarılabildi. Bu, CV'nizin büyük bölümünün görsel/grafik olduğunu ve ATS tarafından okunamadığını gösterir.",
                "affected_text": "",
                "fix": "CV'nizi metin tabanlı olarak yeniden tasarlayın. Görsel ağırlıklı template'lerden kaçının.",
                "count": word_count
            })
        elif word_count < 200:
            issues.append({
                "type": "short_content",
                "severity": "medium",
                "title": "Az İçerik",
                "description": f"CV'den {word_count} kelime okundu. Deneyimli adaylar için bu düşük olabilir.",
                "affected_text": "",
                "fix": "Deneyim ve yeteneklerinizi daha detaylı açıklayın.",
                "count": word_count
            })
        
        # Tarih formatları
        date_patterns = re.findall(
            r'\b(19|20)\d{2}\s*[-–—]\s*(19|20)?\d{0,4}\b|\b(Ocak|Şubat|Mart|Nisan|Mayıs|Haziran|Temmuz|Ağustos|Eylül|Ekim|Kasım|Aralık|January|February|March|April|May|June|July|August|September|October|November|December)\s*(19|20)\d{2}\b',
            text, re.IGNORECASE
        )
        if not date_patterns and word_count > 100:
            issues.append({
                "type": "no_dates",
                "severity": "low",
                "title": "Tarih Bilgisi Bulunamadı",
                "description": "CV'de tarih formatında bilgi tespit edilemedi.",
                "affected_text": "",
                "fix": "Tarihlerinizi standart formatta yazın: '2022 - 2024' veya 'Ocak 2022 - Şubat 2024'",
                "count": 0
            })
        
        # Tekrarlayan karakterler
        repeated = re.findall(r'(.)\1{5,}', text)
        if repeated:
            issues.append({
                "type": "repeated_chars",
                "severity": "low",
                "title": "Tekrarlayan Karakterler",
                "description": "Ardışık tekrarlayan karakterler tespit edildi.",
                "affected_text": "".join(set(repeated))[:20],
                "fix": "Görsel ayırıcılar yerine boşluk veya başlık kullanın.",
                "count": len(repeated)
            })
        
        return issues
    
    def _detect_layout_issues(self, text: str) -> List[Dict]:
        """Düzen sorunlarını tespit et."""
        issues = []
        
        # Yapışık kelimeler
        stuck_words = re.findall(r'[a-zğüşıöç][A-ZĞÜŞİÖÇ][a-zğüşıöçA-ZĞÜŞİÖÇ]{4,}', text)
        if len(stuck_words) > 3:
            issues.append({
                "type": "stuck_words",
                "severity": "medium",
                "title": "Yapışık Kelimeler Tespit Edildi",
                "description": f"Bazı kelimeler birbirine yapışmış: {', '.join(stuck_words[:3])}",
                "affected_text": ", ".join(stuck_words[:5]),
                "fix": "CV'nizi tek sütunlu ve tablosuz tasarlayın.",
                "count": len(stuck_words)
            })
        
        # Çok uzun satırlar
        lines = text.split('\n')
        very_long_lines = [l for l in lines if len(l) > 200]
        if len(very_long_lines) > 3:
            issues.append({
                "type": "long_lines",
                "severity": "low",
                "title": "Çok Uzun Satırlar",
                "description": "Bazı satırlar çok uzun. Yan yana sütunların tek satırda okunmasından kaynaklanabilir.",
                "affected_text": very_long_lines[0][:100] + "..." if very_long_lines else "",
                "fix": "Tek sütunlu düzen kullanın.",
                "count": len(very_long_lines)
            })
        
        return issues
    
    def _calculate_ats_score(self, issues: List[Dict]) -> int:
        """ATS uyumluluk skoru hesapla (0-100)."""
        score = 100
        
        for issue in issues:
            severity = issue.get("severity", "low")
            issue_type = issue.get("type", "")
            count = issue.get("count", 1)
            
            if severity == "high":
                if issue_type == "reader_inconsistency":
                    score -= 25
                elif issue_type in ["missing_email", "broken_email"]:
                    score -= 20
                elif issue_type == "icons":
                    score -= min(15, 3 * min(count, 5))
                elif issue_type == "split_text":
                    score -= min(15, 5 * min(count, 3))
                elif issue_type == "too_short":
                    score -= 20
                else:
                    score -= 10
            elif severity == "medium":
                if issue_type == "spacing":
                    score -= min(10, count // 5)
                elif issue_type == "stuck_words":
                    score -= min(10, count * 2)
                else:
                    score -= 5
            else:
                score -= min(3, count)
        
        return max(0, min(100, score))
    
    def _get_score_label(self, score: int) -> str:
        """Skora göre etiket döndür."""
        if score >= 90:
            return "Mükemmel"
        elif score >= 75:
            return "İyi"
        elif score >= 60:
            return "Orta"
        elif score >= 40:
            return "Düşük"
        else:
            return "Kritik"
    
    def _generate_recommendations(self, issues: List[Dict], score: int) -> List[str]:
        """Sorunlara göre öneriler oluştur."""
        recommendations = []
        issue_types = {issue.get("type") for issue in issues}
        
        if "icons" in issue_types:
            recommendations.append("🔴 İkonlar yerine metin kullanın. '☎' yerine 'Tel:' veya 'Telefon:' yazın.")
        
        if "reader_inconsistency" in issue_types:
            recommendations.append("🔴 CV'niz farklı ATS'lerde farklı okunuyor. Daha basit bir tasarım kullanın.")
        
        if "missing_email" in issue_types or "broken_email" in issue_types:
            recommendations.append("🔴 E-posta adresinizi düz metin olarak yazın, hyperlink kullanmayın.")
        
        if "split_text" in issue_types:
            recommendations.append("🔴 Özel font efektleri (letter-spacing, özel fontlar) kullanmayın.")
        
        if "too_short" in issue_types:
            recommendations.append("🔴 CV'nizin çoğu grafik/görsel. Metin tabanlı içerik ekleyin.")
        
        if "spacing" in issue_types or "stuck_words" in issue_types:
            recommendations.append("🟡 Tek sütunlu, basit bir tasarıma geçin. Tablo ve çok sütunlu düzenlerden kaçının.")
        
        if "missing_phone" in issue_types:
            recommendations.append("🟡 Telefon numaranızı ekleyin: +90 5XX XXX XX XX")
        
        if "no_dates" in issue_types:
            recommendations.append("🟢 Tarihlerinizi standart formatta yazın: '2022 - 2024'")
        
        if "missing_linkedin" in issue_types:
            recommendations.append("🟢 LinkedIn profil linkinizi ekleyin.")
        
        if issues and score < 90:
            recommendations.append("💡 Microsoft Word'de hazırlayıp 'PDF olarak kaydet' seçeneği en güvenli yöntemdir.")
            recommendations.append("💡 Canva, Figma, Photoshop gibi grafik araçlarından kaçının.")
        
        if not recommendations:
            recommendations.append("✅ CV'niz ATS sistemleri için uyumlu görünüyor!")
        
        return recommendations
    
    def _extract_problematic_texts(self, text: str) -> List[str]:
        """Highlight için sorunlu metin parçalarını çıkar."""
        problematic = []
        
        split_words = re.findall(r'[A-Za-zğüşıöçĞÜŞİÖÇ]\s[A-Za-zğüşıöçĞÜŞİÖÇ](?:\s[A-Za-zğüşıöçĞÜŞİÖÇ])+', text)
        for word in split_words:
            if len(word) >= 5:
                problematic.append(word)
        
        stuck_words = re.findall(r'[a-zğüşıöç][A-ZĞÜŞİÖÇ][a-zğüşıöçA-ZĞÜŞİÖÇ]+', text)
        for word in stuck_words:
            if len(word) >= 6:
                problematic.append(word)
        
        for icon in self.ICON_PATTERNS.keys():
            if icon in text:
                problematic.append(icon)
        
        abnormal_spaces = re.findall(r'\S+\s{3,}\S+', text)
        for space in abnormal_spaces[:10]:
            problematic.append(space)
        
        return list(set(problematic))[:50]
    
    def _create_error_response(self, error_message: str) -> Dict:
        """Hata durumunda standart yanıt oluştur."""
        return {
            "success": False,
            "error": error_message,
            "raw_text": "",
            "cleaned_text": "",
            "issues": [{
                "type": "critical",
                "severity": "high",
                "title": "PDF Okunamadı",
                "description": error_message,
                "affected_text": "",
                "fix": "CV'nizi daha basit bir PDF formatında kaydedin."
            }],
            "score": 0,
            "score_label": "Kritik",
            "recommendations": [
                "CV'nizi Word'de açın ve 'PDF olarak kaydet' seçeneğini kullanın.",
                "Görsel ağırlıklı tasarımdan kaçının.",
                "Basit, tek sütunlu bir şablon kullanın."
            ],
            "stats": {},
            "problematic_texts": [],
            "reader_comparison": None,
            "consistency_analysis": None,
            "metadata": {},
        }
    
    def analyze_raw_text(self, raw_text: str) -> Dict:
        """Zaten çıkarılmış ham metni analiz et."""
        if not raw_text or len(raw_text.strip()) < 50:
            return self._create_error_response("Metin çok kısa veya boş.")
        
        try:
            cleaned_text = self._clean_text(raw_text)
            
            all_issues = []
            all_issues.extend(self._detect_icon_issues(raw_text))
            all_issues.extend(self._detect_spacing_issues(raw_text))
            all_issues.extend(self._detect_contact_issues(raw_text))
            all_issues.extend(self._detect_formatting_issues(raw_text))
            all_issues.extend(self._detect_layout_issues(raw_text))
            
            score = self._calculate_ats_score(all_issues)
            recommendations = self._generate_recommendations(all_issues, score)
            
            stats = {
                "total_characters": len(raw_text),
                "total_words": len(raw_text.split()),
                "total_lines": len(raw_text.splitlines()),
                "total_pages": 1,
                "issues_count": len(all_issues),
                "high_severity_count": len([i for i in all_issues if i.get("severity") == "high"]),
                "medium_severity_count": len([i for i in all_issues if i.get("severity") == "medium"]),
                "low_severity_count": len([i for i in all_issues if i.get("severity") == "low"]),
            }
            
            problematic_texts = self._extract_problematic_texts(raw_text)
            
            return {
                "success": True,
                "raw_text": raw_text,
                "cleaned_text": cleaned_text,
                "issues": all_issues,
                "score": score,
                "score_label": self._get_score_label(score),
                "recommendations": recommendations,
                "stats": stats,
                "problematic_texts": problematic_texts,
                "reader_comparison": None,
                "consistency_analysis": None,
                "metadata": {},
            }
            
        except Exception as e:
            return self._create_error_response(f"Analiz hatası: {str(e)}")


# Singleton instance
ats_simulation_service = ATSSimulationService()

# -*- coding: utf-8 -*-
"""
Job Search Service - Hybrid System
===================================
- Kariyer.net: Yandex X-Ray (aktif ilanlar)
- LinkedIn + Indeed: JobSpy

Tüm kaynaklar birleştirilip karışık sonuç döner.
"""
from jobspy import scrape_jobs
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from urllib.parse import quote_plus
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import pandas as pd
import time


# ============================================
# JOBSPY PARAMETRELERİ
# ============================================

# JobSpy experience_level mapping (LinkedIn için)
JOBSPY_EXPERIENCE_MAP = {
    "stajyer": "internship",
    "yeni_mezun": "entry_level",
    "1-3_yil": "associate",
    "3-5_yil": "mid_senior_level",
    "5+_yil": "director",
}

# JobSpy job_type mapping
JOBSPY_JOB_TYPE_MAP = {
    "full_time": "fulltime",
    "part_time": "parttime",
    "contract": "contract",
    "internship": "internship",
}

# Şehir isimleri mapping (Türkçe -> İngilizce)
CITY_MAPPING = {
    "İstanbul": "Istanbul",
    "Ankara": "Ankara",
    "İzmir": "Izmir",
    "Bursa": "Bursa",
    "Antalya": "Antalya",
    "Adana": "Adana",
    "Konya": "Konya",
    "Gaziantep": "Gaziantep",
    "Kocaeli": "Kocaeli",
    "Eskişehir": "Eskisehir",
}


# ============================================
# MESLEK GRUPLARI VE ALANLARI
# ============================================

# Meslek grupları ve alt alanları
PROFESSION_GROUPS = {
    "bilgisayar_muhendisligi": {
        "label": "Bilgisayar Mühendisliği",
        "label_en": "Computer Engineering",
        "fields": {
            "backend": {
                "label": "Backend Developer",
                "keywords_tr": ["backend developer", "backend", "sunucu geliştirici", "java developer", "python developer"],
                "keywords_en": ["Backend Developer", "Backend Engineer", "Server Developer"]
            },
            "frontend": {
                "label": "Frontend Developer",
                "keywords_tr": ["frontend developer", "frontend", "react developer", "vue developer", "angular developer"],
                "keywords_en": ["Frontend Developer", "React Developer", "UI Developer"]
            },
            "fullstack": {
                "label": "Full Stack Developer",
                "keywords_tr": ["full stack developer", "fullstack", "tam yığın"],
                "keywords_en": ["Full Stack Developer", "Fullstack Developer", "Full-Stack Engineer"]
            },
            "mobile": {
                "label": "Mobile Developer",
                "keywords_tr": ["mobil uygulama", "mobil developer", "android developer", "ios developer"],
                "keywords_en": ["Mobile Developer", "iOS Developer", "Android Developer", "Flutter Developer"]
            },
            "devops": {
                "label": "DevOps Engineer",
                "keywords_tr": ["devops", "sistem mühendisi", "bulut mühendisi"],
                "keywords_en": ["DevOps Engineer", "Cloud Engineer", "Site Reliability Engineer", "SRE"]
            },
            "yapay_zeka": {
                "label": "Yapay Zeka / AI",
                "keywords_tr": ["yapay zeka", "makine öğrenmesi", "derin öğrenme", "nlp", "bilgisayarlı görü"],
                "keywords_en": ["AI Engineer", "Machine Learning Engineer", "ML Engineer", "Data Scientist", "NLP Engineer"]
            },
            "data": {
                "label": "Data Engineer / Analyst",
                "keywords_tr": ["veri mühendisi", "veri analisti", "büyük veri", "data engineer"],
                "keywords_en": ["Data Engineer", "Data Analyst", "Big Data Engineer", "BI Developer"]
            },
            "test": {
                "label": "QA / Test Engineer",
                "keywords_tr": ["test mühendisi", "yazılım test", "qa mühendisi", "otomasyon test"],
                "keywords_en": ["QA Engineer", "Test Engineer", "SDET", "Quality Assurance"]
            },
            "embedded": {
                "label": "Embedded Developer",
                "keywords_tr": ["gömülü yazılım", "gömülü sistem", "firmware"],
                "keywords_en": ["Embedded Engineer", "Firmware Engineer", "Embedded Software Developer"]
            },
            "security": {
                "label": "Security Engineer",
                "keywords_tr": ["siber güvenlik", "güvenlik mühendisi", "penetrasyon testi"],
                "keywords_en": ["Security Engineer", "Cybersecurity", "Penetration Tester", "InfoSec"]
            },
            "game": {
                "label": "Game Developer",
                "keywords_tr": ["oyun geliştirici", "unity developer", "unreal developer"],
                "keywords_en": ["Game Developer", "Unity Developer", "Unreal Developer"]
            },
            "blockchain": {
                "label": "Blockchain Developer",
                "keywords_tr": ["blockchain geliştirici", "web3 developer", "akıllı kontrat"],
                "keywords_en": ["Blockchain Developer", "Web3 Developer", "Smart Contract Developer"]
            },
        }
    },
    "elektrik_elektronik_muhendisligi": {
        "label": "Elektrik-Elektronik Mühendisliği",
        "label_en": "Electrical & Electronics Engineering",
        "fields": {
            "elektrik_proje": {
                "label": "Elektrik Proje Mühendisi",
                "keywords_tr": ["elektrik proje", "elektrik mühendisi", "enerji mühendisi"],
                "keywords_en": ["Electrical Engineer", "Power Engineer", "Electrical Project Engineer"]
            },
            "elektronik_tasarim": {
                "label": "Elektronik Tasarım Mühendisi",
                "keywords_tr": ["elektronik tasarım", "pcb tasarım", "devre tasarım"],
                "keywords_en": ["Electronics Design Engineer", "PCB Designer", "Hardware Engineer"]
            },
            "otomasyon": {
                "label": "Otomasyon Mühendisi",
                "keywords_tr": ["otomasyon mühendisi", "plc programlama", "scada"],
                "keywords_en": ["Automation Engineer", "PLC Programmer", "Control Systems Engineer"]
            },
            "rf_mikrodalga": {
                "label": "RF/Mikrodalga Mühendisi",
                "keywords_tr": ["rf mühendisi", "mikrodalga", "telekomünikasyon"],
                "keywords_en": ["RF Engineer", "Microwave Engineer", "Telecommunications Engineer"]
            },
            "guc_elektroniği": {
                "label": "Güç Elektroniği Mühendisi",
                "keywords_tr": ["güç elektroniği", "inverter", "konvertör"],
                "keywords_en": ["Power Electronics Engineer", "Inverter Engineer"]
            },
        }
    },
    "makine_muhendisligi": {
        "label": "Makine Mühendisliği",
        "label_en": "Mechanical Engineering",
        "fields": {
            "tasarim": {
                "label": "Mekanik Tasarım Mühendisi",
                "keywords_tr": ["mekanik tasarım", "solidworks", "catia", "autocad"],
                "keywords_en": ["Mechanical Design Engineer", "CAD Engineer", "Product Design Engineer"]
            },
            "uretim": {
                "label": "Üretim Mühendisi",
                "keywords_tr": ["üretim mühendisi", "imalat mühendisi", "cnc"],
                "keywords_en": ["Manufacturing Engineer", "Production Engineer", "Process Engineer"]
            },
            "hvac": {
                "label": "HVAC Mühendisi",
                "keywords_tr": ["hvac mühendisi", "iklimlendirme", "havalandırma"],
                "keywords_en": ["HVAC Engineer", "Climate Control Engineer"]
            },
            "otomotiv": {
                "label": "Otomotiv Mühendisi",
                "keywords_tr": ["otomotiv mühendisi", "araç tasarım"],
                "keywords_en": ["Automotive Engineer", "Vehicle Engineer"]
            },
            "kalite": {
                "label": "Kalite Mühendisi",
                "keywords_tr": ["kalite mühendisi", "kalite kontrol", "kalite güvence"],
                "keywords_en": ["Quality Engineer", "QC Engineer", "Quality Assurance Engineer"]
            },
        }
    },
    "insaat_muhendisligi": {
        "label": "İnşaat Mühendisliği",
        "label_en": "Civil Engineering",
        "fields": {
            "yapi": {
                "label": "Yapı Mühendisi",
                "keywords_tr": ["yapı mühendisi", "statik mühendisi", "betonarme"],
                "keywords_en": ["Structural Engineer", "Building Engineer"]
            },
            "santiye": {
                "label": "Şantiye Mühendisi",
                "keywords_tr": ["şantiye mühendisi", "şantiye şefi", "inşaat mühendisi"],
                "keywords_en": ["Site Engineer", "Construction Engineer"]
            },
            "geoteknik": {
                "label": "Geoteknik Mühendisi",
                "keywords_tr": ["geoteknik mühendisi", "zemin mekaniği"],
                "keywords_en": ["Geotechnical Engineer", "Soil Engineer"]
            },
            "ulasim": {
                "label": "Ulaşım Mühendisi",
                "keywords_tr": ["ulaşım mühendisi", "karayolu", "trafik mühendisi"],
                "keywords_en": ["Transportation Engineer", "Traffic Engineer"]
            },
        }
    },
    "endustri_muhendisligi": {
        "label": "Endüstri Mühendisliği",
        "label_en": "Industrial Engineering",
        "fields": {
            "uretim_planlama": {
                "label": "Üretim Planlama Mühendisi",
                "keywords_tr": ["üretim planlama", "planlama mühendisi", "mrp"],
                "keywords_en": ["Production Planning Engineer", "Planning Engineer"]
            },
            "lojistik": {
                "label": "Lojistik Mühendisi",
                "keywords_tr": ["lojistik mühendisi", "tedarik zinciri", "depo yönetimi"],
                "keywords_en": ["Logistics Engineer", "Supply Chain Engineer"]
            },
            "is_analisti": {
                "label": "İş Analisti",
                "keywords_tr": ["iş analisti", "süreç iyileştirme", "yalın üretim"],
                "keywords_en": ["Business Analyst", "Process Improvement Engineer", "Lean Engineer"]
            },
            "erp": {
                "label": "ERP Uzmanı",
                "keywords_tr": ["erp uzmanı", "sap", "oracle erp"],
                "keywords_en": ["ERP Specialist", "SAP Consultant", "ERP Consultant"]
            },
        }
    },
    "kimya_muhendisligi": {
        "label": "Kimya Mühendisliği",
        "label_en": "Chemical Engineering",
        "fields": {
            "proses": {
                "label": "Proses Mühendisi",
                "keywords_tr": ["proses mühendisi", "kimya mühendisi", "üretim prosesi"],
                "keywords_en": ["Process Engineer", "Chemical Process Engineer"]
            },
            "arge": {
                "label": "Ar-Ge Mühendisi",
                "keywords_tr": ["arge mühendisi", "araştırma geliştirme", "formülasyon"],
                "keywords_en": ["R&D Engineer", "Research Engineer"]
            },
        }
    },
    "biyomedikal_muhendisligi": {
        "label": "Biyomedikal Mühendisliği",
        "label_en": "Biomedical Engineering",
        "fields": {
            "medikal_cihaz": {
                "label": "Medikal Cihaz Mühendisi",
                "keywords_tr": ["medikal cihaz", "tıbbi cihaz", "biyomedikal"],
                "keywords_en": ["Medical Device Engineer", "Biomedical Engineer"]
            },
            "klinik": {
                "label": "Klinik Mühendis",
                "keywords_tr": ["klinik mühendis", "hastane mühendisi"],
                "keywords_en": ["Clinical Engineer", "Hospital Engineer"]
            },
        }
    },
}

# Eski FIELD_TERMS'i koruyalım (geriye uyumluluk)
# TÜM meslek gruplarındaki alanları birleştir
FIELD_TERMS = {}
for profession_key, profession_data in PROFESSION_GROUPS.items():
    for field_key, field_data in profession_data["fields"].items():
        if field_key not in FIELD_TERMS:
            FIELD_TERMS[field_key] = field_data


# Şehirler
TURKEY_CITIES = [
    "İstanbul", "Ankara", "İzmir", "Bursa", "Antalya", 
    "Adana", "Konya", "Gaziantep", "Kocaeli", "Eskişehir",
    "Remote"
]

# Zaman filtreleri
TIME_FILTERS = {
    "d": 1,
    "d3": 3,
    "w": 7,
    "m": 30,
    "": None,
}


def create_driver() -> webdriver.Chrome:
    """Headless Chrome driver oluştur - Docker uyumlu."""
    import os
    
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_argument('--lang=tr-TR')
    
    # Docker için Chrome binary path
    chrome_bin = os.environ.get('CHROME_BIN')
    if chrome_bin:
        options.binary_location = chrome_bin
    
    # Docker'da ChromeDriver path belirle
    chromedriver_path = os.environ.get('CHROMEDRIVER_PATH')
    if chromedriver_path:
        from selenium.webdriver.chrome.service import Service
        service = Service(executable_path=chromedriver_path)
        driver = webdriver.Chrome(service=service, options=options)
    else:
        driver = webdriver.Chrome(options=options)
    
    driver.set_page_load_timeout(20)
    return driver


def scrape_kariyer_xray(
    keyword: str,
    days: int = 7,
    limit: int = 10,
    city: Optional[str] = None
) -> List[Dict]:
    """
    Kariyer.net'i Yandex X-Ray ile scrape et.
    Aktif olmayan ilanları filtreler.
    
    Not: X-Ray yöntemi bazen bloklanabilir veya timeout alabilir.
    Bu durumda boş liste döner ve sistem JobSpy sonuçlarını kullanır.
    """
    results = []
    
    # Tarih hesapla
    date_from = (datetime.now() - timedelta(days=days)).strftime("%Y%m%d")
    
    # X-Ray sorgusu oluştur - şehir varsa ekle
    city_query = f' "{city}"' if city and city != "Remote" else ""
    query = f'site:kariyer.net/is-ilani {keyword}{city_query} date:>={date_from} -"Bu ilan başvuruları artık kabul etmiyor."'
    url = f"https://yandex.com.tr/search/?text={quote_plus(query)}&lr=11508"
    
    print(f"[KARIYER X-RAY] Aranıyor: {keyword}{' - ' + city if city else ''}")
    
    driver = None
    try:
        driver = create_driver()
        driver.get(url)
        time.sleep(2)
        
        # Sonuçları bul
        search_results = driver.find_elements(By.CSS_SELECTOR, 'li.serp-item, div.organic')
        
        for item in search_results:
            if len(results) >= limit:
                break
            
            try:
                # Link ve başlık
                link_elem = item.find_element(By.CSS_SELECTOR, 'a[href*="kariyer.net/is-ilani"]')
                link = link_elem.get_attribute('href')
                
                # Başlık
                try:
                    title_elem = item.find_element(By.CSS_SELECTOR, 'h2, span.OrganicTitle-LinkText')
                    title = title_elem.text.strip()
                except:
                    title = link_elem.text.strip()
                
                if not title or not link or len(title) < 5:
                    continue
                
                # Snippet (şirket adı vs içerebilir)
                try:
                    snippet_elem = item.find_element(By.CSS_SELECTOR, 'span.OrganicTextContentSpan, div.text-container')
                    snippet = snippet_elem.text.strip()[:150]
                except:
                    snippet = ""
                
                results.append({
                    "title": title,
                    "company": "",  # X-Ray'den şirket adı almak zor
                    "location": "",
                    "url": link,
                    "description": "",  # X-Ray tam açıklama vermiyor
                    "snippet": snippet,
                    "source": "Kariyer.net",
                    "date_posted": ""
                })
                
            except Exception:
                continue
        
        print(f"[KARIYER X-RAY] {len(results)} ilan bulundu")
        
    except TimeoutException:
        print(f"[KARIYER X-RAY] Timeout hatası")
    except Exception as e:
        print(f"[KARIYER X-RAY] Hata: {e}")
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass
    
    return results


def scrape_jobspy(
    search_term: str,
    days: int = 7,
    limit: int = 15,
    city: Optional[str] = None,
    is_remote: Optional[bool] = None,
    job_type: Optional[str] = None,
    experience_level: Optional[str] = None
) -> List[Dict]:
    """
    JobSpy ile Indeed ve LinkedIn'den veri çek.
    Şehir belirtilirse o şehirde arar.
    
    Args:
        search_term: Arama terimi
        days: Kaç gün öncesine kadar
        limit: Maksimum sonuç sayısı
        city: Şehir (opsiyonel)
        is_remote: Sadece remote ilanlar mı?
        job_type: İş tipi (fulltime, parttime, contract, internship)
        experience_level: Tecrübe seviyesi (internship, entry_level, associate, mid_senior_level, director)
    """
    results = []
    
    try:
        # Konum belirleme - şehir varsa İngilizce'ye çevir
        if city and city != "Remote":
            location = CITY_MAPPING.get(city, city)
        elif is_remote:
            location = "Turkey"  # Remote için tüm Türkiye
        else:
            location = "Turkey"
        
        print(f"[JOBSPY] Aranıyor: {search_term} - Konum: {location} - Remote: {is_remote} - JobType: {job_type} - Exp: {experience_level}")
        
        hours_old = days * 24 if days else None
        
        # JobSpy parametreleri
        jobspy_params = {
            "site_name": ["indeed", "linkedin"],
            "search_term": search_term,
            "location": location,
            "results_wanted": limit,
            "hours_old": hours_old,
            "country_indeed": "Turkey",
            "linkedin_fetch_description": True,
        }
        
        # Remote filtresi
        if is_remote:
            jobspy_params["is_remote"] = True
        
        # Job type filtresi
        if job_type and job_type in JOBSPY_JOB_TYPE_MAP:
            jobspy_params["job_type"] = JOBSPY_JOB_TYPE_MAP[job_type]
        
        # Experience level filtresi (sadece LinkedIn için çalışıyor)
        if experience_level and experience_level in JOBSPY_EXPERIENCE_MAP:
            jobspy_params["linkedin_experience_level"] = JOBSPY_EXPERIENCE_MAP[experience_level]
        
        jobs_df = scrape_jobs(**jobspy_params)
        
        if jobs_df is not None and not jobs_df.empty:
            for _, row in jobs_df.iterrows():
                # Full description for skill gap analysis
                full_desc = str(row.get("description", "")) if pd.notna(row.get("description")) else ""
                
                job = {
                    "title": str(row.get("title", "")) if pd.notna(row.get("title")) else "",
                    "company": str(row.get("company", "")) if pd.notna(row.get("company")) else "",
                    "location": str(row.get("location", "")) if pd.notna(row.get("location")) else "",
                    "url": str(row.get("job_url", "")) if pd.notna(row.get("job_url")) else "",
                    "description": full_desc,  # Full description for skill gap
                    "snippet": full_desc[:200] if full_desc else "",  # Short snippet for display
                    "source": str(row.get("site", "")).title() if pd.notna(row.get("site")) else "Unknown",
                    "date_posted": str(row.get("date_posted", "")) if pd.notna(row.get("date_posted")) else "",
                }
                
                if job["title"] and job["url"]:
                    results.append(job)
        
        print(f"[JOBSPY] {len(results)} ilan bulundu")
        
    except Exception as e:
        print(f"[JOBSPY] Hata: {e}")
    
    return results


def search_jobs(
    field: str,
    sites: List[str] = None,
    time_range: str = "w",
    city: Optional[str] = None,
    limit: int = 20,
    country: str = "Turkey",
    fields: Optional[List[str]] = None,
    experience: Optional[str] = None,
    is_remote: Optional[bool] = None,
    job_type: Optional[str] = None,
) -> Dict:
    """
    Hibrit iş arama:
    - Kariyer.net: Yandex X-Ray
    - LinkedIn + Indeed: JobSpy
    
    Tüm sonuçlar birleştirilip karışık döner.
    
    Args:
        experience: Tecrübe seviyesi (stajyer, yeni_mezun, 1-3_yil, 3-5_yil, 5+_yil)
        is_remote: Sadece remote ilanlar
        job_type: İş tipi (full_time, part_time, contract, internship)
    """
    # Eski API uyumluluğu
    if fields and len(fields) > 0:
        field = fields[0]
    
    if not field or field not in FIELD_TERMS:
        return {
            "success": False,
            "jobs": [],
            "total_count": 0,
            "scraped_at": datetime.now().isoformat(),
            "error": "Geçerli bir alan seçmelisiniz",
            "filters": {}
        }
    
    field_info = FIELD_TERMS[field]
    days = TIME_FILTERS.get(time_range, 7) or 30
    
    # Tecrübe seviyesi için arama terimi eki
    EXPERIENCE_KEYWORDS = {
        "stajyer": {"tr": "stajyer", "en": "intern"},
        "yeni_mezun": {"tr": "yeni mezun", "en": "junior entry level"},
        "1-3_yil": {"tr": "junior", "en": "junior"},
        "3-5_yil": {"tr": "mid-level", "en": "mid-level"},
        "5+_yil": {"tr": "senior", "en": "senior"},
    }
    
    experience_label = None
    if experience and experience in EXPERIENCE_KEYWORDS:
        experience_label = EXPERIENCE_KEYWORDS[experience]["tr"]
    
    result = {
        "success": False,
        "jobs": [],
        "total_count": 0,
        "scraped_at": datetime.now().isoformat(),
        "error": None,
        "filters": {
            "field": field,
            "field_label": field_info["label"],
            "search_term": field_info["keywords_en"][0],
            "time_range": time_range,
            "location": city or country,
            "experience": experience_label,
        }
    }
    
    all_jobs = []
    seen_titles = set()
    
    # Tecrübe seviyesi için keyword eki
    exp_keyword_tr = ""
    exp_keyword_en = ""
    if experience and experience in EXPERIENCE_KEYWORDS:
        exp_keyword_tr = EXPERIENCE_KEYWORDS[experience]["tr"]
        exp_keyword_en = EXPERIENCE_KEYWORDS[experience]["en"]
    
    try:
        # 1. Kariyer.net X-Ray (Türkçe terimlerle)
        kariyer_keyword = field_info["keywords_tr"][0]
        if exp_keyword_tr:
            kariyer_keyword = f"{exp_keyword_tr} {kariyer_keyword}"
        
        kariyer_jobs = scrape_kariyer_xray(
            keyword=kariyer_keyword,
            days=days,
            limit=8,
            city=city
        )
        
        for job in kariyer_jobs:
            title_key = job["title"].lower()[:40]
            if title_key not in seen_titles:
                seen_titles.add(title_key)
                all_jobs.append(job)
        
        # 2. JobSpy (Indeed + LinkedIn) - İngilizce terimlerle
        jobspy_keyword = field_info["keywords_en"][0]
        if exp_keyword_en:
            jobspy_keyword = f"{exp_keyword_en} {jobspy_keyword}"
        
        # JobSpy için experience level mapping
        jobspy_exp = None
        if experience and experience in JOBSPY_EXPERIENCE_MAP:
            jobspy_exp = experience
        
        jobspy_jobs = scrape_jobspy(
            search_term=jobspy_keyword,
            days=days,
            limit=12,
            city=city,
            is_remote=is_remote,
            job_type=job_type,
            experience_level=jobspy_exp
        )
        
        for job in jobspy_jobs:
            title_key = job["title"].lower()[:40]
            if title_key not in seen_titles:
                seen_titles.add(title_key)
                all_jobs.append(job)
        
        # Sonuçları sırala: LinkedIn, Indeed önce, Kariyer.net en sonda
        def sort_key(job):
            source = job.get("source", "").lower()
            if "linkedin" in source:
                return 0
            elif "indeed" in source:
                return 1
            else:  # Kariyer.net ve diğerleri en sonda
                return 2
        
        all_jobs.sort(key=sort_key)
        all_jobs = all_jobs[:limit]
        
        result["success"] = True
        result["jobs"] = all_jobs
        result["total_count"] = len(all_jobs)
        
    except Exception as e:
        result["error"] = str(e)
        print(f"[ERROR] {e}")
    
    return result


# API için yardımcı fonksiyonlar
def get_all_fields() -> List[Dict]:
    """Tüm alanları döndür."""
    return [
        {"value": k, "label": v["label"], "keywords_count": len(v["keywords_tr"]) + len(v["keywords_en"])}
        for k, v in FIELD_TERMS.items()
    ]


def get_cities(country: str = "turkey") -> List[str]:
    """Şehirleri döndür."""
    return TURKEY_CITIES


def get_supported_sites() -> List[str]:
    """Desteklenen siteleri döndür."""
    return ["kariyer.net", "indeed", "linkedin"]


async def analyze_skill_gap(
    cv_data: Dict,
    job_title: str,
    job_description: str,
    company_name: str = ""
) -> Dict:
    """
    CV ve iş ilanını karşılaştırarak uyum analizi yap.
    
    TAMAMEN LLM TABANLI SİSTEM:
    - Rule-based matching iptal edildi
    - Tüm analiz LLM'e bırakıldı
    - Token limiti artırıldı (2000)
    - Detaylı ve doğru sonuçlar
    
    Args:
        cv_data: Kullanıcının CV verisi (skills, projects, experience vb.)
        job_title: İlan başlığı
        job_description: İlan açıklaması (aranan kriterler)
        company_name: Şirket adı (opsiyonel)
    
    Returns:
        {
            "match_percentage": int (0-100),
            "matching_skills": List[str],
            "missing_skills": List[str],
            "partial_skills": List[str],
            "recommendation": str,
            "success": bool
        }
    """
    from app.services.llm_service import LLMService
    import json
    
    llm_service = LLMService()
    
    # CV'den bilgileri çıkar
    cv_skills = cv_data.get("skills", [])
    cv_projects = cv_data.get("projects", [])
    cv_experience = cv_data.get("experience", [])
    cv_education = cv_data.get("education", [])
    
    # Proje detaylarını hazırla
    projects_text = ""
    if cv_projects:
        for p in cv_projects[:5]:
            if isinstance(p, dict):
                projects_text += f"- {p.get('name', '')}: {p.get('description', '')}\n"
            else:
                projects_text += f"- {p}\n"
    
    # Deneyim detaylarını hazırla
    experience_text = ""
    if cv_experience:
        for exp in cv_experience[:5]:
            if isinstance(exp, dict):
                experience_text += f"- {exp.get('title', '')} @ {exp.get('company', '')}\n"
            else:
                experience_text += f"- {exp}\n"
    
    # ============================================
    # TAMAMEN LLM TABANLI ANALİZ
    # ============================================
    
    system_prompt = """Sen bir İK uzmanısın. CV ile iş ilanını karşılaştır.

## KRİTİK KURALLAR

1. **SADECE TEKNOLOJİ/ARAÇ ADLARINI LİSTELE**
   - ✅ Doğru: Python, FastAPI, React, Docker, Git, LangChain, PostgreSQL
   - ❌ Yanlış: "Object-Oriented Programming", "Error handling", "API integration"
   - ❌ Yanlış: "Strong debugging skills", "Clear documentation writing"
   - Sadece somut teknoloji, framework, kütüphane, araç adları yaz

2. **EŞLEŞTİRME**
   - CV'de yazanla ilanda istenen aynıysa → matching_skills
   - İlanda istenip CV'de yoksa → missing_skills  
   - Benzer teknoloji varsa (Flask/FastAPI, React/Vue) → partial_skills

3. **UYUM YÜZDESİ**
   - matching / (matching + missing) * 100

## JSON ÇIKTI (SADECE JSON DÖNDÜR)

{
    "match_percentage": 65,
    "matching_skills": ["Python", "Git", "REST API"],
    "missing_skills": ["FastAPI", "LangChain", "Pinecone", "Docker"],
    "partial_skills": ["CV'de Flask var, ilanda FastAPI isteniyor"],
    "recommendation": "Türkçe 2-3 cümle öneri"
}"""

    # Varsayılan değerler
    no_skills = "Belirtilmemiş"
    no_projects = "Belirtilmemiş"
    no_experience = "Belirtilmemiş"
    
    user_message = f"""
===== ADAY CV BİLGİLERİ =====

[YETENEKLER/SKILLS]
{", ".join(cv_skills) if cv_skills else no_skills}

[PROJELER]
{projects_text if projects_text else no_projects}

[İŞ DENEYİMİ]
{experience_text if experience_text else no_experience}

===== İŞ İLANI =====

Pozisyon: {job_title}
Şirket: {company_name or "Belirtilmemiş"}

--- İLAN AÇIKLAMASI ---
{job_description[:6000] if job_description else "İlan açıklaması yok"}
--- İLAN AÇIKLAMASI BİTİŞ ---

===== GÖREV =====

Yukarıdaki CV ve iş ilanını dikkatli bir şekilde karşılaştır.
CV'de olan ve ilanda istenen yetenekleri eşleştir.
İlanda istenip CV'de olmayan yetenekleri eksik olarak listele.
Sonuçları JSON formatında döndür."""

    try:
        print(f"[SKILL-GAP] LLM analizi başlıyor: {job_title}")
        
        response = await llm_service.chat(
            message=user_message,
            system_prompt=system_prompt,
            temperature=0.1,  # Deterministik sonuç için düşük
            max_tokens=2000   # Uzun ilanlar için yüksek token
        )
        
        if not response:
            print("[SKILL-GAP] LLM boş cevap döndürdü")
            return {
                "success": False,
                "error": "LLM yanıt vermedi",
                "match_percentage": 0,
                "matching_skills": [],
                "missing_skills": [],
                "partial_skills": [],
                "recommendation": "Analiz yapılamadı. Lütfen tekrar deneyin."
            }
        
        # JSON parse et
        cleaned = response.strip()
        
        # Markdown code block varsa içini al
        if "```" in cleaned:
            import re
            match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', cleaned)
            if match:
                cleaned = match.group(1).strip()
        
        # JSON kısmını al
        if "{" in cleaned and "}" in cleaned:
            start = cleaned.find("{")
            end = cleaned.rfind("}") + 1
            cleaned = cleaned[start:end]
        
        # Parse et
        result = json.loads(cleaned)
        result["success"] = True
        result["analysis_method"] = "llm_full"
        
        print(f"[SKILL-GAP] Analiz tamamlandı: %{result.get('match_percentage', 0)} uyum")
        return result
        
    except json.JSONDecodeError as e:
        print(f"[SKILL-GAP] JSON parse hatası: {e}")
        # Basit fallback - CV skills ile ilan metnini karşılaştır
        matching = []
        for skill in cv_skills:
            if skill.lower() in job_description.lower():
                matching.append(skill)
        
        percentage = min(100, int(len(matching) / max(1, len(cv_skills)) * 100)) if cv_skills else 30
        
        return {
            "success": True,
            "match_percentage": percentage,
            "matching_skills": matching[:10],
            "missing_skills": [],
            "partial_skills": [],
            "recommendation": "Detaylı analiz için tekrar deneyin.",
            "analysis_method": "fallback"
        }
        
    except Exception as e:
        print(f"[SKILL-GAP] Hata: {e}")
        return {
            "success": False,
            "error": str(e),
            "match_percentage": 0,
            "matching_skills": [],
            "missing_skills": [],
            "partial_skills": [],
            "recommendation": ""
        }


# Test
if __name__ == "__main__":
    print("=" * 70)
    print("HİBRİT SİSTEM TESTİ")
    print("=" * 70)
    
    result = search_jobs(
        field="yapay_zeka",
        time_range="w",
        limit=10
    )
    
    print(f"\nToplam: {result['total_count']} ilan")
    for job in result["jobs"]:
        print(f"  - [{job['source']}] {job['title']}")

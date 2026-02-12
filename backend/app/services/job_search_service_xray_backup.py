# -*- coding: utf-8 -*-
"""
Job Search Service - Yandex X-Ray Scraper
==========================================
Yandex X-Ray araması yaparak iş ilanlarını çeker.

ÖNEMLİ: 380 KARAKTER LİMİTİ VE AKILLI KESİM
- Yandex'te URL limiti var (~400 karakter)
- Güvenli bölge: 380 karakter
- Önce sabit parçalar (site, tarih, negatif filtreler)
- Kalan bütçe kadar terim eklenir, limit dolunca DURULUR
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from urllib.parse import quote_plus
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import time


# ============================================
# SABIT AYARLAR
# ============================================
MAX_QUERY_LENGTH = 380  # Güvenli karakter limiti

# Negatif filtreler - toplu liste sayfalarını engelliyor
NEGATIVE_FILTERS = '-title:"İş İlanları" -title:"Jobs in"'

# İş siteleri (Türkiye odaklı)
JOB_SITES = {
    "linkedin": {
        "domain": "tr.linkedin.com/jobs",
        "name": "LinkedIn",
    },
    "kariyer": {
        "domain": "kariyer.net/is-ilani",
        "name": "Kariyer.net",
    },
    "youthall": {
        "domain": "youthall.com/tr/career",
        "name": "Youthall",
    },
    "savunmakariyer": {
        "domain": "savunmakariyer.com/ilan",
        "name": "SavunmaKariyer",
    },
    "secretcv": {
        "domain": "secretcv.com/is-ilani",
        "name": "SecretCV",
    },
    "indeed": {
        "domain": "tr.indeed.com/viewjob",
        "name": "Indeed TR",
    },
}

# Zaman seçenekleri -> gün sayısı
TIME_TO_DAYS = {
    "d": 1,
    "d3": 3,
    "w": 7,
    "m": 30,
    "": 0,
}

# ============================================
# ALAN TÜREVLERİ - ÖNEMLİDEN DAHA AZ ÖNEMLİYE SIRALANMIŞ
# (Limit dolunca sondakiler kesilir)
# ============================================
FIELD_TERMS = {
    "backend": {
        "label": "Backend Developer",
        "keywords": [
            "Backend Developer",
            "Backend Engineer",
            "Node.js Developer",
            "Java Developer",
            "Python Developer",
            ".NET Developer",
            "PHP Developer",
            "Go Developer",
            "Golang Developer",
            "Spring Boot Developer",
            "Django Developer",
            "Laravel Developer",
            "API Developer",
            "Server Side Developer",
            "Back-end Developer",
        ]
    },
    "frontend": {
        "label": "Frontend Developer",
        "keywords": [
            "Frontend Developer",
            "Frontend Engineer",
            "React Developer",
            "Vue.js Developer",
            "Angular Developer",
            "JavaScript Developer",
            "TypeScript Developer",
            "Web Developer",
            "Next.js Developer",
            "UI Developer",
            "Front-end Developer",
            "React.js Developer",
            "Vue Developer",
        ]
    },
    "fullstack": {
        "label": "Full Stack Developer",
        "keywords": [
            "Full Stack Developer",
            "Fullstack Developer",
            "Full-Stack Developer",
            "Full Stack Engineer",
            "MERN Developer",
            "MEAN Developer",
            "Full Stack Web Developer",
        ]
    },
    "mobile": {
        "label": "Mobile Developer",
        "keywords": [
            "Mobile Developer",
            "iOS Developer",
            "Android Developer",
            "Flutter Developer",
            "React Native Developer",
            "Swift Developer",
            "Kotlin Developer",
            "Mobile Engineer",
            "Mobile Application Developer",
            "Cross Platform Developer",
        ]
    },
    "devops": {
        "label": "DevOps Engineer",
        "keywords": [
            "DevOps Engineer",
            "DevOps Developer",
            "Cloud Engineer",
            "AWS Engineer",
            "Kubernetes Engineer",
            "Docker Engineer",
            "Platform Engineer",
            "SRE",
            "Site Reliability Engineer",
            "CI/CD Engineer",
            "Azure Engineer",
            "Infrastructure Engineer",
        ]
    },
    "yapay_zeka": {
        "label": "Yapay Zeka / AI",
        "keywords": [
            "AI Engineer",
            "Machine Learning Engineer",
            "ML Engineer",
            "Data Scientist",
            "Deep Learning Engineer",
            "NLP Engineer",
            "AI Developer",
            "Yapay Zeka",
            "Computer Vision Engineer",
            "MLOps Engineer",
            "LLM Engineer",
            "Artificial Intelligence",
            "Makine Öğrenmesi",
            "AI Researcher",
        ]
    },
    "data": {
        "label": "Data Engineer",
        "keywords": [
            "Data Engineer",
            "Data Analyst",
            "SQL Developer",
            "Big Data Engineer",
            "ETL Developer",
            "Data Architect",
            "Database Developer",
            "Spark Developer",
            "Data Pipeline Engineer",
            "Veri Mühendisi",
            "Data Platform Engineer",
        ]
    },
    "test": {
        "label": "QA / Test Engineer",
        "keywords": [
            "QA Engineer",
            "Test Engineer",
            "SDET",
            "Automation Tester",
            "Test Automation Engineer",
            "Quality Assurance Engineer",
            "Software Test Engineer",
            "Performance Tester",
            "Selenium Developer",
            "Manual Tester",
            "QA Analyst",
        ]
    },
    "embedded": {
        "label": "Embedded Developer",
        "keywords": [
            "Embedded Developer",
            "Embedded Engineer",
            "Firmware Developer",
            "Gömülü Yazılım",
            "IoT Developer",
            "Embedded Software Engineer",
            "Gömülü Sistemler",
            "Microcontroller Developer",
            "RTOS Developer",
            "Embedded Systems Engineer",
        ]
    },
    "security": {
        "label": "Security Engineer",
        "keywords": [
            "Security Engineer",
            "Cybersecurity Engineer",
            "Siber Güvenlik",
            "Penetration Tester",
            "Security Analyst",
            "SOC Analyst",
            "Information Security",
            "Application Security Engineer",
            "Network Security Engineer",
            "Cloud Security Engineer",
        ]
    },
}

# Tecrübe terimleri
EXPERIENCE_TERMS = {
    "stajyer": "Intern",
    "yeni_mezun": "Junior",
    "1-3_yil": "Junior",
    "3-5_yil": "Mid-Level",
    "5+_yil": "Senior",
}

# Türkiye şehirleri
TURKEY_CITIES = [
    "İstanbul", "Ankara", "İzmir", "Bursa", "Antalya", 
    "Adana", "Konya", "Gaziantep", "Kocaeli", "Eskişehir",
    "Kayseri", "Denizli", "Samsun", "Trabzon", "Malatya",
    "Remote"
]

# Ülkeler
COUNTRIES = {"turkey": "Türkiye"}


def calculate_date_filter(time_range: str) -> str:
    if not time_range or time_range not in TIME_TO_DAYS or TIME_TO_DAYS[time_range] == 0:
        return ""
    days = TIME_TO_DAYS[time_range]
    target_date = datetime.now() - timedelta(days=days)
    return target_date.strftime("%Y%m%d")


def build_optimized_query(
    site_key: str,
    field: str,
    time_range: str = "w",
    experience: Optional[str] = None,
    city: Optional[str] = None,
) -> Tuple[str, int, int]:
    """
    380 karakter limitine uygun optimize edilmiş sorgu oluştur.
    
    Returns:
        (query_string, used_keywords_count, total_keywords_count)
    """
    if site_key not in JOB_SITES or field not in FIELD_TERMS:
        return "", 0, 0
    
    # 1. SABİT PARÇALARI HESAPLA
    site_part = f'site:{JOB_SITES[site_key]["domain"]}'
    
    date_str = calculate_date_filter(time_range)
    date_part = f'date:>={date_str}' if date_str else ""
    
    # Şehir ve tecrübe (opsiyonel)
    city_part = f'"{city}"' if city else ""
    exp_part = f'"{EXPERIENCE_TERMS[experience]}"' if experience and experience in EXPERIENCE_TERMS else ""
    
    # 2. SABİT UZUNLUĞU HESAPLA
    # Format: site:xxx -title:"İş İlanları" -title:"Jobs in" (keywords) "city" "exp" date:>=xxx
    fixed_parts = [site_part, NEGATIVE_FILTERS]
    if city_part:
        fixed_parts.append(city_part)
    if exp_part:
        fixed_parts.append(exp_part)
    if date_part:
        fixed_parts.append(date_part)
    
    # Sabit parçaların uzunluğu (boşluklar dahil) + parantezler için 3 karakter
    fixed_length = len(" ".join(fixed_parts)) + 3  # () ve bir boşluk
    
    # 3. KALAN BÜTÇEYİ HESAPLA
    remaining_budget = MAX_QUERY_LENGTH - fixed_length
    
    # 4. TERİMLERİ EKLE (BÜTÇE DOLANA KADAR)
    keywords = FIELD_TERMS[field]["keywords"]
    total_keywords = len(keywords)
    
    selected_keywords = []
    current_length = 0
    
    for keyword in keywords:
        # Her terim için gereken uzunluk: "keyword" + " | " (ayraç)
        keyword_with_quotes = f'"{keyword}"'
        separator_length = 3 if selected_keywords else 0  # " | " sadece ilkinden sonra
        needed_length = len(keyword_with_quotes) + separator_length
        
        # Bütçe kontrolü
        if current_length + needed_length > remaining_budget:
            break  # BÜTÇE DOLDU, DUR!
        
        selected_keywords.append(keyword_with_quotes)
        current_length += needed_length
    
    used_keywords = len(selected_keywords)
    
    # 5. FİNAL SORGUYU OLUŞTUR
    # Format: site:xxx -title:"..." -title:"..." (kw1 | kw2 | kw3) "city" "exp" date:>=xxx
    keywords_part = f'({" | ".join(selected_keywords)})' if selected_keywords else ""
    
    query_parts = [site_part, NEGATIVE_FILTERS, keywords_part]
    if city_part:
        query_parts.append(city_part)
    if exp_part:
        query_parts.append(exp_part)
    if date_part:
        query_parts.append(date_part)
    
    final_query = " ".join([p for p in query_parts if p])
    
    print(f"[QUERY] {len(final_query)} karakter, {used_keywords}/{total_keywords} terim kullanıldı")
    
    return final_query, used_keywords, total_keywords


def create_driver() -> webdriver.Chrome:
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_argument('--lang=tr-TR')
    
    driver = webdriver.Chrome(options=options)
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'
    })
    return driver


def scrape_single_site(
    driver: webdriver.Chrome,
    site_key: str,
    field: str,
    time_range: str = "w",
    experience: Optional[str] = None,
    city: Optional[str] = None,
    limit: int = 10
) -> Tuple[List[Dict], str, int, int]:
    """
    TEK BİR SİTEDE arama yap.
    Returns: (jobs, url, used_keywords, total_keywords)
    """
    query, used_kw, total_kw = build_optimized_query(
        site_key, field, time_range, experience, city
    )
    
    if not query:
        return [], "", 0, 0
    
    encoded_query = quote_plus(query)
    url = f"https://yandex.com.tr/search/?text={encoded_query}"
    
    field_label = FIELD_TERMS.get(field, {}).get("label", field)
    print(f"[{site_key.upper()}] {field_label} aranıyor ({used_kw}/{total_kw} terim)...")
    
    try:
        driver.get(url)
        time.sleep(3)
        
        results = []
        serp_items = driver.find_elements(By.CSS_SELECTOR, '.serp-item')
        
        for item in serp_items:
            if len(results) >= limit:
                break
            
            try:
                link_elem = item.find_element(By.CSS_SELECTOR, 'a.OrganicTitle-Link, a.Link, a[href^="http"]')
                link = link_elem.get_attribute('href')
                
                if not link or 'yandex' in link:
                    continue
                
                if JOB_SITES[site_key]["domain"].split('/')[0] not in link:
                    continue
                
                try:
                    title_elem = item.find_element(By.CSS_SELECTOR, '.OrganicTitleContentSpan, h2')
                    title = title_elem.text.strip()
                except:
                    title = link_elem.text.strip()
                
                if not title or len(title) < 5:
                    continue
                
                try:
                    snippet_elem = item.find_element(By.CSS_SELECTOR, '.OrganicText, .TextContainer')
                    snippet = snippet_elem.text.strip()[:200]
                except:
                    snippet = ""
                
                results.append({
                    "title": title,
                    "url": link,
                    "snippet": snippet,
                    "source": JOB_SITES[site_key]["name"],
                })
                
            except Exception:
                continue
        
        print(f"[{site_key.upper()}] {len(results)} ilan bulundu")
        return results, url, used_kw, total_kw
        
    except Exception as e:
        print(f"[{site_key.upper()}] Hata: {e}")
        return [], url, used_kw, total_kw


def search_jobs(
    field: str,
    sites: List[str] = None,
    time_range: str = "w",
    experience: Optional[str] = None,
    city: Optional[str] = None,
    limit: int = 15,
    # Eski parametre uyumluluğu
    fields: Optional[List[str]] = None,
    country: Optional[str] = None,
) -> Dict:
    """
    Yandex X-Ray ile iş ilanı ara.
    380 karakter limiti ile optimize edilmiş sorgu kullanır.
    """
    if fields and len(fields) > 0:
        field = fields[0]
    
    if sites is None:
        sites = ["linkedin"]
    
    if not field or field not in FIELD_TERMS:
        return {
            "success": False,
            "url": "",
            "jobs": [],
            "total_count": 0,
            "scraped_at": datetime.now().isoformat(),
            "error": "Geçerli bir alan seçmelisiniz",
            "filters": {}
        }
    
    field_info = FIELD_TERMS[field]
    limit_per_site = max(5, limit // len(sites))
    
    result = {
        "success": False,
        "url": "",
        "queries": [],
        "jobs": [],
        "total_count": 0,
        "scraped_at": datetime.now().isoformat(),
        "error": None,
        "filters": {
            "field": field,
            "field_label": field_info["label"],
            "keywords_total": len(field_info["keywords"]),
            "keywords_used": 0,
            "sites": sites,
            "time_range": time_range,
            "experience": experience,
            "city": city,
        }
    }
    
    driver = None
    all_jobs = []
    all_urls = []
    total_used_kw = 0
    
    try:
        driver = create_driver()
        
        for site_key in sites:
            if site_key not in JOB_SITES:
                continue
            
            jobs, url, used_kw, total_kw = scrape_single_site(
                driver=driver,
                site_key=site_key,
                field=field,
                time_range=time_range,
                experience=experience,
                city=city,
                limit=limit_per_site
            )
            
            all_jobs.extend(jobs)
            if url:
                all_urls.append(url)
            total_used_kw = used_kw  # Son sitenin değeri
            
            if len(sites) > 1:
                time.sleep(1.5)
        
        all_jobs = all_jobs[:limit]
        
        result["success"] = True
        result["jobs"] = all_jobs
        result["total_count"] = len(all_jobs)
        result["url"] = all_urls[0] if all_urls else ""
        result["queries"] = all_urls
        result["filters"]["keywords_used"] = total_used_kw
        
    except Exception as e:
        result["error"] = str(e)
        print(f"[ERROR] {e}")
        
    finally:
        if driver:
            driver.quit()
    
    return result


# API için
def get_all_fields() -> List[Dict]:
    return [
        {
            "value": k, 
            "label": v["label"],
            "keywords_count": len(v["keywords"])
        }
        for k, v in FIELD_TERMS.items()
    ]


def get_countries() -> List[Dict]:
    return [{"value": k, "label": v} for k, v in COUNTRIES.items()]


def get_cities(country: str) -> List[str]:
    if country == "turkey":
        return TURKEY_CITIES
    return []


# Test
if __name__ == "__main__":
    print("=" * 70)
    print("380 KARAKTER LİMİTLİ OPTİMİZE SORGU TEST")
    print("=" * 70)
    
    # Test: Yapay Zeka alanı
    query, used, total = build_optimized_query(
        site_key="linkedin",
        field="yapay_zeka",
        time_range="w",
        city="Ankara"
    )
    
    print(f"\nSorgu ({len(query)} karakter):")
    print(query)
    print(f"\nKullanılan terim: {used}/{total}")

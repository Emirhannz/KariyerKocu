# -*- coding: utf-8 -*-
"""
Skill Matcher Service
=====================
LLM'den bağımsız, rule-based skill eşleştirme.
CV ve iş ilanı arasındaki uyumu hızlıca hesaplar.
"""

import re
from typing import Dict, List, Tuple, Any


# ============================================================================
# BİLGİSAYAR MÜHENDİSLİĞİ - KAPSAMLI TEKNOLOJİ SÖZLÜĞÜ
# ============================================================================
# Her alan için tüm yaygın teknolojiler dahil edildi.
# Format: "canonical_name": ["variant1", "variant2", ...]

TECH_SYNONYMS = {
    # =========================================================================
    # PROGRAMLAMA DİLLERİ
    # =========================================================================
    "python": ["python", "python3", "python2"],
    "javascript": ["javascript", "ecmascript"],
    "typescript": ["typescript"],
    "java": ["java", "jdk", "jre", "j2ee", "jse"],
    "csharp": ["c#", "csharp", "c sharp", "c-sharp"],
    "cpp": ["c++", "cpp", "c plus plus"],
    "c": ["c language", "c programlama"],
    "go": ["golang", "go programming", "go language"],
    "rust": ["rust", "rust-lang"],
    "ruby": ["ruby"],
    "php": ["php", "php7", "php8"],
    "kotlin": ["kotlin", "kt"],
    "swift": ["swift"],
    "scala": ["scala"],
    "r": ["r language", "r programming", "r studio"],
    "matlab": ["matlab"],
    "perl": ["perl"],
    "lua": ["lua"],
    "dart": ["dart"],
    "elixir": ["elixir"],
    "clojure": ["clojure"],
    "haskell": ["haskell"],
    "groovy": ["groovy"],
    
    # =========================================================================
    # BACKEND FRAMEWORKS
    # =========================================================================
    # Python
    "django": ["django", "django rest", "drf", "django rest framework"],
    "flask": ["flask"],
    "fastapi": ["fastapi", "fast api", "fast-api"],
    "pyramid": ["pyramid"],
    "tornado": ["tornado"],
    "aiohttp": ["aiohttp"],
    "celery": ["celery"],
    
    # JavaScript/Node
    "nodejs": ["node", "nodejs", "node.js", "node js"],
    "express": ["express", "expressjs", "express.js"],
    "nestjs": ["nest", "nestjs", "nest.js"],
    "koa": ["koa", "koajs"],
    "hapi": ["hapi", "hapijs"],
    "fastify": ["fastify"],
    
    # Java
    "spring": ["spring", "spring boot", "springboot", "spring framework"],
    "spring mvc": ["spring mvc"],
    "hibernate": ["hibernate", "jpa", "java persistence"],
    "struts": ["struts"],
    "maven": ["maven", "mvn"],
    "gradle": ["gradle"],
    
    # .NET
    "dotnet": [".net", "dotnet", ".net core", ".net framework", "dotnet core"],
    "aspnet": ["asp.net", "aspnet", "asp.net core", "aspnet core", "asp.net mvc"],
    "entity framework": ["entity framework", "ef core"],
    "blazor": ["blazor"],
    
    # Ruby
    "rails": ["rails", "ruby on rails", "ror"],
    "sinatra": ["sinatra"],
    
    # PHP
    "laravel": ["laravel"],
    "symfony": ["symfony"],
    "codeigniter": ["codeigniter"],
    "wordpress": ["wordpress", "wp"],
    "drupal": ["drupal"],
    
    # Go
    "gin": ["gin", "gin-gonic"],
    "echo": ["echo framework"],
    "fiber": ["fiber"],
    
    # =========================================================================
    # FRONTEND FRAMEWORKS & LIBRARIES
    # =========================================================================
    "react": ["react", "reactjs", "react.js", "react js"],
    "vue": ["vue", "vuejs", "vue.js", "vue js", "vue3", "vue2"],
    "angular": ["angular", "angularjs", "angular.js", "angular 2+"],
    "svelte": ["svelte", "sveltejs"],
    "nextjs": ["next", "nextjs", "next.js", "next js"],
    "nuxtjs": ["nuxt", "nuxtjs", "nuxt.js"],
    "gatsby": ["gatsby", "gatsbyjs"],
    "remix": ["remix"],
    "ember": ["ember", "emberjs", "ember.js"],
    "backbone": ["backbone", "backbonejs"],
    "jquery": ["jquery", "jq"],
    "redux": ["redux", "redux toolkit", "rtk"],
    "mobx": ["mobx"],
    "zustand": ["zustand"],
    "recoil": ["recoil"],
    "rxjs": ["rxjs", "reactive extensions"],
    "webpack": ["webpack"],
    "vite": ["vite", "vitejs"],
    "parcel": ["parcel"],
    "rollup": ["rollup"],
    "babel": ["babel", "babeljs"],
    "eslint": ["eslint"],
    "prettier": ["prettier"],
    
    # =========================================================================
    # CSS & STYLING
    # =========================================================================
    "html": ["html", "html5", "html 5"],
    "css": ["css", "css3", "css 3"],
    "sass": ["sass", "scss"],
    "less": ["less"],
    "tailwind": ["tailwind", "tailwindcss", "tailwind css"],
    "bootstrap": ["bootstrap", "bootstrap 5", "bootstrap5"],
    "material ui": ["material ui", "mui", "material-ui", "material design"],
    "chakra ui": ["chakra", "chakra ui", "chakra-ui"],
    "ant design": ["ant design", "antd"],
    "styled components": ["styled components", "styled-components"],
    "emotion": ["emotion"],
    
    # =========================================================================
    # MOBILE DEVELOPMENT
    # =========================================================================
    "android": ["android", "android studio", "android sdk"],
    "ios": ["ios", "iphone", "ipad"],
    "swift": ["swift", "swiftui"],
    "kotlin": ["kotlin", "kotlin android"],
    "react native": ["react native", "reactnative", "rn"],
    "flutter": ["flutter"],
    "xamarin": ["xamarin"],
    "ionic": ["ionic"],
    "cordova": ["cordova", "phonegap"],
    "capacitor": ["capacitor"],
    "expo": ["expo"],
    
    # =========================================================================
    # DATABASES - SQL
    # =========================================================================
    "sql": ["sql", "structured query language"],
    "postgresql": ["postgresql", "postgres", "psql", "pg", "pgsql"],
    "mysql": ["mysql", "my sql", "mariadb"],
    "mssql": ["mssql", "sql server", "microsoft sql server", "t-sql", "tsql"],
    "oracle": ["oracle", "oracle db", "oracle database", "pl/sql", "plsql"],
    "sqlite": ["sqlite", "sqlite3"],
    "db2": ["db2", "ibm db2"],
    
    # =========================================================================
    # DATABASES - NoSQL
    # =========================================================================
    "mongodb": ["mongodb", "mongo", "mongoose"],
    "redis": ["redis"],
    "elasticsearch": ["elasticsearch", "elastic search"],
    "cassandra": ["cassandra", "apache cassandra"],
    "dynamodb": ["dynamodb", "dynamo db", "aws dynamodb"],
    "couchdb": ["couchdb", "couch"],
    "firebase": ["firebase", "firebase realtime", "firestore"],
    "neo4j": ["neo4j", "graph database"],
    "influxdb": ["influxdb", "influx"],
    "memcached": ["memcached"],
    
    # =========================================================================
    # CLOUD PLATFORMS
    # =========================================================================
    "aws": ["aws", "amazon web services", "amazon cloud"],
    "azure": ["azure", "microsoft azure", "ms azure"],
    "gcp": ["gcp", "google cloud", "google cloud platform"],
    "heroku": ["heroku"],
    "digitalocean": ["digitalocean", "digital ocean"],
    "vercel": ["vercel", "zeit"],
    "netlify": ["netlify"],
    "cloudflare": ["cloudflare"],
    "alibaba cloud": ["alibaba cloud", "aliyun"],
    
    # AWS Services
    "ec2": ["ec2", "aws ec2", "elastic compute"],
    "s3": ["s3", "aws s3", "simple storage"],
    "lambda": ["lambda", "aws lambda", "serverless"],
    "rds": ["rds", "aws rds"],
    "cloudwatch": ["cloudwatch"],
    "sqs": ["sqs", "simple queue service"],
    "sns": ["sns", "simple notification"],
    "eks": ["eks", "elastic kubernetes"],
    "ecs": ["ecs", "elastic container"],
    
    # =========================================================================
    # DEVOPS & CI/CD
    # =========================================================================
    "docker": ["docker", "container", "containerization", "dockerfile"],
    "kubernetes": ["kubernetes", "k8s", "kubectl"],
    "helm": ["helm", "helm charts"],
    "terraform": ["terraform", "tf", "iac", "infrastructure as code"],
    "ansible": ["ansible"],
    "puppet": ["puppet"],
    "chef": ["chef"],
    "jenkins": ["jenkins"],
    "gitlab ci": ["gitlab ci", "gitlab-ci", "gitlab ci/cd"],
    "github actions": ["github actions", "gh actions"],
    "circleci": ["circleci", "circle ci"],
    "travis": ["travis", "travis ci", "travisci"],
    "argocd": ["argocd", "argo cd"],
    "prometheus": ["prometheus"],
    "grafana": ["grafana"],
    "datadog": ["datadog"],
    "new relic": ["new relic", "newrelic"],
    "splunk": ["splunk"],
    "elk": ["elk", "elk stack", "elastic stack"],
    "logstash": ["logstash"],
    "kibana": ["kibana"],
    "nginx": ["nginx"],
    "apache": ["apache", "apache http", "httpd"],
    "haproxy": ["haproxy"],
    "vault": ["vault", "hashicorp vault"],
    "consul": ["consul"],
    
    # =========================================================================
    # VERSION CONTROL
    # =========================================================================
    "git": ["git", "git scm", "git version control"],
    "github": ["github"],
    "gitlab": ["gitlab"],
    "bitbucket": ["bitbucket"],
    "svn": ["svn", "subversion"],
    "mercurial": ["mercurial", "hg"],
    
    # =========================================================================
    # AI / MACHINE LEARNING
    # =========================================================================
    "machine learning": ["machine learning", "makine öğrenmesi", "makine öğrenimi"],
    "deep learning": ["deep learning", "derin öğrenme"],
    "artificial intelligence": ["artificial intelligence", "yapay zeka"],
    "tensorflow": ["tensorflow"],
    "pytorch": ["pytorch", "torch"],
    "keras": ["keras"],
    "scikit-learn": ["scikit-learn", "sklearn", "scikit learn"],
    "pandas": ["pandas"],
    "numpy": ["numpy"],
    "scipy": ["scipy"],
    "matplotlib": ["matplotlib"],
    "seaborn": ["seaborn"],
    "opencv": ["opencv", "cv2", "computer vision"],
    "nlp": ["nlp", "natural language processing", "doğal dil işleme"],
    "huggingface": ["huggingface", "hugging face", "transformers"],
    "bert": ["bert"],
    "gpt": ["gpt", "gpt-3", "gpt-4", "chatgpt"],
    "llm": ["llm", "large language model", "büyük dil modeli"],
    "mlops": ["mlops", "ml ops"],
    "mlflow": ["mlflow", "ml flow"],
    "kubeflow": ["kubeflow"],
    "jupyter": ["jupyter", "jupyter notebook", "jupyterlab"],
    "colab": ["colab", "google colab"],
    "spark": ["spark", "apache spark", "pyspark"],
    "hadoop": ["hadoop", "apache hadoop", "hdfs"],
    "airflow": ["airflow", "apache airflow"],
    
    # =========================================================================
    # DATA ENGINEERING
    # =========================================================================
    "etl": ["etl", "extract transform load"],
    "data warehouse": ["data warehouse", "dwh", "veri ambarı"],
    "data lake": ["data lake", "veri gölü"],
    "snowflake": ["snowflake"],
    "databricks": ["databricks"],
    "redshift": ["redshift", "aws redshift"],
    "bigquery": ["bigquery", "big query", "bq"],
    "power bi": ["power bi", "powerbi"],
    "tableau": ["tableau"],
    "looker": ["looker"],
    "dbt": ["dbt", "data build tool"],
    "kafka": ["kafka", "apache kafka"],
    "rabbitmq": ["rabbitmq", "rabbit mq", "rabbit"],
    "pulsar": ["pulsar", "apache pulsar"],
    "flink": ["flink", "apache flink"],
    
    # =========================================================================
    # SECURITY / CYBERSECURITY
    # =========================================================================
    "cybersecurity": ["cybersecurity", "cyber security", "siber güvenlik"],
    "penetration testing": ["penetration testing", "pentest", "pen test", "sızma testi"],
    "owasp": ["owasp", "owasp top 10"],
    "burp suite": ["burp suite", "burp", "burpsuite"],
    "metasploit": ["metasploit"],
    "nmap": ["nmap"],
    "wireshark": ["wireshark"],
    "kali": ["kali", "kali linux"],
    "siem": ["siem", "security information"],
    "soc": ["soc", "security operations center"],
    "firewall": ["firewall", "güvenlik duvarı"],
    "vpn": ["vpn", "virtual private network"],
    "oauth": ["oauth", "oauth2", "oauth 2.0"],
    "jwt": ["jwt", "json web token"],
    "ssl": ["ssl", "tls", "https", "ssl/tls"],
    "encryption": ["encryption", "şifreleme", "cryptography"],
    
    # =========================================================================
    # TESTING & QA
    # =========================================================================
    "testing": ["testing", "test", "yazılım test"],
    "unit testing": ["unit testing", "unit test", "birim test"],
    "integration testing": ["integration testing", "integration test", "entegrasyon testi"],
    "e2e testing": ["e2e testing", "end to end", "uçtan uca test"],
    "jest": ["jest"],
    "mocha": ["mocha"],
    "chai": ["chai"],
    "cypress": ["cypress"],
    "selenium": ["selenium", "selenium webdriver"],
    "playwright": ["playwright"],
    "puppeteer": ["puppeteer"],
    "junit": ["junit", "junit5"],
    "testng": ["testng", "test ng"],
    "pytest": ["pytest", "py.test"],
    "unittest": ["unittest", "python unittest"],
    "postman": ["postman"],
    "insomnia": ["insomnia"],
    "swagger": ["swagger", "openapi", "open api"],
    "jmeter": ["jmeter", "apache jmeter"],
    "loadrunner": ["loadrunner", "load runner"],
    "katalon": ["katalon", "katalon studio"],
    "appium": ["appium"],
    "tdd": ["tdd", "test driven development"],
    "bdd": ["bdd", "behavior driven development"],
    "cucumber": ["cucumber", "gherkin"],
    
    # =========================================================================
    # EMBEDDED & IoT
    # =========================================================================
    "embedded": ["embedded", "gömülü", "gömülü sistem", "embedded systems"],
    "firmware": ["firmware", "yazılım"],
    "rtos": ["rtos", "real time os", "freertos"],
    "arduino": ["arduino"],
    "raspberry pi": ["raspberry pi", "raspi", "rpi"],
    "esp32": ["esp32", "esp8266"],
    "stm32": ["stm32"],
    "arm": ["arm", "arm cortex"],
    "mqtt": ["mqtt", "message queue"],
    "modbus": ["modbus"],
    "can bus": ["can bus", "can protocol"],
    "i2c": ["i2c"],
    "spi": ["spi"],
    "uart": ["uart"],
    "iot": ["iot", "internet of things", "nesnelerin interneti"],
    
    # =========================================================================
    # GAME DEVELOPMENT
    # =========================================================================
    "unity": ["unity", "unity3d", "unity 3d"],
    "unreal": ["unreal", "unreal engine", "ue4", "ue5"],
    "godot": ["godot", "godot engine"],
    "game development": ["game development", "oyun geliştirme", "game dev"],
    "directx": ["directx", "dx11", "dx12"],
    "opengl": ["opengl", "gl"],
    "vulkan": ["vulkan"],
    "blender": ["blender"],
    "3d modeling": ["3d modeling", "3d modelleme"],
    
    # =========================================================================
    # BLOCKCHAIN
    # =========================================================================
    "blockchain": ["blockchain", "blok zinciri"],
    "ethereum": ["ethereum", "eth"],
    "solidity": ["solidity"],
    "smart contract": ["smart contract", "akıllı kontrat"],
    "web3": ["web3", "web 3", "web3.js"],
    "hardhat": ["hardhat"],
    "truffle": ["truffle"],
    "nft": ["nft", "non-fungible token"],
    "defi": ["defi", "decentralized finance"],
    
    # =========================================================================
    # API & PROTOCOLS
    # =========================================================================
    "rest": ["rest", "restful", "rest api", "restful api"],
    "graphql": ["graphql", "gql"],
    "grpc": ["grpc", "g-rpc"],
    "websocket": ["websocket", "ws", "socket.io"],
    "soap": ["soap", "soap api"],
    "api": ["api", "application programming interface"],
    "microservices": ["microservices", "mikro servis", "mikroservis"],
    "monolith": ["monolith", "monolithic", "monolit"],
    "serverless": ["serverless", "sunucusuz"],
    
    # =========================================================================
    # OTHER TOOLS & CONCEPTS
    # =========================================================================
    "linux": ["linux", "unix", "ubuntu", "centos", "debian", "redhat"],
    "windows": ["windows", "windows server"],
    "macos": ["macos", "mac os", "osx"],
    "bash": ["bash", "shell", "shell script", "sh"],
    "powershell": ["powershell", "ps", "pwsh"],
    "vim": ["vim", "vi", "neovim"],
    "vscode": ["vscode", "vs code", "visual studio code"],
    "intellij": ["intellij", "intellij idea", "jetbrains"],
    "agile": ["agile", "çevik", "agile methodology"],
    "scrum": ["scrum"],
    "kanban": ["kanban"],
    "jira": ["jira", "atlassian jira"],
    "confluence": ["confluence"],
    "trello": ["trello"],
    "asana": ["asana"],
    "slack": ["slack"],
    "teams": ["teams", "microsoft teams", "ms teams"],
    "design patterns": ["design patterns", "tasarım kalıpları", "tasarım desenleri"],
    "solid": ["solid", "solid principles"],
    "oop": ["oop", "object oriented", "nesne yönelimli"],
    "functional programming": ["functional programming", "fp", "fonksiyonel programlama"],
    "clean code": ["clean code", "temiz kod"],
    "code review": ["code review", "kod inceleme"],
    "pair programming": ["pair programming", "eşli programlama"],
}


def normalize_skill(skill: str) -> str:
    """Skill adını normalize et."""
    return skill.lower().strip()


def find_canonical_skill(skill: str) -> str:
    """Skill için canonical (standart) ismi bul."""
    skill_lower = normalize_skill(skill)
    
    for canonical, variants in TECH_SYNONYMS.items():
        if skill_lower in variants:
            return canonical
        for variant in variants:
            if variant in skill_lower or skill_lower in variant:
                return canonical
    
    return skill_lower


def extract_skills_from_text(text: str) -> List[str]:
    """
    Metin içinden skill'leri çıkar.
    İş ilanı açıklamalarından otomatik skill extraction.
    """
    if not text:
        return []
    
    text_lower = text.lower()
    found_skills = set()
    
    for canonical, variants in TECH_SYNONYMS.items():
        for variant in variants:
            # Kelime sınırları ile ara
            pattern = r'\b' + re.escape(variant) + r'\b'
            if re.search(pattern, text_lower):
                found_skills.add(canonical)
                break
    
    return list(found_skills)


def match_skills(
    cv_skills: List[str],
    job_skills: List[str],
    job_description: str = ""
) -> Dict[str, Any]:
    """
    CV skills ile iş ilanı skills'lerini eşleştir.
    
    Args:
        cv_skills: CV'deki yetenekler
        job_skills: İlanda listelenen yetenekler  
        job_description: İlan açıklaması (ek skill çıkarmak için)
    
    Returns:
        {
            "matching_skills": [...],
            "missing_skills": [...],
            "partial_skills": [...],
            "match_percentage": int,
            "cv_extra_skills": [...]  # CV'de olup ilanda olmayan
        }
    """
    # Normalize et
    cv_normalized = {find_canonical_skill(s): s for s in cv_skills}
    job_normalized = {find_canonical_skill(s): s for s in job_skills}
    
    # İlan açıklamasından ek skilleri çıkar
    if job_description:
        desc_skills = extract_skills_from_text(job_description)
        for skill in desc_skills:
            if skill not in job_normalized:
                job_normalized[skill] = skill.title()
    
    matching = []
    missing = []
    partial = []
    cv_extra = []
    
    # Eşleştirme yap
    for job_canonical, job_original in job_normalized.items():
        if job_canonical in cv_normalized:
            matching.append(job_original)
        else:
            # Partial match kontrolü
            partial_found = False
            for cv_canonical, cv_original in cv_normalized.items():
                # İlişkili teknoloji kontrolü
                if is_related_tech(cv_canonical, job_canonical):
                    partial.append(f"{cv_original} (CV'de var, ilanda {job_original} isteniyor)")
                    partial_found = True
                    break
            
            if not partial_found:
                missing.append(job_original)
    
    # CV'de olup ilanda olmayan skilleri bul
    for cv_canonical, cv_original in cv_normalized.items():
        if cv_canonical not in job_normalized:
            cv_extra.append(cv_original)
    
    # Yüzde hesapla
    total_required = len(job_normalized)
    if total_required == 0:
        percentage = 50  # İlanda skill belirtilmemişse orta değer
    else:
        # Matching: tam puan, Partial: yarım puan
        score = len(matching) + (len(partial) * 0.5)
        percentage = int((score / total_required) * 100)
        percentage = min(100, max(0, percentage))
    
    return {
        "matching_skills": matching,
        "missing_skills": missing,
        "partial_skills": partial,
        "cv_extra_skills": cv_extra[:10],  # İlk 10 tane
        "match_percentage": percentage,
        "total_required": total_required,
        "analysis_method": "rule_based"
    }


def is_related_tech(tech1: str, tech2: str) -> bool:
    """İki teknolojinin ilişkili olup olmadığını kontrol et."""
    relations = {
        # Dil benzerliği
        ("python", "java"): True,
        ("javascript", "typescript"): True,
        ("csharp", "java"): True,
        
        # Framework ilişkisi
        ("react", "vue"): True,
        ("react", "angular"): True,
        ("django", "flask"): True,
        ("django", "fastapi"): True,
        ("spring", "dotnet"): True,
        
        # Database benzerliği
        ("postgresql", "mysql"): True,
        ("mongodb", "redis"): True,
        
        # Cloud benzerliği
        ("aws", "azure"): True,
        ("aws", "gcp"): True,
        ("azure", "gcp"): True,
    }
    
    key1 = (tech1, tech2)
    key2 = (tech2, tech1)
    
    return relations.get(key1, False) or relations.get(key2, False)


def generate_recommendation(
    matching: List[str],
    missing: List[str],
    partial: List[str],
    percentage: int,
    job_title: str
) -> str:
    """Türkçe öneri metni oluştur."""
    
    if percentage >= 80:
        return f"CV'niz {job_title} pozisyonu için oldukça uygun. {', '.join(matching[:3])} gibi önemli yetenekleriniz var."
    
    elif percentage >= 50:
        rec = f"CV'niz {job_title} pozisyonu ile orta düzeyde uyumlu."
        if missing:
            rec += f" {', '.join(missing[:3])} teknolojilerini öğrenmeniz CV'nizi güçlendirir."
        return rec
    
    else:
        rec = f"Bu pozisyon için bazı yetenekleri geliştirmeniz gerekiyor."
        if missing:
            rec += f" Özellikle {', '.join(missing[:3])} alanlarına odaklanmanızı öneririm."
        if matching:
            rec += f" Ancak {', '.join(matching[:2])} gibi yetenekleriniz güçlü."
        return rec


# Test
if __name__ == "__main__":
    cv = ["Python", "FastAPI", "PostgreSQL", "React", "Git"]
    job = ["Python", "Django", "MySQL", "Docker"]
    
    result = match_skills(cv, job)
    print(f"Eşleşen: {result['matching_skills']}")
    print(f"Eksik: {result['missing_skills']}")
    print(f"Benzer: {result['partial_skills']}")
    print(f"Uyum: %{result['match_percentage']}")

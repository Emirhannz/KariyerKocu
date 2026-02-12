"""
KariyerKoçu - Speech Service (Speech-to-Text)
==============================================
Groq Whisper-large-v3 kullanarak ses tanıma servisi.
Teknik terimler için prompt desteği içerir.
"""

import os
import tempfile
from typing import Optional
from groq import Groq


# Groq API Key - .env dosyasından okunuyor
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# Teknik terimler prompt'u - Whisper'ın doğru anlaması için
TECH_TERMS_PROMPT = """
Yazılım mülakatı kaydı. Aşağıdaki terimler geçebilir:
Python, JavaScript, TypeScript, Java, C++, C#, Go, Rust, Swift, Kotlin,
React, Angular, Vue, Next.js, Node.js, Express, FastAPI, Django, Flask,
Docker, Kubernetes, CI/CD, GitHub, GitLab, Jenkins, AWS, Azure, GCP,
SQL, PostgreSQL, MySQL, MongoDB, Redis, Elasticsearch,
REST API, GraphQL, WebSocket, Microservices, Backend, Frontend, Fullstack,
Machine Learning, Deep Learning, TensorFlow, PyTorch, YOLO, CNN, LLM, GPT,
Jetson, Raspberry Pi, NVIDIA, CUDA, ARM, embedded systems,
Agile, Scrum, DevOps, testing, debugging, deployment, pipeline,
container, image, repository, branch, merge, commit, push, pull.
"""


class SpeechService:
    """Ses tanıma servisi - Groq Whisper-large-v3."""
    
    def __init__(self):
        self.client = None
        self._init_client()
    
    def _init_client(self):
        """Groq client'ı başlat."""
        try:
            self.client = Groq(api_key=GROQ_API_KEY)
        except Exception as e:
            print(f"⚠️ Groq client başlatılamadı: {e}")
            self.client = None
    
    async def transcribe_audio(
        self, 
        audio_bytes: bytes, 
        filename: str = "audio.wav",
        use_tech_prompt: bool = True
    ) -> dict:
        """
        Ses dosyasını metne çevir (Groq Whisper-large-v3).
        
        Args:
            audio_bytes: Ses dosyası içeriği (bytes)
            filename: Orijinal dosya adı
            use_tech_prompt: Teknik terim prompt'u kullan
        
        Returns:
            {"text": "transcribed text", "success": True} veya
            {"error": "hata mesajı", "success": False}
        """
        if not self.client:
            return {
                "error": "Groq client başlatılamadı",
                "success": False
            }
        
        # Geçici dosyaya kaydet
        suffix = os.path.splitext(filename)[1] or ".wav"
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name
        
        try:
            # WebM/Opus formatını WAV'a çevir
            if suffix.lower() in [".webm", ".ogg", ".opus"]:
                converted_path = await self._convert_to_wav(tmp_path)
                if converted_path:
                    os.unlink(tmp_path)
                    tmp_path = converted_path
            
            # Groq Whisper API ile transkript
            with open(tmp_path, "rb") as f:
                transcription = self.client.audio.transcriptions.create(
                    file=(tmp_path, f.read()),
                    model="whisper-large-v3",
                    response_format="json",
                    language="tr",
                    temperature=0.0,
                    prompt=TECH_TERMS_PROMPT if use_tech_prompt else None
                )
            
            # "Thank you for watching" gibi Whisper artifact'larını temizle
            text = transcription.text
            text = self._clean_whisper_artifacts(text)
            
            return {
                "text": text,
                "success": True
            }
            
        except Exception as e:
            return {
                "error": f"Transkript hatası: {str(e)}",
                "success": False
            }
        finally:
            # Geçici dosyayı temizle
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    def _clean_whisper_artifacts(self, text: str) -> str:
        """Whisper'ın eklediği gereksiz ifadeleri temizle."""
        # Sık görülen Whisper artifact'ları
        artifacts = [
            "Thank you for watching.",
            "Thanks for watching.",
            "Thank you for watching!",
            "Abone olmayı unutmayın.",
            "Beğenmeyi unutmayın.",
            "...",
        ]
        
        result = text
        for artifact in artifacts:
            result = result.replace(artifact, "").strip()
        
        return result
    
    async def _convert_to_wav(self, input_path: str) -> Optional[str]:
        """WebM/Opus dosyasını WAV'a çevir (FFmpeg gerekli)."""
        import subprocess
        
        output_path = input_path.replace(os.path.splitext(input_path)[1], "_converted.wav")
        
        try:
            result = subprocess.run([
                "ffmpeg", "-y", "-i", input_path,
                "-ar", "16000", "-ac", "1",
                output_path
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 and os.path.exists(output_path):
                return output_path
            return None
        except Exception:
            return None


# Singleton instance
speech_service = SpeechService()

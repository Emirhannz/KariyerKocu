"""
KariyerKoçu - Mülakat Modelleri
===============================
Mülakat oturumu, soru ve cevap modelleri.
"""

from datetime import datetime
from sqlalchemy import Column, String, DateTime, JSON, ForeignKey, Integer, Text, Float, Boolean, Enum
from sqlalchemy.orm import relationship
from app.database import Base
import uuid
import enum


class InterviewStatus(str, enum.Enum):
    """Mülakat durumu."""
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class QuestionType(str, enum.Enum):
    """Soru türü."""
    TECHNICAL = "technical"      # Teknik bilgi sorusu
    CV_BASED = "cv_based"        # CV'deki proje hakkında
    SCENARIO = "scenario"        # Senaryo bazlı problem çözme
    BEHAVIORAL = "behavioral"    # Davranışsal soru


class InterviewSession(Base):
    """Mülakat oturumu."""
    
    __tablename__ = "interview_sessions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    cv_id = Column(String, ForeignKey("cvs.id"), nullable=True)  # CV yoksa da mülakat yapılabilir
    
    # Mülakat ayarları
    company_sector = Column(String, nullable=False)
    position = Column(String, nullable=False)
    experience_level = Column(String, nullable=False)
    interview_type = Column(String, nullable=False)  # sektorel / sektor_yorum
    
    # Durum
    status = Column(String, default=InterviewStatus.IN_PROGRESS)
    current_question_number = Column(Integer, default=0)
    total_questions = Column(Integer, default=7)
    
    # Skorlar (mülakat bitince hesaplanır)
    total_score = Column(Float, nullable=True)
    average_score = Column(Float, nullable=True)
    
    # Zaman damgaları
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # İlişkiler
    questions = relationship("InterviewQuestion", back_populates="session", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<InterviewSession {self.id[:8]} - {self.position} ({self.status})>"


class InterviewQuestion(Base):
    """Mülakat sorusu."""
    
    __tablename__ = "interview_questions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey("interview_sessions.id"), nullable=False)
    
    # Soru bilgileri
    question_number = Column(Integer, nullable=False)
    question_text = Column(Text, nullable=False)  # Kullanıcıya gösterilecek (Deepfake, API, vs.)
    question_tts = Column(Text, nullable=True)    # TTS için Türkçe telaffuz (Dipfeyk, Ey Pi Ay, vs.)
    question_type = Column(String, default=QuestionType.TECHNICAL)
    
    # Önceki soruyla bağlantı (geçiş cümlesi için)
    transition_text = Column(Text, nullable=True)  # "Güzel, şimdi şu konuya geçelim..."
    transition_tts = Column(Text, nullable=True)   # Geçiş metninin TTS versiyonu
    
    # Cevap durumu
    is_answered = Column(Boolean, default=False)
    
    # Zaman damgaları
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # İlişkiler
    session = relationship("InterviewSession", back_populates="questions")
    answer = relationship("InterviewAnswer", back_populates="question", uselist=False, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<InterviewQuestion #{self.question_number} - {self.question_type}>"


class InterviewAnswer(Base):
    """Mülakat cevabı ve değerlendirmesi."""
    
    __tablename__ = "interview_answers"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    question_id = Column(String, ForeignKey("interview_questions.id"), nullable=False)
    
    # Kullanıcı cevabı
    user_answer = Column(Text, nullable=False)
    
    # LLM değerlendirmesi (mülakat bitene kadar kullanıcıya gösterilmez)
    score = Column(Integer, nullable=True)  # 1-10
    evaluation_reason = Column(Text, nullable=True)  # Neden bu puan?
    ideal_answer = Column(Text, nullable=True)  # İdeal cevap ne olmalıydı
    strengths = Column(JSON, nullable=True)  # ["güçlü yön 1", "güçlü yön 2"]
    weaknesses = Column(JSON, nullable=True)  # ["eksik 1", "eksik 2"]
    
    # Zaman damgaları
    answered_at = Column(DateTime, default=datetime.utcnow)
    
    # İlişkiler
    question = relationship("InterviewQuestion", back_populates="answer")
    
    def __repr__(self):
        return f"<InterviewAnswer - Score: {self.score}/10>"

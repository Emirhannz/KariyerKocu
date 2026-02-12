import { useEffect, useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { 
  Loader2, 
  MessageSquare, 
  Building, 
  Briefcase, 
  Trophy,
  FileQuestion,
  AlertCircle,
  XCircle,
  Mic,
  Keyboard,
  User
} from 'lucide-react';
import api from '../../lib/api';
import { useAuthStore } from '../../stores/authStore';
import type { InterviewConfig } from '../../types';

interface ActiveSession {
  session_id: string;
  interview_settings: Record<string, string>;
  total_questions: number;
}

export function InterviewStartPage() {
  const navigate = useNavigate();
  const { user } = useAuthStore();
  
  // Config
  const [config, setConfig] = useState<InterviewConfig | null>(null);
  const [loadingConfig, setLoadingConfig] = useState(true);
  
  // Active session check
  const [activeSession, setActiveSession] = useState<ActiveSession | null>(null);
  
  // Form state
  const [sector, setSector] = useState('');
  const [position, setPosition] = useState('');
  const [experienceLevel, setExperienceLevel] = useState('');
  const [interviewType, setInterviewType] = useState('');
  const [questionCount, setQuestionCount] = useState(7);
  
  // Yeni: Mülakat modu ve ses tercihi
  const [interviewMode, setInterviewMode] = useState<'text' | 'voice'>('text');
  const [voiceGender, setVoiceGender] = useState<'male' | 'female'>('male');
  
  // Submit state
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Check for active session on mount
  useEffect(() => {
    const stored = localStorage.getItem('interview_session');
    if (stored) {
      try {
        const session = JSON.parse(stored);
        setActiveSession(session);
      } catch {
        // Invalid session, clear it
        localStorage.removeItem('interview_session');
      }
    }
  }, []);

  // Fetch config on mount
  useEffect(() => {
    const fetchConfig = async () => {
      try {
        const response = await api.get<InterviewConfig>('/interview/config');
        setConfig(response.data);
      } catch (err) {
        setError('Konfigürasyon yüklenemedi');
      } finally {
        setLoadingConfig(false);
      }
    };
    fetchConfig();
  }, []);

  // Available positions based on selected sector
  const availablePositions = sector && config?.positions ? config.positions[sector] || [] : [];

  const handleCancelActiveSession = async () => {
    if (!activeSession) return;
    
    try {
      // Optionally notify backend (if endpoint exists)
      try {
        await api.post(`/interview/abandon?session_id=${activeSession.session_id}`);
      } catch {
        // Backend might not have this endpoint, that's OK
      }
    } finally {
      // Always clear local storage
      localStorage.removeItem('interview_session');
      setActiveSession(null);
    }
  };



  const handleStartInterview = async () => {
    if (!sector || !position || !experienceLevel || !interviewType) {
      setError('Lütfen tüm alanları doldurun');
      return;
    }

    setSubmitting(true);
    setError(null);

    try {
      const response = await api.post('/interview/start', {
        company_sector: sector,
        position: position,
        experience_level: experienceLevel,
        interview_type: interviewType,
        question_count: questionCount,
        interview_mode: interviewMode,
        voice_gender: voiceGender,
      });
      
      // Store session in localStorage with user_id for multi-user safety
      const sessionData = {
        ...response.data,
        user_id: user?.id  // Kullanıcı ID'sini ekle
      };
      localStorage.setItem('interview_session', JSON.stringify(sessionData));
      
      // Sesli modda voice-session, yazılı modda normal session sayfasına git
      if (interviewMode === 'voice') {
        navigate('/interview/voice-session');
      } else {
        navigate('/interview/session');
      }
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } };
      setError(error.response?.data?.detail || 'Mülakat başlatılamadı');
    } finally {
      setSubmitting(false);
    }
  };

  if (loadingConfig) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">Mülakat Simülasyonu</h1>
        <p className="text-muted-foreground mt-2">
          Yapay zeka ile gerçekçi mülakat pratiği yap
        </p>
      </div>

      {/* Active Session Warning */}
      {activeSession && (
        <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-xl p-6 space-y-4">
          <div className="flex items-start gap-3">
            <AlertCircle className="h-6 w-6 text-yellow-500 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="font-semibold text-yellow-600">Devam Eden Mülakat Var</h3>
              <p className="text-sm text-muted-foreground mt-1">
                {activeSession.interview_settings?.position_name || 'Mülakat'} pozisyonu için 
                başladığınız bir mülakat var. Yeni bir mülakat başlatmak için önce mevcut mülakatı iptal etmelisiniz.
              </p>
            </div>
          </div>
          
          <button
            onClick={handleCancelActiveSession}
            className="w-full py-3 rounded-lg border border-red-500/50 text-red-500 font-medium flex items-center justify-center gap-2 hover:bg-red-500/10 transition-colors"
          >
            <XCircle className="h-5 w-5" />
            Mülakatı İptal Et
          </button>
        </div>
      )}

      {/* Form - Only show if no active session */}
      {!activeSession && (
        <>
          <div className="bg-card border border-border rounded-xl p-6 space-y-6">
            
            {/* Sector Selection */}
            <div className="space-y-3">
              <label className="flex items-center gap-2 font-medium">
                <Building className="h-5 w-5 text-primary" />
                Firma Sektörü
              </label>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                {config?.sectors.map((s) => (
                  <button
                    key={s.id}
                    onClick={() => { setSector(s.id); setPosition(''); }}
                    className={`p-3 rounded-lg border text-sm font-medium transition-all ${
                      sector === s.id
                        ? 'border-primary bg-primary/10 text-primary'
                        : 'border-border hover:border-primary/50'
                    }`}
                  >
                    {s.name}
                  </button>
                ))}
              </div>
            </div>

            {/* Position Selection */}
            {sector && (
              <div className="space-y-3">
                <label className="flex items-center gap-2 font-medium">
                  <Briefcase className="h-5 w-5 text-purple-500" />
                  Pozisyon
                </label>
                <div className="grid grid-cols-2 gap-2">
                  {availablePositions.map((p) => (
                    <button
                      key={p.id}
                      onClick={() => setPosition(p.id)}
                      className={`p-3 rounded-lg border text-sm font-medium transition-all text-left ${
                        position === p.id
                          ? 'border-primary bg-primary/10 text-primary'
                          : 'border-border hover:border-primary/50'
                      }`}
                    >
                      {p.name}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Experience Level */}
            <div className="space-y-3">
              <label className="flex items-center gap-2 font-medium">
                <Trophy className="h-5 w-5 text-yellow-500" />
                Tecrübe Seviyesi
              </label>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                {config?.experience_levels.map((e) => (
                  <button
                    key={e.id}
                    onClick={() => setExperienceLevel(e.id)}
                    className={`p-3 rounded-lg border text-sm font-medium transition-all ${
                      experienceLevel === e.id
                        ? 'border-primary bg-primary/10 text-primary'
                        : 'border-border hover:border-primary/50'
                    }`}
                  >
                    {e.name}
                  </button>
                ))}
              </div>
            </div>

            {/* Interview Type */}
            <div className="space-y-3">
              <label className="flex items-center gap-2 font-medium">
                <FileQuestion className="h-5 w-5 text-green-500" />
                Mülakat Tipi
              </label>
              <div className="grid grid-cols-1 gap-2">
                {config?.interview_types.map((t) => (
                  <button
                    key={t.id}
                    onClick={() => setInterviewType(t.id)}
                    className={`p-4 rounded-lg border text-left transition-all ${
                      interviewType === t.id
                        ? 'border-primary bg-primary/10'
                        : 'border-border hover:border-primary/50'
                    }`}
                  >
                    <span className={`font-medium ${interviewType === t.id ? 'text-primary' : ''}`}>
                      {t.name}
                    </span>
                    <p className="text-sm text-muted-foreground mt-1">{t.description}</p>
                  </button>
                ))}
              </div>
            </div>

            {/* Interview Mode - Yazılı/Sesli */}
            <div className="space-y-3">
              <label className="flex items-center gap-2 font-medium">
                <Mic className="h-5 w-5 text-pink-500" />
                Mülakat Modu
              </label>
              <div className="grid grid-cols-2 gap-3">
                <button
                  onClick={() => setInterviewMode('text')}
                  className={`p-4 rounded-lg border text-left transition-all ${
                    interviewMode === 'text'
                      ? 'border-primary bg-primary/10'
                      : 'border-border hover:border-primary/50'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <Keyboard className={`h-6 w-6 ${interviewMode === 'text' ? 'text-primary' : 'text-muted-foreground'}`} />
                    <div>
                      <span className={`font-medium block ${interviewMode === 'text' ? 'text-primary' : ''}`}>
                        Yazılı Mülakat
                      </span>
                      <p className="text-xs text-muted-foreground mt-0.5">Sorular ve cevaplar yazılı</p>
                    </div>
                  </div>
                </button>
                <button
                  onClick={() => setInterviewMode('voice')}
                  className={`p-4 rounded-lg border text-left transition-all ${
                    interviewMode === 'voice'
                      ? 'border-primary bg-primary/10'
                      : 'border-border hover:border-primary/50'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <Mic className={`h-6 w-6 ${interviewMode === 'voice' ? 'text-primary' : 'text-muted-foreground'}`} />
                    <div>
                      <span className={`font-medium block ${interviewMode === 'voice' ? 'text-primary' : ''}`}>
                        Sesli Mülakat
                      </span>
                      <p className="text-xs text-muted-foreground mt-0.5">AI konuşur, sen konuş</p>
                    </div>
                  </div>
                </button>
              </div>
            </div>

            {/* Voice Gender - Sadece Sesli modda göster */}
            {interviewMode === 'voice' && (
              <div className="space-y-3">
                <label className="flex items-center gap-2 font-medium">
                  <User className="h-5 w-5 text-cyan-500" />
                  AI Sesi
                </label>
                <div className="grid grid-cols-2 gap-3">
                  <button
                    onClick={() => setVoiceGender('male')}
                    className={`p-3 rounded-lg border text-sm font-medium transition-all flex items-center justify-center gap-2 ${
                      voiceGender === 'male'
                        ? 'border-primary bg-primary/10 text-primary'
                        : 'border-border hover:border-primary/50'
                    }`}
                  >
                    👨 Ahmet (Erkek)
                  </button>
                  <button
                    onClick={() => setVoiceGender('female')}
                    className={`p-3 rounded-lg border text-sm font-medium transition-all flex items-center justify-center gap-2 ${
                      voiceGender === 'female'
                        ? 'border-primary bg-primary/10 text-primary'
                        : 'border-border hover:border-primary/50'
                    }`}
                  >
                    👩 Emel (Kadın)
                  </button>
                </div>
              </div>
            )}

            {/* Question Count */}
            <div className="space-y-3">
              <label className="flex items-center gap-2 font-medium">
                <MessageSquare className="h-5 w-5 text-blue-500" />
                Soru Sayısı: <span className="text-primary">{questionCount}</span>
              </label>
              <input
                type="range"
                min="1"
                max="7"
                value={questionCount}
                onChange={(e) => setQuestionCount(parseInt(e.target.value))}
                className="w-full h-2 bg-muted rounded-lg appearance-none cursor-pointer accent-primary"
              />
              <div className="flex justify-between text-xs text-muted-foreground">
                <span>1 (Kısa)</span>
                <span>7 (Detaylı)</span>
              </div>
            </div>

            {/* Error */}
            {error && (
              <div className="flex items-center gap-2 p-4 rounded-lg bg-destructive/10 text-destructive">
                <AlertCircle className="h-5 w-5 flex-shrink-0" />
                <p className="text-sm">{error}</p>
              </div>
            )}

            {/* Submit */}
            <button
              onClick={handleStartInterview}
              disabled={submitting || !sector || !position || !experienceLevel || !interviewType}
              className="w-full py-4 rounded-lg gradient-primary text-white font-medium flex items-center justify-center gap-2 hover:opacity-90 disabled:opacity-50 transition-opacity text-lg"
            >
              {submitting ? (
                <>
                  <Loader2 className="h-5 w-5 animate-spin" />
                  Mülakat Başlatılıyor...
                </>
              ) : (
                <>
                  <MessageSquare className="h-5 w-5" />
                  Mülakata Başla
                </>
              )}
            </button>
          </div>

          {/* Tips */}
          <div className="bg-muted/50 rounded-xl p-4 text-sm text-muted-foreground">
            <p className="font-medium text-foreground mb-2">💡 İpuçları</p>
            <ul className="space-y-1">
              <li>• Sorulara detaylı ve örneklerle cevap verin</li>
              <li>• Teknik sorularda kod veya yaklaşım açıklayın</li>
              <li>• Her cevap için en az 2-3 cümle yazın</li>
            </ul>
          </div>
        </>
      )}

      {/* Interview History Link */}
      <div className="text-center">
        <Link 
          to="/interview/history" 
          className="text-sm text-muted-foreground hover:text-primary transition-colors"
        >
          Geçmiş mülakatlarımı görüntüle →
        </Link>
      </div>
    </div>
  );
}

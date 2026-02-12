import { useEffect, useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Loader2, 
  User, 
  Bot,
  AlertCircle,
  CheckCircle,
  Mic,
  MicOff,
  Play,
  Pause,
  Volume2,
  FileText,
  ChevronDown,
  ChevronUp
} from 'lucide-react';
import api from '../../lib/api';

interface InterviewSession {
  session_id: string;
  message: string;
  total_questions: number;
  interview_settings: Record<string, string>;
}

interface Question {
  session_id: string;
  question_id: string;
  question_number: number;
  total_questions: number;
  transition_text: string | null;
  transition_tts: string | null;  // TTS için Türkçe telaffuz versiyonu
  question_text: string;
  question_tts: string | null;    // TTS için Türkçe telaffuz versiyonu
  question_type: string;
  is_last_question: boolean;
}

interface ChatMessage {
  type: 'bot' | 'user';
  content: string;
  audioUrl?: string;
  isTransition?: boolean;
  isPlayed?: boolean;
}

export function VoiceInterviewPage() {
  const navigate = useNavigate();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const audioRef = useRef<HTMLAudioElement>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const initialized = useRef(false);
  
  // Session state
  const [session, setSession] = useState<InterviewSession | null>(null);
  const [currentQuestion, setCurrentQuestion] = useState<Question | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [voiceGender, setVoiceGender] = useState<'male' | 'female'>('male');
  
  // Audio state  
  const [isPlaying, setIsPlaying] = useState(false);
  const [playingIndex, setPlayingIndex] = useState<number | null>(null);
  const [audioProgress, setAudioProgress] = useState(0);
  const [audioDuration, setAudioDuration] = useState(0);
  const [isRecording, setIsRecording] = useState(false);
  
  // Text visibility state
  const [expandedTexts, setExpandedTexts] = useState<Set<number>>(new Set());
  
  // UI state
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [completed, setCompleted] = useState(false);

  // Load session and get first question
  useEffect(() => {
    const loadSession = async () => {
      if (initialized.current) return;
      initialized.current = true;

      const stored = localStorage.getItem('interview_session');
      if (!stored) {
        navigate('/interview/start');
        return;
      }

      try {
        const sessionData: InterviewSession = JSON.parse(stored);
        setSession(sessionData);
        
        // Get voice preference from session settings
        const gender = sessionData.interview_settings?.voice_gender || 'male';
        setVoiceGender(gender as 'male' | 'female');
        
        // Welcome message
        const positionName = sessionData.interview_settings?.position_name || 'bu pozisyon';
        const welcomeMessage = `Merhaba! ${positionName} sesli mülakatına hoş geldiniz. Sorularımı dinleyip mikrofon butonuna basarak cevap verebilirsiniz. Başarılar!`;
        
        // Create audio for welcome message
        const welcomeAudio = await generateTTSUrl(welcomeMessage, gender as 'male' | 'female');
        
        setMessages([{
          type: 'bot',
          content: welcomeMessage,
          audioUrl: welcomeAudio,
          isPlayed: false
        }]);

        // Fetch first question
        const response = await api.get<Question>(`/interview/question?session_id=${sessionData.session_id}`);
        setCurrentQuestion(response.data);
        
        // Add question to chat with audio
        await addQuestionToChat(response.data, gender as 'male' | 'female');
      } catch (err) {
        setError('Mülakat yüklenemedi');
      } finally {
        setLoading(false);
      }
    };

    loadSession();
  }, [navigate]);

  // Scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Audio time update handler
  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    const handleTimeUpdate = () => {
      setAudioProgress(audio.currentTime);
    };

    const handleLoadedMetadata = () => {
      setAudioDuration(audio.duration);
    };

    const handleEnded = () => {
      setIsPlaying(false);
      if (playingIndex !== null) {
        setMessages(prev => prev.map((m, i) => 
          i === playingIndex ? { ...m, isPlayed: true } : m
        ));
      }
      setPlayingIndex(null);
      setAudioProgress(0);
    };

    audio.addEventListener('timeupdate', handleTimeUpdate);
    audio.addEventListener('loadedmetadata', handleLoadedMetadata);
    audio.addEventListener('ended', handleEnded);

    return () => {
      audio.removeEventListener('timeupdate', handleTimeUpdate);
      audio.removeEventListener('loadedmetadata', handleLoadedMetadata);
      audio.removeEventListener('ended', handleEnded);
    };
  }, [playingIndex]);

  // Generate TTS audio URL
  const generateTTSUrl = async (text: string, gender: 'male' | 'female'): Promise<string> => {
    try {
      const response = await api.post('/interview/voice/tts', {
        text,
        voice_gender: gender
      }, {
        responseType: 'blob'
      });
      
      const audioBlob = new Blob([response.data], { type: 'audio/mpeg' });
      return URL.createObjectURL(audioBlob);
    } catch (err) {
      console.error('TTS error:', err);
      return '';
    }
  };

  // Play/Pause audio for a message
  const togglePlayMessage = async (index: number) => {
    const message = messages[index];
    if (!message.audioUrl) return;
    
    const audio = audioRef.current;
    if (!audio) return;

    // If clicking the same message that's playing
    if (playingIndex === index) {
      if (isPlaying) {
        // Pause - kaldığı yeri hatırla
        audio.pause();
        setIsPlaying(false);
      } else {
        // Resume - kaldığı yerden devam et
        audio.play();
        setIsPlaying(true);
      }
      return;
    }

    // If playing different message, stop current and play new
    if (isPlaying && playingIndex !== null) {
      audio.pause();
    }

    // Start playing new message
    audio.src = message.audioUrl;
    audio.currentTime = 0;
    setPlayingIndex(index);
    setIsPlaying(true);
    setAudioProgress(0);
    audio.play();
  };

  // Seek audio
  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    const audio = audioRef.current;
    if (!audio) return;
    
    const newTime = parseFloat(e.target.value);
    audio.currentTime = newTime;
    setAudioProgress(newTime);
  };

  // Toggle text visibility
  const toggleTextVisibility = (index: number) => {
    setExpandedTexts(prev => {
      const newSet = new Set(prev);
      if (newSet.has(index)) {
        newSet.delete(index);
      } else {
        newSet.add(index);
      }
      return newSet;
    });
  };

  // Format time (seconds to mm:ss)
  const formatTime = (seconds: number): string => {
    if (!seconds || isNaN(seconds)) return '0:00';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const addQuestionToChat = async (question: Question, gender: 'male' | 'female') => {
    // Transition text - Değerlendirme/geçiş mesajı
    // TTS için transition_text kullan (LLM'in ürettiği TTS versiyonunu DEĞİL)
    // TTS servisi kendi sözlüğü ile İngilizce terimleri dönüştürecek
    if (question.transition_text) {
      const transitionAudio = await generateTTSUrl(question.transition_text, gender);
      setMessages(prev => [...prev, {
        type: 'bot',
        content: question.transition_text!,
        audioUrl: transitionAudio,
        isTransition: true,
        isPlayed: false
      }]);
    }
    
    // Question - Soru için question_tts kullan (LLM'in ürettiği fonetik versiyon)
    const ttsText = question.question_tts || question.question_text;
    const questionAudio = await generateTTSUrl(ttsText, gender);
    setMessages(prev => [...prev, {
      type: 'bot',
      content: question.question_text,  // Ekranda normal metin göster
      audioUrl: questionAudio,
      isPlayed: false
    }]);
  };

  // Start recording
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      
      const chunks: Blob[] = [];
      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunks.push(e.data);
        }
      };
      
      mediaRecorder.onstop = async () => {
        stream.getTracks().forEach(track => track.stop());
        // Send the recording
        await sendRecording(chunks);
      };
      
      mediaRecorder.start();
      setIsRecording(true);
    } catch (err) {
      setError('Mikrofon erişimi reddedildi');
    }
  };

  // Stop recording and send
  const stopRecording = () => {
    if (!mediaRecorderRef.current) return;
    mediaRecorderRef.current.stop();
    setIsRecording(false);
  };

  const sendRecording = async (chunks: Blob[]) => {
    if (!currentQuestion || !session || chunks.length === 0) return;
    
    setProcessing(true);
    setError(null);

    try {
      // Create audio blob
      const audioBlob = new Blob(chunks, { type: 'audio/webm' });
      
      // Send to voice-answer endpoint
      const formData = new FormData();
      formData.append('audio', audioBlob, 'recording.webm');
      
      const response = await api.post(`/interview/voice/voice-answer/${session.session_id}`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      
      // Add user response to chat (as voice message indicator)
      setMessages(prev => [...prev, {
        type: 'user',
        content: `🎤 Sesli yanıt: "${response.data.transcribed_text.substring(0, 50)}${response.data.transcribed_text.length > 50 ? '...' : ''}"`
      }]);
      
      // Play feedback if any
      if (response.data.evaluation?.feedback) {
        const feedbackAudio = await generateTTSUrl(response.data.evaluation.feedback, voiceGender);
        setMessages(prev => [...prev, {
          type: 'bot',
          content: response.data.evaluation.feedback,
          audioUrl: feedbackAudio,
          isTransition: true,
          isPlayed: false
        }]);
      }
      
      // Check if complete
      if (response.data.is_complete) {
        await api.post(`/interview/complete?session_id=${session.session_id}`);
        setCompleted(true);
        
        const completionMessage = 'Mülakat tamamlandı! Sonuçlarınız hazırlanıyor...';
        const completionAudio = await generateTTSUrl(completionMessage, voiceGender);
        setMessages(prev => [...prev, {
          type: 'bot',
          content: `🎉 ${completionMessage}`,
          audioUrl: completionAudio,
          isPlayed: false
        }]);
        
        setTimeout(() => {
          navigate(`/interview/report/${session.session_id}`);
        }, 3000);
      } else {
        // Get next question
        const questionResponse = await api.get<Question>(`/interview/question?session_id=${session.session_id}`);
        setCurrentQuestion(questionResponse.data);
        await addQuestionToChat(questionResponse.data, voiceGender);
      }
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } };
      setError(error.response?.data?.detail || 'Cevap gönderilemedi');
    } finally {
      setProcessing(false);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-6">
        <div className="relative">
          <Loader2 className="h-16 w-16 animate-spin text-primary" />
          <Volume2 className="h-6 w-6 text-primary absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2" />
        </div>
        <div className="text-center space-y-2">
          <h2 className="text-xl font-semibold">Sesli Mülakat Hazırlanıyor</h2>
          <p className="text-muted-foreground">
            Yapay zeka mülakatçınız hazırlanıyor...
          </p>
          <p className="text-sm text-muted-foreground">
            Bu işlem 30-60 saniye sürebilir
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto flex flex-col h-[calc(100vh-10rem)]">
      {/* Hidden audio element */}
      <audio ref={audioRef} className="hidden" />
      
      {/* Header */}
      <div className="flex items-center justify-between pb-4 border-b border-border">
        <div>
          <h1 className="text-xl font-bold flex items-center gap-2">
            <Volume2 className="h-5 w-5 text-primary" />
            Sesli Mülakat
          </h1>
          {session && (
            <p className="text-sm text-muted-foreground">
              {session.interview_settings.position_name} • {session.interview_settings.experience_level_name}
            </p>
          )}
        </div>
        {currentQuestion && !completed && (
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-primary/10 text-primary text-sm">
            <span className="font-medium">{currentQuestion.question_number}</span>
            <span>/</span>
            <span>{currentQuestion.total_questions}</span>
          </div>
        )}
        {completed && (
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-green-500/10 text-green-500 text-sm">
            <CheckCircle className="h-4 w-4" />
            Tamamlandı
          </div>
        )}
      </div>

      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto py-4 space-y-4">
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`flex gap-3 ${msg.type === 'user' ? 'flex-row-reverse' : ''}`}
          >
            {/* Avatar */}
            <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
              msg.type === 'bot' ? 'bg-primary/10' : 'bg-muted'
            }`}>
              {msg.type === 'bot' ? (
                <Bot className="h-4 w-4 text-primary" />
              ) : (
                <User className="h-4 w-4 text-muted-foreground" />
              )}
            </div>
            
            {/* Message - Voice Style for bot messages */}
            <div className={`max-w-[80%] ${msg.type === 'user' ? 'text-right' : ''}`}>
              {msg.type === 'bot' && msg.audioUrl ? (
                // Voice message style - with progress bar and text toggle
                <div className={`p-4 rounded-2xl ${
                  msg.isTransition 
                    ? 'bg-blue-500/10 border border-blue-500/20'
                    : 'bg-card border border-border'
                }`}>
                  {/* Header with play button */}
                  <div className="flex items-center gap-3">
                    <button
                      onClick={() => togglePlayMessage(i)}
                      className={`w-12 h-12 rounded-full flex items-center justify-center transition-all flex-shrink-0 ${
                        playingIndex === i && isPlaying
                          ? 'bg-primary text-white' 
                          : msg.isPlayed 
                            ? 'bg-green-500/20 text-green-500 hover:bg-green-500/30' 
                            : 'bg-primary/20 text-primary hover:bg-primary/30'
                      }`}
                    >
                      {playingIndex === i && isPlaying ? (
                        <Pause className="h-5 w-5" />
                      ) : (
                        <Play className="h-5 w-5 ml-0.5" />
                      )}
                    </button>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-medium">
                          {msg.isTransition ? '💬 Değerlendirme' : '🎯 Soru'}
                        </span>
                        {msg.isPlayed && (
                          <span className="text-xs text-green-500">✓ Dinlendi</span>
                        )}
                      </div>
                      
                      {/* Progress bar - only show when this message is playing */}
                      {playingIndex === i && (
                        <div className="mt-2 flex items-center gap-2">
                          <span className="text-xs text-muted-foreground w-10">
                            {formatTime(audioProgress)}
                          </span>
                          <input
                            type="range"
                            min="0"
                            max={audioDuration || 100}
                            value={audioProgress}
                            onChange={handleSeek}
                            className="flex-1 h-1.5 bg-muted rounded-lg appearance-none cursor-pointer accent-primary"
                          />
                          <span className="text-xs text-muted-foreground w-10 text-right">
                            {formatTime(audioDuration)}
                          </span>
                        </div>
                      )}
                      
                      {/* Preview text */}
                      {!expandedTexts.has(i) && (
                        <p className="text-xs text-muted-foreground mt-1 truncate">
                          {msg.content.substring(0, 60)}...
                        </p>
                      )}
                    </div>
                  </div>
                  
                  {/* Expanded full text */}
                  {expandedTexts.has(i) && (
                    <div className="mt-3 p-3 bg-muted/50 rounded-lg">
                      <p className="text-sm whitespace-pre-wrap">{(msg.content || '').replace(/\\n/g, '\n')}</p>
                    </div>
                  )}
                  
                  {/* Text toggle button */}
                  <button
                    onClick={() => toggleTextVisibility(i)}
                    className="mt-3 w-full flex items-center justify-center gap-1 text-xs text-muted-foreground hover:text-foreground transition-colors py-1"
                  >
                    <FileText className="h-3 w-3" />
                    {expandedTexts.has(i) ? (
                      <>Metni Gizle <ChevronUp className="h-3 w-3" /></>
                    ) : (
                      <>Metni Göster <ChevronDown className="h-3 w-3" /></>
                    )}
                  </button>
                </div>
              ) : (
                // Regular text message for user
                <div className={`p-4 rounded-2xl break-words ${
                  msg.type === 'bot'
                    ? 'bg-card border border-border'
                    : 'bg-primary text-primary-foreground'
                }`}>
                  <p className="whitespace-pre-wrap text-left">{(msg.content || '').replace(/\\n/g, '\n')}</p>
                </div>
              )}
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Voice Controls */}
      {!completed && (
        <div className="pt-4 border-t border-border">
          {error && (
            <div className="flex items-center gap-2 mb-3 p-3 rounded-lg bg-destructive/10 text-destructive text-sm">
              <AlertCircle className="h-4 w-4 flex-shrink-0" />
              {error}
            </div>
          )}
          
          {/* Status indicator */}
          <div className="text-center mb-4">
            {processing && (
              <div className="flex items-center justify-center gap-2 text-yellow-500">
                <Loader2 className="h-5 w-5 animate-spin" />
                <span>Cevabınız işleniyor...</span>
              </div>
            )}
            {isRecording && (
              <div className="flex items-center justify-center gap-2 text-red-500">
                <div className="w-3 h-3 rounded-full bg-red-500 animate-pulse" />
                <span>Kayıt yapılıyor... Bitirmek için tekrar basın</span>
              </div>
            )}
            {!isRecording && !processing && (
              <div className="flex items-center justify-center gap-2 text-muted-foreground">
                <Mic className="h-5 w-5" />
                <span>Önce soruyu dinleyin, sonra cevap vermek için mikrofona basın</span>
              </div>
            )}
          </div>
          
          {/* Control buttons */}
          <div className="flex justify-center gap-4">
            {!isRecording ? (
              <button
                onClick={startRecording}
                disabled={processing}
                className="p-6 rounded-full bg-primary text-white hover:opacity-90 disabled:opacity-50 transition-all shadow-lg hover:shadow-xl"
                title="Kayda başla"
              >
                <Mic className="h-8 w-8" />
              </button>
            ) : (
              <button
                onClick={stopRecording}
                className="p-6 rounded-full bg-red-500 text-white hover:opacity-90 transition-all shadow-lg hover:shadow-xl animate-pulse"
                title="Kaydı bitir ve gönder"
              >
                <MicOff className="h-8 w-8" />
              </button>
            )}
          </div>
          
          <p className="text-xs text-muted-foreground mt-4 text-center">
            {voiceGender === 'male' ? '👨 Ahmet' : '👩 Emel'} sesiyle mülakatınız yürütülüyor
          </p>
        </div>
      )}
    </div>
  );
}

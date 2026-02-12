import { useEffect, useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Loader2, 
  Send, 
  User, 
  Bot,
  AlertCircle,
  CheckCircle
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
  question_text: string;
  question_type: string;
  is_last_question: boolean;
}

interface ChatMessage {
  type: 'bot' | 'user';
  content: string;
  questionType?: string;
  isTransition?: boolean;
}

export function InterviewSessionPage() {
  const navigate = useNavigate();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  // FIX #1: Prevent double-fetch with useRef
  const initialized = useRef(false);
  
  // Session state
  const [session, setSession] = useState<InterviewSession | null>(null);
  const [currentQuestion, setCurrentQuestion] = useState<Question | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  
  // Input state
  const [answer, setAnswer] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [completed, setCompleted] = useState(false);

  // Load session from localStorage and get first question
  useEffect(() => {
    const loadSession = async () => {
      // FIX #1: Only run once (prevent React StrictMode double-fetch)
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
        
        // FIX #2: Custom friendly welcome message instead of backend message
        const positionName = sessionData.interview_settings?.position_name || 'bu pozisyon';
        const welcomeMessage = `Merhaba! ${positionName} mülakatına hoş geldiniz. Sorularımı dikkatlice okuyup cevaplamaya hazır olduğunuzda başlayabiliriz. Başarılar! 🎯`;
        
        setMessages([{
          type: 'bot',
          content: welcomeMessage
        }]);

        // Fetch first question
        const response = await api.get<Question>(`/interview/question?session_id=${sessionData.session_id}`);
        setCurrentQuestion(response.data);
        
        // Add question to chat
        addQuestionToChat(response.data);
      } catch (err) {
        setError('Mülakat yüklenemedi');
      } finally {
        setLoading(false);
      }
    };

    loadSession();
  }, [navigate]);

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const addQuestionToChat = (question: Question) => {
    const newMessages: ChatMessage[] = [];
    
    // FIX #3: Transition text is a bridge/feedback, mark appropriately
    if (question.transition_text) {
      newMessages.push({
        type: 'bot',
        content: question.transition_text,
        isTransition: true
      });
    }
    
    newMessages.push({
      type: 'bot',
      content: question.question_text,
      questionType: question.question_type
    });
    
    setMessages(prev => [...prev, ...newMessages]);
  };

  const handleSubmitAnswer = async () => {
    if (!answer.trim() || answer.length < 10 || !currentQuestion || !session) {
      if (answer.length < 10) {
        setError('Cevabınız en az 10 karakter olmalı');
      }
      return;
    }

    setSubmitting(true);
    setError(null);

    // Add user answer to chat
    setMessages(prev => [...prev, { type: 'user', content: answer }]);
    const currentAnswer = answer;
    setAnswer('');

    try {
      // Submit answer
      const response = await api.post('/interview/answer', {
        session_id: session.session_id,
        question_id: currentQuestion.question_id,
        answer: currentAnswer
      });

      // Check if there's a next question
      if (response.data.has_next_question) {
        // Fetch next question
        const questionResponse = await api.get<Question>(`/interview/question?session_id=${session.session_id}`);
        setCurrentQuestion(questionResponse.data);
        addQuestionToChat(questionResponse.data);
      } else {
        // Complete interview
        await api.post(`/interview/complete?session_id=${session.session_id}`);
        setCompleted(true);
        setMessages(prev => [...prev, {
          type: 'bot',
          content: '🎉 Mülakat tamamlandı! Sonuçlarınız hazırlanıyor...'
        }]);
        
        // Navigate to report after a delay
        setTimeout(() => {
          navigate(`/interview/report/${session.session_id}`);
        }, 2000);
      }
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } };
      setError(error.response?.data?.detail || 'Cevap gönderilemedi');
      // Remove the user message if there was an error
      setMessages(prev => prev.slice(0, -1));
      setAnswer(currentAnswer);
    } finally {
      setSubmitting(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmitAnswer();
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto flex flex-col h-[calc(100vh-10rem)]">
      {/* Header */}
      <div className="flex items-center justify-between pb-4 border-b border-border">
        <div>
          <h1 className="text-xl font-bold">Mülakat Simülasyonu</h1>
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
            
            {/* Message */}
            <div className={`max-w-[80%] ${msg.type === 'user' ? 'text-right' : ''}`}>
              {msg.questionType && (
                <span className="inline-block mb-1 px-2 py-0.5 rounded text-xs bg-muted text-muted-foreground">
                  {msg.questionType === 'TECHNICAL' ? '⚙️ Teknik Soru' :
                   msg.questionType === 'CV_BASED' ? '📄 CV Sorusu' :
                   msg.questionType === 'SCENARIO' ? '🎯 Senaryo Sorusu' :
                   msg.questionType === 'BEHAVIORAL' ? '🧠 Davranışsal Soru' : ''}
                </span>
              )}
              {/* FIX #3: Transition messages styled as blue info bubble, not faded */}
              <div className={`p-4 rounded-2xl break-words ${
                msg.type === 'bot'
                  ? msg.isTransition 
                    ? 'bg-blue-500/10 text-blue-400 border border-blue-500/20'
                    : 'bg-card border border-border'
                  : 'bg-primary text-primary-foreground'
              }`}>
                <p className="whitespace-pre-wrap text-left">{(msg.content || '').replace(/\\n/g, '\n')}</p>
              </div>
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      {!completed && (
        <div className="pt-4 border-t border-border">
          {error && (
            <div className="flex items-center gap-2 mb-3 p-3 rounded-lg bg-destructive/10 text-destructive text-sm">
              <AlertCircle className="h-4 w-4 flex-shrink-0" />
              {error}
            </div>
          )}
          
            <div className="flex gap-3">
              <textarea
                value={answer}
                onChange={(e) => setAnswer(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Cevabınızı yazın... (Enter ile gönderin, Shift+Enter yeni satır)"
                disabled={submitting}
                rows={3}
                className="flex-1 p-4 rounded-xl bg-background border border-input focus:border-primary focus:ring-2 focus:ring-primary/20 outline-none transition-all resize-none disabled:opacity-50"
              />
              
              {/* Gönder butonu */}
              <button
                onClick={handleSubmitAnswer}
                disabled={submitting || answer.length < 10}
                className="px-6 rounded-xl gradient-primary text-white flex items-center justify-center hover:opacity-90 disabled:opacity-50 transition-opacity"
              >
                {submitting ? (
                  <Loader2 className="h-5 w-5 animate-spin" />
                ) : (
                  <Send className="h-5 w-5" />
                )}
              </button>
            </div>
          
          <p className={`text-xs mt-2 text-center ${answer.length < 30 ? 'text-yellow-500' : 'text-muted-foreground'}`}>
            {answer.length}/10+ karakter
            {answer.length > 0 && answer.length < 30 && (
              <span className="block text-yellow-500">💡 Daha detaylı cevap verin (30+ karakter önerilir)</span>
            )}
          </p>
        </div>
      )}
    </div>
  );
}

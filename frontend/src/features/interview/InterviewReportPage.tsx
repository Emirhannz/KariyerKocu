import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { 
  Loader2, 
  CheckCircle, 
  XCircle,
  TrendingUp,
  TrendingDown,
  MessageSquare,
  Trophy,
  Clock,
  ChevronDown,
  ChevronUp
} from 'lucide-react';
import api from '../../lib/api';
import { formatDateTime } from '../../lib/utils';

interface QuestionReport {
  question_number: number;
  question_type: string;
  question_text: string;
  user_answer: string;
  score: number;
  evaluation_reason: string;
  ideal_answer: string | null;
  strengths: string[];
  weaknesses: string[];
}

interface InterviewReport {
  session_id: string;
  completed_at: string;
  duration_minutes: number | null;
  company_sector: string;
  company_sector_name: string;
  position: string;
  position_name: string;
  experience_level: string;
  experience_level_name: string;
  interview_type: string;
  total_questions: number;
  answered_questions: number;
  average_score: number;
  passing_score: number;
  passed: boolean;
  questions: QuestionReport[];
  overall_strengths: string[];
  overall_weaknesses: string[];
  recommendation: string | null;
}

export function InterviewReportPage() {
  const { sessionId } = useParams<{ sessionId: string }>();
  const [report, setReport] = useState<InterviewReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedQuestions, setExpandedQuestions] = useState<number[]>([]);

  useEffect(() => {
    const fetchReport = async () => {
      if (!sessionId) return;
      
      try {
        const response = await api.get<InterviewReport>(`/interview/report/${sessionId}`);
        setReport(response.data);
        // Expand first question by default
        if (response.data.questions.length > 0) {
          setExpandedQuestions([1]);
        }
      } catch (err: unknown) {
        const error = err as { response?: { data?: { detail?: string } } };
        setError(error.response?.data?.detail || 'Rapor yüklenemedi');
      } finally {
        setLoading(false);
      }
    };

    fetchReport();
    // Clear session from localStorage
    localStorage.removeItem('interview_session');
  }, [sessionId]);

  const toggleQuestion = (num: number) => {
    setExpandedQuestions(prev => 
      prev.includes(num) ? prev.filter(n => n !== num) : [...prev, num]
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  if (error || !report) {
    return (
      <div className="max-w-2xl mx-auto text-center py-12 space-y-4">
        <p className="text-destructive">{error}</p>
        <Link 
          to="/interview/start"
          className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-primary text-white hover:opacity-90"
        >
          Yeni Mülakat Başlat
        </Link>
      </div>
    );
  }

  const scorePercentage = (report.average_score / 10) * 100;

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-bold">Mülakat Raporu</h1>
        <p className="text-muted-foreground">
          {report.position_name} • {report.company_sector_name}
        </p>
      </div>

      {/* Result Card */}
      <div className={`rounded-2xl p-8 text-center ${
        report.passed 
          ? 'bg-gradient-to-r from-green-500/20 to-emerald-500/20 border border-green-500/30' 
          : 'bg-gradient-to-r from-orange-500/20 to-red-500/20 border border-orange-500/30'
      }`}>
        <div className="flex items-center justify-center gap-3 mb-4">
          {report.passed ? (
            <CheckCircle className="h-10 w-10 text-green-500" />
          ) : (
            <XCircle className="h-10 w-10 text-orange-500" />
          )}
          <span className={`text-3xl font-bold ${report.passed ? 'text-green-500' : 'text-orange-500'}`}>
            {report.passed ? 'Başarılı!' : 'Geliştirmeli'}
          </span>
        </div>
        
        <div className="flex items-center justify-center gap-2 mb-6">
          <span className="text-5xl font-bold">{report.average_score.toFixed(1)}</span>
          <span className="text-2xl text-muted-foreground">/10</span>
        </div>

        {/* Score Bar */}
        <div className="max-w-md mx-auto">
          <div className="h-4 bg-muted rounded-full overflow-hidden">
            <div 
              className={`h-full rounded-full transition-all ${
                report.passed ? 'bg-green-500' : 'bg-orange-500'
              }`}
              style={{ width: `${scorePercentage}%` }}
            />
          </div>
          <div className="flex justify-between mt-2 text-sm text-muted-foreground">
            <span>0</span>
            <span className="text-primary">Geçme: {report.passing_score}</span>
            <span>10</span>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-card border border-border rounded-xl p-4 text-center">
          <MessageSquare className="h-6 w-6 text-primary mx-auto mb-2" />
          <p className="text-2xl font-bold">{report.answered_questions}/{report.total_questions}</p>
          <p className="text-sm text-muted-foreground">Cevaplanan</p>
        </div>
        <div className="bg-card border border-border rounded-xl p-4 text-center">
          <Trophy className="h-6 w-6 text-yellow-500 mx-auto mb-2" />
          <p className="text-2xl font-bold">{report.experience_level_name}</p>
          <p className="text-sm text-muted-foreground">Seviye</p>
        </div>
        <div className="bg-card border border-border rounded-xl p-4 text-center">
          <Clock className="h-6 w-6 text-blue-500 mx-auto mb-2" />
          <p className="text-2xl font-bold">{report.duration_minutes || '-'}</p>
          <p className="text-sm text-muted-foreground">Dakika</p>
        </div>
        <div className="bg-card border border-border rounded-xl p-4 text-center">
          <TrendingUp className="h-6 w-6 text-green-500 mx-auto mb-2" />
          <p className="text-sm font-bold">{formatDateTime(report.completed_at).split(',')[0]}</p>
          <p className="text-sm text-muted-foreground">Tarih</p>
        </div>
      </div>

      {/* Strengths & Weaknesses */}
      <div className="grid md:grid-cols-2 gap-6">
        {report.overall_strengths.length > 0 && (
          <div className="bg-green-500/10 border border-green-500/30 rounded-xl p-6">
            <div className="flex items-center gap-2 mb-4 text-green-500">
              <TrendingUp className="h-5 w-5" />
              <span className="font-semibold">Güçlü Yönler</span>
            </div>
            <ul className="space-y-2">
              {report.overall_strengths.map((s, i) => (
                <li key={i} className="flex items-start gap-2 text-sm">
                  <CheckCircle className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                  {s}
                </li>
              ))}
            </ul>
          </div>
        )}

        {report.overall_weaknesses.length > 0 && (
          <div className="bg-orange-500/10 border border-orange-500/30 rounded-xl p-6">
            <div className="flex items-center gap-2 mb-4 text-orange-500">
              <TrendingDown className="h-5 w-5" />
              <span className="font-semibold">Geliştirmeli Alanlar</span>
            </div>
            <ul className="space-y-2">
              {report.overall_weaknesses.map((w, i) => (
                <li key={i} className="flex items-start gap-2 text-sm">
                  <XCircle className="h-4 w-4 text-orange-500 mt-0.5 flex-shrink-0" />
                  {w}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Recommendation */}
      {report.recommendation && (
        <div className="bg-primary/10 border border-primary/30 rounded-xl p-6">
          <h3 className="font-semibold text-lg mb-2">💡 Öneri</h3>
          <p className="text-muted-foreground whitespace-pre-wrap">{(report.recommendation || '').split('\\n').join('\n')}</p>
        </div>
      )}

      {/* Question Details */}
      <div className="space-y-4">
        <h3 className="font-semibold text-xl">Soru Detayları</h3>
        
        {report.questions.map((q) => (
          <div key={q.question_number} className="bg-card border border-border rounded-xl overflow-hidden">
            <button
              onClick={() => toggleQuestion(q.question_number)}
              className="w-full p-4 flex items-center justify-between hover:bg-muted/50 transition-colors"
            >
              <div className="flex items-center gap-4">
                <span className={`w-10 h-10 rounded-full flex items-center justify-center font-bold ${
                  q.score >= 7 ? 'bg-green-500/20 text-green-500' :
                  q.score >= 5 ? 'bg-yellow-500/20 text-yellow-500' :
                  'bg-red-500/20 text-red-500'
                }`}>
                  {q.score}
                </span>
                <div className="text-left">
                  <p className="font-medium">Soru {q.question_number}</p>
                  <p className="text-xs text-muted-foreground">
                    {q.question_type === 'TECHNICAL' ? 'Teknik' :
                     q.question_type === 'CV_BASED' ? 'CV' :
                     q.question_type === 'SCENARIO' ? 'Senaryo' : 'Davranışsal'}
                  </p>
                </div>
              </div>
              {expandedQuestions.includes(q.question_number) ? (
                <ChevronUp className="h-5 w-5 text-muted-foreground" />
              ) : (
                <ChevronDown className="h-5 w-5 text-muted-foreground" />
              )}
            </button>
            
            {expandedQuestions.includes(q.question_number) && (
              <div className="p-4 pt-0 space-y-4 border-t border-border">
                <div>
                  <p className="text-sm text-muted-foreground mb-1">Soru</p>
                  <p className="font-medium">{q.question_text}</p>
                </div>
                
                <div>
                  <p className="text-sm text-muted-foreground mb-1">Cevabınız</p>
                  <p className="p-3 rounded-lg bg-muted/50 whitespace-pre-wrap">
                    {q.user_answer.startsWith('[SESLI]') 
                      ? '🎤 Sesli yanıt'
                      : (q.user_answer || '').split('\\n').join('\n')
                    }
                  </p>
                </div>
                
                <div>
                  <p className="text-sm text-muted-foreground mb-1">Değerlendirme</p>
                  <p className="whitespace-pre-wrap">{(q.evaluation_reason || '').split('\\n').join('\n')}</p>
                </div>

                {q.ideal_answer && (
                  <div>
                    <p className="text-sm text-muted-foreground mb-1">Örnek Cevap</p>
                    <p className="p-3 rounded-lg bg-green-500/10 border border-green-500/30 whitespace-pre-wrap">
                      {(q.ideal_answer || '').split('\\n').join('\n')}
                    </p>
                  </div>
                )}

                {(q.strengths.length > 0 || q.weaknesses.length > 0) && (
                  <div className="grid md:grid-cols-2 gap-4">
                    {q.strengths.length > 0 && (
                      <div>
                        <p className="text-sm text-green-500 mb-2">✓ Güçlü Yönler</p>
                        <ul className="text-sm space-y-1">
                          {q.strengths.map((s, i) => (
                            <li key={i}>• {s}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                    {q.weaknesses.length > 0 && (
                      <div>
                        <p className="text-sm text-orange-500 mb-2">✗ Eksikler</p>
                        <ul className="text-sm space-y-1">
                          {q.weaknesses.map((w, i) => (
                            <li key={i}>• {w}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Actions */}
      <div className="flex gap-4">
        <Link
          to="/interview/history"
          className="flex-1 py-3 rounded-lg border border-border hover:bg-muted transition-colors font-medium text-center"
        >
          Geçmiş Mülakatlar
        </Link>
        <Link
          to="/interview/start"
          className="flex-1 py-3 rounded-lg gradient-primary text-white font-medium hover:opacity-90 transition-opacity text-center"
        >
          Yeni Mülakat
        </Link>
      </div>
    </div>
  );
}

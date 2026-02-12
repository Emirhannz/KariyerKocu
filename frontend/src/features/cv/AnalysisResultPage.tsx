import { useEffect, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { 
  Loader2, 
  ArrowLeft,
  CheckCircle,
  AlertTriangle,
  XCircle,
  TrendingUp,
  Lightbulb,
  Target
} from 'lucide-react';
import api from '../../lib/api';


interface FieldAnalysis {
  field: string;
  field_name: string;
  overall_score: number;
  strengths: string[];
  weaknesses: string[];
  matching_skills: string[];
  missing_skills: string[];
}

interface AnalysisResult {
  id: string;
  sector: string;
  sector_name: string;
  fields: string[];
  experience_level: string;
  experience_level_name: string;
  overall_score: number;
  field_analyses: FieldAnalysis[];
  created_at: string;
}

export function AnalysisResultPage() {
  const [data, setData] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchParams] = useSearchParams();

  useEffect(() => {
    const fetchAnalysis = async () => {
      const analysisId = searchParams.get('analysis_id');
      
      if (!analysisId) {
        setError('Analiz ID bulunamadı.');
        setLoading(false);
        return;
      }

      try {
        const response = await api.get<AnalysisResult>(`/analysis/detail/${analysisId}`);
        setData(response.data);
      } catch (err: unknown) {
        const error = err as { response?: { data?: { detail?: string } } };
        setError(error.response?.data?.detail || 'Analiz yüklenemedi.');
      } finally {
        setLoading(false);
      }
    };

    fetchAnalysis();
  }, [searchParams]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="max-w-2xl mx-auto text-center py-12 space-y-4">
        <p className="text-destructive">{error}</p>
        <Link 
          to="/dashboard"
          className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-primary text-white hover:opacity-90"
        >
          <ArrowLeft className="h-4 w-4" />
          Dashboard'a Dön
        </Link>
      </div>
    );
  }

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-500';
    if (score >= 60) return 'text-yellow-500';
    return 'text-red-500';
  };

  const getScoreBg = (score: number) => {
    if (score >= 80) return 'bg-green-500';
    if (score >= 60) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <Link 
            to="/dashboard" 
            className="text-sm text-muted-foreground hover:text-foreground mb-2 inline-flex items-center gap-1"
          >
            <ArrowLeft className="h-4 w-4" />
            Dashboard'a Dön
          </Link>
          <h1 className="text-3xl font-bold">📊 CV Analiz Sonucu</h1>
          <p className="text-muted-foreground mt-1">
            {new Date(data.created_at).toLocaleDateString('tr-TR', {
              day: 'numeric',
              month: 'long',
              year: 'numeric',
              hour: '2-digit',
              minute: '2-digit'
            })}
          </p>
        </div>
        <Link
          to={`/recommendations?analysis_id=${data.id}`}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-primary text-white hover:opacity-90"
        >
          <Lightbulb className="h-4 w-4" />
          Bu Analiz İçin Tavsiye Al
        </Link>
      </div>

      {/* Overall Score Card */}
      <div className="bg-gradient-to-br from-primary/10 via-purple-500/10 to-pink-500/10 border border-primary/30 rounded-xl p-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold mb-2">Genel Puan</h2>
            <div className="flex flex-wrap gap-2 mt-2">
              <span className="px-3 py-1 rounded-full bg-blue-500/10 text-blue-500 text-sm">
                {data.sector_name}
              </span>
              <span className="px-3 py-1 rounded-full bg-purple-500/10 text-purple-500 text-sm">
                {data.experience_level_name}
              </span>
            </div>
          </div>
          <div className={`text-5xl font-bold ${getScoreColor(data.overall_score)}`}>
            {data.overall_score}
            <span className="text-lg text-muted-foreground">/100</span>
          </div>
        </div>
        <div className="mt-4 h-3 bg-muted rounded-full overflow-hidden">
          <div 
            className={`h-full rounded-full transition-all ${getScoreBg(data.overall_score)}`}
            style={{ width: `${data.overall_score}%` }}
          />
        </div>
      </div>

      {/* Field Analyses */}
      <div className="space-y-6">
        <h2 className="text-xl font-semibold flex items-center gap-2">
          <Target className="h-5 w-5 text-primary" />
          Alan Bazlı Analiz
        </h2>

        {data.field_analyses.map((field, index) => (
          <div key={index} className="bg-card border border-border rounded-xl p-6 space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-medium">{field.field_name}</h3>
              <div className={`text-2xl font-bold ${getScoreColor(field.overall_score)}`}>
                {field.overall_score}/100
              </div>
            </div>
            
            <div className="h-2 bg-muted rounded-full overflow-hidden">
              <div 
                className={`h-full rounded-full ${getScoreBg(field.overall_score)}`}
                style={{ width: `${field.overall_score}%` }}
              />
            </div>

            <div className="grid md:grid-cols-2 gap-4">
              {/* Strengths */}
              <div className="space-y-2">
                <h4 className="font-medium text-green-500 flex items-center gap-2">
                  <CheckCircle className="h-4 w-4" />
                  Güçlü Yönler
                </h4>
                {field.strengths.length > 0 ? (
                  <ul className="space-y-1">
                    {field.strengths.map((s, i) => (
                      <li key={i} className="text-sm text-muted-foreground flex items-start gap-2">
                        <span className="text-green-500">•</span>
                        {s}
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-sm text-muted-foreground">Henüz belirlenmedi</p>
                )}
              </div>

              {/* Weaknesses */}
              <div className="space-y-2">
                <h4 className="font-medium text-red-500 flex items-center gap-2">
                  <XCircle className="h-4 w-4" />
                  Geliştirilmesi Gereken Alanlar
                </h4>
                {field.weaknesses.length > 0 ? (
                  <ul className="space-y-1">
                    {field.weaknesses.map((w, i) => (
                      <li key={i} className="text-sm text-muted-foreground flex items-start gap-2">
                        <span className="text-red-500">•</span>
                        {w}
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-sm text-muted-foreground">Harika! Eksik yok.</p>
                )}
              </div>
            </div>

            {/* Matching Skills */}
            {field.matching_skills.length > 0 && (
              <div className="pt-4 border-t border-border">
                <h4 className="font-medium text-sm mb-2 flex items-center gap-2">
                  <TrendingUp className="h-4 w-4 text-primary" />
                  Eşleşen Beceriler
                </h4>
                <div className="flex flex-wrap gap-2">
                  {field.matching_skills.map((skill, i) => (
                    <span key={i} className="px-2 py-1 rounded-md bg-green-500/10 text-green-500 text-xs">
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Missing Skills */}
            {field.missing_skills.length > 0 && (
              <div className="pt-4 border-t border-border">
                <h4 className="font-medium text-sm mb-2 flex items-center gap-2">
                  <AlertTriangle className="h-4 w-4 text-yellow-500" />
                  Eksik Beceriler
                </h4>
                <div className="flex flex-wrap gap-2">
                  {field.missing_skills.map((skill, i) => (
                    <span key={i} className="px-2 py-1 rounded-md bg-yellow-500/10 text-yellow-500 text-xs">
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Action Buttons */}
      <div className="flex flex-wrap gap-4 justify-center pb-8">
        <Link
          to={`/recommendations?analysis_id=${data.id}`}
          className="flex items-center gap-2 px-6 py-3 rounded-lg bg-primary text-white hover:opacity-90 font-medium"
        >
          <Lightbulb className="h-5 w-5" />
          Bu Analiz İçin Tavsiye Al
        </Link>
        <Link
          to="/cv/analysis"
          className="flex items-center gap-2 px-6 py-3 rounded-lg border border-border hover:bg-muted transition-colors font-medium"
        >
          <TrendingUp className="h-5 w-5" />
          Yeni Analiz Yap
        </Link>
      </div>
    </div>
  );
}

import { useEffect, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { 
  Loader2, 
  BookOpen, 
  Lightbulb, 
  Award,
  ExternalLink,
  Rocket,
  Target,
  ArrowLeft
} from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import api from '../../lib/api';

interface LearningResource {
  name: string;
  url: string;
  type: string;
  description: string;
}

interface ProjectSuggestion {
  name: string;
  description: string;
  difficulty: string;
  skills: string[];
}

interface SkillRecommendation {
  skill: string;
  priority: string;
  reason?: string;
  description?: string;
  resources: LearningResource[];
  estimated_time?: string;
}

interface FieldRecommendation {
  field: string;
  field_name: string;
  field_id?: string;
  current_score?: number;
  skills: SkillRecommendation[];
  skill_recommendations?: SkillRecommendation[];
  projects: ProjectSuggestion[];
  project_suggestions?: ProjectSuggestion[];
  certifications: string[];
  quick_tips: string[];
  personalized_advice?: string;  // AI tarafından oluşturulan kişisel tavsiye
}

interface RecommendationData {
  created_at: string;
  experience_level: string;
  experience_name: string;
  field_recommendations: FieldRecommendation[];
  general_advice: Record<string, string[]>;
  priority_actions: string[];
}

export function RecommendationsPage() {
  const [data, setData] = useState<RecommendationData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchParams] = useSearchParams();

  useEffect(() => {
    const fetchRecommendations = async () => {
      try {
        // URL'den analysis_id al
        const analysisId = searchParams.get('analysis_id');
        const url = analysisId 
          ? `/analysis/recommend?analysis_id=${analysisId}` 
          : '/analysis/recommend';
        
        const response = await api.get<RecommendationData>(url, {
          timeout: 180000 // 3 dakika timeout - LLM tavsiyeleri uzun sürebilir
        });
        setData(response.data);
      } catch (err: unknown) {
        const error = err as { response?: { data?: { detail?: string } }, code?: string, message?: string };
        if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
          setError('Tavsiye oluşturma zaman aşımına uğradı. Lütfen tekrar deneyin.');
        } else {
          setError(error.response?.data?.detail || 'Tavsiyeler yüklenemedi. Önce CV analizi yapın.');
        }
      } finally {
        setLoading(false);
      }
    };

    fetchRecommendations();
  }, [searchParams]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4">
        <Loader2 className="h-10 w-10 animate-spin text-primary" />
        <div className="text-center">
          <p className="font-medium text-lg">Yapay Zeka Tavsiyeleri Hazırlanıyor...</p>
          <p className="text-sm text-muted-foreground mt-1">Bu işlem 30-60 saniye sürebilir, lütfen bekleyin</p>
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="max-w-2xl mx-auto text-center py-12 space-y-4">
        <p className="text-destructive">{error}</p>
        <Link 
          to="/cv/analysis"
          className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-primary text-white hover:opacity-90"
        >
          <ArrowLeft className="h-4 w-4" />
          CV Analiz Yap
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">Kariyer Tavsiyeleri</h1>
        <p className="text-muted-foreground mt-2">
          CV analizine göre kişiselleştirilmiş öneriler • {data.experience_name}
        </p>
      </div>

      {/* Priority Actions */}
      {data.priority_actions && data.priority_actions.length > 0 && (
        <div className="bg-gradient-to-r from-primary/20 to-accent/20 border border-primary/30 rounded-xl p-6">
          <h3 className="font-semibold text-lg mb-4">🎯 Öncelikli Aksiyonlar</h3>
          <ul className="space-y-3">
            {data.priority_actions.map((action, i) => (
              <li key={i} className="flex items-start gap-3">
                <span className="flex-shrink-0 w-6 h-6 rounded-full bg-primary/20 text-primary text-xs flex items-center justify-center font-medium">
                  {i + 1}
                </span>
                <span className="text-foreground">{action}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Field Recommendations */}
      {data.field_recommendations && data.field_recommendations.map((fieldRec) => (
        <div key={fieldRec.field || fieldRec.field_id} className="space-y-6">
          <h2 className="text-2xl font-bold flex items-center gap-2">
            <Target className="h-6 w-6 text-primary" />
            {fieldRec.field_name}
            {fieldRec.current_score !== undefined && (
              <span className="text-base font-normal text-muted-foreground ml-2">
                (Puan: {fieldRec.current_score}/100)
              </span>
            )}
          </h2>

          {/* Personalized AI Advice - EN ÖNEMLİ BÖLÜM */}
          {fieldRec.personalized_advice && (
            <div className="bg-card border border-border rounded-xl overflow-hidden">
              {/* Header */}
              <div className="bg-gradient-to-r from-violet-600/20 via-purple-600/20 to-fuchsia-600/20 px-6 py-4 border-b border-border">
                <h3 className="font-semibold text-lg flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-gradient-to-br from-violet-500 to-purple-600 text-white">
                    <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                    </svg>
                  </div>
                  <span>AI Kariyer Koçun Diyor Ki...</span>
                </h3>
              </div>
              
              {/* Content */}
              <div className="p-6">
                <div className="
                  [&_h2]:flex [&_h2]:items-center [&_h2]:gap-2 [&_h2]:text-base [&_h2]:font-bold [&_h2]:text-primary [&_h2]:mt-6 [&_h2]:mb-4 [&_h2]:pb-2 [&_h2]:border-b [&_h2]:border-border/50
                  [&_h2:first-child]:mt-0
                  [&_h3]:text-sm [&_h3]:font-semibold [&_h3]:text-foreground [&_h3]:mt-5 [&_h3]:mb-3 [&_h3]:bg-muted/50 [&_h3]:p-2 [&_h3]:rounded-lg
                  [&_p]:text-sm [&_p]:text-muted-foreground [&_p]:leading-relaxed [&_p]:mb-2
                  [&_p>strong]:block [&_p>strong]:text-foreground [&_p>strong]:font-semibold [&_p>strong]:mt-3 [&_p>strong]:mb-1
                  [&_strong]:text-primary [&_strong]:font-medium
                  [&_ul]:space-y-2 [&_ul]:my-4
                  [&_li]:relative [&_li]:pl-6 [&_li]:text-sm [&_li]:text-muted-foreground [&_li]:py-1
                  [&_li]:before:content-[''] [&_li]:before:absolute [&_li]:before:left-0 [&_li]:before:top-3 [&_li]:before:w-2 [&_li]:before:h-2 [&_li]:before:rounded-full [&_li]:before:bg-primary/60
                  [&_ol]:space-y-3 [&_ol]:my-4 [&_ol]:list-none [&_ol]:counter-reset-[item]
                  [&_ol>li]:relative [&_ol>li]:pl-10 [&_ol>li]:counter-increment-[item]
                  [&_ol>li]:before:content-[counter(item)] [&_ol>li]:before:absolute [&_ol>li]:before:left-0 [&_ol>li]:before:top-0 [&_ol>li]:before:w-7 [&_ol>li]:before:h-7 [&_ol>li]:before:rounded-full [&_ol>li]:before:bg-primary/20 [&_ol>li]:before:text-primary [&_ol>li]:before:text-xs [&_ol>li]:before:font-bold [&_ol>li]:before:flex [&_ol>li]:before:items-center [&_ol>li]:before:justify-center
                ">
                  <ReactMarkdown>
                    {fieldRec.personalized_advice}
                  </ReactMarkdown>
                </div>
              </div>
            </div>
          )}
          {/* Skills to Learn */}
          {((fieldRec.skill_recommendations && fieldRec.skill_recommendations.length > 0) || (fieldRec.skills && fieldRec.skills.length > 0)) && (
            <div className="bg-card border border-border rounded-xl p-6">
              <h3 className="font-semibold text-lg mb-4 flex items-center gap-2">
                <BookOpen className="h-5 w-5 text-blue-500" />
                Öğrenilmesi Gereken Beceriler
              </h3>
              <div className="space-y-4">
                {(fieldRec.skill_recommendations || fieldRec.skills || []).map((skill, i) => (
                  <div key={i} className="p-4 rounded-lg bg-muted/50 space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="font-medium">{skill.skill}</span>
                      <span className={`px-2 py-1 rounded text-xs ${
                        skill.priority === 'high' ? 'bg-red-500/20 text-red-500' :
                        skill.priority === 'medium' ? 'bg-yellow-500/20 text-yellow-500' :
                        'bg-green-500/20 text-green-500'
                      }`}>
                        {skill.priority === 'high' ? 'Yüksek Öncelik' :
                         skill.priority === 'medium' ? 'Orta Öncelik' : 'Düşük Öncelik'}
                      </span>
                    </div>
                    <p className="text-sm text-muted-foreground">{skill.description || skill.reason}</p>
                    {skill.resources && skill.resources.length > 0 && (
                      <div className="flex flex-wrap gap-2">
                        {skill.resources.map((res, j) => (
                          <a
                            key={j}
                            href={res.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg bg-primary/10 text-primary text-sm hover:bg-primary/20 transition-colors"
                          >
                            {res.name}
                            <ExternalLink className="h-3 w-3" />
                          </a>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Project Ideas */}
          {((fieldRec.project_suggestions && fieldRec.project_suggestions.length > 0) || (fieldRec.projects && fieldRec.projects.length > 0)) && (
            <div className="bg-card border border-border rounded-xl p-6">
              <h3 className="font-semibold text-lg mb-4 flex items-center gap-2">
                <Rocket className="h-5 w-5 text-purple-500" />
                Proje Fikirleri
              </h3>
              <div className="grid md:grid-cols-2 gap-4">
                {(fieldRec.project_suggestions || fieldRec.projects || []).map((project, i) => (
                  <div key={i} className="p-4 rounded-lg bg-muted/50 space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="font-medium">{project.name}</span>
                      <span className={`px-2 py-1 rounded text-xs ${
                        project.difficulty === 'Kolay' ? 'bg-green-500/20 text-green-500' :
                        project.difficulty === 'Orta' ? 'bg-yellow-500/20 text-yellow-500' :
                        'bg-red-500/20 text-red-500'
                      }`}>
                        {project.difficulty}
                      </span>
                    </div>
                    <p className="text-sm text-muted-foreground">{project.description}</p>
                    {project.skills && (
                      <div className="flex flex-wrap gap-1">
                        {project.skills.map((skill, j) => (
                          <span key={j} className="px-2 py-0.5 rounded bg-secondary text-secondary-foreground text-xs">
                            {skill}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Certifications */}
          {fieldRec.certifications && fieldRec.certifications.length > 0 && (
            <div className="bg-card border border-border rounded-xl p-6">
              <h3 className="font-semibold text-lg mb-4 flex items-center gap-2">
                <Award className="h-5 w-5 text-yellow-500" />
                Önerilen Sertifikalar
              </h3>
              <ul className="space-y-2">
                {fieldRec.certifications.map((cert, i) => (
                  <li key={i} className="flex items-start gap-2">
                    <span className="text-yellow-500 mt-1">•</span>
                    <span className="text-muted-foreground">{cert}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Quick Tips */}
          {fieldRec.quick_tips && fieldRec.quick_tips.length > 0 && (
            <div className="bg-card border border-border rounded-xl p-6">
              <h3 className="font-semibold text-lg mb-4 flex items-center gap-2">
                <Lightbulb className="h-5 w-5 text-orange-500" />
                Hızlı İpuçları
              </h3>
              <ul className="space-y-2">
                {fieldRec.quick_tips.map((tip, i) => (
                  <li key={i} className="flex items-start gap-2">
                    <span className="text-orange-500 mt-1">💡</span>
                    <span className="text-muted-foreground">{tip}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      ))}

      {/* General Advice */}
      {data.general_advice && Object.keys(data.general_advice).length > 0 && (
        <div className="bg-card border border-border rounded-xl p-6">
          <h3 className="font-semibold text-lg mb-4">📚 Genel Tavsiyeler</h3>
          <div className="space-y-4">
            {Object.entries(data.general_advice).map(([category, tips]) => (
              <div key={category}>
                <h4 className="font-medium text-primary mb-2 capitalize">{category.replace('_', ' ')}</h4>
                <ul className="space-y-1">
                  {tips.map((tip, i) => (
                    <li key={i} className="text-sm text-muted-foreground">• {tip}</li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Navigation */}
      <div className="flex gap-3">
        <Link
          to="/cv/analysis"
          className="flex-1 py-3 rounded-lg border border-border hover:bg-muted transition-colors font-medium text-center"
        >
          Yeni Analiz Yap
        </Link>
        <Link
          to="/interview/start"
          className="flex-1 py-3 rounded-lg gradient-primary text-white font-medium hover:opacity-90 transition-opacity text-center"
        >
          Mülakat Simülasyonu
        </Link>
      </div>
    </div>
  );
}

import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Loader2, 
  CheckCircle,
  AlertCircle,
  TrendingUp,
  TrendingDown,
  Target,
  Lightbulb
} from 'lucide-react';
import api from '../../lib/api';
import type { AnalysisConfig, CVAnalysisResult } from '../../types';


export function CVAnalysisPage() {
  
  // Config data
  const [config, setConfig] = useState<AnalysisConfig | null>(null);
  const [loadingConfig, setLoadingConfig] = useState(true);
  
  // Form state
  const [sector, setSector] = useState('');
  const [fields, setFields] = useState<string[]>([]);
  const [experienceLevel, setExperienceLevel] = useState('');
  const analysisMethod = 'pre_llm'; // Fixed analysis method
  
  // Analysis state
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState<CVAnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Fetch config on mount
  useEffect(() => {
    const fetchConfig = async () => {
      try {
        const response = await api.get<AnalysisConfig>('/analysis/config');
        setConfig(response.data);
      } catch (err) {
        setError('Konfigürasyon yüklenemedi');
      } finally {
        setLoadingConfig(false);
      }
    };
    fetchConfig();
  }, []);

  // Available fields based on selected sector
  const availableFields = sector && config?.fields ? config.fields[sector] || [] : [];

  const handleFieldToggle = (fieldId: string) => {
    // Sadece tek bir alan seçilebilir
    setFields(prev => 
      prev.includes(fieldId) 
        ? [] // Aynı alana tıklanırsa seçimi kaldır
        : [fieldId] // Yeni alan seçilirse sadece onu seç
    );
  };

  const handleAnalyze = async () => {
    if (!sector || fields.length === 0 || !experienceLevel) {
      setError('Lütfen tüm alanları doldurun');
      return;
    }

    setAnalyzing(true);
    setError(null);

    try {
      // Analiz uzun sürebilir, 5 dakikalık timeout kullan
      const response = await api.post<CVAnalysisResult>('/analysis/analyze', {
        sector,
        fields,
        experience_level: experienceLevel,
        analysis_method: analysisMethod,
      }, {
        timeout: 300000 // 5 dakika timeout - analiz uzun sürebilir
      });
      setResult(response.data);
    } catch (err: unknown) {
      console.error('CV Analysis Error:', err);
      const error = err as { response?: { data?: { detail?: string }, status?: number }, message?: string, code?: string };
      
      // Timeout hatası kontrolü
      if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
        setError('Analiz zaman aşımına uğradı. Lütfen tekrar deneyin.');
      } else {
        const errorDetail = error.response?.data?.detail || error.message || 'Analiz başarısız';
        const statusCode = error.response?.status;
        setError(statusCode ? `Hata ${statusCode}: ${errorDetail}` : errorDetail);
      }
    } finally {
      setAnalyzing(false);
    }
  };

  if (loadingConfig) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  // Show results if analysis is complete
  if (result) {
    return <AnalysisResults result={result} onNewAnalysis={() => setResult(null)} />;
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">CV Analizi</h1>
        <p className="text-muted-foreground mt-2">
          Hedef alanını seç, CV'ni yapay zeka ile analiz et
        </p>
      </div>

      {/* Form */}
      <div className="bg-card border border-border rounded-xl p-6 space-y-6">
        {/* Sector Selection */}
        <div className="space-y-3">
          <label className="block font-medium">Hedef Sektör</label>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
            {config?.sectors.map((s) => (
              <button
                key={s.id}
                onClick={() => { setSector(s.id); setFields([]); }}
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

        {/* Field Selection */}
        {sector && (
          <div className="space-y-3">
            <label className="block font-medium">Hedef Alan(lar)</label>
            <p className="text-sm text-muted-foreground">Birden fazla seçebilirsin</p>
            <div className="grid grid-cols-2 gap-2">
              {availableFields.map((f) => (
                <button
                  key={f.id}
                  onClick={() => handleFieldToggle(f.id)}
                  className={`p-3 rounded-lg border text-sm font-medium transition-all text-left ${
                    fields.includes(f.id)
                      ? 'border-primary bg-primary/10 text-primary'
                      : 'border-border hover:border-primary/50'
                  }`}
                >
                  {fields.includes(f.id) && <CheckCircle className="h-4 w-4 inline mr-2" />}
                  {f.name}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Experience Level */}
        <div className="space-y-3">
          <label className="block font-medium">Tecrübe Seviyesi</label>
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

        {/* Analysis method is now fixed to pre_llm */}

        {/* Error */}
        {error && (
          <div className="flex items-center gap-2 p-4 rounded-lg bg-destructive/10 text-destructive">
            <AlertCircle className="h-5 w-5 flex-shrink-0" />
            <p className="text-sm">{error}</p>
          </div>
        )}

        {/* Submit */}
        <button
          onClick={handleAnalyze}
          disabled={analyzing || !sector || fields.length === 0 || !experienceLevel}
          className="w-full py-3 rounded-lg gradient-primary text-white font-medium flex items-center justify-center gap-2 hover:opacity-90 disabled:opacity-50 transition-opacity"
        >
          {analyzing ? (
            <div className="flex flex-col items-center gap-1">
              <div className="flex items-center gap-2">
                <Loader2 className="h-5 w-5 animate-spin" />
                <span>Yapay Zeka Analiz Ediyor...</span>
              </div>
              <span className="text-xs opacity-75">Bu işlem 30-60 saniye sürebilir</span>
            </div>
          ) : (
            <>
              CV Analiz Et
            </>
          )}
        </button>
      </div>
    </div>
  );
}

// Analysis Results Component
function AnalysisResults({ 
  result, 
  onNewAnalysis 
}: { 
  result: CVAnalysisResult; 
  onNewAnalysis: () => void;
}) {
  const navigate = useNavigate();
  
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Analiz Sonuçları</h1>
          <p className="text-muted-foreground mt-1">
            {new Date(result.analysis_date).toLocaleDateString('tr-TR', { 
              day: 'numeric', 
              month: 'long', 
              year: 'numeric' 
            })}
          </p>
        </div>
        <button
          onClick={onNewAnalysis}
          className="px-4 py-2 rounded-lg border border-border hover:bg-muted transition-colors text-sm"
        >
          Yeni Analiz
        </button>
      </div>

      {/* Field Analyses */}
      {result.field_analyses.map((analysis) => (
        <div key={analysis.field_id} className="bg-card border border-border rounded-xl p-6 space-y-6">
          {/* Field Header */}
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold">{analysis.field_name}</h2>
            <div className="flex items-center gap-2">
              <div className="text-3xl font-bold gradient-text">
                {analysis.overall_score}
              </div>
              <span className="text-muted-foreground">/100</span>
            </div>
          </div>

          {/* Score Bar */}
          <div className="h-3 bg-muted rounded-full overflow-hidden">
            <div 
              className={`h-full rounded-full transition-all ${
                analysis.overall_score >= 80 ? 'bg-green-500' :
                analysis.overall_score >= 60 ? 'bg-yellow-500' :
                analysis.overall_score >= 40 ? 'bg-orange-500' : 'bg-red-500'
              }`}
              style={{ width: `${analysis.overall_score}%` }}
            />
          </div>

          {/* Category Scores */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {Object.entries(analysis.category_scores).map(([key, cat]) => (
              <div key={key} className="text-center p-3 rounded-lg bg-muted/50">
                <p className="text-xs text-muted-foreground capitalize mb-1">
                  {key === 'summary' ? 'Özet' :
                   key === 'education' ? 'Eğitim' :
                   key === 'experience' ? 'Deneyim' :
                   key === 'projects' ? 'Projeler' :
                   key === 'skills' ? 'Beceriler' :
                   key === 'certifications' ? 'Sertifikalar' :
                   key === 'languages' ? 'Diller' : key}
                </p>
                <p className="text-lg font-bold">{cat.score}</p>
              </div>
            ))}
          </div>

          {/* Strengths & Weaknesses */}
          <div className="grid md:grid-cols-2 gap-4">
            <div className="p-4 rounded-lg bg-green-500/10 border border-green-500/30">
              <div className="flex items-center gap-2 mb-3 text-green-500">
                <TrendingUp className="h-5 w-5" />
                <span className="font-medium">Güçlü Yönler</span>
              </div>
              <ul className="space-y-2">
                {analysis.strengths.map((s, i) => (
                  <li key={i} className="text-sm flex items-start gap-2">
                    <CheckCircle className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                    {s}
                  </li>
                ))}
              </ul>
            </div>

            <div className="p-4 rounded-lg bg-orange-500/10 border border-orange-500/30">
              <div className="flex items-center gap-2 mb-3 text-orange-500">
                <TrendingDown className="h-5 w-5" />
                <span className="font-medium">Geliştirmeli Alanlar</span>
              </div>
              <ul className="space-y-2">
                {analysis.weaknesses.map((w, i) => (
                  <li key={i} className="text-sm flex items-start gap-2">
                    <AlertCircle className="h-4 w-4 text-orange-500 mt-0.5 flex-shrink-0" />
                    {w}
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Skills */}
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <div className="flex items-center gap-2 mb-3">
                <Target className="h-5 w-5 text-primary" />
                <span className="font-medium">Eşleşen Beceriler</span>
              </div>
              <div className="flex flex-wrap gap-2">
                {analysis.matching_skills.map((skill, i) => (
                  <span key={i} className="px-2 py-1 rounded-full bg-primary/10 text-primary text-xs">
                    {skill}
                  </span>
                ))}
              </div>
            </div>

            <div>
              <div className="flex items-center gap-2 mb-3">
                <Lightbulb className="h-5 w-5 text-yellow-500" />
                <span className="font-medium">Öğrenilmesi Gereken</span>
              </div>
              <div className="flex flex-wrap gap-2">
                {analysis.missing_skills.map((skill, i) => (
                  <span key={i} className="px-2 py-1 rounded-full bg-yellow-500/10 text-yellow-500 text-xs">
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>
      ))}

      {/* Action Items */}
      {result.action_items.length > 0 && (
        <div className="bg-card border border-border rounded-xl p-6">
          <h3 className="font-semibold text-lg mb-4">📌 Aksiyon Önerileri</h3>
          <ul className="space-y-3">
            {result.action_items.map((item, i) => (
              <li key={i} className="flex items-start gap-3">
                <span className="flex-shrink-0 w-6 h-6 rounded-full bg-primary/10 text-primary text-xs flex items-center justify-center font-medium">
                  {i + 1}
                </span>
                <span className="text-muted-foreground">{item}</span>
              </li>
            ))}
          </ul>
        </div>
      )}



      {/* Navigation */}
      <div className="flex gap-3">
        <button
          onClick={() => navigate('/recommendations')}
          className="flex-1 py-3 rounded-lg border border-border hover:bg-muted transition-colors font-medium"
        >
          Tavsiyeler Al
        </button>
        <button
          onClick={() => navigate('/interview/start')}
          className="flex-1 py-3 rounded-lg gradient-primary text-white font-medium hover:opacity-90 transition-opacity"
        >
          Mülakat Simülasyonu
        </button>
      </div>
    </div>
  );
}

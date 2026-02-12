import { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { 
  Bot, 
  Loader2, 
  AlertTriangle, 
  CheckCircle, 
  XCircle,
  ChevronDown,
  ChevronUp,
  Lightbulb,
  FileWarning,
  Upload,
  FileText,
  RefreshCw
} from 'lucide-react';
import api from '../../lib/api';

interface ATSIssue {
  type: string;
  severity: 'high' | 'medium' | 'low';
  title: string;
  description: string;
  affected_text: string;
  location?: string;
  fix?: string;
  count?: number;
}

interface ATSResult {
  success: boolean;
  raw_text: string;
  cleaned_text: string;
  issues: ATSIssue[];
  score: number;
  recommendations: string[];
  stats: {
    total_characters: number;
    total_words: number;
    total_lines: number;
    total_pages: number;
    issues_count: number;
    high_severity_count: number;
    medium_severity_count: number;
    low_severity_count: number;
  };
  problematic_texts?: string[];
  error?: string;
}

type TestMode = 'select' | 'system' | 'upload';

export function ATSSimulationSection() {
  const [mode, setMode] = useState<TestMode>('select');
  const [result, setResult] = useState<ATSResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showRawText, setShowRawText] = useState(false);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);

  // Sistemdeki CV'yi test et
  const runSystemCVSimulation = async () => {
    setLoading(true);
    setError(null);
    setMode('system');
    
    try {
      const response = await api.get<ATSResult>('/analysis/ats-simulation/from-cv');
      setResult(response.data);
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } };
      setError(error.response?.data?.detail || 'ATS simülasyonu başarısız oldu.');
    } finally {
      setLoading(false);
    }
  };

  // Yüklenen CV'yi test et (backend'e kaydetmeden)
  const runUploadedCVSimulation = async (file: File) => {
    setLoading(true);
    setError(null);
    setUploadedFile(file);
    
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      // Özel endpoint - sadece ATS simülasyonu, CV kaydetmez
      const response = await api.post<ATSResult>('/analysis/ats-simulation/test-file', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 60000,
      });
      setResult(response.data);
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } };
      setError(error.response?.data?.detail || 'ATS simülasyonu başarısız oldu.');
    } finally {
      setLoading(false);
    }
  };

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const pdfFile = acceptedFiles[0];
    if (pdfFile && pdfFile.type === 'application/pdf') {
      setMode('upload');
      runUploadedCVSimulation(pdfFile);
    } else {
      setError('Sadece PDF dosyası yükleyebilirsiniz');
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'application/pdf': ['.pdf'] },
    maxFiles: 1,
    maxSize: 10 * 1024 * 1024,
    noClick: mode !== 'select',
    noDrag: mode !== 'select',
  });

  const resetTest = () => {
    setMode('select');
    setResult(null);
    setError(null);
    setUploadedFile(null);
    setShowRawText(false);
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-500';
    if (score >= 60) return 'text-yellow-500';
    return 'text-red-500';
  };

  const getScoreLabel = (score: number) => {
    if (score >= 80) return 'ATS Uyumlu';
    if (score >= 60) return 'Kısmen Uyumlu';
    return 'Sorunlu';
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'high':
        return <XCircle className="h-4 w-4 text-red-500" />;
      case 'medium':
        return <AlertTriangle className="h-4 w-4 text-yellow-500" />;
      default:
        return <CheckCircle className="h-4 w-4 text-blue-500" />;
    }
  };

  const getSeverityBg = (severity: string) => {
    switch (severity) {
      case 'high':
        return 'border-red-500/30 bg-red-500/5';
      case 'medium':
        return 'border-yellow-500/30 bg-yellow-500/5';
      default:
        return 'border-blue-500/30 bg-blue-500/5';
    }
  };

  const highlightProblems = (text: string, problems: string[]) => {
    let highlighted = text.split('\\n').join('\n').split('\\r').join('');
    if (!problems || problems.length === 0) return highlighted;
    
    const sortedProblems = [...problems].sort((a, b) => b.length - a.length);
    sortedProblems.forEach(problem => {
      const escapedProblem = problem.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
      highlighted = highlighted.replace(
        new RegExp(escapedProblem, 'g'),
        `<mark class="ats-error">${problem}</mark>`
      );
    });
    
    return highlighted;
  };

  return (
    <div className="bg-card border border-border rounded-xl overflow-hidden animate-in fade-in slide-in-from-bottom-4 duration-500">
      {/* Header */}
      <div className="bg-gradient-to-r from-orange-500/10 via-red-500/10 to-pink-500/10 p-6 border-b border-border">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-orange-500/10">
              <Bot className="h-6 w-6 text-orange-500" />
            </div>
            <div>
              <h2 className="text-xl font-semibold">🤖 ATS Simülasyonu</h2>
              <p className="text-sm text-muted-foreground">
                {mode === 'system' && 'Sistemdeki CV test ediliyor'}
                {mode === 'upload' && uploadedFile && `Test edilen: ${uploadedFile.name}`}
                {mode === 'select' && 'CV\'niz robotların gözünden nasıl görünüyor?'}
              </p>
            </div>
          </div>
          
          {result && (
            <button
              onClick={resetTest}
              className="flex items-center gap-2 px-4 py-2 rounded-lg border border-border hover:bg-muted transition-colors"
            >
              <RefreshCw className="h-4 w-4" />
              Yeni Test
            </button>
          )}
        </div>
      </div>

      {/* Mode Selection */}
      {mode === 'select' && !loading && (
        <div className="p-6 space-y-4 animate-in fade-in duration-300">
          <div className="text-center mb-6">
            <div className="inline-flex p-4 rounded-full bg-muted mb-4">
              <Bot className="h-8 w-8 text-muted-foreground" />
            </div>
            <h3 className="font-medium mb-2">ATS Uyumluluk Testi</h3>
            <p className="text-sm text-muted-foreground max-w-md mx-auto">
              CV'nizin ATS robotları tarafından nasıl okunduğunu test edin.
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 gap-4">
            {/* Sistemdeki CV */}
            <button
              onClick={runSystemCVSimulation}
              className="group p-6 rounded-xl border-2 border-dashed border-border hover:border-primary/50 hover:bg-primary/5 transition-all duration-300 text-left"
            >
              <div className="flex items-center gap-3 mb-3">
                <div className="p-2 rounded-lg bg-primary/10 group-hover:bg-primary/20 transition-colors">
                  <FileText className="h-5 w-5 text-primary" />
                </div>
                <span className="font-medium">Sistemdeki CV'yi Test Et</span>
              </div>
              <p className="text-sm text-muted-foreground">
                Daha önce yüklediğiniz CV'yi ATS testine sokun. Bu test profil bilgilerinizi etkilemez.
              </p>
            </button>
            
            {/* Yeni CV Yükle */}
            <div
              {...getRootProps()}
              className={`group p-6 rounded-xl border-2 border-dashed transition-all duration-300 text-left cursor-pointer
                ${isDragActive 
                  ? 'border-orange-500 bg-orange-500/10' 
                  : 'border-border hover:border-orange-500/50 hover:bg-orange-500/5'
                }`}
            >
              <input {...getInputProps()} />
              <div className="flex items-center gap-3 mb-3">
                <div className="p-2 rounded-lg bg-orange-500/10 group-hover:bg-orange-500/20 transition-colors">
                  <Upload className="h-5 w-5 text-orange-500" />
                </div>
                <span className="font-medium">Başka CV Analiz Et</span>
              </div>
              <p className="text-sm text-muted-foreground">
                Farklı bir CV dosyası yükleyip test edin. Bu test sistemdeki CV'yi değiştirmez.
              </p>
            </div>
          </div>
          
          <div className="p-3 rounded-lg bg-blue-500/10 border border-blue-500/20 mt-4">
            <p className="text-xs text-blue-500 text-center">
              💡 <strong>Not:</strong> ATS testleri sadece simülasyon amaçlıdır ve profil bilgilerinizi değiştirmez.
            </p>
          </div>
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div className="p-12 text-center animate-in fade-in duration-300">
          <Loader2 className="h-12 w-12 animate-spin text-orange-500 mx-auto mb-4" />
          <p className="font-medium">ATS Simülasyonu Çalışıyor...</p>
          <p className="text-sm text-muted-foreground mt-1">CV robotlar tarafından analiz ediliyor</p>
        </div>
      )}

      {/* Error State */}
      {error && !loading && (
        <div className="p-6 animate-in fade-in duration-300">
          <div className="flex items-center gap-3 p-4 rounded-lg bg-red-500/10 border border-red-500/30">
            <XCircle className="h-5 w-5 text-red-500" />
            <p className="text-red-500">{error}</p>
          </div>
          <button
            onClick={resetTest}
            className="mt-4 w-full py-2 rounded-lg border border-border hover:bg-muted transition-colors"
          >
            Tekrar Dene
          </button>
        </div>
      )}

      {/* Results */}
      {result && !loading && (
        <div className="p-6 space-y-6 animate-in fade-in slide-in-from-bottom-2 duration-500">
          {/* Score Card */}
          <div className="flex items-center gap-6 p-4 rounded-lg bg-muted/50">
            <div className="relative">
              <svg className="w-24 h-24 transform -rotate-90">
                <circle
                  cx="48"
                  cy="48"
                  r="40"
                  stroke="currentColor"
                  strokeWidth="8"
                  fill="none"
                  className="text-muted"
                />
                <circle
                  cx="48"
                  cy="48"
                  r="40"
                  stroke="currentColor"
                  strokeWidth="8"
                  fill="none"
                  strokeDasharray={`${result.score * 2.51} 251`}
                  className={`${getScoreColor(result.score)} transition-all duration-1000`}
                  style={{ strokeDashoffset: 0 }}
                />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center">
                <span className={`text-2xl font-bold ${getScoreColor(result.score)}`}>
                  {result.score}
                </span>
              </div>
            </div>
            
            <div className="flex-1">
              <h3 className={`text-lg font-semibold ${getScoreColor(result.score)}`}>
                {getScoreLabel(result.score)}
              </h3>
              <p className="text-sm text-muted-foreground mt-1">
                {result.stats.total_words} kelime • {result.stats.total_pages} sayfa • {result.stats.issues_count} sorun
              </p>
              <div className="flex gap-2 mt-2">
                {result.stats.high_severity_count > 0 && (
                  <span className="px-2 py-1 rounded text-xs bg-red-500/10 text-red-500">
                    {result.stats.high_severity_count} kritik
                  </span>
                )}
                {result.stats.medium_severity_count > 0 && (
                  <span className="px-2 py-1 rounded text-xs bg-yellow-500/10 text-yellow-500">
                    {result.stats.medium_severity_count} orta
                  </span>
                )}
                {result.stats.low_severity_count > 0 && (
                  <span className="px-2 py-1 rounded text-xs bg-blue-500/10 text-blue-500">
                    {result.stats.low_severity_count} düşük
                  </span>
                )}
              </div>
            </div>
          </div>

          {/* Issues */}
          {result.issues.length > 0 && (
            <div className="space-y-3">
              <h3 className="font-semibold flex items-center gap-2">
                <FileWarning className="h-5 w-5 text-yellow-500" />
                Tespit Edilen Sorunlar ({result.issues.length})
              </h3>
              
              <div className="space-y-2">
                {result.issues.map((issue, index) => (
                  <div
                    key={index}
                    className={`p-4 rounded-lg border ${getSeverityBg(issue.severity)} animate-in fade-in slide-in-from-left duration-300`}
                    style={{ animationDelay: `${index * 50}ms` }}
                  >
                    <div className="flex items-start gap-3">
                      {getSeverityIcon(issue.severity)}
                      <div className="flex-1">
                        <div className="flex items-center gap-2 flex-wrap">
                          <h4 className="font-medium">{issue.title}</h4>
                          {issue.location && (
                            <span className="px-2 py-0.5 rounded-full bg-muted text-xs text-muted-foreground">
                              📍 {issue.location}
                            </span>
                          )}
                        </div>
                        <p className="text-sm text-muted-foreground mt-1">
                          {issue.description}
                        </p>
                        {issue.affected_text && (
                          <code className="block mt-2 text-xs bg-muted px-2 py-1 rounded overflow-x-auto">
                            {issue.affected_text}
                          </code>
                        )}
                        {issue.fix && (
                          <div className="mt-2 p-2 rounded bg-green-500/10 border border-green-500/20">
                            <p className="text-xs text-green-600 dark:text-green-400">
                              💡 <strong>Düzeltme:</strong> {issue.fix}
                            </p>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Recommendations */}
          {result.recommendations.length > 0 && (
            <div className="space-y-3">
              <h3 className="font-semibold flex items-center gap-2">
                <Lightbulb className="h-5 w-5 text-primary" />
                Öneriler
              </h3>
              
              <div className="space-y-2">
                {result.recommendations.map((rec, index) => (
                  <div
                    key={index}
                    className="p-3 rounded-lg bg-primary/5 border border-primary/20 text-sm animate-in fade-in duration-300"
                    style={{ animationDelay: `${index * 50}ms` }}
                  >
                    {rec}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Raw Text Toggle */}
          <div className="border-t border-border pt-4">
            <button
              onClick={() => setShowRawText(!showRawText)}
              className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors"
            >
              {showRawText ? (
                <ChevronUp className="h-4 w-4" />
              ) : (
                <ChevronDown className="h-4 w-4" />
              )}
              {showRawText ? 'Robotun Gördüğünü Gizle' : 'Robotun Gördüğünü Göster'}
            </button>
            
            {showRawText && (
              <div className="mt-4 animate-in fade-in slide-in-from-top-2 duration-300">
                <h4 className="text-sm font-medium mb-2 flex items-center gap-2">
                  <Bot className="h-4 w-4 text-orange-500" />
                  Robotun Gözüyle (ATS'in Okuduğu Ham Metin)
                </h4>
                <p className="text-xs text-muted-foreground mb-2">
                  ATS robotları CV'nizi bu şekilde görüyor. <span className="text-red-500 font-medium">Kırmızı bölümler</span> sorunlu alanlardır.
                </p>
                <div 
                  className="p-4 rounded-lg bg-muted/50 border border-border text-xs font-mono whitespace-pre-wrap max-h-80 overflow-y-auto [&_.ats-error]:bg-red-500/30 [&_.ats-error]:text-red-400 [&_.ats-error]:px-0.5 [&_.ats-error]:rounded"
                  dangerouslySetInnerHTML={{
                    __html: result.raw_text 
                      ? highlightProblems(result.raw_text, result.problematic_texts || [])
                      : 'İçerik çıkarılamadı'
                  }}
                />
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

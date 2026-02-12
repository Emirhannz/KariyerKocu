import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { 
  PenTool, 
  Mail, 
  Loader2, 
  Copy, 
  CheckCircle,
  Lightbulb,
  Building2,
  Briefcase,
  FileText,
  Sparkles,
  RefreshCw,
  User,
  Factory,
  Palette
} from 'lucide-react';
import api from '../../lib/api';

type GenerateType = 'cover_letter' | 'email';

interface Option {
  value: string;
  label: string;
  description: string;
}

interface OptionsData {
  position_types: Option[];
  sectors: Option[];
  styles: Option[];
  lengths: Option[];
}

interface CoverLetterResult {
  success: boolean;
  cover_letter?: string;
  word_count?: number;
  profile_type?: string;
  sector?: string;
  tips?: string[];
  error?: string;
}

interface EmailResult {
  success: boolean;
  subject?: string;
  body?: string;
  profile_type?: string;
  tips?: string[];
  error?: string;
}

export function CoverLetterPage() {
  const [searchParams] = useSearchParams();
  const initialType = searchParams.get('type') === 'email' ? 'email' : 'cover_letter';
  
  const [generateType, setGenerateType] = useState<GenerateType>(initialType);
  const [options, setOptions] = useState<OptionsData | null>(null);
  
  // Form state
  const [companyName, setCompanyName] = useState('');
  const [positionTitle, setPositionTitle] = useState('');
  const [positionType, setPositionType] = useState('junior');
  const [sector, setSector] = useState('tech');
  const [style, setStyle] = useState('professional');
  const [length, setLength] = useState('medium');
  const [companyNote, setCompanyNote] = useState('');
  const [jobDescription, setJobDescription] = useState('');
  
  // UI state
  const [loading, setLoading] = useState(false);
  const [optionsLoading, setOptionsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [letterResult, setLetterResult] = useState<CoverLetterResult | null>(null);
  const [emailResult, setEmailResult] = useState<EmailResult | null>(null);
  const [copied, setCopied] = useState(false);

  // Seçenekleri yükle
  useEffect(() => {
    const fetchOptions = async () => {
      try {
        const response = await api.get<OptionsData>('/cover-letter/options');
        setOptions(response.data);
      } catch (err) {
        console.error('Seçenekler yüklenemedi:', err);
      } finally {
        setOptionsLoading(false);
      }
    };
    fetchOptions();
  }, []);

  const handleGenerate = async () => {
    if (!companyName.trim() || !positionTitle.trim()) {
      setError('Şirket adı ve pozisyon zorunludur');
      return;
    }

    setLoading(true);
    setError(null);
    setLetterResult(null);
    setEmailResult(null);

    try {
      if (generateType === 'cover_letter') {
        const response = await api.post<CoverLetterResult>('/cover-letter/cover-letter', {
          company_name: companyName,
          position_title: positionTitle,
          position_type: positionType,
          sector: sector,
          style: style,
          length: length,
          company_note: companyNote || null,
          job_description: jobDescription || null
        });
        setLetterResult(response.data);
      } else {
        const response = await api.post<EmailResult>('/cover-letter/email', {
          company_name: companyName,
          position_title: positionTitle,
          position_type: positionType,
          sector: sector,
          style: style,
          length: length,
          company_note: companyNote || null
        });
        setEmailResult(response.data);
      }
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } };
      setError(error.response?.data?.detail || 'Oluşturma sırasında bir hata oluştu');
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Kopyalama hatası:', err);
    }
  };

  const handleReset = () => {
    setLetterResult(null);
    setEmailResult(null);
    setError(null);
  };

  const result = letterResult || emailResult;
  const resultText = letterResult?.cover_letter || 
    (emailResult ? `Konu: ${emailResult.subject}\n\n${emailResult.body}` : '');

  if (optionsLoading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <div className="p-3 rounded-xl bg-gradient-to-br from-pink-500/20 to-purple-500/20">
          <PenTool className="h-8 w-8 text-pink-500" />
        </div>
        <div>
          <h1 className="text-2xl font-bold">Akıllı Önyazı & E-mail</h1>
          <p className="text-muted-foreground">
            CV'nize ve profilinize göre kişiselleştirilmiş içerik
          </p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 p-1 bg-muted rounded-lg w-fit">
        <button
          onClick={() => { setGenerateType('cover_letter'); handleReset(); }}
          className={`flex items-center gap-2 px-4 py-2 rounded-md transition-colors ${
            generateType === 'cover_letter' 
              ? 'bg-card shadow-sm text-pink-500' 
              : 'text-muted-foreground hover:text-foreground'
          }`}
        >
          <FileText className="h-4 w-4" />
          Önyazı
        </button>
        <button
          onClick={() => { setGenerateType('email'); handleReset(); }}
          className={`flex items-center gap-2 px-4 py-2 rounded-md transition-colors ${
            generateType === 'email' 
              ? 'bg-card shadow-sm text-pink-500' 
              : 'text-muted-foreground hover:text-foreground'
          }`}
        >
          <Mail className="h-4 w-4" />
          E-mail
        </button>
      </div>

      {/* Form */}
      {!result && (
        <div className="bg-card border border-border rounded-xl p-6 space-y-6">
          {/* Company & Position */}
          <div className="grid md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="flex items-center gap-2 text-sm font-medium">
                <Building2 className="h-4 w-4 text-muted-foreground" />
                Şirket Adı *
              </label>
              <input
                type="text"
                value={companyName}
                onChange={(e) => setCompanyName(e.target.value)}
                placeholder="Örn: Trendyol, ASELSAN, Getir"
                className="w-full px-4 py-3 rounded-lg border border-border bg-background focus:outline-none focus:ring-2 focus:ring-pink-500/50"
              />
            </div>
            <div className="space-y-2">
              <label className="flex items-center gap-2 text-sm font-medium">
                <Briefcase className="h-4 w-4 text-muted-foreground" />
                Pozisyon *
              </label>
              <input
                type="text"
                value={positionTitle}
                onChange={(e) => setPositionTitle(e.target.value)}
                placeholder="Örn: Backend Developer, AI Engineer"
                className="w-full px-4 py-3 rounded-lg border border-border bg-background focus:outline-none focus:ring-2 focus:ring-pink-500/50"
              />
            </div>
          </div>

          {/* Position Type & Sector */}
          <div className="grid md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="flex items-center gap-2 text-sm font-medium">
                <User className="h-4 w-4 text-muted-foreground" />
                Pozisyon Tipi *
              </label>
              <select
                value={positionType}
                onChange={(e) => setPositionType(e.target.value)}
                className="w-full px-4 py-3 rounded-lg border border-border bg-background focus:outline-none focus:ring-2 focus:ring-pink-500/50"
              >
                {options?.position_types.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label} - {opt.description}
                  </option>
                ))}
              </select>
            </div>
            <div className="space-y-2">
              <label className="flex items-center gap-2 text-sm font-medium">
                <Factory className="h-4 w-4 text-muted-foreground" />
                Sektör *
              </label>
              <select
                value={sector}
                onChange={(e) => setSector(e.target.value)}
                className="w-full px-4 py-3 rounded-lg border border-border bg-background focus:outline-none focus:ring-2 focus:ring-pink-500/50"
              >
                {options?.sectors.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Style Selection */}
          <div className="space-y-2">
            <label className="flex items-center gap-2 text-sm font-medium">
              <Palette className="h-4 w-4 text-muted-foreground" />
              Yazım Tonu
            </label>
            <div className="flex gap-3 flex-wrap">
              {options?.styles.map((opt) => (
                <button
                  key={opt.value}
                  onClick={() => setStyle(opt.value)}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg border transition-all ${
                    style === opt.value
                      ? 'border-pink-500 bg-pink-500/10 text-pink-500'
                      : 'border-border hover:border-pink-500/50'
                  }`}
                >
                  {opt.value === 'professional' && '💼'}
                  {opt.value === 'friendly' && '😊'}
                  {opt.value === 'direct' && '⚡'}
                  {opt.label}
                </button>
              ))}
            </div>
          </div>

          {/* Length Selection */}
          <div className="space-y-2">
            <label className="flex items-center gap-2 text-sm font-medium">
              <FileText className="h-4 w-4 text-muted-foreground" />
              Uzunluk
            </label>
            <div className="flex gap-3 flex-wrap">
              {options?.lengths?.map((opt) => (
                <button
                  key={opt.value}
                  onClick={() => setLength(opt.value)}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg border transition-all ${
                    length === opt.value
                      ? 'border-pink-500 bg-pink-500/10 text-pink-500'
                      : 'border-border hover:border-pink-500/50'
                  }`}
                >
                  {opt.value === 'short' && '📝'}
                  {opt.value === 'medium' && '📄'}
                  {opt.value === 'long' && '📋'}
                  <span>{opt.label}</span>
                  <span className="text-xs text-muted-foreground">({opt.description})</span>
                </button>
              ))}
            </div>
          </div>

          {/* Company Note */}
          <div className="space-y-2">
            <label className="flex items-center gap-2 text-sm font-medium">
              <Sparkles className="h-4 w-4 text-muted-foreground" />
              Firmaya Özel Not
              <span className="text-muted-foreground font-normal">(Opsiyonel)</span>
            </label>
            <textarea
              value={companyNote}
              onChange={(e) => setCompanyNote(e.target.value)}
              placeholder="Örn: Şirketin X projesini takip ediyorum, Y teknolojinize hayranlık duyuyorum..."
              rows={2}
              className="w-full px-4 py-3 rounded-lg border border-border bg-background focus:outline-none focus:ring-2 focus:ring-pink-500/50 resize-none"
            />
            <p className="text-xs text-muted-foreground">
              Bu not önyazıya doğal bir şekilde dahil edilecek
            </p>
          </div>

          {/* Job Description (Only for Cover Letter) */}
          {generateType === 'cover_letter' && (
            <div className="space-y-2">
              <label className="flex items-center gap-2 text-sm font-medium">
                <FileText className="h-4 w-4 text-muted-foreground" />
                İlan Açıklaması
                <span className="text-muted-foreground font-normal">(Opsiyonel)</span>
              </label>
              <textarea
                value={jobDescription}
                onChange={(e) => setJobDescription(e.target.value)}
                placeholder="İlan metnini buraya yapıştırın... (Aranan kriterler, beklentiler vs.)"
                rows={3}
                className="w-full px-4 py-3 rounded-lg border border-border bg-background focus:outline-none focus:ring-2 focus:ring-pink-500/50 resize-none"
              />
              <p className="text-xs text-muted-foreground">
                İlan metni varsa, CV'nizdeki uyumlu yetenekler öne çıkarılır
              </p>
            </div>
          )}

          {/* Error */}
          {error && (
            <div className="p-4 rounded-lg bg-red-500/10 border border-red-500/30 text-red-500 text-sm">
              {error}
            </div>
          )}

          {/* Submit Button */}
          <button
            onClick={handleGenerate}
            disabled={loading || !companyName.trim() || !positionTitle.trim()}
            className="w-full flex items-center justify-center gap-2 py-3 px-4 rounded-lg bg-gradient-to-r from-pink-500 to-purple-500 text-white font-medium hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
          >
            {loading ? (
              <>
                <Loader2 className="h-5 w-5 animate-spin" />
                Profilinize göre oluşturuluyor...
              </>
            ) : (
              <>
                <Sparkles className="h-5 w-5" />
                {generateType === 'cover_letter' ? 'Önyazı Oluştur' : 'E-mail Oluştur'}
              </>
            )}
          </button>

          {/* Info Box */}
          <div className="p-4 rounded-lg bg-blue-500/5 border border-blue-500/20">
            <p className="text-sm text-blue-400">
              💡 <strong>Akıllı Sistem:</strong> CV'nizdeki bilgiler ve seçtiğiniz pozisyon tipine göre 
              gerçekçi bir metin oluşturulur. Stajyer için "10 yıllık tecrübe" gibi saçmalıklar yapmayız!
            </p>
          </div>
        </div>
      )}

      {/* Result */}
      {result && result.success && (
        <div className="space-y-4">
          {/* Result Card */}
          <div className="bg-card border border-border rounded-xl overflow-hidden">
            <div className="bg-gradient-to-r from-pink-500/10 to-purple-500/10 p-4 border-b border-border flex items-center justify-between flex-wrap gap-4">
              <div className="flex items-center gap-3">
                <CheckCircle className="h-5 w-5 text-green-500" />
                <span className="font-medium">
                  {generateType === 'cover_letter' ? 'Önyazınız Hazır!' : 'E-mailiniz Hazır!'}
                </span>
                {letterResult?.word_count && (
                  <span className="text-sm text-muted-foreground">
                    ({letterResult.word_count} kelime)
                  </span>
                )}
                {result.profile_type && (
                  <span className="px-2 py-1 rounded-full bg-pink-500/10 text-pink-500 text-xs">
                    {result.profile_type}
                  </span>
                )}
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => handleCopy(resultText)}
                  className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-pink-500/10 text-pink-500 hover:bg-pink-500/20 transition-colors text-sm"
                >
                  {copied ? (
                    <>
                      <CheckCircle className="h-4 w-4" />
                      Kopyalandı!
                    </>
                  ) : (
                    <>
                      <Copy className="h-4 w-4" />
                      Kopyala
                    </>
                  )}
                </button>
                <button
                  onClick={handleReset}
                  className="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-border hover:bg-muted transition-colors text-sm"
                >
                  <RefreshCw className="h-4 w-4" />
                  Yeni
                </button>
              </div>
            </div>

            {/* Email Subject */}
            {emailResult?.subject && (
              <div className="p-4 border-b border-border bg-muted/50">
                <span className="text-sm text-muted-foreground">Konu: </span>
                <span className="font-medium">{emailResult.subject}</span>
              </div>
            )}

            {/* Content */}
            <div className="p-6">
              <div className="whitespace-pre-wrap text-sm leading-relaxed">
                {(letterResult?.cover_letter || emailResult?.body || '')
                  .split('\\n').join('\n')
                  .split('\\r').join('')
                }
              </div>
            </div>
          </div>

          {/* Tips */}
          {result.tips && result.tips.length > 0 && (
            <div className="bg-card border border-border rounded-xl p-4 space-y-3">
              <h3 className="font-medium flex items-center gap-2">
                <Lightbulb className="h-4 w-4 text-yellow-500" />
                İpuçları
              </h3>
              <ul className="space-y-2">
                {result.tips.map((tip, index) => (
                  <li key={index} className="flex items-start gap-2 text-sm text-muted-foreground">
                    <span className="text-yellow-500">•</span>
                    {tip}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Error Result */}
      {result && !result.success && (
        <div className="bg-card border border-red-500/30 rounded-xl p-6 text-center">
          <p className="text-red-500">{result.error || 'Bir hata oluştu'}</p>
          <button
            onClick={handleReset}
            className="mt-4 px-4 py-2 rounded-lg bg-muted hover:bg-muted/80 transition-colors"
          >
            Tekrar Dene
          </button>
        </div>
      )}
    </div>
  );
}

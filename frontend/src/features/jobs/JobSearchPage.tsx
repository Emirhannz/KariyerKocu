import { useState, useEffect } from 'react';
import { 
  Search, 
  Briefcase, 
  Loader2,
  ExternalLink,
  Calendar,
  MapPin,
  AlertCircle,
  CheckCircle2,
  GraduationCap,
  Zap,
  X,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Clock
} from 'lucide-react';
import api from '../../lib/api';
import { cn } from '../../lib/utils';

// Tipler
interface JobResult {
  title: string;
  company?: string;
  location?: string;
  url: string;
  description?: string;
  snippet: string;
  source: string;
  date_posted?: string;
}

// Başvurulan iş tipini tanımla
interface AppliedJob {
  url: string;
  title: string;
  company?: string;
  appliedAt: string;
}

interface SkillGapResult {
  success: boolean;
  match_percentage: number;
  matching_skills: string[];
  missing_skills: string[];
  partial_skills: string[];
  recommendation: string;
  error?: string;
}

interface JobSearchResponse {
  success: boolean;
  jobs: JobResult[];
  total_count: number;
  scraped_at: string;
  error: string | null;
  search_info?: {
    field: string;
    field_label: string;
    search_term: string;
  };
  filters?: {
    field: string;
    field_label: string;
    search_term: string;
    sites: string[];
    time_range: string;
    location?: string;
  };
}

interface FieldOption {
  value: string;
  label: string;
  keywords_count?: number;
}

interface SearchOptions {
  fields: FieldOption[];
  experience_levels: { value: string; label: string }[];
  job_types: { value: string; label: string }[];
  sites: { value: string; domain: string }[];
  time_ranges: { value: string; label: string }[];
}

// API'den gelen meslek grupları
interface ProfessionGroup {
  value: string;
  label: string;
  label_en: string;
  fields: { value: string; label: string }[];
}

export function JobSearchPage() {
  // Form state
  const [profession, setProfession] = useState('bilgisayar_muhendisligi');
  const [selectedField, setSelectedField] = useState<string>('backend');
  const [timeRange, setTimeRange] = useState<string>('w');
  const [city, setCity] = useState<string>('');
  const [experienceLevel, setExperienceLevel] = useState<string>('');
  const [isRemote, setIsRemote] = useState<boolean>(false);
  const [jobType, setJobType] = useState<string>('');
  
  // Custom mode için (Siz Belirtin)
  const [isCustomMode, setIsCustomMode] = useState(false);
  const [customProfession, setCustomProfession] = useState('');
  const [customField, setCustomField] = useState('');
  
  // API'den gelen meslek grupları
  const [professions, setProfessions] = useState<ProfessionGroup[]>([]);
  const [availableFields, setAvailableFields] = useState<{ value: string; label: string }[]>([]);
  
  // Options from API
  const [options, setOptions] = useState<SearchOptions | null>(null);
  const [cities, setCities] = useState<string[]>([]);
  
  // Results state
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<JobSearchResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  
  // Arama yapıldığında hangi meslek seçiliydi? (Skill Gap için)
  const [searchedProfession, setSearchedProfession] = useState<string | null>(null);
  const [searchedIsCustomMode, setSearchedIsCustomMode] = useState<boolean>(false);
  
  // Skill Gap Modal state
  const [skillGapModalOpen, setSkillGapModalOpen] = useState(false);
  const [selectedJob, setSelectedJob] = useState<JobResult | null>(null);
  const [skillGapLoading, setSkillGapLoading] = useState(false);
  const [skillGapResult, setSkillGapResult] = useState<SkillGapResult | null>(null);
  
  // Başvurulan işler state
  const [appliedJobs, setAppliedJobs] = useState<AppliedJob[]>([]);
  
  // Component yüklendiğinde localStorage'dan başvuruları yükle
  useEffect(() => {
    const savedApplied = localStorage.getItem('appliedJobs');
    if (savedApplied) {
      try {
        setAppliedJobs(JSON.parse(savedApplied));
      } catch (e) {
        console.error('Başvurular yüklenemedi:', e);
      }
    }
  }, []);
  
  // Başvuru işaretle/kaldır
  const toggleApplied = (job: JobResult) => {
    setAppliedJobs(prev => {
      const isAlreadyApplied = prev.some(aj => aj.url === job.url);
      let updated: AppliedJob[];
      
      if (isAlreadyApplied) {
        // Kaldır
        updated = prev.filter(aj => aj.url !== job.url);
      } else {
        // Ekle
        const newApplied: AppliedJob = {
          url: job.url,
          title: job.title,
          company: job.company,
          appliedAt: new Date().toISOString()
        };
        updated = [...prev, newApplied];
        
        // Başvuru istatistiklerini güncelle
        const today = new Date().toISOString().split('T')[0];
        const stats = JSON.parse(localStorage.getItem('applicationStats') || '{}');
        stats[today] = (stats[today] || 0) + 1;
        localStorage.setItem('applicationStats', JSON.stringify(stats));
      }
      
      localStorage.setItem('appliedJobs', JSON.stringify(updated));
      return updated;
    });
  };
  
  // İş başvurulmuş mu kontrol et
  const isJobApplied = (jobUrl: string) => appliedJobs.some(aj => aj.url === jobUrl);
  
  // Seçenekleri ve meslek gruplarını yükle
  useEffect(() => {
    const fetchData = async () => {
      try {
        // Options
        const optionsRes = await api.get<SearchOptions>('/jobs/options');
        setOptions(optionsRes.data);
        
        // Şehirler
        const citiesRes = await api.get<{ cities: string[] }>('/jobs/cities/turkey');
        setCities(citiesRes.data.cities);
        
        // Meslek grupları
        const professionsRes = await api.get<{ professions: ProfessionGroup[] }>('/jobs/professions');
        setProfessions(professionsRes.data.professions);
        
        // İlk meslek grubunun alanlarını ayarla
        if (professionsRes.data.professions.length > 0) {
          const firstProfession = professionsRes.data.professions[0];
          setProfession(firstProfession.value);
          setAvailableFields(firstProfession.fields);
          if (firstProfession.fields.length > 0) {
            setSelectedField(firstProfession.fields[0].value);
          }
        }
      } catch (err) {
        console.error('Veri yüklenemedi:', err);
      }
    };
    fetchData();
  }, []);

  // Meslek değişince alanları güncelle
  useEffect(() => {
    if (isCustomMode) return;
    
    const selected = professions.find(p => p.value === profession);
    if (selected) {
      setAvailableFields(selected.fields);
      const fieldValues = selected.fields.map(f => f.value);
      if (!fieldValues.includes(selectedField) && selected.fields.length > 0) {
        setSelectedField(selected.fields[0].value);
      }
    }
  }, [profession, professions, isCustomMode, selectedField]);

  // Seçili alanın bilgisini al
  const getFieldInfo = (fieldKey: string): FieldOption | undefined => {
    return options?.fields.find(f => f.value === fieldKey);
  };

  // Arama yap
  const handleSearch = async () => {
    setLoading(true);
    setError(null);
    setResults(null);
    
    // Arama anındaki meslek bilgisini kaydet (Skill Gap için)
    setSearchedProfession(profession);
    setSearchedIsCustomMode(isCustomMode);
    
    try {
      let response;
      
      if (isCustomMode) {
        // Custom arama
        if (!customProfession && !customField) {
          setError('Lütfen meslek veya pozisyon belirtin');
          setLoading(false);
          return;
        }
        
        response = await api.post<JobSearchResponse>('/jobs/search-custom', null, {
          params: {
            profession: customProfession,
            field: customField,
            limit: 20
          }
        });
      } else {
        // Normal arama
        if (!selectedField) {
          setError('Lütfen bir alan seçin');
          setLoading(false);
          return;
        }
        
        const payload: Record<string, unknown> = {
          field: selectedField,
          time_range: timeRange,
          limit: 20,
        };
        
        if (city) payload.city = city;
        if (experienceLevel) payload.experience_level = experienceLevel;
        if (isRemote) payload.is_remote = true;
        if (jobType) payload.job_type = jobType;
        
        response = await api.post<JobSearchResponse>('/jobs/search', payload);
      }
      
      setResults(response.data);
      
      // Başarılı arama sonuçlarını localStorage'a kaydet
      if (response.data.success && response.data.jobs && response.data.jobs.length > 0) {
        // Alan label'ını bul
        let queryLabel: string;
        if (isCustomMode) {
          queryLabel = `${customProfession} ${customField}`.trim();
        } else {
          // Seçili alanın label'ını bul
          const fieldInfo = availableFields.find(f => f.value === selectedField);
          queryLabel = fieldInfo?.label || response.data.search_info?.field_label || selectedField;
        }
        
        const searchHistory = {
          timestamp: new Date().toISOString(),
          query: queryLabel,
          results: response.data.jobs.slice(0, 20), // İlk 20 sonuç
          total_count: response.data.total_count || response.data.jobs.length
        };
        localStorage.setItem('lastJobSearch', JSON.stringify(searchHistory));
      }
      
      if (!response.data.success) {
        setError(response.data.error || 'Arama başarısız oldu');
      }
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Bir hata oluştu';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const selectedFieldInfo = getFieldInfo(selectedField);

  // Site renkleri
  const getSiteColor = (source: string) => {
    const s = source.toLowerCase();
    if (s.includes('indeed')) return 'bg-blue-500/10 text-blue-500';
    if (s.includes('linkedin')) return 'bg-sky-500/10 text-sky-500';
    if (s.includes('glassdoor')) return 'bg-green-500/10 text-green-500';
    if (s.includes('kariyer')) return 'bg-orange-500/10 text-orange-500';
    return 'bg-gray-500/10 text-gray-500';
  };

  // Skill Gap analizi yap
  const handleSkillGapAnalysis = async (job: JobResult) => {
    setSelectedJob(job);
    setSkillGapModalOpen(true);
    setSkillGapLoading(true);
    setSkillGapResult(null);
    
    try {
      const response = await api.post<SkillGapResult>('/jobs/skill-gap', {
        job_title: job.title,
        job_description: job.description || job.snippet || '',
        company_name: job.company || ''
      });
      setSkillGapResult(response.data);
    } catch (err) {
      setSkillGapResult({
        success: false,
        match_percentage: 0,
        matching_skills: [],
        missing_skills: [],
        partial_skills: [],
        recommendation: '',
        error: 'Analiz yapılamadı. Lütfen CV yüklediğinizden emin olun.'
      });
    } finally {
      setSkillGapLoading(false);
    }
  };

  const closeSkillGapModal = () => {
    setSkillGapModalOpen(false);
    setSelectedJob(null);
    setSkillGapResult(null);
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold gradient-text mb-2">🔍 Türkiye İş İlanları</h1>
        <p className="text-muted-foreground">
          Çeşitli platformlardan güncel iş ilanları
        </p>
      </div>

      {/* Search Form */}
      <div className="bg-card border border-border rounded-2xl p-6 shadow-lg">
        {/* Meslek + İlan Tarihi */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <label className="text-sm font-medium flex items-center gap-2">
              <GraduationCap className="h-4 w-4 text-primary" />
              Meslek
            </label>
            <select
              value={isCustomMode ? 'custom' : profession}
              onChange={(e) => {
                if (e.target.value === 'custom') {
                  setIsCustomMode(true);
                } else {
                  setIsCustomMode(false);
                  setProfession(e.target.value);
                }
              }}
              className="w-full px-4 py-3 rounded-xl bg-background border border-border focus:border-primary focus:ring-1 focus:ring-primary outline-none transition-all"
            >
              {professions.map(p => (
                <option key={p.value} value={p.value}>{p.label}</option>
              ))}
              <option value="custom">✏️ Siz Belirtin</option>
            </select>
          </div>

          {/* İlan Tarihi */}
          <div className="space-y-2">
            <label className="text-sm font-medium flex items-center gap-2">
              <Calendar className="h-4 w-4 text-primary" />
              İlan Tarihi
            </label>
            <select
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value)}
              className="w-full px-4 py-3 rounded-xl bg-background border border-border focus:border-primary focus:ring-1 focus:ring-primary outline-none transition-all"
            >
              {options?.time_ranges.map(t => (
                <option key={t.value} value={t.value}>{t.label}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Custom Mode - Siz Belirtin */}
        {isCustomMode && (
          <div className="mt-4 p-4 rounded-xl bg-primary/5 border border-primary/20 space-y-4">
            <p className="text-sm text-muted-foreground">
              Mesleğinizi ve aradığınız pozisyonu yazın:
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Meslek</label>
                <input
                  type="text"
                  value={customProfession}
                  onChange={(e) => setCustomProfession(e.target.value)}
                  placeholder="Örn: Hemşire, Avukat, Muhasebeci..."
                  className="w-full px-4 py-3 rounded-xl bg-background border border-border focus:border-primary focus:ring-1 focus:ring-primary outline-none transition-all"
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Pozisyon / Alan</label>
                <input
                  type="text"
                  value={customField}
                  onChange={(e) => setCustomField(e.target.value)}
                  placeholder="Örn: Yoğun Bakım Hemşiresi, Ceza Avukatı..."
                  className="w-full px-4 py-3 rounded-xl bg-background border border-border focus:border-primary focus:ring-1 focus:ring-primary outline-none transition-all"
                />
              </div>
            </div>
          </div>
        )}

        {/* Alan Seçimi - Sadece custom mode değilse göster */}
        {!isCustomMode && (
          <div className="mt-6 space-y-3">
            <label className="text-sm font-medium flex items-center gap-2">
              <Briefcase className="h-4 w-4 text-primary" />
              Aranacak Pozisyon
            </label>
            <div className="flex flex-wrap gap-2">
              {availableFields.map(field => {
                const isSelected = selectedField === field.value;
                return (
                  <button
                    key={field.value}
                    onClick={() => setSelectedField(field.value)}
                    className={cn(
                      'px-4 py-2 rounded-full text-sm font-medium transition-all',
                      isSelected
                        ? 'bg-green-500 text-white'
                        : 'bg-muted text-muted-foreground hover:bg-muted/80'
                    )}
                  >
                    {field.label}
                  </button>
                );
              })}
            </div>
          </div>
        )}

        {/* Tecrübe Seviyesi ve Şehir */}
        <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Tecrübe Seviyesi */}
          <div className="space-y-2">
            <label className="text-sm font-medium flex items-center gap-2">
              <Briefcase className="h-4 w-4 text-primary" />
              Tecrübe Seviyesi
            </label>
            <select
              value={experienceLevel}
              onChange={(e) => setExperienceLevel(e.target.value)}
              className="w-full px-4 py-3 rounded-xl bg-background border border-border focus:border-primary focus:ring-1 focus:ring-primary outline-none transition-all"
            >
              <option value="">Tüm Seviyeler</option>
              {options?.experience_levels.map(exp => (
                <option key={exp.value} value={exp.value}>{exp.label}</option>
              ))}
            </select>
          </div>

          {/* Şehir */}
          <div className="space-y-2">
            <label className="text-sm font-medium flex items-center gap-2">
              <MapPin className="h-4 w-4 text-primary" />
              Şehir
            </label>
            <select
              value={city}
              onChange={(e) => setCity(e.target.value)}
              className="w-full px-4 py-3 rounded-xl bg-background border border-border focus:border-primary focus:ring-1 focus:ring-primary outline-none transition-all"
            >
              <option value="">Tüm Türkiye</option>
              {cities.map(c => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          </div>
        </div>

        {/* İş Tipi ve Remote */}
        <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* İş Tipi */}
          <div className="space-y-2">
            <label className="text-sm font-medium flex items-center gap-2">
              <Clock className="h-4 w-4 text-primary" />
              İş Tipi
            </label>
            <select
              value={jobType}
              onChange={(e) => setJobType(e.target.value)}
              className="w-full px-4 py-3 rounded-xl bg-background border border-border focus:border-primary focus:ring-1 focus:ring-primary outline-none transition-all"
            >
              <option value="">Tüm İş Tipleri</option>
              {options?.job_types?.map(jt => (
                <option key={jt.value} value={jt.value}>{jt.label}</option>
              ))}
            </select>
          </div>

          {/* Remote Checkbox */}
          <div className="space-y-2">
            <label className="text-sm font-medium flex items-center gap-2">
              <MapPin className="h-4 w-4 text-primary" />
              Çalışma Şekli
            </label>
            <label className="flex items-center gap-3 px-4 py-3 rounded-xl bg-background border border-border cursor-pointer hover:border-primary transition-all">
              <input
                type="checkbox"
                checked={isRemote}
                onChange={(e) => setIsRemote(e.target.checked)}
                className="w-5 h-5 rounded border-border text-primary focus:ring-primary"
              />
              <span className="text-sm">🏠 Sadece Uzaktan Çalışma (Remote)</span>
            </label>
          </div>
        </div>

        {/* Bilgilendirme Notu */}
        <div className="mt-4 p-3 rounded-xl bg-yellow-500/10 border border-yellow-500/20">
          <p className="text-xs text-yellow-600 flex items-center gap-2">
            <AlertCircle className="h-4 w-4" />
            <span>
              <strong>Not:</strong> Konum, tecrübe ve iş tipi filtreleri bazı platformlarda uygulanır. 
              Diğer kaynaklardaki ilanlar bu filtrelerden etkilenmeyebilir.
            </span>
          </p>
        </div>

        {/* Error */}
        {error && (
          <div className="mt-4 p-4 rounded-xl bg-destructive/10 text-destructive flex items-center gap-2">
            <AlertCircle className="h-5 w-5" />
            {error}
          </div>
        )}

        {/* Search Button */}
        <div className="mt-6">
          <button
            onClick={handleSearch}
            disabled={loading || (isCustomMode ? (!customProfession && !customField) : !selectedField)}
            className="w-full py-4 rounded-xl gradient-primary text-white font-semibold flex items-center justify-center gap-2 hover:opacity-90 transition-opacity disabled:opacity-50"
          >
            {loading ? (
              <>
                <Loader2 className="h-5 w-5 animate-spin" />
                İlanlar aranıyor...
              </>
            ) : (
              <>
                <Search className="h-5 w-5" />
                {isCustomMode 
                  ? `${customField || customProfession || 'İş'} İlanlarını Ara`
                  : `${selectedFieldInfo?.label || 'İş'} İlanlarını Ara`
                }
              </>
            )}
          </button>
        </div>
      </div>

      {/* Results */}
      {results && (
        <div className="space-y-4">
          <div className="flex items-center justify-between flex-wrap gap-2">
            <h2 className="text-xl font-semibold flex items-center gap-2">
              <CheckCircle2 className="h-5 w-5 text-green-500" />
              {results.total_count} İlan Bulundu
            </h2>
            <span className="text-sm text-muted-foreground">
              {new Date(results.scraped_at).toLocaleString('tr-TR')}
            </span>
          </div>

          {/* Filters Info */}
          {results.filters && (
            <div className="flex flex-wrap gap-2">
              <span className="px-3 py-1 rounded-full text-xs bg-green-500/10 text-green-500">
                🔍 {results.filters.search_term}
              </span>
              {results.filters.location && (
                <span className="px-3 py-1 rounded-full text-xs bg-primary/10 text-primary">
                  📍 {results.filters.location}
                </span>
              )}
            </div>
          )}

          {/* Jobs */}
          {results.jobs.length === 0 ? (
            <div className="text-center py-12 text-muted-foreground">
              <Search className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>Kriterlere uygun ilan bulunamadı.</p>
            </div>
          ) : (
            <div className="grid gap-4">
              {results.jobs.map((job, index) => {
                // Skill Gap sadece bilgisayar mühendisliği için göster
                // ARAMA ANINDA seçili olan mesleğe bak, mevcut dropdown değerine değil!
                const isComputerEngineering = searchedProfession === 'bilgisayar_muhendisligi' && !searchedIsCustomMode;
                const notKariyer = job.source?.toLowerCase() !== 'kariyer.net';
                const canAnalyze = isComputerEngineering && notKariyer;
                
                return (
                  <div
                    key={index}
                    className="p-5 rounded-xl border border-border bg-card hover:border-primary/50 hover:shadow-lg transition-all group"
                  >
                    <div className="flex items-start gap-4">
                      {/* Sol Taraf: Skill Gap Butonu */}
                      {canAnalyze && (
                        <button
                          onClick={(e) => {
                            e.preventDefault();
                            e.stopPropagation();
                            handleSkillGapAnalysis(job);
                          }}
                          className="flex-shrink-0 p-3 rounded-xl bg-gradient-to-br from-primary/20 to-primary/10 hover:from-primary/30 hover:to-primary/20 text-primary transition-all hover:scale-105 border border-primary/20"
                          title="CV Uyum Analizi"
                        >
                          <Zap className="h-6 w-6" />
                        </button>
                      )}
                      
                      {/* Orta: İlan Bilgileri */}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-2 flex-wrap">
                          <span className={cn('px-2 py-1 rounded-full text-xs font-medium', getSiteColor(job.source))}>
                            {job.source}
                          </span>
                          {job.company && (
                            <span className="px-2 py-1 rounded-full text-xs font-medium bg-muted text-muted-foreground">
                              🏢 {job.company}
                            </span>
                          )}
                          {job.location && (
                            <span className="px-2 py-1 rounded-full text-xs font-medium bg-muted text-muted-foreground">
                              📍 {job.location}
                            </span>
                          )}
                          {job.date_posted && (
                            <span className="px-2 py-1 rounded-full text-xs font-medium bg-muted text-muted-foreground">
                              📅 {job.date_posted}
                            </span>
                          )}
                        </div>
                        <a 
                          href={job.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="font-semibold text-lg hover:text-primary transition-colors line-clamp-2"
                        >
                          {job.title}
                        </a>
                        {job.snippet && (
                          <p className="mt-2 text-sm text-muted-foreground line-clamp-2">
                            {job.snippet}
                          </p>
                        )}
                      </div>
                      
                      {/* Sağ: Başvuru Checkbox ve Harici Link */}
                      <div className="flex flex-col items-center gap-2 flex-shrink-0">
                        {/* Başvuru Checkbox */}
                        <button
                          onClick={(e) => {
                            e.preventDefault();
                            e.stopPropagation();
                            toggleApplied(job);
                          }}
                          className={cn(
                            "p-2 rounded-lg transition-all",
                            isJobApplied(job.url)
                              ? "bg-green-500/20 text-green-500 hover:bg-green-500/30"
                              : "bg-muted/50 text-muted-foreground hover:bg-muted hover:text-foreground"
                          )}
                          title={isJobApplied(job.url) ? "Başvuru yapıldı ✓" : "Başvuru yaptım olarak işaretle"}
                        >
                          {isJobApplied(job.url) ? (
                            <CheckCircle className="h-5 w-5" />
                          ) : (
                            <CheckCircle2 className="h-5 w-5" />
                          )}
                        </button>
                        
                        {/* Harici Link */}
                        <a
                          href={job.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="p-2 rounded-lg hover:bg-muted transition-colors"
                          title="İlana git"
                        >
                          <ExternalLink className="h-5 w-5 text-muted-foreground hover:text-primary" />
                        </a>
                      </div>
                    </div>
                    
                    {/* Başvuru durumu badge */}
                    {isJobApplied(job.url) && (
                      <div className="mt-3 pt-3 border-t border-border">
                        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-green-500/10 text-green-600 text-xs font-medium">
                          <CheckCircle className="h-3.5 w-3.5" />
                          Başvuru yapıldı
                        </span>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* Loading */}
      {loading && (
        <div className="text-center py-8">
          <div className="inline-flex items-center gap-3 px-6 py-4 rounded-2xl bg-card border border-border">
            <Loader2 className="h-6 w-6 animate-spin text-primary" />
            <div className="text-left">
              <p className="font-medium">İş platformları taranıyor...</p>
              <p className="text-sm text-muted-foreground">Bu işlem 15-30 saniye sürebilir</p>
            </div>
          </div>
        </div>
      )}

      {/* Skill Gap Modal */}
      {skillGapModalOpen && selectedJob && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center">
          <div 
            className="absolute inset-0 bg-black/60 backdrop-blur-md"
            onClick={closeSkillGapModal}
          />
          
          <div className="relative bg-card border border-border rounded-2xl p-6 w-full max-w-lg mx-4 shadow-2xl animate-in fade-in zoom-in-95 duration-200 max-h-[80vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-lg flex items-center gap-2">
                <Zap className="h-5 w-5 text-primary" />
                CV Uyum Analizi
              </h3>
              <button 
                onClick={closeSkillGapModal}
                className="p-1 rounded-lg hover:bg-muted transition-colors"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            {/* İlan Bilgisi */}
            <div className="p-3 rounded-xl bg-muted/50 mb-4">
              <p className="font-medium line-clamp-2">{selectedJob.title}</p>
              {selectedJob.company && (
                <p className="text-sm text-muted-foreground">🏢 {selectedJob.company}</p>
              )}
            </div>
            
            {skillGapLoading ? (
              <div className="text-center py-8">
                <Loader2 className="h-8 w-8 animate-spin text-primary mx-auto mb-2" />
                <p className="text-sm text-muted-foreground">CV'niz analiz ediliyor...</p>
              </div>
            ) : skillGapResult ? (
              <div className="space-y-4">
                {skillGapResult.error ? (
                  <div className="p-4 rounded-xl bg-destructive/10 text-destructive flex items-center gap-2">
                    <AlertTriangle className="h-5 w-5" />
                    {skillGapResult.error}
                  </div>
                ) : (
                  <>
                    {/* Uyum Yüzdesi */}
                    <div className="text-center p-4 rounded-xl bg-gradient-to-r from-primary/10 to-primary/5">
                      <div className="text-4xl font-bold text-primary mb-1">
                        %{skillGapResult.match_percentage}
                      </div>
                      <p className="text-sm text-muted-foreground">Genel Uyum</p>
                    </div>

                    {/* Eşleşen Yetenekler */}
                    {skillGapResult.matching_skills.length > 0 && (
                      <div>
                        <h4 className="font-medium flex items-center gap-2 mb-2">
                          <CheckCircle className="h-4 w-4 text-green-500" />
                          Eşleşen Yetenekler
                        </h4>
                        <div className="flex flex-wrap gap-2">
                          {skillGapResult.matching_skills.map((skill, i) => (
                            <span key={i} className="px-2 py-1 rounded-full text-xs bg-green-500/10 text-green-500">
                              {skill}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Eksik Yetenekler */}
                    {skillGapResult.missing_skills.length > 0 && (
                      <div>
                        <h4 className="font-medium flex items-center gap-2 mb-2">
                          <XCircle className="h-4 w-4 text-red-500" />
                          Eksik Yetenekler
                        </h4>
                        <div className="flex flex-wrap gap-2">
                          {skillGapResult.missing_skills.map((skill, i) => (
                            <span key={i} className="px-2 py-1 rounded-full text-xs bg-red-500/10 text-red-500">
                              {skill}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Kısmen Eşleşen */}
                    {skillGapResult.partial_skills.length > 0 && (
                      <div>
                        <h4 className="font-medium flex items-center gap-2 mb-2">
                          <AlertTriangle className="h-4 w-4 text-yellow-500" />
                          Benzer Yetenekler
                        </h4>
                        <div className="flex flex-wrap gap-2">
                          {skillGapResult.partial_skills.map((skill, i) => (
                            <span key={i} className="px-2 py-1 rounded-full text-xs bg-yellow-500/10 text-yellow-500">
                              {skill}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Öneri */}
                    {skillGapResult.recommendation && (
                      <div className="p-3 rounded-xl bg-primary/5 border border-primary/20">
                        <h4 className="font-medium flex items-center gap-2 mb-1">
                          💡 Öneri
                        </h4>
                        <p className="text-sm text-muted-foreground">
                          {skillGapResult.recommendation}
                        </p>
                      </div>
                    )}
                  </>
                )}
              </div>
            ) : null}

            {/* İlana Git Butonu */}
            <div className="mt-6">
              <a
                href={selectedJob.url}
                target="_blank"
                rel="noopener noreferrer"
                className="w-full py-3 rounded-xl gradient-primary text-white font-semibold flex items-center justify-center gap-2 hover:opacity-90 transition-opacity"
              >
                <ExternalLink className="h-4 w-4" />
                İlana Git
              </a>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

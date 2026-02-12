import { useEffect, useState, useRef, useCallback } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { 
  FileText, 
  BarChart3, 
  MessageSquare, 
  Target,
  Upload,
  TrendingUp,
  CheckCircle,
  XCircle,
  Clock,
  ArrowRight,
  Loader2,
  Lightbulb,
  Eye,
  X,
  Briefcase,
  Search,
  PenTool,
  Mail,
  AlertTriangle,
  Trash2,
  ExternalLink,
  ChevronLeft,
  ChevronRight,
  Code2,
  BarChart,
  Bot
} from 'lucide-react';
import api from '../../lib/api';
import type { DashboardData } from '../../types';
import { formatDate } from '../../lib/utils';
import { SkeletonDashboard } from '../../components/ui/Skeleton';

// LocalStorage'dan kaydedilen iş arama sonuçları tipi
interface SavedJobSearch {
  timestamp: string;
  query: string;
  results: {
    title: string;
    company?: string;
    location?: string;
    url: string;
    source: string;
  }[];
  total_count: number;
}

// LocalStorage'dan başvuru sayıları tipi
interface ApplicationStats {
  [date: string]: number;
}

interface AnalysisListItem {
  id: string;
  created_at: string;
  fields: string[];
  field_names: string[];
  experience_level: string;
  overall_score: number;
}

// Custom Confirm Modal Component
function ConfirmModal({ 
  isOpen, 
  onClose, 
  onConfirm, 
  title, 
  message 
}: { 
  isOpen: boolean; 
  onClose: () => void; 
  onConfirm: () => void; 
  title: string; 
  message: string; 
}) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-black/60 backdrop-blur-sm"
        onClick={onClose}
      />
      
      {/* Modal */}
      <div className="relative bg-card border border-border rounded-2xl p-6 max-w-md w-full mx-4 shadow-2xl animate-in fade-in zoom-in-95 duration-200">
        {/* Icon */}
        <div className="w-12 h-12 rounded-full bg-red-500/10 flex items-center justify-center mx-auto mb-4">
          <AlertTriangle className="h-6 w-6 text-red-500" />
        </div>
        
        {/* Title */}
        <h3 className="text-lg font-semibold text-center mb-2">
          {title}
        </h3>
        
        {/* Message */}
        <p className="text-muted-foreground text-center text-sm mb-6">
          {message}
        </p>
        
        {/* Buttons */}
        <div className="flex gap-3">
          <button
            onClick={onClose}
            className="flex-1 py-2.5 px-4 rounded-lg border border-border hover:bg-muted transition-colors font-medium"
          >
            Vazgeç
          </button>
          <button
            onClick={() => {
              onConfirm();
            }}
            className="flex-1 py-2.5 px-4 rounded-lg bg-red-500 text-white hover:bg-red-600 transition-colors font-medium"
          >
            İptal Et
          </button>
        </div>
      </div>
    </div>
  );
}

// Son İş Aramaları Carousel Bileşeni
function JobSearchCarousel({ lastJobSearch }: { lastJobSearch: SavedJobSearch | null }) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const jobs = lastJobSearch?.results?.slice(0, 20) || [];
  const totalJobs = jobs.length;

  // 10 saniyede bir otomatik değiştirme
  useEffect(() => {
    if (totalJobs <= 1) return;
    
    const interval = setInterval(() => {
      setCurrentIndex((prev) => (prev + 1) % totalJobs);
    }, 10000);
    
    return () => clearInterval(interval);
  }, [totalJobs]);

  if (!lastJobSearch || jobs.length === 0) {
    return (
      <div className="bg-card border border-border rounded-xl p-6 flex flex-col items-center justify-center min-h-[300px]">
        <Briefcase className="h-12 w-12 text-muted-foreground/30 mb-4" />
        <h3 className="font-semibold text-lg mb-2">Son İş Aramaları</h3>
        <p className="text-sm text-muted-foreground text-center mb-4">
          Henüz iş araması yapmadınız
        </p>
        <Link 
          to="/jobs" 
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 transition-colors"
        >
          <Search className="h-4 w-4" />
          İş Ara
        </Link>
      </div>
    );
  }

  const currentJob = jobs[currentIndex];

  return (
    <div className="bg-card border border-border rounded-xl p-6 flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold text-lg flex items-center gap-2">
          <Briefcase className="h-5 w-5 text-orange-500" />
          Son İş Aramaları
        </h3>
        <span className="text-xs text-muted-foreground bg-muted px-2 py-1 rounded-full">
          {currentIndex + 1} / {totalJobs}
        </span>
      </div>
      
      <p className="text-sm text-muted-foreground mb-4">
        <strong>"{lastJobSearch.query}"</strong> • {lastJobSearch.total_count} sonuç bulundu
      </p>

      {/* Mevcut İş İlanı */}
      <a
        href={currentJob.url}
        target="_blank"
        rel="noopener noreferrer"
        className="flex-1 p-4 rounded-xl bg-gradient-to-r from-orange-500/10 to-yellow-500/10 border border-orange-500/20 hover:border-orange-500/40 transition-all group min-h-[140px] flex flex-col"
      >
        <div className="flex items-start justify-between gap-2 mb-3">
          <span className="text-xs px-2 py-1 rounded-full bg-orange-500/20 text-orange-500 font-medium">
            {currentJob.source}
          </span>
          <ExternalLink className="h-4 w-4 text-muted-foreground group-hover:text-orange-500 transition-colors flex-shrink-0" />
        </div>
        
        <h4 className="font-semibold text-lg group-hover:text-orange-500 transition-colors line-clamp-2 mb-2">
          {currentJob.title}
        </h4>
        
        <div className="mt-auto space-y-1">
          {currentJob.company && (
            <p className="text-sm text-muted-foreground flex items-center gap-1.5">
              🏢 {currentJob.company}
            </p>
          )}
          {currentJob.location && (
            <p className="text-sm text-muted-foreground flex items-center gap-1.5">
              📍 {currentJob.location}
            </p>
          )}
        </div>
      </a>

      {/* Navigasyon */}
      <div className="flex items-center justify-between mt-4">
        <button
          onClick={() => setCurrentIndex((prev) => (prev - 1 + totalJobs) % totalJobs)}
          className="p-2 rounded-lg hover:bg-muted transition-colors"
        >
          <ChevronLeft className="h-5 w-5" />
        </button>
        
        <div className="flex gap-1">
          {jobs.slice(0, 10).map((_, i) => (
            <button
              key={i}
              onClick={() => setCurrentIndex(i)}
              className={`w-2 h-2 rounded-full transition-colors ${
                i === currentIndex ? 'bg-orange-500' : 'bg-muted-foreground/30'
              }`}
            />
          ))}
          {totalJobs > 10 && (
            <span className="text-xs text-muted-foreground ml-1">+{totalJobs - 10}</span>
          )}
        </div>
        
        <button
          onClick={() => setCurrentIndex((prev) => (prev + 1) % totalJobs)}
          className="p-2 rounded-lg hover:bg-muted transition-colors"
        >
          <ChevronRight className="h-5 w-5" />
        </button>
      </div>

      {/* Tümünü Gör Linki */}
      <Link 
        to="/jobs" 
        className="flex items-center justify-center gap-2 w-full py-2.5 mt-4 rounded-lg bg-orange-500/10 text-orange-500 hover:bg-orange-500/20 transition-colors font-medium text-sm"
      >
        Tüm Aramaları Gör <ArrowRight className="h-4 w-4" />
      </Link>
    </div>
  );
}

export function DashboardPage() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [cancellingInterview, setCancellingInterview] = useState(false);
  
  // Analysis selection modal state
  const [showAnalysisModal, setShowAnalysisModal] = useState(false);
  const [modalType, setModalType] = useState<'view' | 'recommend'>('recommend');
  const [analyses, setAnalyses] = useState<AnalysisListItem[]>([]);
  const [loadingAnalyses, setLoadingAnalyses] = useState(false);
  const [cancelConfirmOpen, setCancelConfirmOpen] = useState(false);
  
  // Analiz silme modal state'leri
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [deleteTargetId, setDeleteTargetId] = useState<string | null>(null);
  const [deletingAnalysis, setDeletingAnalysis] = useState(false);
  
  // LocalStorage'dan yüklenen veriler
  const [lastJobSearch, setLastJobSearch] = useState<SavedJobSearch | null>(null);
  const [applicationStats, setApplicationStats] = useState<ApplicationStats>({});
  
  // Carousel state
  const [carouselIndex, setCarouselIndex] = useState(0);
  
  const navigate = useNavigate();

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const response = await api.get<DashboardData>('/user/dashboard');
        setData(response.data);
        
        // Backend ile localStorage'ı senkronize et
        // Eğer backend'de aktif mülakat yoksa localStorage'ı temizle
        if (!response.data.interview.has_active_interview) {
          localStorage.removeItem('interview_session');
        }
      } catch (err) {
        setError('Dashboard verisi yüklenemedi');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboard();
    
    // LocalStorage'dan son iş aramalarını yükle
    const savedSearch = localStorage.getItem('lastJobSearch');
    if (savedSearch) {
      try {
        setLastJobSearch(JSON.parse(savedSearch));
      } catch (e) {
        console.error('Son arama yüklenemedi:', e);
      }
    }
    
    // Başvuru istatistiklerini yükle
    const savedStats = localStorage.getItem('applicationStats');
    if (savedStats) {
      try {
        setApplicationStats(JSON.parse(savedStats));
      } catch (e) {
        console.error('Başvuru istatistikleri yüklenemedi:', e);
      }
    }
  }, []);
  
  // Carousel auto-rotate with reset capability
  const carouselIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  
  const startCarouselTimer = useCallback(() => {
    if (carouselIntervalRef.current) {
      clearInterval(carouselIntervalRef.current);
    }
    carouselIntervalRef.current = setInterval(() => {
      setCarouselIndex((prev) => (prev + 1) % 4);
    }, 8000);
  }, []);
  
  const handleCarouselChange = useCallback((newIndex: number | ((prev: number) => number)) => {
    setCarouselIndex(newIndex);
    startCarouselTimer(); // Reset timer on manual change
  }, [startCarouselTimer]);
  
  useEffect(() => {
    startCarouselTimer();
    return () => {
      if (carouselIntervalRef.current) {
        clearInterval(carouselIntervalRef.current);
      }
    };
  }, [startCarouselTimer]);

  // Modal açma fonksiyonu (hem Analizi Gör hem Tavsiye Al için)
  const handleOpenModal = async (type: 'view' | 'recommend') => {
    setModalType(type);
    setLoadingAnalyses(true);
    setShowAnalysisModal(true);
    try {
      const response = await api.get<{ analyses: AnalysisListItem[] }>('/analysis/list');
      setAnalyses(response.data.analyses);
    } catch (err) {
      console.error('Analizler yüklenemedi:', err);
    } finally {
      setLoadingAnalyses(false);
    }
  };

  // Analiz seçildiğinde ilgili sayfaya git
  const handleSelectAnalysis = (analysisId: string) => {
    setShowAnalysisModal(false);
    if (modalType === 'recommend') {
      navigate(`/recommendations?analysis_id=${analysisId}`);
    } else {
      navigate(`/cv/analysis/result?analysis_id=${analysisId}`);
    }
  };

  // Aktif mülakatı iptal et
  const handleCancelInterview = async () => {
    setCancelConfirmOpen(false);
    
    try {
      setCancellingInterview(true);
      await api.delete('/interview/cancel');
    } catch (err) {
      // 404 hatası = zaten aktif mülakat yok, sorun değil
      console.log('Mülakat zaten yok veya iptal edilemedi:', err);
    } finally {
      // Her durumda localStorage'ı temizle
      localStorage.removeItem('interview_session');
      setCancellingInterview(false);
      
      // Dashboard'u yenile
      try {
        const response = await api.get<DashboardData>('/user/dashboard');
        setData(response.data);
      } catch (refreshErr) {
        console.error('Dashboard yenilenemedi:', refreshErr);
      }
    }
  };

  // Analiz silme modal'ını aç
  const openDeleteModal = (e: React.MouseEvent, analysisId: string) => {
    e.stopPropagation();
    setDeleteTargetId(analysisId);
    setDeleteModalOpen(true);
  };

  // Analizi sil
  const handleDeleteAnalysis = async () => {
    if (!deleteTargetId) return;
    
    try {
      setDeletingAnalysis(true);
      await api.delete(`/analysis/${deleteTargetId}`);
      setAnalyses(prev => prev.filter(a => a.id !== deleteTargetId));
      setDeleteModalOpen(false);
      setDeleteTargetId(null);
    } catch (err) {
      console.error('Analiz silinemedi:', err);
    } finally {
      setDeletingAnalysis(false);
    }
  };

  if (loading) {
    return <SkeletonDashboard />;
  }

  if (error || !data) {
    return (
      <div className="text-center py-12">
        <p className="text-destructive">{error || 'Bir hata oluştu'}</p>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Cancel Interview Confirmation Modal */}
      <ConfirmModal
        isOpen={cancelConfirmOpen}
        onClose={() => setCancelConfirmOpen(false)}
        onConfirm={handleCancelInterview}
        title="Mülakatı İptal Et"
        message="Aktif mülakatı iptal etmek istediğinize emin misiniz? Bu işlem geri alınamaz."
      />

      {/* Welcome Section */}
      <div className="space-y-2">
        <h1 className="text-3xl font-bold">
          Merhaba, <span className="gradient-text">{data.user_name || 'Kullanıcı'}</span>! 👋
        </h1>
        <p className="text-muted-foreground">
          Kariyer yolculuğunda bugün ne yapmak istersin?
        </p>
      </div>

      {/* Career Goals Banner */}
      {!data.has_career_goals && (
        <Link 
          to="/profile" 
          className="block bg-gradient-to-r from-primary/20 to-accent/20 border border-primary/30 rounded-xl p-6 hover:border-primary/50 transition-colors"
        >
          <div className="flex items-center gap-4">
            <div className="p-3 rounded-lg bg-primary/20">
              <Target className="h-6 w-6 text-primary" />
            </div>
            <div className="flex-1">
              <h3 className="font-semibold">Kariyer Hedefini Belirle</h3>
              <p className="text-sm text-muted-foreground">
                Hedefini belirlersen sana özel öneriler sunabiliriz
              </p>
            </div>
            <ArrowRight className="h-5 w-5 text-muted-foreground" />
          </div>
        </Link>
      )}

      {/* Üst Sıra - 3 Kart: CV Durumu, CV Analizi, Önyazı */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 stagger-children">
        {/* CV Card */}
        <div className="bg-card border border-border rounded-xl p-6 space-y-4 card-hover">
          <div className="flex items-center justify-between">
            <div className="p-3 rounded-lg bg-blue-500/10 icon-container">
              <FileText className="h-6 w-6 text-blue-500" />
            </div>
            {data.cv.is_uploaded ? (
              <span className="flex items-center gap-1 text-sm text-success">
                <CheckCircle className="h-4 w-4" />
                Yüklendi
              </span>
            ) : (
              <span className="flex items-center gap-1 text-sm text-muted-foreground">
                <Clock className="h-4 w-4" />
                Bekleniyor
              </span>
            )}
          </div>
          
          <div>
            <h3 className="font-semibold text-lg">CV Durumu</h3>
            {data.cv.is_uploaded ? (
              <div className="space-y-1 mt-2">
                <p className="text-sm text-foreground font-medium">{data.cv.filename}</p>
              </div>
            ) : (
              <p className="text-sm text-muted-foreground mt-2">
                CV'ni yükle ve analiz etmeye başla
              </p>
            )}
          </div>

          <div className="flex gap-2">
            <Link 
              to="/cv/upload" 
              className="flex items-center justify-center gap-2 flex-1 py-2.5 rounded-lg bg-blue-500/10 text-blue-500 hover:bg-blue-500/20 transition-colors font-medium text-sm"
            >
              <Upload className="h-4 w-4" />
              {data.cv.is_uploaded ? 'CV Güncelle' : 'CV Yükle'}
            </Link>
            <Link 
              to="/cv/upload?ats=true" 
              className="flex items-center justify-center gap-2 flex-1 py-2.5 rounded-lg bg-orange-500/10 text-orange-500 hover:bg-orange-500/20 transition-colors font-medium text-sm"
            >
              <Bot className="h-4 w-4" />
              ATS Testi
            </Link>
          </div>
        </div>

        {/* Analysis Card */}
        <div className="bg-card border border-border rounded-xl p-6 space-y-4 card-hover">
          <div className="flex items-center justify-between">
            <div className="p-3 rounded-lg bg-purple-500/10 icon-container">
              <BarChart3 className="h-6 w-6 text-purple-500" />
            </div>
            {data.analysis.has_analysis && (
              <span className="text-sm text-muted-foreground">
                {data.analysis.total_analyses} analiz
              </span>
            )}
          </div>
          
          <div>
            <h3 className="font-semibold text-lg">CV Analizi</h3>
            {data.analysis.has_analysis ? (
              <div className="space-y-2 mt-2">
                <div className="flex items-center gap-2">
                  <div className="flex-1 h-2 bg-muted rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-purple-500 rounded-full progress-animated"
                      style={{ width: `${data.analysis.strongest_score || 0}%` }}
                    />
                  </div>
                  <span className="text-sm font-medium">{data.analysis.strongest_score}/100</span>
                </div>
                <p className="text-sm text-muted-foreground">
                  En güçlü alan: <strong>{data.analysis.strongest_field_name}</strong>
                </p>
              </div>
            ) : (
              <p className="text-sm text-muted-foreground mt-2">
                CV'ni analiz et ve güçlü yönlerini keşfet
              </p>
            )}
          </div>

          {/* 3 Aksiyon Butonu */}
          {data.analysis.has_analysis ? (
            <div className="grid grid-cols-3 gap-2">
              <button 
                onClick={() => handleOpenModal('view')}
                className="flex flex-col items-center justify-center gap-1 py-2.5 rounded-lg bg-purple-500/10 text-purple-500 hover:bg-purple-500/20 transition-colors font-medium text-xs"
              >
                <Eye className="h-4 w-4" />
                Analizi Gör
              </button>
              <button 
                onClick={() => handleOpenModal('recommend')}
                className="flex flex-col items-center justify-center gap-1 py-2.5 rounded-lg bg-yellow-500/10 text-yellow-500 hover:bg-yellow-500/20 transition-colors font-medium text-xs"
              >
                <Lightbulb className="h-4 w-4" />
                Tavsiye Al
              </button>
              <Link 
                to="/cv/analysis" 
                className="flex flex-col items-center justify-center gap-1 py-2.5 rounded-lg bg-blue-500/10 text-blue-500 hover:bg-blue-500/20 transition-colors font-medium text-xs"
              >
                <TrendingUp className="h-4 w-4" />
                Yeni Analiz
              </Link>
            </div>
          ) : (
            <Link 
              to="/cv/analysis" 
              className="flex items-center justify-center gap-2 w-full py-2.5 rounded-lg bg-purple-500/10 text-purple-500 hover:bg-purple-500/20 transition-colors font-medium text-sm"
            >
              <TrendingUp className="h-4 w-4" />
              Analiz Et
            </Link>
          )}
        </div>

        {/* Interview Card - Analysis'den sonra Cover Letter gelecek */}
        {/* Cover Letter Card */}
        <div className="bg-card border border-border rounded-xl p-6 space-y-4 card-hover">
          <div className="flex items-center justify-between">
            <div className="p-3 rounded-lg bg-pink-500/10 icon-container">
              <PenTool className="h-6 w-6 text-pink-500" />
            </div>
            <span className="flex items-center gap-1 text-sm text-pink-500">
              <Mail className="h-4 w-4" />
              AI Yazıcı
            </span>
          </div>
          
          <div>
            <h3 className="font-semibold text-lg">Önyazı & E-mail</h3>
            <p className="text-sm text-muted-foreground mt-2">
              CV'nize göre profesyonel önyazı ve başvuru e-maili oluşturun
            </p>
          </div>

          <Link 
            to="/cover-letter" 
            className="flex items-center justify-center gap-2 w-full py-2.5 rounded-lg bg-pink-500/10 text-pink-500 hover:bg-pink-500/20 transition-colors font-medium text-sm"
          >
            <PenTool className="h-4 w-4" />
            Oluştur
          </Link>
        </div>
      </div>

      {/* Alt Sıra - 2 Büyük Kart: Mülakat Simülasyonu, İş İlanı Ara */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 stagger-children">
        {/* Interview Card */}
        <div className="bg-card border border-border rounded-xl p-6 space-y-4 card-hover">
          <div className="flex items-center justify-between">
            <div className="p-3 rounded-lg bg-green-500/10 icon-container">
              <MessageSquare className="h-6 w-6 text-green-500" />
            </div>
            {data.interview.has_interview && (
              <span className="text-sm text-muted-foreground">
                {data.interview.total_interviews} mülakat
              </span>
            )}
          </div>
          
          <div>
            <h3 className="font-semibold text-lg">Mülakat Simülasyonu</h3>
            {data.interview.has_interview ? (
              <div className="space-y-2 mt-2">
                <div className="flex items-center gap-2">
                  {data.interview.passed ? (
                    <span className="flex items-center gap-1 text-success text-sm">
                      <CheckCircle className="h-4 w-4" />
                      Başarılı
                    </span>
                  ) : (
                    <span className="flex items-center gap-1 text-destructive text-sm">
                      <XCircle className="h-4 w-4" />
                      Geliştirmeli
                    </span>
                  )}
                  <span className="text-sm font-medium">
                    {data.interview.last_score?.toFixed(1)}/10
                  </span>
                </div>
                <p className="text-sm text-muted-foreground">
                  Son: {data.interview.last_position}
                </p>
              </div>
            ) : (
              <p className="text-sm text-muted-foreground mt-2">
                Mülakat simülasyonu ile pratik yap
              </p>
            )}
          </div>

          {data.interview.has_active_interview ? (
            <button
              onClick={() => setCancelConfirmOpen(true)}
              disabled={cancellingInterview}
              className="flex items-center justify-center gap-2 w-full py-2.5 rounded-lg bg-red-500/10 text-red-500 hover:bg-red-500/20 transition-colors font-medium text-sm disabled:opacity-50"
            >
              <XCircle className="h-4 w-4" />
              {cancellingInterview ? 'İptal Ediliyor...' : 'Devam Eden Mülakatı İptal Et'}
            </button>
          ) : (
            <div className="grid grid-cols-2 gap-2">
              <Link 
                to="/interview/history" 
                className="flex items-center justify-center gap-2 py-2.5 rounded-lg bg-blue-500/10 text-blue-500 hover:bg-blue-500/20 transition-colors font-medium text-sm"
              >
                <Eye className="h-4 w-4" />
                Değerlendirmeler
              </Link>
              <Link 
                to="/interview/start" 
                className="flex items-center justify-center gap-2 py-2.5 rounded-lg bg-green-500/10 text-green-500 hover:bg-green-500/20 transition-colors font-medium text-sm"
              >
                <MessageSquare className="h-4 w-4" />
                Mülakat Başlat
              </Link>
            </div>
          )}
        </div>

        {/* Job Search Card */}
        <div className="bg-card border border-border rounded-xl p-6 space-y-4 card-hover">
          <div className="flex items-center justify-between">
            <div className="p-3 rounded-lg bg-orange-500/10 icon-container">
              <Briefcase className="h-6 w-6 text-orange-500" />
            </div>
            <span className="flex items-center gap-1 text-sm text-orange-500">
              <Search className="h-4 w-4" />
              Çoklu Platform
            </span>
          </div>
          
          <div>
            <h3 className="font-semibold text-lg">İş İlanı Ara</h3>
            <p className="text-sm text-muted-foreground mt-2">
              Çeşitli platformlardan ilanları bul
            </p>
          </div>

          <Link 
            to="/jobs" 
            className="flex items-center justify-center gap-2 w-full py-2.5 rounded-lg bg-orange-500/10 text-orange-500 hover:bg-orange-500/20 transition-colors font-medium text-sm"
          >
            <Briefcase className="h-4 w-4" />
            İş Ara
          </Link>
        </div>
      </div>

      {/* Dashboard İkili Bölüm - Sol: İpuçları Carousel, Sağ: Son İş Aramaları */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Sol Taraf - Kariyer İpuçları, LeetCode, Başvuru İstatistikleri, Kişisel Gelişim */}
        <div className="bg-card border border-border rounded-xl p-6 overflow-hidden">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-lg flex items-center gap-2">
              {carouselIndex === 0 && <><Code2 className="h-5 w-5 text-yellow-500" /> Günlük Kod Pratiği</>}
              {carouselIndex === 1 && <><Lightbulb className="h-5 w-5 text-blue-500" /> Kariyer İpuçları</>}
              {carouselIndex === 2 && <><BarChart className="h-5 w-5 text-green-500" /> Başvuru İstatistikleri</>}
              {carouselIndex === 3 && <><TrendingUp className="h-5 w-5 text-purple-500" /> Kişisel Gelişim</>}
            </h3>
            <div className="flex items-center gap-2">
              <button 
                onClick={() => handleCarouselChange((prev) => (prev - 1 + 4) % 4)}
                className="p-1.5 rounded-lg hover:bg-muted transition-colors"
              >
                <ChevronLeft className="h-4 w-4" />
              </button>
              <div className="flex gap-1.5">
                {[0, 1, 2, 3].map((i) => (
                  <button
                    key={i}
                    onClick={() => handleCarouselChange(i)}
                    className={`w-2 h-2 rounded-full transition-colors ${
                      i === carouselIndex ? 'bg-primary' : 'bg-muted-foreground/30'
                    }`}
                  />
                ))}
              </div>
              <button 
                onClick={() => handleCarouselChange((prev) => (prev + 1) % 4)}
                className="p-1.5 rounded-lg hover:bg-muted transition-colors"
              >
                <ChevronRight className="h-4 w-4" />
              </button>
            </div>
          </div>
          
          {/* Carousel Content - Fixed height to prevent layout shift */}
          <div className="h-[260px] overflow-hidden">
            {/* Slide 0: LeetCode Günlük Hatırlatma */}
            {carouselIndex === 0 && (
              <div className="space-y-4">
                <div className="p-4 rounded-xl bg-gradient-to-r from-yellow-500/10 to-orange-500/10 border border-yellow-500/20">
                  <div className="flex items-center gap-3 mb-3">
                    <div className="p-2 rounded-lg bg-yellow-500/20">
                      <Code2 className="h-5 w-5 text-yellow-500" />
                    </div>
                    <div>
                      <h4 className="font-medium">Bugün LeetCode çözdün mü?</h4>
                      <p className="text-sm text-muted-foreground">Günlük 1 soru çözmek, mülakatlarda fark yaratır!</p>
                    </div>
                  </div>
                  <a 
                    href="https://leetcode.com/problemset/?difficulty=EASY&page=1" 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="flex items-center justify-center gap-2 w-full py-2.5 rounded-lg bg-yellow-500 text-black font-medium hover:bg-yellow-400 transition-colors"
                  >
                    <ExternalLink className="h-4 w-4" />
                    LeetCode'a Git
                  </a>
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <a href="https://www.hackerrank.com/domains/tutorials/10-days-of-javascript" target="_blank" rel="noopener noreferrer" 
                     className="p-2 rounded-lg bg-muted/50 hover:bg-muted text-xs text-center transition-colors">
                    🎯 HackerRank
                  </a>
                  <a href="https://www.codewars.com" target="_blank" rel="noopener noreferrer" 
                     className="p-2 rounded-lg bg-muted/50 hover:bg-muted text-xs text-center transition-colors">
                    ⚔️ CodeWars
                  </a>
                </div>
              </div>
            )}
            
            {/* Slide 1: Kariyer İpuçları */}
            {carouselIndex === 1 && (
              <div className="space-y-3">
                {(() => {
                  const tips = [
                    { tip: "CV'nizi her iş başvurusu için özelleştirin. İlana uygun anahtar kelimeleri ekleyin.", category: "CV Hazırlama", icon: "📄" },
                    { tip: "Profesyonel ağ profilinizi düzenli güncelleyin. Recruiters aktif profilleri önceliklendirir.", category: "Networking", icon: "🔗" },
                    { tip: "Mülakat öncesi şirket hakkında araştırma yapın ve 2-3 soru hazırlayın.", category: "Mülakat", icon: "💬" },
                    { tip: "GitHub ve portfolio projelerinizi güncel tutun. Teknik roller için önemlidir.", category: "Portfolio", icon: "💻" },
                    { tip: "Başvuru yaptığınız pozisyondaki kişileri profesyonel ağlardan bulup bağlantı isteği gönderin.", category: "Networking", icon: "🤝" },
                    { tip: "STAR metoduyla mülakat sorularına hazırlanın: Situation, Task, Action, Result.", category: "Mülakat", icon: "⭐" },
                    { tip: "Soft skill'lerinizi (iletişim, takım çalışması) örneklerle anlatmaya hazır olun.", category: "Soft Skills", icon: "🗣️" },
                  ];
                  const dayIndex = new Date().getDate();
                  return tips.slice(0, 3).map((_, i) => (
                    <div key={i} className="p-3 rounded-xl bg-muted/30 border border-border/50">
                      <div className="flex items-start gap-2">
                        <span className="text-lg">{tips[(dayIndex + i) % tips.length].icon}</span>
                        <div>
                          <span className="text-xs px-2 py-0.5 rounded-full bg-blue-500/10 text-blue-500 font-medium">
                            {tips[(dayIndex + i) % tips.length].category}
                          </span>
                          <p className="text-sm mt-1 leading-relaxed">{tips[(dayIndex + i) % tips.length].tip}</p>
                        </div>
                      </div>
                    </div>
                  ));
                })()}
              </div>
            )}
            
            {/* Slide 2: Başvuru İstatistikleri */}
            {carouselIndex === 2 && (
              <div className="space-y-4">
                {(() => {
                  const last7Days = Array.from({ length: 7 }, (_, i) => {
                    const date = new Date();
                    date.setDate(date.getDate() - (6 - i));
                    return date.toISOString().split('T')[0];
                  });
                  const weeklyData = last7Days.map(date => applicationStats[date] || 0);
                  const totalApplications = weeklyData.reduce((a, b) => a + b, 0);
                  const maxValue = Math.max(...weeklyData, 1);
                  
                  return (
                    <>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm text-muted-foreground">Son 7 gün</span>
                        <span className="text-lg font-bold text-green-500">{totalApplications} başvuru</span>
                      </div>
                      <div className="flex items-end justify-between gap-2 h-24 p-4 rounded-xl bg-muted/30">
                        {weeklyData.map((count, i) => (
                          <div key={i} className="flex-1 flex flex-col items-center gap-1">
                            <div 
                              className="w-full bg-green-500/80 rounded-t-sm transition-all duration-500"
                              style={{ height: `${(count / maxValue) * 100}%`, minHeight: count > 0 ? '8px' : '4px' }}
                            />
                            <span className="text-[10px] text-muted-foreground">
                              {['Pz', 'Pt', 'Sa', 'Ça', 'Pe', 'Cu', 'Ct'][new Date(last7Days[i]).getDay()]}
                            </span>
                          </div>
                        ))}
                      </div>
                      <p className="text-xs text-muted-foreground text-center">
                        💡 İş ilanlarından başvuru yaptıklarınızı işaretleyin!
                      </p>
                    </>
                  );
                })()}
              </div>
            )}
            
            {/* Slide 3: Kişisel Gelişim Kaynakları */}
            {carouselIndex === 3 && (
              <div className="space-y-3">
                <p className="text-sm text-muted-foreground mb-2">Kariyer gelişiminiz için önerilen kaynaklar:</p>
                <a href="https://www.coursera.org/browse/computer-science" target="_blank" rel="noopener noreferrer"
                   className="flex items-center gap-3 p-3 rounded-xl bg-muted/30 hover:bg-muted transition-colors group">
                  <span className="text-xl">🎓</span>
                  <div className="flex-1">
                    <p className="font-medium text-sm group-hover:text-primary">Coursera - Computer Science</p>
                    <p className="text-xs text-muted-foreground">Dünya üniversitelerinden ücretsiz dersler</p>
                  </div>
                  <ExternalLink className="h-4 w-4 text-muted-foreground" />
                </a>
                <a href="https://roadmap.sh" target="_blank" rel="noopener noreferrer"
                   className="flex items-center gap-3 p-3 rounded-xl bg-muted/30 hover:bg-muted transition-colors group">
                  <span className="text-xl">🗺️</span>
                  <div className="flex-1">
                    <p className="font-medium text-sm group-hover:text-primary">Roadmap.sh</p>
                    <p className="text-xs text-muted-foreground">Developer kariyer yol haritaları</p>
                  </div>
                  <ExternalLink className="h-4 w-4 text-muted-foreground" />
                </a>
                <a href="https://www.freecodecamp.org" target="_blank" rel="noopener noreferrer"
                   className="flex items-center gap-3 p-3 rounded-xl bg-muted/30 hover:bg-muted transition-colors group">
                  <span className="text-xl">💻</span>
                  <div className="flex-1">
                    <p className="font-medium text-sm group-hover:text-primary">freeCodeCamp</p>
                    <p className="text-xs text-muted-foreground">Ücretsiz web development eğitimleri</p>
                  </div>
                  <ExternalLink className="h-4 w-4 text-muted-foreground" />
                </a>
              </div>
            )}
          </div>
        </div>
        
        {/* Sağ Taraf - Son İş Aramaları (Bağımsız Carousel) */}
        <JobSearchCarousel lastJobSearch={lastJobSearch} />
      </div>

      {/* Suggested Actions */}
      {data.suggested_actions.length > 0 && (
        <div className="bg-card border border-border rounded-xl p-6">
          <h3 className="font-semibold text-lg mb-4">📌 Önerilen Adımlar</h3>
          <ul className="space-y-3">
            {data.suggested_actions.map((action, index) => (
              <li key={index} className="flex items-center gap-3 text-muted-foreground">
                <span className="flex-shrink-0 w-6 h-6 rounded-full bg-primary/10 text-primary text-xs flex items-center justify-center font-medium">
                  {index + 1}
                </span>
                {action}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Career Goals Summary */}
      {data.has_career_goals && (
        <div className="bg-card border border-border rounded-xl p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-lg">🎯 Kariyer Hedefin</h3>
            <Link to="/profile" className="text-sm text-primary hover:underline">
              Düzenle
            </Link>
          </div>
          <div className="flex flex-wrap gap-3">
            {data.career_goals.target_sector_name && (
              <span className="px-3 py-1.5 rounded-full bg-blue-500/10 text-blue-500 text-sm">
                {data.career_goals.target_sector_name}
              </span>
            )}
            {data.career_goals.target_position_name && (
              <span className="px-3 py-1.5 rounded-full bg-purple-500/10 text-purple-500 text-sm">
                {data.career_goals.target_position_name}
              </span>
            )}
            {data.career_goals.experience_level_name && (
              <span className="px-3 py-1.5 rounded-full bg-green-500/10 text-green-500 text-sm">
                {data.career_goals.experience_level_name}
              </span>
            )}
          </div>
        </div>
      )}

      {/* Hızlı İstatistikler - Quick Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-card border border-border rounded-xl p-4 text-center">
          <div className="text-2xl font-bold text-primary">{data.analysis.total_analyses || 0}</div>
          <div className="text-xs text-muted-foreground mt-1">CV Analizi</div>
        </div>
        <div className="bg-card border border-border rounded-xl p-4 text-center">
          <div className="text-2xl font-bold text-green-500">{data.interview.total_interviews || 0}</div>
          <div className="text-xs text-muted-foreground mt-1">Mülakat</div>
        </div>
        <div className="bg-card border border-border rounded-xl p-4 text-center">
          <div className="text-2xl font-bold text-purple-500">{data.analysis.strongest_score || '-'}</div>
          <div className="text-xs text-muted-foreground mt-1">En Yüksek Skor</div>
        </div>
        <div className="bg-card border border-border rounded-xl p-4 text-center">
          <div className="text-2xl font-bold text-orange-500">{data.cv.skills_count || 0}</div>
          <div className="text-xs text-muted-foreground mt-1">Yetenek</div>
        </div>
      </div>

      {/* Analysis Selection Modal */}
      {showAnalysisModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
          <div className="bg-card border border-border rounded-2xl p-6 w-full max-w-md mx-4 shadow-xl">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-lg">
                {modalType === 'view' ? '📊 Analiz Sonucunu Görüntüle' : '💡 Tavsiye Al'}
              </h3>
              <button 
                onClick={() => setShowAnalysisModal(false)}
                className="p-1 rounded-lg hover:bg-muted transition-colors"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
            
            {loadingAnalyses ? (
              <div className="flex items-center justify-center py-8">
                <Loader2 className="h-6 w-6 animate-spin text-primary" />
              </div>
            ) : analyses.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                <p>Henüz analiz yapılmamış.</p>
                <Link 
                  to="/cv/analysis" 
                  className="text-primary hover:underline mt-2 inline-block"
                  onClick={() => setShowAnalysisModal(false)}
                >
                  İlk analizini yap →
                </Link>
              </div>
            ) : (
              <div className="space-y-3">
                <p className="text-sm text-muted-foreground mb-4">
                  {modalType === 'view' 
                    ? 'Görüntülemek istediğin analizi seç:' 
                    : 'Tavsiye almak istediğin analizi seç:'}
                </p>
                {analyses.map((analysis) => (
                  <div
                    key={analysis.id}
                    className="relative group"
                  >
                    {/* Silme butonu */}
                    <button 
                      onClick={(e) => openDeleteModal(e, analysis.id)}
                      className="absolute -top-2 -right-2 p-1.5 bg-red-500 text-white rounded-full shadow-lg opacity-0 group-hover:opacity-100 transition-all hover:bg-red-600 z-20 hover:scale-105"
                      title="Analizi Sil"
                    >
                      <Trash2 className="h-3 w-3" />
                    </button>
                    
                    <button
                      onClick={() => handleSelectAnalysis(analysis.id)}
                      className="w-full p-4 rounded-xl border border-border bg-muted/30 hover:bg-muted/60 hover:border-primary/50 transition-all text-left"
                    >
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex flex-wrap gap-1">
                          {analysis.field_names.map((name, i) => (
                            <span key={i} className="px-2 py-0.5 rounded-full bg-primary/10 text-primary text-xs">
                              {name}
                            </span>
                          ))}
                        </div>
                        <span className="text-sm font-medium text-primary">
                          {analysis.overall_score}/100
                        </span>
                      </div>
                      <p className="text-xs text-muted-foreground">
                        {formatDate(analysis.created_at)}
                      </p>
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Analysis Delete Confirmation Modal */}
      {deleteModalOpen && (
        <div className="fixed inset-0 z-[60] flex items-center justify-center">
          {/* Backdrop with blur */}
          <div 
            className="absolute inset-0 bg-black/60 backdrop-blur-md"
            onClick={() => {
              setDeleteModalOpen(false);
              setDeleteTargetId(null);
            }}
          />
          
          {/* Modal Content */}
          <div className="relative bg-card border border-border rounded-2xl p-6 w-full max-w-md mx-4 shadow-2xl animate-in fade-in zoom-in-95 duration-200">
            {/* Icon */}
            <div className="w-12 h-12 rounded-full bg-red-500/10 flex items-center justify-center mx-auto mb-4">
              <AlertTriangle className="h-6 w-6 text-red-500" />
            </div>
            
            {/* Title */}
            <h3 className="text-lg font-semibold text-center mb-2">
              Analizi Sil
            </h3>
            
            {/* Message */}
            <p className="text-muted-foreground text-center text-sm mb-6">
              Bu analiz kaydını silmek istediğinize emin misiniz? Bu işlem geri alınamaz.
            </p>
            
            {/* Buttons */}
            <div className="flex gap-3">
              <button
                onClick={() => {
                  setDeleteModalOpen(false);
                  setDeleteTargetId(null);
                }}
                className="flex-1 py-2.5 px-4 rounded-lg border border-border hover:bg-muted transition-colors font-medium"
              >
                İptal
              </button>
              <button
                onClick={handleDeleteAnalysis}
                disabled={deletingAnalysis}
                className="flex-1 py-2.5 px-4 rounded-lg bg-red-500 text-white hover:bg-red-600 transition-colors font-medium disabled:opacity-50"
              >
                {deletingAnalysis ? 'Siliniyor...' : 'Sil'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

import { Link, useLocation, useNavigate } from 'react-router-dom';
import { 
  LayoutDashboard, 
  FileText, 
  BarChart3, 
  MessageSquare, 
  User,
  LogOut,
  Moon,
  Sun,
  Menu,
  X,
  ChevronDown,
  Lightbulb,
  Eye,
  TrendingUp,
  Loader2,
  Briefcase,
  XCircle,
  AlertCircle,
  AlertTriangle,
  Trash2
} from 'lucide-react';
import { useState, useEffect, useRef } from 'react';
import { useAuthStore } from '../../stores/authStore';
import { useThemeStore } from '../../stores/themeStore';
import { cn } from '../../lib/utils';
import api from '../../lib/api';

interface AnalysisListItem {
  id: string;
  created_at: string;
  fields: string[];
  field_names: string[];
  experience_level: string;
  overall_score: number;
}

const navItems = [
  { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/cv/upload', label: 'CV Yükle', icon: FileText, hasCVUploadDropdown: true },
  { path: '/cv/analysis', label: 'CV Analiz', icon: BarChart3, hasDropdown: true },
  { path: '/jobs', label: 'İş Ara', icon: Briefcase },
  { path: '/cover-letter', label: 'Önyazı', icon: FileText },
  { path: '/interview/start', label: 'Mülakat', icon: MessageSquare, isInterview: true, hasInterviewDropdown: true },
  { path: '/profile', label: 'Profil', icon: User },
];

export function Header() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [cvDropdownOpen, setCvDropdownOpen] = useState(false);
  const [cvUploadDropdownOpen, setCvUploadDropdownOpen] = useState(false);
  const [interviewDropdownOpen, setInterviewDropdownOpen] = useState(false);
  const [analysisModalOpen, setAnalysisModalOpen] = useState(false);
  const [modalType, setModalType] = useState<'view' | 'recommend'>('recommend');
  const [analyses, setAnalyses] = useState<AnalysisListItem[]>([]);
  const [loadingAnalyses, setLoadingAnalyses] = useState(false);
  
  // Dropdown refs for click outside detection
  const headerRef = useRef<HTMLDivElement>(null);
  
  // Dropdown dışına tıklamayı yakala
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (headerRef.current && !headerRef.current.contains(event.target as Node)) {
        setCvDropdownOpen(false);
        setCvUploadDropdownOpen(false);
        setInterviewDropdownOpen(false);
      }
    };
    
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);
  
  // Mülakat iptal modal state'leri
  const [interviewCancelModalOpen, setInterviewCancelModalOpen] = useState(false);
  const [cancellingInterview, setCancellingInterview] = useState(false);
  
  // Analiz silme modal state'leri
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [deleteTargetId, setDeleteTargetId] = useState<string | null>(null);
  const [deletingAnalysis, setDeletingAnalysis] = useState(false);
  
  // Mülakat sırasında navigasyon koruması
  const [leaveInterviewModalOpen, setLeaveInterviewModalOpen] = useState(false);
  const [pendingNavigationPath, setPendingNavigationPath] = useState<string | null>(null);
  
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();
  const { theme, toggleTheme } = useThemeStore();

  // Aktif mülakat kontrolü - KULLANICI ID'sini de kontrol et
  const hasActiveInterview = () => {
    const stored = localStorage.getItem('interview_session');
    if (stored) {
      try {
        const session = JSON.parse(stored);
        // Session'ın mevcut kullanıcıya ait olduğunu kontrol et
        if (user && session.user_id && session.user_id !== user.id) {
          // Başka kullanıcının session'ı, temizle
          localStorage.removeItem('interview_session');
          return false;
        }
        return true;
      } catch {
        // Invalid JSON, temizle
        localStorage.removeItem('interview_session');
        return false;
      }
    }
    return false;
  };

  // Navigasyon kontrolü - mülakat sayfasındayken başka yere gitmek istenirse
  const handleNavClick = (e: React.MouseEvent, path: string) => {
    // Mülakat sayfasındaysak ve aktif mülakat varsa uyar
    if (location.pathname.startsWith('/interview') && hasActiveInterview() && !path.startsWith('/interview')) {
      e.preventDefault();
      setPendingNavigationPath(path);
      setLeaveInterviewModalOpen(true);
      return;
    }
    // Normal navigasyon
    navigate(path);
  };

  // Mülakatı bırak ve yönlendir
  const handleLeaveInterview = async () => {
    try {
      setCancellingInterview(true);
      await api.delete('/interview/cancel');
    } catch (err) {
      // 404 hatası = zaten aktif mülakat yok, sorun değil
      console.log('Mülakat zaten yok veya iptal edilemedi:', err);
    } finally {
      // Her durumda localStorage'ı temizle ve modal'ı kapat
      localStorage.removeItem('interview_session');
      setCancellingInterview(false);
      setLeaveInterviewModalOpen(false);
      if (pendingNavigationPath) {
        navigate(pendingNavigationPath);
        setPendingNavigationPath(null);
      }
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  // Modal açma fonksiyonu (hem Analizi Gör hem Tavsiye Al için)
  const handleOpenModal = async (type: 'view' | 'recommend') => {
    setModalType(type);
    setCvDropdownOpen(false);
    setLoadingAnalyses(true);
    setAnalysisModalOpen(true);
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
    setAnalysisModalOpen(false);
    if (modalType === 'recommend') {
      navigate(`/recommendations?analysis_id=${analysisId}`);
    } else {
      navigate(`/cv/analysis/result?analysis_id=${analysisId}`);
    }
  };

  // Mülakat linkine tıklama kontrolü
  const handleInterviewClick = async (e?: React.MouseEvent) => {
    e?.preventDefault();
    
    // localStorage'dan aktif oturum kontrolü
    const stored = localStorage.getItem('interview_session');
    if (stored) {
      try {
        const session = JSON.parse(stored);
        // Oturumun mevcut kullanıcıya ait olduğunu kontrol et
        if (user && session.user_id && session.user_id !== user.id) {
          // Başka kullanıcının session'ı, temizle ve devam et
          localStorage.removeItem('interview_session');
        } else {
          // Aktif oturum var ve mevcut kullanıcıya ait, modal göster
          setInterviewCancelModalOpen(true);
          return;
        }
      } catch {
        // Invalid session, temizle
        localStorage.removeItem('interview_session');
      }
    }
    
    // Aktif oturum yok, direkt sayfaya git
    navigate('/interview/start');
  };

  // Mülakat iptal fonksiyonu
  const handleCancelInterview = async () => {
    try {
      setCancellingInterview(true);
      await api.delete('/interview/cancel');
    } catch (err) {
      // 404 hatası = zaten aktif mülakat yok, sorun değil
      console.log('Mülakat zaten yok veya iptal edilemedi:', err);
    } finally {
      // Her durumda localStorage'ı temizle ve modal'ı kapat
      localStorage.removeItem('interview_session');
      setCancellingInterview(false);
      setInterviewCancelModalOpen(false);
      navigate('/interview/start');
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

  return (
    <>
    <header ref={headerRef} className="sticky top-0 z-50 w-full border-b border-border bg-[var(--color-header)] shadow-sm transition-all duration-300">
      <div className="container mx-auto flex h-16 items-center justify-between px-4">
        {/* Logo */}
        <Link to="/dashboard" className="flex items-center gap-2">
          <img src="/logoenyeni.png" alt="KariyerKoçu" className="h-9 w-auto object-contain" />
          <span className="font-bold text-xl hidden sm:inline">
            <span className="text-[#1e3a5f]">Kariyer</span><span className="gradient-text">Koçu</span>
          </span>
        </Link>

        {/* Desktop Navigation */}
        <nav className="hidden md:flex items-center gap-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname.startsWith(item.path);
            
            // CV Yükle için dropdown menü
            if ('hasCVUploadDropdown' in item && item.hasCVUploadDropdown) {
              return (
                <div key={item.path} className="relative">
                  <button
                    onClick={() => setCvUploadDropdownOpen(!cvUploadDropdownOpen)}
                    className={cn(
                      'flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 hover:scale-105',
                      isActive
                        ? 'bg-primary/10 text-primary'
                        : 'text-muted-foreground hover:text-foreground hover:bg-muted'
                    )}
                  >
                    <Icon className="h-4 w-4" />
                    {item.label}
                    <ChevronDown className={cn("h-3 w-3 transition-transform duration-300", cvUploadDropdownOpen && "rotate-180")} />
                  </button>
                  
                  {cvUploadDropdownOpen && (
                    <div className="absolute top-full left-0 mt-2 w-48 bg-card/95 backdrop-blur-xl border border-border rounded-xl shadow-2xl py-2 z-50 animate-in fade-in zoom-in-95 duration-200">
                      <Link
                        to="/cv/upload"
                        onClick={() => setCvUploadDropdownOpen(false)}
                        className="flex items-center gap-3 px-4 py-2.5 text-sm hover:bg-primary/5 transition-colors group"
                      >
                        <FileText className="h-4 w-4 text-muted-foreground group-hover:text-blue-500 transition-colors" />
                        <span className="group-hover:text-blue-500 transition-colors">CV Yükle</span>
                      </Link>
                      <Link
                        to="/cv/upload?ats=true"
                        onClick={() => setCvUploadDropdownOpen(false)}
                        className="flex items-center gap-3 px-4 py-2.5 text-sm hover:bg-primary/5 transition-colors group"
                      >
                        <Briefcase className="h-4 w-4 text-muted-foreground group-hover:text-orange-500 transition-colors" />
                        <span className="group-hover:text-orange-500 transition-colors">ATS Testi</span>
                      </Link>
                    </div>
                  )}
                </div>
              );
            }
            
            // CV Analiz için dropdown menü
            if (item.hasDropdown) {
              return (
                <div key={item.path} className="relative">
                  <button
                    onClick={() => setCvDropdownOpen(!cvDropdownOpen)}
                    className={cn(
                      'flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 hover:scale-105',
                      isActive
                        ? 'bg-primary/10 text-primary'
                        : 'text-muted-foreground hover:text-foreground hover:bg-muted'
                    )}
                  >
                    <Icon className="h-4 w-4" />
                    {item.label}
                    <ChevronDown className={cn("h-3 w-3 transition-transform duration-300", cvDropdownOpen && "rotate-180")} />
                  </button>
                  
                  {cvDropdownOpen && (
                    <div className="absolute top-full left-0 mt-2 w-56 bg-card/95 backdrop-blur-xl border border-border rounded-xl shadow-2xl py-2 z-50 animate-in fade-in zoom-in-95 duration-200">
                      <button
                        onClick={() => handleOpenModal('view')}
                        className="flex items-center gap-3 px-4 py-2.5 text-sm hover:bg-primary/5 transition-colors w-full text-left group"
                      >
                        <Eye className="h-4 w-4 text-muted-foreground group-hover:text-primary transition-colors" />
                        <span className="group-hover:text-primary transition-colors">Analizi Gör</span>
                      </button>
                      <button
                        onClick={() => handleOpenModal('recommend')}
                        className="flex items-center gap-3 px-4 py-2.5 text-sm hover:bg-primary/5 transition-colors w-full text-left group"
                      >
                        <Lightbulb className="h-4 w-4 text-muted-foreground group-hover:text-yellow-500 transition-colors" />
                        <span className="group-hover:text-yellow-500 transition-colors">Tavsiye Al</span>
                      </button>
                      <Link
                        to="/cv/analysis"
                        onClick={() => setCvDropdownOpen(false)}
                        className="flex items-center gap-3 px-4 py-2.5 text-sm hover:bg-primary/5 transition-colors group"
                      >
                        <TrendingUp className="h-4 w-4 text-muted-foreground group-hover:text-blue-500 transition-colors" />
                        <span className="group-hover:text-blue-500 transition-colors">Yeni Analiz</span>
                      </Link>
                    </div>
                  )}
                </div>
              );
            }
            // Mülakat linki için özel kontrol - dropdown ile
            if ('isInterview' in item && item.isInterview && 'hasInterviewDropdown' in item && item.hasInterviewDropdown) {
              return (
                <div key={item.path} className="relative">
                  <button
                    onClick={() => setInterviewDropdownOpen(!interviewDropdownOpen)}
                    className={cn(
                      'flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 hover:scale-105',
                      isActive
                        ? 'bg-primary/10 text-primary'
                        : 'text-muted-foreground hover:text-foreground hover:bg-muted'
                    )}
                  >
                    <Icon className="h-4 w-4" />
                    {item.label}
                    <ChevronDown className={cn("h-3 w-3 transition-transform duration-300", interviewDropdownOpen && "rotate-180")} />
                  </button>
                  
                  {interviewDropdownOpen && (
                    <div className="absolute top-full left-0 mt-2 w-56 bg-card/95 backdrop-blur-xl border border-border rounded-xl shadow-2xl py-2 z-50 animate-in fade-in zoom-in-95 duration-200">
                      <button
                        onClick={() => {
                          setInterviewDropdownOpen(false);
                          handleInterviewClick();
                        }}
                        className="flex items-center gap-3 px-4 py-2.5 text-sm hover:bg-primary/5 transition-colors w-full text-left group"
                      >
                        <MessageSquare className="h-4 w-4 text-muted-foreground group-hover:text-green-500 transition-colors" />
                        <span className="group-hover:text-green-500 transition-colors">Mülakat Başlat</span>
                      </button>
                      <Link
                        to="/interview/history"
                        onClick={() => setInterviewDropdownOpen(false)}
                        className="flex items-center gap-3 px-4 py-2.5 text-sm hover:bg-primary/5 transition-colors group"
                      >
                        <Eye className="h-4 w-4 text-muted-foreground group-hover:text-blue-500 transition-colors" />
                        <span className="group-hover:text-blue-500 transition-colors">Değerlendirmeler</span>
                      </Link>
                    </div>
                  )}
                </div>
              );
            }
            // Normal mülakat linki için eski kontrol (fallback)
            if ('isInterview' in item && item.isInterview) {
              return (
                <button
                  key={item.path}
                  onClick={handleInterviewClick}
                  className={cn(
                    'flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors',
                    isActive
                      ? 'bg-primary/10 text-primary'
                      : 'text-muted-foreground hover:text-foreground hover:bg-muted'
                  )}
                >
                  <Icon className="h-4 w-4" />
                  {item.label}
                </button>
              );
            }
            
            return (
              <button
                key={item.path}
                onClick={(e) => handleNavClick(e, item.path)}
                className={cn(
                  'flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 hover:scale-105',
                  isActive
                    ? 'bg-primary/10 text-primary shadow-[0_0_15px_rgba(99,102,241,0.15)]'
                    : 'text-muted-foreground hover:text-foreground hover:bg-muted'
                )}
              >
                <Icon className="h-4 w-4" />
                {item.label}
              </button>
            );
          })}
        </nav>

        {/* Right Side */}
        <div className="flex items-center gap-2">
          {/* Theme Toggle */}
          <button
            onClick={toggleTheme}
            className="p-2 rounded-lg hover:bg-muted transition-all duration-200 hover:scale-110"
            aria-label="Tema değiştir"
          >
            {theme === 'dark' ? (
              <Sun className="h-5 w-5 text-muted-foreground" />
            ) : (
              <Moon className="h-5 w-5 text-muted-foreground" />
            )}
          </button>

          {/* User Menu */}
          <div className="hidden sm:flex items-center gap-2">
            <span className="text-sm text-muted-foreground">
              {user?.full_name || user?.email}
            </span>
            <button
              onClick={handleLogout}
              className="p-2 rounded-lg hover:bg-muted transition-colors text-muted-foreground hover:text-destructive"
              aria-label="Çıkış yap"
            >
              <LogOut className="h-5 w-5" />
            </button>
          </div>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="md:hidden p-2 rounded-lg hover:bg-muted transition-colors"
            aria-label="Menü"
          >
            {mobileMenuOpen ? (
              <X className="h-5 w-5" />
            ) : (
              <Menu className="h-5 w-5" />
            )}
          </button>
        </div>
      </div>

      {/* Mobile Navigation */}
      {mobileMenuOpen && (
        <div className="md:hidden border-t border-border bg-background">
          <nav className="container mx-auto px-4 py-4 flex flex-col gap-2">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname.startsWith(item.path);
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  onClick={() => setMobileMenuOpen(false)}
                  className={cn(
                    'flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-colors',
                    isActive
                      ? 'bg-primary/10 text-primary'
                      : 'text-muted-foreground hover:text-foreground hover:bg-muted'
                  )}
                >
                  <Icon className="h-5 w-5" />
                  {item.label}
                </Link>
              );
            })}
            <hr className="border-border my-2" />
            <button
              onClick={handleLogout}
              className="flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium text-destructive hover:bg-destructive/10 transition-colors w-full text-left"
            >
              <LogOut className="h-5 w-5" />
              Çıkış Yap
            </button>
          </nav>
        </div>
      )}
    </header>

    {/* Analysis Selection Modal - Header dışında, ekranın ortasında */}
    {analysisModalOpen && (
      <div className="fixed inset-0 z-[100] flex items-center justify-center">
        {/* Backdrop with strong blur */}
        <div 
          className="absolute inset-0 bg-black/60 backdrop-blur-md"
          onClick={() => setAnalysisModalOpen(false)}
        />
        
        {/* Modal Content */}
        <div className="relative bg-card border border-border rounded-2xl p-6 w-full max-w-md mx-4 shadow-2xl animate-in fade-in zoom-in-95 duration-200">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-lg">
              {modalType === 'view' ? '📊 Analiz Sonucunu Görüntüle' : '💡 Tavsiye Al'}
            </h3>
            <button 
              onClick={() => setAnalysisModalOpen(false)}
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
                onClick={() => setAnalysisModalOpen(false)}
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
                    className="w-full p-4 rounded-xl border border-border bg-muted/30 hover:bg-muted/60 hover:border-primary/50 transition-all text-left card-hover"
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
                      {new Date(analysis.created_at).toLocaleDateString('tr-TR')}
                    </p>
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    )}

    {/* Interview Cancel Modal */}
    {interviewCancelModalOpen && (
      <div className="fixed inset-0 z-[100] flex items-center justify-center">
        {/* Backdrop with blur */}
        <div 
          className="absolute inset-0 bg-black/60 backdrop-blur-md"
          onClick={() => setInterviewCancelModalOpen(false)}
        />
        
        {/* Modal Content */}
        <div className="relative bg-card border border-border rounded-2xl p-6 w-full max-w-md mx-4 shadow-2xl animate-in fade-in zoom-in-95 duration-200">
          <div className="flex items-start gap-3 mb-4">
            <AlertCircle className="h-6 w-6 text-yellow-500 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="font-semibold text-lg">Devam Eden Mülakat Var</h3>
              <p className="text-sm text-muted-foreground mt-1">
                Başladığınız bir mülakat var. Yeni bir mülakat başlatmak için önce mevcut mülakatı iptal etmelisiniz.
              </p>
            </div>
          </div>
          
          <div className="flex gap-3">
            <button
              onClick={() => setInterviewCancelModalOpen(false)}
              className="flex-1 py-3 rounded-lg border border-border text-muted-foreground font-medium hover:bg-muted transition-colors"
            >
              Vazgeç
            </button>
            <button
              onClick={handleCancelInterview}
              disabled={cancellingInterview}
              className="flex-1 py-3 rounded-lg bg-red-500/10 border border-red-500/50 text-red-500 font-medium flex items-center justify-center gap-2 hover:bg-red-500/20 transition-colors disabled:opacity-50"
            >
              <XCircle className="h-5 w-5" />
              {cancellingInterview ? 'İptal Ediliyor...' : 'İptal Et'}
            </button>
          </div>
        </div>
      </div>
    )}

    {/* Analysis Delete Confirmation Modal */}
    {deleteModalOpen && (
      <div className="fixed inset-0 z-[110] flex items-center justify-center">
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

    {/* Leave Interview Confirmation Modal */}
    {leaveInterviewModalOpen && (
      <div className="fixed inset-0 z-[110] flex items-center justify-center">
        {/* Backdrop with blur */}
        <div 
          className="absolute inset-0 bg-black/60 backdrop-blur-md"
          onClick={() => {
            setLeaveInterviewModalOpen(false);
            setPendingNavigationPath(null);
          }}
        />
        
        {/* Modal Content */}
        <div className="relative bg-card border border-border rounded-2xl p-6 w-full max-w-md mx-4 shadow-2xl animate-in fade-in zoom-in-95 duration-200">
          {/* Icon */}
          <div className="w-12 h-12 rounded-full bg-yellow-500/10 flex items-center justify-center mx-auto mb-4">
            <AlertCircle className="h-6 w-6 text-yellow-500" />
          </div>
          
          {/* Title */}
          <h3 className="text-lg font-semibold text-center mb-2">
            Mülakatı Yarıda Bırak?
          </h3>
          
          {/* Message */}
          <p className="text-muted-foreground text-center text-sm mb-6">
            Çıkarsanız mülakat ilerlemeniz kaybedilecek ve kayıt silinecektir. Devam etmek istediğinize emin misiniz?
          </p>
          
          {/* Buttons */}
          <div className="flex gap-3">
            <button
              onClick={() => {
                setLeaveInterviewModalOpen(false);
                setPendingNavigationPath(null);
              }}
              className="flex-1 py-2.5 px-4 rounded-lg border border-border hover:bg-muted transition-colors font-medium"
            >
              Mülakata Dön
            </button>
            <button
              onClick={handleLeaveInterview}
              disabled={cancellingInterview}
              className="flex-1 py-2.5 px-4 rounded-lg bg-red-500 text-white hover:bg-red-600 transition-colors font-medium disabled:opacity-50"
            >
              {cancellingInterview ? 'İptal Ediliyor...' : 'Çık ve Sil'}
            </button>
          </div>
        </div>
      </div>
    )}
    </>
  );
}

import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { 
  User as UserIcon, 
  Mail, 
  Calendar, 
  Target, 
  FileText, 
  BarChart3, 
  MessageSquare,
  Lock,
  Edit3,
  Save,
  X,
  Loader2,
  Upload,
  Eye,
  CheckCircle,
  Phone,
  ChevronLeft,
  ChevronRight
} from 'lucide-react';
import api from '../../lib/api';
import { formatDate } from '../../lib/utils';
import type { CareerGoals, SelectOption } from '../../types';
import { useAuthStore } from '../../stores/authStore';

interface ProfileData {
  id: string;
  email: string;
  full_name: string | null;
  phone: string | null;
  created_at: string;
  has_cv: boolean;
  cv_filename: string | null;
  cv_uploaded_at: string | null;
  career_goals: CareerGoals;
}

interface ProfileStats {
  total_analyses: number;
  total_interviews: number;
  highest_score: number | null;
}

interface InterviewConfig {
  sectors: SelectOption[];
  positions: Record<string, SelectOption[]>;
  experience_levels: SelectOption[];
}

// CV detayları için interface
interface CVDetails {
  has_cv: boolean;
  filename?: string;
  personal?: {
    full_name?: string;
    title?: string;
    email?: string;
    phone?: string;
    location?: string;
    linkedin?: string;
    github?: string;
  };
  summary?: string;
  skills?: string[];
  experience?: Array<{
    title?: string;
    company?: string;
    start_date?: string;
    end_date?: string;
    duration?: string;
  }>;
  education?: Array<{
    degree?: string;
    field?: string;
    school?: string;
    start_year?: number;
    end_year?: number;
  }>;
  projects?: Array<{
    name?: string;
    technologies?: string[];
    description?: string;
  }>;
  languages?: Record<string, string>;
  stats?: {
    skills_count: number;
    experience_count: number;
    education_count: number;
    projects_count: number;
  };
}

export function ProfilePage() {
  const [profile, setProfile] = useState<ProfileData | null>(null);
  const [stats, setStats] = useState<ProfileStats>({ total_analyses: 0, total_interviews: 0, highest_score: null });
  const [config, setConfig] = useState<InterviewConfig | null>(null);
  const [cvDetails, setCvDetails] = useState<CVDetails | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Edit states
  const [editingName, setEditingName] = useState(false);
  const [editingCareer, setEditingCareer] = useState(false);
  const [editingCV, setEditingCV] = useState(false);
  const [newName, setNewName] = useState('');
  const [newPhone, setNewPhone] = useState('');
  const [savingName, setSavingName] = useState(false);
  const [savingCareer, setSavingCareer] = useState(false);
  const [savingCV, setSavingCV] = useState(false);
  
  // CV edit state
  const [editCVData, setEditCVData] = useState({
    summary: '',
    skills: '',
  });
  
  // Career goals edit state
  const [selectedSector, setSelectedSector] = useState<string>('');
  const [selectedPosition, setSelectedPosition] = useState<string>('');
  const [selectedExperience, setSelectedExperience] = useState<string>('');
  
  // Password modal
  const [passwordModalOpen, setPasswordModalOpen] = useState(false);
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [passwordError, setPasswordError] = useState<string | null>(null);
  const [passwordSuccess, setPasswordSuccess] = useState(false);
  const [savingPassword, setSavingPassword] = useState(false);
  
  // Projeler pagination
  const [projectPage, setProjectPage] = useState(0);
  const projectsPerPage = 3;

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [profileRes, dashboardRes, configRes, cvDetailsRes] = await Promise.all([
        api.get<ProfileData>('/user/profile'),
        api.get('/user/dashboard'),
        api.get<InterviewConfig>('/interview/config'),
        api.get<CVDetails>('/user/cv-details')
      ]);
      
      setProfile(profileRes.data);
      setStats({
        total_analyses: dashboardRes.data.analysis?.total_analyses || 0,
        total_interviews: dashboardRes.data.interview?.total_interviews || 0,
        highest_score: dashboardRes.data.analysis?.strongest_score || null
      });
      setConfig(configRes.data);
      setCvDetails(cvDetailsRes.data);
      
      // Initialize edit values
      setNewName(profileRes.data.full_name || '');
      setNewPhone(profileRes.data.phone || '');
      setSelectedSector(profileRes.data.career_goals.target_sector || '');
      setSelectedPosition(profileRes.data.career_goals.target_position || '');
      setSelectedExperience(profileRes.data.career_goals.experience_level || '');
    } catch (err) {
      setError('Profil yüklenemedi');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSaveName = async () => {
    const { updateUser } = useAuthStore.getState();
    try {
      setSavingName(true);
      await api.put('/user/profile', { full_name: newName, phone: newPhone });
      setProfile(prev => prev ? { ...prev, full_name: newName, phone: newPhone } : null);
      // AuthStore'u da güncelle - Header'daki isim değişsin
      updateUser({ full_name: newName });
      setEditingName(false);
    } catch (err) {
      console.error('Bilgiler güncellenemedi:', err);
    } finally {
      setSavingName(false);
    }
  };

  const handleSaveCareerGoals = async () => {
    try {
      setSavingCareer(true);
      await api.put('/user/profile/career-goals', {
        target_sector: selectedSector || null,
        target_position: selectedPosition || null,
        experience_level: selectedExperience || null
      });
      
      // Refresh profile to get updated names
      const profileRes = await api.get<ProfileData>('/user/profile');
      setProfile(profileRes.data);
      setEditingCareer(false);
    } catch (err) {
      console.error('Kariyer hedefi güncellenemedi:', err);
    } finally {
      setSavingCareer(false);
    }
  };

  const handleStartEditCV = () => {
    if (cvDetails) {
      setEditCVData({
        summary: cvDetails.summary || '',
        skills: cvDetails.skills?.join(', ') || '',
      });
      setEditingCV(true);
    }
  };

  const handleSaveCV = async () => {
    try {
      setSavingCV(true);
      const skillsArray = editCVData.skills
        .split(',')
        .map(s => s.trim())
        .filter(s => s.length > 0);
      
      await api.put('/cv/update-info', {
        summary: editCVData.summary,
        skills: skillsArray,
      });
      
      // CV details'i yenile
      const cvDetailsRes = await api.get<CVDetails>('/user/cv-details');
      setCvDetails(cvDetailsRes.data);
      setEditingCV(false);
    } catch (err) {
      console.error('CV bilgileri güncellenemedi:', err);
    } finally {
      setSavingCV(false);
    }
  };

  const handleChangePassword = async () => {
    setPasswordError(null);
    
    if (newPassword.length < 6) {
      setPasswordError('Yeni şifre en az 6 karakter olmalı');
      return;
    }
    
    if (newPassword !== confirmPassword) {
      setPasswordError('Yeni şifreler eşleşmiyor');
      return;
    }
    
    try {
      setSavingPassword(true);
      await api.put('/user/profile/password', {
        current_password: currentPassword,
        new_password: newPassword
      });
      setPasswordSuccess(true);
      setTimeout(() => {
        setPasswordModalOpen(false);
        setPasswordSuccess(false);
        setCurrentPassword('');
        setNewPassword('');
        setConfirmPassword('');
      }, 2000);
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } };
      setPasswordError(error.response?.data?.detail || 'Şifre değiştirilemedi');
    } finally {
      setSavingPassword(false);
    }
  };

  const getPositionsForSector = () => {
    if (!config || !selectedSector) return [];
    return config.positions[selectedSector] || [];
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  if (error || !profile) {
    return (
      <div className="text-center py-12">
        <p className="text-destructive">{error || 'Profil bulunamadı'}</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold gradient-text">Profil</h1>
        <p className="text-muted-foreground mt-1">Hesap ayarlarını ve kariyer hedeflerini yönet</p>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {/* Kişisel Bilgiler Kartı */}
        <div className="bg-card border border-border rounded-2xl p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-semibold flex items-center gap-2">
              <UserIcon className="h-5 w-5 text-primary" />
              Kişisel Bilgiler
            </h2>
            {!editingName && (
              <button 
                onClick={() => setEditingName(true)}
                className="p-2 rounded-lg hover:bg-muted transition-colors"
              >
                <Edit3 className="h-4 w-4 text-muted-foreground" />
              </button>
            )}
          </div>
          
          <div className="space-y-4">
            {/* Ad Soyad */}
            <div>
              <label className="text-sm text-muted-foreground">Ad Soyad</label>
              {editingName ? (
                <div className="flex items-center gap-2 mt-1">
                  <input
                    type="text"
                    value={newName}
                    onChange={(e) => setNewName(e.target.value)}
                    className="flex-1 px-3 py-2 rounded-lg border border-border bg-background focus:outline-none focus:ring-2 focus:ring-primary/50"
                    placeholder="Ad Soyad"
                  />
                  <button 
                    onClick={handleSaveName}
                    disabled={savingName}
                    className="p-2 rounded-lg bg-primary text-white hover:bg-primary/90 transition-colors"
                  >
                    {savingName ? <Loader2 className="h-4 w-4 animate-spin" /> : <Save className="h-4 w-4" />}
                  </button>
                  <button 
                    onClick={() => {
                      setEditingName(false);
                      setNewName(profile.full_name || '');
                    }}
                    className="p-2 rounded-lg hover:bg-muted transition-colors"
                  >
                    <X className="h-4 w-4" />
                  </button>
                </div>
              ) : (
                <p className="font-medium mt-1">{profile.full_name || 'Belirtilmemiş'}</p>
              )}
            </div>
            
            {/* Telefon */}
            <div>
              <label className="text-sm text-muted-foreground">Telefon</label>
              {editingName ? (
                <div className="flex items-center gap-2 mt-1">
                  <Phone className="h-4 w-4 text-muted-foreground" />
                  <input
                    type="tel"
                    value={newPhone}
                    onChange={(e) => setNewPhone(e.target.value)}
                    className="flex-1 px-3 py-2 rounded-lg border border-border bg-background focus:outline-none focus:ring-2 focus:ring-primary/50"
                    placeholder="+90 5XX XXX XX XX"
                  />
                </div>
              ) : (
                <p className="font-medium flex items-center gap-2 mt-1">
                  <Phone className="h-4 w-4 text-muted-foreground" />
                  {profile.phone || 'Belirtilmemiş'}
                </p>
              )}
            </div>
            
            {/* Email */}
            <div className="flex items-center gap-3">
              <Mail className="h-4 w-4 text-muted-foreground" />
              <div>
                <label className="text-sm text-muted-foreground">Email</label>
                <p className="font-medium">{profile.email}</p>
              </div>
            </div>
            
            {/* Üyelik Tarihi */}
            <div className="flex items-center gap-3">
              <Calendar className="h-4 w-4 text-muted-foreground" />
              <div>
                <label className="text-sm text-muted-foreground">Üyelik Tarihi</label>
                <p className="font-medium">{formatDate(profile.created_at)}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Kariyer Hedefi Kartı */}
        <div className="bg-card border border-border rounded-2xl p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-semibold flex items-center gap-2">
              <Target className="h-5 w-5 text-primary" />
              Kariyer Hedefi
            </h2>
            {!editingCareer && (
              <button 
                onClick={() => setEditingCareer(true)}
                className="p-2 rounded-lg hover:bg-muted transition-colors"
              >
                <Edit3 className="h-4 w-4 text-muted-foreground" />
              </button>
            )}
          </div>
          
          {editingCareer && config ? (
            <div className="space-y-4">
              {/* Sektör */}
              <div>
                <label className="text-sm text-muted-foreground block mb-1">Sektör</label>
                <select
                  value={selectedSector}
                  onChange={(e) => {
                    setSelectedSector(e.target.value);
                    setSelectedPosition('');
                  }}
                  className="w-full px-3 py-2 rounded-lg border border-border bg-background focus:outline-none focus:ring-2 focus:ring-primary/50"
                >
                  <option value="">Seçiniz</option>
                  {config.sectors.map((s) => (
                    <option key={s.id} value={s.id}>{s.name}</option>
                  ))}
                </select>
              </div>
              
              {/* Pozisyon */}
              <div>
                <label className="text-sm text-muted-foreground block mb-1">Pozisyon</label>
                <select
                  value={selectedPosition}
                  onChange={(e) => setSelectedPosition(e.target.value)}
                  disabled={!selectedSector}
                  className="w-full px-3 py-2 rounded-lg border border-border bg-background focus:outline-none focus:ring-2 focus:ring-primary/50 disabled:opacity-50"
                >
                  <option value="">Seçiniz</option>
                  {getPositionsForSector().map((p) => (
                    <option key={p.id} value={p.id}>{p.name}</option>
                  ))}
                </select>
              </div>
              
              {/* Tecrübe Seviyesi */}
              <div>
                <label className="text-sm text-muted-foreground block mb-1">Tecrübe Seviyesi</label>
                <select
                  value={selectedExperience}
                  onChange={(e) => setSelectedExperience(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg border border-border bg-background focus:outline-none focus:ring-2 focus:ring-primary/50"
                >
                  <option value="">Seçiniz</option>
                  {config.experience_levels.map((e) => (
                    <option key={e.id} value={e.id}>{e.name}</option>
                  ))}
                </select>
              </div>
              
              <div className="flex gap-2">
                <button 
                  onClick={handleSaveCareerGoals}
                  disabled={savingCareer}
                  className="flex-1 py-2 rounded-lg bg-primary text-white hover:bg-primary/90 transition-colors flex items-center justify-center gap-2"
                >
                  {savingCareer ? <Loader2 className="h-4 w-4 animate-spin" /> : <Save className="h-4 w-4" />}
                  Kaydet
                </button>
                <button 
                  onClick={() => {
                    setEditingCareer(false);
                    setSelectedSector(profile.career_goals.target_sector || '');
                    setSelectedPosition(profile.career_goals.target_position || '');
                    setSelectedExperience(profile.career_goals.experience_level || '');
                  }}
                  className="px-4 py-2 rounded-lg border border-border hover:bg-muted transition-colors"
                >
                  İptal
                </button>
              </div>
            </div>
          ) : (
            <div className="space-y-3">
              <div>
                <label className="text-sm text-muted-foreground">Sektör</label>
                <p className="font-medium">{profile.career_goals.target_sector_name || 'Belirtilmemiş'}</p>
              </div>
              <div>
                <label className="text-sm text-muted-foreground">Pozisyon</label>
                <p className="font-medium">{profile.career_goals.target_position_name || 'Belirtilmemiş'}</p>
              </div>
              <div>
                <label className="text-sm text-muted-foreground">Tecrübe Seviyesi</label>
                <p className="font-medium">{profile.career_goals.experience_level_name || 'Belirtilmemiş'}</p>
              </div>
            </div>
          )}
        </div>

        {/* CV Durumu Kartı */}
        <div className="bg-card border border-border rounded-2xl p-6">
          <h2 className="font-semibold flex items-center gap-2 mb-4">
            <FileText className="h-5 w-5 text-primary" />
            CV Durumu
          </h2>
          
          {profile.has_cv ? (
            <div className="space-y-3">
              <div className="flex items-center gap-2 text-success">
                <CheckCircle className="h-5 w-5" />
                <span className="font-medium">CV yüklenmiş</span>
              </div>
              <div>
                <label className="text-sm text-muted-foreground">Dosya Adı</label>
                <p className="font-medium">{profile.cv_filename}</p>
              </div>
              <div>
                <label className="text-sm text-muted-foreground">Yükleme Tarihi</label>
                <p className="font-medium">{profile.cv_uploaded_at ? formatDate(profile.cv_uploaded_at) : '-'}</p>
              </div>
              <div className="flex gap-2 mt-4">
                <Link
                  to="/cv/analysis"
                  className="flex-1 py-2 rounded-lg border border-border hover:bg-muted transition-colors flex items-center justify-center gap-2 text-sm"
                >
                  <Eye className="h-4 w-4" />
                  Analiz Et
                </Link>
                <Link
                  to="/cv/upload"
                  className="flex-1 py-2 rounded-lg border border-border hover:bg-muted transition-colors flex items-center justify-center gap-2 text-sm"
                >
                  <Upload className="h-4 w-4" />
                  Yeni Yükle
                </Link>
              </div>
            </div>
          ) : (
            <div className="text-center py-4">
              <p className="text-muted-foreground mb-4">Henüz CV yüklenmemiş</p>
              <Link
                to="/cv/upload"
                className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-primary text-white hover:bg-primary/90 transition-colors"
              >
                <Upload className="h-4 w-4" />
                CV Yükle
              </Link>
            </div>
          )}
        </div>

        {/* İstatistikler Kartı */}
        <div className="bg-card border border-border rounded-2xl p-6">
          <h2 className="font-semibold flex items-center gap-2 mb-4">
            <BarChart3 className="h-5 w-5 text-primary" />
            İstatistikler
          </h2>
          
          <div className="grid grid-cols-3 gap-4">
            <div className="text-center p-3 rounded-xl bg-muted/50">
              <BarChart3 className="h-6 w-6 mx-auto text-primary mb-2" />
              <p className="text-2xl font-bold">{stats.total_analyses}</p>
              <p className="text-xs text-muted-foreground">Analiz</p>
            </div>
            <div className="text-center p-3 rounded-xl bg-muted/50">
              <MessageSquare className="h-6 w-6 mx-auto text-primary mb-2" />
              <p className="text-2xl font-bold">{stats.total_interviews}</p>
              <p className="text-xs text-muted-foreground">Mülakat</p>
            </div>
            <div className="text-center p-3 rounded-xl bg-muted/50">
              <Target className="h-6 w-6 mx-auto text-primary mb-2" />
              <p className="text-2xl font-bold">{stats.highest_score ?? '-'}</p>
              <p className="text-xs text-muted-foreground">En Yüksek</p>
            </div>
          </div>
        </div>
      </div>
      {/* CV Detayları - Yeni Bölüm */}
      {cvDetails?.has_cv && (
        <div className="bg-card border border-border rounded-2xl p-6 md:col-span-2">
          <div className="flex items-center justify-between mb-6">
            <h2 className="font-semibold flex items-center gap-2">
              <FileText className="h-5 w-5 text-primary" />
              CV Bilgileri
              <span className="text-xs text-muted-foreground ml-2">
                {cvDetails.filename}
              </span>
            </h2>
            <div className="flex gap-2">
              {editingCV ? (
                <>
                  <button
                    onClick={() => setEditingCV(false)}
                    className="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-border text-muted-foreground hover:bg-muted transition-colors text-sm font-medium"
                  >
                    <X className="h-4 w-4" />
                    İptal
                  </button>
                  <button
                    onClick={handleSaveCV}
                    disabled={savingCV}
                    className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-green-500/10 text-green-500 hover:bg-green-500/20 transition-colors text-sm font-medium disabled:opacity-50"
                  >
                    {savingCV ? <Loader2 className="h-4 w-4 animate-spin" /> : <Save className="h-4 w-4" />}
                    Kaydet
                  </button>
                </>
              ) : (
                <button
                  onClick={handleStartEditCV}
                  className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-primary/10 text-primary hover:bg-primary/20 transition-colors text-sm font-medium"
                >
                  <Edit3 className="h-4 w-4" />
                  Bilgileri Düzenle
                </button>
              )}
            </div>
          </div>
          
          {editingCV ? (
            /* Düzenleme Modu */
            <div className="space-y-6">
              {/* Hakkımda / Özet düzenleme */}
              <div>
                <label className="text-sm font-medium text-muted-foreground mb-2 block">
                  Hakkımda / Özet
                </label>
                <textarea
                  value={editCVData.summary}
                  onChange={(e) => setEditCVData(prev => ({ ...prev, summary: e.target.value }))}
                  className="w-full px-4 py-3 rounded-xl bg-muted/30 border border-border focus:outline-none focus:ring-2 focus:ring-primary/50 text-sm resize-none"
                  rows={4}
                  placeholder="Kendinizi kısaca tanıtın..."
                />
              </div>
              
              {/* Yetenekler düzenleme */}
              <div>
                <label className="text-sm font-medium text-muted-foreground mb-2 block">
                  Yetenekler (virgülle ayırın)
                </label>
                <textarea
                  value={editCVData.skills}
                  onChange={(e) => setEditCVData(prev => ({ ...prev, skills: e.target.value }))}
                  className="w-full px-4 py-3 rounded-xl bg-muted/30 border border-border focus:outline-none focus:ring-2 focus:ring-primary/50 text-sm resize-none"
                  rows={3}
                  placeholder="Python, JavaScript, React, Node.js..."
                />
                <p className="text-xs text-muted-foreground mt-1">
                  Örnek: Python, JavaScript, React, Node.js, SQL
                </p>
              </div>
              
              <div className="p-4 rounded-xl bg-blue-500/10 border border-blue-500/20">
                <p className="text-sm text-blue-500">
                  💡 <strong>İpucu:</strong> Burada yaptığınız değişiklikler CV analizlerinde ve mülakatlarınızda kullanılacaktır. 
                  Eğer CV yanlış okunduysa buradan düzeltebilirsiniz.
                </p>
              </div>
            </div>
          ) : (
            /* Görüntüleme Modu */
            <div className="grid gap-6 md:grid-cols-2">
              {/* Hakkımda / Özet */}
              {cvDetails.summary && (
                <div className="md:col-span-2">
                  <h3 className="text-sm font-medium text-muted-foreground mb-2">Hakkımda</h3>
                  <p className="text-sm bg-muted/30 rounded-xl p-4 leading-relaxed">
                    {cvDetails.summary}
                  </p>
              </div>
            )}
            
            {/* Yetenekler */}
            {cvDetails.skills && cvDetails.skills.length > 0 && (
              <div>
                <h3 className="text-sm font-medium text-muted-foreground mb-2">
                  Yetenekler ({cvDetails.skills.length})
                </h3>
                <div className="flex flex-wrap gap-2">
                  {cvDetails.skills.slice(0, 15).map((skill, i) => (
                    <span 
                      key={i}
                      className="px-3 py-1 rounded-full text-xs bg-primary/10 text-primary font-medium"
                    >
                      {skill}
                    </span>
                  ))}
                  {cvDetails.skills.length > 15 && (
                    <span className="px-3 py-1 rounded-full text-xs bg-muted text-muted-foreground">
                      +{cvDetails.skills.length - 15} daha
                    </span>
                  )}
                </div>
              </div>
            )}
            
            {/* Diller */}
            {cvDetails.languages && Object.keys(cvDetails.languages).length > 0 && (
              <div>
                <h3 className="text-sm font-medium text-muted-foreground mb-2">Diller</h3>
                <div className="flex flex-wrap gap-2">
                  {Object.entries(cvDetails.languages).map(([lang, level], i) => (
                    <span 
                      key={i}
                      className="px-3 py-1 rounded-full text-xs bg-blue-500/10 text-blue-500 font-medium"
                    >
                      {lang}: {level}
                    </span>
                  ))}
                </div>
              </div>
            )}
            
            {/* Deneyim */}
            {cvDetails.experience && cvDetails.experience.length > 0 && (
              <div className="md:col-span-2">
                <h3 className="text-sm font-medium text-muted-foreground mb-2">
                  Deneyim ({cvDetails.experience.length})
                </h3>
                <div className="space-y-3">
                  {cvDetails.experience.slice(0, 3).map((exp, i) => (
                    <div key={i} className="p-3 rounded-xl bg-muted/30 border border-border/50">
                      <div className="font-medium text-sm">{exp.title}</div>
                      <div className="text-sm text-muted-foreground">{exp.company}</div>
                      {exp.duration && (
                        <div className="text-xs text-muted-foreground mt-1">{exp.duration}</div>
                      )}
                    </div>
                  ))}
                  {cvDetails.experience.length > 3 && (
                    <p className="text-xs text-muted-foreground">
                      +{cvDetails.experience.length - 3} deneyim daha
                    </p>
                  )}
                </div>
              </div>
            )}
            
            {/* Eğitim */}
            {cvDetails.education && cvDetails.education.length > 0 && (
              <div>
                <h3 className="text-sm font-medium text-muted-foreground mb-2">
                  Eğitim ({cvDetails.education.length})
                </h3>
                <div className="space-y-3">
                  {cvDetails.education.map((edu, i) => (
                    <div key={i} className="p-3 rounded-xl bg-muted/30 border border-border/50">
                      <div className="font-medium text-sm">{edu.school}</div>
                      <div className="text-sm text-muted-foreground">{edu.field}</div>
                      {(edu.start_year || edu.end_year) && (
                        <div className="text-xs text-muted-foreground mt-1">
                          {edu.start_year} - {edu.end_year || 'Devam'}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            {/* Projeler */}
            {cvDetails.projects && cvDetails.projects.length > 0 && (
              <div>
                <div className="flex items-center justify-between mb-2">
                  <h3 className="text-sm font-medium text-muted-foreground">
                    Projeler ({cvDetails.projects.length})
                  </h3>
                  {cvDetails.projects.length > projectsPerPage && (
                    <div className="flex items-center gap-1">
                      <button
                        onClick={() => setProjectPage(p => Math.max(0, p - 1))}
                        disabled={projectPage === 0}
                        className="p-1 rounded hover:bg-muted transition-colors disabled:opacity-30"
                      >
                        <ChevronLeft className="h-4 w-4" />
                      </button>
                      <span className="text-xs text-muted-foreground">
                        {projectPage + 1}/{Math.ceil(cvDetails.projects.length / projectsPerPage)}
                      </span>
                      <button
                        onClick={() => setProjectPage(p => Math.min(Math.ceil(cvDetails.projects!.length / projectsPerPage) - 1, p + 1))}
                        disabled={projectPage >= Math.ceil(cvDetails.projects.length / projectsPerPage) - 1}
                        className="p-1 rounded hover:bg-muted transition-colors disabled:opacity-30"
                      >
                        <ChevronRight className="h-4 w-4" />
                      </button>
                    </div>
                  )}
                </div>
                <div className="space-y-3">
                  {cvDetails.projects.slice(projectPage * projectsPerPage, (projectPage + 1) * projectsPerPage).map((project, i) => (
                    <div key={i} className="p-3 rounded-xl bg-muted/30 border border-border/50 animate-in fade-in duration-300">
                      <div className="font-medium text-sm">{project.name}</div>
                      {project.technologies && project.technologies.length > 0 && (
                        <div className="flex flex-wrap gap-1 mt-1">
                          {project.technologies.slice(0, 5).map((tech, j) => (
                            <span key={j} className="text-xs px-2 py-0.5 rounded bg-primary/10 text-primary">
                              {tech}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
          )}
        </div>
      )}
      {/* Güvenlik Kartı */}
      <div className="bg-card border border-border rounded-2xl p-6">
        <h2 className="font-semibold flex items-center gap-2 mb-4">
          <Lock className="h-5 w-5 text-primary" />
          Güvenlik
        </h2>
        
        <button
          onClick={() => setPasswordModalOpen(true)}
          className="px-4 py-2 rounded-lg border border-border hover:bg-muted transition-colors flex items-center gap-2"
        >
          <Lock className="h-4 w-4" />
          Şifre Değiştir
        </button>
      </div>

      {/* Şifre Değiştir Modal */}
      {passwordModalOpen && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center">
          <div 
            className="absolute inset-0 bg-black/60 backdrop-blur-md"
            onClick={() => {
              setPasswordModalOpen(false);
              setPasswordError(null);
              setPasswordSuccess(false);
              setCurrentPassword('');
              setNewPassword('');
              setConfirmPassword('');
            }}
          />
          
          <div className="relative bg-card border border-border rounded-2xl p-6 w-full max-w-md mx-4 shadow-2xl animate-in fade-in zoom-in-95 duration-200">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-lg flex items-center gap-2">
                <Lock className="h-5 w-5 text-primary" />
                Şifre Değiştir
              </h3>
              <button 
                onClick={() => {
                  setPasswordModalOpen(false);
                  setPasswordError(null);
                  setPasswordSuccess(false);
                }}
                className="p-1 rounded-lg hover:bg-muted transition-colors"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
            
            {passwordSuccess ? (
              <div className="text-center py-8">
                <CheckCircle className="h-12 w-12 text-success mx-auto mb-4" />
                <p className="font-medium text-success">Şifre başarıyla değiştirildi!</p>
              </div>
            ) : (
              <div className="space-y-4">
                <div>
                  <label className="text-sm text-muted-foreground block mb-1">Mevcut Şifre</label>
                  <input
                    type="password"
                    value={currentPassword}
                    onChange={(e) => setCurrentPassword(e.target.value)}
                    className="w-full px-3 py-2 rounded-lg border border-border bg-background focus:outline-none focus:ring-2 focus:ring-primary/50"
                    placeholder="••••••••"
                  />
                </div>
                
                <div>
                  <label className="text-sm text-muted-foreground block mb-1">Yeni Şifre</label>
                  <input
                    type="password"
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    className="w-full px-3 py-2 rounded-lg border border-border bg-background focus:outline-none focus:ring-2 focus:ring-primary/50"
                    placeholder="En az 6 karakter"
                  />
                </div>
                
                <div>
                  <label className="text-sm text-muted-foreground block mb-1">Yeni Şifre (Tekrar)</label>
                  <input
                    type="password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    className="w-full px-3 py-2 rounded-lg border border-border bg-background focus:outline-none focus:ring-2 focus:ring-primary/50"
                    placeholder="Yeni şifreyi tekrar girin"
                  />
                </div>
                
                {passwordError && (
                  <p className="text-destructive text-sm">{passwordError}</p>
                )}
                
                <button
                  onClick={handleChangePassword}
                  disabled={savingPassword || !currentPassword || !newPassword || !confirmPassword}
                  className="w-full py-2 rounded-lg bg-primary text-white hover:bg-primary/90 transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
                >
                  {savingPassword ? <Loader2 className="h-4 w-4 animate-spin" /> : <Save className="h-4 w-4" />}
                  Şifreyi Değiştir
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

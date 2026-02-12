import { useState, useEffect, useCallback } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '../../stores/authStore';
import { Mail, Lock, User, ArrowRight, Loader2, Eye, EyeOff, AlertTriangle, Check, X } from 'lucide-react';

// Şifre gücü hesaplama
function calculatePasswordStrength(password: string): { score: number; label: string; color: string } {
  let score = 0;
  if (password.length >= 6) score += 1;
  if (password.length >= 8) score += 1;
  if (/[a-z]/.test(password)) score += 1;
  if (/[A-Z]/.test(password)) score += 1;
  if (/[0-9]/.test(password)) score += 1;
  if (/[^a-zA-Z0-9]/.test(password)) score += 1;

  if (score <= 2) return { score, label: 'Zayıf', color: 'bg-red-500' };
  if (score <= 4) return { score, label: 'Orta', color: 'bg-yellow-500' };
  return { score, label: 'Güçlü', color: 'bg-green-500' };
}

// Email format doğrulama - sadece küçük harf ve ASCII karakterler
function isValidEmail(email: string): boolean {
  // Temel format kontrolü
  const basicFormat = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  if (!basicFormat) return false;
  
  // Büyük harf kontrolü
  if (email !== email.toLowerCase()) return false;
  
  // Türkçe ve özel karakter kontrolü (sadece ASCII)
  if (!/^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$/.test(email)) return false;
  
  return true;
}

// Email hata mesajı belirle
function getEmailError(email: string): string | null {
  if (!email) return null;
  
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    return 'Geçerli bir email adresi girin';
  }
  
  if (email !== email.toLowerCase()) {
    return 'Email adresi küçük harfle yazılmalıdır';
  }
  
  if (/[çğıöşüÇĞİÖŞÜ]/.test(email)) {
    return 'Email adresinde Türkçe karakter kullanılamaz';
  }
  
  if (!/^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$/.test(email)) {
    return 'Email adresinde geçersiz karakter var';
  }
  
  return null;
}

export function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { login, isLoading, error, clearError } = useAuthStore();
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });
  const [showPassword, setShowPassword] = useState(false);
  const [capsLock, setCapsLock] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);

  // Kayıt başarılı mesajı
  useEffect(() => {
    if (location.state?.registered) {
      setShowSuccess(true);
      // State'i temizle
      window.history.replaceState({}, document.title);
      // 5 saniye sonra mesajı gizle
      setTimeout(() => setShowSuccess(false), 5000);
    }
  }, [location.state]);

  // Caps Lock algılama
  const handleKeyDown = useCallback((e: KeyboardEvent) => {
    setCapsLock(e.getModifierState('CapsLock'));
  }, []);

  const handleKeyUp = useCallback((e: KeyboardEvent) => {
    setCapsLock(e.getModifierState('CapsLock'));
  }, []);

  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown);
    window.addEventListener('keyup', handleKeyUp);
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      window.removeEventListener('keyup', handleKeyUp);
    };
  }, [handleKeyDown, handleKeyUp]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    clearError();
    
    try {
      await login(formData);
      navigate('/dashboard');
    } catch {
      // Error is handled in store
    }
  };

  const isFormValid = formData.email && formData.password && isValidEmail(formData.email);

  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-3 mb-4">
            <img src="/logoenyeni.png" alt="KariyerKoçu" className="h-12 w-auto object-contain" />
            <span className="font-bold text-3xl">
              <span className="text-[#1e3a5f]">Kariyer</span>
              <span className="gradient-text">Koçu</span>
            </span>
          </div>
          <p className="text-muted-foreground">Kariyer yolculuğuna devam et</p>
        </div>

        {/* Form Card */}
        <div className="bg-card border border-border rounded-2xl p-8 shadow-lg">
          <h2 className="text-2xl font-bold mb-6 text-center">Giriş Yap</h2>

          {/* Başarılı Kayıt Mesajı */}
          {showSuccess && (
            <div className="mb-4 p-3 rounded-lg bg-green-500/10 border border-green-500/30 text-green-500 text-sm flex items-center gap-2">
              <Check className="h-4 w-4 flex-shrink-0" />
              <span>Kayıt başarılı! Şimdi giriş yapabilirsiniz.</span>
            </div>
          )}

          {error && (
            <div className="mb-4 p-3 rounded-lg bg-destructive/10 border border-destructive/30 text-destructive text-sm flex items-center gap-2">
              <X className="h-4 w-4 flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Email */}
            <div>
              <label className="block text-sm font-medium mb-2">Email</label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  className={`w-full pl-10 pr-4 py-3 rounded-lg bg-background border focus:ring-2 focus:ring-primary/20 outline-none transition-all ${
                    formData.email && !isValidEmail(formData.email)
                      ? 'border-red-500 focus:border-red-500'
                      : 'border-input focus:border-primary'
                  }`}
                  placeholder="ornek@email.com"
                  required
                  autoComplete="email"
                />
              </div>
              {formData.email && getEmailError(formData.email) && (
                <p className="mt-1 text-xs text-red-500 flex items-center gap-1">
                  <AlertTriangle className="h-3 w-3" />
                  {getEmailError(formData.email)}
                </p>
              )}
            </div>

            {/* Password */}
            <div>
              <label className="block text-sm font-medium mb-2">Şifre</label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  className="w-full pl-10 pr-12 py-3 rounded-lg bg-background border border-input focus:border-primary focus:ring-2 focus:ring-primary/20 outline-none transition-all"
                  placeholder="••••••"
                  required
                  autoComplete="current-password"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                  tabIndex={-1}
                >
                  {showPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                </button>
              </div>
              
              {/* Caps Lock Uyarısı */}
              {capsLock && (
                <p className="mt-2 text-xs text-amber-500 flex items-center gap-1 animate-pulse">
                  <AlertTriangle className="h-3 w-3" />
                  Caps Lock açık!
                </p>
              )}
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isLoading || !isFormValid}
              className="w-full py-3 rounded-lg gradient-primary text-white font-medium flex items-center justify-center gap-2 hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? (
                <>
                  <Loader2 className="h-5 w-5 animate-spin" />
                  <span>Giriş yapılıyor...</span>
                </>
              ) : (
                <>
                  Giriş Yap
                  <ArrowRight className="h-5 w-5" />
                </>
              )}
            </button>
          </form>

          {/* Register Link */}
          <p className="mt-6 text-center text-sm text-muted-foreground">
            Hesabın yok mu?{' '}
            <Link to="/register" className="text-primary hover:underline font-medium">
              Kayıt Ol
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}

export function RegisterPage() {
  const navigate = useNavigate();
  const { register, isLoading, error, clearError } = useAuthStore();
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    full_name: '',
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [capsLock, setCapsLock] = useState(false);
  const [touched, setTouched] = useState({
    email: false,
    password: false,
    confirmPassword: false,
    full_name: false,
  });

  // Caps Lock algılama
  const handleKeyDown = useCallback((e: KeyboardEvent) => {
    setCapsLock(e.getModifierState('CapsLock'));
  }, []);

  const handleKeyUp = useCallback((e: KeyboardEvent) => {
    setCapsLock(e.getModifierState('CapsLock'));
  }, []);

  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown);
    window.addEventListener('keyup', handleKeyUp);
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      window.removeEventListener('keyup', handleKeyUp);
    };
  }, [handleKeyDown, handleKeyUp]);

  const passwordStrength = calculatePasswordStrength(formData.password);
  const passwordsMatch = formData.password === formData.confirmPassword;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    clearError();
    
    if (!passwordsMatch) {
      return;
    }
    
    try {
      await register({
        email: formData.email,
        password: formData.password,
        full_name: formData.full_name,
      });
      navigate('/login', { state: { registered: true } });
    } catch {
      // Error is handled in store
    }
  };

  const isFormValid = 
    formData.full_name.length >= 2 &&
    isValidEmail(formData.email) &&
    formData.password.length >= 6 &&
    passwordsMatch;

  // Şifre gereksinimleri
  const passwordRequirements = [
    { met: formData.password.length >= 6, text: 'En az 6 karakter' },
    { met: /[a-z]/.test(formData.password), text: 'Küçük harf (a-z)' },
    { met: /[A-Z]/.test(formData.password), text: 'Büyük harf (A-Z)' },
    { met: /[0-9]/.test(formData.password), text: 'Rakam (0-9)' },
  ];

  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-3 mb-4">
            <img src="/logoenyeni.png" alt="KariyerKoçu" className="h-12 w-auto object-contain" />
            <span className="font-bold text-3xl">
              <span className="text-[#1e3a5f]">Kariyer</span>
              <span className="gradient-text">Koçu</span>
            </span>
          </div>
          <p className="text-muted-foreground">Kariyer yolculuğuna başla</p>
        </div>

        {/* Form Card */}
        <div className="bg-card border border-border rounded-2xl p-8 shadow-lg">
          <h2 className="text-2xl font-bold mb-6 text-center">Kayıt Ol</h2>

          {error && (
            <div className="mb-4 p-3 rounded-lg bg-destructive/10 border border-destructive/30 text-destructive text-sm flex items-center gap-2">
              <X className="h-4 w-4 flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Name */}
            <div>
              <label className="block text-sm font-medium mb-2">Ad Soyad</label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
                <input
                  type="text"
                  value={formData.full_name}
                  onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                  onBlur={() => setTouched({ ...touched, full_name: true })}
                  className={`w-full pl-10 pr-4 py-3 rounded-lg bg-background border focus:ring-2 focus:ring-primary/20 outline-none transition-all ${
                    touched.full_name && formData.full_name.length < 2
                      ? 'border-red-500 focus:border-red-500'
                      : 'border-input focus:border-primary'
                  }`}
                  placeholder="Ahmet Yılmaz"
                  required
                  autoComplete="name"
                />
              </div>
              {touched.full_name && formData.full_name.length < 2 && (
                <p className="mt-1 text-xs text-red-500 flex items-center gap-1">
                  <AlertTriangle className="h-3 w-3" />
                  İsim en az 2 karakter olmalı
                </p>
              )}
            </div>

            {/* Email */}
            <div>
              <label className="block text-sm font-medium mb-2">Email</label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  onBlur={() => setTouched({ ...touched, email: true })}
                  className={`w-full pl-10 pr-4 py-3 rounded-lg bg-background border focus:ring-2 focus:ring-primary/20 outline-none transition-all ${
                    touched.email && !isValidEmail(formData.email)
                      ? 'border-red-500 focus:border-red-500'
                      : 'border-input focus:border-primary'
                  }`}
                  placeholder="ornek@email.com"
                  required
                  autoComplete="email"
                />
              </div>
              {touched.email && formData.email && getEmailError(formData.email) && (
                <p className="mt-1 text-xs text-red-500 flex items-center gap-1">
                  <AlertTriangle className="h-3 w-3" />
                  {getEmailError(formData.email)}
                </p>
              )}
            </div>

            {/* Password */}
            <div>
              <label className="block text-sm font-medium mb-2">Şifre</label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  onBlur={() => setTouched({ ...touched, password: true })}
                  className="w-full pl-10 pr-12 py-3 rounded-lg bg-background border border-input focus:border-primary focus:ring-2 focus:ring-primary/20 outline-none transition-all"
                  placeholder="En az 6 karakter"
                  minLength={6}
                  required
                  autoComplete="new-password"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                  tabIndex={-1}
                >
                  {showPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                </button>
              </div>
              
              {/* Caps Lock Uyarısı */}
              {capsLock && (
                <p className="mt-2 text-xs text-amber-500 flex items-center gap-1 animate-pulse">
                  <AlertTriangle className="h-3 w-3" />
                  Caps Lock açık!
                </p>
              )}
              
              {/* Şifre Gücü Göstergesi */}
              {formData.password && (
                <div className="mt-2 space-y-2">
                  <div className="flex items-center gap-2">
                    <div className="flex-1 h-1.5 bg-muted rounded-full overflow-hidden">
                      <div 
                        className={`h-full ${passwordStrength.color} transition-all`}
                        style={{ width: `${(passwordStrength.score / 6) * 100}%` }}
                      />
                    </div>
                    <span className={`text-xs font-medium ${
                      passwordStrength.score <= 2 ? 'text-red-500' : 
                      passwordStrength.score <= 4 ? 'text-yellow-500' : 'text-green-500'
                    }`}>
                      {passwordStrength.label}
                    </span>
                  </div>
                  
                  {/* Şifre Gereksinimleri */}
                  <div className="grid grid-cols-2 gap-1">
                    {passwordRequirements.map((req, i) => (
                      <div key={i} className="flex items-center gap-1 text-xs">
                        {req.met ? (
                          <Check className="h-3 w-3 text-green-500" />
                        ) : (
                          <X className="h-3 w-3 text-muted-foreground" />
                        )}
                        <span className={req.met ? 'text-green-500' : 'text-muted-foreground'}>
                          {req.text}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Confirm Password */}
            <div>
              <label className="block text-sm font-medium mb-2">Şifre Tekrar</label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
                <input
                  type={showConfirmPassword ? 'text' : 'password'}
                  value={formData.confirmPassword}
                  onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
                  onBlur={() => setTouched({ ...touched, confirmPassword: true })}
                  className={`w-full pl-10 pr-12 py-3 rounded-lg bg-background border focus:ring-2 focus:ring-primary/20 outline-none transition-all ${
                    touched.confirmPassword && formData.confirmPassword && !passwordsMatch
                      ? 'border-red-500 focus:border-red-500'
                      : 'border-input focus:border-primary'
                  }`}
                  placeholder="Şifreyi tekrar girin"
                  required
                  autoComplete="new-password"
                />
                <button
                  type="button"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                  tabIndex={-1}
                >
                  {showConfirmPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                </button>
              </div>
              {touched.confirmPassword && formData.confirmPassword && !passwordsMatch && (
                <p className="mt-1 text-xs text-red-500 flex items-center gap-1">
                  <AlertTriangle className="h-3 w-3" />
                  Şifreler eşleşmiyor
                </p>
              )}
              {touched.confirmPassword && formData.confirmPassword && passwordsMatch && (
                <p className="mt-1 text-xs text-green-500 flex items-center gap-1">
                  <Check className="h-3 w-3" />
                  Şifreler eşleşiyor
                </p>
              )}
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isLoading || !isFormValid}
              className="w-full py-3 rounded-lg gradient-primary text-white font-medium flex items-center justify-center gap-2 hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? (
                <>
                  <Loader2 className="h-5 w-5 animate-spin" />
                  <span>Kayıt yapılıyor...</span>
                </>
              ) : (
                <>
                  Kayıt Ol
                  <ArrowRight className="h-5 w-5" />
                </>
              )}
            </button>
          </form>

          {/* Login Link */}
          <p className="mt-6 text-center text-sm text-muted-foreground">
            Zaten hesabın var mı?{' '}
            <Link to="/login" className="text-primary hover:underline font-medium">
              Giriş Yap
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}

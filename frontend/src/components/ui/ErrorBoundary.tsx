import { Component, type ErrorInfo, type ReactNode } from 'react';
import { AlertTriangle, RefreshCw, Home } from 'lucide-react';
import { Link } from 'react-router-dom';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

/**
 * Global Error Boundary
 * React component hatalarını yakalar ve kullanıcı dostu bir hata sayfası gösterir.
 */
export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null
    };
  }

  static getDerivedStateFromError(error: Error): Partial<State> {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    this.setState({ errorInfo });
    
    // Hata logla (production'da bir error tracking servisine gönder)
    console.error('Error Boundary yakaladı:', error);
    console.error('Component stack:', errorInfo.componentStack);
    
    // TODO: Sentry, LogRocket veya başka bir error tracking servisine gönder
    // logErrorToService(error, errorInfo);
  }

  handleRetry = (): void => {
    this.setState({ hasError: false, error: null, errorInfo: null });
  };

  render(): ReactNode {
    if (this.state.hasError) {
      // Custom fallback varsa onu göster
      if (this.props.fallback) {
        return this.props.fallback;
      }

      // Varsayılan hata sayfası
      return (
        <div className="min-h-screen flex items-center justify-center bg-background p-4">
          <div className="max-w-md w-full text-center">
            {/* Hata İkonu */}
            <div className="w-20 h-20 rounded-full bg-red-500/10 flex items-center justify-center mx-auto mb-6">
              <AlertTriangle className="h-10 w-10 text-red-500" />
            </div>
            
            {/* Başlık */}
            <h1 className="text-2xl font-bold mb-2">Bir Şeyler Ters Gitti</h1>
            
            {/* Açıklama */}
            <p className="text-muted-foreground mb-6">
              Beklenmeyen bir hata oluştu. Lütfen sayfayı yenileyin veya ana sayfaya dönün.
            </p>
            
            {/* Hata detayı (development'da) */}
            {import.meta.env.DEV && this.state.error && (
              <div className="mb-6 p-4 rounded-lg bg-red-500/10 border border-red-500/20 text-left">
                <p className="text-sm font-mono text-red-500 break-all">
                  {this.state.error.message}
                </p>
                {this.state.errorInfo && (
                  <pre className="mt-2 text-xs text-muted-foreground overflow-auto max-h-32">
                    {this.state.errorInfo.componentStack}
                  </pre>
                )}
              </div>
            )}
            
            {/* Butonlar */}
            <div className="flex flex-col sm:flex-row gap-3 justify-center">
              <button
                onClick={this.handleRetry}
                className="flex items-center justify-center gap-2 px-6 py-3 rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 transition-colors font-medium"
              >
                <RefreshCw className="h-4 w-4" />
                Tekrar Dene
              </button>
              
              <Link
                to="/dashboard"
                className="flex items-center justify-center gap-2 px-6 py-3 rounded-lg border border-border hover:bg-muted transition-colors font-medium"
              >
                <Home className="h-4 w-4" />
                Ana Sayfa
              </Link>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

/**
 * Sayfa seviyesi hata gösterimi
 */
interface PageErrorProps {
  title?: string;
  message?: string;
  onRetry?: () => void;
  showHomeButton?: boolean;
}

export function PageError({
  title = "Bir hata oluştu",
  message = "Sayfa yüklenirken bir sorun oluştu.",
  onRetry,
  showHomeButton = true
}: PageErrorProps) {
  return (
    <div className="flex flex-col items-center justify-center py-16 px-4">
      <div className="w-16 h-16 rounded-full bg-red-500/10 flex items-center justify-center mb-4">
        <AlertTriangle className="h-8 w-8 text-red-500" />
      </div>
      
      <h2 className="text-xl font-semibold mb-2">{title}</h2>
      <p className="text-muted-foreground text-center max-w-md mb-6">{message}</p>
      
      <div className="flex gap-3">
        {onRetry && (
          <button
            onClick={onRetry}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 transition-colors"
          >
            <RefreshCw className="h-4 w-4" />
            Tekrar Dene
          </button>
        )}
        
        {showHomeButton && (
          <Link
            to="/dashboard"
            className="flex items-center gap-2 px-4 py-2 rounded-lg border border-border hover:bg-muted transition-colors"
          >
            <Home className="h-4 w-4" />
            Ana Sayfa
          </Link>
        )}
      </div>
    </div>
  );
}

/**
 * API hata mesajı gösterimi
 */
interface ApiErrorProps {
  error: string | null;
  onDismiss?: () => void;
}

export function ApiError({ error, onDismiss }: ApiErrorProps) {
  if (!error) return null;
  
  return (
    <div className="p-4 rounded-lg bg-red-500/10 border border-red-500/20 flex items-start gap-3">
      <AlertTriangle className="h-5 w-5 text-red-500 flex-shrink-0 mt-0.5" />
      <div className="flex-1">
        <p className="text-sm text-red-500">{error}</p>
      </div>
      {onDismiss && (
        <button
          onClick={onDismiss}
          className="text-red-500 hover:text-red-600"
        >
          ×
        </button>
      )}
    </div>
  );
}

export default ErrorBoundary;

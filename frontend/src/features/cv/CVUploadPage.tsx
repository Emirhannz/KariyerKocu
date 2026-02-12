import { useCallback, useState, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { 
  Upload, 
  FileText, 
  CheckCircle, 
  XCircle, 
  Loader2,
  Trash2,
  Bot,
  RefreshCw
} from 'lucide-react';
import api from '../../lib/api';
import { ATSSimulationSection } from './ATSSimulationSection';

interface CVData {
  full_name: string | null;
  email: string | null;
  skills: string[];
  projects: { name: string }[];
}

export function CVUploadPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const [cvData, setCvData] = useState<CVData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [existingCV, setExistingCV] = useState<{ id: string; original_filename: string } | null>(null);
  const [loadingExisting, setLoadingExisting] = useState(true);
  const [showATSSection, setShowATSSection] = useState(searchParams.get('ats') === 'true');

  // Mevcut CV'yi kontrol et
  useEffect(() => {
    const checkExistingCV = async () => {
      try {
        const response = await api.get('/cv/my-cv');
        if (response.data) {
          setExistingCV({
            id: response.data.id,
            original_filename: response.data.original_filename
          });
        }
      } catch {
        // CV yok, normal
      } finally {
        setLoadingExisting(false);
      }
    };
    checkExistingCV();
  }, []);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const pdfFile = acceptedFiles[0];
    if (pdfFile && pdfFile.type === 'application/pdf') {
      setFile(pdfFile);
      setError(null);
      setUploadSuccess(false);
      setCvData(null);
    } else {
      setError('Sadece PDF dosyası yükleyebilirsiniz');
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'application/pdf': ['.pdf'] },
    maxFiles: 1,
    maxSize: 10 * 1024 * 1024, // 10MB
  });

  const handleUpload = async () => {
    if (!file) return;

    setUploading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await api.post('/cv/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 120000, // 2 dakika - LLM işlemi uzun sürebilir
      });
      
      setUploadSuccess(true);
      setCvData(response.data);
      // Mevcut CV'yi güncelle
      setExistingCV({
        id: response.data.id,
        original_filename: file.name
      });
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } }; code?: string };
      if (error.code === 'ECONNABORTED') {
        setError('İşlem zaman aşımına uğradı. CV büyük olabilir, lütfen tekrar deneyin.');
      } else {
        setError(error.response?.data?.detail || 'Yükleme başarısız');
      }
    } finally {
      setUploading(false);
    }
  };

  const handleRemove = () => {
    setFile(null);
    setUploadSuccess(false);
    setCvData(null);
    setError(null);
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      {/* Header - ATS modu değilse göster */}
      {!showATSSection && (
        <div>
          <h1 className="text-3xl font-bold">CV Yükle</h1>
          <p className="text-muted-foreground mt-2">
            PDF formatında CV'ni yükle, yapay zeka analiz etsin
          </p>
        </div>
      )}

      {/* Upload Area - ATS modu değilse göster */}
      {!showATSSection && (
        <div
          {...getRootProps()}
          className={`
            border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-all
          ${isDragActive 
            ? 'border-primary bg-primary/5' 
            : 'border-border hover:border-primary/50 hover:bg-muted/50'
          }
          ${uploadSuccess ? 'border-success bg-success/5' : ''}
          ${error ? 'border-destructive bg-destructive/5' : ''}
        `}
      >
        <input {...getInputProps()} />
        
        {!file ? (
          <div className="space-y-4">
            <div className="mx-auto w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center">
              <Upload className="h-8 w-8 text-primary" />
            </div>
            <div>
              <p className="font-medium">
                {isDragActive ? 'Dosyayı buraya bırak' : 'CV dosyasını sürükle veya tıkla'}
              </p>
              <p className="text-sm text-muted-foreground mt-1">
                Sadece PDF, maksimum 10MB
              </p>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="mx-auto w-16 h-16 rounded-full bg-blue-500/10 flex items-center justify-center">
              <FileText className="h-8 w-8 text-blue-500" />
            </div>
            <div>
              <p className="font-medium">{file.name}</p>
              <p className="text-sm text-muted-foreground">
                {(file.size / 1024 / 1024).toFixed(2)} MB
              </p>
            </div>
          </div>
        )}
      </div>
      )}

      {/* Error Message - ATS modu değilse göster */}
      {!showATSSection && error && (
        <div className="flex items-center gap-2 p-4 rounded-lg bg-destructive/10 text-destructive">
          <XCircle className="h-5 w-5 flex-shrink-0" />
          <p className="text-sm">{error}</p>
        </div>
      )}

      {/* Success Message - ATS modu değilse göster */}
      {!showATSSection && uploadSuccess && cvData && (
        <div className="p-6 rounded-xl bg-success/10 border border-success/30 space-y-4">
          <div className="flex flex-col items-center justify-center gap-2 text-success py-4">
            <CheckCircle className="h-8 w-8" />
            <span className="font-medium text-lg">CV başarıyla yüklendi!</span>
          </div>
        </div>
      )}

      {/* Action Buttons - ATS modu değilse göster */}
      {!showATSSection && (
        <div className="flex gap-3">
        {file && !uploadSuccess && (
          <>
            <button
              onClick={handleRemove}
              className="flex-1 py-3 rounded-lg border border-border text-muted-foreground hover:bg-muted transition-colors flex items-center justify-center gap-2"
            >
              <Trash2 className="h-4 w-4" />
              Kaldır
            </button>
            <button
              onClick={handleUpload}
              disabled={uploading}
              className="flex-1 py-3 rounded-lg gradient-primary text-white font-medium flex items-center justify-center gap-2 hover:opacity-90 disabled:opacity-50 transition-opacity"
            >
              {uploading ? (
                <Loader2 className="h-5 w-5 animate-spin" />
              ) : (
                <>
                  <Upload className="h-5 w-5" />
                  Yükle
                </>
              )}
            </button>
          </>
        )}
        
        {uploadSuccess && (
          <button
            onClick={() => navigate('/cv/analysis')}
            className="w-full py-3 rounded-lg gradient-primary text-white font-medium flex items-center justify-center gap-2 hover:opacity-90 transition-opacity"
          >
            CV'yi Analiz Et
            <span>→</span>
          </button>
        )}
        </div>
      )}

      {/* Mevcut CV varsa - Güncelle ve ATS butonları - ATS modu değilse göster */}
      {!showATSSection && !loadingExisting && existingCV && !file && !uploadSuccess && (
        <div className="mt-6 p-6 rounded-xl bg-card border border-border">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 rounded-full bg-blue-500/10 flex items-center justify-center">
              <FileText className="h-5 w-5 text-blue-500" />
            </div>
            <div>
              <p className="font-medium">Mevcut CV</p>
              <p className="text-sm text-muted-foreground">{existingCV.original_filename}</p>
            </div>
          </div>
          
          <div className="flex gap-3">
            <button
              onClick={() => (document.querySelector('input[type="file"]') as HTMLInputElement)?.click()}
              className="flex-1 py-3 rounded-lg border border-primary text-primary hover:bg-primary/5 transition-colors flex items-center justify-center gap-2"
            >
              <RefreshCw className="h-4 w-4" />
              CV Güncelle
            </button>
            <button
              onClick={() => setShowATSSection(!showATSSection)}
              className="flex-1 py-3 rounded-lg bg-orange-500/10 border border-orange-500/30 text-orange-500 hover:bg-orange-500/20 transition-colors flex items-center justify-center gap-2"
            >
              <Bot className="h-4 w-4" />
              ATS Simülasyonu
            </button>
          </div>
        </div>
      )}

      {/* ATS Simülasyonu Section - URL'de ats=true varsa veya butonla açıldıysa göster */}
      {showATSSection && (
        <div className="mt-6">
          <ATSSimulationSection />
        </div>
      )}
    </div>
  );
}

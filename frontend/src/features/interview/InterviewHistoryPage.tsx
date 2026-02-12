import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { 
  Loader2, 
  MessageSquare, 
  Trophy,
  CheckCircle,
  Calendar,
  ArrowRight,
  TrendingDown,
  X,
  AlertTriangle
} from 'lucide-react';
import api from '../../lib/api';
import type { InterviewHistoryResponse } from '../../types';
import { formatDate } from '../../lib/utils';

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
            İptal
          </button>
          <button
            onClick={() => {
              onConfirm();
              onClose();
            }}
            className="flex-1 py-2.5 px-4 rounded-lg bg-red-500 text-white hover:bg-red-600 transition-colors font-medium"
          >
            Sil
          </button>
        </div>
      </div>
    </div>
  );
}

export function InterviewHistoryPage() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<InterviewHistoryResponse | null>(null);
  
  // Delete confirmation modal state
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [deleteTargetId, setDeleteTargetId] = useState<string | null>(null);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const response = await api.get<InterviewHistoryResponse>('/interview/history');
        setData(response.data);
      } catch (err) {
        setError('Mülakat geçmişi yüklenemedi');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchHistory();
  }, []);

  const openDeleteModal = (sessionId: string) => {
    setDeleteTargetId(sessionId);
    setDeleteModalOpen(true);
  };

  const handleDelete = async () => {
    if (!deleteTargetId) return;

    try {
      await api.delete(`/interview/history/${deleteTargetId}`);
      setData(prev => prev ? {
        ...prev,
        total_count: prev.total_count - 1,
        interviews: prev.interviews.filter(i => i.session_id !== deleteTargetId)
      } : null);
    } catch (err) {
      console.error('Silme hatası:', err);
    } finally {
      setDeleteTargetId(null);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Delete Confirmation Modal */}
      <ConfirmModal
        isOpen={deleteModalOpen}
        onClose={() => setDeleteModalOpen(false)}
        onConfirm={handleDelete}
        title="Mülakatı Sil"
        message="Bu mülakat kaydını silmek istediğinize emin misiniz? Bu işlem geri alınamaz."
      />

      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Mülakat Geçmişi</h1>
          <p className="text-muted-foreground mt-2">
            Tamamladığınız tüm mülakatlar ve değerlendirme sonuçları
          </p>
        </div>
        
        <Link 
          to="/interview/start" 
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-primary text-white hover:bg-primary/90 transition-colors font-medium"
        >
          <MessageSquare className="h-4 w-4" />
          Yeni Mülakat
        </Link>
      </div>

      {error && (
        <div className="p-4 rounded-lg bg-destructive/10 text-destructive text-sm font-medium">
          {error}
        </div>
      )}

      {!data || data.interviews.length === 0 ? (
        <div className="text-center py-16 bg-muted/30 rounded-xl border border-dashed border-border">
          <MessageSquare className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
          <h3 className="text-lg font-semibold">Henüz mülakat yapmadınız</h3>
          <p className="text-muted-foreground mt-2 max-w-sm mx-auto">
            İlk mülakatınızı başlatın ve yapay zeka ile kendinizi geliştirin.
          </p>
          <Link 
            to="/interview/start" 
            className="inline-flex items-center gap-2 mt-6 px-4 py-2 rounded-lg bg-primary text-white hover:bg-primary/90 transition-colors"
          >
            Mülakat Başlat
          </Link>
        </div>
      ) : (
        <div className="space-y-4">
          {data.interviews.map((interview) => (
            <div 
              key={interview.session_id}
              className="relative bg-card border border-border rounded-xl p-5 hover:border-primary/50 transition-all group"
            >
              <button 
                onClick={() => openDeleteModal(interview.session_id)}
                className="absolute -top-3 -right-3 p-1.5 bg-red-500 text-white rounded-full shadow-lg opacity-0 group-hover:opacity-100 transition-all hover:bg-red-600 z-20 hover:scale-105"
                title="Mülakatı Sil"
              >
                <X className="h-4 w-4" />
              </button>
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div className="space-y-2">
                  <div className="flex items-center gap-3">
                    <h3 className="font-semibold text-lg">
                      {interview.position_name}
                    </h3>
                    <span className="text-sm text-muted-foreground px-2 py-0.5 rounded-full bg-muted">
                      {interview.company_sector_name}
                    </span>
                    {interview.status === 'in_progress' && (
                      <span className="text-xs font-medium px-2 py-0.5 rounded-full bg-yellow-500/10 text-yellow-500">
                        Devam Ediyor
                      </span>
                    )}
                    {interview.status === 'cancelled' && (
                      <span className="text-xs font-medium px-2 py-0.5 rounded-full bg-red-500/10 text-red-500">
                        İptal Edildi
                      </span>
                    )}
                  </div>
                  
                  <div className="flex flex-wrap items-center gap-x-6 gap-y-2 text-sm text-muted-foreground">
                    <div className="flex items-center gap-2">
                      <Trophy className="h-4 w-4" />
                      {interview.experience_level_name}
                    </div>
                    <div className="flex items-center gap-2">
                      <Calendar className="h-4 w-4" />
                      {formatDate(interview.created_at)}
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-6">
                  {interview.status === 'completed' && interview.average_score !== null && (
                    <div className="text-right">
                      <div className="flex items-center justify-end gap-2 mb-1">
                        {interview.passed ? (
                          <span className="flex items-center gap-1 text-xs font-medium text-success bg-success/10 px-2 py-0.5 rounded-full">
                            <CheckCircle className="h-3 w-3" />
                            Başarılı
                          </span>
                        ) : (
                          <span className="flex items-center gap-1 text-xs font-medium text-destructive bg-destructive/10 px-2 py-0.5 rounded-full">
                            <TrendingDown className="h-3 w-3" />
                            Geliştirilmeli
                          </span>
                        )}
                      </div>
                      <div className="text-2xl font-bold font-mono text-primary">
                        {interview.average_score.toFixed(1)}
                        <span className="text-sm font-normal text-muted-foreground ml-1">/ 10</span>
                      </div>
                    </div>
                  )}

                  {interview.status === 'completed' ? (
                    <Link
                      to={`/interview/report/${interview.session_id}`}
                      className="flex items-center gap-2 px-4 py-2 rounded-lg bg-secondary hover:bg-secondary/80 text-secondary-foreground transition-colors text-sm font-medium whitespace-nowrap"
                    >
                      Raporu Gör
                      <ArrowRight className="h-4 w-4" />
                    </Link>
                  ) : interview.status === 'in_progress' ? (
                    <div className="flex gap-2">
                      <Link
                        to="/interview/start"
                        className="flex items-center gap-2 px-4 py-2 rounded-lg bg-yellow-500/10 text-yellow-500 hover:bg-yellow-500/20 transition-colors text-sm font-medium whitespace-nowrap"
                      >
                        Yönet
                      </Link>
                    </div>
                  ) : (
                    <span className="text-sm text-muted-foreground italic">
                      Görüntülenecek rapor yok
                    </span>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

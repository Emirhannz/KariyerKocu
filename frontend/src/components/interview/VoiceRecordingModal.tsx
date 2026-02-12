import { useState, useRef, useEffect, useCallback } from 'react';
import { Mic, Square, Send, X, Loader2 } from 'lucide-react';
import api from '../../lib/api';

interface VoiceRecordingModalProps {
  isOpen: boolean;
  onClose: () => void;
  onTranscriptionComplete: (text: string) => void;
}

export function VoiceRecordingModal({ 
  isOpen, 
  onClose, 
  onTranscriptionComplete 
}: VoiceRecordingModalProps) {
  const [status, setStatus] = useState<'idle' | 'recording' | 'processing'>('idle');
  const [volumeLevel, setVolumeLevel] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [recordingTime, setRecordingTime] = useState(0);
  
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const streamRef = useRef<MediaStream | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const animationFrameRef = useRef<number | null>(null);
  const timerRef = useRef<number | null>(null);

  // Cleanup on unmount or close
  useEffect(() => {
    return () => {
      stopRecording();
      cleanup();
    };
  }, []);

  // Reset when modal opens
  useEffect(() => {
    if (isOpen) {
      setStatus('idle');
      setVolumeLevel(0);
      setError(null);
      setRecordingTime(0);
    }
  }, [isOpen]);

  const cleanup = () => {
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
    }
    if (timerRef.current) {
      clearInterval(timerRef.current);
    }
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
    }
    if (audioContextRef.current) {
      audioContextRef.current.close();
    }
  };

  const startRecording = async () => {
    setError(null);
    
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;
      
      // Setup audio analysis for volume meter
      audioContextRef.current = new AudioContext();
      const analyser = audioContextRef.current.createAnalyser();
      const source = audioContextRef.current.createMediaStreamSource(stream);
      source.connect(analyser);
      analyser.fftSize = 256;
      analyserRef.current = analyser;
      
      // Start volume monitoring
      const updateVolume = () => {
        if (!analyserRef.current) return;
        
        const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount);
        analyserRef.current.getByteFrequencyData(dataArray);
        const average = dataArray.reduce((a, b) => a + b) / dataArray.length;
        setVolumeLevel(Math.min(100, average * 1.5));
        
        animationFrameRef.current = requestAnimationFrame(updateVolume);
      };
      updateVolume();
      
      // Setup MediaRecorder
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      });
      
      chunksRef.current = [];
      
      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunksRef.current.push(e.data);
        }
      };
      
      mediaRecorderRef.current = mediaRecorder;
      mediaRecorder.start(100);
      
      setStatus('recording');
      setRecordingTime(0);
      
      // Timer
      timerRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);
      
    } catch (err) {
      console.error('Mikrofon hatası:', err);
      setError('Mikrofon erişimi sağlanamadı');
    }
  };

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && status === 'recording') {
      mediaRecorderRef.current.stop();
    }
    if (timerRef.current) {
      clearInterval(timerRef.current);
    }
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
    }
    setVolumeLevel(0);
  }, [status]);

  const sendRecording = async () => {
    stopRecording();
    
    // Wait a bit for the last data
    await new Promise(resolve => setTimeout(resolve, 200));
    
    if (chunksRef.current.length === 0) {
      setError('Kayıt alınamadı');
      return;
    }
    
    setStatus('processing');
    
    const audioBlob = new Blob(chunksRef.current, { type: 'audio/webm' });
    
    try {
      const formData = new FormData();
      formData.append('audio', audioBlob, 'recording.webm');
      
      const response = await api.post<{ text: string; success: boolean }>(
        '/interview/transcribe',
        formData,
        {
          headers: { 'Content-Type': 'multipart/form-data' }
        }
      );
      
      if (response.data.success && response.data.text) {
        onTranscriptionComplete(response.data.text);
        cleanup();
        onClose();
      } else {
        setError('Ses tanınamadı, lütfen tekrar deneyin');
        setStatus('idle');
      }
    } catch (err: any) {
      console.error('Transkripsiyon hatası:', err);
      setError(err.response?.data?.detail || 'Ses gönderilemedi');
      setStatus('idle');
    } finally {
      cleanup();
    }
  };

  const cancelRecording = () => {
    stopRecording();
    cleanup();
    setStatus('idle');
    onClose();
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Blur backdrop */}
      <div 
        className="absolute inset-0 bg-black/60 backdrop-blur-md"
        onClick={status === 'idle' ? cancelRecording : undefined}
      />
      
      {/* Modal */}
      <div className="relative bg-card border border-border rounded-2xl p-8 w-full max-w-md mx-4 shadow-2xl">
        {/* Close button */}
        <button
          onClick={cancelRecording}
          className="absolute top-4 right-4 p-2 rounded-lg hover:bg-muted transition-colors"
        >
          <X className="h-5 w-5 text-muted-foreground" />
        </button>
        
        <div className="text-center">
          <h3 className="text-xl font-bold mb-2">🎤 Sesli Cevap</h3>
          <p className="text-sm text-muted-foreground mb-6">
            {status === 'idle' && 'Başlat butonuna basıp konuşmaya başlayın'}
            {status === 'recording' && 'Konuşmanızı dinliyorum...'}
            {status === 'processing' && 'Sesiniz işleniyor...'}
          </p>
          
          {/* Volume indicator */}
          <div className="relative w-32 h-32 mx-auto mb-6">
            {/* Outer ring - volume indicator */}
            <div 
              className="absolute inset-0 rounded-full transition-all duration-100"
              style={{
                background: status === 'recording' 
                  ? `radial-gradient(circle, transparent 50%, rgba(139, 92, 246, ${volumeLevel / 200}) 100%)`
                  : 'transparent',
                transform: `scale(${1 + volumeLevel / 200})`,
              }}
            />
            
            {/* Inner circle */}
            <div className={`
              absolute inset-4 rounded-full flex items-center justify-center
              ${status === 'recording' ? 'bg-red-500 animate-pulse' : 'bg-primary/10'}
              ${status === 'processing' ? 'bg-yellow-500/20' : ''}
            `}>
              {status === 'processing' ? (
                <Loader2 className="h-12 w-12 text-yellow-500 animate-spin" />
              ) : (
                <Mic className={`h-12 w-12 ${status === 'recording' ? 'text-white' : 'text-primary'}`} />
              )}
            </div>
          </div>
          
          {/* Recording time */}
          {status === 'recording' && (
            <p className="text-2xl font-mono font-bold text-red-500 mb-6">
              {formatTime(recordingTime)}
            </p>
          )}
          
          {/* Error message */}
          {error && (
            <p className="text-sm text-destructive mb-4 bg-destructive/10 p-3 rounded-lg">
              {error}
            </p>
          )}
          
          {/* Buttons */}
          <div className="flex justify-center gap-3">
            {status === 'idle' && (
              <button
                onClick={startRecording}
                className="px-8 py-3 rounded-xl bg-primary text-primary-foreground font-medium hover:opacity-90 transition-opacity flex items-center gap-2"
              >
                <Mic className="h-5 w-5" />
                Başlat
              </button>
            )}
            
            {status === 'recording' && (
              <>
                <button
                  onClick={stopRecording}
                  className="px-6 py-3 rounded-xl bg-red-500 text-white font-medium hover:opacity-90 transition-opacity flex items-center gap-2"
                >
                  <Square className="h-4 w-4" />
                  Bitir
                </button>
                <button
                  onClick={sendRecording}
                  className="px-6 py-3 rounded-xl bg-green-500 text-white font-medium hover:opacity-90 transition-opacity flex items-center gap-2"
                >
                  <Send className="h-4 w-4" />
                  Gönder
                </button>
              </>
            )}
            
            {status === 'processing' && (
              <p className="text-muted-foreground">Ses işleniyor, lütfen bekleyin...</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

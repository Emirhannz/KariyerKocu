import { useState, useRef, useCallback } from 'react';
import { Mic, Square, Loader2 } from 'lucide-react';
import api from '../../lib/api';

interface VoiceInputProps {
  onTranscription: (text: string) => void;
  disabled?: boolean;
}

export function VoiceInput({ onTranscription, disabled }: VoiceInputProps) {
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);

  const startRecording = useCallback(async () => {
    setError(null);
    
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      
      // MediaRecorder oluştur
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      });
      
      chunksRef.current = [];
      
      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunksRef.current.push(e.data);
        }
      };
      
      mediaRecorder.onstop = async () => {
        // Stream'i durdur
        stream.getTracks().forEach(track => track.stop());
        
        // Blob oluştur
        const audioBlob = new Blob(chunksRef.current, { type: 'audio/webm' });
        
        // Backend'e gönder
        setIsProcessing(true);
        
        try {
          const formData = new FormData();
          formData.append('audio', audioBlob, 'recording.webm');
          
          const response = await api.post<{ text: string; success: boolean }>(
            '/interview/transcribe',
            formData,
            {
              headers: {
                'Content-Type': 'multipart/form-data',
              },
            }
          );
          
          if (response.data.success && response.data.text) {
            onTranscription(response.data.text);
          }
        } catch (err: any) {
          console.error('Transkripsiyon hatası:', err);
          setError(err.response?.data?.detail || 'Ses tanınamadı');
        } finally {
          setIsProcessing(false);
        }
      };
      
      mediaRecorderRef.current = mediaRecorder;
      mediaRecorder.start(100); // Her 100ms'de chunk al
      setIsRecording(true);
      
    } catch (err) {
      console.error('Mikrofon hatası:', err);
      setError('Mikrofon erişimi sağlanamadı');
    }
  }, [onTranscription]);

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  }, [isRecording]);

  const handleClick = () => {
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  };

  return (
    <div className="flex items-center gap-2">
      <button
        onClick={handleClick}
        disabled={disabled || isProcessing}
        className={`
          p-3 rounded-full transition-all
          ${isRecording 
            ? 'bg-red-500 text-white animate-pulse' 
            : 'bg-primary/10 text-primary hover:bg-primary/20'
          }
          ${(disabled || isProcessing) ? 'opacity-50 cursor-not-allowed' : ''}
        `}
        title={isRecording ? 'Kaydı durdur' : 'Sesli yanıt ver'}
      >
        {isProcessing ? (
          <Loader2 className="h-5 w-5 animate-spin" />
        ) : isRecording ? (
          <Square className="h-5 w-5" />
        ) : (
          <Mic className="h-5 w-5" />
        )}
      </button>
      
      {isRecording && (
        <span className="text-sm text-red-500 animate-pulse">
          Kaydediliyor...
        </span>
      )}
      
      {isProcessing && (
        <span className="text-sm text-muted-foreground">
          İşleniyor...
        </span>
      )}
      
      {error && (
        <span className="text-sm text-red-500">
          {error}
        </span>
      )}
    </div>
  );
}

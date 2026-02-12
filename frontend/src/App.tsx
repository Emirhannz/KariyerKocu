import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useEffect } from 'react';
import { MainLayout } from './components/layout/MainLayout';
import { ProtectedRoute } from './components/layout/ProtectedRoute';
import { LoginPage, RegisterPage } from './features/auth/AuthPages';
import { DashboardPage } from './features/dashboard/DashboardPage';
import { CVUploadPage } from './features/cv/CVUploadPage';
import { CVAnalysisPage } from './features/cv/CVAnalysisPage';
import { RecommendationsPage } from './features/cv/RecommendationsPage';
import { AnalysisResultPage } from './features/cv/AnalysisResultPage';
import { InterviewStartPage } from './features/interview/InterviewStartPage';
import { InterviewSessionPage } from './features/interview/InterviewSessionPage';
import { VoiceInterviewPage } from './features/interview/VoiceInterviewPage';
import { InterviewReportPage } from './features/interview/InterviewReportPage';
import { InterviewHistoryPage } from './features/interview/InterviewHistoryPage';
import { ProfilePage } from './features/profile/ProfilePage';
import { JobSearchPage } from './features/jobs/JobSearchPage';
import { CoverLetterPage } from './features/cover-letter/CoverLetterPage';
import { initTheme } from './stores/themeStore';

import { ToastProvider } from './components/ui/Toast';
import { ErrorBoundary } from './components/ui/ErrorBoundary';

function App() {
  useEffect(() => {
    initTheme();
  }, []);

  return (
    <ErrorBoundary>
      <BrowserRouter>
        <ToastProvider>
        <Routes>
        {/* Public Routes */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />

        {/* Protected Routes */}
        <Route element={<ProtectedRoute />}>
          <Route element={<MainLayout />}>
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/cv/upload" element={<CVUploadPage />} />
            <Route path="/cv/analysis" element={<CVAnalysisPage />} />
            <Route path="/cv/analysis/result" element={<AnalysisResultPage />} />
            <Route path="/recommendations" element={<RecommendationsPage />} />
            <Route path="/interview/start" element={<InterviewStartPage />} />
            <Route path="/interview/session" element={<InterviewSessionPage />} />
            <Route path="/interview/voice-session" element={<VoiceInterviewPage />} />
            <Route path="/interview/history" element={<InterviewHistoryPage />} />
            <Route path="/interview/report/:sessionId" element={<InterviewReportPage />} />
            <Route path="/profile" element={<ProfilePage />} />
            <Route path="/jobs" element={<JobSearchPage />} />
            <Route path="/cover-letter" element={<CoverLetterPage />} />
          </Route>
        </Route>

        {/* Redirect root to dashboard */}
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        
        {/* 404 */}
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
        </ToastProvider>
      </BrowserRouter>
    </ErrorBoundary>
  );
}

export default App;

// API Types - Backend'den gelen verilerin tipleri

// ============================================================================
// AUTH
// ============================================================================

export interface User {
  id: string;
  email: string;
  full_name: string | null;
  is_active: boolean;
  created_at: string;
  target_sector?: string;
  target_position?: string;
  experience_level?: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name?: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
}

// ============================================================================
// CAREER GOALS
// ============================================================================

export interface CareerGoals {
  target_sector: string | null;
  target_sector_name: string | null;
  target_position: string | null;
  target_position_name: string | null;
  experience_level: string | null;
  experience_level_name: string | null;
}

// ============================================================================
// DASHBOARD
// ============================================================================

export interface CVSummary {
  is_uploaded: boolean;
  filename: string | null;
  full_name: string | null;
  skills_count: number;
  projects_count: number;
  uploaded_at: string | null;
}

export interface AnalysisSummary {
  has_analysis: boolean;
  last_analysis_date: string | null;
  strongest_field: string | null;
  strongest_field_name: string | null;
  strongest_score: number | null;
  total_analyses: number;
}

export interface InterviewSummary {
  has_interview: boolean;
  last_interview_date: string | null;
  last_position: string | null;
  last_score: number | null;
  passed: boolean | null;
  total_interviews: number;
  has_active_interview: boolean;
  active_session_id: string | null;
}

export interface DashboardData {
  user_name: string | null;
  email: string;
  member_since: string;
  career_goals: CareerGoals;
  has_career_goals: boolean;
  cv: CVSummary;
  analysis: AnalysisSummary;
  interview: InterviewSummary;
  suggested_actions: string[];
}

// ============================================================================
// CONFIG (Dropdown Data)
// ============================================================================

export interface SelectOption {
  id: string;
  name: string;
}

export interface InterviewTypeOption extends SelectOption {
  description: string;
}

export interface AnalysisConfig {
  sectors: SelectOption[];
  fields: Record<string, SelectOption[]>;
  experience_levels: SelectOption[];
}

export interface InterviewConfig {
  sectors: SelectOption[];
  positions: Record<string, SelectOption[]>;
  experience_levels: SelectOption[];
  interview_types: InterviewTypeOption[];
}

// ============================================================================
// CV ANALYSIS
// ============================================================================

export interface CategoryScore {
  score: number;
  weight: number;
  reason: string;
  suggestions: string[];
}

export interface FieldAnalysis {
  field_id: string;
  field_name: string;
  overall_score: number;
  category_scores: Record<string, CategoryScore>;
  strengths: string[];
  weaknesses: string[];
  matching_skills: string[];
  missing_skills: string[];
}

export interface CVAnalysisResult {
  cv_id: string;
  analysis_date: string;
  cv_name?: string; // Opsiyonel - backend döndürmeyebilir
  profile_context: Record<string, unknown>;
  field_analyses: FieldAnalysis[];
  strongest_field: string;
  action_items: string[];
}

// ============================================================================
// INTERVIEW
// ============================================================================

export interface InterviewQuestion {
  session_id: string;
  question_id: string;
  question_number: number;
  total_questions: number;
  transition_text: string | null;
  question_text: string;
  question_type: string;
  is_last_question: boolean;
}

export interface QuestionReport {
  question_number: number;
  question_type: string;
  question_text: string;
  user_answer: string;
  score: number;
  evaluation_reason: string;
  ideal_answer: string | null;
  strengths: string[];
  weaknesses: string[];
}

export interface InterviewReport {
  session_id: string;
  completed_at: string;
  duration_minutes: number | null;
  company_sector: string;
  company_sector_name: string;
  position: string;
  position_name: string;
  experience_level: string;
  experience_level_name: string;
  interview_type: string;
  total_questions: number;
  answered_questions: number;
  average_score: number;
  passing_score: number;
  passed: boolean;
  questions: QuestionReport[];
  overall_strengths: string[];
  overall_weaknesses: string[];
  recommendation: string | null;
}

export interface InterviewHistoryItem {
  session_id: string;
  position_name: string;
  company_sector_name: string;
  experience_level_name: string;
  average_score: number | null;
  passed: boolean | null;
  status: string;
  created_at: string;
  completed_at: string | null;
}

export interface InterviewHistoryResponse {
  total_count: number;
  interviews: InterviewHistoryItem[];
}

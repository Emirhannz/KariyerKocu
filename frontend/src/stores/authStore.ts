import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import api from '../lib/api';
import type { User, LoginRequest, RegisterRequest, LoginResponse } from '../types';

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  login: (data: LoginRequest) => Promise<void>;
  register: (data: RegisterRequest) => Promise<void>;
  logout: () => void;
  clearError: () => void;
  checkAuth: () => Promise<void>;
  updateUser: (updates: Partial<User>) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      login: async (data: LoginRequest) => {
        set({ isLoading: true, error: null });
        try {
          const response = await api.post<LoginResponse>('/auth/login', data);
          const { access_token, user } = response.data;
          
          // Önceki kullanıcının verilerini temizle
          localStorage.removeItem('interview_session');
          localStorage.removeItem('lastJobSearch');
          localStorage.removeItem('applicationStats');
          localStorage.removeItem('appliedJobs');
          
          localStorage.setItem('token', access_token);
          
          set({
            user,
            token: access_token,
            isAuthenticated: true,
            isLoading: false,
          });
        } catch (error: unknown) {
          const err = error as { response?: { data?: { detail?: string } } };
          set({
            error: err.response?.data?.detail || 'Giriş başarısız',
            isLoading: false,
          });
          throw error;
        }
      },

      register: async (data: RegisterRequest) => {
        set({ isLoading: true, error: null });
        try {
          await api.post('/auth/register', data);
          // Kayıt başarılı, login sayfasına yönlendir
          set({ isLoading: false });
        } catch (error: unknown) {
          const err = error as { response?: { data?: { detail?: string } } };
          set({
            error: err.response?.data?.detail || 'Kayıt başarısız',
            isLoading: false,
          });
          throw error;
        }
      },

      logout: () => {
        localStorage.removeItem('token');
        // Kullanıcıya özel verileri temizle
        localStorage.removeItem('lastJobSearch');
        localStorage.removeItem('applicationStats');
        localStorage.removeItem('appliedJobs');
        localStorage.removeItem('interview_session');
        set({
          user: null,
          token: null,
          isAuthenticated: false,
        });
      },

      clearError: () => set({ error: null }),

      updateUser: (updates: Partial<User>) => set((state) => ({
        user: state.user ? { ...state.user, ...updates } : null
      })),

      checkAuth: async () => {
        const token = localStorage.getItem('token');
        if (!token) {
          set({ isAuthenticated: false });
          return;
        }
        
        try {
          const response = await api.get<{ id: string; email: string; full_name: string | null }>('/auth/me');
          set({
            user: response.data as User,
            token,
            isAuthenticated: true,
          });
        } catch {
          localStorage.removeItem('token');
          set({
            user: null,
            token: null,
            isAuthenticated: false,
          });
        }
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ token: state.token }),
    }
  )
);

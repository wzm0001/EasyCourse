import { create } from 'zustand';
import type { UserInfo, LoginRequest, LoginResponse } from '@/types/auth';
import api from '@/api';
import { getMe } from '@/api/auth';

interface AuthState {
  token: string | null;
  user: UserInfo | null;
  isAuthenticated: boolean;
  login: (data: LoginRequest, remember?: boolean) => Promise<void>;
  logout: () => void;
  setUser: (user: UserInfo) => void;
  loadFromStorage: () => void;
  refreshUser: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  token: null,
  user: null,
  isAuthenticated: false,

  login: async (data: LoginRequest, remember: boolean = false) => {
    const response = await api.post<LoginResponse>('/auth/login', data);
    const result = response.data as any;
    const { access_token, user } = result.data || result;
    const storage = remember ? localStorage : sessionStorage;
    storage.setItem('token', access_token);
    storage.setItem('user', JSON.stringify(user));
    if (remember) {
      localStorage.setItem('remember', 'true');
    } else {
      localStorage.removeItem('remember');
    }
    set({
      token: access_token,
      user,
      isAuthenticated: true,
    });
  },

  logout: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    localStorage.removeItem('remember');
    sessionStorage.removeItem('token');
    sessionStorage.removeItem('user');
    set({
      token: null,
      user: null,
      isAuthenticated: false,
    });
  },

  setUser: (user: UserInfo) => {
    const remember = localStorage.getItem('remember') === 'true';
    const storage = remember ? localStorage : sessionStorage;
    storage.setItem('user', JSON.stringify(user));
    set({ user });
  },

  loadFromStorage: () => {
    const remember = localStorage.getItem('remember') === 'true';
    const storage = remember ? localStorage : sessionStorage;
    const token = storage.getItem('token');
    const userStr = storage.getItem('user');
    if (token && userStr) {
      try {
        const user = JSON.parse(userStr) as UserInfo;
        set({
          token,
          user,
          isAuthenticated: true,
        });
      } catch {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        sessionStorage.removeItem('token');
        sessionStorage.removeItem('user');
      }
    }
  },

  refreshUser: async () => {
    const { token, isAuthenticated } = get();
    if (!token || !isAuthenticated) return;
    try {
      const res = await getMe();
      const userData = (res as any)?.data || res;
      if (userData) {
        const remember = localStorage.getItem('remember') === 'true';
        const storage = remember ? localStorage : sessionStorage;
        storage.setItem('user', JSON.stringify(userData));
        set({ user: userData });
      }
    } catch {
      // ignore refresh errors
    }
  },
}));

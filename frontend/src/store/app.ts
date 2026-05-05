import { create } from 'zustand';

interface AppState {
  theme: 'light' | 'dark';
  sidebarCollapsed: boolean;
  currentSemester: string | null;
  toggleTheme: () => void;
  toggleSidebar: () => void;
  setCurrentSemester: (semester: string) => void;
}

export const useAppStore = create<AppState>((set) => ({
  theme: 'light',
  sidebarCollapsed: false,
  currentSemester: null,

  toggleTheme: () =>
    set((state) => ({
      theme: state.theme === 'light' ? 'dark' : 'light',
    })),

  toggleSidebar: () =>
    set((state) => ({
      sidebarCollapsed: !state.sidebarCollapsed,
    })),

  setCurrentSemester: (semester: string) =>
    set({ currentSemester: semester }),
}));

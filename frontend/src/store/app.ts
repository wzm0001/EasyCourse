import { create } from 'zustand';

interface AppState {
  theme: 'light' | 'dark';
  sidebarCollapsed: boolean;
  mobileDrawerOpen: boolean;
  currentSemester: string | null;
  toggleTheme: () => void;
  toggleSidebar: () => void;
  setMobileDrawerOpen: (open: boolean) => void;
  setCurrentSemester: (semester: string) => void;
}

export const useAppStore = create<AppState>((set) => ({
  theme: 'light',
  sidebarCollapsed: false,
  mobileDrawerOpen: false,
  currentSemester: null,

  toggleTheme: () =>
    set((state) => ({
      theme: state.theme === 'light' ? 'dark' : 'light',
    })),

  toggleSidebar: () =>
    set((state) => ({
      sidebarCollapsed: !state.sidebarCollapsed,
    })),

  setMobileDrawerOpen: (open: boolean) =>
    set({ mobileDrawerOpen: open }),

  setCurrentSemester: (semester: string) =>
    set({ currentSemester: semester }),
}));

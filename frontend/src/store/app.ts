import { create } from 'zustand';
import { getActiveSemester } from '@/api/semesters';

interface AppState {
  theme: 'light' | 'dark';
  sidebarCollapsed: boolean;
  mobileDrawerOpen: boolean;
  currentSemester: string | null;
  currentSemesterName: string | null;
  currentSemesterArchived: boolean;
  unreadCount: number;
  toggleTheme: () => void;
  toggleSidebar: () => void;
  setMobileDrawerOpen: (open: boolean) => void;
  setCurrentSemester: (semester: string) => void;
  setUnreadCount: (count: number) => void;
  fetchActiveSemester: () => Promise<void>;
}

export const useAppStore = create<AppState>((set) => ({
  theme: 'light',
  sidebarCollapsed: false,
  mobileDrawerOpen: false,
  currentSemester: null,
  currentSemesterName: null,
  currentSemesterArchived: false,
  unreadCount: 0,

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

  setUnreadCount: (count: number) =>
    set({ unreadCount: count }),

  fetchActiveSemester: async () => {
    try {
      const res = await getActiveSemester();
      const data = (res as any)?.data || res;
      if (data && data.id) {
        set({
          currentSemester: data.id,
          currentSemesterName: data.name,
          currentSemesterArchived: data.is_archived || data.status === 'archived',
        });
      } else {
        set({ currentSemester: null, currentSemesterName: null, currentSemesterArchived: false });
      }
    } catch {
      set({ currentSemester: null, currentSemesterName: null, currentSemesterArchived: false });
    }
  },
}));

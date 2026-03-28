import { create } from 'zustand';
import type { Alert } from '@/types';

interface AlertStore {
  unreadCount: number;
  alerts: Alert[];
  setAlerts: (alerts: Alert[]) => void;
  addAlert: (alert: Alert) => void;
  markRead: () => void;
  incrementUnread: () => void;
}

export const useAlertStore = create<AlertStore>((set) => ({
  unreadCount: 0,
  alerts: [],
  setAlerts: (alerts) => set({ alerts }),
  addAlert: (alert) =>
    set((state) => ({
      alerts: [alert, ...state.alerts],
      unreadCount: state.unreadCount + 1,
    })),
  markRead: () => set({ unreadCount: 0 }),
  incrementUnread: () => set((s) => ({ unreadCount: s.unreadCount + 1 })),
}));

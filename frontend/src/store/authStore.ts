import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface AuthState {
  user: { id: string; email: string } | null;
  isAuthenticated: boolean;
  sessionId: string;
  setUser: (user: { id: string; email: string } | null) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      isAuthenticated: false,
      sessionId: crypto.randomUUID(),
      setUser: (user) =>
        set({
          user,
          isAuthenticated: user !== null,
        }),
      logout: () =>
        set({
          user: null,
          isAuthenticated: false,
        }),
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        sessionId: state.sessionId,
      }),
    }
  )
);

import { type Session, type User } from '@supabase/supabase-js';
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { supabase } from '@/lib/supabase';
import { apiClient } from '@/services/api';

interface AuthState {
  user: User | null;
  session: Session | null;
  isAuthenticated: boolean;
  sessionId: string;
  isLoading: boolean;

  signUp: (email: string, password: string) => Promise<void>;
  signIn: (email: string, password: string) => Promise<void>;
  signOut: () => Promise<void>;
  initialize: () => Promise<void>;
  setUser: (user: User | null) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, _get) => ({
      user: null,
      session: null,
      isAuthenticated: false,
      sessionId: crypto.randomUUID(),
      isLoading: true,

      signUp: async (email: string, password: string) => {
        const { data, error } = await supabase.auth.signUp({
          email,
          password,
        });
        if (error) throw error;

        set({
          user: data.user,
          session: data.session,
          isAuthenticated: !!data.user,
        });
      },

      signIn: async (email: string, password: string) => {
        const { data, error } = await supabase.auth.signInWithPassword({
          email,
          password,
        });
        if (error) throw error;

        const previousSessionId = _get().sessionId;

        set({
          user: data.user,
          session: data.session,
          isAuthenticated: !!data.user,
        });

        // Migrate anonymous activities to authenticated user
        if (previousSessionId) {
          try {
            await apiClient.migrateActivities(previousSessionId);
          } catch {
            // Migration is best-effort; don't block sign-in
          }
        }
      },

      signOut: async () => {
        await supabase.auth.signOut();
        set({
          user: null,
          session: null,
          isAuthenticated: false,
          sessionId: crypto.randomUUID(),
        });
      },

      initialize: async () => {
        try {
          const {
            data: { session },
          } = await supabase.auth.getSession();
          set({
            user: session?.user ?? null,
            session: session ?? null,
            isAuthenticated: !!session?.user,
            isLoading: false,
          });

          supabase.auth.onAuthStateChange((_event, session) => {
            set({
              user: session?.user ?? null,
              session: session ?? null,
              isAuthenticated: !!session?.user,
            });
          });
        } catch {
          set({ isLoading: false });
        }
      },

      setUser: (user) =>
        set({
          user,
          isAuthenticated: user !== null,
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

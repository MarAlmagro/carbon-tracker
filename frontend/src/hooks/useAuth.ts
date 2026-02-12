import { useAuthStore } from '@/store/authStore';

export function useAuth() {
  const {
    user,
    isAuthenticated,
    sessionId,
    isLoading,
    session,
    signUp,
    signIn,
    signOut,
    initialize,
    setUser,
  } = useAuthStore();

  return {
    user,
    isAuthenticated,
    sessionId,
    isLoading,
    session,
    signUp,
    signIn,
    signOut,
    initialize,
    setUser,
  };
}

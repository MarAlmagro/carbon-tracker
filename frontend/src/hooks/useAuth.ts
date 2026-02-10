import { useAuthStore } from '@/store/authStore';

export function useAuth() {
  const { user, isAuthenticated, sessionId, setUser, logout } = useAuthStore();

  return {
    user,
    isAuthenticated,
    sessionId,
    setUser,
    logout,
  };
}

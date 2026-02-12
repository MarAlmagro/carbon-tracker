import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import { AuthGuard } from '@/components/auth/AuthGuard';
import { AppShell } from '@/components/layout/AppShell';
import { ComparisonPage } from '@/pages/ComparisonPage';
import { DashboardPage } from '@/pages/DashboardPage';
import { HomePage } from '@/pages/HomePage';
import { ProfilePage } from '@/pages/ProfilePage';
import { SignInPage } from '@/pages/SignInPage';
import { SignUpPage } from '@/pages/SignUpPage';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/signin" element={<SignInPage />} />
          <Route path="/signup" element={<SignUpPage />} />
          <Route path="/" element={<AppShell />}>
            <Route index element={<HomePage />} />
            <Route path="dashboard" element={<DashboardPage />} />
            <Route path="compare" element={<ComparisonPage />} />
            <Route
              path="profile"
              element={
                <AuthGuard>
                  <ProfilePage />
                </AuthGuard>
              }
            />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;

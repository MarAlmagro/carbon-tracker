import { Outlet } from 'react-router-dom';
import { Navigation } from './Navigation';

export function AppShell() {
  return (
    <div className="min-h-screen flex flex-col">
      <Navigation />
      <main className="flex-1 container mx-auto px-4 py-8">
        <Outlet />
      </main>
      <footer className="border-t py-6 text-center text-sm text-muted-foreground">
        <p>© 2026 Carbon Footprint Tracker</p>
      </footer>
    </div>
  );
}

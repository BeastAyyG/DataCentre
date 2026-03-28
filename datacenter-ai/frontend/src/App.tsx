import { BrowserRouter, Routes, Route, NavLink, useLocation } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useWebSocket } from '@/hooks/useWebSocket';
import { useAlertStore } from '@/store/useAlertStore';
import { ToastContainer } from '@/components/ui/Toast';
import { LandingPage } from '@/pages/LandingPage';
import { OverviewPage } from '@/pages/OverviewPage';
import { AnomaliesPage } from '@/pages/AnomaliesPage';
import { ActionsPage } from '@/pages/ActionsPage';
import { DashboardPage } from '@/pages/Dashboard';
import { SimulationViewPage } from '@/pages/SimulationView';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

function NavBar() {
  const unreadCount = useAlertStore((s) => s.unreadCount);

  return (
    <nav className="bg-slate-900 border-b border-slate-700 px-6 py-3 flex items-center gap-6">
      <div className="flex items-center gap-2">
        <div className="w-6 h-6 bg-gradient-to-br from-cyber-purple to-cyber-600 rounded flex items-center justify-center">
          <span className="text-white text-xs font-bold">AI</span>
        </div>
        <span className="font-bold text-white">AKAGAMI</span>
      </div>
      <div className="flex gap-1">
        {[
          { to: '/overview', label: 'Overview' },
          { to: '/dashboard', label: 'Dashboard' },
          { to: '/anomalies', label: 'AI Anomalies', badge: unreadCount },
          { to: '/actions', label: 'Actions' },
        ].map(({ to, label, badge }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `px-4 py-2 rounded-lg text-sm font-medium transition flex items-center gap-2 ${
                isActive ? 'bg-slate-800 text-white' : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
              }`
            }
          >
            {label}
            {badge != null && badge > 0 && (
              <span className="bg-red-500 text-white text-xs font-bold rounded-full px-1.5 py-0.5">
                {badge}
              </span>
            )}
          </NavLink>
        ))}
      </div>
      <div className="ml-auto flex items-center gap-3">
        <NavLink
          to="/"
          className="text-xs text-slate-500 hover:text-slate-300 transition"
        >
          ← Landing
        </NavLink>
        <NavLink
          to="/simulation"
          className="px-4 py-2 rounded-lg text-sm font-medium bg-cyber-purple text-white hover:bg-cyber-purpleDark transition"
        >
          🎯 Simulation View
        </NavLink>
      </div>
    </nav>
  );
}

function DashboardLayout({ children }: { children: React.ReactNode }) {
  useWebSocket();
  return (
    <div className="min-h-screen bg-slate-950">
      <NavBar />
      {children}
    </div>
  );
}

function AppContent() {
  const location = useLocation();
  const isLanding = location.pathname === '/';

  if (isLanding) {
    return <LandingPage />;
  }

  return (
    <DashboardLayout>
      <main className="p-6 max-w-7xl mx-auto">
        <Routes>
          <Route path="/overview" element={<OverviewPage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/anomalies" element={<AnomaliesPage />} />
          <Route path="/actions" element={<ActionsPage />} />
          <Route path="/simulation" element={<SimulationViewPage />} />
        </Routes>
      </main>
      <ToastContainer />
    </DashboardLayout>
  );
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AppContent />
      </BrowserRouter>
    </QueryClientProvider>
  );
}

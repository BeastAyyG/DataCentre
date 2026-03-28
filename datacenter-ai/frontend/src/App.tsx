import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useWebSocket } from '@/hooks/useWebSocket';
import { useAlertStore } from '@/store/useAlertStore';
import { ToastContainer } from '@/components/ui/Toast';
import { OverviewPage } from '@/pages/OverviewPage';
import { AnomaliesPage } from '@/pages/AnomaliesPage';
import { ActionsPage } from '@/pages/ActionsPage';

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
        <div className="w-6 h-6 bg-blue-600 rounded flex items-center justify-center">
          <span className="text-white text-xs font-bold">AI</span>
        </div>
        <span className="font-bold text-white">DataCenter AI</span>
      </div>
      <div className="flex gap-1">
        {[
          { to: '/', label: 'Overview' },
          { to: '/anomalies', label: 'AI Anomalies', badge: unreadCount },
          { to: '/actions', label: 'Actions' },
        ].map(({ to, label, badge }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              px-4 py-2 rounded-lg text-sm font-medium transition flex items-center gap-2 
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
    </nav>
  );
}

function AppContent() {
  useWebSocket();
  return (
    <div className="min-h-screen bg-slate-950">
      <NavBar />
      <main className="p-6 max-w-7xl mx-auto">
        <Routes>
          <Route path="/" element={<OverviewPage />} />
          <Route path="/anomalies" element={<AnomaliesPage />} />
          <Route path="/actions" element={<ActionsPage />} />
        </Routes>
      </main>
      <ToastContainer />
    </div>
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

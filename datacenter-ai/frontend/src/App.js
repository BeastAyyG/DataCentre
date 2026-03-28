"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.default = App;
var react_router_dom_1 = require("react-router-dom");
var react_query_1 = require("@tanstack/react-query");
var useWebSocket_1 = require("@/hooks/useWebSocket");
var useAlertStore_1 = require("@/store/useAlertStore");
var Toast_1 = require("@/components/ui/Toast");
var queryClient = new react_query_1.QueryClient({
    defaultOptions: {
        queries: {
            retry: 1,
            refetchOnWindowFocus: false,
        },
    },
});
function NavBar() {
    var unreadCount = (0, useAlertStore_1.useAlertStore)(function (s) { return s.unreadCount; });
    return (<nav className/>);
    "bg-slate-900 border-b border-slate-700 px-6 py-3 flex items-center gap-6">
        < div;
    className = ;
    "flex items-center gap-2">
        < div;
    className = ;
    "w-6 h-6 bg-blue-600 rounded flex items-center justify-center">
        < span;
    className = ;
    "text-white text-xs font-bold">AI</span>;
    div >
        <span className/>;
    "font-bold text-white">DataCenter AI</span>;
    div >
        <div className/>;
    "flex gap-1">;
    {
        [
            { to: '/', label: 'Overview' },
            { to: '/anomalies', label: 'AI Anomalies', badge: unreadCount },
            { to: '/actions', label: 'Actions' },
        ].map(function (_a) {
            var to = _a.to, label = _a.label, badge = _a.badge;
            return (<react_router_dom_1.NavLink key={to} to={to} className={function (_a) {
                    var isActive = _a.isActive;
                    return px - 4;
                }} py-2 rounded-lg text-sm font-medium transition flex items-center gap-2/>);
        });
    }
        >
            { label: label };
    {
        badge != null && badge > 0 && (<span className/>);
        "bg-red-500 text-white text-xs font-bold rounded-full px-1.5 py-0.5">;
        {
            badge;
        }
        span >
        ;
    }
    react_router_dom_1.NavLink >
    ;
}
div >
;
nav >
;
;
function AppContent() {
    (0, useWebSocket_1.useWebSocket)();
    return (<div className/>);
    "min-h-screen bg-slate-950">
        < NavBar /  >
        <main className/>;
    "p-6 max-w-7xl mx-auto">
        < react_router_dom_1.Routes >
        <react_router_dom_1.Route path/>;
    "/" element={<OverviewPage />} />
        < react_router_dom_1.Route;
    path = ;
    "/anomalies" element={<AnomaliesPage />} />
        < react_router_dom_1.Route;
    path = ;
    "/actions" element={<ActionsPage />} />;
    react_router_dom_1.Routes >
    ;
    main >
        <Toast_1.ToastContainer />;
    div >
    ;
    ;
}
function App() {
    return (<react_query_1.QueryClientProvider client={queryClient}>
      <react_router_dom_1.BrowserRouter>
        <AppContent />
      </react_router_dom_1.BrowserRouter>
    </react_query_1.QueryClientProvider>);
}

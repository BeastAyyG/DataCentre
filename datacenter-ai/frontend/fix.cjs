const fs = require('fs');

const tryFix = (file, pattern, replacement) => {
    try {
        let content = fs.readFileSync(file, 'utf8');
        content = content.replace(pattern, replacement);
        fs.writeFileSync(file, content);
        console.log('Fixed ' + file);
    } catch (e) {
        console.log('Failed ' + file + ' : ' + e.message);
    }
};

tryFix('src/components/molecules/AlertRow.tsx', /<div className=\{[^>]*?order border-slate-700 rounded-lg p-4 mb-3 bg-slate-800 \}>/, `<div className={\`border border-slate-700 rounded-lg p-4 mb-3 bg-slate-800 \${alert.severity === 'critical' ? 'border-red-500 bg-red-950/20' : ''}\`}>`);
tryFix('src/components/molecules/MetricCard.tsx', /<span className=\{[^>]*?ext-xs font-semibold ml-1 \}>/, `<span className={\`text-xs font-semibold ml-1 \${(trend ?? 0) >= 0 ? "text-green-400" : "text-red-400"}\`}>`);
tryFix('src/components/molecules/WorkOrderCard.tsx', /style=\{\{ width: \$\{\(completedSteps \/ steps\.length\) \* 100\}% \}\}/, "style={{ width: `${(completedSteps / steps.length) * 100}%` }}");
tryFix('src/components/organisms/KPIStrip.tsx', /sublabel=\{\$\{kpi\.active_critical_alerts\} critical .*? warning\}/, "sublabel={`${kpi.active_critical_alerts} critical · ${kpi.active_warning_alerts} warning`}");
tryFix('src/components/ui/Badge.tsx', /<span className=\{[^>]*?ext-xs font-semibold px-2 py-0\.5 rounded  \}>/, "<span className={`text-xs font-semibold px-2 py-0.5 rounded ${variantClasses[variant]} ${className}`}>");
tryFix('src/components/ui/Button.tsx', /className=\{[^}]*?ont-medium transition disabled:opacity-50 disabled:cursor-not-allowed[\s\S]*?\}/, "className={`font-medium transition disabled:opacity-50 disabled:cursor-not-allowed ${variantClasses[variant]} ${sizeClasses[size!]} ${className}`}");
tryFix('src/components/ui/Card.tsx', /<div className=\{[^>]*?g-slate-800 rounded-lg border border-slate-700 \}>/, "<div className={`bg-slate-800 rounded-lg border border-slate-700 ${className}`}>");
tryFix('src/components/ui/Skeleton.tsx', /className=\{[^}]*?nimate-pulse bg-slate-700 rounded \}/, "className={`animate-pulse bg-slate-700 rounded ${className}`}");
tryFix('src/components/ui/Toast.tsx', /className=\{[^}]*?lex items-center gap-3 px-4 py-3 rounded-lg border-slate-700 \}/, "className={`flex items-center gap-3 px-4 py-3 rounded-lg border border-slate-700 shadow-lg ${typeClasses[toast.type]}`}");
tryFix('src/hooks/useWebSocket.ts', /const wsUrl = \$\{proto\}:\/\/\/ws\/sensors;/, "const wsUrl = `${proto}://${window.location.host}/ws/sensors`;");
tryFix('src/hooks/useWorkOrders.ts', /toast\.success\(Work order completed! Saved ~[^{]*?\{data\.estimated_saving_usd\}\)/, "toast.success(`Work order completed! Saved ~\\$${data.estimated_saving_usd}`)");

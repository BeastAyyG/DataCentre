import os

fixes = [
    ('src/components/molecules/AlertRow.tsx', 'className={', '    <div className={order border-slate-700 rounded-lg p-4 mb-3 bg-slate-800 }>\n'),
    ('src/components/molecules/MetricCard.tsx', '<span className={', '          <span className={	ext-xs font-semibold ml-1 }>\n'),
    ('src/components/molecules/WorkOrderCard.tsx', 'style={{ width:', '              style={{ width: ${(completedSteps / steps.length) * 100}% }}\n'),
    ('src/components/organisms/KPIStrip.tsx', 'sublabel={$', '        sublabel={${kpi.active_critical_alerts} critical \\u00b7  warning}\n'),
    ('src/components/ui/Badge.tsx', '<span className={', '    <span className={	ext-xs font-semibold px-2 py-0.5 rounded  }>\n'),
    ('src/components/ui/Button.tsx', 'className={', '      className={ont-medium transition disabled:opacity-50 disabled:cursor-not-allowed   }\n'),
    ('src/components/ui/Card.tsx', '<div className={', '    <div className={g-slate-800 rounded-lg border border-slate-700 }>\n'),
    ('src/components/ui/Skeleton.tsx', 'className={', '      className={nimate-pulse bg-slate-700 rounded }\n'),
    ('src/components/ui/Toast.tsx', 'className={', '      className={lex items-center gap-3 px-4 py-3 rounded-lg border shadow-lg }\n'),
    ('src/hooks/useWebSocket.ts', 'const wsUrl =', '    const wsUrl = ${proto}:///ws/sensors;\n'),
    ('src/hooks/useWorkOrders.ts', 'toast.success(', '        toast.success(Work order completed! Saved ~)\n')
]

for fp, search, replacement in fixes:
    if os.path.exists(fp):
        with open(fp, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Check if already fixed
        already_fixed = False
        for i, line in enumerate(lines):
            # If line is exactly replacement, it's fixed
            if line.strip() == replacement.strip():
                already_fixed = True
                break
                
        if already_fixed:
            continue
            
        # Find index with search string
        for i, line in enumerate(lines):
            if search in line and ('\x0c' in line or '\x08' in line or '\x0b' in line or '\x0a' in line or '\t' in line or '{ ' in line or '=$' in line or '~{' in line):
                lines[i] = replacement
                break
                
        with open(fp, 'w', encoding='utf-8') as f:
            f.writelines(lines)

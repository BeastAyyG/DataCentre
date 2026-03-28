import os
import re

def fix_file(filepath, pattern, replacement):
    if not os.path.exists(filepath): return
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    content = re.sub(pattern, replacement, content)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

fix_file('src/components/molecules/AlertRow.tsx', r'<div className={.*?mb-3 }>', r'<div className={order border-slate-700 rounded-lg p-4 mb-3 bg-slate-800 }>')
fix_file('src/components/molecules/MetricCard.tsx', r'<span className={.*?ml-1 }>', r'<span className={	ext-xs font-semibold ml-1 }>')
fix_file('src/components/molecules/WorkOrderCard.tsx', r'style={{ width: \$\{\(completedSteps / steps\.length\) \* 100\}% }}', r'style={{ width: ${(completedSteps / steps.length) * 100}% }}')
fix_file('src/components/organisms/KPIStrip.tsx', r'sublabel=\{\$\{kpi\.active_critical_alerts\}.*?warning\}', r'sublabel={${kpi.active_critical_alerts} critical \\u00b7  warning}')
fix_file('src/components/ui/Badge.tsx', r'<span className={.*?rounded  }>', r'<span className={	ext-xs font-semibold px-2 py-0.5 rounded  }>')
fix_file('src/components/ui/Button.tsx', r'className={.*?disabled:cursor-not-allowed   }', r'className={ont-medium transition disabled:opacity-50 disabled:cursor-not-allowed   }')
fix_file('src/components/ui/Card.tsx', r'<div className={.*?border border-slate-700 }>', r'<div className={g-slate-800 rounded-lg border border-slate-700 }>')
fix_file('src/components/ui/Skeleton.tsx', r'className={.*?bg-slate-700 rounded }', r'className={nimate-pulse bg-slate-700 rounded }')
fix_file('src/components/ui/Toast.tsx', r'className={.*?border-slate-700 }>', r'className={lex items-center gap-3 px-4 py-3 rounded-lg border border-slate-700 shadow-lg }>')

# others
fix_file('src/hooks/useWebSocket.ts', r'const wsUrl = \$\{proto\}///ws/sensors;', r'const wsUrl = ${proto}:///ws/sensors;')
fix_file('src/hooks/useWorkOrders.ts', r'toast\.success\(Work order completed! Saved ~\{data\.estimated_saving_usd\}\)', r'toast.success(Work order completed! Saved ~{data.estimated_saving_usd})')


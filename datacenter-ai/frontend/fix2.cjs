const fs = require('fs');
let fp = 'src/components/organisms/KPIStrip.tsx';
let content = fs.readFileSync(fp, 'utf8');
content = content.replace(/sublabel=\{.*\}/g, "sublabel={${kpi.active_critical_alerts} critical ·  warning}");
fs.writeFileSync(fp, content);

fp = 'src/components/ui/Toast.tsx';
content = fs.readFileSync(fp, 'utf8');
content = content.replace(/className=\{.*lex items-center gap-3.*\}/g, "className={lex items-center gap-3 px-4 py-3 rounded-lg border shadow-lg }");
fs.writeFileSync(fp, content);

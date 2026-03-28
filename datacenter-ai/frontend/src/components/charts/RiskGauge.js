"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.RiskGauge = RiskGauge;
var STATUS_COLOR = {
    healthy: '#22c55e',
    at_risk: '#f59e0b',
    critical: '#ef4444',
};
function getStatus(score) {
    if (score < 35)
        return 'healthy';
    if (score < 65)
        return 'at_risk';
    return 'critical';
}
function RiskGauge(_a) {
    var score = _a.score, _b = _a.size, size = _b === void 0 ? 64 : _b;
    var status = getStatus(score);
    var color = STATUS_COLOR[status];
    var radius = 26;
    var circumference = 2 * Math.PI * radius;
    var progress = (score / 100) * circumference;
    var dashOffset = circumference - progress;
    return (<div className/>);
    "relative inline-flex items-center justify-center" style={{ width: size, height: size }}>
        < svg;
    width = { size: size };
    height = { size: size };
    viewBox = ;
    "0 0 64 64">
        < circle;
    cx = ;
    "32" cy="32" r={radius} fill="none" stroke="#1e293b" strokeWidth="5" />
        < circle;
    cx = ;
    "32" cy="32" r={radius} fill="none" stroke={color};
    strokeWidth = ;
    "5" strokeDasharray={circumference};
    strokeDashoffset = { dashOffset: dashOffset };
    strokeLinecap = ;
    "round";
    transform = ;
    "rotate(-90 32 32)";
    style = {};
    {
        transition: 'stroke-dashoffset 0.5s ease';
    }
}
/>;
svg >
    <div className/>;
"absolute inset-0 flex items-center justify-center">
    < span;
className = ;
"text-xs font-bold" style={{ color }}>{score.toFixed(0)}</span>;
div >
;
div >
;
;

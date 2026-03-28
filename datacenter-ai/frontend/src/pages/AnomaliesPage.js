"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.AnomaliesPage = AnomaliesPage;
var useAlertStore_1 = require("@/store/useAlertStore");
var AlertPanel_1 = require("@/components/organisms/AlertPanel");
var Card_1 = require("@/components/ui/Card");
function AnomaliesPage() {
    var unreadCount = (0, useAlertStore_1.useAlertStore)(function (s) { return s.unreadCount; });
    var markRead = (0, useAlertStore_1.useAlertStore)(function (s) { return s.markRead; });
    return (<div className/>);
    "space-y-6">
        < div;
    className = ;
    "flex items-center justify-between">
        < div >
        <h1 className/>;
    "text-2xl font-bold text-white">AI Anomaly Detection</h1>
        < p;
    className = ;
    "text-sm text-slate-400 mt-1">AI-generated alerts with risk scores and recommended actions</p>;
    div >
        { unreadCount: unreadCount } > 0 && (<button onClick={markRead} className/>);
    "text-xs text-blue-400 hover:text-blue-300"
        >
            Mark;
    all;
    ({ unreadCount: unreadCount });
    button >
    ;
}
div >
    <Card_1.Card title/>;
"Open Alerts">
    < AlertPanel_1.AlertPanel /  >
;
Card_1.Card >
    <div className/>;
"bg-slate-800 border border-slate-700 rounded-lg p-4">
    < h3;
className = ;
"text-sm font-semibold text-slate-300 mb-3">How Risk Scoring Works</h3>
    < div;
className = ;
"grid grid-cols-3 gap-4 text-xs">
    < div;
className = ;
"bg-slate-900 rounded p-3">
    < p;
className = ;
"text-blue-400 font-semibold mb-1">IsolationForest (50%)</p>
    < p;
className = ;
"text-slate-400">Unsupervised anomaly detection on 6 sensor features: temperature, power, airflow, humidity, CPU.</p>;
div >
    <div className/>;
"bg-slate-900 rounded p-3">
    < p;
className = ;
"text-blue-400 font-semibold mb-1">Prophet Forecast (35%)</p>
    < p;
className = ;
"text-slate-400">Time-series forecasting of expected temperature/power — deviations flag risk.</p>;
div >
    <div className/>;
"bg-slate-900 rounded p-3">
    < p;
className = ;
"text-blue-400 font-semibold mb-1">Alert Frequency (15%)</p>
    < p;
className = ;
"text-slate-400">Devices with recurring alerts get a compounding risk bonus.</p>;
div >
;
div >
    <div className/>;
"mt-3 flex items-center gap-6 text-xs text-slate-400">
    < span > <span className/>;
"text-green-400">&lt;35</span> Healthy (green)</span>
    < span > <span className/>;
"text-amber-400">35-65</span> At Risk (amber)</span>
    < span > <span className/>;
"text-red-400">&gt;65</span> Critical (red)</span>;
div >
;
div >
;
div >
;
;

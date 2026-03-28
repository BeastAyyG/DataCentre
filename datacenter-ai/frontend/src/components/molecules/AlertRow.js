"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.AlertRow = AlertRow;
var react_1 = require("react");
var Badge_1 = require("@/components/ui/Badge");
var Button_1 = require("@/components/ui/Button");
function AlertRow(_a) {
    var alert = _a.alert, onAccept = _a.onAccept, onReject = _a.onReject, loading = _a.loading;
    var _b = (0, react_1.useState)(false), showReject = _b[0], setShowReject = _b[1];
    var _c = (0, react_1.useState)(''), rejectReason = _c[0], setRejectReason = _c[1];
    return (<div className={} order rounded-lg p-4 mb-3/>);
}
 >
    <div className/>;
"flex items-start justify-between gap-3">
    < div;
className = ;
"flex-1">
    < div;
className = ;
"flex items-center gap-2 mb-1">
    < Badge_1.Badge;
variant = { alert: alert, : .severity } > { alert: alert, : .severity.toUpperCase() };
Badge_1.Badge >
    <Badge_1.Badge variant={alert.status === 'open' ? 'default' : 'healthy'}>{alert.status}</Badge_1.Badge>
        ,
            <span className/>;
"text-xs text-slate-500">{alert.device_id}</span>
    < span;
className = ;
"text-xs text-slate-500 ml-auto">{format(new Date(alert.triggered_at), 'HH:mm:ss')}</span>;
div >
    <p className/>;
"text-sm text-slate-200 mb-1">{alert.reason}</p>;
{
    alert.impact_estimate && (<p className/>);
    "text-xs text-slate-400 mb-2">Impact: {alert.impact_estimate}</p>;
}
{
    alert.recommended_action && (<p className/>);
    "text-xs text-blue-300 bg-blue-950/40 rounded p-2 border border-blue-800">;
    AI;
    Recommendation: {
        alert.recommended_action;
    }
    p >
    ;
}
{
    showReject && (<div className/>);
    "mt-2">
        < input;
    type = ;
    "text";
    placeholder = ;
    "Reason for rejection (optional)";
    className = ;
    "w-full bg-slate-800 border border-slate-600 rounded px-3 py-1.5 text-sm text-slate-200 mb-2";
    value = { rejectReason: rejectReason };
    onChange = {}(e);
    setRejectReason(e.target.value);
}
/>
    < div;
className = ;
"flex gap-2">
    < Button_1.Button;
variant = ;
"ghost" size="sm" onClick={() => setShowReject(false)}>Cancel</Button>
    < Button_1.Button;
variant = ;
"reject" size="sm" onClick={() => { onReject(alert.id, 'Operator', rejectReason); setShowReject(false); }}>Confirm Reject</Button>;
div >
;
div >
;
div >
    {};
showReject && alert.status === 'open' && (<div className/>);
"flex flex-col gap-2 ml-3">
    < Button_1.Button;
variant = ;
"accept" size="sm" disabled={loading} onClick={() => onAccept(alert.id, 'Operator')}>;
{
    loading ? 'Accepting...' : 'Accept';
}
Button_1.Button >
    <Button_1.Button variant/>;
"reject" size="sm" disabled={loading} onClick={() => setShowReject(true)}>Reject</Button>;
div >
;
div >
;
div >
;
;

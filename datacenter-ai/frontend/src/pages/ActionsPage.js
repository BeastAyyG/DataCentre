"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ActionsPage = ActionsPage;
var react_1 = require("react");
var WorkOrderList_1 = require("@/components/organisms/WorkOrderList");
var AuditLogDrawer_1 = require("@/components/organisms/AuditLogDrawer");
var Card_1 = require("@/components/ui/Card");
var Button_1 = require("@/components/ui/Button");
function ActionsPage() {
    var _a = (0, react_1.useState)(false), showAudit = _a[0], setShowAudit = _a[1];
    return (<div className/>);
    "space-y-6">
        < div;
    className = ;
    "flex items-center justify-between">
        < div >
        <h1 className/>;
    "text-2xl font-bold text-white">Actions & Work Orders</h1>
        < p;
    className = ;
    "text-sm text-slate-400 mt-1">Manage work orders from AI recommendations and view operator actions</p>;
    div >
        <Button_1.Button variant/>;
    "ghost" size="sm" onClick={() => setShowAudit(true)}>;
    View;
    Audit;
    Log;
    Button_1.Button >
    ;
    div >
        <Card_1.Card title/>;
    "Active Work Orders">
        < WorkOrderList_1.WorkOrderList /  >
    ;
    Card_1.Card >
        <div className/>;
    "bg-slate-800 border border-slate-700 rounded-lg p-4">
        < h3;
    className = ;
    "text-sm font-semibold text-slate-300 mb-3">Human-in-the-Loop Design</h3>
        < div;
    className = ;
    "space-y-2 text-xs text-slate-400">
        < p > 1.;
    AI;
    detects;
    anomaly;
    and;
    creates;
    a;
    recommendation;
    with (Accept / Reject)
        options;
    p >
        <p>2. Operator reviews the AI explanation, impact estimate, and recommended action</p>
            ,
                <p>3. Accept creates a structured work order with step-by-step guidance; Reject logs the reason</p>
                    ,
                        <p>4. All actions are recorded in the immutable audit log for compliance and learning</p>;
    div >
    ;
    div >
        <AuditLogDrawer_1.AuditLogDrawer open={showAudit} onClose={function () { return setShowAudit(false); }}/>;
    div >
    ;
    ;
}

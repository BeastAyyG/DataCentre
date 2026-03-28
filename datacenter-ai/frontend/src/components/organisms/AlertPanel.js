"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.AlertPanel = AlertPanel;
var useAlerts_1 = require("@/hooks/useAlerts");
var AlertRow_1 = require("@/components/molecules/AlertRow");
var Skeleton_1 = require("@/components/ui/Skeleton");
function AlertPanel() {
    var _a = (0, useAlerts_1.useAlerts)({ status: 'open' }), data = _a.data, isLoading = _a.isLoading;
    var acceptMutation = (0, useAlerts_1.useAcceptAlert)();
    var rejectMutation = (0, useAlerts_1.useRejectAlert)();
    if (isLoading) {
        return (<div className/>);
        "space-y-3">;
        {
            Array.from({ length: 3 }).map(function (_, i) { return <Skeleton_1.SkeletonAlertRow key={i}/>; });
        }
        div >
        ;
        ;
    }
    var alerts = (data === null || data === void 0 ? void 0 : data.items) || [];
    if (alerts.length === 0) {
        return (<div className/>);
        "text-center py-12 text-slate-500">
            < div;
        className = ;
        "text-4xl mb-3">✓</div>
            < p;
        className = ;
        "text-lg font-medium text-slate-300 mb-1">All Clear</p>
            < p;
        className = ;
        "text-sm">No open anomalies — all systems operating normally.</p>;
        div >
        ;
        ;
    }
    return (<div>
      {alerts.map(function (alert) { return (<AlertRow_1.AlertRow key={alert.id} alert={alert} onAccept={function (id, actor) { return acceptMutation.mutate({ id: id, actor: actor }); }} onReject={function (id, actor, reason) { return rejectMutation.mutate({ id: id, actor: actor, reason: reason }); }} loading={acceptMutation.isPending || rejectMutation.isPending}/>); })}
    </div>);
}

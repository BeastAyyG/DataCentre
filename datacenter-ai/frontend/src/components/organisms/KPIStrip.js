"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.KPIStrip = KPIStrip;
var useKPIs_1 = require("@/hooks/useKPIs");
var MetricCard_1 = require("@/components/molecules/MetricCard");
var Skeleton_1 = require("@/components/ui/Skeleton");
function KPIStrip() {
    var _a;
    var _b = (0, useKPIs_1.useKPIs)('24h'), kpi = _b.data, isLoading = _b.isLoading;
    if (isLoading || !kpi) {
        return (<div className/>);
        "grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-3">;
        {
            Array.from({ length: 6 }).map(function (_, i) { return <Skeleton_1.SkeletonCard key={i}/>; });
        }
        div >
        ;
        ;
    }
    return (<div className/>);
    "grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-3">
        < MetricCard_1.MetricCard;
    label = ;
    "PUE";
    value = { kpi: kpi, : .pue.toFixed(3) };
    trend = { kpi: kpi, : (_a = .pue_trend) !== null && _a !== void 0 ? _a : undefined };
    sublabel = ;
    "Power Usage Effectiveness"
        /  >
        <MetricCard_1.MetricCard label/>;
    "Total Power";
    value = { kpi: kpi, : .total_power_kwh.toFixed(1) };
    unit = ;
    "kWh";
    sublabel = ;
    "Last 24h"
        /  >
        <MetricCard_1.MetricCard label/>;
    "Cooling";
    value = { kpi: kpi, : .cooling_power_kwh.toFixed(1) };
    unit = ;
    "kWh";
    sublabel = ;
    "Last 24h"
        /  >
        <MetricCard_1.MetricCard label/>;
    "Uptime Saved";
    value = { kpi: kpi, : .downtime_avoided_hours.toFixed(1) };
    unit = ;
    "hrs";
    sublabel = ;
    "Last 24h"
        /  >
        <MetricCard_1.MetricCard label/>;
    "Cost Saved";
    value = { '$': +kpi.cost_savings_usd.toLocaleString() };
    sublabel = ;
    "Last 24h"
        /  >
        <MetricCard_1.MetricCard label/>;
    "Active Alerts";
    value = { kpi: kpi, : .active_critical_alerts + kpi.active_warning_alerts };
    sublabel = { $: $ };
    {
        kpi.active_critical_alerts;
    }
    critical;
    warning;
}
/>;
div >
;
;

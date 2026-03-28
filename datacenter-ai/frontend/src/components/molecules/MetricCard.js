"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.MetricCard = MetricCard;
var Card_1 = require("@/components/ui/Card");
function MetricCard(_a) {
    var label = _a.label, value = _a.value, unit = _a.unit, trend = _a.trend, sublabel = _a.sublabel;
    return (<Card_1.Card className/>);
    "min-w-[120px]">
        < p;
    className = ;
    "text-xs text-slate-400 uppercase tracking-wide mb-1">{label}</p>
        < div;
    className = ;
    "flex items-baseline gap-1">
        < span;
    className = ;
    "text-2xl font-bold text-white">{value}</span>;
    {
        unit && <span className/>;
        "text-sm text-slate-400">{unit}</span>};
        {
            trend !== undefined && (<span className={ext - xs} font-semibold ml-1/>);
        }
         >
            { trend: trend } >= 0 ? '+' : '';
    }
    {
        trend.toFixed(2);
    }
    span >
    ;
}
div >
    { sublabel: sublabel } && <p className/>;
"text-xs text-slate-500 mt-1">{sublabel}</p>};
Card_1.Card >
;
;

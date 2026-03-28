"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.DeviceNode = DeviceNode;
var Badge_1 = require("@/components/ui/Badge");
var RiskGauge_1 = require("@/components/charts/RiskGauge");
function DeviceNode(_a) {
    var device = _a.device, sensorData = _a.sensorData, onClick = _a.onClick;
    var statusVariant = device.status === 'healthy' ? 'healthy' : device.status === 'at_risk' ? 'at_risk' : device.status === 'critical' ? 'critical' : 'default';
    return (<div className={} g-slate-800 border-2 rounded-lg p-3 cursor-pointer hover:bg-slate-700 transition/>);
}
onClick = { onClick: onClick }
    >
        <div className/>;
"flex items-center justify-between mb-2">
    < div >
    <p className/>;
"text-sm font-semibold text-white">{device.name}</p>
    < p;
className = ;
"text-xs text-slate-500">{device.id}</p>;
div >
    <RiskGauge_1.RiskGauge score={device.current_risk_score} size={48}/>;
div >
    <div className/>;
"flex items-center gap-2 mb-1">
    < Badge_1.Badge;
variant = { statusVariant: statusVariant } > { device: device, : .status };
Badge_1.Badge >
    { device: device, : .zone && <span className/>, "text-xs text-slate-500">{device.zone}</span>}: , div: div } >
    { sensorData: sensorData } && (<div className/>);
"grid grid-cols-2 gap-1 mt-2 text-xs">;
{
    sensorData.inlet_temp_c != null && (<div><span className/>"text-slate-500">Temp:</span>, <span className/>);
    "text-slate-200">{sensorData.inlet_temp_c.toFixed(1)}C</span></div>;
}
{
    sensorData.power_kw != null && (<div><span className/>"text-slate-500">Power:</span>, <span className/>);
    "text-slate-200">{sensorData.power_kw.toFixed(1)}kW</span></div>;
}
{
    sensorData.pue_instant != null && (<div><span className/>"text-slate-500">PUE:</span>, <span className/>);
    "text-slate-200">{sensorData.pue_instant.toFixed(3)}</span></div>;
}
div >
;
div >
;
;

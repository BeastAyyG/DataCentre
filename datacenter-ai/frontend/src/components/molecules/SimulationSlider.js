"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.SimulationSlider = SimulationSlider;
var react_1 = require("react");
var Button_1 = require("@/components/ui/Button");
var Spinner_1 = require("@/components/ui/Spinner");
function SimulationSlider(_a) {
    var devices = _a.devices, selectedDeviceId = _a.selectedDeviceId, currentSetpoint = _a.currentSetpoint, onRun = _a.onRun, onDeviceChange = _a.onDeviceChange, loading = _a.loading;
    var _b = (0, react_1.useState)(currentSetpoint), value = _b[0], setValue = _b[1];
    return (<div className/>);
    "bg-slate-900 border border-slate-700 rounded-lg p-4">
        < div;
    className = ;
    "flex items-center justify-between mb-3">
        < h4;
    className = ;
    "text-sm font-semibold text-white">What-If: Cooling Setpoint</h4>
        < select;
    className = ;
    "bg-slate-800 border border-slate-600 text-slate-200 text-xs rounded px-2 py-1";
    value = { selectedDeviceId: selectedDeviceId };
    onChange = {}(e);
    {
        onDeviceChange(e.target.value);
        setValue(currentSetpoint);
    }
}
    >
        { devices: devices, : .map(function (d) { return (<option key={d.id} value={d.id}>{d.name} ({d.id})</option>); }) };
select >
;
div >
    <div className/>;
"flex items-center gap-4 mb-3">
    < input;
type = ;
"range";
min = { 16:  };
max = { 28:  };
step = { 0.5:  };
value = { value: value };
onChange = {}(e);
setValue(parseFloat(e.target.value));
className = ;
"flex-1 accent-blue-500"
    /  >
    <span className/>;
"text-white font-bold w-12 text-right">{value}C</span>;
div >
    <div className/>;
"flex items-center justify-between mb-3 text-xs">
    < span;
className = ;
"text-slate-400">;
Current: <span className/>;
"text-white">{currentSetpoint}C</span>;
span >
    <span className/>;
"text-slate-400">;
Delta: {
    ' ';
}
<span className={value !== currentSetpoint ? 'text-blue-400' : 'text-slate-500'}>
            {value - currentSetpoint > 0 ? '+' : ''}{(value - currentSetpoint).toFixed(1)}C
          </span>;
span >
;
div >
    <Button_1.Button variant/>;
"primary";
className = ;
"w-full";
disabled = { loading: loading } || value === currentSetpoint;
onClick = {}();
onRun(selectedDeviceId, currentSetpoint, value);
    >
        {} < Spinner_1.Spinner;
size = { 14:  } /  > Running;
 > ;
'Run Simulation';
Button_1.Button >
;
div >
;
;

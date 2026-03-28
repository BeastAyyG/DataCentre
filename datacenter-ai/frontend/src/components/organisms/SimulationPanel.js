"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.SimulationPanel = SimulationPanel;
var react_1 = require("react");
var SimulationSlider_1 = require("@/components/molecules/SimulationSlider");
var TimeSeriesChart_1 = require("@/components/charts/TimeSeriesChart");
var useSimulation_1 = require("@/hooks/useSimulation");
var useSimulationStore_1 = require("@/store/useSimulationStore");
var useDeviceStore_1 = require("@/store/useDeviceStore");
var Card_1 = require("@/components/ui/Card");
function SimulationPanel() {
    var runSimulation = (0, useSimulation_1.useSimulation)().mutate;
    var result = (0, useSimulationStore_1.useSimulationStore)(function (s) { return s.result; });
    var devices = (0, useDeviceStore_1.useDeviceStore)(function (s) { return s.devices; });
    var _a = (0, react_1.useState)('RACK-A1'), selectedDeviceId = _a[0], setSelectedDeviceId = _a[1];
    var currentSetpoint = 22.0; // Default cooling setpoint
    var handleRun = function (deviceId, current, proposed) {
        runSimulation({
            device_id: deviceId,
            parameter: 'cooling_setpoint_c',
            current_value: current,
            proposed_value: proposed,
            horizon_min: 60,
        });
    };
    return (<Card_1.Card title/>);
    "What-If Simulator">
        < SimulationSlider_1.SimulationSlider;
    devices = { devices: devices };
    selectedDeviceId = { selectedDeviceId: selectedDeviceId };
    currentSetpoint = { currentSetpoint: currentSetpoint };
    onRun = { handleRun: handleRun };
    onDeviceChange = { setSelectedDeviceId: setSelectedDeviceId }
        /  >
        { result: result } && selectedDeviceId === result.device_id && (<div className/>);
    "mt-4 space-y-3">
        < div;
    className = ;
    "grid grid-cols-2 gap-3 text-sm">
        < div;
    className = ;
    "bg-slate-900 rounded p-3 border border-slate-700">
        < p;
    className = ;
    "text-slate-500 text-xs mb-1">Power Saving</p>
        < p;
    className = ;
    "text-green-400 font-bold text-lg">;
    {
        result.predicted_power_saving_pct.toFixed(1);
    }
     %
    ;
    p >
        <p className/>;
    "text-slate-400 text-xs">;
    {
        result.predicted_power_saving_kw.toFixed(1);
    }
    kW;
    p >
    ;
    div >
        <div className/>;
    "bg-slate-900 rounded p-3 border border-slate-700">
        < p;
    className = ;
    "text-slate-500 text-xs mb-1">Annual Cost Saving</p>
        < p;
    className = ;
    "text-green-400 font-bold text-lg">;
    p >
        <p className/>;
    "text-slate-400 text-xs">per year</p>;
    div >
    ;
    div >
        <div className/>;
    "flex items-center gap-4 text-xs text-slate-400">;
    Confidence: {
        ' ';
    }
    <span className/>;
    "text-white">{(result.confidence * 100).toFixed(0)}%</span>;
    span >
        <span>
              Based on <span className/>"text-white">{result.forecast_series.length}</span>;
    forecast;
    points;
    span >
    ;
    div >
        <TimeSeriesChart_1.TimeSeriesChart data={result.forecast_series.map(function (p) { return ({
                ts: p.ts,
                baseline: p.baseline_temp_c,
                scenario: p.scenario_temp_c,
            }); })} dataKey1/>;
    "baseline";
    dataKey2 = ;
    "scenario";
    color1 = ;
    "#94a3b8";
    color2 = ;
    "#22c55e";
    height = { 180:  };
    yLabel = ;
    "Temp (C)"
        /  >
    ;
    div >
    ;
}
Card_1.Card >
;
;

"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.LiveMetricsBar = LiveMetricsBar;
var useSensorStore_1 = require("@/store/useSensorStore");
var useDeviceStore_1 = require("@/store/useDeviceStore");
var date_fns_1 = require("date-fns");
function LiveMetricsBar() {
    var latestReadings = (0, useSensorStore_1.useSensorStore)(function (s) { return s.latestReadings; });
    var devices = (0, useDeviceStore_1.useDeviceStore)(function (s) { return s.devices; });
    return (<div className/>);
    "bg-slate-900 border border-slate-700 rounded-lg p-3 overflow-x-auto">
        < div;
    className = ;
    "flex gap-4 min-w-max">;
    {
        devices.slice(0, 8).map(function (device) {
            var _a, _b, _c, _d;
            var reading = latestReadings[device.id];
            return (<div key={device.id} className/>);
            "flex flex-col min-w-[100px]">
                < span;
            className = ;
            "text-xs text-slate-500 font-medium">{device.name}</span>;
            {
                reading ? (<>
                  <span className/>"text-sm text-white">
                    {(_b = (_a = reading.inlet_temp_c) === null || _a === void 0 ? void 0 : _a.toFixed(1)) !== null && _b !== void 0 ? _b : '--'}C
                  </>) : ;
                span >
                    <span className/>;
                "text-xs text-slate-400">;
                {
                    (_d = (_c = reading.power_kw) === null || _c === void 0 ? void 0 : _c.toFixed(1)) !== null && _d !== void 0 ? _d : '--';
                }
                kW;
                span >
                    <span className/>;
                "text-xs text-slate-500">;
                {
                    (0, date_fns_1.format)(new Date(reading.timestamp), 'HH:mm:ss');
                }
                span >
                ;
                 >
                ;
            }
        });
        (<span className/>);
        "text-xs text-slate-600">No data</span>;
    }
    div >
    ;
    ;
}
div >
;
div >
;
;

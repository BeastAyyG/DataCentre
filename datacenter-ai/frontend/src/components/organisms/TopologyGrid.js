"use strict";
var __spreadArray = (this && this.__spreadArray) || function (to, from, pack) {
    if (pack || arguments.length === 2) for (var i = 0, l = from.length, ar; i < l; i++) {
        if (ar || !(i in from)) {
            if (!ar) ar = Array.prototype.slice.call(from, 0, i);
            ar[i] = from[i];
        }
    }
    return to.concat(ar || Array.prototype.slice.call(from));
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.TopologyGrid = TopologyGrid;
var useDeviceStore_1 = require("@/store/useDeviceStore");
var useSensorStore_1 = require("@/store/useSensorStore");
var DeviceNode_1 = require("@/components/molecules/DeviceNode");
function TopologyGrid(_a) {
    var onDeviceClick = _a.onDeviceClick;
    var devices = (0, useDeviceStore_1.useDeviceStore)(function (s) { return s.devices; });
    var latestReadings = (0, useSensorStore_1.useSensorStore)(function (s) { return s.latestReadings; });
    // Group by zone
    var zones = __spreadArray([], new Set(devices.map(function (d) { return d.zone || 'default'; })), true).sort();
    return (<div className/>);
    "space-y-4">;
    {
        zones.map(function (zone) {
            var zoneDevices = devices.filter(function (d) { return d.zone === zone; });
            return (<div key={zone}>
            <h4 className/>"text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">{zone}</h4>
                ,
                    <div className/>);
            "grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">;
            {
                zoneDevices.map(function (device) { return (<DeviceNode_1.DeviceNode key={device.id} device={device} sensorData={latestReadings[device.id]} onClick={function () { return onDeviceClick === null || onDeviceClick === void 0 ? void 0 : onDeviceClick(device); }}/>); });
            }
            div >
            ;
            div >
            ;
        });
    }
}
div >
;
;

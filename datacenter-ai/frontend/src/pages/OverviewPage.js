"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.OverviewPage = OverviewPage;
var react_1 = require("react");
var react_query_1 = require("@tanstack/react-query");
var client_1 = require("@/api/client");
var useDeviceStore_1 = require("@/store/useDeviceStore");
var useAlertStore_1 = require("@/store/useAlertStore");
var KPIStrip_1 = require("@/components/organisms/KPIStrip");
var TopologyGrid_1 = require("@/components/organisms/TopologyGrid");
var LiveMetricsBar_1 = require("@/components/organisms/LiveMetricsBar");
var SimulationPanel_1 = require("@/components/organisms/SimulationPanel");
var Card_1 = require("@/components/ui/Card");
var Button_1 = require("@/components/ui/Button");
function OverviewPage() {
    var setDevices = (0, useDeviceStore_1.useDeviceStore)(function (s) { return s.setDevices; });
    var unreadCount = (0, useAlertStore_1.useAlertStore)(function (s) { return s.unreadCount; });
    var devices = (0, react_query_1.useQuery)({
        queryKey: ['devices'],
        queryFn: client_1.apiDevices.list,
        refetchInterval: 10000,
    }).data;
    (0, react_1.useEffect)(function () {
        if (devices)
            setDevices(devices);
    }, [devices, setDevices]);
    return (<div className/>);
    "space-y-6">
        < div;
    className = ;
    "flex items-center justify-between">
        < div >
        <h1 className/>;
    "text-2xl font-bold text-white">Data Center Overview</h1>
        < p;
    className = ;
    "text-sm text-slate-400 mt-1">Real-time infrastructure monitoring</p>;
    div >
        <div className/>;
    "flex items-center gap-3">;
    {
        unreadCount > 0 && (<div className/>);
        "bg-red-600 text-white text-xs font-bold px-3 py-1 rounded-full">;
        {
            unreadCount;
        }
        Alert;
        {
            unreadCount > 1 ? 's' : '';
        }
        div >
        ;
    }
    <Button_1.Button variant/>;
    "ghost";
    size = ;
    "sm";
    onClick = {}();
    client_1.apiDemo.injectAnomaly('RACK-A1');
}
    >
        Inject;
Demo;
Alert;
Button_1.Button >
;
div >
;
div >
    <KPIStrip_1.KPIStrip />
        ,
            <LiveMetricsBar_1.LiveMetricsBar />
                ,
                    <div className/>;
"grid grid-cols-1 lg:grid-cols-3 gap-6">
    < div;
className = ;
"lg:col-span-2">
    < Card_1.Card;
title = ;
"Rack Topology">
    < TopologyGrid_1.TopologyGrid /  >
;
Card_1.Card >
;
div >
    <div>
          <SimulationPanel_1.SimulationPanel />
        </div>;
div >
;
div >
;
;

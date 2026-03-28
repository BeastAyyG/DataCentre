"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.useWebSocket = useWebSocket;
var react_1 = require("react");
var useSensorStore_1 = require("@/store/useSensorStore");
var useAlertStore_1 = require("@/store/useAlertStore");
var HEARTBEAT_INTERVAL_MS = 30000;
function useWebSocket() {
    var wsRef = (0, react_1.useRef)(null);
    var updateReading = (0, useSensorStore_1.useSensorStore)(function (s) { return s.updateReading; });
    var addAlert = (0, useAlertStore_1.useAlertStore)(function (s) { return s.addAlert; });
    var heartbeatRef = (0, react_1.useRef)(null);
    var connect = (0, react_1.useCallback)(function () {
        var proto = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        var wsUrl = $, proto = (void 0).proto; ///ws/sensors;
        var ws = new WebSocket(wsUrl);
        wsRef.current = ws;
        ws.onmessage = function (event) {
            try {
                var msg = JSON.parse(event.data);
                if (msg.type === 'sensor_update') {
                    updateReading(msg.payload);
                }
                else if (msg.type === 'alert_triggered') {
                    addAlert(msg.payload);
                }
            }
            catch (e) {
                console.error('WS parse error:', e);
            }
        };
        ws.onclose = function () {
            if (heartbeatRef.current)
                clearInterval(heartbeatRef.current);
            setTimeout(connect, 3000);
        };
        ws.onerror = function (err) {
            console.error('WebSocket error:', err);
            ws.close();
        };
        // Heartbeat: send ping every 30s to detect stale connections
        heartbeatRef.current = setInterval(function () {
            if (ws.readyState === WebSocket.OPEN) {
                ws.send('ping');
            }
        }, HEARTBEAT_INTERVAL_MS);
    }, [updateReading, addAlert]);
    (0, react_1.useEffect)(function () {
        connect();
        return function () {
            var _a;
            if (heartbeatRef.current)
                clearInterval(heartbeatRef.current);
            (_a = wsRef.current) === null || _a === void 0 ? void 0 : _a.close();
        };
    }, [connect]);
}

"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.apiDemo = exports.apiHealth = exports.apiML = exports.apiAuditLog = exports.apiSimulation = exports.apiKPIs = exports.apiWorkOrders = exports.apiAlerts = exports.apiSensors = exports.apiDevices = void 0;
var axios_1 = require("axios");
var client = axios_1.default.create({
    baseURL: '/api/v1',
    headers: { 'Content-Type': 'application/json' },
});
// ── Devices ────────────────────────────────────────────────────────────────────
exports.apiDevices = {
    list: function () { return client.get('/devices').then(function (r) { return r.data; }); },
    get: function (id) { return client.get(/devices/).then(function (r) { return r.data; }); },
};
// ── Sensors ────────────────────────────────────────────────────────────────────
exports.apiSensors = {
    latest: function (deviceIds) {
        return client.get('/sensors/latest', {
            params: deviceIds ? { device_ids: deviceIds } : {},
        }).then(function (r) { return r.data; });
    },
    history: function (deviceId, limit) {
        if (limit === void 0) { limit = 100; }
        return client.get('/sensors/history', {
            params: { device_id: deviceId, limit: limit },
        }).then(function (r) { return r.data; });
    },
};
// ── Alerts ─────────────────────────────────────────────────────────────────────
exports.apiAlerts = {
    list: function (params) {
        return client.get('/alerts', { params: params }).then(function (r) { return r.data; });
    },
    get: function (id) { return client.get(/alerts/).then(function (r) { return r.data; }); },
    acknowledge: function (id, body) {
        return client.patch(/alerts/ / acknowledge, body).then(function (r) { return r.data; });
    },
    accept: function (id, body) {
        return client.post(/alerts/ / accept, body).then(function (r) { return r.data; });
    },
    reject: function (id, body) {
        return client.post(/alerts/ / reject, body).then(function (r) { return r.data; });
    },
};
// ── Work Orders ────────────────────────────────────────────────────────────────
exports.apiWorkOrders = {
    list: function (params) {
        return client.get('/work-orders', { params: params }).then(function (r) { return r.data; });
    },
    get: function (id) { return client.get(/work-orders/).then(function (r) { return r.data; }); },
    create: function (body) {
        return client.post('/work-orders', body).then(function (r) { return r.data; });
    },
    update: function (id, body) {
        return client.patch(/work-orders/, body).then(function (r) { return r.data; });
    },
};
// ── KPIs ───────────────────────────────────────────────────────────────────────
exports.apiKPIs = {
    get: function (window) {
        if (window === void 0) { window = '24h'; }
        return client.get('/kpis', { params: { window: window } }).then(function (r) { return r.data; });
    },
};
// ── Simulation ─────────────────────────────────────────────────────────────────
exports.apiSimulation = {
    whatIf: function (body) { return client.post('/simulation/what-if', body).then(function (r) { return r.data; }); },
};
// ── Audit Log ──────────────────────────────────────────────────────────────────
exports.apiAuditLog = {
    list: function (params) {
        return client.get('/audit-log', { params: params }).then(function (r) { return r.data; });
    },
};
// ── ML ─────────────────────────────────────────────────────────────────────────
exports.apiML = {
    modelRegistry: function () { return client.get('/ml/model-registry').then(function (r) { return r.data; }); },
};
// ── Health ─────────────────────────────────────────────────────────────────────
exports.apiHealth = {
    check: function () { return client.get('/health').then(function (r) { return r.data; }); },
};
// ── Demo ───────────────────────────────────────────────────────────────────────
exports.apiDemo = {
    injectAnomaly: function (deviceId) {
        if (deviceId === void 0) { deviceId = 'RACK-A1'; }
        return client.post('/demo/inject-anomaly', null, { params: { device_id: deviceId } }).then(function (r) { return r.data; });
    },
};

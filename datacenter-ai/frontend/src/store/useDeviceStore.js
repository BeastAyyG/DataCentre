"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.useDeviceStore = void 0;
var zustand_1 = require("zustand");
exports.useDeviceStore = (0, zustand_1.create)(function (set) { return ({
    devices: [],
    selectedDeviceId: null,
    setDevices: function (devices) { return set({ devices: devices }); },
    selectDevice: function (id) { return set({ selectedDeviceId: id }); },
}); });

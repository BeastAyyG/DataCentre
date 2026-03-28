"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.useSimulationStore = void 0;
var zustand_1 = require("zustand");
exports.useSimulationStore = (0, zustand_1.create)(function (set) { return ({
    result: null,
    isRunning: false,
    setResult: function (result) { return set({ result: result }); },
    setRunning: function (isRunning) { return set({ isRunning: isRunning }); },
}); });

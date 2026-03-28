"use strict";
var __assign = (this && this.__assign) || function () {
    __assign = Object.assign || function(t) {
        for (var s, i = 1, n = arguments.length; i < n; i++) {
            s = arguments[i];
            for (var p in s) if (Object.prototype.hasOwnProperty.call(s, p))
                t[p] = s[p];
        }
        return t;
    };
    return __assign.apply(this, arguments);
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.useSensorStore = void 0;
var zustand_1 = require("zustand");
exports.useSensorStore = (0, zustand_1.create)(function (set) { return ({
    latestReadings: {},
    updateReading: function (reading) {
        return set(function (state) {
            var _a;
            return ({
                latestReadings: __assign(__assign({}, state.latestReadings), (_a = {}, _a[reading.device_id] = reading, _a)),
            });
        });
    },
}); });

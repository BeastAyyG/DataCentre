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
exports.useAlertStore = void 0;
var zustand_1 = require("zustand");
exports.useAlertStore = (0, zustand_1.create)(function (set) { return ({
    unreadCount: 0,
    alerts: [],
    setAlerts: function (alerts) { return set({ alerts: alerts }); },
    addAlert: function (alert) {
        return set(function (state) { return ({
            alerts: __spreadArray([alert], state.alerts, true),
            unreadCount: state.unreadCount + 1,
        }); });
    },
    markRead: function () { return set({ unreadCount: 0 }); },
    incrementUnread: function () { return set(function (s) { return ({ unreadCount: s.unreadCount + 1 }); }); },
}); });

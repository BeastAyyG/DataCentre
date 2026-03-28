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
exports.useWorkOrderStore = void 0;
var zustand_1 = require("zustand");
exports.useWorkOrderStore = (0, zustand_1.create)(function (set) { return ({
    workOrders: [],
    setWorkOrders: function (workOrders) { return set({ workOrders: workOrders }); },
    addWorkOrder: function (wo) { return set(function (s) { return ({ workOrders: __spreadArray([wo], s.workOrders, true) }); }); },
    updateWorkOrder: function (wo) {
        return set(function (s) { return ({
            workOrders: s.workOrders.map(function (w) { return (w.id === wo.id ? wo : w); }),
        }); });
    },
}); });

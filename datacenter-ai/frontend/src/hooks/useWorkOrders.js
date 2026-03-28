"use strict";
var __rest = (this && this.__rest) || function (s, e) {
    var t = {};
    for (var p in s) if (Object.prototype.hasOwnProperty.call(s, p) && e.indexOf(p) < 0)
        t[p] = s[p];
    if (s != null && typeof Object.getOwnPropertySymbols === "function")
        for (var i = 0, p = Object.getOwnPropertySymbols(s); i < p.length; i++) {
            if (e.indexOf(p[i]) < 0 && Object.prototype.propertyIsEnumerable.call(s, p[i]))
                t[p[i]] = s[p[i]];
        }
    return t;
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.useWorkOrders = useWorkOrders;
exports.useUpdateWorkOrder = useUpdateWorkOrder;
var react_query_1 = require("@tanstack/react-query");
var client_1 = require("@/api/client");
var useWorkOrderStore_1 = require("@/store/useWorkOrderStore");
var useToast_1 = require("@/hooks/useToast");
function useWorkOrders(params) {
    var setWorkOrders = (0, useWorkOrderStore_1.useWorkOrderStore)(function (s) { return s.setWorkOrders; });
    return (0, react_query_1.useQuery)({
        queryKey: ['work-orders', params],
        queryFn: function () { return client_1.apiWorkOrders.list(params); },
        refetchInterval: 30000,
        onSuccess: function (data) { return setWorkOrders(data.items); },
    });
}
function useUpdateWorkOrder() {
    var queryClient = (0, react_query_1.useQueryClient)();
    return (0, react_query_1.useMutation)({
        mutationFn: function (_a) {
            var id = _a.id, body = __rest(_a, ["id"]);
            return client_1.apiWorkOrders.update(id, body);
        },
        onSuccess: function (data) {
            var _a, _b;
            if (data.status === 'completed') {
                useToast_1.toast.success(Work, order, completed, Saved, ~{ data: data, : (_b = (_a = .estimated_saving_usd) === null || _a === void 0 ? void 0 : _a.toFixed(0)) !== null && _b !== void 0 ? _b : '—' });
            }
            else {
                useToast_1.toast.success('Work order updated');
            }
            queryClient.invalidateQueries({ queryKey: ['work-orders'] });
            queryClient.invalidateQueries({ queryKey: ['audit-log'] });
        },
        onError: function () {
            useToast_1.toast.error('Failed to update work order');
        },
    });
}

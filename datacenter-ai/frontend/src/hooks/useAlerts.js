"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.useAlerts = useAlerts;
exports.useAcceptAlert = useAcceptAlert;
exports.useRejectAlert = useRejectAlert;
var react_query_1 = require("@tanstack/react-query");
var client_1 = require("@/api/client");
var useAlertStore_1 = require("@/store/useAlertStore");
var useWorkOrderStore_1 = require("@/store/useWorkOrderStore");
var useToast_1 = require("@/hooks/useToast");
function useAlerts(params) {
    var setAlerts = (0, useAlertStore_1.useAlertStore)(function (s) { return s.setAlerts; });
    return (0, react_query_1.useQuery)({
        queryKey: ['alerts', params],
        queryFn: function () { return client_1.apiAlerts.list(params); },
        refetchInterval: 30000,
        onSuccess: function (data) { return setAlerts(data.items); },
    });
}
function useAcceptAlert() {
    var queryClient = (0, react_query_1.useQueryClient)();
    var addWorkOrder = (0, useWorkOrderStore_1.useWorkOrderStore)(function (s) { return s.addWorkOrder; });
    return (0, react_query_1.useMutation)({
        mutationFn: function (_a) {
            var id = _a.id, actor = _a.actor;
            return client_1.apiAlerts.accept(id, { accepted_by: actor });
        },
        onMutate: function () {
            useToast_1.toast.info('Creating work order...');
        },
        onSuccess: function (data) {
            addWorkOrder(data.work_order);
            useToast_1.toast.success('Work order created from AI recommendation');
            queryClient.invalidateQueries({ queryKey: ['alerts'] });
            queryClient.invalidateQueries({ queryKey: ['work-orders'] });
            queryClient.invalidateQueries({ queryKey: ['audit-log'] });
        },
        onError: function () {
            useToast_1.toast.error('Failed to accept recommendation — please try again');
        },
    });
}
function useRejectAlert() {
    var queryClient = (0, react_query_1.useQueryClient)();
    return (0, react_query_1.useMutation)({
        mutationFn: function (_a) {
            var id = _a.id, actor = _a.actor, reason = _a.reason;
            return client_1.apiAlerts.reject(id, { rejected_by: actor, reason: reason });
        },
        onSuccess: function () {
            useToast_1.toast.info('Recommendation rejected — reason logged');
            queryClient.invalidateQueries({ queryKey: ['alerts'] });
            queryClient.invalidateQueries({ queryKey: ['audit-log'] });
        },
        onError: function () {
            useToast_1.toast.error('Failed to reject — please try again');
        },
    });
}

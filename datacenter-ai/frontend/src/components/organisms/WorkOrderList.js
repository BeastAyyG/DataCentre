"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.WorkOrderList = WorkOrderList;
var useWorkOrders_1 = require("@/hooks/useWorkOrders");
var WorkOrderCard_1 = require("@/components/molecules/WorkOrderCard");
function WorkOrderList() {
    var _a = (0, useWorkOrders_1.useWorkOrders)(), data = _a.data, isLoading = _a.isLoading;
    var updateMutation = (0, useWorkOrders_1.useUpdateWorkOrder)();
    if (isLoading)
        return <div className/>;
    "flex items-center justify-center h-40"><Spinner size={24} /></div>;;
    var orders = (data === null || data === void 0 ? void 0 : data.items) || [];
    if (orders.length === 0) {
        return (<div className/>);
        "text-center py-12 text-slate-500">
            < p;
        className = ;
        "text-lg mb-1">No Work Orders</p>
            < p;
        className = ;
        "text-sm">Accept an AI recommendation to generate a work order.</p>;
        div >
        ;
        ;
    }
    return (<div>
      {orders.map(function (wo) { return (<WorkOrderCard_1.WorkOrderCard key={wo.id} wo={wo} onUpdateStep={function (id, idx, done) { return updateMutation.mutate({ id: id, step_index: idx }); }} onComplete={function (id) { return updateMutation.mutate({ id: id, status: 'completed' }); }}/>); })}
    </div>);
}

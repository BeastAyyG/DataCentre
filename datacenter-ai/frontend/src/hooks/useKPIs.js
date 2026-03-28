"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.useKPIs = useKPIs;
var react_query_1 = require("@tanstack/react-query");
var client_1 = require("@/api/client");
function useKPIs(window) {
    if (window === void 0) { window = '24h'; }
    return (0, react_query_1.useQuery)({
        queryKey: ['kpis', window],
        queryFn: function () { return client_1.apiKPIs.get(window); },
        refetchInterval: 60000,
    });
}

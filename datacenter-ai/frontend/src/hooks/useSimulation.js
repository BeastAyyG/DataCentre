"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.useSimulation = useSimulation;
var react_query_1 = require("@tanstack/react-query");
var client_1 = require("@/api/client");
var useSimulationStore_1 = require("@/store/useSimulationStore");
function useSimulation() {
    var setResult = (0, useSimulationStore_1.useSimulationStore)(function (s) { return s.setResult; });
    var setRunning = (0, useSimulationStore_1.useSimulationStore)(function (s) { return s.setRunning; });
    return (0, react_query_1.useMutation)({
        mutationFn: client_1.apiSimulation.whatIf,
        onMutate: function () { return setRunning(true); },
        onSuccess: function (data) {
            setResult(data);
            setRunning(false);
        },
        onError: function () { return setRunning(false); },
    });
}

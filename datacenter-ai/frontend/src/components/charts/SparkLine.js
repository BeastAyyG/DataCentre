"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.SparkLine = SparkLine;
var recharts_1 = require("recharts");
function SparkLine(_a) {
    var data = _a.data, _b = _a.color, color = _b === void 0 ? '#3b82f6' : _b, _c = _a.height, height = _c === void 0 ? 32 : _c;
    var chartData = data.map(function (v, i) { return ({ i: i, v: v }); });
    return (<recharts_1.ResponsiveContainer width/>);
    "100%" height={height}>
        < recharts_1.LineChart;
    data = { chartData: chartData } >
        <recharts_1.Line type/>;
    "monotone" dataKey="v" stroke={color} strokeWidth={1.5} dot={false} />;
    recharts_1.LineChart >
    ;
    recharts_1.ResponsiveContainer >
    ;
    ;
}

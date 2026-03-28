"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.TimeSeriesChart = TimeSeriesChart;
var recharts_1 = require("recharts");
var date_fns_1 = require("date-fns");
function TimeSeriesChart(_a) {
    var data = _a.data, _b = _a.dataKey1, dataKey1 = _b === void 0 ? 'baseline' : _b, _c = _a.dataKey2, dataKey2 = _c === void 0 ? 'scenario' : _c, _d = _a.color1, color1 = _d === void 0 ? '#3b82f6' : _d, _e = _a.color2, color2 = _e === void 0 ? '#22c55e' : _e, _f = _a.height, height = _f === void 0 ? 240 : _f, yLabel = _a.yLabel;
    return (<recharts_1.ResponsiveContainer width/>);
    "100%" height={height}>
        < recharts_1.AreaChart;
    data = { data: data };
    margin = {};
    {
        top: 8, right;
        8, left;
        0, bottom;
        0;
    }
}
 >
    <recharts_1.CartesianGrid strokeDasharray/>;
"3 3" stroke="#334155" />
    < recharts_1.XAxis;
dataKey = ;
"ts";
tickFormatter = {}(v);
(0, date_fns_1.format)(new Date(v), 'HH:mm');
stroke = ;
"#94a3b8";
fontSize = { 11:  }
    /  >
    <recharts_1.YAxis stroke/>;
"#94a3b8" fontSize={11} label={yLabel ? { value: yLabel, angle: -90, position: 'insideLeft', fill: '#94a3b8', fontSize: 10 } : undefined} />
    < recharts_1.Tooltip;
contentStyle = {};
{
    backgroundColor: '#1e293b', border;
    '1px solid #334155', borderRadius;
    '8px', fontSize;
    12;
}
labelFormatter = {}(v);
(0, date_fns_1.format)(new Date(v), 'MMM d, HH:mm');
/>
    < recharts_1.Area;
type = ;
"monotone" dataKey={dataKey1} stroke={color1} fill={color1} fillOpacity={0.2} strokeWidth={2} />;
{
    dataKey2 && <recharts_1.Area type/>;
    "monotone" dataKey={dataKey2} stroke={color2} fill={color2} fillOpacity={0.2} strokeWidth={2} />};
    recharts_1.AreaChart >
    ;
    recharts_1.ResponsiveContainer >
    ;
    ;
}

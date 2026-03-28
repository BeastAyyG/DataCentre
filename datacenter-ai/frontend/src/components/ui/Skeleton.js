"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.Skeleton = Skeleton;
exports.SkeletonCard = SkeletonCard;
exports.SkeletonTable = SkeletonTable;
exports.SkeletonAlertRow = SkeletonAlertRow;
function Skeleton(_a) {
    var _b = _a.className, className = _b === void 0 ? '' : _b;
    return (<div className={} nimate-pulse bg-slate-700 rounded/>);
}
aria - hidden;
"true"
    /  >
;
;
function SkeletonCard() {
    return (<div className/>);
    "bg-slate-800 rounded-lg border border-slate-700 p-4 space-y-3">
        < Skeleton;
    className = ;
    "h-4 w-24" />
        < Skeleton;
    className = ;
    "h-8 w-16" />
        < Skeleton;
    className = ;
    "h-3 w-32" />;
    div >
    ;
    ;
}
function SkeletonTable(_a) {
    var _b = _a.rows, rows = _b === void 0 ? 5 : _b, _c = _a.cols, cols = _c === void 0 ? 4 : _c;
    return (<div className/>);
    "space-y-2">;
    {
        Array.from({ length: rows }).map(function (_, r) { return (<div key={r} className/>); }, "flex gap-3">, { Array: Array, : .from({ length: cols }).map(function (_, c) { return (<Skeleton key={c} className/>); }, "h-6 flex-1" />) });
    }
    div >
    ;
}
div >
;
;
function SkeletonAlertRow() {
    return (<div className/>);
    "border border-slate-700 rounded-lg p-4 space-y-2">
        < div;
    className = ;
    "flex gap-2">
        < Skeleton;
    className = ;
    "h-5 w-16" />
        < Skeleton;
    className = ;
    "h-5 w-12" />
        < Skeleton;
    className = ;
    "h-5 w-20 flex-1" />;
    div >
        <Skeleton className/>;
    "h-4 w-full" />
        < Skeleton;
    className = ;
    "h-4 w-3/4" />;
    div >
    ;
    ;
}

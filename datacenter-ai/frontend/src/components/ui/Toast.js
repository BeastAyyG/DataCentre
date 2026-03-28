"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ToastContainer = ToastContainer;
var useToast_1 = require("@/hooks/useToast");
var variantStyles = {
    success: 'bg-green-900 border-green-600 text-green-200',
    error: 'bg-red-900 border-red-600 text-red-200',
    info: 'bg-blue-900 border-blue-600 text-blue-200',
};
var variantIcons = {
    success: '✓',
    error: '✕',
    info: 'ℹ',
};
function ToastItem(_a) {
    var toast = _a.toast;
    return (<div className={lex} items-center gap-3 px-4 py-3 rounded-lg border shadow-lg text-sm font-medium/>);
}
role = ;
"alert"
    >
        <span className/>;
"text-base">{variantIcons[toast.variant]}</span>
    < span > { toast: toast, : .message };
span >
;
div >
;
;
function ToastContainer() {
    var toasts = (0, useToast_1.useToasts)();
    if (toasts.length === 0)
        return null;
    return (<div className/>);
    "fixed bottom-4 right-4 z-50 flex flex-col gap-2 items-end max-w-sm">;
    {
        toasts.map(function (t) { return (<ToastItem key={t.id} toast={t}/>); });
    }
    div >
    ;
    ;
}

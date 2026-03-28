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
exports.toast = void 0;
exports.useToasts = useToasts;
var react_1 = require("react");
var _toasts = [];
var _listeners = [];
function notify() {
    _listeners.forEach(function (l) { return l(__spreadArray([], _toasts, true)); });
}
exports.toast = {
    show: function (message, variant) {
        if (variant === void 0) { variant = 'info'; }
        var id = Math.random().toString(36).slice(2);
        _toasts = __spreadArray(__spreadArray([], _toasts, true), [{ id: id, message: message, variant: variant }], false);
        notify();
        setTimeout(function () {
            _toasts = _toasts.filter(function (t) { return t.id !== id; });
            notify();
        }, 4000);
    },
    success: function (message) { return exports.toast.show(message, 'success'); },
    error: function (message) { return exports.toast.show(message, 'error'); },
    info: function (message) { return exports.toast.show(message, 'info'); },
};
function useToasts() {
    var _a = (0, react_1.useState)([]), toasts = _a[0], setToasts = _a[1];
    var ref = (0, react_1.useRef)(function (t) { return setToasts(t); });
    (0, react_1.useEffect)(function () {
        _listeners.push(ref.current);
        return function () {
            _listeners.splice(_listeners.indexOf(ref.current), 1);
        };
    }, []);
    return toasts;
}

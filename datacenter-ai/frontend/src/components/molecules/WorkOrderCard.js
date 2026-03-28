"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.WorkOrderCard = WorkOrderCard;
var Badge_1 = require("@/components/ui/Badge");
var Button_1 = require("@/components/ui/Button");
function WorkOrderCard(_a) {
    var wo = _a.wo, onUpdateStep = _a.onUpdateStep, onComplete = _a.onComplete;
    var steps = wo.steps || [];
    var completedSteps = steps.filter(function (s) { return s.done; }).length;
    var priorityVariant = wo.priority === 'critical' ? 'critical' : wo.priority === 'high' ? 'warning' : 'default';
    return (<div className/>);
    "border border-slate-700 rounded-lg p-4 mb-3 bg-slate-800">
        < div;
    className = ;
    "flex items-start justify-between mb-3">
        < div >
        <div className/>;
    "flex items-center gap-2 mb-1">
        < Badge_1.Badge;
    variant = { priorityVariant: priorityVariant } > { wo: wo, : .priority.toUpperCase() };
    Badge_1.Badge >
        <Badge_1.Badge variant={wo.status === 'completed' ? 'healthy' : wo.status === 'in_progress' ? 'at_risk' : 'default'}>{wo.status}</Badge_1.Badge>;
    div >
        <h4 className/>;
    "text-sm font-semibold text-white">{wo.title}</h4>;
    {
        wo.description && <p className/>;
        "text-xs text-slate-400 mt-1">{wo.description}</p>};
        div >
            { wo: wo, : .estimated_saving_usd != null && (<div className/>),
                "text-xs text-green-400 font-semibold"> saved</p>: , div: div } >
        ;
    }
    div >
        { steps: steps, : .length > 0 && (<div className/>), Progress: Progress, span: span } >
        <span>{completedSteps}/{steps.length} steps</span>;
    div >
        <div className/>;
    "w-full bg-slate-700 rounded-full h-1.5">
        < div;
    className = ;
    "bg-green-500 h-1.5 rounded-full transition-all";
    style = {};
    {
        width: $;
        {
            (completedSteps / steps.length) * 100;
        }
         % ;
    }
}
/>;
div >
    <div className/>;
"mt-2 space-y-1">;
{
    steps.map(function (step) { return (<div key={step.step} className/>); }, "flex items-center gap-2 text-xs">
        < input, type = , "checkbox", checked = { step: step, : .done }, onChange = {}(e), onUpdateStep(wo.id, step.step - 1, e.target.checked));
}
className = ;
"rounded bg-slate-700 border-slate-500";
disabled = { wo: wo, : .status === 'completed' }
    /  >
    <span className={step.done ? 'text-slate-500 line-through' : 'text-slate-300'}>{step.description}</span>;
div >
;
div >
;
div >
;
<div className/>;
"flex items-center justify-between">
    < div;
className = ;
"text-xs text-slate-500">;
{
    wo.owner && <span>Owner: {wo.owner}</span>;
}
<span className/>;
"ml-3">{format(new Date(wo.created_at), 'MMM d, HH:mm')}</span>;
div >
    { wo: wo, : .status !== 'completed' && (<Button_1.Button variant/>), "accept" size="sm" onClick={() => onComplete(wo.id)}>Mark Complete</Button>:  };
div >
;
div >
;
;

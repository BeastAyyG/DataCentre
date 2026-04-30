"""Plotly Dash Monitoring Dashboard.

Live monitoring dashboard for the DataCentre AI platform.  Shows per-node
CPU, temperature, network throughput and power metrics with 2-second
auto-refresh, plus a running cost total from the Cost Simulation Engine.

Usage::

    python -m datacenter_ai.dashboard.app
    # or
    python datacenter-ai/dashboard/app.py

The dashboard polls the FastAPI backend at ``BACKEND_URL`` (default
``http://localhost:8000/api/v1``).
"""

import os
import json
import logging
import urllib.request
import urllib.error
from datetime import datetime

import dash
from dash import dcc, html, Input, Output, callback
import plotly.graph_objects as go
from plotly.subplots import make_subplots

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000/api/v1")
REFRESH_INTERVAL_MS = 2_000  # 2 seconds
MAX_HISTORY = 30              # data-points to show in time-series charts

# In-memory rolling history: device_id → list of reading dicts
_history: dict = {}


# ---------------------------------------------------------------------------
# Data fetching helpers
# ---------------------------------------------------------------------------


def _fetch(path: str, timeout: int = 4) -> dict | list | None:
    """Make a GET request to the backend and return parsed JSON.

    Args:
        path: API path relative to ``BACKEND_URL``.
        timeout: Request timeout in seconds.

    Returns:
        Parsed response body, or ``None`` on error.
    """
    url = f"{BACKEND_URL}{path}"
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            return json.loads(resp.read().decode())
    except Exception as exc:
        logger.debug("Dashboard fetch error for %s: %s", url, exc)
        return None


def _fetch_devices() -> list:
    """Return the list of device objects from the backend."""
    result = _fetch("/devices")
    if isinstance(result, list):
        return result
    return []


def _fetch_kpis() -> dict:
    """Return the current KPI snapshot."""
    result = _fetch("/kpis")
    if isinstance(result, dict):
        return result
    return {}


def _fetch_cost_summary() -> dict:
    """Return the cost-engine running totals."""
    result = _fetch("/cost/summary")
    if isinstance(result, dict):
        return result
    return {}


def _fetch_ids_status() -> dict:
    """Return the Network IDS status."""
    result = _fetch("/cyber/ids/status")
    if isinstance(result, dict):
        return result
    return {}


# ---------------------------------------------------------------------------
# App layout
# ---------------------------------------------------------------------------

app = dash.Dash(
    __name__,
    title="DataCentre AI Dashboard",
    update_title=None,
)

app.layout = html.Div(
    style={"fontFamily": "Arial, sans-serif", "backgroundColor": "#0d1117", "color": "#c9d1d9", "padding": "20px"},
    children=[
        # ── Header ──────────────────────────────────────────────────────
        html.Div(
            style={"display": "flex", "justifyContent": "space-between", "alignItems": "center", "marginBottom": "20px"},
            children=[
                html.H1(
                    "🖥  DataCentre AI — Live Dashboard",
                    style={"color": "#58a6ff", "margin": 0, "fontSize": "24px"},
                ),
                html.Div(
                    id="last-updated",
                    style={"color": "#8b949e", "fontSize": "12px"},
                ),
            ],
        ),

        # ── KPI Banner ──────────────────────────────────────────────────
        html.Div(id="kpi-banner", style={"marginBottom": "20px"}),

        # ── Cost Banner ─────────────────────────────────────────────────
        html.Div(id="cost-banner", style={"marginBottom": "20px"}),

        # ── Per-node charts ─────────────────────────────────────────────
        dcc.Graph(id="metrics-chart", style={"height": "500px"}),

        # ── Network / IDS ───────────────────────────────────────────────
        dcc.Graph(id="network-chart", style={"height": "300px", "marginTop": "20px"}),

        # ── Auto-refresh interval ────────────────────────────────────────
        dcc.Interval(
            id="interval-component",
            interval=REFRESH_INTERVAL_MS,
            n_intervals=0,
        ),
    ],
)


# ---------------------------------------------------------------------------
# Callbacks
# ---------------------------------------------------------------------------


@callback(
    Output("kpi-banner", "children"),
    Output("cost-banner", "children"),
    Output("metrics-chart", "figure"),
    Output("network-chart", "figure"),
    Output("last-updated", "children"),
    Input("interval-component", "n_intervals"),
)
def refresh_dashboard(n_intervals: int):
    """Main refresh callback — fetches live data and rebuilds all chart figures.

    Args:
        n_intervals: Monotonically-increasing trigger counter from the interval.

    Returns:
        Tuple of (kpi_banner, cost_banner, metrics_figure, network_figure, timestamp_str).
    """
    # -- KPI banner ----------------------------------------------------------
    kpis = _fetch_kpis()
    kpi_cards = _build_kpi_banner(kpis)

    # -- Cost banner ---------------------------------------------------------
    cost = _fetch_cost_summary()
    cost_banner = _build_cost_banner(cost)

    # -- Device metrics ------------------------------------------------------
    devices = _fetch_devices()
    _update_history(devices)
    metrics_fig = _build_metrics_figure()

    # -- Network chart -------------------------------------------------------
    network_fig = _build_network_figure()

    timestamp = f"Last updated: {datetime.utcnow().strftime('%H:%M:%S')} UTC"
    return kpi_cards, cost_banner, metrics_fig, network_fig, timestamp


# ---------------------------------------------------------------------------
# Helper builders
# ---------------------------------------------------------------------------


def _build_kpi_banner(kpis: dict) -> html.Div:
    """Build the KPI summary card strip.

    Args:
        kpis: KPI snapshot dict from the backend.

    Returns:
        Dash html.Div containing KPI cards.
    """
    card_style = {
        "backgroundColor": "#161b22",
        "borderRadius": "8px",
        "padding": "15px 20px",
        "minWidth": "150px",
        "textAlign": "center",
        "border": "1px solid #30363d",
    }
    label_style = {"color": "#8b949e", "fontSize": "12px", "marginBottom": "5px"}
    value_style = {"color": "#58a6ff", "fontSize": "22px", "fontWeight": "bold"}

    cards = [
        _kpi_card("PUE", f"{kpis.get('pue', '—')}", card_style, label_style, value_style),
        _kpi_card("Power (kWh)", f"{kpis.get('total_power_kwh', '—')}", card_style, label_style, value_style),
        _kpi_card("Cooling (kWh)", f"{kpis.get('cooling_power_kwh', '—')}", card_style, label_style, value_style),
        _kpi_card("Cost Savings", f"${kpis.get('cost_savings_usd', 0):.2f}", card_style, label_style, value_style),
        _kpi_card("Critical Alerts", str(kpis.get("active_critical_alerts", 0)),
                  {**card_style, "borderColor": "#da3633"}, label_style,
                  {**value_style, "color": "#f85149"}),
        _kpi_card("Warnings", str(kpis.get("active_warning_alerts", 0)),
                  {**card_style, "borderColor": "#d29922"}, label_style,
                  {**value_style, "color": "#e3b341"}),
    ]
    return html.Div(
        cards,
        style={"display": "flex", "gap": "15px", "flexWrap": "wrap"},
    )


def _kpi_card(label: str, value: str, card_style: dict, label_style: dict, value_style: dict) -> html.Div:
    """Create a single KPI card component.

    Args:
        label: Card label text.
        value: Displayed metric value.
        card_style: CSS style dict for the card container.
        label_style: CSS style dict for the label.
        value_style: CSS style dict for the value.

    Returns:
        html.Div card component.
    """
    return html.Div(
        [
            html.Div(label, style=label_style),
            html.Div(value, style=value_style),
        ],
        style=card_style,
    )


def _build_cost_banner(cost: dict) -> html.Div:
    """Build the running cost summary strip.

    Args:
        cost: Cost engine summary dict from the backend.

    Returns:
        Dash html.Div with cost summary.
    """
    card_style = {
        "backgroundColor": "#1a1f2e",
        "borderRadius": "8px",
        "padding": "10px 18px",
        "border": "1px solid #1f6feb",
        "display": "flex",
        "gap": "30px",
        "alignItems": "center",
        "flexWrap": "wrap",
    }
    item_style = {"display": "flex", "flexDirection": "column", "alignItems": "center"}
    label_style = {"color": "#8b949e", "fontSize": "11px"}
    value_style = {"color": "#3fb950", "fontSize": "18px", "fontWeight": "bold"}

    return html.Div(
        [
            html.Div("💡 Cost Engine", style={"color": "#58a6ff", "fontWeight": "bold", "marginRight": "10px"}),
            html.Div([
                html.Div("Total kWh", style=label_style),
                html.Div(f"{cost.get('total_kwh', 0):.4f}", style=value_style),
            ], style=item_style),
            html.Div([
                html.Div("Total Cost", style=label_style),
                html.Div(f"${cost.get('total_cost_usd', 0):.4f}", style=value_style),
            ], style=item_style),
            html.Div([
                html.Div("Savings kWh", style=label_style),
                html.Div(f"{cost.get('savings_kwh', 0):.4f}", style={**value_style, "color": "#58a6ff"}),
            ], style=item_style),
            html.Div([
                html.Div("Savings USD", style=label_style),
                html.Div(f"${cost.get('savings_usd', 0):.4f}", style={**value_style, "color": "#58a6ff"}),
            ], style=item_style),
            html.Div([
                html.Div("Agent Decisions", style=label_style),
                html.Div(str(cost.get("decision_count", 0)), style={**value_style, "color": "#e3b341"}),
            ], style=item_style),
        ],
        style=card_style,
    )


def _update_history(devices: list) -> None:
    """Append the latest device readings to the rolling in-memory history.

    Args:
        devices: List of device dicts from the backend ``/devices`` endpoint.
    """
    for dev in devices:
        did = dev.get("id")
        if not did:
            continue
        if did not in _history:
            _history[did] = []
        point = {
            "ts": datetime.utcnow().isoformat(),
            "cpu": dev.get("cpu_util_pct") or 0,
            "temp": dev.get("inlet_temp_c") or 0,
            "power": dev.get("power_kw") or 0,
            "network": (dev.get("network_bps") or 0) / 1e6,  # → Mbps
            "name": dev.get("name", did),
        }
        _history[did].append(point)
        # Keep rolling window
        if len(_history[did]) > MAX_HISTORY:
            _history[did] = _history[did][-MAX_HISTORY:]


def _build_metrics_figure() -> go.Figure:
    """Build a 2×2 subplot figure for CPU, temperature, power and network.

    Returns:
        A Plotly Figure with four subplots, one per metric.
    """
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=("CPU Utilisation (%)", "Inlet Temperature (°C)",
                        "Power Consumption (kW)", "Network (Mbps)"),
        vertical_spacing=0.12,
        horizontal_spacing=0.08,
    )

    colours = ["#58a6ff", "#3fb950", "#f78166", "#e3b341", "#79c0ff", "#56d364"]

    for i, (device_id, readings) in enumerate(_history.items()):
        if not readings:
            continue
        colour = colours[i % len(colours)]
        name = readings[-1]["name"]
        xs = [r["ts"] for r in readings]

        fig.add_trace(go.Scatter(x=xs, y=[r["cpu"] for r in readings],
                                 name=name, line=dict(color=colour), showlegend=True), row=1, col=1)
        fig.add_trace(go.Scatter(x=xs, y=[r["temp"] for r in readings],
                                 name=name, line=dict(color=colour), showlegend=False), row=1, col=2)
        fig.add_trace(go.Scatter(x=xs, y=[r["power"] for r in readings],
                                 name=name, line=dict(color=colour), showlegend=False), row=2, col=1)
        fig.add_trace(go.Scatter(x=xs, y=[r["network"] for r in readings],
                                 name=name, line=dict(color=colour), showlegend=False), row=2, col=2)

    fig.update_layout(
        paper_bgcolor="#0d1117",
        plot_bgcolor="#161b22",
        font=dict(color="#c9d1d9"),
        legend=dict(
            bgcolor="#161b22",
            bordercolor="#30363d",
            borderwidth=1,
            font=dict(size=10),
        ),
        margin=dict(l=50, r=20, t=40, b=40),
    )
    fig.update_xaxes(showgrid=True, gridcolor="#21262d")
    fig.update_yaxes(showgrid=True, gridcolor="#21262d")
    return fig


def _build_network_figure() -> go.Figure:
    """Build a bar chart of current network throughput per device.

    Returns:
        A Plotly Figure bar chart.
    """
    device_names = []
    network_values = []

    for device_id, readings in _history.items():
        if readings:
            device_names.append(readings[-1]["name"])
            network_values.append(readings[-1]["network"])

    fig = go.Figure(go.Bar(
        x=device_names,
        y=network_values,
        marker_color="#58a6ff",
        text=[f"{v:.2f}" for v in network_values],
        textposition="outside",
    ))
    fig.update_layout(
        title="Current Network Throughput per Device (Mbps)",
        paper_bgcolor="#0d1117",
        plot_bgcolor="#161b22",
        font=dict(color="#c9d1d9"),
        yaxis_title="Mbps",
        margin=dict(l=50, r=20, t=50, b=40),
    )
    fig.update_yaxes(showgrid=True, gridcolor="#21262d")
    return fig


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    port = int(os.environ.get("DASHBOARD_PORT", 8050))
    debug = os.environ.get("DASHBOARD_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug)

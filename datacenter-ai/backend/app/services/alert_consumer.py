import logging
import uuid
from datetime import datetime
from ..core.event_bus import event_bus
from ..core.event_types import DeviceRiskEvent, AlertTriggeredEvent
from ..db.session import get_db_context
from ..models.anomaly_alert import AnomalyAlert
from ..models.device import Device

logger = logging.getLogger(__name__)

_ACTION_TEMPLATES = {
    "inlet_temp_c": [
        "Check server fans in {device_id} for blockage or failure",
        "Verify hot/cold aisle containment is intact",
        "Reduce workload on servers in this rack",
        "Schedule preventive maintenance on rack cooling",
    ],
    "power_kw": [
        "Inspect PDU load distribution in {device_id}",
        "Check for failed power modules",
        "Verify UPS battery status",
        "Reduce non-critical load to free power headroom",
    ],
    "default": [
        "Run diagnostics on {device_id}",
        "Review recent configuration changes",
        "Check physical infrastructure for anomalies",
        "Escalate to infrastructure team if issue persists",
    ],
}

# Cyber action templates mapped by threat type
_CYBER_ACTION_TEMPLATES = {
    "ddos": [
        "Block source IPs at firewall and enable rate limiting",
        "Activate DDoS mitigation service",
        "Scale network capacity to absorb traffic spike",
    ],
    "intrusion": [
        "Isolate affected systems and force password reset",
        "Review and block suspicious IP addresses",
        "Enable enhanced monitoring on affected accounts",
    ],
    "ransomware": [
        "Immediately isolate infected systems",
        "Initiate backup restoration protocol",
        "Notify security operations center",
    ],
    "port_scan": [
        "Block source IP at firewall",
        "Enable IDS/IPS alerts for targeted ports",
        "Review firewall rules for unused ports",
    ],
    "exfiltration": [
        "Block external data connections immediately",
        "Investigate data loss scope",
        "Notify data protection officer",
    ],
    "compromise": [
        "Isolate all affected systems immediately",
        "Begin incident response protocol",
        "Preserve evidence for forensic analysis",
    ],
    "default": [
        "Investigate the security incident",
        "Isolate affected systems",
        "Notify security operations center",
    ],
}


class AlertConsumer:
    """EventBus subscriber — creates AnomalyAlert rows when RiskScorer emits critical/at-risk events."""

    def __init__(self):
        event_bus.subscribe("DeviceRiskEvent", self.on_device_risk)

    async def on_device_risk(self, event: DeviceRiskEvent) -> None:
        try:
            with get_db_context() as db:
                # Check if there's a cyber anomaly contributing factor
                is_cyber = event.contributing_factors.get("cyber_anomaly", False)

                # Only alert for at_risk or critical
                if event.risk_label == "healthy":
                    return

                # Check if there's already an open alert for this device
                existing = (
                    db.query(AnomalyAlert)
                    .filter(
                        AnomalyAlert.device_id == event.device_id,
                        AnomalyAlert.status.in_(["open", "acknowledged"]),
                    )
                    .first()
                )
                if existing:
                    # Update existing
                    existing.risk_score = event.risk_score
                    existing.anomaly_score = event.anomaly_score
                    existing.forecast_deviation = event.forecast_deviation
                    db.commit()
                    return

                # Determine affected metric and action
                cf = event.contributing_factors

                if is_cyber:
                    # Cyber threat handling
                    threat_type = cf.get("threat_type", "default")
                    templates = _CYBER_ACTION_TEMPLATES.get(
                        threat_type, _CYBER_ACTION_TEMPLATES["default"]
                    )
                    action = templates[0].format(device_id=event.device_id)

                    reason = (
                        f"CYBER THREAT DETECTED: {threat_type.upper()} attack detected. "
                        f"Risk score {event.risk_score:.1f}/100 ({event.risk_label}). "
                        f"AI confidence: {cf.get('cyber_score', event.anomaly_score * 100):.1f}%. "
                        f"Immediate action required to prevent data breach or service disruption."
                    )
                    impact = (
                        f"Critical: {threat_type.upper()} attack in progress. "
                        f"Potential data loss, service outage, or compliance violation. "
                        f"Estimated impact: ${event.risk_score * 100:.0f} per minute if unresolved."
                    )
                    severity = "critical"
                    affected_metric = "cyber_threat"
                else:
                    # Standard thermal/environmental handling
                    if cf.get("anomaly_confidence", 0) > cf.get(
                        "forecast_deviation", 0
                    ):
                        metric = "inlet_temp_c"
                    else:
                        metric = "power_kw"

                    templates = _ACTION_TEMPLATES.get(
                        metric, _ACTION_TEMPLATES["default"]
                    )
                    action = templates[0].format(device_id=event.device_id)

                    reason = (
                        f"Risk score {event.risk_score:.1f}/100 ({event.risk_label}) driven by "
                        f"anomaly_confidence={event.contributing_factors.get('anomaly_confidence', 0):.3f}, "
                        f"forecast_deviation={event.contributing_factors.get('forecast_deviation', 0):.3f}. "
                        f"Recommend immediate inspection of {metric}."
                    )
                    impact = (
                        f"Estimated {event.risk_score * 0.5:.0f} minutes downtime if unresolved. "
                        f"Energy inefficiency of ~{event.risk_score * 0.1:.1f}% above baseline."
                    )
                    severity = (
                        "critical" if event.risk_label == "critical" else "warning"
                    )
                    affected_metric = metric

                alert = AnomalyAlert(
                    id=str(uuid.uuid4()),
                    device_id=event.device_id,
                    severity=severity,
                    status="open",
                    anomaly_score=event.anomaly_score,
                    forecast_deviation=event.forecast_deviation,
                    risk_score=event.risk_score,
                    affected_metric=affected_metric,
                    reason=reason,
                    impact_estimate=impact,
                    recommended_action=action,
                    triggered_at=datetime.utcnow(),
                )
                db.add(alert)
                db.commit()

                logger.info(
                    "Alert created: %s for device %s (severity=%s, risk=%.1f, cyber=%s)",
                    alert.id,
                    event.device_id,
                    alert.severity,
                    event.risk_score,
                    is_cyber,
                )

                # Push WebSocket notification
                ws_event = AlertTriggeredEvent(
                    alert_id=alert.id,
                    device_id=event.device_id,
                    severity=alert.severity,
                    reason=reason,
                    impact_estimate=impact,
                    recommended_action=action,
                    risk_score=event.risk_score,
                )
                await event_bus.publish(ws_event)

        except Exception as e:
            logger.error("AlertConsumer error: %s", e)


alert_consumer = AlertConsumer()

import logging
from ..core.event_bus import event_bus
from ..core.event_types import DeviceRiskEvent
from ..ml.ml_service import ml_service
from .cyber_simulator import cyber_simulator

logger = logging.getLogger(__name__)


class MLConsumer:
    """EventBus subscriber — runs ML inference when triggered by scheduler."""

    def __init__(self):
        event_bus.subscribe("DeviceRiskEvent", self._nop)  # register only

    async def _nop(self, event: DeviceRiskEvent) -> None:
        pass  # Events are processed by scheduler, this is just for bus registration

    def trigger_inference(self) -> list:
        """Called by the scheduler on each interval."""
        try:
            # Run base ML inference
            results = ml_service.run_inference()
            
            # If cyber simulation is running, factor in cyber anomalies
            if cyber_simulator.is_running:
                cyber_results = self._run_cyber_inference()
                results = self._combine_results(results, cyber_results)
            
            return results
        except Exception as e:
            logger.error("ML inference error: %s", e)
            return []

    def _run_cyber_inference(self) -> list:
        """Run cyber anomaly inference for devices affected by active scenario."""
        from ..ml.cyber_anomaly_detector import cyber_anomaly_detector
        from ..db.session import get_db_context
        from ..models.device import Device
        
        cyber_results = []
        
        with get_db_context() as db:
            devices = db.query(Device).all()
            
            for device in devices:
                # Get anomaly readings from the cyber simulator
                anomaly_data = cyber_simulator.get_anomaly_reading(device.id)
                
                if not anomaly_data:
                    continue
                
                # Compute cyber anomaly score
                network_bps = anomaly_data.get("network_bps", 0)
                cpu_util = anomaly_data.get("cpu_util_pct", 0)
                power_kw = anomaly_data.get("power_kw", 0)
                airflow = anomaly_data.get("airflow_cfm", 0)
                
                if network_bps > 0 or cpu_util > 0:
                    cyber_score = cyber_anomaly_detector.get_cyber_risk_score(
                        network_bps=network_bps,
                        cpu_util_pct=cpu_util,
                        power_kw=power_kw,
                        airflow_cfm=airflow,
                    )
                    
                    # Get base risk from ML
                    base_score = device.current_risk_score or 0
                    
                    # Combine: cyber score boosts the risk significantly during active threat
                    combined_score = max(base_score, cyber_score)
                    
                    if combined_score > 35:  # At risk or critical
                        cyber_results.append({
                            "device_id": device.id,
                            "risk_score": combined_score,
                            "risk_label": "critical" if combined_score > 65 else "at_risk",
                            "anomaly_score": cyber_score / 100,
                            "forecast_deviation": 0,
                            "contributing_factors": {
                                "cyber_anomaly": True,
                                "cyber_score": round(cyber_score, 2),
                                "threat_type": cyber_simulator.active_scenario.get("threat_type") if cyber_simulator.active_scenario else None,
                            },
                        })
                        
                        logger.info(
                            f"Cyber anomaly detected: device={device.id}, "
                            f"cyber_score={cyber_score:.1f}, combined={combined_score:.1f}"
                        )
        
        return cyber_results

    def _combine_results(self, base_results: list, cyber_results: list) -> list:
        """Combine base ML results with cyber anomaly results."""
        # Create a map by device_id
        result_map = {r["device_id"]: r for r in base_results}
        
        # Override/add cyber results
        for cr in cyber_results:
            device_id = cr["device_id"]
            if device_id in result_map:
                # Combine - take max of base and cyber
                existing = result_map[device_id]
                if cr["risk_score"] > existing.get("risk_score", 0):
                    result_map[device_id] = cr
            else:
                result_map[device_id] = cr
        
        return list(result_map.values())


ml_consumer = MLConsumer()

import asyncio
import logging
import random
import uuid
import json
from datetime import datetime
from typing import Dict, List, Optional, Callable

logger = logging.getLogger(__name__)

# Threat definitions with phases and behaviors
THREAT_DEFINITIONS = {
    "ddos": {
        "name": "DDoS Attack",
        "description": "Distributed Denial of Service attack flooding network resources",
        "severity_levels": {
            "low": {"network_spike": 3.0, "duration_phase_sec": 15},
            "medium": {"network_spike": 7.0, "duration_phase_sec": 12},
            "high": {"network_spike": 15.0, "duration_phase_sec": 10},
            "critical": {"network_spike": 30.0, "duration_phase_sec": 8},
        },
        "phases": ["recon", "exploit", "action", "impact"],
        "affected_metrics": ["network_bps", "cpu_util_pct", "power_kw"],
        "indicators": [
            {"type": "network_spike", "threshold": 2.0, "description": "Abnormal network throughput spike"},
            {"type": "latency", "threshold": 500, "description": "High network latency"},
            {"type": "packet_loss", "threshold": 0.05, "description": "Packet loss detected"},
        ],
        "recommended_action": "Block source IPs at firewall and enable rate limiting",
    },
    "intrusion": {
        "name": "Intrusion Attempt",
        "description": "Unauthorized access attempt exploiting system vulnerabilities",
        "severity_levels": {
            "low": {"auth_fail_rate": 5.0, "duration_phase_sec": 20},
            "medium": {"auth_fail_rate": 15.0, "duration_phase_sec": 15},
            "high": {"auth_fail_rate": 30.0, "duration_phase_sec": 12},
            "critical": {"auth_fail_rate": 50.0, "duration_phase_sec": 8},
        },
        "phases": ["recon", "exploit", "action", "impact"],
        "affected_metrics": ["cpu_util_pct", "network_bps", "power_kw"],
        "indicators": [
            {"type": "auth_failures", "threshold": 3, "description": "Multiple failed authentication attempts"},
            {"type": "unusual_port", "threshold": 1, "description": "Access to unusual port detected"},
            {"type": "privilege_escalation", "threshold": 1, "description": "Potential privilege escalation attempt"},
        ],
        "recommended_action": "Isolate affected systems and force password reset for compromised accounts",
    },
    "ransomware": {
        "name": "Ransomware Attack",
        "description": "Malicious encryption of data demanding ransom",
        "severity_levels": {
            "low": {"encryption_rate": 0.1, "duration_phase_sec": 30},
            "medium": {"encryption_rate": 0.3, "duration_phase_sec": 25},
            "high": {"encryption_rate": 0.6, "duration_phase_sec": 20},
            "critical": {"encryption_rate": 1.0, "duration_phase_sec": 15},
        },
        "phases": ["recon", "exploit", "action", "impact"],
        "affected_metrics": ["cpu_util_pct", "power_kw", "airflow_cfm"],
        "indicators": [
            {"type": "write_spike", "threshold": 10000, "description": "Abnormal disk write activity"},
            {"type": "crypto_process", "threshold": 1, "description": "Cryptocurrency mining process detected"},
            {"type": "file_modification", "threshold": 100, "description": "Rapid file modifications"},
        ],
        "recommended_action": "Immediately isolate infected systems and initiate backup restoration",
    },
    "port_scan": {
        "name": "Port Scan Attack",
        "description": "Systematic scanning of network ports to identify vulnerabilities",
        "severity_levels": {
            "low": {"scan_rate": 10.0, "duration_phase_sec": 25},
            "medium": {"scan_rate": 50.0, "duration_phase_sec": 20},
            "high": {"scan_rate": 100.0, "duration_phase_sec": 15},
            "critical": {"scan_rate": 200.0, "duration_phase_sec": 10},
        },
        "phases": ["recon", "exploit", "action", "impact"],
        "affected_metrics": ["network_bps", "cpu_util_pct"],
        "indicators": [
            {"type": "connection_pattern", "threshold": 20, "description": "Sequential port connection pattern"},
            {"type": "closed_port_rate", "threshold": 0.8, "description": "High rate of closed port responses"},
            {"type": "scan_signature", "threshold": 1, "description": "Port scan signature detected"},
        ],
        "recommended_action": "Block source IP at firewall and enable IDS/IPS alerts",
    },
    "exfiltration": {
        "name": "Data Exfiltration",
        "description": "Unauthorized transfer of sensitive data outside the network",
        "severity_levels": {
            "low": {"exfil_rate": 0.1, "duration_phase_sec": 40},
            "medium": {"exfil_rate": 0.3, "duration_phase_sec": 30},
            "high": {"exfil_rate": 0.6, "duration_phase_sec": 20},
            "critical": {"exfil_rate": 1.0, "duration_phase_sec": 15},
        },
        "phases": ["recon", "exploit", "action", "impact"],
        "affected_metrics": ["network_bps", "power_kw", "cpu_util_pct"],
        "indicators": [
            {"type": "outbound_traffic", "threshold": 2.0, "description": "Unusual outbound traffic volume"},
            {"type": "encrypted_channel", "threshold": 1, "description": "Encrypted tunnel detected"},
            {"type": "large_transfer", "threshold": 1000000, "description": "Large data transfer to external destination"},
        ],
        "recommended_action": "Block external connections and investigate data loss",
    },
    "compromise": {
        "name": "System Compromise",
        "description": "Full system compromise with lateral movement",
        "severity_levels": {
            "low": {"lateral_rate": 0.1, "duration_phase_sec": 45},
            "medium": {"lateral_rate": 0.3, "duration_phase_sec": 35},
            "high": {"lateral_rate": 0.6, "duration_phase_sec": 25},
            "critical": {"lateral_rate": 1.0, "duration_phase_sec": 15},
        },
        "phases": ["recon", "exploit", "action", "impact"],
        "affected_metrics": ["cpu_util_pct", "power_kw", "network_bps", "airflow_cfm"],
        "indicators": [
            {"type": "new_process", "threshold": 10, "description": "Unusual new process spawning"},
            {"type": "lateral_movement", "threshold": 1, "description": "Lateral movement detected"},
            {"type": "persistence", "threshold": 1, "description": "Persistence mechanism installed"},
        ],
        "recommended_action": "Isolate all affected systems immediately and begin incident response",
    },
}


class CyberSimulator:
    """Simulates cybersecurity threats for the datacenter AI platform.
    
    Generates realistic attack sequences with phases (recon -> exploit -> action -> impact)
    that produce observable anomalies in sensor metrics, triggering ML-based detection.
    """

    DEFAULT_TARGETS = ["RACK-A1", "RACK-A2", "RACK-B1", "RACK-B2", "PDU-1", "PDU-2", "CRAC-1", "CRAC-2"]
    
    SOURCE_IPS = [
        "185.220.101.42", "45.33.32.156", "104.131.0.69", "192.168.1.100",
        "10.0.0.50", "172.16.0.25", "203.0.113.50", "198.51.100.14",
    ]

    def __init__(self):
        self._running = False
        self._scenario_task: Optional[asyncio.Task] = None
        self._active_scenario: Optional[Dict] = None
        self._phase_callbacks: List[Callable] = []
        self._indicators_triggered: List[Dict] = []

    @property
    def is_running(self) -> bool:
        return self._running

    @property
    def active_scenario(self) -> Optional[Dict]:
        return self._active_scenario

    def get_available_threat_types(self) -> List[str]:
        return list(THREAT_DEFINITIONS.keys())

    def get_available_scenarios(self) -> List[Dict]:
        """Return list of available scenario definitions for API."""
        scenarios = []
        for threat_type, definition in THREAT_DEFINITIONS.items():
            for severity in ["low", "medium", "high", "critical"]:
                scenarios.append({
                    "threat_type": threat_type,
                    "name": f"{definition['name']} ({severity.upper()})",
                    "severity": severity,
                    "description": definition["description"],
                    "recommended_action": definition["recommended_action"],
                })
        return scenarios

    async def start_scenario(
        self,
        threat_type: str,
        severity: str = "medium",
        target_device_id: Optional[str] = None,
        intensity: float = 0.5,
    ) -> Dict:
        """Start a new cyber attack scenario."""
        if self._running:
            await self.stop_scenario()

        if threat_type not in THREAT_DEFINITIONS:
            raise ValueError(f"Unknown threat type: {threat_type}. Available: {self.get_available_threat_types()}")

        if severity not in ["low", "medium", "high", "critical"]:
            raise ValueError(f"Invalid severity: {severity}")

        target = target_device_id or random.choice(self.DEFAULT_TARGETS)
        scenario_id = str(uuid.uuid4())
        threat_def = THREAT_DEFINITIONS[threat_type]
        
        self._active_scenario = {
            "id": scenario_id,
            "threat_type": threat_type,
            "name": threat_def["name"],
            "severity": severity,
            "target_device_id": target,
            "intensity": intensity,
            "source_ip": random.choice(self.SOURCE_IPS),
            "status": "active",
            "started_at": datetime.utcnow(),
            "current_phase": "recon",
            "phase_index": 0,
            "phases": threat_def["phases"],
            "affected_metrics": threat_def["affected_metrics"],
            "indicators": threat_def["indicators"],
            "recommended_action": threat_def["recommended_action"],
            "description": threat_def["description"],
            "affected_devices": [],
            "detected": False,
            "detected_at": None,
            "detection_latency_sec": None,
        }
        
        self._running = True
        self._indicators_triggered = []
        
        # Start scenario loop
        self._scenario_task = asyncio.create_task(self._run_scenario())
        
        logger.info(
            f"Cyber scenario started: {threat_type}/{severity} targeting {target} "
            f"(scenario_id={scenario_id})"
        )
        
        return self._active_scenario

    async def stop_scenario(self) -> Optional[Dict]:
        """Stop the current scenario."""
        if not self._running:
            return None

        self._running = False
        
        if self._scenario_task:
            self._scenario_task.cancel()
            try:
                await self._scenario_task
            except asyncio.CancelledError:
                pass

        if self._active_scenario:
            self._active_scenario["status"] = "contained"
            self._active_scenario["ended_at"] = datetime.utcnow()
            
            # Calculate detection latency if detected
            if self._active_scenario.get("detected_at"):
                delta = self._active_scenario["detected_at"] - self._active_scenario["started_at"]
                self._active_scenario["detection_latency_sec"] = delta.total_seconds()
            
            result = self._active_scenario.copy()
            logger.info(f"Cyber scenario stopped: {result['id']}")
            
            self._active_scenario = None
            self._indicators_triggered = []
            
            return result
        
        return None

    async def get_simulation_state(self) -> Dict:
        """Get current simulation state for dashboard."""
        if not self._active_scenario:
            return {
                "running": False,
                "active_scenario_id": None,
                "active_threat": None,
                "affected_devices": [],
                "attack_phase": "none",
                "indicators_triggered": [],
                "elapsed_sec": 0.0,
            }

        elapsed = (datetime.utcnow() - self._active_scenario["started_at"]).total_seconds()
        
        return {
            "running": self._running,
            "active_scenario_id": self._active_scenario["id"],
            "active_threat": {
                "id": self._active_scenario["id"],
                "threat_type": self._active_scenario["threat_type"],
                "threat_name": self._active_scenario["name"],
                "severity": self._active_scenario["severity"],
                "phase": self._active_scenario["current_phase"],
                "status": self._active_scenario["status"],
                "target_device_id": self._active_scenario["target_device_id"],
                "source_ip": self._active_scenario.get("source_ip"),
                "indicator_count": len(self._indicators_triggered),
                "confidence": min(len(self._indicators_triggered) * 0.25, 1.0),
                "description": self._active_scenario.get("description"),
                "recommended_action": self._active_scenario.get("recommended_action"),
                "started_at": self._active_scenario["started_at"].isoformat(),
                "detected_at": self._active_scenario.get("detected_at").isoformat() if self._active_scenario.get("detected_at") else None,
            },
            "affected_devices": self._active_scenario.get("affected_devices", []),
            "attack_phase": self._active_scenario["current_phase"],
            "indicators_triggered": self._indicators_triggered.copy(),
            "elapsed_sec": elapsed,
        }

    def get_anomaly_reading(self, device_id: str) -> Dict:
        """Get modified sensor reading for a device affected by the current scenario.
        
        Returns anomaly values to inject into sensor data based on the active threat.
        """
        if not self._active_scenario or not self._running:
            return {}

        threat_type = self._active_scenario["threat_type"]
        phase = self._active_scenario["current_phase"]
        severity = self._active_scenario["severity"]
        intensity = self._active_scenario["intensity"]
        target = self._active_scenario["target_device_id"]
        
        # Only affect target and potentially spread in later phases
        if device_id != target:
            # In later phases, can affect other devices
            if phase in ["action", "impact"] and random.random() < 0.3 * intensity:
                if device_id not in self._active_scenario.get("affected_devices", []):
                    self._active_scenario.setdefault("affected_devices", []).append(device_id)
            return {}

        threat_def = THREAT_DEFINITIONS.get(threat_type, {})
        severity_config = threat_def.get("severity_levels", {}).get(severity, {})
        
        anomalies = {}
        
        # Generate anomalies based on threat type and phase
        if phase in ["exploit", "action", "impact"]:
            phase_multiplier = {"exploit": 0.5, "action": 0.8, "impact": 1.0}.get(phase, 0.3)
            
            if threat_type == "ddos":
                network_multiplier = severity_config.get("network_spike", 3.0) * intensity * phase_multiplier
                anomalies["network_bps"] = int(1_000_000 * network_multiplier)
                anomalies["cpu_util_pct"] = min(50 * intensity * phase_multiplier, 95)
                
            elif threat_type == "intrusion":
                anomalies["cpu_util_pct"] = min(30 * intensity * phase_multiplier, 80)
                anomalies["network_bps"] = int(500_000 * intensity * phase_multiplier)
                if phase == "action":
                    anomalies["power_kw"] = 2 * intensity
                    
            elif threat_type == "ransomware":
                anomalies["cpu_util_pct"] = min(80 * intensity * phase_multiplier, 99)
                anomalies["power_kw"] = 3 * intensity * phase_multiplier
                anomalies["airflow_cfm"] = -100 * intensity * phase_multiplier
                
            elif threat_type == "port_scan":
                anomalies["network_bps"] = int(200_000 * intensity * phase_multiplier)
                anomalies["cpu_util_pct"] = min(20 * intensity * phase_multiplier, 50)
                
            elif threat_type == "exfiltration":
                anomalies["network_bps"] = int(2_000_000 * intensity * phase_multiplier)
                anomalies["cpu_util_pct"] = min(30 * intensity * phase_multiplier, 70)
                
            elif threat_type == "compromise":
                anomalies["cpu_util_pct"] = min(60 * intensity * phase_multiplier, 95)
                anomalies["power_kw"] = 4 * intensity * phase_multiplier
                anomalies["network_bps"] = int(1_000_000 * intensity * phase_multiplier)
                anomalies["airflow_cfm"] = -150 * intensity * phase_multiplier

        return anomalies

    def get_triggered_indicators(self) -> List[Dict]:
        """Return list of currently triggered indicators."""
        if not self._active_scenario or not self._running:
            return []
        return self._indicators_triggered.copy()

    async def _run_scenario(self):
        """Main scenario loop - progresses through attack phases."""
        try:
            phases = self._active_scenario["phases"]
            severity = self._active_scenario["severity"]
            intensity = self._active_scenario["intensity"]
            
            # Calculate phase duration based on severity
            base_duration = {
                "low": 30, "medium": 20, "high": 15, "critical": 10
            }.get(severity, 20)
            
            for phase_idx, phase in enumerate(phases):
                if not self._running:
                    break
                    
                self._active_scenario["current_phase"] = phase
                self._active_scenario["phase_index"] = phase_idx
                
                # Phase progresses over time
                phase_duration = base_duration * intensity
                
                # Check indicators as we progress
                await self._check_and_trigger_indicators(phase)
                
                # Simulate detection if enough indicators triggered
                if len(self._indicators_triggered) >= 3 and not self._active_scenario.get("detected"):
                    self._active_scenario["detected"] = True
                    self._active_scenario["detected_at"] = datetime.utcnow()
                    delta = self._active_scenario["detected_at"] - self._active_scenario["started_at"]
                    self._active_scenario["detection_latency_sec"] = delta.total_seconds()
                    logger.info(
                        f"Threat DETECTED: {self._active_scenario['threat_type']} "
                        f"(latency={self._active_scenario['detection_latency_sec']:.1f}s)"
                    )
                
                await asyncio.sleep(phase_duration)
            
            # Scenario completed - auto-stop
            if self._running:
                await self.stop_scenario()
                
        except asyncio.CancelledError:
            logger.info("Scenario cancelled")
            raise
        except Exception as e:
            logger.error(f"Scenario error: {e}")
            await self.stop_scenario()

    async def _check_and_trigger_indicators(self, phase: str):
        """Check and trigger indicators based on current phase and threat type."""
        if not self._active_scenario:
            return

        threat_type = self._active_scenario["threat_type"]
        severity = self._active_scenario["severity"]
        intensity = self._active_scenario["intensity"]
        
        threat_def = THREAT_DEFINITIONS.get(threat_type, {})
        indicators = threat_def.get("indicators", [])
        
        # Probability of triggering based on phase and severity
        phase_trigger_prob = {"recon": 0.1, "exploit": 0.4, "action": 0.7, "impact": 0.9}.get(phase, 0.3)
        severity_multiplier = {"low": 0.3, "medium": 0.6, "high": 0.8, "critical": 1.0}.get(severity, 0.5)
        
        for indicator in indicators:
            indicator_id = f"{phase}_{indicator['type']}"
            
            # Don't trigger same indicator twice
            if any(i.get("indicator_type") == indicator["type"] for i in self._indicators_triggered):
                continue
            
            trigger_prob = phase_trigger_prob * severity_multiplier * intensity
            
            if random.random() < trigger_prob:
                triggered = {
                    "indicator_type": indicator["type"],
                    "value": indicator["threshold"] * random.uniform(1.2, 2.0),
                    "threshold": indicator["threshold"],
                    "triggered": True,
                    "description": indicator["description"],
                    "phase": phase,
                    "timestamp": datetime.utcnow().isoformat(),
                }
                self._indicators_triggered.append(triggered)
                logger.debug(f"Indicator triggered: {indicator['type']} at {phase} phase")


# Global instance
cyber_simulator = CyberSimulator()

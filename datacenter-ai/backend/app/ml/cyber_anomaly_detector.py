import numpy as np
import logging
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)

# Network/cyber anomaly thresholds
NETWORK_SPIKE_THRESHOLD = 2.5  # Multiplier over baseline
AUTH_FAILURE_THRESHOLD = 5  # Count per window
LATENCY_THRESHOLD_MS = 500
PACKET_LOSS_THRESHOLD = 0.05
WRITE_SPIKE_THRESHOLD = 10000  # bytes/sec
CONNECTION_PATTERN_THRESHOLD = 20  # connections
OUTBOUND_TRAFFIC_THRESHOLD = 2.0  # Multiplier over baseline


class CyberAnomalyDetector:
    """Detects cyber threats based on network and system metrics.
    
    This detector analyzes sensor metrics during active cyber scenarios
    and produces anomaly scores that feed into the RiskScorer ensemble.
    """

    def __init__(self):
        self._baseline_network = 1_000_000  # 1 Mbps baseline
        self._baseline_cpu = 50.0  # 50% baseline

    def compute_network_anomaly_score(
        self,
        network_bps: float,
        baseline_network_bps: float = None,
    ) -> float:
        """Compute network anomaly score (0-1)."""
        baseline = baseline_network_bps or self._baseline_network
        ratio = network_bps / baseline if baseline > 0 else 0
        
        if ratio < NETWORK_SPIKE_THRESHOLD:
            return 0.0
        
        # Linear scaling above threshold
        score = min((ratio - NETWORK_SPIKE_THRESHOLD) / (10 - NETWORK_SPIKE_THRESHOLD), 1.0)
        return float(score)

    def compute_auth_anomaly_score(
        self,
        failed_auths: int,
        window_size: int = 60,
    ) -> float:
        """Compute authentication anomaly score (0-1) based on failed attempts."""
        if failed_auths < AUTH_FAILURE_THRESHOLD:
            return 0.0
        
        # Exponential scaling above threshold
        excess = failed_auths - AUTH_FAILURE_THRESHOLD
        score = 1 - np.exp(-excess / 10)
        return float(min(score, 1.0))

    def compute_cpu_anomaly_score(
        self,
        cpu_util_pct: float,
        baseline_cpu: float = None,
    ) -> float:
        """Compute CPU anomaly score (0-1)."""
        baseline = baseline_cpu or self._baseline_cpu
        
        if cpu_util_pct < baseline * 1.5:
            return 0.0
        
        # Smooth scaling
        ratio = cpu_util_pct / baseline
        score = min((ratio - 1.5) / 0.5, 1.0)
        return float(max(0.0, score))

    def compute_write_anomaly_score(
        self,
        write_rate: float,
    ) -> float:
        """Compute disk write anomaly score (0-1) - indicative of ransomware."""
        if write_rate < WRITE_SPIKE_THRESHOLD:
            return 0.0
        
        score = min((write_rate / WRITE_SPIKE_THRESHOLD - 1) / 9, 1.0)
        return float(score)

    def compute_connection_pattern_score(
        self,
        connection_count: int,
        unique_ports: int,
    ) -> float:
        """Compute connection pattern anomaly score (0-1) - indicative of port scan."""
        if connection_count < CONNECTION_PATTERN_THRESHOLD:
            return 0.0
        
        # High connections to many unique ports = port scan
        port_ratio = unique_ports / max(connection_count, 1)
        score = min(connection_count / 100 + port_ratio, 1.0)
        return float(min(score, 1.0))

    def compute_outbound_traffic_score(
        self,
        outbound_bps: float,
        inbound_bps: float,
        baseline_outbound: float = None,
    ) -> float:
        """Compute outbound traffic anomaly score (0-1) - indicative of exfiltration."""
        baseline = baseline_outbound or (self._baseline_network * 0.3)
        
        if outbound_bps < baseline * OUTBOUND_TRAFFIC_THRESHOLD:
            return 0.0
        
        ratio = outbound_bps / baseline
        # Also check outbound/inbound ratio
        total = outbound_bps + inbound_bps
        outbound_ratio = outbound_bps / total if total > 0 else 0
        
        score = min((ratio - OUTBOUND_TRAFFIC_THRESHOLD) / 5 + (outbound_ratio - 0.5) * 2, 1.0)
        return float(max(0.0, min(score, 1.0)))

    def score_all(
        self,
        network_bps: float,
        cpu_util_pct: float,
        power_kw: float,
        airflow_cfm: float,
        auth_failures: int = 0,
        write_rate: float = 0,
        connection_count: int = 0,
        unique_ports: int = 0,
        outbound_bps: float = 0,
        inbound_bps: float = 0,
    ) -> Tuple[float, Dict]:
        """Compute combined cyber anomaly score (0-1) and contributing factors."""
        
        network_score = self.compute_network_anomaly_score(network_bps)
        cpu_score = self.compute_cpu_anomaly_score(cpu_util_pct)
        auth_score = self.compute_auth_anomaly_score(auth_failures)
        write_score = self.compute_write_anomaly_score(write_rate)
        connection_score = self.compute_connection_pattern_score(connection_count, unique_ports)
        outbound_score = self.compute_outbound_traffic_score(outbound_bps, inbound_bps)
        
        # Weighted combination - network and CPU are most indicative
        weights = {
            "network": 0.25,
            "cpu": 0.20,
            "auth": 0.15,
            "write": 0.15,
            "connection": 0.15,
            "outbound": 0.10,
        }
        
        combined = (
            weights["network"] * network_score +
            weights["cpu"] * cpu_score +
            weights["auth"] * auth_score +
            weights["write"] * write_score +
            weights["connection"] * connection_score +
            weights["outbound"] * outbound_score
        )
        
        factors = {
            "network_anomaly": round(network_score, 4),
            "cpu_anomaly": round(cpu_score, 4),
            "auth_anomaly": round(auth_score, 4),
            "write_anomaly": round(write_score, 4),
            "connection_anomaly": round(connection_score, 4),
            "outbound_anomaly": round(outbound_score, 4),
        }
        
        return float(combined), factors

    def get_cyber_risk_score(
        self,
        network_bps: float,
        cpu_util_pct: float,
        power_kw: float,
        airflow_cfm: float,
        **kwargs
    ) -> float:
        """Get cyber risk score on 0-100 scale."""
        score, _ = self.score_all(
            network_bps=network_bps,
            cpu_util_pct=cpu_util_pct,
            power_kw=power_kw,
            airflow_cfm=airflow_cfm,
            **kwargs
        )
        return score * 100


# Global instance
cyber_anomaly_detector = CyberAnomalyDetector()

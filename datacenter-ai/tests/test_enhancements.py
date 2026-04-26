"""pytest test suite for DataCentre AI enhancements.

Covers:
1. Cooling Agent (CoolingEnv, CoolingAgent, train helper)
2. Network IDS (NetworkIDS detection, thresholds, fitting)
3. Fault Injection (FaultInjector inject / resolve / verify)
4. Cost Engine (record_reading, record_agent_decision, summary, calculate)
"""

import asyncio
import sys
import os

import numpy as np
import pytest

# ── Make the backend package importable without a full FastAPI server ───────
_BACKEND = os.path.join(os.path.dirname(__file__), "..", "backend")
if _BACKEND not in sys.path:
    sys.path.insert(0, _BACKEND)


# ===========================================================================
# 1. Cooling Agent
# ===========================================================================


class TestCoolingEnv:
    """Tests for the CoolingEnv gymnasium environment."""

    def setup_method(self):
        from app.ml.cooling_agent import CoolingEnv
        self.env = CoolingEnv(max_steps=10)

    def test_observation_space_shape(self):
        """Observation vector should have 5 components."""
        obs, _ = self.env.reset()
        assert obs.shape == (5,), f"Expected (5,), got {obs.shape}"

    def test_action_space_shape(self):
        """Action space should be a 1-D continuous box."""
        assert self.env.action_space.shape == (1,)

    def test_reset_returns_valid_obs(self):
        """Reset should return an observation within bounds."""
        obs, info = self.env.reset(seed=42)
        lo = self.env.observation_space.low
        hi = self.env.observation_space.high
        assert np.all(obs >= lo), "Observation below lower bound"
        assert np.all(obs <= hi), "Observation above upper bound"
        assert isinstance(info, dict)

    def test_step_returns_transition(self):
        """Step should return (obs, reward, terminated, truncated, info)."""
        self.env.reset(seed=0)
        obs, reward, terminated, truncated, info = self.env.step(np.array([0.5]))
        assert obs.shape == (5,)
        assert isinstance(reward, float)
        assert isinstance(terminated, bool)
        assert isinstance(truncated, bool)
        assert "setpoint" in info

    def test_episode_terminates(self):
        """Episode should end after max_steps steps."""
        self.env.reset(seed=1)
        truncated = False
        for _ in range(10):
            _, _, _, truncated, _ = self.env.step(np.array([0.0]))
        assert truncated, "Episode should have been truncated after max_steps"

    def test_reward_penalises_high_setpoint_under_high_cpu(self):
        """High setpoint with high CPU load should yield a lower reward."""
        env = self._make_env_with_state(cpu=95.0, setpoint=26.0)
        _, reward_risky, _, _, _ = env.step(np.array([1.0]))

        env2 = self._make_env_with_state(cpu=20.0, setpoint=20.0)
        _, reward_safe, _, _, _ = env2.step(np.array([1.0]))

        assert reward_risky < reward_safe

    def _make_env_with_state(self, cpu: float, setpoint: float):
        from app.ml.cooling_agent import CoolingEnv
        env = CoolingEnv(max_steps=10)
        env.reset(seed=7)
        env._cpu_util = cpu
        env._setpoint = setpoint
        return env


class TestCoolingAgent:
    """Tests for the CoolingAgent wrapper."""

    def setup_method(self):
        from app.ml.cooling_agent import CoolingAgent
        from pathlib import Path
        self.agent = CoolingAgent(model_path=Path("/tmp/nonexistent_model.zip"))

    def test_is_loaded_false_when_no_model(self):
        """Agent should report not loaded when model file is missing."""
        assert not self.agent.is_loaded()

    def test_heuristic_fallback_low_cpu(self):
        """When CPU is low and temperature is cool, setpoint should increase."""
        result = self.agent.recommend_action(cpu_util=20, inlet_temp=21, setpoint=22, hour=14)
        assert result["delta_setpoint"] >= 0, "Expected upward setpoint adjustment"
        assert result["policy"] == "heuristic_fallback"

    def test_heuristic_fallback_high_cpu(self):
        """When CPU is very high, setpoint should decrease."""
        result = self.agent.recommend_action(cpu_util=95, inlet_temp=30, setpoint=24, hour=12)
        assert result["delta_setpoint"] <= 0, "Expected downward setpoint adjustment"

    def test_new_setpoint_within_bounds(self):
        """Recommended setpoint must stay within allowed range."""
        from app.ml.cooling_agent import COOLING_SETPOINT_MIN, COOLING_SETPOINT_MAX
        for cpu in [0, 50, 100]:
            result = self.agent.recommend_action(cpu_util=cpu, inlet_temp=22, setpoint=22, hour=6)
            assert COOLING_SETPOINT_MIN <= result["new_setpoint"] <= COOLING_SETPOINT_MAX

    def test_energy_reduction_pct_increases_with_setpoint(self):
        """Higher setpoint should produce higher energy reduction percentage."""
        low = self.agent.compute_energy_reduction_pct(baseline_kw=10, new_setpoint=22)
        high = self.agent.compute_energy_reduction_pct(baseline_kw=10, new_setpoint=25)
        assert high > low

    def test_energy_reduction_pct_zero_at_baseline(self):
        """At exactly baseline setpoint, reduction should be 0."""
        from app.ml.cooling_agent import BASELINE_SETPOINT
        result = self.agent.compute_energy_reduction_pct(baseline_kw=10, new_setpoint=BASELINE_SETPOINT)
        assert result == 0.0


class TestTrainCoolingAgent:
    """Smoke test for the training helper."""

    def test_train_returns_agent(self):
        """train_cooling_agent should return a CoolingAgent with a loaded model."""
        from app.ml.cooling_agent import train_cooling_agent, CoolingAgent
        agent = train_cooling_agent(total_timesteps=1_000)
        assert isinstance(agent, CoolingAgent)
        assert agent.is_loaded()

    def test_train_saves_model(self, tmp_path):
        """train_cooling_agent should save the model when save_path is given."""
        from app.ml.cooling_agent import train_cooling_agent
        save_path = tmp_path / "test_cooling.zip"
        train_cooling_agent(total_timesteps=500, save_path=save_path)
        assert save_path.exists(), "Model file should have been created"


# ===========================================================================
# 2. Network IDS
# ===========================================================================


class TestNetworkIDS:
    """Tests for the NetworkIDS intrusion detection system."""

    def setup_method(self):
        from app.ml.network_ids import NetworkIDS
        self.ids = NetworkIDS()
        self.ids.ensure_fitted()

    def test_status_fitted(self):
        """IDS should report as fitted after ensure_fitted."""
        status = self.ids.get_status()
        assert status["fitted"] is True

    def test_normal_traffic_no_alert(self):
        """Normal traffic should not trigger an alert."""
        result = self.ids.detect(
            network_bps=1_000_000,
            cpu_util_pct=60,
            power_kw=8,
            airflow_cfm=600,
        )
        assert isinstance(result["score"], float)
        assert "severity" in result

    def test_anomalous_traffic_higher_score(self):
        """Anomalous traffic (high bps, high CPU) should score more anomalous."""
        normal = self.ids.detect(
            network_bps=1_000_000, cpu_util_pct=60, power_kw=8, airflow_cfm=600
        )
        anomalous = self.ids.detect(
            network_bps=100_000_000, cpu_util_pct=99, power_kw=50, airflow_cfm=100
        )
        assert anomalous["score"] <= normal["score"], "Anomalous should have lower (worse) IF score"

    def test_detect_returns_required_keys(self):
        """Detection result must contain all expected keys."""
        result = self.ids.detect(network_bps=500_000, cpu_util_pct=40, power_kw=5, airflow_cfm=500)
        for key in ("score", "alert", "severity", "confidence", "features"):
            assert key in result, f"Missing key: {key}"

    def test_severity_levels(self):
        """Severity should be one of normal / warning / critical."""
        result = self.ids.detect(network_bps=500_000, cpu_util_pct=40, power_kw=5, airflow_cfm=500)
        assert result["severity"] in ("normal", "warning", "critical")

    def test_confidence_range(self):
        """Confidence should be between 0 and 1."""
        result = self.ids.detect(network_bps=1_000_000, cpu_util_pct=60, power_kw=8, airflow_cfm=600)
        assert 0.0 <= result["confidence"] <= 1.0

    def test_set_thresholds_updates_values(self):
        """set_thresholds should update alert_threshold and critical_threshold."""
        self.ids.set_thresholds(alert_threshold=-0.05, critical_threshold=-0.20)
        assert self.ids.alert_threshold == -0.05
        assert self.ids.critical_threshold == -0.20

    def test_custom_alert_threshold_fires_on_borderline(self):
        """A very high (lenient) alert threshold should flag traffic as alert=True."""
        self.ids.set_thresholds(alert_threshold=100.0)
        result = self.ids.detect(network_bps=1_000_000, cpu_util_pct=60, power_kw=8, airflow_cfm=600)
        assert result["alert"] is True

    def test_detect_batch(self):
        """Batch detection should return one result per input row."""
        X = np.array([
            [1_000_000, 60, 8, 600, 0.0, 10],
            [5_000_000, 95, 20, 200, 0.05, 100],
        ])
        results = self.ids.detect_batch(X)
        assert len(results) == 2

    def test_fit_and_save_reload(self, tmp_path):
        """Fit, save, then reload should produce a functional model."""
        from app.ml.network_ids import NetworkIDS
        rng = np.random.RandomState(0)
        X = rng.normal(size=(200, 6))
        ids = NetworkIDS(model_path=tmp_path / "ids.joblib")
        ids.fit(X)
        assert ids._fitted

        ids2 = NetworkIDS(model_path=tmp_path / "ids.joblib")
        assert ids2._fitted


# ===========================================================================
# 3. Fault Injection
# ===========================================================================


class TestFaultInjector:
    """Tests for the FaultInjector service."""

    def setup_method(self):
        from app.services.fault_injector import FaultInjector
        self.injector = FaultInjector()

    def _run(self, coro):
        """Run a coroutine synchronously."""
        return asyncio.get_event_loop().run_until_complete(coro)

    def test_inject_cpu_spike(self):
        """Injecting a cpu_spike fault should return a valid record."""
        record = self._run(self.injector.inject("RACK-A1", "cpu_spike", duration_sec=1))
        assert record["fault_type"] == "cpu_spike"
        assert record["device_id"] == "RACK-A1"
        assert record["fault_id"]

    def test_inject_network_drop(self):
        """Injecting a network_drop fault should return a valid record."""
        record = self._run(self.injector.inject("RACK-B1", "network_drop", duration_sec=1))
        assert record["fault_type"] == "network_drop"

    def test_inject_disk_full(self):
        """Injecting a disk_full fault should return a valid record."""
        record = self._run(self.injector.inject("RACK-A2", "disk_full", duration_sec=1))
        assert record["fault_type"] == "disk_full"

    def test_invalid_fault_type_raises(self):
        """Unknown fault type should raise ValueError."""
        with pytest.raises(ValueError):
            self._run(self.injector.inject("RACK-A1", "meteor_strike"))

    def test_active_faults_listed(self):
        """Injected fault should appear in active list."""
        self._run(self.injector.inject("RACK-A1", "cpu_spike", duration_sec=60))
        active = self.injector.list_active_faults()
        assert len(active) >= 1

    def test_resolve_removes_from_active(self):
        """Resolving a fault should remove it from the active list."""
        record = self._run(self.injector.inject("RACK-A1", "network_drop", duration_sec=60))
        fault_id = record["fault_id"]
        self.injector.resolve(fault_id)
        active_ids = [f["fault_id"] for f in self.injector.list_active_faults()]
        assert fault_id not in active_ids

    def test_resolve_nonexistent_returns_none(self):
        """Resolving a nonexistent fault should return None."""
        result = self.injector.resolve("does-not-exist")
        assert result is None

    def test_mark_rerouted(self):
        """Marking a fault as rerouted should set rerouted=True."""
        record = self._run(self.injector.inject("RACK-B2", "cpu_spike", duration_sec=60))
        fault_id = record["fault_id"]
        ok = self.injector.mark_rerouted(fault_id)
        assert ok is True
        verify = self.injector.verify_rerouting(fault_id)
        assert verify["rerouted"] is True

    def test_verify_rerouting_not_found(self):
        """verify_rerouting for an unknown fault should return status=not_found."""
        result = self.injector.verify_rerouting("nonexistent-id")
        assert result["status"] == "not_found"

    def test_inject_random(self):
        """inject_random should produce a valid fault record."""
        record = self._run(self.injector.inject_random(duration_sec=1))
        assert record["fault_type"] in ["cpu_spike", "network_drop", "disk_full"]
        assert record["fault_id"]

    def test_history_is_populated(self):
        """Fault history should grow with each injection."""
        self._run(self.injector.inject("RACK-A1", "disk_full", duration_sec=1))
        self._run(self.injector.inject("RACK-A2", "cpu_spike", duration_sec=1))
        history = self.injector.list_history()
        assert len(history) >= 2

    def test_intensity_affects_record(self):
        """Fault intensity should be stored in the record."""
        record = self._run(self.injector.inject("RACK-A1", "cpu_spike", duration_sec=1, intensity=0.5))
        assert record["intensity"] == 0.5


# ===========================================================================
# 4. Cost Engine
# ===========================================================================


class TestCostEngine:
    """Tests for the CostEngine power consumption and cost tracker."""

    def setup_method(self):
        from app.services.cost_engine import CostEngine
        self.engine = CostEngine(energy_cost_per_kwh=0.10)
        self.engine.reset()

    def test_record_reading_returns_kwh(self):
        """record_reading should return positive kWh for positive power."""
        result = self.engine.record_reading("RACK-A1", power_kw=10.0, interval_hours=1.0)
        assert result["kwh"] == pytest.approx(10.0, rel=1e-6)
        assert result["cost_usd"] == pytest.approx(1.0, rel=1e-6)

    def test_record_reading_cumulative(self):
        """Multiple readings for same device should accumulate kWh."""
        self.engine.record_reading("RACK-A1", power_kw=5.0, interval_hours=1.0)
        self.engine.record_reading("RACK-A1", power_kw=5.0, interval_hours=1.0)
        summary = self.engine.get_summary()
        assert summary["total_kwh"] == pytest.approx(10.0, rel=1e-6)

    def test_record_reading_zero_power_ok(self):
        """Zero power reading should produce zero kWh and no error."""
        result = self.engine.record_reading("RACK-A1", power_kw=0.0, interval_hours=1.0)
        assert result["kwh"] == 0.0
        assert result["cost_usd"] == 0.0

    def test_record_agent_decision_tracks_savings(self):
        """Agent decision should track kWh and USD savings."""
        result = self.engine.record_agent_decision(
            decision_type="cooling_adjust",
            device_id="RACK-A1",
            power_kw_before=10.0,
            power_kw_after=8.0,
            interval_hours=1.0,
        )
        assert result["saved_kwh"] == pytest.approx(2.0, rel=1e-6)
        assert result["saved_usd"] == pytest.approx(0.20, rel=1e-6)

    def test_record_agent_decision_no_negative_savings(self):
        """Savings should be zero (not negative) when after > before."""
        result = self.engine.record_agent_decision(
            decision_type="reroute",
            device_id="RACK-A2",
            power_kw_before=5.0,
            power_kw_after=8.0,  # Power went up
            interval_hours=1.0,
        )
        assert result["saved_kwh"] == 0.0

    def test_summary_reflects_totals(self):
        """get_summary should return correct accumulated totals."""
        self.engine.record_reading("RACK-A1", power_kw=10.0, interval_hours=1.0)
        self.engine.record_agent_decision("test", "RACK-A1", 10.0, 8.0, 1.0)
        summary = self.engine.get_summary()
        assert summary["total_kwh"] == pytest.approx(10.0, rel=1e-6)
        assert summary["savings_kwh"] == pytest.approx(2.0, rel=1e-6)
        assert summary["decision_count"] == 1

    def test_calculate_power_cost(self):
        """calculate_power_cost should correctly compute kWh and cost."""
        result = self.engine.calculate_power_cost(power_kw=5.0, hours=2.0)
        assert result["kwh"] == pytest.approx(10.0, rel=1e-6)
        assert result["cost_usd"] == pytest.approx(1.0, rel=1e-6)

    def test_calculate_power_cost_zero(self):
        """Zero power should produce zero cost."""
        result = self.engine.calculate_power_cost(power_kw=0.0, hours=1.0)
        assert result["kwh"] == 0.0
        assert result["cost_usd"] == 0.0

    def test_reset_clears_totals(self):
        """reset() should zero all accumulators."""
        self.engine.record_reading("RACK-A1", power_kw=100.0, interval_hours=1.0)
        self.engine.reset()
        summary = self.engine.get_summary()
        assert summary["total_kwh"] == 0.0
        assert summary["total_cost_usd"] == 0.0
        assert summary["decision_count"] == 0

    def test_get_recent_decisions(self):
        """get_recent_decisions should return most recent records first."""
        for i in range(5):
            self.engine.record_agent_decision(f"decision_{i}", "RACK-A1", 10.0, 8.0, 1.0)
        recent = self.engine.get_recent_decisions(limit=3)
        assert len(recent) == 3
        assert recent[0]["decision_type"] == "decision_4"

    def test_per_device_breakdown(self):
        """Summary should include a per-device kWh breakdown."""
        self.engine.record_reading("RACK-A1", power_kw=5.0, interval_hours=1.0)
        self.engine.record_reading("RACK-A2", power_kw=3.0, interval_hours=1.0)
        summary = self.engine.get_summary()
        assert "RACK-A1" in summary["per_device"]
        assert "RACK-A2" in summary["per_device"]

    def test_energy_cost_rate(self):
        """Energy cost per kWh should match the configured rate."""
        engine = self.__class__.__dict__["setup_method"](self) or self.engine
        # Use a custom rate
        from app.services.cost_engine import CostEngine
        engine2 = CostEngine(energy_cost_per_kwh=0.20)
        result = engine2.record_reading("RACK-X", power_kw=1.0, interval_hours=1.0)
        assert result["cost_usd"] == pytest.approx(0.20, rel=1e-6)

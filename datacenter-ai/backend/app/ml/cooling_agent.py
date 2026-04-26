"""Predictive Cooling Agent using Stable-Baselines3 PPO.

This module provides a reinforcement learning environment and PPO-based agent
that dynamically adjusts server cooling setpoints based on CPU load, targeting
approximately 20% energy reduction versus a baseline fixed-setpoint policy.
"""

import logging
import numpy as np
from pathlib import Path
from typing import Optional, Tuple, Dict, Any

import gymnasium as gym
from gymnasium import spaces

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

COOLING_SETPOINT_MIN = 18.0   # °C — minimum cooling setpoint
COOLING_SETPOINT_MAX = 27.0   # °C — maximum cooling setpoint (ASHRAE A2 limit)
BASELINE_SETPOINT = 22.0      # °C — fixed baseline used for comparison
CPU_LOAD_MEAN = 60.0          # % — typical average CPU utilisation
CPU_LOAD_STD = 15.0           # % — standard deviation
POWER_PER_DEGREE_KW = 0.5     # kW saved per +1 °C setpoint increase
THERMAL_RISK_THRESHOLD = 70.0  # % CPU — above this cooling must stay cool
ENERGY_COST_PER_KWH = 0.10    # USD/kWh (matches config default)

# ---------------------------------------------------------------------------
# Gymnasium Environment
# ---------------------------------------------------------------------------


class CoolingEnv(gym.Env):
    """Gymnasium environment for data-centre cooling optimisation.

    State space:
        - cpu_util_pct (0-100)
        - inlet_temp_c (18-40)
        - current_setpoint (COOLING_SETPOINT_MIN - COOLING_SETPOINT_MAX)
        - time_of_day_sin, time_of_day_cos (cyclic hour encoding)

    Action space:
        Continuous: delta setpoint in [-1, +1] °C applied each step.

    Reward:
        +energy_saved_kw (reward power savings)
        -thermal_penalty  (penalise when temperature exceeds safe threshold)
    """

    metadata = {"render_modes": []}

    def __init__(self, max_steps: int = 288):
        """Initialise the cooling environment.

        Args:
            max_steps: Maximum number of steps per episode (default 288 ≈ 24 h at 5-min steps).
        """
        super().__init__()
        self.max_steps = max_steps
        self._step_count = 0

        # Observation: [cpu_util, inlet_temp, setpoint, time_sin, time_cos]
        low = np.array([0.0, 15.0, COOLING_SETPOINT_MIN, -1.0, -1.0], dtype=np.float32)
        high = np.array([100.0, 45.0, COOLING_SETPOINT_MAX, 1.0, 1.0], dtype=np.float32)
        self.observation_space = spaces.Box(low=low, high=high, dtype=np.float32)

        # Action: continuous delta setpoint [-1, +1] °C
        self.action_space = spaces.Box(
            low=np.array([-1.0], dtype=np.float32),
            high=np.array([1.0], dtype=np.float32),
            dtype=np.float32,
        )

        self._setpoint = BASELINE_SETPOINT
        self._cpu_util = CPU_LOAD_MEAN
        self._inlet_temp = 22.0
        self._hour = 12

    def reset(self, *, seed: Optional[int] = None, options: Optional[dict] = None):
        """Reset the environment to an initial state.

        Args:
            seed: Optional random seed.
            options: Optional configuration dict (unused).

        Returns:
            Tuple of (observation, info).
        """
        super().reset(seed=seed)
        self._step_count = 0
        self._setpoint = BASELINE_SETPOINT
        self._hour = int(self.np_random.integers(0, 24))
        self._cpu_util = float(np.clip(self.np_random.normal(CPU_LOAD_MEAN, CPU_LOAD_STD), 5, 100))
        self._inlet_temp = float(np.clip(self.np_random.normal(22, 2), 18, 38))
        return self._observe(), {}

    def step(self, action: np.ndarray) -> Tuple[np.ndarray, float, bool, bool, dict]:
        """Apply action (delta setpoint) and return transition.

        Args:
            action: np.ndarray of shape (1,) containing the setpoint delta in °C.

        Returns:
            Tuple of (observation, reward, terminated, truncated, info).
        """
        delta = float(np.clip(action[0], -1.0, 1.0))
        prev_setpoint = self._setpoint
        self._setpoint = float(np.clip(self._setpoint + delta, COOLING_SETPOINT_MIN, COOLING_SETPOINT_MAX))

        # Simulate next CPU and temperature
        self._hour = (self._hour + 1) % 24
        hour_factor = 0.5 + 0.5 * abs(12 - self._hour) / 12
        self._cpu_util = float(np.clip(
            CPU_LOAD_MEAN * hour_factor + self.np_random.normal(0, CPU_LOAD_STD * 0.3),
            5, 100,
        ))
        # Higher setpoint → slightly higher inlet temp
        temp_drift = (self._setpoint - BASELINE_SETPOINT) * 0.3
        self._inlet_temp = float(np.clip(
            22.0 + temp_drift + self.np_random.normal(0, 0.5),
            15.0, 45.0,
        ))

        reward = self._compute_reward(prev_setpoint)
        self._step_count += 1
        terminated = False
        truncated = self._step_count >= self.max_steps
        info = {
            "setpoint": self._setpoint,
            "cpu_util": self._cpu_util,
            "inlet_temp": self._inlet_temp,
            "energy_saved_kw": max(0.0, (self._setpoint - BASELINE_SETPOINT) * POWER_PER_DEGREE_KW),
        }
        return self._observe(), reward, terminated, truncated, info

    def _observe(self) -> np.ndarray:
        """Build observation vector from current state."""
        angle = 2 * np.pi * self._hour / 24
        return np.array(
            [self._cpu_util, self._inlet_temp, self._setpoint,
             np.sin(angle), np.cos(angle)],
            dtype=np.float32,
        )

    def _compute_reward(self, prev_setpoint: float) -> float:
        """Compute step reward: energy savings minus thermal risk penalty.

        Args:
            prev_setpoint: The setpoint before the action was applied.

        Returns:
            Scalar reward value.
        """
        # Reward energy saved by raising the setpoint above baseline
        energy_saved_kw = max(0.0, (self._setpoint - BASELINE_SETPOINT) * POWER_PER_DEGREE_KW)
        energy_reward = energy_saved_kw * 0.1  # Scale reward

        # Penalise high CPU load with a high setpoint (thermal risk)
        thermal_penalty = 0.0
        if self._cpu_util > THERMAL_RISK_THRESHOLD and self._setpoint > BASELINE_SETPOINT + 2:
            overshoot = self._setpoint - (BASELINE_SETPOINT + 2)
            thermal_penalty = overshoot * 0.5

        # Small penalty for rapid setpoint oscillation
        stability_penalty = abs(self._setpoint - prev_setpoint) * 0.01

        return energy_reward - thermal_penalty - stability_penalty


# ---------------------------------------------------------------------------
# Agent wrapper
# ---------------------------------------------------------------------------


class CoolingAgent:
    """Wraps a Stable-Baselines3 PPO model for data-centre cooling control.

    Usage::

        agent = CoolingAgent(model_path=Path("ml/artifacts/cooling_ppo.zip"))
        agent.load()
        action = agent.recommend_action(cpu_util=70, inlet_temp=24, setpoint=22, hour=14)
    """

    def __init__(self, model_path: Path):
        """Initialise the cooling agent.

        Args:
            model_path: Path to the saved PPO model (.zip file).
        """
        self.model_path = Path(model_path)
        self._model = None
        self._env = CoolingEnv()

    def load(self) -> bool:
        """Load a pre-trained PPO model from disk.

        Returns:
            True if model loaded successfully, False otherwise.
        """
        try:
            from stable_baselines3 import PPO  # type: ignore
            if not self.model_path.exists():
                logger.warning("Cooling agent model not found at %s", self.model_path)
                return False
            self._model = PPO.load(str(self.model_path))
            logger.info("Cooling agent loaded from %s", self.model_path)
            return True
        except Exception as exc:
            logger.error("Failed to load cooling agent: %s", exc)
            return False

    def is_loaded(self) -> bool:
        """Return whether a trained model is available."""
        return self._model is not None

    def recommend_action(
        self,
        cpu_util: float,
        inlet_temp: float,
        setpoint: float,
        hour: int,
    ) -> Dict[str, Any]:
        """Recommend a setpoint delta for the given observations.

        Args:
            cpu_util: Current CPU utilisation in percent (0-100).
            inlet_temp: Current rack inlet temperature in °C.
            setpoint: Current cooling setpoint in °C.
            hour: Current hour of day (0-23).

        Returns:
            Dict with keys: ``delta_setpoint``, ``new_setpoint``, ``estimated_energy_saved_kw``,
            ``policy``.
        """
        angle = 2 * np.pi * hour / 24
        obs = np.array(
            [cpu_util, inlet_temp, setpoint, np.sin(angle), np.cos(angle)],
            dtype=np.float32,
        )

        if self._model is not None:
            action, _ = self._model.predict(obs, deterministic=True)
            delta = float(np.clip(action[0], -1.0, 1.0))
            policy = "rl_ppo"
        else:
            # Heuristic fallback: raise setpoint when CPU is low, lower when hot
            if cpu_util < 40 and inlet_temp < 24:
                delta = 0.5
            elif cpu_util > THERMAL_RISK_THRESHOLD or inlet_temp > 28:
                delta = -0.5
            else:
                delta = 0.0
            policy = "heuristic_fallback"

        new_setpoint = float(np.clip(setpoint + delta, COOLING_SETPOINT_MIN, COOLING_SETPOINT_MAX))
        energy_saved_kw = max(0.0, (new_setpoint - BASELINE_SETPOINT) * POWER_PER_DEGREE_KW)

        return {
            "delta_setpoint": round(delta, 3),
            "new_setpoint": round(new_setpoint, 2),
            "estimated_energy_saved_kw": round(energy_saved_kw, 3),
            "policy": policy,
        }

    def compute_energy_reduction_pct(
        self,
        baseline_kw: float,
        new_setpoint: float,
    ) -> float:
        """Estimate energy reduction percentage vs baseline fixed setpoint.

        Args:
            baseline_kw: Baseline power consumption in kW.
            new_setpoint: The proposed new setpoint in °C.

        Returns:
            Energy reduction as a percentage (0-100).
        """
        if baseline_kw <= 0:
            return 0.0
        saved_kw = max(0.0, (new_setpoint - BASELINE_SETPOINT) * POWER_PER_DEGREE_KW)
        return round(min(saved_kw / baseline_kw * 100, 50.0), 2)


# ---------------------------------------------------------------------------
# Training helper
# ---------------------------------------------------------------------------


def train_cooling_agent(
    total_timesteps: int = 50_000,
    save_path: Optional[Path] = None,
) -> CoolingAgent:
    """Train a PPO cooling agent and optionally save it to disk.

    Args:
        total_timesteps: Number of environment steps to train for.
        save_path: If provided, the trained model is saved at this path.

    Returns:
        A ``CoolingAgent`` instance with the trained PPO model loaded.
    """
    from stable_baselines3 import PPO  # type: ignore
    from stable_baselines3.common.env_checker import check_env  # type: ignore

    env = CoolingEnv()
    check_env(env, warn=True)

    model = PPO(
        "MlpPolicy",
        env,
        verbose=0,
        n_steps=512,
        batch_size=64,
        n_epochs=10,
        gamma=0.99,
        learning_rate=3e-4,
    )
    model.learn(total_timesteps=total_timesteps)
    logger.info("Cooling agent training complete (%d timesteps)", total_timesteps)

    if save_path is not None:
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        model.save(str(save_path))
        logger.info("Cooling agent saved to %s", save_path)

    agent = CoolingAgent(model_path=save_path or Path("cooling_ppo.zip"))
    agent._model = model
    return agent


# ---------------------------------------------------------------------------
# Global singleton (lazy-loaded)
# ---------------------------------------------------------------------------

_cooling_agent: Optional[CoolingAgent] = None


def get_cooling_agent(artifacts_dir: Optional[Path] = None) -> CoolingAgent:
    """Return (and optionally initialise) the global CoolingAgent singleton.

    Args:
        artifacts_dir: Directory that contains ``cooling_ppo.zip``.  If not
            supplied the agent's ``is_loaded()`` may return False, in which
            case the heuristic fallback is used.

    Returns:
        The global ``CoolingAgent`` instance.
    """
    global _cooling_agent
    if _cooling_agent is None:
        path = (artifacts_dir or Path("ml/artifacts")) / "cooling_ppo.zip"
        _cooling_agent = CoolingAgent(model_path=path)
        _cooling_agent.load()
    return _cooling_agent

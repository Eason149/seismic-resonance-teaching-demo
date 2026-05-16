from dataclasses import dataclass
from typing import Dict, Tuple

import numpy as np
from scipy import signal


@dataclass
class BuildingSystem:
    """
    Single-DOF building model as a 2nd-order LTI system:
        x''(t) + 2*zeta*omega_n*x'(t) + omega_n^2*x(t) = -a_g(t)

    Transfer function:
        H(s) = X(s)/A_g(s) = -1 / (s^2 + 2*zeta*omega_n*s + omega_n^2)
    """

    name: str
    f_n: float  # Natural frequency in Hz
    zeta: float = 0.05

    @property
    def omega_n(self) -> float:
        return 2 * np.pi * self.f_n

    def lti(self) -> signal.lti:
        num = [-1.0]
        den = [1.0, 2 * self.zeta * self.omega_n, self.omega_n**2]
        return signal.lti(num, den)

    def simulate_response(self, t: np.ndarray, a_g: np.ndarray) -> np.ndarray:
        sys = self.lti()
        _, x, _ = signal.lsim(sys, U=a_g, T=t)
        return x

    def frequency_response(self, f_hz: np.ndarray) -> np.ndarray:
        w = 2 * np.pi * f_hz
        # |H(jw)| = 1 / sqrt((wn^2-w^2)^2 + (2*zeta*wn*w)^2)
        denom = np.sqrt(
            (self.omega_n**2 - w**2) ** 2 + (2 * self.zeta * self.omega_n * w) ** 2
        )
        return 1.0 / denom


def default_buildings(zeta: float = 0.05) -> Dict[str, BuildingSystem]:
    return {
        "Low-rise (f_n=2.5 Hz)": BuildingSystem("Low-rise", f_n=2.5, zeta=zeta),
        "Mid-rise (f_n=1.2 Hz)": BuildingSystem("Mid-rise", f_n=1.2, zeta=zeta),
        "High-rise (f_n=0.5 Hz)": BuildingSystem("High-rise", f_n=0.5, zeta=zeta),
    }


def normalized_signals(signals: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
    out: Dict[str, np.ndarray] = {}
    for k, x in signals.items():
        peak = np.max(np.abs(x))
        out[k] = x / peak if peak > 0 else x.copy()
    return out


def peak_metrics(signals: Dict[str, np.ndarray]) -> Dict[str, Tuple[float, float]]:
    """
    Return {name: (peak_abs, rms)} for quick reporting.
    """
    info = {}
    for name, x in signals.items():
        peak = float(np.max(np.abs(x)))
        rms = float(np.sqrt(np.mean(x**2)))
        info[name] = (peak, rms)
    return info

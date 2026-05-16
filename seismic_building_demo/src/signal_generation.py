import numpy as np
from scipy.signal.windows import tukey


def generate_time_vector(fs: float = 200.0, duration: float = 40.0) -> np.ndarray:
    """Generate a uniform time axis."""
    n = int(fs * duration)
    return np.arange(n) / fs


def generate_seismic_signal(
    t: np.ndarray,
    noise_level: float = 0.12,
    seed: int = 42,
) -> np.ndarray:
    """
    Generate a synthetic earthquake acceleration signal a_g(t).

    Model:
    a_g(t) = envelope(t) * [sin(2*pi*f1*t) + 0.6*sin(2*pi*f2*t) + 0.3*sin(2*pi*f3*t)] + noise
    """
    rng = np.random.default_rng(seed)

    f1, f2, f3 = 0.8, 1.6, 3.2
    base = (
        np.sin(2 * np.pi * f1 * t)
        + 0.6 * np.sin(2 * np.pi * f2 * t + 0.3)
        + 0.3 * np.sin(2 * np.pi * f3 * t + 1.0)
    )

    # Tukey envelope: weak-start, strong-middle, decaying-end.
    env_tukey = tukey(len(t), alpha=0.75)
    # Slight right-tail exponential decay to mimic post-main-shock attenuation.
    tail_decay = np.exp(-0.012 * t)
    tail_decay /= tail_decay.max()
    envelope = 0.2 + 0.8 * env_tukey * tail_decay

    noise = noise_level * rng.standard_normal(len(t))
    ag = envelope * base + 0.4 * envelope * noise
    return ag


def dominant_frequency(signal: np.ndarray, fs: float) -> float:
    """Return dominant frequency from one-sided FFT magnitude (excluding DC)."""
    n = len(signal)
    freqs = np.fft.rfftfreq(n, d=1.0 / fs)
    mag = np.abs(np.fft.rfft(signal))
    if len(mag) > 1:
        idx = np.argmax(mag[1:]) + 1
    else:
        idx = 0
    return float(freqs[idx])

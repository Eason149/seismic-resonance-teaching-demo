from pathlib import Path
from typing import Dict, Tuple

import matplotlib.pyplot as plt
import numpy as np

from .building_system import BuildingSystem


def setup_style() -> None:
    plt.style.use("default")
    plt.rcParams.update(
        {
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "font.size": 13,
            "axes.titlesize": 15,
            "axes.labelsize": 13,
            "legend.fontsize": 12,
            "xtick.labelsize": 12,
            "ytick.labelsize": 12,
            "lines.linewidth": 2.0,
        }
    )


def savefig(fig: plt.Figure, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_seismic_waveform(t: np.ndarray, a_g: np.ndarray, out_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(11, 4.8))
    ax.plot(t, a_g, color="#d62728")
    ax.set_title("Demo 1: Simulated Seismic Ground Acceleration Input")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Acceleration (arb. unit)")
    ax.grid(alpha=0.28)
    savefig(fig, out_path)


def plot_spectrum(
    t: np.ndarray, a_g: np.ndarray, fs: float, out_path: Path, fmax: float = 10.0
) -> float:
    n = len(a_g)
    freqs = np.fft.rfftfreq(n, d=1.0 / fs)
    mag = np.abs(np.fft.rfft(a_g)) / n

    mask = freqs <= fmax
    ff = freqs[mask]
    mm = mag[mask]

    if len(mm) > 1:
        peak_idx = np.argmax(mm[1:]) + 1
    else:
        peak_idx = 0
    peak_f = float(ff[peak_idx])
    peak_m = float(mm[peak_idx])

    fig, ax = plt.subplots(figsize=(11, 4.8))
    ax.plot(ff, mm, color="#1f77b4")
    ax.scatter([peak_f], [peak_m], color="black", zorder=3, label=f"Main freq: {peak_f:.2f} Hz")
    ax.axvline(peak_f, color="black", linestyle="--", alpha=0.6)
    ax.set_title("Demo 2: Seismic Signal Frequency Spectrum (FFT)")
    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel("Magnitude")
    ax.set_xlim(0, fmax)
    ax.grid(alpha=0.28)
    ax.legend(loc="upper right")
    savefig(fig, out_path)
    return peak_f


def plot_building_frequency_responses(
    buildings: Dict[str, BuildingSystem], out_path: Path
) -> None:
    f = np.linspace(0.05, 10.0, 2000)
    fig, ax = plt.subplots(figsize=(11, 5.2))

    colors = ["#ff7f0e", "#2ca02c", "#1f77b4"]
    for (label, bld), c in zip(buildings.items(), colors):
        h = bld.frequency_response(f)
        ax.plot(f, h, label=label, color=c)
        idx = np.argmax(h)
        ax.scatter([f[idx]], [h[idx]], color=c, s=36)
        ax.text(f[idx] + 0.1, h[idx], f"peak @ {f[idx]:.2f} Hz", color=c, fontsize=11)

    ax.set_title("Demo 3: Building Frequency Responses and Resonance Peaks")
    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel("Response Magnitude |H(jω)|")
    ax.set_xlim(0, 6.0)
    ax.grid(alpha=0.28)
    ax.legend(loc="upper right")
    savefig(fig, out_path)


def plot_responses_real_scale(
    t: np.ndarray, a_g: np.ndarray, responses: Dict[str, np.ndarray], out_path: Path
) -> None:
    fig, axs = plt.subplots(4, 1, figsize=(12, 8.5), sharex=True)
    axs[0].plot(t, a_g, color="#d62728")
    axs[0].set_title("Demo 4: Same Input, Different System Outputs (Real Scale)")
    axs[0].set_ylabel("a_g(t)")
    axs[0].grid(alpha=0.28)

    colors = ["#ff7f0e", "#2ca02c", "#1f77b4"]
    for i, ((name, x), c) in enumerate(zip(responses.items(), colors), start=1):
        axs[i].plot(t, x, color=c, label=name)
        axs[i].set_ylabel("x(t)")
        axs[i].grid(alpha=0.28)
        axs[i].legend(loc="upper right")

    axs[-1].set_xlabel("Time (s)")
    savefig(fig, out_path)


def plot_responses_normalized(
    t: np.ndarray, responses_norm: Dict[str, np.ndarray], out_path: Path
) -> None:
    fig, ax = plt.subplots(figsize=(12, 5.2))
    colors = ["#ff7f0e", "#2ca02c", "#1f77b4"]
    for (name, x), c in zip(responses_norm.items(), colors):
        ax.plot(t, x, label=name, color=c)

    ax.set_title("Demo 4b: Normalized Building Responses")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Normalized displacement x(t)")
    ax.grid(alpha=0.28)
    ax.legend(loc="upper right")
    savefig(fig, out_path)


def plot_damping_comparison(
    t: np.ndarray,
    response_by_zeta: Dict[str, np.ndarray],
    out_path: Path,
    f_n: float,
) -> None:
    fig, ax = plt.subplots(figsize=(12, 5.2))
    colors = ["#d62728", "#1f77b4", "#2ca02c"]
    for (name, x), c in zip(response_by_zeta.items(), colors):
        ax.plot(t, x, label=name, color=c)
    ax.set_title(f"Demo 5: Damping Effect on Response (f_n={f_n:.1f} Hz)")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Relative displacement x(t)")
    ax.grid(alpha=0.28)
    ax.legend(loc="upper right")
    savefig(fig, out_path)


def plot_input_and_response_overview(
    t: np.ndarray, a_g: np.ndarray, x: np.ndarray, out_path: Path, title_suffix: str
) -> None:
    fig, axs = plt.subplots(2, 1, figsize=(11.5, 6.2), sharex=True)
    axs[0].plot(t, a_g, color="#d62728")
    axs[0].set_ylabel("a_g(t)")
    axs[0].grid(alpha=0.28)
    axs[0].set_title(f"Input and Response Overview ({title_suffix})")

    axs[1].plot(t, x, color="#2ca02c")
    axs[1].set_ylabel("x(t)")
    axs[1].set_xlabel("Time (s)")
    axs[1].grid(alpha=0.28)
    savefig(fig, out_path)

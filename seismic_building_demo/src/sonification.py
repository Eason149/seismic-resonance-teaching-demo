from pathlib import Path

import numpy as np
from scipy.io import wavfile
from scipy.signal import resample


def _loop_with_crossfade(x: np.ndarray, n_out: int, crossfade_len: int) -> np.ndarray:
    """Repeat x to length n_out using overlap-add crossfade between loop boundaries."""
    if len(x) == 0:
        return np.zeros(n_out, dtype=float)
    if len(x) >= n_out:
        return x[:n_out].copy()

    cf = int(max(1, min(crossfade_len, len(x) // 4)))
    out = x.copy()
    while len(out) < n_out:
        remain = n_out - len(out)
        chunk = x[: min(len(x), remain + cf)].copy()
        if len(out) >= cf and len(chunk) >= cf:
            fade_out = np.linspace(1.0, 0.0, cf, endpoint=True)
            fade_in = np.linspace(0.0, 1.0, cf, endpoint=True)
            out[-cf:] = out[-cf:] * fade_out + chunk[:cf] * fade_in
            out = np.concatenate([out, chunk[cf:]])
        else:
            out = np.concatenate([out, chunk])
    return out[:n_out]


def normalize_audio(x: np.ndarray, peak: float = 0.8) -> np.ndarray:
    m = np.max(np.abs(x))
    if m <= 0:
        return np.zeros_like(x, dtype=np.float32)
    return (peak * x / m).astype(np.float32)


def sonify_signal(
    x: np.ndarray,
    fs_signal: float,
    out_path: Path,
    audio_fs: int = 44100,
    speed_factor: float = 16.0,
    target_duration_sec: float = 10.0,
    target_peak: float = 0.95,
    reference_peak: float | None = None,
    gain: float = 1.0,
    target_rms: float | None = None,
    pre_emphasis: float = 0.18,
    crossfade_ms: float = 80.0,
) -> None:
    """
    Convert low-frequency signal to audible WAV by time compression.
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)
    n_fast = max(1, int(len(x) * audio_fs / (fs_signal * speed_factor)))
    x_fast = resample(x, n_fast)
    x_fast = x_fast - np.mean(x_fast)
    # Mild pre-emphasis: keeps waveform character while improving audibility.
    if len(x_fast) > 1:
        pe = float(np.clip(pre_emphasis, 0.0, 0.95))
        x_fast = (1.0 - pe) * x_fast + pe * np.concatenate([[0.0], np.diff(x_fast)])

    # Extend/fit to a fixed classroom-friendly duration.
    n_out = max(1, int(target_duration_sec * audio_fs))
    if len(x_fast) < n_out:
        cf = int(audio_fs * crossfade_ms / 1000.0)
        x_audio = _loop_with_crossfade(x_fast, n_out, cf)
    else:
        x_audio = x_fast[:n_out]

    # Use a shared reference peak so different files preserve relative loudness differences.
    if reference_peak is None or reference_peak <= 0:
        scale_ref = np.max(np.abs(x_audio))
    else:
        scale_ref = reference_peak
    if scale_ref <= 0:
        y = np.zeros_like(x_audio, dtype=np.float32)
    else:
        y = np.clip((target_peak / scale_ref) * x_audio, -target_peak, target_peak).astype(
            np.float32
        )
    if gain != 1.0:
        y = np.clip(y * gain, -0.98, 0.98).astype(np.float32)

    # Optional loudness lift: keep quiet signals audible without fully flattening dynamics.
    if target_rms is not None and target_rms > 0:
        cur_rms = float(np.sqrt(np.mean(y.astype(np.float64) ** 2)))
        if cur_rms > 1e-9 and cur_rms < target_rms:
            boost = target_rms / cur_rms
            y = np.clip(y * boost, -0.98, 0.98).astype(np.float32)

    # Short fade in/out to avoid click.
    fade_len = min(int(0.02 * audio_fs), len(y) // 4)
    if fade_len > 1:
        fade_in = np.linspace(0.0, 1.0, fade_len)
        fade_out = np.linspace(1.0, 0.0, fade_len)
        y[:fade_len] *= fade_in
        y[-fade_len:] *= fade_out

    wav_i16 = np.int16(np.clip(y, -1.0, 1.0) * 32767)
    wavfile.write(str(out_path), audio_fs, wav_i16)

from pathlib import Path

from src.animation import create_building_animation, create_three_building_damping_animation
from src.building_system import BuildingSystem, default_buildings, normalized_signals, peak_metrics
from src.signal_generation import dominant_frequency, generate_seismic_signal, generate_time_vector
from src.sonification import sonify_signal
from src.visualization import (
    plot_building_frequency_responses,
    plot_damping_comparison,
    plot_input_and_response_overview,
    plot_responses_normalized,
    plot_responses_real_scale,
    plot_seismic_waveform,
    plot_spectrum,
    setup_style,
)


def ensure_dirs(base: Path) -> None:
    for p in [
        base / "outputs",
        base / "outputs" / "figures",
        base / "outputs" / "animations",
        base / "outputs" / "audio",
    ]:
        p.mkdir(parents=True, exist_ok=True)


def run_all_demos(quick: bool = True) -> list[str]:
    base = Path(__file__).resolve().parent
    ensure_dirs(base)
    setup_style()

    fs = 200.0
    duration = 40.0
    t = generate_time_vector(fs=fs, duration=duration)
    a_g = generate_seismic_signal(t)

    created: list[str] = []

    # Demo 1
    p = base / "outputs" / "figures" / "01_seismic_input_waveform.png"
    plot_seismic_waveform(t, a_g, p)
    created.append(str(p))

    # Demo 2
    p = base / "outputs" / "figures" / "02_seismic_frequency_spectrum.png"
    peak_f = plot_spectrum(t, a_g, fs=fs, out_path=p, fmax=10.0)
    created.append(str(p))

    # Demo 3
    buildings = default_buildings(zeta=0.05)
    p = base / "outputs" / "figures" / "03_building_frequency_response.png"
    plot_building_frequency_responses(buildings, p)
    created.append(str(p))

    # Demo 4
    responses = {label: b.simulate_response(t, a_g) for label, b in buildings.items()}
    p = base / "outputs" / "figures" / "04a_responses_real_scale.png"
    plot_responses_real_scale(t, a_g, responses, p)
    created.append(str(p))

    responses_norm = normalized_signals(responses)
    p = base / "outputs" / "figures" / "04b_responses_normalized.png"
    plot_responses_normalized(t, responses_norm, p)
    created.append(str(p))

    # Optional additional overview (kept for classroom flexibility)
    p = base / "outputs" / "figures" / "04_different_building_responses.png"
    mid_resp = responses["Mid-rise (f_n=1.2 Hz)"]
    plot_input_and_response_overview(t, a_g, mid_resp, p, "Mid-rise Example")
    created.append(str(p))

    # Demo 5: damping comparison at near-resonant building
    f_n_demo = 1.2
    zetas = [0.02, 0.05, 0.15]
    damping_resp = {}
    for z in zetas:
        b = BuildingSystem(name=f"f_n={f_n_demo}", f_n=f_n_demo, zeta=z)
        damping_resp[f"zeta={z:.2f}"] = b.simulate_response(t, a_g)
    p = base / "outputs" / "figures" / "05_damping_comparison.png"
    plot_damping_comparison(t, damping_resp, p, f_n=f_n_demo)
    created.append(str(p))

    # Demo 6: animations
    resonance_building = BuildingSystem("Resonance case", f_n=peak_f, zeta=0.02)
    x_res = resonance_building.simulate_response(t, a_g)
    p = base / "outputs" / "animations" / "06a_resonance_building.gif"
    create_building_animation(
        t,
        a_g,
        x_res,
        out_path=p,
        title="Demo 6A: Resonance-Dominant Building Vibration",
        quick=quick,
        visual_scale=18.0,
        collapse_drift_ratio=0.115,
        collapse_ag_ratio=0.70,
    )
    created.append(str(p))

    damped_building = BuildingSystem("Damped case", f_n=peak_f, zeta=0.15)
    x_damped = damped_building.simulate_response(t, a_g)
    p = base / "outputs" / "animations" / "06b_damped_building.gif"
    create_building_animation(
        t,
        a_g,
        x_damped,
        out_path=p,
        title="Demo 6B: Higher Damping Building Vibration",
        quick=quick,
        visual_scale=18.0,
        collapse_drift_ratio=0.13,
        collapse_ag_ratio=0.70,
    )
    created.append(str(p))

    # Demo 6C/6D: low/mid/high-rise comparison under low/high damping
    low_damp_buildings = default_buildings(zeta=0.02)
    high_damp_buildings = default_buildings(zeta=0.15)
    low_low = low_damp_buildings["Low-rise (f_n=2.5 Hz)"].simulate_response(t, a_g)
    low_mid = low_damp_buildings["Mid-rise (f_n=1.2 Hz)"].simulate_response(t, a_g)
    low_high = low_damp_buildings["High-rise (f_n=0.5 Hz)"].simulate_response(t, a_g)
    high_low = high_damp_buildings["Low-rise (f_n=2.5 Hz)"].simulate_response(t, a_g)
    high_mid = high_damp_buildings["Mid-rise (f_n=1.2 Hz)"].simulate_response(t, a_g)
    high_high = high_damp_buildings["High-rise (f_n=0.5 Hz)"].simulate_response(t, a_g)

    p = base / "outputs" / "animations" / "06c_three_buildings_low_damping.gif"
    create_three_building_damping_animation(
        t=t,
        a_g=a_g,
        x_low=low_low,
        x_mid=low_mid,
        x_high=low_high,
        out_path=p,
        title="Demo 6C: Low/Mid/High-rise under Low Damping",
        damping_label="Low damping (zeta=0.02)",
        damper_count=1,
        quick=quick,
        visual_scale=18.0,
    )
    created.append(str(p))

    p = base / "outputs" / "animations" / "06d_three_buildings_high_damping.gif"
    create_three_building_damping_animation(
        t=t,
        a_g=a_g,
        x_low=high_low,
        x_mid=high_mid,
        x_high=high_high,
        out_path=p,
        title="Demo 6D: Low/Mid/High-rise under Higher Damping",
        damping_label="Higher damping (zeta=0.15)",
        damper_count=3,
        quick=quick,
        visual_scale=18.0,
    )
    created.append(str(p))

    # Required alias filename
    p_alias = base / "outputs" / "animations" / "06_building_vibration_animation.gif"
    if p_alias.exists():
        p_alias.unlink()
    p_alias.write_bytes((base / "outputs" / "animations" / "06a_resonance_building.gif").read_bytes())
    created.append(str(p_alias))

    # Demo 7: sonification
    # Audible + fixed 10s clips for classroom playback.
    speed = 16.0
    speed_damped = 28.0
    duration_audio = 10.0
    p = base / "outputs" / "audio" / "seismic_input.wav"
    sonify_signal(
        a_g,
        fs_signal=fs,
        out_path=p,
        audio_fs=44100,
        speed_factor=speed,
        target_duration_sec=duration_audio,
        target_peak=0.95,
        gain=1.22,
        pre_emphasis=0.16,
        crossfade_ms=90.0,
    )
    created.append(str(p))

    # Shared reference to preserve amplitude contrast between resonance and damping.
    shared_ref = max(float(abs(x_res).max()), float(abs(x_damped).max()))
    p = base / "outputs" / "audio" / "building_response_resonance.wav"
    sonify_signal(
        x_res,
        fs_signal=fs,
        out_path=p,
        audio_fs=44100,
        speed_factor=speed,
        target_duration_sec=duration_audio,
        target_peak=0.95,
        reference_peak=shared_ref,
        gain=1.26,
        pre_emphasis=0.08,
        crossfade_ms=90.0,
    )
    created.append(str(p))

    p = base / "outputs" / "audio" / "building_response_damped.wav"
    sonify_signal(
        x_damped,
        fs_signal=fs,
        out_path=p,
        audio_fs=44100,
        speed_factor=speed_damped,
        target_duration_sec=duration_audio,
        target_peak=0.95,
        reference_peak=None,
        gain=1.45,
        target_rms=0.20,
        pre_emphasis=0.26,
        crossfade_ms=90.0,
    )
    created.append(str(p))

    # Console summary
    print("\n=== Seismic-Building Demo Completed ===")
    print(f"Sampling rate: {fs:.0f} Hz, duration: {duration:.1f} s")
    print(f"Dominant seismic frequency (Demo 2): {peak_f:.3f} Hz")
    print("\nPeak response metrics (Demo 4):")
    for name, (peak, rms) in peak_metrics(responses).items():
        print(f"  - {name}: peak={peak:.4f}, rms={rms:.4f}")
    print("\nGenerated files:")
    for f in created:
        print(f"  - {f}")
    return created


if __name__ == "__main__":
    # quick=True reduces animation frames and runtime for classroom laptops.
    run_all_demos(quick=True)

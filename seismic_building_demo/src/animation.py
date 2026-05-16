from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.patches import Polygon, Rectangle


def create_building_animation(
    t: np.ndarray,
    a_g: np.ndarray,
    x: np.ndarray,
    out_path: Path,
    title: str,
    quick: bool = True,
    visual_scale: float = 18.0,
    collapse_drift_ratio: float = 0.08,
    collapse_ag_ratio: float = 0.65,
) -> None:
    """
    Create a side-by-side animation:
    left: seismic input waveform + time cursor
    right: simplified multi-story building swaying with x(t)
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)

    n = len(t)
    step = 8 if quick else 3
    idx = np.arange(0, n, step)

    x_vis = visual_scale * x
    xlim = max(np.max(np.abs(x_vis)), 1.0) * 1.6
    building_height = 10.0
    floors = 8

    fig = plt.figure(figsize=(11.5, 5.2), facecolor="white")
    gs = fig.add_gridspec(1, 2, width_ratios=[1.25, 1.0])
    ax_wave = fig.add_subplot(gs[0, 0])
    ax_bld = fig.add_subplot(gs[0, 1])

    # Left panel
    ax_wave.plot(t, a_g, color="#d62728", label="Seismic input a_g(t)")
    cursor = ax_wave.axvline(t[0], color="black", linestyle="--", lw=1.6)
    ax_wave.set_title("Seismic Input with Time Cursor")
    ax_wave.set_xlabel("Time (s)")
    ax_wave.set_ylabel("Acceleration")
    ax_wave.grid(alpha=0.25)
    ax_wave.legend(loc="upper right")

    # Right panel
    ax_bld.set_title("Building Sway (visual scaling applied)")
    ax_bld.set_xlim(-xlim, xlim)
    ax_bld.set_ylim(0, building_height + 1.2)
    ax_bld.set_xlabel("Lateral displacement (visual)")
    ax_bld.set_yticks([])
    ax_bld.grid(alpha=0.15)

    # Ground
    ax_bld.plot([-xlim, xlim], [0.2, 0.2], color="black", lw=1.8)
    floor_y = np.linspace(1.2, building_height - 0.35, floors)
    width = 2.8
    btm_pad = 0.25
    shear_gain = 0.025

    # Filled building body, then draw floor lines inside it.
    initial_poly = np.array(
        [[-width / 2, btm_pad], [width / 2, btm_pad], [width / 2, building_height], [-width / 2, building_height]]
    )
    body_patch = Polygon(
        initial_poly,
        closed=True,
        facecolor="#4f6d8a",
        edgecolor="#1f2e3c",
        linewidth=2.2,
        alpha=0.95,
    )
    ax_bld.add_patch(body_patch)

    floor_lines = []
    for fy in floor_y:
        line, = ax_bld.plot(
            [-width / 2, width / 2],
            [fy, fy],
            color="#dfe8f0",
            lw=2.2,
            solid_capstyle="butt",
        )
        floor_lines.append(line)

    txt = ax_bld.text(
        0.02,
        0.98,
        "",
        transform=ax_bld.transAxes,
        va="top",
        ha="left",
        fontsize=11,
        bbox={"boxstyle": "round,pad=0.25", "fc": "white", "ec": "gray", "alpha": 0.9},
    )

    fig.suptitle(title, fontsize=14)
    state = {
        "collapsed": False,
        "collapse_start": -1,
        "collapse_dir": 1.0,
        "collapse_poly": initial_poly.copy(),
        "collapse_floor_segments": [],
        "collapse_disp": np.array([]),
        "collapse_y": np.array([]),
    }
    ag_peak = float(np.max(np.abs(a_g))) if len(a_g) > 0 else 0.0

    def rotate_points(points: np.ndarray, pivot: np.ndarray, angle_rad: float) -> np.ndarray:
        c = np.cos(angle_rad)
        s = np.sin(angle_rad)
        p = points - pivot
        r = np.empty_like(points)
        r[:, 0] = c * p[:, 0] - s * p[:, 1]
        r[:, 1] = s * p[:, 0] + c * p[:, 1]
        return r + pivot

    def update(frame_i: int):
        i = idx[frame_i]
        cursor.set_xdata([t[i], t[i]])
        shift = x_vis[i]

        if not state["collapsed"]:
            # More realistic deformation: lower floors move less, upper floors move more.
            y_nodes = np.linspace(btm_pad, building_height, 28)
            ratio_nodes = y_nodes / building_height
            # Reduce rubber-band look: more rigid-body translation + mild height-dependent shear.
            disp_nodes = shift * (0.58 + 0.42 * (ratio_nodes**1.15)) + shear_gain * shift * ratio_nodes

            left_x = disp_nodes - width / 2
            right_x = disp_nodes + width / 2
            poly = np.vstack(
                [
                    np.column_stack([left_x, y_nodes]),
                    np.column_stack([right_x[::-1], y_nodes[::-1]]),
                ]
            )
            body_patch.set_xy(poly)

            for j, fy in enumerate(floor_y):
                r = fy / building_height
                floor_disp = shift * (0.58 + 0.42 * (r**1.15)) + shear_gain * shift * r
                floor_lines[j].set_data([floor_disp - width / 2, floor_disp + width / 2], [fy, fy])

            top_disp = shift * (0.58 + 0.42 * (1.0**1.15)) + shear_gain * shift
            base_disp = shift * 0.58
            drift_ratio = abs(top_disp - base_disp) / building_height

            strong_shaking = ag_peak > 0 and abs(a_g[i]) >= collapse_ag_ratio * ag_peak
            if drift_ratio >= collapse_drift_ratio and strong_shaking:
                state["collapsed"] = True
                state["collapse_start"] = frame_i
                state["collapse_dir"] = 1.0 if top_disp >= base_disp else -1.0
                state["collapse_poly"] = body_patch.get_xy().copy()
                state["collapse_floor_segments"] = []
                for line in floor_lines:
                    lx, ly = line.get_data()
                    state["collapse_floor_segments"].append(
                        np.array([[lx[0], ly[0]], [lx[1], ly[1]]], dtype=float)
                    )
                state["collapse_y"] = y_nodes.copy()
                state["collapse_disp"] = disp_nodes.copy()
                status = "COLLAPSE TRIGGERED"
            else:
                status = "SAFE"
        else:
            # Progressive collapse: height shrinks, permanent lean increases, then minor fall.
            elapsed = frame_i - state["collapse_start"]
            progress = min(1.0, elapsed / 26.0)

            y0 = state["collapse_y"]
            d0 = state["collapse_disp"]
            if len(y0) == 0 or len(d0) == 0:
                y0 = np.linspace(btm_pad, building_height, 28)
                d0 = np.zeros_like(y0)

            # Vertical compression (pancake effect) + permanent drift.
            y_new = btm_pad + (y0 - btm_pad) * (1.0 - 0.52 * progress)
            lean = state["collapse_dir"] * (0.45 * width * progress)
            d_new = d0 + lean * ((y0 - btm_pad) / (building_height - btm_pad + 1e-9))

            left_x = d_new - width / 2
            right_x = d_new + width / 2
            poly = np.vstack(
                [
                    np.column_stack([left_x, y_new]),
                    np.column_stack([right_x[::-1], y_new[::-1]]),
                ]
            )

            # Late-stage slight global rotation and sinking for final failure look.
            angle = state["collapse_dir"] * np.deg2rad(26.0 * max(0.0, progress - 0.35))
            pivot = np.array([left_x[0] if state["collapse_dir"] > 0 else right_x[0], btm_pad])
            fallen = rotate_points(poly, pivot, angle)
            fallen[:, 1] -= 0.9 * max(0.0, progress - 0.45)
            body_patch.set_xy(fallen)

            for j, line in enumerate(floor_lines):
                seg0 = state["collapse_floor_segments"][j]
                y_floor = seg0[0, 1]
                y_floor_new = btm_pad + (y_floor - btm_pad) * (1.0 - 0.52 * progress)
                ratio = (y_floor - btm_pad) / (building_height - btm_pad + 1e-9)
                floor_lean = state["collapse_dir"] * (0.45 * width * progress) * ratio
                d_floor = floor_lean + np.interp(y_floor, y0, d0)
                x1 = d_floor - width / 2
                x2 = d_floor + width / 2
                seg = np.array([[x1, y_floor_new], [x2, y_floor_new]], dtype=float)
                seg = rotate_points(seg, pivot, angle)
                seg[:, 1] -= 0.9 * max(0.0, progress - 0.45)
                line.set_data(seg[:, 0], seg[:, 1])
            drift_ratio = collapse_drift_ratio
            status = "COLLAPSED"

        txt.set_text(
            f"t = {t[i]:5.2f} s\nx(t) = {x[i]: .4f}\nvisual scale = {visual_scale:.1f}x\n"
            f"drift ratio = {drift_ratio:.3f}\nstatus = {status}"
        )
        return [cursor, body_patch, txt, *floor_lines]

    anim = FuncAnimation(fig, update, frames=len(idx), interval=35, blit=True)
    writer = PillowWriter(fps=20 if quick else 25)
    anim.save(str(out_path), writer=writer)
    plt.close(fig)


def create_three_building_damping_animation(
    t: np.ndarray,
    a_g: np.ndarray,
    x_low: np.ndarray,
    x_mid: np.ndarray,
    x_high: np.ndarray,
    out_path: Path,
    title: str,
    damping_label: str,
    damper_count: int,
    quick: bool = True,
    visual_scale: float = 18.0,
) -> None:
    """
    Left: seismic input waveform + cursor.
    Right: low/mid/high-rise buildings with fixed geometry for fair comparison.
    Damping is represented by added dampers (higher count = higher damping).
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)

    n = len(t)
    step = 8 if quick else 3
    idx = np.arange(0, n, step)

    x_low_vis = visual_scale * x_low
    x_mid_vis = visual_scale * x_mid
    x_high_vis = visual_scale * x_high

    xlim = max(
        float(np.max(np.abs(x_low_vis))),
        float(np.max(np.abs(x_mid_vis))),
        float(np.max(np.abs(x_high_vis))),
        1.0,
    ) * 1.25

    fig = plt.figure(figsize=(13.5, 5.8), facecolor="white")
    gs = fig.add_gridspec(1, 2, width_ratios=[1.15, 1.35])
    ax_wave = fig.add_subplot(gs[0, 0])
    ax_bld = fig.add_subplot(gs[0, 1])

    ax_wave.plot(t, a_g, color="#d62728", label="Seismic input a_g(t)")
    cursor = ax_wave.axvline(t[0], color="black", linestyle="--", lw=1.6)
    ax_wave.set_title("Seismic Input with Time Cursor")
    ax_wave.set_xlabel("Time (s)")
    ax_wave.set_ylabel("Acceleration")
    ax_wave.grid(alpha=0.25)
    ax_wave.legend(loc="upper right")

    ax_bld.set_title(f"Low/Mid/High-rise Comparison ({damping_label})")
    ax_bld.set_xlim(-12.0, 12.0)
    ax_bld.set_ylim(0, 12.8)
    ax_bld.set_xticks([])
    ax_bld.set_yticks([])
    ax_bld.grid(alpha=0.12)
    ax_bld.plot([-12.0, 12.0], [0.25, 0.25], color="black", lw=1.8)

    centers = [-7.0, 0.0, 7.0]
    heights = [6.0, 8.5, 11.0]
    floors = [4, 6, 9]
    widths = [2.1, 2.1, 2.1]
    labels = ["Low-rise", "Mid-rise", "High-rise"]
    colors = ["#8ecae6", "#4f6d8a", "#355070"]
    signals = [x_low_vis, x_mid_vis, x_high_vis]

    bodies: list[Polygon] = []
    floor_lines: list[list] = []
    label_text = []
    base_y = 0.25

    for c, h, nf, w, lb, fc in zip(centers, heights, floors, widths, labels, colors):
        poly = np.array([[c - w / 2, base_y], [c + w / 2, base_y], [c + w / 2, h], [c - w / 2, h]])
        patch = Polygon(poly, closed=True, facecolor=fc, edgecolor="#1f2e3c", linewidth=2.0, alpha=0.95)
        ax_bld.add_patch(patch)
        bodies.append(patch)

        y_f = np.linspace(base_y + 0.9, h - 0.4, nf)
        lines = []
        for fy in y_f:
            line, = ax_bld.plot([c - w / 2, c + w / 2], [fy, fy], color="#e6eef5", lw=2.0, solid_capstyle="butt")
            lines.append(line)
        floor_lines.append(lines)
        label_text.append(ax_bld.text(c, h + 0.45, lb, ha="center", va="bottom", fontsize=10))

    # Damper icon(s): fixed size, only count changes with damping level.
    damper_artists = []
    for k in range(max(1, damper_count)):
        x0 = -10.8 + 1.2 * k
        y0 = 0.55
        r = Rectangle((x0, y0), 0.65, 0.28, facecolor="#adb5bd", edgecolor="#495057", linewidth=1.1)
        ax_bld.add_patch(r)
        damper_artists.append(r)
        l1, = ax_bld.plot([x0 + 0.65, x0 + 1.0], [y0 + 0.14, y0 + 0.14], color="#495057", lw=1.4)
        damper_artists.append(l1)

    txt = ax_bld.text(
        0.02,
        0.98,
        "",
        transform=ax_bld.transAxes,
        va="top",
        ha="left",
        fontsize=11,
        bbox={"boxstyle": "round,pad=0.25", "fc": "white", "ec": "gray", "alpha": 0.9},
    )
    fig.suptitle(title, fontsize=14)

    def update(frame_i: int):
        i = idx[frame_i]
        cursor.set_xdata([t[i], t[i]])

        for b_idx, (c, h, w, sig, patch) in enumerate(zip(centers, heights, widths, signals, bodies)):
            shift = np.clip(sig[i], -xlim, xlim)
            y_nodes = np.linspace(base_y, h, 24)
            ratio = np.clip(y_nodes / h, 0.0, 1.0)
            disp = shift * (0.62 + 0.38 * (ratio**1.08))
            left = c + disp - w / 2
            right = c + disp + w / 2
            poly = np.vstack([np.column_stack([left, y_nodes]), np.column_stack([right[::-1], y_nodes[::-1]])])
            patch.set_xy(poly)

            y_f = np.linspace(base_y + 0.9, h - 0.4, floors[b_idx])
            for j, fy in enumerate(y_f):
                r = fy / h
                fd = shift * (0.62 + 0.38 * (r**1.08))
                floor_lines[b_idx][j].set_data([c + fd - w / 2, c + fd + w / 2], [fy, fy])

        txt.set_text(
            f"t = {t[i]:5.2f} s\n"
            f"damping = {damping_label}\n"
            f"damper units = {max(1, damper_count)}\n"
            f"visual scale = {visual_scale:.1f}x"
        )
        artists = [cursor, txt, *bodies, *label_text, *damper_artists]
        for group in floor_lines:
            artists.extend(group)
        return artists

    anim = FuncAnimation(fig, update, frames=len(idx), interval=35, blit=True)
    writer = PillowWriter(fps=20 if quick else 25)
    anim.save(str(out_path), writer=writer)
    plt.close(fig)

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.font_manager as font_manager
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Rectangle
import numpy as np
import scienceplots  # noqa: F401  Registers the SciencePlots style sheets.
from scipy import signal

try:
    from .common import ROOT, read_json
    from .yang_2026 import REFERENCE_PATH, REPORT_PATH, _continuous_filter_coefficients
except ImportError:
    from common import ROOT, read_json
    from yang_2026 import REFERENCE_PATH, REPORT_PATH, _continuous_filter_coefficients


DIGITIZED_PATH = ROOT / "RocketRecoveryCases" / "Paper_Yang_2026" / "reference" / "digitized" / "yang-2026-fig09-11-digitization.json"
LANDING_REPORT_PATH = ROOT / "RocketRecoveryCases" / "Paper_Yang_2026" / "identified_landing_model" / "yang-2026-identified-landing-report.json"
BARGE_RAO_PATH = ROOT / "RocketRecoveryCases" / "Barge_120x50" / "Output" / "RocketRecovery" / "deck-point-rao-medium.json"
BARGE_SEA_PATH = ROOT / "RocketRecoveryCases" / "Barge_120x50" / "Output" / "RocketRecovery" / "sea-state-response.json"
HYDRO_CONVERGENCE_PATH = ROOT / "RocketRecoveryCases" / "Barge_120x50" / "validation" / "barge-hydrodynamic-convergence.json"
BARGE_SENSITIVITY_PATH = ROOT / "RocketRecoveryCases" / "Barge_120x50" / "Output" / "RocketRecovery" / "wave-sensitivity-revision-600s.json"
BARGE_DURATION_PATH = ROOT / "RocketRecoveryCases" / "Barge_120x50" / "Output" / "RocketRecovery" / "wave-duration-sensitivity.json"
CHRONO_REPORT_PATH = ROOT / "RocketRecoveryCases" / "Chrono_LeggedRecovery" / "chrono-same-platform-multibody-report.json"
CHRONO_RESPONSE_PATH = ROOT / "RocketRecoveryCases" / "Chrono_LeggedRecovery" / "Output" / "RocketRecovery" / "chrono-same-platform-multibody-response.json"
IDENTIFIABILITY_PATH = ROOT / "RocketRecoveryCases" / "Paper_Yang_2026" / "identified_landing_model" / "yang-2026-identifiability-report.json"
PLATFORM_CONFIG_PATH = ROOT / "RocketRecoveryCases" / "Barge_120x50" / "platform_config.json"
FIGURE_DIR = ROOT / "paper" / "yang_2026_extension" / "figures"
AUDIT_FIGURE_DIR = ROOT / "paper" / "yang_2026_extension" / "audit_figures"


COLORS = {
    "model": "#0072B2",
    "reference": "#333333",
    "hydro": "#009E73",
    "contact": "#D55E00",
    "coupling": "#CC79A7",
    "secondary": "#56B4E9",
    "flexible": "#0072B2",
    "rigid": "#D55E00",
    "test": "#009E73",
    "digitized": "#333333",
}


def configure_style() -> None:
    plt.style.use(["science", "no-latex"])
    font_manager.findfont("Times New Roman", fallback_to_default=False)
    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": ["Times New Roman"],
            "mathtext.fontset": "stix",
            "font.size": 9.0,
            "axes.titlesize": 9.4,
            "axes.labelsize": 9.0,
            "xtick.labelsize": 8.1,
            "ytick.labelsize": 8.1,
            "legend.fontsize": 7.8,
            "figure.dpi": 180,
            "savefig.dpi": 600,
            "savefig.transparent": False,
            "svg.fonttype": "none",
            "axes.grid": True,
            "grid.alpha": 0.18,
            "grid.linewidth": 0.45,
            "lines.linewidth": 1.2,
            "axes.linewidth": 0.65,
            "legend.frameon": False,
            "figure.constrained_layout.use": True,
        }
    )


def save_figure(fig: plt.Figure, stem: str, output_dir: Path = FIGURE_DIR) -> list[str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for suffix in ("png", "svg"):
        path = output_dir / f"{stem}.{suffix}"
        fig.savefig(path, bbox_inches="tight", facecolor="white")
        paths.append(str(path.relative_to(ROOT).as_posix()))
    plt.close(fig)
    return paths


def coupled_framework_figure() -> list[str]:
    fig, axis = plt.subplots(figsize=(7.15, 3.35))
    axis.set_xlim(0.0, 10.0)
    axis.set_ylim(0.0, 5.0)
    axis.axis("off")

    boxes = [
        (0.35, 3.2, 2.05, 1.05, "Potential-flow BEM\npanel mesh", COLORS["hydro"]),
        (3.0, 3.2, 2.05, 1.05, "Hydrodynamic data\n$A(\\omega), B(\\omega), F_w(\\omega)$", COLORS["hydro"]),
        (5.65, 3.2, 2.05, 1.05, "Radiation-memory\nplatform dynamics", COLORS["model"]),
        (7.8, 1.0, 1.85, 1.1, "Multibody dynamics\nvehicle and four legs", COLORS["contact"]),
        (4.55, 0.75, 2.05, 1.1, "Deck kinematics\nat four foot points", COLORS["coupling"]),
        (1.35, 0.75, 2.1, 1.1, "Wave synthesis\nJONSWAP realizations", COLORS["secondary"]),
    ]
    for x, y, width, height, label, color in boxes:
        axis.add_patch(Rectangle((x, y), width, height, facecolor="white", edgecolor=color, linewidth=1.25))
        axis.text(x + width / 2.0, y + height / 2.0, label, ha="center", va="center", fontsize=8.6)

    arrows = [
        ((2.4, 3.72), (3.0, 3.72), COLORS["hydro"], None),
        ((5.05, 3.72), (5.65, 3.72), COLORS["hydro"], None),
        ((3.45, 1.75), (5.9, 3.2), COLORS["secondary"], "$F_w(t)$"),
        ((6.2, 3.2), (5.7, 1.85), COLORS["coupling"], "platform pose"),
        ((6.6, 1.3), (7.8, 1.3), COLORS["coupling"], "deck pose"),
        ((8.6, 2.1), (7.3, 3.2), COLORS["contact"], "$F_z, M_x, M_y$ feedback\nother channels audited"),
    ]
    for start, end, color, label in arrows:
        axis.add_patch(FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=9, linewidth=1.0, color=color))
        if label:
            mx = (start[0] + end[0]) / 2.0
            my = (start[1] + end[1]) / 2.0
            axis.text(mx, my + 0.16, label, color=color, ha="center", va="center", fontsize=7.7)

    axis.text(0.35, 4.65, "Frequency-domain hydrodynamics", fontsize=8.4, weight="bold", color=COLORS["hydro"])
    axis.text(5.65, 4.65, "Time-domain coupled simulation", fontsize=8.4, weight="bold", color=COLORS["model"])
    axis.text(7.25, 0.25, "Fixed-point iteration; surge, sway and yaw constrained without mooring/DP data", fontsize=7.5, ha="center")
    return save_figure(fig, "fig01-coupled-framework")


def barge_geometry_figure(config: dict[str, Any], wave_report: dict[str, Any]) -> list[str]:
    length = float(config["platform"]["length_m"])
    beam = float(config["platform"]["beam_m"])
    draft = float(config["platform"]["draft_m"])
    deck_z = float(config["platform"]["deck_z_m"])
    nx = int(config["mesh"]["nx"])
    ny = int(config["mesh"]["ny"])
    nz = int(config["mesh"]["nz"])

    fig = plt.figure(figsize=(7.15, 4.05), layout="none")
    axis = fig.add_subplot(121, projection="3d")
    x = np.linspace(-length / 2.0, length / 2.0, nx + 1)
    y = np.linspace(-beam / 2.0, beam / 2.0, ny + 1)
    z = np.linspace(-draft, 0.0, nz + 1)

    for xv in x:
        axis.plot([xv, xv], [-beam / 2.0, beam / 2.0], [-draft, -draft], color="#8A8A8A", linewidth=0.35)
    for yv in y:
        axis.plot([-length / 2.0, length / 2.0], [yv, yv], [-draft, -draft], color="#8A8A8A", linewidth=0.35)
    for zv in z:
        axis.plot([-length / 2.0, length / 2.0], [-beam / 2.0, -beam / 2.0], [zv, zv], color="#8A8A8A", linewidth=0.35)
        axis.plot([-length / 2.0, length / 2.0], [beam / 2.0, beam / 2.0], [zv, zv], color="#8A8A8A", linewidth=0.35)
    for xv in x:
        axis.plot([xv, xv], [-beam / 2.0, -beam / 2.0], [-draft, 0.0], color="#8A8A8A", linewidth=0.35)
        axis.plot([xv, xv], [beam / 2.0, beam / 2.0], [-draft, 0.0], color="#8A8A8A", linewidth=0.35)
    for yv in y:
        axis.plot([-length / 2.0, -length / 2.0], [yv, yv], [-draft, 0.0], color="#8A8A8A", linewidth=0.35)
        axis.plot([length / 2.0, length / 2.0], [yv, yv], [-draft, 0.0], color="#8A8A8A", linewidth=0.35)

    corners_x = [-length / 2.0, length / 2.0, length / 2.0, -length / 2.0, -length / 2.0]
    corners_y = [-beam / 2.0, -beam / 2.0, beam / 2.0, beam / 2.0, -beam / 2.0]
    axis.plot(corners_x, corners_y, [deck_z] * 5, color=COLORS["model"], linewidth=1.4, label="deck outline")
    axis.plot(corners_x, corners_y, [0.0] * 5, color=COLORS["secondary"], linewidth=1.0, linestyle="--", label="waterline")

    center = next(point for point in wave_report["deck_points"]["all"] if point["id"] == "landing_center")
    px, py, pz = (float(value) for value in center["position_m"])
    axis.scatter(px, py, pz, marker="*", s=52, color=COLORS["contact"], depthshade=False, label="landing center")
    physical_points = wave_report["deck_points"]["physical_legs"]
    generic_points = [point for point in wave_report["deck_points"]["generic_sampling"] if point["id"] != "landing_center"]
    for point in physical_points:
        px, py, pz = (float(value) for value in point["position_m"])
        axis.scatter(px, py, pz, marker="o", s=21, facecolor="white", edgecolor=COLORS["contact"], depthshade=False)
    for point in generic_points:
        px, py, pz = (float(value) for value in point["position_m"])
        axis.scatter(px, py, pz, marker="x", s=19, color=COLORS["secondary"], depthshade=False)
    axis.plot([], [], [], marker="o", linestyle="None", markerfacecolor="white", markeredgecolor=COLORS["contact"], label="6.926 m leg proxy")
    axis.plot([], [], [], marker="x", linestyle="None", color=COLORS["secondary"], label=r"generic $\pm9$ m sample")

    axis.set_xlabel("$x$ (m)", labelpad=2)
    axis.set_ylabel("$y$ (m)", labelpad=2)
    axis.set_zlabel("$z$ (m)", labelpad=2)
    axis.set_xlim(-65.0, 65.0)
    axis.set_ylim(-32.0, 32.0)
    axis.set_zlim(-8.0, 5.0)
    axis.set_box_aspect((length, beam, 22.0))
    axis.view_init(elev=21.0, azim=-57.0)
    axis.set_title("Boundary-element geometry", pad=2)
    axis.grid(False)

    plan = fig.add_subplot(122)
    plan.add_patch(Rectangle((-length / 2.0, -beam / 2.0), length, beam, fill=False, edgecolor=COLORS["model"], linewidth=1.1))
    plan.scatter(0.0, 0.0, marker="*", s=70, color=COLORS["contact"], zorder=4)
    physical_xy = np.asarray([[float(point["position_m"][0]), float(point["position_m"][1])] for point in physical_points])
    closed_xy = np.vstack([physical_xy, physical_xy[0]])
    plan.plot(closed_xy[:, 0], closed_xy[:, 1], color=COLORS["contact"], linewidth=0.9, linestyle=":")
    plan.scatter(physical_xy[:, 0], physical_xy[:, 1], marker="o", s=34, facecolor="white", edgecolor=COLORS["contact"], zorder=3)
    generic_xy = np.asarray([[float(point["position_m"][0]), float(point["position_m"][1])] for point in generic_points])
    plan.scatter(generic_xy[:, 0], generic_xy[:, 1], marker="x", s=34, color=COLORS["secondary"], zorder=3)
    for point, (x_point, y_point) in zip(physical_points, physical_xy):
        plan.text(x_point + 0.45, y_point + 0.45, point["id"].replace("_", " "), fontsize=6.8)
    plan.set(xlim=(-12.0, 12.0), ylim=(-12.0, 12.0), xlabel="$x$ (m)", ylabel="$y$ (m)", title="Deck-center landing layout")
    plan.set_aspect("equal", adjustable="box")
    handles, labels = axis.get_legend_handles_labels()
    # Reserve a deterministic legend band below both axes.  The global
    # constrained-layout setting otherwise ignores subplots_adjust and lets
    # the legend cover the plan-view x axis in vector and document exports.
    fig.subplots_adjust(left=0.045, right=0.985, top=0.90, bottom=0.245, wspace=0.42)
    fig.legend(handles, labels, loc="lower center", bbox_to_anchor=(0.5, 0.025), ncol=3, frameon=False)
    return save_figure(fig, "fig02-barge-geometry-mesh")


def scalar_target_figure(reference: dict[str, Any]) -> list[str]:
    conditions = ["Y0_simultaneous", "Y1_1-2-1", "Y2_2-2"]
    labels = ["Simultaneous", "1-2-1", "2-2"]
    metric_specs = [
        ("peak_vertical_acceleration_g", "Peak axial acceleration", "g", 1.0),
        ("maximum_main_strut_load_n", "Maximum main-strut load", "kN", 1.0e-3),
        ("maximum_buffer_stroke_m", "Maximum buffer stroke", "mm", 1.0e3),
    ]
    fig, axes = plt.subplots(1, 3, figsize=(7.15, 2.55))
    x = np.arange(len(conditions), dtype=float)
    width = 0.24
    for axis, (metric, title, unit, scale) in zip(axes, metric_specs):
        rows = [next(row for row in reference["table_2"] if row["condition_id"] == condition and row["metric"] == metric) for condition in conditions]
        axis.bar(x - width, [row["flexible"] * scale for row in rows], width, label="Flexible model", color=COLORS["flexible"])
        axis.bar(x, [row["rigid"] * scale for row in rows], width, label="Rigid model", color=COLORS["rigid"])
        axis.bar(x + width, [row["test"] * scale for row in rows], width, label="Test (printed)", color=COLORS["test"])
        axis.set_title(title)
        axis.set_ylabel(unit)
        axis.set_xticks(x, labels)
        axis.tick_params(axis="x", rotation=18)
        if metric == "maximum_main_strut_load_n":
            axis.text(
                1.0 + width,
                rows[1]["test"] * scale,
                "Printed value\nflagged",
                ha="center",
                va="bottom",
                fontsize=7,
                color="#8a1c1c",
            )
    axes[0].legend(frameon=False, loc="upper right")
    fig.suptitle("Yang et al. (2026) Table 2 validation targets", fontsize=9.5)
    return save_figure(fig, "audit01-yang-published-scalar-targets", AUDIT_FIGURE_DIR)


def read_curve(path: Path) -> tuple[np.ndarray, np.ndarray]:
    with path.open("r", encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    return (
        np.asarray([float(row["time_s"]) for row in rows], dtype=float),
        np.asarray([float(row["value"]) for row in rows], dtype=float),
    )


def digitized_history_figure(digitized: dict[str, Any]) -> list[str]:
    condition_order = ["Y0_simultaneous", "Y1_1-2-1", "Y2_2-2"]
    condition_labels = ["Simultaneous", "1-2-1", "2-2"]
    metrics = [
        ("rocket_vertical_acceleration_mm_s2", "Acceleration", "m/s$^2$", 1.0e-3),
        ("main_strut_load_n", "Main-strut load", "kN", 1.0e-3),
        ("buffer_stroke_mm", "Buffer stroke", "mm", 1.0),
    ]
    fig, axes = plt.subplots(3, 3, figsize=(7.15, 5.1), sharex=False)
    for row_index, (condition, condition_label) in enumerate(zip(condition_order, condition_labels)):
        for column_index, (metric, title, unit, scale) in enumerate(metrics):
            curve = next(item for item in digitized["curves"] if item["condition_id"] == condition and item["metric"] == metric)
            time_s, values = read_curve(ROOT / curve["csv"])
            axis = axes[row_index, column_index]
            axis.scatter(time_s, values * scale, s=1.9, color=COLORS["digitized"], linewidths=0, label="Digitized test pixels")
            axis.set_xlim(curve["x_range"])
            axis.set_ylabel(unit)
            if row_index == 0:
                axis.set_title(title)
            if row_index == 2:
                axis.set_xlabel("Time (s)")
            if column_index == 0:
                axis.text(-0.28, 0.5, condition_label, transform=axis.transAxes, rotation=90, va="center", ha="center", fontweight="bold")
            if row_index == 0 and column_index == 0:
                axis.legend(frameon=False, loc="upper right")
    fig.suptitle("Digitized Yang et al. (2026) validation traces", fontsize=9.5)
    return save_figure(fig, "audit02-yang-digitized-test-histories", AUDIT_FIGURE_DIR)


def deck_filter_figure(reference: dict[str, Any], report: dict[str, Any]) -> list[str]:
    deck = report["deck_filter_reproduction"]
    time_s = np.asarray(deck["time_s"], dtype=float)
    heave = np.asarray(deck["heave_time_series"], dtype=float)
    pitch = np.asarray(deck["pitch_time_series"], dtype=float)
    dt = float(deck["dt_s"])
    fig, axes = plt.subplots(2, 2, figsize=(7.15, 4.6))

    visible = time_s <= min(40.0, float(time_s[-1]))
    axes[0, 0].plot(time_s[visible], heave[visible], color="#256f7a", linewidth=0.9)
    axes[0, 0].set(title="Deterministic heave realization", xlabel="Time (s)", ylabel="Heave (m)")
    axes[1, 0].plot(time_s[visible], np.degrees(pitch[visible]), color="#8b5a2b", linewidth=0.9)
    axes[1, 0].set(title="Deterministic pitch realization", xlabel="Time (s)", ylabel="Pitch (deg)")

    for axis, motion, values, unit_scale, ylabel in [
        (axes[0, 1], "heave", heave, 1.0, "PSD (m$^2$/Hz)"),
        (axes[1, 1], "pitch", pitch, 180.0 / np.pi, "PSD (deg$^2$/Hz)"),
    ]:
        frequency_hz, psd = signal.welch(values * unit_scale, fs=1.0 / dt, nperseg=min(4096, len(values)))
        numerator, denominator = _continuous_filter_coefficients(reference, motion)
        omega = 2.0 * np.pi * frequency_hz
        _, response = signal.freqs(numerator, denominator, worN=omega)
        theoretical = np.abs(response) ** 2 * unit_scale**2
        valid = (frequency_hz > 0.0) & (frequency_hz <= 0.5)
        psd_normalized = psd / max(float(np.max(psd[valid])), np.finfo(float).tiny)
        theoretical_normalized = theoretical / max(float(np.max(theoretical[valid])), np.finfo(float).tiny)
        axis.semilogy(frequency_hz[valid], psd_normalized[valid], color=COLORS["model"], linewidth=0.9, label="Present realization")
        axis.semilogy(frequency_hz[valid], theoretical_normalized[valid], color=COLORS["reference"], linestyle="--", linewidth=1.0, label="Published transfer shape")
        axis.set_xlim(0.0, 0.5)
        axis.set_ylim(1.0e-6, 2.0)
        axis.set(title=f"{motion.capitalize()} spectral shape", xlabel="Frequency (Hz)", ylabel="Normalized PSD")
        axis.legend(frameon=False)

    fig.suptitle(f"Response of the published deck filters to unit white noise (seed {deck['seed']})", fontsize=9.5)
    return save_figure(fig, "figS02-yang-deck-filter-reproduction")


def identified_landing_comparison_figure(report: dict[str, Any], identifiability: dict[str, Any]) -> list[str]:
    condition_order = ["Y0_simultaneous", "Y1_1-2-1", "Y2_2-2"]
    condition_labels = ["Simultaneous", "1-2-1", "2-2"]
    metrics = [
        ("acceleration_up_m_s2", "Axial acceleration", "m/s$^2$", 1.0),
        ("strut_force_n", "Main-strut load", "kN", 1.0e-3),
        ("stroke_m", "Buffer stroke", "mm", 1.0e3),
    ]
    fig, axes = plt.subplots(3, 3, figsize=(7.15, 5.65), sharex=True)
    for row_index, (condition_id, condition_label) in enumerate(zip(condition_order, condition_labels)):
        comparison = report["comparisons"][condition_id]
        envelope = identifiability["prediction_envelopes"][condition_id]
        time_s = np.asarray(envelope["time_s"], dtype=float)
        for column_index, (metric, title, unit, scale) in enumerate(metrics):
            axis = axes[row_index, column_index]
            paper = np.asarray(envelope["reference"][metric], dtype=float) * scale
            channel = envelope["channels"][metric]
            model = np.asarray(channel["median"], dtype=float) * scale
            lower = np.asarray(channel["p05"], dtype=float) * scale
            upper = np.asarray(channel["p95"], dtype=float) * scale
            quality = comparison["metrics"][metric]
            axis.plot(time_s, paper, color=COLORS["reference"], linestyle="--", linewidth=1.0, label="Published test (digitized)")
            axis.fill_between(time_s, lower, upper, color=COLORS["model"], alpha=0.16, linewidth=0, label="Near-optimal P05-P95")
            axis.plot(time_s, model, color=COLORS["model"], linewidth=1.15, label="Near-optimal median")
            axis.set_ylabel(unit)
            axis.text(
                0.98,
                0.95,
                f"nRMSE {quality['normalized_rmse_vs_paper_peak']:.2f}\nr {quality['correlation']:.2f}",
                transform=axis.transAxes,
                ha="right",
                va="top",
                fontsize=7.3,
                bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.75, "pad": 1.5},
            )
            if row_index == 0:
                axis.set_title(title)
            if row_index == 2:
                axis.set_xlabel("Time from detected contact (s)")
            if column_index == 0:
                role = "calibration" if row_index == 0 else "hold-out"
                axis.text(-0.29, 0.5, f"{condition_label}\n({role})", transform=axis.transAxes, rotation=90, va="center", ha="center", fontweight="bold")
    axes[0, 2].legend(frameon=False, loc="lower right", fontsize=7.0)
    fig.suptitle("Comparison with the Yang et al. drop tests", fontsize=9.5)
    return save_figure(fig, "fig03-yang-identified-landing-comparison")


def yang_identifiability_figure(report: dict[str, Any]) -> list[str]:
    singular_values = np.asarray(report["best_solution"]["jacobian_relative_singular_values"], dtype=float)
    ensemble = report["near_optimal_ensemble"]
    labels = ["force ratio", "stroke ratio", "$k_1$", "$k_2$", "$c_c$", "$c_r$"]
    correlation = np.asarray(ensemble["pearson_correlation"], dtype=float)
    fig, axes = plt.subplots(1, 2, figsize=(7.15, 3.10))
    axes[0].semilogy(np.arange(1, len(singular_values) + 1), singular_values, marker="o", color=COLORS["model"])
    axes[0].axhline(1.0e-2, color=COLORS["reference"], linestyle="--", linewidth=0.8, label="practical screening level")
    axes[0].set(xlabel="Jacobian singular-value index", ylabel="Relative singular value", title="Local sensitivity spectrum", xticks=np.arange(1, len(singular_values) + 1))
    axes[0].legend(loc="lower left")
    image = axes[1].imshow(correlation, vmin=-1.0, vmax=1.0, cmap="coolwarm")
    axes[1].set(xticks=np.arange(len(labels)), yticks=np.arange(len(labels)), xticklabels=labels, yticklabels=labels, title="Near-optimal parameter correlation")
    axes[1].tick_params(axis="x", rotation=40)
    for row in range(correlation.shape[0]):
        for column in range(correlation.shape[1]):
            axes[1].text(column, row, f"{correlation[row, column]:.2f}", ha="center", va="center", fontsize=6.2, color="white" if abs(correlation[row, column]) > 0.62 else "black")
    fig.colorbar(image, ax=axes[1], fraction=0.046, pad=0.04, label="Pearson $r$")
    fig.suptitle("Practical non-identifiability of the reduced drop-test model", fontsize=9.5)
    return save_figure(fig, "figS01-yang-identifiability")


def barge_hydrodynamic_figure(convergence: dict[str, Any]) -> list[str]:
    completed = [run for run in convergence["runs"] if run.get("status") == "solver_completed"]
    medium = next(run for run in completed if run["level"] == "medium")
    fine = next((run for run in completed if run["level"] == "fine"), None)
    rows = medium["motion_rao"]["rows"]
    headings = [float(value) for value in medium["motion_rao"]["headings_deg"]]
    fig, axes = plt.subplots(2, 2, figsize=(7.15, 4.65))
    frequency = np.asarray([float(row["frequency_rad_s"]) for row in rows])

    def medium_series(dof: str, heading: float, angular: bool = False) -> np.ndarray:
        heading_index = min(range(len(headings)), key=lambda index: abs(headings[index] - heading))
        values = np.asarray([row["amplitudes_by_heading"][dof][heading_index] for row in rows], dtype=float)
        return np.degrees(values) if angular else values

    active = frequency <= 2.0 + 1.0e-12
    axes[0, 0].plot(frequency[active], medium_series("heave", 0.0)[active], color=COLORS["model"], label="0 deg, 2048 panels")
    axes[0, 0].plot(frequency[active], medium_series("heave", 90.0)[active], color=COLORS["hydro"], linestyle="--", label="90 deg, 2048 panels")
    axes[0, 0].set(title="Heave RAO (active response band)", xlabel="Wave frequency (rad/s)", ylabel="m/m", xlim=(0.2, 2.0))
    axes[0, 0].legend()
    axes[0, 1].plot(frequency[active], medium_series("roll", 90.0, angular=True)[active], color=COLORS["hydro"], label="roll, 90 deg")
    axes[0, 1].plot(frequency[active], medium_series("pitch", 0.0, angular=True)[active], color=COLORS["model"], linestyle="--", label="pitch, 0 deg")
    axes[0, 1].set(title="Angular RAOs (active response band)", xlabel="Wave frequency (rad/s)", ylabel="deg/m", xlim=(0.2, 2.0))
    axes[0, 1].legend()

    if fine is not None:
        fine_rows = fine["motion_rao"]["rows"]
        fine_headings = [float(value) for value in fine["motion_rao"]["headings_deg"]]
        fine_frequency = np.asarray([float(row["frequency_rad_s"]) for row in fine_rows])

        def fine_series(dof: str, heading: float, angular: bool = False) -> np.ndarray:
            heading_index = min(range(len(fine_headings)), key=lambda index: abs(fine_headings[index] - heading))
            values = np.asarray([row["amplitudes_by_heading"][dof][heading_index] for row in fine_rows], dtype=float)
            return np.degrees(values) if angular else values

        for axis, dof, heading, angular in (
            (axes[0, 0], "heave", 90.0, False),
            (axes[0, 1], "roll", 90.0, True),
            (axes[0, 1], "pitch", 0.0, True),
        ):
            axis.scatter(fine_frequency, fine_series(dof, heading, angular), marker="s", s=23, facecolor="white", edgecolor=COLORS["contact"], zorder=5, label="8192-panel anchors")
        axes[0, 0].legend(loc="best")

    hydro_rows = medium["hydrodynamics"]
    tail_rows = [row for row in hydro_rows if float(row["frequency_rad_s"]) >= 4.0 - 1.0e-12]
    tail_frequency = np.asarray([float(row["frequency_rad_s"]) for row in tail_rows])
    a_inf = medium["radiation_checks"]["A_inf_diagonal_kg"]
    for index, key, label, color, line_style in (
        (2, "33", "$A_{33}$", COLORS["model"], "-"),
        (3, "44", "$A_{44}$", COLORS["hydro"], "--"),
        (4, "55", "$A_{55}$", COLORS["contact"], "-."),
    ):
        estimate = float(a_inf[key])
        values = np.asarray([float(row["added_mass_kg"][index][index]) for row in tail_rows]) / estimate
        axes[1, 0].plot(tail_frequency, values, color=color, linestyle=line_style, marker="o", markersize=2.8, label=label)
    axes[1, 0].axhline(1.0, color=COLORS["reference"], linewidth=0.8, linestyle=":")
    axes[1, 0].set(title="Finite-cutoff added-mass tail", xlabel="Wave frequency (rad/s)", ylabel=r"$A_{ii}(\omega)/\widehat{A}_{ii,\infty}$", xlim=(4.0, 5.0))
    axes[1, 0].legend(ncol=3, loc="best")

    checks = convergence["acceptance"]["pair_checks"]
    labels = [f"{row['coarser']} to {row['finer']}" for row in checks]
    values = [100.0 * float(row["maximum_selected_relative_change"]) if row["maximum_selected_relative_change"] is not None else np.nan for row in checks]
    axes[1, 1].bar(labels, values, color=[COLORS["secondary"], COLORS["contact"]][: len(values)], width=0.62)
    axes[1, 1].axhline(5.0, color=COLORS["reference"], linestyle="--", linewidth=0.9, label="5% criterion")
    axes[1, 1].set(title="Mesh refinement (criterion not met)", ylabel="Maximum selected change (%)")
    axes[1, 1].tick_params(axis="x", rotation=18)
    axes[1, 1].legend(loc="best")
    fig.suptitle("Hydrodynamic response and numerical convergence of the rectangular barge", fontsize=9.5)
    return save_figure(fig, "fig04-platform-hydrodynamic-response")


def chrono_stage3_coupling_figure(report: dict[str, Any], response: dict[str, Any]) -> list[str]:
    chrono = response["multibody"]
    summary = chrono["summary"]
    time_s = np.asarray(chrono["time_s"], dtype=float) - 510.0
    mask = (time_s >= -0.5) & (time_s <= 4.0)
    fig, axes = plt.subplots(4, 2, figsize=(7.15, 7.85), sharex=False)
    leg_ids = sorted(chrono["forces"]["leg_contact_force_n"])
    colors = [COLORS["model"], COLORS["hydro"], COLORS["contact"], COLORS["coupling"]]
    line_styles = ["-", "--", "-.", ":"]
    for leg_id, color, line_style in zip(leg_ids, colors, line_styles):
        contact_force = np.asarray(chrono["forces"]["leg_contact_force_n"][leg_id], dtype=float) * 1.0e-3
        stroke = np.asarray(chrono["contact"]["leg_stroke_m"][leg_id], dtype=float) * 1.0e3
        axes[0, 0].plot(time_s[mask], contact_force[mask], color=color, linestyle=line_style, linewidth=1.05, label=leg_id.replace("_", " "))
        axes[0, 1].plot(time_s[mask], stroke[mask], color=color, linestyle=line_style, linewidth=1.05, label=leg_id.replace("_", " "))
    first_contact = float(summary["first_contact_time_s"]) - 510.0
    touchdown_sequence = summary["contact_state"]["touchdown_sequence"]
    last_initial_contact = max(float(row["first_contact_time_s"]) for row in touchdown_sequence) - 510.0
    for axis in axes[0, :]:
        axis.axvspan(first_contact, last_initial_contact, color="#F0E442", alpha=0.12, linewidth=0)
        axis.axvline(first_contact, color="#777777", linewidth=0.7, linestyle="--")
        axis.axvline(last_initial_contact, color="#777777", linewidth=0.7, linestyle="--")
    axes[0, 0].set(title="Footpad contact force", xlabel="Time from nominal touchdown (s)", ylabel="kN")
    axes[0, 1].set(title="Main-buffer stroke", xlabel="Time from nominal touchdown (s)", ylabel="mm")
    axes[0, 0].legend(frameon=False, ncol=2)

    platform_time = np.asarray(response["platform_time_s"], dtype=float) - 510.0
    baseline = np.asarray(response["baseline_q_active"], dtype=float)
    feedback = np.asarray(response["final_q_active"], dtype=float)
    visible = (platform_time >= -0.5) & (platform_time <= 12.0)
    axes[1, 0].plot(platform_time[visible], baseline[visible, 0], color="#555555", linestyle="--", linewidth=1.0, label="same-platform no-contact baseline")
    axes[1, 0].plot(platform_time[visible], feedback[visible, 0], color=COLORS["flexible"], linewidth=1.15, label="four-pass interface solution")
    axes[1, 0].set(title="Platform heave", xlabel="Time from nominal touchdown (s)", ylabel="m")
    axes[1, 0].legend(frameon=False)
    axes[1, 1].plot(platform_time[visible], np.degrees(baseline[visible, 1]), color="#555555", linestyle="--", linewidth=1.0, label="same-platform no-contact baseline")
    axes[1, 1].plot(platform_time[visible], np.degrees(feedback[visible, 1]), color=COLORS["flexible"], linewidth=1.15, label="four-pass interface solution")
    axes[1, 1].set(title="Platform roll", xlabel="Time from nominal touchdown (s)", ylabel="deg")
    axes[1, 1].legend(frameon=False)
    pass_rows = report["iterative_run"]["passes"]
    pass_ids = [int(row["pass"]) for row in pass_rows]
    peak_force = [float(row["contact_summary"]["max_leg_contact_force_kn"]) * 1.0e-3 for row in pass_rows]
    peak_stroke = [float(row["contact_summary"]["max_leg_stroke_m"]) * 1.0e3 for row in pass_rows]
    axes[2, 0].plot(pass_ids, peak_force, marker="o", color=COLORS["contact"], label="peak contact force (MN)")
    twin = axes[2, 0].twinx()
    twin.plot(pass_ids, peak_stroke, marker="s", linestyle="--", color=COLORS["model"], label="peak buffer stroke (mm)")
    axes[2, 0].set(title="Interface-iteration sensitivity", xlabel="Interface pass", ylabel="Peak force (MN)", xticks=pass_ids)
    twin.set_ylabel("Peak stroke (mm)")
    handles_a, labels_a = axes[2, 0].get_legend_handles_labels()
    handles_b, labels_b = twin.get_legend_handles_labels()
    axes[2, 0].legend(handles_a + handles_b, labels_a + labels_b, loc="best")

    dt_values = report["time_step_convergence"]["values"]
    dt_order = ["dt", "dt_over_2", "dt_over_4"]
    dt_ms = np.asarray([0.5, 0.25, 0.125])
    dt_force = np.asarray([float(dt_values[key]["max_leg_contact_force_kn"]) * 1.0e-3 for key in dt_order])
    dt_impulse = np.asarray([float(dt_values[key]["total_normal_impulse_ns"]) * 1.0e-6 for key in dt_order])
    axes[2, 1].plot(dt_ms, dt_force, marker="o", color=COLORS["contact"], label="peak force (MN)")
    dt_twin = axes[2, 1].twinx()
    dt_twin.plot(dt_ms, dt_impulse, marker="s", linestyle="--", color=COLORS["model"], label="normal impulse (MN s)")
    axes[2, 1].set(title="Time-step sensitivity (overall criterion failed)", xlabel="Contact step (ms)", ylabel="Peak force (MN)", xticks=dt_ms)
    axes[2, 1].invert_xaxis()
    dt_twin.set_ylabel("Normal impulse (MN s)")
    dt_handles_a, dt_labels_a = axes[2, 1].get_legend_handles_labels()
    dt_handles_b, dt_labels_b = dt_twin.get_legend_handles_labels()
    axes[2, 1].legend(dt_handles_a + dt_handles_b, dt_labels_a + dt_labels_b, loc="best")

    for offset, (leg_id, color, line_style) in enumerate(zip(leg_ids, colors, line_styles)):
        contact_state = np.asarray(chrono["contact"]["leg_contact"][leg_id], dtype=float)
        axes[3, 0].step(
            time_s[mask],
            contact_state[mask] + 1.25 * offset,
            where="post",
            color=color,
            linestyle=line_style,
            linewidth=1.0,
        )
    axes[3, 0].axvspan(first_contact, last_initial_contact, color="#F0E442", alpha=0.12, linewidth=0)
    axes[3, 0].set(
        title="Four-foot contact state",
        xlabel="Time from nominal touchdown (s)",
        ylabel="Contact indicator",
        yticks=[1.25 * index + 0.5 for index in range(len(leg_ids))],
        yticklabels=[leg_id.replace("_", " ") for leg_id in leg_ids],
    )
    axes[3, 0].set_ylim(-0.2, 1.25 * (len(leg_ids) - 1) + 1.2)

    regularization = report["contact_regularization_sensitivity"]["rows"]
    stiffness = np.asarray([float(row["normal_stiffness_n_m"]) * 1.0e-6 for row in regularization])
    reg_force = np.asarray([float(row["peak_contact_force_kn"]) * 1.0e-3 for row in regularization])
    penetration = np.asarray([float(row["maximum_penetration_m"]) * 1.0e3 for row in regularization])
    axes[3, 1].plot(stiffness, reg_force, marker="o", color=COLORS["contact"], label="peak force (MN)")
    reg_twin = axes[3, 1].twinx()
    reg_twin.plot(stiffness, penetration, marker="s", linestyle="--", color=COLORS["model"], label="penetration (mm)")
    axes[3, 1].set(title="Penalty-contact regularization", xlabel="Normal stiffness (MN/m)", ylabel="Peak force (MN)", xticks=stiffness)
    reg_twin.set_ylabel("Maximum penetration (mm)")
    reg_handles_a, reg_labels_a = axes[3, 1].get_legend_handles_labels()
    reg_handles_b, reg_labels_b = reg_twin.get_legend_handles_labels()
    axes[3, 1].legend(reg_handles_a + reg_handles_b, reg_labels_a + reg_labels_b, loc="center right", fontsize=6.5)
    fig.suptitle("Same-platform partitioned response for a 15 m port-offset touchdown", fontsize=9.5)
    return save_figure(fig, "fig06-partitioned-contact-feedback")


def barge_wave_sensitivity_figure(report: dict[str, Any], duration_report: dict[str, Any]) -> list[str]:
    cases = {(row["sea_state_id"], float(row["heading_deg"])): row for row in report["cases"]}
    headings = sorted({float(row["heading_deg"]) for row in report["cases"]})
    colors = [COLORS["model"], COLORS["hydro"], COLORS["contact"]]
    line_styles = ["-", "--", "-."]
    markers = ["o", "s", "^"]
    fig, axes = plt.subplots(2, 2, figsize=(7.15, 4.65))
    metrics = [
        (axes[0, 0], "landing_center.max_abs_vertical_velocity_m_s", "Landing-center vertical speed", "P95 maximum (m/s)"),
        (axes[0, 1], "four_feet.max_vertical_velocity_span_m_s", "Actual-radius four-foot speed difference", "P95 maximum span (m/s)"),
        (axes[1, 0], "platform.max_tilt_deg", "Platform tilt", "P95 maximum (deg)"),
    ]
    for axis, metric, title, ylabel in metrics:
        for hs, color, line_style, marker in zip((1, 2, 3), colors, line_styles, markers):
            selected = [cases[(f"Hs{hs}_Tp8", heading)] for heading in headings]
            p50 = np.asarray([row["statistics"][metric]["p50"] for row in selected], dtype=float)
            p95 = np.asarray([row["statistics"][metric]["p95"] for row in selected], dtype=float)
            ci = [row["statistics"][metric]["p95_bootstrap_95ci"] for row in selected]
            lower = np.asarray([item["lower"] for item in ci], dtype=float)
            upper = np.asarray([item["upper"] for item in ci], dtype=float)
            axis.fill_between(headings, p50, p95, color=color, alpha=0.10, linewidth=0)
            axis.errorbar(
                headings,
                p95,
                yerr=np.vstack([p95 - lower, upper - p95]),
                color=color,
                linestyle=line_style,
                marker=marker,
                markersize=3.0,
                linewidth=1.1,
                elinewidth=0.55,
                capsize=1.5,
                label=rf"$H_s={hs}$ m",
            )
            invalid = np.asarray([not bool(row["linear_validity"]["pass"]) for row in selected])
            if np.any(invalid):
                axis.scatter(np.asarray(headings)[invalid], p95[invalid], marker="x", s=21, color=color, zorder=5)
        axis.set(title=title, xlabel="Wave heading (deg)", ylabel=ylabel)
    axes[0, 0].legend(frameon=False)

    duration_cases = {(row["sea_state_id"], float(row["duration_s"])): row for row in duration_report["cases"]}
    durations = sorted({float(row["duration_s"]) for row in duration_report["cases"]})
    for state_id, label, color, marker in (
        ("Hs3_Tp8", "$T_p=8$ s", COLORS["model"], "o"),
        ("Hs3_Tp10", "$T_p=10$ s", COLORS["contact"], "s"),
    ):
        values = np.asarray(
            [duration_cases[(state_id, duration)]["statistics"]["landing_center.max_abs_vertical_velocity_m_s"]["p95"] for duration in durations]
        )
        intervals = [
            duration_cases[(state_id, duration)]["statistics"]["landing_center.max_abs_vertical_velocity_m_s"]["p95_bootstrap_95ci"]
            for duration in durations
        ]
        lower = np.asarray([row["lower"] for row in intervals])
        upper = np.asarray([row["upper"] for row in intervals])
        axes[1, 1].errorbar(
            durations,
            values,
            yerr=np.vstack([values - lower, upper - values]),
            color=color,
            marker=marker,
            capsize=2.0,
            linewidth=1.1,
            label=label,
        )
    axes[1, 1].set(title="$H_s=3$ m, 90 deg: record-length sensitivity", xlabel="Record duration (s)", ylabel="P95 center speed (m/s)", xticks=durations)
    axes[1, 1].legend(loc="best")

    fig.suptitle("Random-wave deck motion: P95, bootstrap uncertainty and validity flags", fontsize=9.5)
    return save_figure(fig, "fig05-random-wave-deck-statistics")


def main() -> None:
    configure_style()
    reference = read_json(REFERENCE_PATH)
    report = read_json(REPORT_PATH)
    digitized = read_json(DIGITIZED_PATH)
    landing_report = read_json(LANDING_REPORT_PATH)
    identifiability = read_json(IDENTIFIABILITY_PATH)
    hydro_convergence = read_json(HYDRO_CONVERGENCE_PATH)
    barge_sensitivity = read_json(BARGE_SENSITIVITY_PATH)
    barge_duration = read_json(BARGE_DURATION_PATH)
    chrono_report = read_json(CHRONO_REPORT_PATH)
    chrono_response = read_json(CHRONO_RESPONSE_PATH)
    platform_config = read_json(PLATFORM_CONFIG_PATH)
    outputs = []
    outputs.extend(coupled_framework_figure())
    outputs.extend(barge_geometry_figure(platform_config, barge_sensitivity))
    outputs.extend(deck_filter_figure(reference, report))
    outputs.extend(identified_landing_comparison_figure(landing_report, identifiability))
    outputs.extend(yang_identifiability_figure(identifiability))
    outputs.extend(barge_hydrodynamic_figure(hydro_convergence))
    outputs.extend(chrono_stage3_coupling_figure(chrono_report, chrono_response))
    outputs.extend(barge_wave_sensitivity_figure(barge_sensitivity, barge_duration))
    audit_outputs = []
    audit_outputs.extend(scalar_target_figure(reference))
    audit_outputs.extend(digitized_history_figure(digitized))
    outputs.extend(audit_outputs)
    print("Generated paper figures:")
    for output in outputs:
        print(output)


if __name__ == "__main__":
    main()

"""
ACS Visualization — Publication-Quality Plots
===============================================
High-resolution histograms for the ACS phase space and invariant mass
spectrum. Dark theme, annotated with statistical results.
"""

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import config as cfg


# ─────────────────────────────────────────────
# Style Configuration
# ─────────────────────────────────────────────
def _setup_style():
    """Apply publication-quality dark style."""
    plt.rcParams.update({
        "figure.facecolor":   "#0a0a0f",
        "axes.facecolor":     "#0d0d15",
        "axes.edgecolor":     "#333355",
        "axes.labelcolor":    "#ccccee",
        "axes.grid":          True,
        "grid.color":         "#1a1a2e",
        "grid.alpha":         0.6,
        "text.color":         "#ccccee",
        "xtick.color":        "#8888aa",
        "ytick.color":        "#8888aa",
        "font.family":        "monospace",
        "font.size":          10,
        "figure.dpi":         cfg.DPI,
        "savefig.dpi":        cfg.DPI,
        "savefig.facecolor":  "#0a0a0f",
        "savefig.bbox":       "tight",
    })


def _ensure_output_dir():
    os.makedirs(cfg.OUTPUT_DIR, exist_ok=True)


# ─────────────────────────────────────────────
# ACS Phase Histogram
# ─────────────────────────────────────────────
def plot_acs_phase(phases, stat_results, title_suffix="",
                   filename="acs_phase_higgs.png"):
    """
    Plot the ACS phase distribution with attractor, signal/sideband
    regions, and significance annotation.
    """
    _setup_style()
    _ensure_output_dir()

    fig, ax = plt.subplots(figsize=(14, 7))

    attractor = stat_results["attractor"]
    sig_lo, sig_hi = stat_results["signal_window"]
    sb_l_lo, sb_l_hi = stat_results["left_sideband"]
    sb_r_lo, sb_r_hi = stat_results["right_sideband"]

    # Determine plot range: center on attractor
    plot_half = 0.08
    plot_lo = attractor - plot_half
    plot_hi = attractor + plot_half

    # Filter phases to plot range
    mask = (phases >= plot_lo) & (phases <= plot_hi)
    phases_plot = phases[mask]

    # Histogram
    counts, bin_edges, patches = ax.hist(
        phases_plot, bins=cfg.PHASE_HIST_BINS, range=(plot_lo, plot_hi),
        color="#4a90d9", alpha=0.85, edgecolor="none",
        label=f"ACS Phase (N={len(phases_plot):,})"
    )

    # Color bins in signal region
    bin_centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])
    for bc, patch in zip(bin_centers, patches):
        if sig_lo <= bc <= sig_hi:
            patch.set_facecolor("#ff6b6b")
            patch.set_alpha(0.95)
        elif (sb_l_lo <= bc <= sb_l_hi) or (sb_r_lo <= bc <= sb_r_hi):
            patch.set_facecolor("#ffd93d")
            patch.set_alpha(0.7)

    # Attractor line
    ymax = ax.get_ylim()[1]
    ax.axvline(attractor, color="#00ff88", linewidth=2.0, linestyle="--",
               label=f"π/4 Attractor = {attractor:.6f}", zorder=10)

    # Signal region shading
    ax.axvspan(sig_lo, sig_hi, alpha=0.12, color="#ff6b6b",
               label=f"Signal region [{sig_lo:.4f}, {sig_hi:.4f}]")

    # Sideband shading
    ax.axvspan(sb_l_lo, sb_l_hi, alpha=0.08, color="#ffd93d",
               label="Sidebands (B estimation)")
    ax.axvspan(sb_r_lo, sb_r_hi, alpha=0.08, color="#ffd93d")

    # Significance annotation box
    Z = stat_results["significance_Z"]
    S = stat_results["S_estimate"]
    B = stat_results["B_estimate"]
    N = stat_results["N_signal"]

    info_text = (
        f"Signal region events: {N:,}\n"
        f"Background estimate:  {B:.1f}\n"
        f"Signal excess S:      {S:.1f}\n"
        f"Significance Z:       {Z:.2f} σ"
    )

    props = dict(boxstyle="round,pad=0.6", facecolor="#1a1a2e",
                 edgecolor="#4a90d9", alpha=0.9)
    ax.text(0.97, 0.95, info_text, transform=ax.transAxes,
            fontsize=10, verticalalignment="top", horizontalalignment="right",
            bbox=props, fontfamily="monospace", color="#ccccee")

    # Labels
    ax.set_xlabel("ACS Phase θ = arctan(M / M_target)  [rad]", fontsize=12)
    ax.set_ylabel("Events / bin", fontsize=12)
    ax.set_title(
        f"Asymmetric Convergence Sequence — Higgs Window "
        f"(M_target = {cfg.TARGET_MASS} GeV) {title_suffix}",
        fontsize=13, fontweight="bold", color="#eeeeff", pad=15
    )

    ax.legend(loc="upper left", fontsize=9, framealpha=0.8,
              facecolor="#0d0d15", edgecolor="#333355")

    # GPU badge
    gpu_text = "RTX 5090 GPU-accelerated" if cfg.USE_GPU else "CPU mode"
    ax.text(0.97, 0.02, gpu_text, transform=ax.transAxes,
            fontsize=8, color="#666688", ha="right", va="bottom",
            fontstyle="italic")

    filepath = os.path.join(cfg.OUTPUT_DIR, filename)
    fig.savefig(filepath)
    plt.close(fig)
    print(f"[viz] Saved: {filepath}")
    return filepath


# ─────────────────────────────────────────────
# Invariant Mass Spectrum
# ─────────────────────────────────────────────
def plot_mass_spectrum(masses, filename="mass_spectrum_higgs.png"):
    """
    Plot the dimuon invariant mass spectrum in the Higgs window.
    """
    _setup_style()
    _ensure_output_dir()

    fig, ax = plt.subplots(figsize=(14, 7))

    low, high = cfg.MASS_WINDOW
    mask = (masses >= low) & (masses <= high)
    masses_plot = masses[mask]

    ax.hist(masses_plot, bins=cfg.MASS_HIST_BINS, range=(low, high),
            color="#8b5cf6", alpha=0.85, edgecolor="none",
            label=f"Dimuon Mass (N={len(masses_plot):,})")

    # Mark target resonance mass
    ax.axvline(cfg.TARGET_MASS, color="#00ff88", linewidth=2.0,
               linestyle="--", label=f"m_target = {cfg.TARGET_MASS} GeV")

    ax.set_xlabel("Invariant Mass M(μ⁺μ⁻)  [GeV]", fontsize=12)
    ax.set_ylabel("Events / bin", fontsize=12)
    ax.set_title(
        f"Dimuon Invariant Mass — Window [{low}, {high}] GeV",
        fontsize=13, fontweight="bold", color="#eeeeff", pad=15
    )
    ax.legend(loc="upper right", fontsize=10, framealpha=0.8,
              facecolor="#0d0d15", edgecolor="#333355")

    filepath = os.path.join(cfg.OUTPUT_DIR, filename)
    fig.savefig(filepath)
    plt.close(fig)
    print(f"[viz] Saved: {filepath}")
    return filepath


# ─────────────────────────────────────────────
# Full Mass Spectrum (all resonances)
# ─────────────────────────────────────────────
def plot_full_spectrum(masses, filename="mass_spectrum_full.png"):
    """
    Plot the full dimuon mass spectrum showing all resonances
    (J/ψ, Υ, Z, Higgs window).
    """
    _setup_style()
    _ensure_output_dir()

    fig, axes = plt.subplots(1, 2, figsize=(18, 7),
                              gridspec_kw={"width_ratios": [1, 1]})

    # Left: log-scale full range
    ax = axes[0]
    ax.hist(masses, bins=1000, range=(0.5, 200), color="#4a90d9",
            alpha=0.85, edgecolor="none")
    ax.set_yscale("log")
    ax.set_xlabel("M(μ⁺μ⁻)  [GeV]", fontsize=12)
    ax.set_ylabel("Events / bin (log)", fontsize=12)
    ax.set_title("Full Dimuon Mass Spectrum", fontsize=13,
                 fontweight="bold", color="#eeeeff", pad=12)

    # Mark resonances
    for mass, name, col in [
        (cfg.JPSI_MASS, "J/ψ", "#ff6b6b"),
        (cfg.UPSILON_1S_MASS, "Υ(1S)", "#ffd93d"),
        (cfg.Z_MASS, "Z", "#00ff88"),
        (cfg.HIGGS_MASS, "H", "#ff88ff"),
    ]:
        ax.axvline(mass, color=col, linewidth=1.2, linestyle="--", alpha=0.8)
        ax.text(mass, ax.get_ylim()[1] * 0.5, f" {name}",
                color=col, fontsize=9, rotation=90, va="center")

    # Right: Higgs zoom
    ax2 = axes[1]
    low, high = cfg.MASS_WINDOW
    mask = (masses >= low) & (masses <= high)
    ax2.hist(masses[mask], bins=cfg.MASS_HIST_BINS, range=(low, high),
             color="#8b5cf6", alpha=0.85, edgecolor="none")
    ax2.axvline(cfg.HIGGS_MASS, color="#00ff88", linewidth=2.0,
                linestyle="--", label=f"m_H = {cfg.HIGGS_MASS} GeV")
    ax2.set_xlabel("M(μ⁺μ⁻)  [GeV]", fontsize=12)
    ax2.set_ylabel("Events / bin", fontsize=12)
    ax2.set_title("Higgs Window Zoom", fontsize=13,
                  fontweight="bold", color="#eeeeff", pad=12)
    ax2.legend(fontsize=10, framealpha=0.8, facecolor="#0d0d15",
               edgecolor="#333355")

    fig.suptitle("CMS Open Data — Dimuon Resonance Landscape",
                 fontsize=15, fontweight="bold", color="#ffffff", y=1.02)
    fig.tight_layout()

    filepath = os.path.join(cfg.OUTPUT_DIR, filename)
    fig.savefig(filepath)
    plt.close(fig)
    print(f"[viz] Saved: {filepath}")
    return filepath

"""
ACS Comparison — Multi-Resonance Convergence Panorama
======================================================
Combines the ACS phase distributions of all four resonances
(J/ψ, Υ, Z, Higgs) into a single publication-quality figure.

Reads the output plots and re-processes the cached phase data
to create a side-by-side comparison with convergence metrics.

Usage:
    python compare.py
"""

import os
import sys
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as cfg
from pipeline import (calculate_kinematics, map_acs_phase,
                       apply_quality_cuts, select_mass_window,
                       to_cpu, _GPU_AVAILABLE)
from ingest import load_data
from stats import compute_phase_statistics


# ─────────────────────────────────────────────
# Resonance definitions
# ─────────────────────────────────────────────
RESONANCES = [
    {
        "name": "φ(1020)",
        "label": "phi",
        "target_mass": cfg.PHI_MASS,
        "mass_window": (0.95, 1.10),
        "color": "#ff9ff3",
    },
    {
        "name": "J/ψ",
        "label": "jpsi",
        "target_mass": cfg.JPSI_MASS,
        "mass_window": (2.8, 3.4),
        "color": "#ff6b6b",
    },
    {
        "name": "ψ(2S)",
        "label": "psi2s",
        "target_mass": cfg.PSI2S_MASS,
        "mass_window": (3.4, 3.95),
        "color": "#ff4757",
    },
    {
        "name": "Υ(1S)",
        "label": "upsilon_1s",
        "target_mass": cfg.UPSILON_1S_MASS,
        "mass_window": (9.0, 9.8),
        "color": "#ffd93d",
    },
    {
        "name": "Υ(2S)",
        "label": "upsilon_2s",
        "target_mass": cfg.UPSILON_2S_MASS,
        "mass_window": (9.8, 10.2),
        "color": "#f0932b",
    },
    {
        "name": "Υ(3S)",
        "label": "upsilon_3s",
        "target_mass": cfg.UPSILON_3S_MASS,
        "mass_window": (10.2, 10.6),
        "color": "#eb4d4b",
    },
    {
        "name": "Z Boson",
        "label": "z",
        "target_mass": cfg.Z_MASS,
        "mass_window": (80.0, 100.0),
        "color": "#00ff88",
    },
    {
        "name": "Higgs",
        "label": "higgs",
        "target_mass": cfg.HIGGS_MASS,
        "mass_window": (115.0, 135.0),
        "color": "#8b5cf6",
    },
]


def process_resonance(res, data_chunks):
    """
    Process pre-loaded data chunks for a specific resonance.
    Returns phases array and statistics dict.
    """
    phases_list = []
    n_window = 0

    for chunk_data in data_chunks:
        masses = chunk_data["masses"]

        # Mass window selection
        low, high = res["mass_window"]
        mask = (masses >= low) & (masses <= high)
        masses_w = masses[mask]
        n_window += len(masses_w)

        if len(masses_w) == 0:
            continue

        # ACS phase mapping
        phases = np.arctan(masses_w / res["target_mass"])
        phases_list.append(phases)

    if len(phases_list) == 0:
        return None, None

    all_phases = np.concatenate(phases_list)
    stats = compute_phase_statistics(all_phases)
    stats["n_window"] = n_window
    stats["resonance"] = res["name"]
    return all_phases, stats


def main():
    print("=" * 70)
    print("  ACS OMNI-LEVEL ANALYSIS — REFLEXIVE |Z|")
    print("  Processing 8 resonances × 13 TeV full dataset...")
    print("=" * 70)

    # Force 13 TeV source
    cfg.ACTIVE_SOURCE = "run2_nanoaod_13tev"

    # ─── Load data once, compute masses once ───
    print("\n[compare] Loading and computing invariant masses...")
    data_chunks = []

    for chunk_data in load_data():
        pt1  = chunk_data["pt1"]
        pt2  = chunk_data["pt2"]
        eta1 = chunk_data["eta1"]
        eta2 = chunk_data["eta2"]
        phi1 = chunk_data["phi1"]
        phi2 = chunk_data["phi2"]
        q1   = chunk_data["q1"]
        q2   = chunk_data["q2"]

        # Quality cuts
        from pipeline import apply_quality_cuts as aqc
        mask = to_cpu(aqc(pt1, pt2, eta1, eta2, q1, q2)).astype(bool)

        if mask.sum() == 0:
            continue

        masses = to_cpu(calculate_kinematics(
            pt1[mask], pt2[mask], eta1[mask], eta2[mask],
            phi1[mask], phi2[mask]
        ))

        data_chunks.append({"masses": masses})

    print(f"[compare] Loaded {len(data_chunks)} chunks")

    # ─── Process each resonance ───
    results = []
    for res in RESONANCES:
        print(f"\n[compare] Processing {res['name']} "
              f"(M={res['target_mass']} GeV, window={res['mass_window']})...")
        phases, stats = process_resonance(res, data_chunks)
        if phases is not None:
            results.append({
                "res": res,
                "phases": phases,
                "stats": stats,
            })
            Z = stats["significance_Z"]
            delta = abs(stats["mean_phase"] - cfg.ACS_ATTRACTOR)
            print(f"  → N={stats['n_window']:,}  |  Z={Z:.2f}σ  |  "
                  f"Δθ={delta:.6f} rad")
        else:
            print(f"  → No events in window!")

    # ─── Create comparison figure ───
    print("\n[compare] Generating panoramic comparison...")

    plt.rcParams.update({
        "figure.facecolor":   "#0a0a0f",
        "axes.facecolor":     "#0d0d15",
        "axes.edgecolor":     "#333355",
        "axes.labelcolor":    "#ccccee",
        "axes.grid":          True,
        "grid.color":         "#1a1a2e",
        "grid.alpha":         0.4,
        "text.color":         "#ccccee",
        "xtick.color":        "#8888aa",
        "ytick.color":        "#8888aa",
        "font.family":        "monospace",
        "font.size":          9,
        "figure.dpi":         cfg.DPI,
        "savefig.dpi":        cfg.DPI,
        "savefig.facecolor":  "#0a0a0f",
        "savefig.bbox":       "tight",
    })

    n_res = len(results)
    fig, axes = plt.subplots(1, n_res, figsize=(6 * n_res, 7))
    if n_res == 1:
        axes = [axes]

    attractor = cfg.ACS_ATTRACTOR

    for i, r in enumerate(results):
        ax = axes[i]
        res = r["res"]
        phases = r["phases"]
        stats = r["stats"]

        # Plot range centered on attractor
        plot_half = 0.08
        plot_lo = attractor - plot_half
        plot_hi = attractor + plot_half
        mask = (phases >= plot_lo) & (phases <= plot_hi)
        phases_plot = phases[mask]

        # Histogram
        ax.hist(phases_plot, bins=200, range=(plot_lo, plot_hi),
                color=res["color"], alpha=0.85, edgecolor="none")

        # Attractor line
        ax.axvline(attractor, color="#00ff88", linewidth=2.0,
                   linestyle="--", alpha=0.9)

        # Signal region
        sig_lo, sig_hi = stats["signal_window"]
        ax.axvspan(sig_lo, sig_hi, alpha=0.15, color="#ffffff")

        # Annotations
        Z = stats["significance_Z"]
        delta = abs(stats["mean_phase"] - attractor)
        N = stats["n_window"]

        info = (
            f"N = {N:,}\n"
            f"Z = {Z:.2f} σ\n"
            f"|Z| = {abs(Z):.2f} σ\n"
            f"Δθ = {delta:.6f}\n"
            f"⟨θ⟩ = {stats['mean_phase']:.6f}"
        )

        props = dict(boxstyle="round,pad=0.4", facecolor="#1a1a2e",
                     edgecolor=res["color"], alpha=0.9)
        ax.text(0.95, 0.95, info, transform=ax.transAxes,
                fontsize=9, va="top", ha="right", bbox=props,
                fontfamily="monospace", color="#ccccee")

        # Title
        ax.set_title(
            f"{res['name']}  (M = {res['target_mass']} GeV)",
            fontsize=12, fontweight="bold", color=res["color"], pad=10
        )

        ax.set_xlabel("θ = arctan(M/M_target)  [rad]", fontsize=10)
        if i == 0:
            ax.set_ylabel("Events / bin", fontsize=10)

        # Reflexive |Z| verdict badge
        absZ = abs(Z)
        verdict = "✓ CONVERGED" if absZ > 5.0 else (
            "◉ STRONG" if absZ > 3.0 else (
            "~ MARGINAL" if absZ > 1.0 else "✗ NO SIGNAL"))
        ax.text(0.5, 0.02, f"|Z| = {absZ:.1f}σ — {verdict}",
                transform=ax.transAxes,
                fontsize=8, ha="center", va="bottom", color="#888888",
                fontstyle="italic")

    fig.suptitle(
        "Asymmetric Convergence Sequence — Omni-Level Reflexive Analysis\n"
        f"Attractor π/4 = {attractor:.6f}  |  76.8M CMS Events (13 TeV)  |  |Z| Reflexive  |  RTX 5090",
        fontsize=13, fontweight="bold", color="#ffffff", y=1.04
    )

    fig.tight_layout()
    os.makedirs(cfg.OUTPUT_DIR, exist_ok=True)
    filepath = os.path.join(cfg.OUTPUT_DIR, "acs_omni_13tev_panorama.png")
    fig.savefig(filepath)
    plt.close(fig)
    print(f"\n[compare] Saved: {filepath}")

    # ─── Summary table ───
    print("\n" + "=" * 80)
    print(f"  {'Resonance':<12s} {'M_target':>10s} {'N_window':>12s} "
          f"{'Z [σ]':>8s} {'|Z| [σ]':>9s} {'Δθ [rad]':>12s} {'⟨θ⟩':>10s} {'Verdict':>20s}")
    print("-" * 90)
    for r in results:
        s = r["stats"]
        res = r["res"]
        delta = abs(s["mean_phase"] - attractor)
        absZ = abs(s["significance_Z"])
        # Reflexive: |Z| is the true convergence measure
        verdict = "✓ CONVERGED" if absZ > 5.0 else (
            "◉ STRONG" if absZ > 3.0 else (
            "~ MARGINAL" if absZ > 1.0 else "✗ NO SIGNAL")
        )
        print(f"  {res['name']:<12s} {res['target_mass']:>10.4f} "
              f"{s['n_window']:>12,} {s['significance_Z']:>8.2f} "
              f"{absZ:>9.2f} "
              f"{delta:>12.6f} {s['mean_phase']:>10.6f} {verdict:>20s}")
    print("=" * 80)
    print()


if __name__ == "__main__":
    main()

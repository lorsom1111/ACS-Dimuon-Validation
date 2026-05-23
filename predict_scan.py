"""
ACS Prediction Test — Scan predicted masses in existing 13 TeV data
====================================================================
Uses the already-downloaded 76.8M event dataset to search for
ACS convergence at the predicted mass points.
"""

import os
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as cfg
from pipeline import calculate_kinematics, apply_quality_cuts, to_cpu
from ingest import load_data
from stats import compute_phase_statistics

cfg.ACTIVE_SOURCE = "run2_nanoaod_13tev"

# ─── Predictions to test ───
PREDICTIONS = [
    {
        "name": "ACS-P1",
        "target_mass": 2.53,
        "mass_window": (2.2, 2.85),
        "color": "#ff6b6b",
        "origin": "J/ψ harmonics (n=3–6), 6× cross-ref",
    },
    {
        "name": "ACS-P2",
        "target_mass": 7.94,
        "mass_window": (7.4, 8.5),
        "color": "#ffd93d",
        "origin": "Υ family harmonics, 4× cross-ref",
    },
    {
        "name": "ACS-P3",
        "target_mass": 8.37,
        "mass_window": (7.9, 8.9),
        "color": "#f0932b",
        "origin": "Υ(1S)+Υ(2S) harmonics, 5× cross-ref",
    },
    {
        "name": "ACS-P4 ⭐",
        "target_mass": 60.6,
        "mass_window": (50.0, 72.0),
        "color": "#00ff88",
        "origin": "Z(n=2) + H(n=1) cross-ref — NEW BOSON?",
    },
]

# Also test some NULL hypothesis controls (random masses where nothing should be)
CONTROLS = [
    {
        "name": "NULL-1",
        "target_mass": 15.0,
        "mass_window": (13.0, 17.0),
        "color": "#555555",
        "origin": "Control: no known resonance",
    },
    {
        "name": "NULL-2",
        "target_mass": 40.0,
        "mass_window": (35.0, 45.0),
        "color": "#555555",
        "origin": "Control: no known resonance",
    },
    {
        "name": "NULL-3",
        "target_mass": 70.0,
        "mass_window": (65.0, 75.0),
        "color": "#555555",
        "origin": "Control: no known resonance",
    },
]

ALL_TARGETS = PREDICTIONS + CONTROLS

print("=" * 70)
print("  ACS PREDICTION SCAN — Testing on 76.8M existing events")
print("=" * 70)

# ─── Load data once ───
print("\n[scan] Loading and computing invariant masses...")
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

    mask = to_cpu(apply_quality_cuts(pt1, pt2, eta1, eta2, q1, q2)).astype(bool)
    if mask.sum() == 0:
        continue

    masses = to_cpu(calculate_kinematics(
        pt1[mask], pt2[mask], eta1[mask], eta2[mask],
        phi1[mask], phi2[mask]
    ))
    data_chunks.append(masses)

all_masses = np.concatenate(data_chunks)
print(f"[scan] Total masses: {len(all_masses):,}")
del data_chunks

# ─── Scan each target ───
results = []
for target in ALL_TARGETS:
    m_t = target["target_mass"]
    lo, hi = target["mass_window"]
    
    mask = (all_masses >= lo) & (all_masses <= hi)
    masses_w = all_masses[mask]
    n_window = len(masses_w)
    
    if n_window == 0:
        print(f"\n[scan] {target['name']}: NO EVENTS in [{lo}, {hi}] GeV")
        results.append({"target": target, "stats": None, "phases": None})
        continue
    
    phases = np.arctan(masses_w / m_t)
    stats = compute_phase_statistics(phases)
    stats["n_window"] = n_window
    
    absZ = abs(stats["significance_Z"])
    delta = abs(stats["mean_phase"] - cfg.ACS_ATTRACTOR)
    
    is_pred = "ACS-P" in target["name"]
    marker = "⚡" if is_pred else "  "
    
    print(f"\n{marker} {target['name']:12s}  M_target={m_t:.2f} GeV  "
          f"[{lo:.1f}, {hi:.1f}] GeV")
    print(f"   N={n_window:>10,}  |  Z={stats['significance_Z']:+.2f}σ  "
          f"|  |Z|={absZ:.2f}σ  |  Δθ={delta:.6f}  "
          f"|  ⟨θ⟩={stats['mean_phase']:.6f}")
    print(f"   Origin: {target['origin']}")
    
    results.append({"target": target, "stats": stats, "phases": phases})


# ─── Summary table ───
print("\n\n" + "=" * 90)
print(f"  {'Target':<14s} {'M [GeV]':>8s} {'N_window':>10s} {'Z [σ]':>9s} "
      f"{'|Z| [σ]':>9s} {'Δθ [rad]':>10s} {'⟨θ⟩':>10s} {'Type':>10s}")
print("-" * 90)

for r in results:
    t = r["target"]
    s = r["stats"]
    if s is None:
        print(f"  {t['name']:<14s} {t['target_mass']:>8.2f} {'—':>10s}")
        continue
    
    absZ = abs(s["significance_Z"])
    delta = abs(s["mean_phase"] - cfg.ACS_ATTRACTOR)
    is_pred = "ACS-P" in t["name"]
    typ = "PREDICT" if is_pred else "CONTROL"
    
    print(f"  {t['name']:<14s} {t['target_mass']:>8.2f} {s['n_window']:>10,} "
          f"{s['significance_Z']:>+9.2f} {absZ:>9.2f} {delta:>10.6f} "
          f"{s['mean_phase']:>10.6f} {typ:>10s}")

print("=" * 90)

# ─── Comparison: predictions vs controls ───
pred_absZ = [abs(r["stats"]["significance_Z"]) for r in results 
             if r["stats"] and "ACS-P" in r["target"]["name"]]
ctrl_absZ = [abs(r["stats"]["significance_Z"]) for r in results 
             if r["stats"] and "NULL" in r["target"]["name"]]

print(f"\n  Mean |Z| predictions: {np.mean(pred_absZ):.2f}σ")
print(f"  Mean |Z| controls:   {np.mean(ctrl_absZ):.2f}σ")
print(f"  Ratio:               {np.mean(pred_absZ)/np.mean(ctrl_absZ):.1f}×")


# ─── Generate comparison plot ───
print("\n[viz] Generating prediction scan plot...")

plt.rcParams.update({
    "figure.facecolor": "#0a0a0f",
    "axes.facecolor": "#0d0d15",
    "axes.edgecolor": "#333355",
    "axes.labelcolor": "#ccccee",
    "text.color": "#ccccee",
    "xtick.color": "#8888aa",
    "ytick.color": "#8888aa",
    "font.family": "monospace",
    "font.size": 9,
})

n_plots = len(ALL_TARGETS)
fig, axes = plt.subplots(2, 4, figsize=(24, 10))
axes = axes.flatten()

attractor = cfg.ACS_ATTRACTOR

for i, r in enumerate(results):
    if i >= len(axes):
        break
    ax = axes[i]
    t = r["target"]
    s = r["stats"]
    phases = r["phases"]
    
    if phases is None:
        ax.text(0.5, 0.5, "NO DATA", transform=ax.transAxes,
                ha="center", va="center", fontsize=14, color="#ff0000")
        continue
    
    # Plot range
    plot_half = 0.08
    plot_lo = attractor - plot_half
    plot_hi = attractor + plot_half
    mask = (phases >= plot_lo) & (phases <= plot_hi)
    
    ax.hist(phases[mask], bins=150, range=(plot_lo, plot_hi),
            color=t["color"], alpha=0.85, edgecolor="none")
    
    ax.axvline(attractor, color="#00ff88", linewidth=2.0,
               linestyle="--", alpha=0.9)
    
    # Signal region
    sig_lo, sig_hi = s["signal_window"]
    ax.axvspan(sig_lo, sig_hi, alpha=0.15, color="#ffffff")
    
    Z = s["significance_Z"]
    absZ = abs(Z)
    delta = abs(s["mean_phase"] - attractor)
    
    info = (f"N = {s['n_window']:,}\n"
            f"Z = {Z:+.2f}σ\n"
            f"|Z| = {absZ:.2f}σ\n"
            f"Δθ = {delta:.6f}")
    
    is_pred = "ACS-P" in t["name"]
    box_edge = t["color"] if is_pred else "#555555"
    props = dict(boxstyle="round,pad=0.3", facecolor="#1a1a2e",
                 edgecolor=box_edge, alpha=0.9)
    ax.text(0.95, 0.95, info, transform=ax.transAxes,
            fontsize=8, va="top", ha="right", bbox=props,
            fontfamily="monospace")
    
    title_color = t["color"] if is_pred else "#888888"
    ax.set_title(f"{t['name']}  (M = {t['target_mass']} GeV)",
                 fontsize=11, fontweight="bold", color=title_color, pad=8)
    
    ax.set_xlabel("θ [rad]", fontsize=9)
    if i % 4 == 0:
        ax.set_ylabel("Events / bin", fontsize=9)
    
    # Verdict
    verdict = "SIGNAL" if absZ > 5.0 else (
        "STRONG" if absZ > 3.0 else (
        "MARGINAL" if absZ > 1.0 else "NULL"))
    verdict_color = "#00ff88" if absZ > 5.0 else (
        "#ffd93d" if absZ > 3.0 else (
        "#ff6b6b" if absZ > 1.0 else "#555555"))
    label = "PREDICTION" if is_pred else "CONTROL"
    ax.text(0.5, 0.02, f"{label} — |Z|={absZ:.1f}σ — {verdict}",
            transform=ax.transAxes, fontsize=7, ha="center", va="bottom",
            color=verdict_color, fontstyle="italic")

fig.suptitle(
    "ACS Prediction Scan — Testing Predicted Masses on 76.8M CMS Events (13 TeV)\n"
    f"Top row: ACS predictions (cross-referenced)  |  Bottom row: Null controls  |  Attractor π/4 = {attractor:.6f}",
    fontsize=13, fontweight="bold", color="#ffffff", y=1.02
)

fig.tight_layout()
outpath = os.path.join(cfg.OUTPUT_DIR, "acs_prediction_scan.png")
fig.savefig(outpath, dpi=200, bbox_inches="tight", facecolor="#0a0a0f")
plt.close()
print(f"[viz] Saved: {outpath}")

print("\n" + "=" * 70)
print("  PREDICTION SCAN COMPLETE")
print("=" * 70)

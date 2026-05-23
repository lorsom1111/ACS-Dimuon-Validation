"""
ACS Omni-Scan — GPU-Parallel Mass Hypothesis Test
===================================================
Single-pass through 76.8M events, tests ALL mass hypotheses
simultaneously on GPU using CuPy vectorized operations.

Strategy:
  1. Read each chunk once
  2. Apply quality cuts (GPU)
  3. Compute invariant masses (GPU)
  4. For EVERY target mass hypothesis simultaneously:
     - Compute ACS phase θ = arctan(M / M_target)
     - Count events in signal/sideband regions
  5. All targets processed in one pass — no re-reading
"""

import os
import sys
import time
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as cfg
from pipeline import calculate_kinematics, apply_quality_cuts, to_cpu, _GPU_AVAILABLE
from ingest import load_data

if _GPU_AVAILABLE:
    import cupy as cp
    xp = cp
    print("[scan] GPU MODE — CuPy on RTX 5090")
else:
    xp = np
    print("[scan] CPU MODE")

cfg.ACTIVE_SOURCE = "run2_nanoaod_13tev"

ACS_ATTRACTOR = float(cfg.ACS_ATTRACTOR)
SIG_HALF = float(cfg.PHASE_SIGNAL_HALFWIDTH)
SB_WIDTH = float(cfg.PHASE_SIDEBAND_WIDTH)

# ═══════════════════════════════════════════════════════════
#  BUILD MASS HYPOTHESIS GRID — ~100 targets for RTX 5090
# ═══════════════════════════════════════════════════════════

# Known resonances (positive controls — should converge)
KNOWN = [
    ("phi",     1.01946),
    ("J/psi",   3.0969),
    ("psi2S",   3.6861),
    ("Y1S",     9.4603),
    ("Y2S",    10.0233),
    ("Y3S",    10.3552),
    ("Z",      91.1876),
    ("H",     125.1),
]
KNOWN_MASSES = {m for _, m in KNOWN}

# ACS cross-referenced predictions (the test)
PREDICTIONS = [
    ("P-0.60",    0.597),
    ("P-0.90",    0.907),
    ("P-1.50",    1.504),
    ("P-1.92",    1.921),
    ("P-2.05",    2.053),
    ("P-2.32",    2.318),
    ("P-2.53",    2.530),   # ⭐ 6× cross-ref
    ("P-2.77",    2.770),
    ("P-4.95",    4.948),
    ("P-5.50",    5.500),
    ("P-6.00",    6.000),
    ("P-6.46",    6.458),
    ("P-6.97",    6.973),
    ("P-7.53",    7.532),
    ("P-7.94",    7.940),   # ⭐ 4× cross-ref
    ("P-8.37",    8.365),   # ⭐ 5× cross-ref
    ("P-44.3",   44.281),
    ("P-60.4",   60.449),   # ⭐⭐ Z+H cross-ref
    ("P-68.3",   68.254),
    ("P-72.9",   72.882),
    ("P-76.0",   75.951),
]
PRED_MASSES = {m for _, m in PREDICTIONS}

# ─── BLIND SWEEP: dense grid, ~100 targets total ───
# Skip masses within 5% of any known or predicted mass
ALL_SWEEP = set()
for m in np.concatenate([
    np.arange(0.3, 5.0, 0.25),   # 0.25 GeV steps below 5 GeV
    np.arange(5.0, 15.0, 0.5),   # 0.5 GeV steps 5-15 GeV
    np.arange(15.0, 50.0, 2.0),  # 2.0 GeV steps 15-50 GeV
    np.arange(50.0, 100.0, 2.0), # 2.0 GeV steps 50-100 GeV
    np.arange(100.0, 200.0, 5.0),# 5.0 GeV steps 100-200 GeV
]):
    m = float(round(m, 1))
    too_close = any(abs(m - k) / max(k, 0.1) < 0.04
                    for k in KNOWN_MASSES | PRED_MASSES)
    if not too_close:
        ALL_SWEEP.add(m)

NULLS = [(f"S-{m:.1f}", m) for m in sorted(ALL_SWEEP)]

ALL_TARGETS = (
    [(f"K-{n}", m, "KNOWN") for n, m in KNOWN] +
    [(n, m, "PRED") for n, m in PREDICTIONS] +
    [(n, m, "NULL") for n, m in NULLS]
)

n_targets = len(ALL_TARGETS)
print(f"\n[scan] {n_targets} mass hypotheses loaded:")
print(f"  {len(KNOWN)} known resonances (positive control)")
print(f"  {len(PREDICTIONS)} ACS predictions (test)")
print(f"  {len(NULLS)} blind sweep points (negative control)")

# Mass windows: ±15% of target mass (or ±10 GeV for heavy)
def get_window(m):
    if m < 5:
        return (m * 0.7, m * 1.3)
    elif m < 50:
        return (m * 0.8, m * 1.2)
    else:
        return (m - 12, m + 12)

# ═══════════════════════════════════════════════════════════
#  ACCUMULATOR ARRAYS (all on GPU)
# ═══════════════════════════════════════════════════════════

# For each target: count N_signal, N_left_sb, N_right_sb, N_window
# Also accumulate phase sums for mean/std
accum = {
    "n_window":   np.zeros(n_targets, dtype=np.int64),
    "n_signal":   np.zeros(n_targets, dtype=np.int64),
    "n_left_sb":  np.zeros(n_targets, dtype=np.int64),
    "n_right_sb": np.zeros(n_targets, dtype=np.int64),
    "phase_sum":  np.zeros(n_targets, dtype=np.float64),
    "phase_sq":   np.zeros(n_targets, dtype=np.float64),
}

# Pre-compute region boundaries for each target
target_masses = np.array([t[1] for t in ALL_TARGETS])
windows_lo = np.array([get_window(t[1])[0] for t in ALL_TARGETS])
windows_hi = np.array([get_window(t[1])[1] for t in ALL_TARGETS])

sig_lo = ACS_ATTRACTOR - SIG_HALF
sig_hi = ACS_ATTRACTOR + SIG_HALF
sb_left_lo = sig_lo - SB_WIDTH
sb_right_hi = sig_hi + SB_WIDTH

# Move to GPU if available
if _GPU_AVAILABLE:
    g_target_masses = cp.asarray(target_masses)
    g_windows_lo = cp.asarray(windows_lo)
    g_windows_hi = cp.asarray(windows_hi)

# ═══════════════════════════════════════════════════════════
#  SINGLE-PASS SCAN
# ═══════════════════════════════════════════════════════════

print(f"\n[scan] Starting single-pass scan over 57 files...")
t0 = time.time()
total_events = 0
chunk_idx = 0

for chunk_data in load_data():
    chunk_idx += 1
    pt1  = chunk_data["pt1"]
    pt2  = chunk_data["pt2"]
    eta1 = chunk_data["eta1"]
    eta2 = chunk_data["eta2"]
    phi1 = chunk_data["phi1"]
    phi2 = chunk_data["phi2"]
    q1   = chunk_data["q1"]
    q2   = chunk_data["q2"]

    # Quality cuts — keep everything on same backend
    if _GPU_AVAILABLE:
        pt1  = cp.asarray(pt1)
        pt2  = cp.asarray(pt2)
        eta1 = cp.asarray(eta1)
        eta2 = cp.asarray(eta2)
        phi1 = cp.asarray(phi1)
        phi2 = cp.asarray(phi2)
        q1   = cp.asarray(q1)
        q2   = cp.asarray(q2)

    cut_mask = apply_quality_cuts(pt1, pt2, eta1, eta2, q1, q2)
    if _GPU_AVAILABLE:
        cut_mask = cp.asarray(cut_mask).astype(bool)
    else:
        cut_mask = np.asarray(cut_mask).astype(bool)

    if int(cut_mask.sum()) == 0:
        continue

    # Invariant mass (GPU)
    masses = calculate_kinematics(
        pt1[cut_mask], pt2[cut_mask], eta1[cut_mask], eta2[cut_mask],
        phi1[cut_mask], phi2[cut_mask]
    )
    n_evt = len(masses)
    total_events += n_evt

    # ── GPU-parallel scan over ALL targets simultaneously ──
    if _GPU_AVAILABLE:
        g_masses = masses if isinstance(masses, cp.ndarray) else cp.asarray(masses)
        # Shape: (n_events, 1) vs (1, n_targets) → broadcasting
        m_col = g_masses[:, None]            # (N, 1)
        mt_row = g_target_masses[None, :]    # (1, T)
        wlo_row = g_windows_lo[None, :]      # (1, T)
        whi_row = g_windows_hi[None, :]      # (1, T)

        # Mass window mask: (N, T) boolean
        in_window = (m_col >= wlo_row) & (m_col <= whi_row)

        # ACS phase for all targets: (N, T)
        phases = cp.arctan(m_col / mt_row)

        # Count events in regions (vectorized across all targets)
        in_sig = in_window & (phases >= sig_lo) & (phases <= sig_hi)
        in_lsb = in_window & (phases >= sb_left_lo) & (phases < sig_lo)
        in_rsb = in_window & (phases > sig_hi) & (phases <= sb_right_hi)

        # Accumulate (sum along event axis → shape (T,))
        n_win = cp.sum(in_window, axis=0)
        n_sig = cp.sum(in_sig, axis=0)
        n_lsb = cp.sum(in_lsb, axis=0)
        n_rsb = cp.sum(in_rsb, axis=0)

        # Phase statistics (masked sum)
        phase_masked = phases * in_window  # zero where not in window
        p_sum = cp.sum(phase_masked, axis=0)
        p_sq  = cp.sum(phase_masked ** 2, axis=0)

        # Transfer to CPU and accumulate
        accum["n_window"]  += cp.asnumpy(n_win)
        accum["n_signal"]  += cp.asnumpy(n_sig)
        accum["n_left_sb"] += cp.asnumpy(n_lsb)
        accum["n_right_sb"]+= cp.asnumpy(n_rsb)
        accum["phase_sum"] += cp.asnumpy(p_sum)
        accum["phase_sq"]  += cp.asnumpy(p_sq)

    else:
        # CPU fallback (same logic, numpy)
        m_col = masses[:, None]
        mt_row = target_masses[None, :]
        wlo_row = windows_lo[None, :]
        whi_row = windows_hi[None, :]

        in_window = (m_col >= wlo_row) & (m_col <= whi_row)
        phases = np.arctan(m_col / mt_row)

        in_sig = in_window & (phases >= sig_lo) & (phases <= sig_hi)
        in_lsb = in_window & (phases >= sb_left_lo) & (phases < sig_lo)
        in_rsb = in_window & (phases > sig_hi) & (phases <= sb_right_hi)

        accum["n_window"]  += np.sum(in_window, axis=0)
        accum["n_signal"]  += np.sum(in_sig, axis=0)
        accum["n_left_sb"] += np.sum(in_lsb, axis=0)
        accum["n_right_sb"]+= np.sum(in_rsb, axis=0)

        phase_masked = phases * in_window
        accum["phase_sum"] += np.sum(phase_masked, axis=0)
        accum["phase_sq"]  += np.sum(phase_masked ** 2, axis=0)

    if chunk_idx % 10 == 0:
        elapsed = time.time() - t0
        print(f"  [{chunk_idx} chunks | {total_events:,} events | {elapsed:.0f}s]")

elapsed = time.time() - t0
print(f"\n[scan] Complete: {total_events:,} events in {elapsed:.1f}s")
print(f"[scan] {n_targets} targets × {total_events:,} events = "
      f"{n_targets * total_events / 1e9:.2f}B phase evaluations")

# ═══════════════════════════════════════════════════════════
#  COMPUTE STATISTICS
# ═══════════════════════════════════════════════════════════

print("\n[scan] Computing significance for all targets...")

results = []
for i, (name, m_target, typ) in enumerate(ALL_TARGETS):
    n_win = int(accum["n_window"][i])
    n_sig = int(accum["n_signal"][i])
    n_lsb = int(accum["n_left_sb"][i])
    n_rsb = int(accum["n_right_sb"][i])

    # Background estimate
    signal_width = sig_hi - sig_lo
    total_sb_width = 2.0 * SB_WIDTH
    total_sb = n_lsb + n_rsb
    B = total_sb * (signal_width / total_sb_width) if total_sb_width > 0 else 0
    S = n_sig - B
    Z = S / np.sqrt(B) if B > 0 else 0.0

    # Mean phase
    mean_phase = accum["phase_sum"][i] / n_win if n_win > 0 else 0
    var_phase = (accum["phase_sq"][i] / n_win - mean_phase**2) if n_win > 0 else 0
    std_phase = np.sqrt(max(0, var_phase))

    results.append({
        "name": name,
        "mass": m_target,
        "type": typ,
        "n_window": n_win,
        "n_signal": n_sig,
        "B": B,
        "S": S,
        "Z": Z,
        "absZ": abs(Z),
        "mean_phase": float(mean_phase),
        "std_phase": float(std_phase),
        "delta_theta": abs(float(mean_phase) - ACS_ATTRACTOR),
    })

# ═══════════════════════════════════════════════════════════
#  RESULTS TABLE
# ═══════════════════════════════════════════════════════════

print("\n" + "=" * 100)
print(f"  {'Target':<14s} {'M [GeV]':>8s} {'N_window':>10s} {'Z [σ]':>9s} "
      f"{'|Z| [σ]':>8s} {'Δθ':>10s} {'⟨θ⟩':>10s} {'Type':>6s} {'Verdict':>12s}")
print("-" * 100)

for r in sorted(results, key=lambda x: -x["absZ"]):
    absZ = r["absZ"]
    verdict = "✓ CONV" if absZ > 5.0 else (
        "◉ STRONG" if absZ > 3.0 else (
        "~ MARG" if absZ > 1.0 else "✗ NULL"))
    
    marker = ""
    if r["type"] == "PRED" and absZ > 3.0:
        marker = " ⚡"
    
    print(f"  {r['name']:<14s} {r['mass']:>8.3f} {r['n_window']:>10,} "
          f"{r['Z']:>+9.2f} {absZ:>8.2f} {r['delta_theta']:>10.6f} "
          f"{r['mean_phase']:>10.6f} {r['type']:>6s} {verdict:>12s}{marker}")

# ── Category summary ──
for typ in ["KNOWN", "PRED", "NULL"]:
    subset = [r for r in results if r["type"] == typ]
    mean_absZ = np.mean([r["absZ"] for r in subset])
    max_absZ = max([r["absZ"] for r in subset])
    n_sig = sum(1 for r in subset if r["absZ"] > 5.0)
    print(f"\n  {typ:>6s}: mean |Z| = {mean_absZ:.2f}σ, "
          f"max = {max_absZ:.2f}σ, {n_sig}/{len(subset)} above 5σ")

# ═══════════════════════════════════════════════════════════
#  VISUALIZATION
# ═══════════════════════════════════════════════════════════

print("\n[viz] Generating scan results plot...")

plt.rcParams.update({
    "figure.facecolor": "#0a0a0f",
    "axes.facecolor": "#0d0d15",
    "axes.edgecolor": "#333355",
    "axes.labelcolor": "#ccccee",
    "text.color": "#ccccee",
    "xtick.color": "#8888aa",
    "ytick.color": "#8888aa",
    "font.family": "monospace",
})

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(20, 12),
                                gridspec_kw={"height_ratios": [3, 2]})

fig.suptitle("ACS Omni-Scan — GPU-Parallel Mass Hypothesis Test\n"
             f"{n_targets} targets × {total_events:,} events = "
             f"{n_targets * total_events / 1e9:.1f}B evaluations "
             f"in {elapsed:.0f}s on RTX 5090",
             fontsize=14, fontweight="bold", color="white", y=0.98)

# Panel 1: |Z| vs Mass for all targets
for r in results:
    if r["type"] == "KNOWN":
        ax1.scatter(r["mass"], r["absZ"], s=200, c="#00ff88", marker="D",
                    zorder=10, edgecolors="white", linewidth=1)
    elif r["type"] == "PRED":
        ax1.scatter(r["mass"], r["absZ"], s=150, c="#ff6b6b", marker="*",
                    zorder=8, edgecolors="white", linewidth=0.5)
    else:
        ax1.scatter(r["mass"], r["absZ"], s=80, c="#555555", marker="o",
                    zorder=5, edgecolors="#888888", linewidth=0.5, alpha=0.6)

# Labels for high-significance
for r in results:
    if r["absZ"] > 10 or (r["type"] == "PRED" and r["absZ"] > 2):
        ax1.annotate(f"{r['name']}\n|Z|={r['absZ']:.1f}σ",
                     (r["mass"], r["absZ"]),
                     textcoords="offset points", xytext=(0, 12),
                     ha="center", fontsize=7,
                     color="#00ff88" if r["type"] == "KNOWN" else (
                         "#ff6b6b" if r["type"] == "PRED" else "#888888"))

ax1.axhline(y=5, color="lime", linestyle="--", alpha=0.3, linewidth=1)
ax1.text(0.8, 5.5, "5σ discovery", color="lime", alpha=0.5, fontsize=9,
         transform=ax1.get_yaxis_transform())
ax1.set_xscale("log")
ax1.set_yscale("log")
ax1.set_xlabel("Mass [GeV]", fontsize=12)
ax1.set_ylabel("|Z| [σ]", fontsize=12)
ax1.set_title("Convergence Significance vs Mass", fontsize=13, fontweight="bold")

# Legend
ax1.scatter([], [], s=200, c="#00ff88", marker="D", label="Known resonances")
ax1.scatter([], [], s=150, c="#ff6b6b", marker="*", label="ACS predictions")
ax1.scatter([], [], s=80, c="#555555", marker="o", label="Null controls")
ax1.legend(fontsize=10, loc="upper right")
ax1.grid(alpha=0.15)

# Panel 2: |Z| bar chart by category
categories = []
for r in sorted(results, key=lambda x: x["mass"]):
    categories.append(r)

x_pos = np.arange(len(categories))
colors = ["#00ff88" if c["type"] == "KNOWN" else
          "#ff6b6b" if c["type"] == "PRED" else "#444444"
          for c in categories]

bars = ax2.bar(x_pos, [c["absZ"] for c in categories],
               color=colors, edgecolor="white", linewidth=0.3, alpha=0.85)
ax2.axhline(y=5, color="lime", linestyle="--", alpha=0.3)
ax2.set_xticks(x_pos)
ax2.set_xticklabels([f"{c['name']}\n{c['mass']:.1f}" for c in categories],
                     fontsize=6, rotation=45, ha="right")
ax2.set_ylabel("|Z| [σ]", fontsize=12)
ax2.set_yscale("log")
ax2.set_title("All Targets Ranked by Mass — Green=Known, Red=Predicted, Gray=Null",
              fontsize=12, fontweight="bold")
ax2.grid(axis="y", alpha=0.15)

plt.tight_layout(rect=[0, 0, 1, 0.94])
outpath = os.path.join(cfg.OUTPUT_DIR, "acs_omni_scan.png")
fig.savefig(outpath, dpi=200, bbox_inches="tight", facecolor="#0a0a0f")
plt.close()
print(f"[viz] Saved: {outpath}")

print("\n" + "=" * 70)
print("  OMNI-SCAN COMPLETE")
print("=" * 70)

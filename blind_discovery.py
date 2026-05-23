"""
ACS Blind Discovery — Fine-grained ρ/ω Analysis
=================================================
The omni-scan NULL control at 0.8 GeV showed |Z| = 13.2σ.
This is the ρ(770)/ω(782) region — particles we never told ACS about.

This script performs a FINE MASS SWEEP (5 MeV steps) across
0.5 – 1.5 GeV to map exactly where ACS finds convergence,
and compare with PDG resonance positions.
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
    print("[rho] GPU MODE — CuPy")
else:
    xp = np
    print("[rho] CPU MODE")

cfg.ACTIVE_SOURCE = "run2_nanoaod_13tev"

ACS_ATTRACTOR = float(cfg.ACS_ATTRACTOR)
SIG_HALF = float(cfg.PHASE_SIGNAL_HALFWIDTH)
SB_WIDTH = float(cfg.PHASE_SIDEBAND_WIDTH)

# ═══════════════════════════════════════════════════════════
#  FINE MASS SWEEP: 0.3 – 2.0 GeV in 5 MeV steps
# ═══════════════════════════════════════════════════════════

sweep_masses = np.arange(0.300, 2.001, 0.005)  # 340 mass hypotheses
n_targets = len(sweep_masses)
print(f"\n[rho] Fine sweep: {n_targets} mass points from "
      f"{sweep_masses[0]:.3f} to {sweep_masses[-1]:.3f} GeV (5 MeV steps)")

# PDG resonances in this range for reference
PDG = {
    "ρ(770)":   0.77526,
    "ω(782)":   0.78265,
    "φ(1020)":  1.01946,
    "η(548)":   0.54786,
    "η'(958)":  0.95778,
    "f₀(980)":  0.990,
    "a₀(980)":  0.980,
}

# Mass window for each hypothesis: ±30%
windows_lo = sweep_masses * 0.70
windows_hi = sweep_masses * 1.30

sig_lo = ACS_ATTRACTOR - SIG_HALF
sig_hi = ACS_ATTRACTOR + SIG_HALF
sb_left_lo = sig_lo - SB_WIDTH
sb_right_hi = sig_hi + SB_WIDTH

# Accumulators
accum_n_win   = np.zeros(n_targets, dtype=np.int64)
accum_n_sig   = np.zeros(n_targets, dtype=np.int64)
accum_n_lsb   = np.zeros(n_targets, dtype=np.int64)
accum_n_rsb   = np.zeros(n_targets, dtype=np.int64)
accum_ph_sum  = np.zeros(n_targets, dtype=np.float64)
accum_ph_sq   = np.zeros(n_targets, dtype=np.float64)

if _GPU_AVAILABLE:
    g_targets = cp.asarray(sweep_masses)
    g_wlo = cp.asarray(windows_lo)
    g_whi = cp.asarray(windows_hi)

# ═══════════════════════════════════════════════════════════
#  SINGLE-PASS SCAN
# ═══════════════════════════════════════════════════════════

print(f"\n[rho] Single-pass scan: {n_targets} targets × 57 files...")
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

    masses = calculate_kinematics(
        pt1[cut_mask], pt2[cut_mask], eta1[cut_mask], eta2[cut_mask],
        phi1[cut_mask], phi2[cut_mask]
    )
    n_evt = len(masses)
    total_events += n_evt

    # ── GPU: process targets in batches of BATCH_T to avoid OOM ──
    BATCH_T = 85  # 85 targets per GPU pass (safe for 16GB VRAM)

    if _GPU_AVAILABLE:
        g_m = masses if isinstance(masses, cp.ndarray) else cp.asarray(masses)

        for t_start in range(0, n_targets, BATCH_T):
            t_end = min(t_start + BATCH_T, n_targets)
            t_slice = slice(t_start, t_end)

            m_col = g_m[:, None]
            mt_row = g_targets[None, t_slice]
            wlo_row = g_wlo[None, t_slice]
            whi_row = g_whi[None, t_slice]

            in_win = (m_col >= wlo_row) & (m_col <= whi_row)
            phases = cp.arctan(m_col / mt_row)

            in_sig = in_win & (phases >= sig_lo) & (phases <= sig_hi)
            in_lsb = in_win & (phases >= sb_left_lo) & (phases < sig_lo)
            in_rsb = in_win & (phases > sig_hi) & (phases <= sb_right_hi)

            accum_n_win[t_slice] += cp.asnumpy(cp.sum(in_win, axis=0))
            accum_n_sig[t_slice] += cp.asnumpy(cp.sum(in_sig, axis=0))
            accum_n_lsb[t_slice] += cp.asnumpy(cp.sum(in_lsb, axis=0))
            accum_n_rsb[t_slice] += cp.asnumpy(cp.sum(in_rsb, axis=0))

            ph_masked = phases * in_win
            accum_ph_sum[t_slice] += cp.asnumpy(cp.sum(ph_masked, axis=0))
            accum_ph_sq[t_slice]  += cp.asnumpy(cp.sum(ph_masked ** 2, axis=0))

            del in_win, phases, in_sig, in_lsb, in_rsb, ph_masked
            cp.get_default_memory_pool().free_all_blocks()

    else:
        m_col = masses[:, None]
        mt_row = sweep_masses[None, :]
        wlo_row = windows_lo[None, :]
        whi_row = windows_hi[None, :]

        in_win = (m_col >= wlo_row) & (m_col <= whi_row)
        phases = np.arctan(m_col / mt_row)

        in_sig = in_win & (phases >= sig_lo) & (phases <= sig_hi)
        in_lsb = in_win & (phases >= sb_left_lo) & (phases < sig_lo)
        in_rsb = in_win & (phases > sig_hi) & (phases <= sb_right_hi)

        accum_n_win += np.sum(in_win, axis=0)
        accum_n_sig += np.sum(in_sig, axis=0)
        accum_n_lsb += np.sum(in_lsb, axis=0)
        accum_n_rsb += np.sum(in_rsb, axis=0)

        ph_masked = phases * in_win
        accum_ph_sum += np.sum(ph_masked, axis=0)
        accum_ph_sq  += np.sum(ph_masked ** 2, axis=0)

    if chunk_idx % 10 == 0:
        elapsed = time.time() - t0
        print(f"  [{chunk_idx} chunks | {total_events:,} events | {elapsed:.0f}s]")

elapsed = time.time() - t0
print(f"\n[rho] Complete: {total_events:,} events in {elapsed:.1f}s")
print(f"[rho] {n_targets} × {total_events:,} = "
      f"{n_targets * total_events / 1e9:.2f}B evaluations")

# ═══════════════════════════════════════════════════════════
#  COMPUTE Z-SCORES
# ═══════════════════════════════════════════════════════════

sig_width = sig_hi - sig_lo
sb_width_total = 2.0 * SB_WIDTH

Z_scores = np.zeros(n_targets)
absZ_scores = np.zeros(n_targets)
mean_phases = np.zeros(n_targets)

for i in range(n_targets):
    n_win = accum_n_win[i]
    n_sig = accum_n_sig[i]
    total_sb = accum_n_lsb[i] + accum_n_rsb[i]

    B = total_sb * (sig_width / sb_width_total) if sb_width_total > 0 else 0
    S = n_sig - B
    Z = S / np.sqrt(B) if B > 0 else 0
    Z_scores[i] = Z
    absZ_scores[i] = abs(Z)
    mean_phases[i] = accum_ph_sum[i] / n_win if n_win > 0 else 0

# ═══════════════════════════════════════════════════════════
#  FIND PEAKS
# ═══════════════════════════════════════════════════════════

print("\n── |Z| Peaks in Fine Sweep ──")
print(f"  {'M [GeV]':>10s} {'|Z| [σ]':>10s} {'Z [σ]':>10s} {'N_window':>10s} "
      f"{'⟨θ⟩':>10s} {'Nearest PDG':>20s}")
print("-" * 80)

# Find local maxima
from scipy.signal import find_peaks
peaks, properties = find_peaks(absZ_scores, height=3.0, distance=10, prominence=1.0)

for p in sorted(peaks, key=lambda x: -absZ_scores[x]):
    m = sweep_masses[p]
    aZ = absZ_scores[p]
    Z = Z_scores[p]
    nw = accum_n_win[p]
    mp = mean_phases[p]

    # Find nearest PDG particle
    nearest = min(PDG.items(), key=lambda x: abs(x[1] - m))
    dist_mev = abs(nearest[1] - m) * 1000

    print(f"  {m:>10.4f} {aZ:>10.2f} {Z:>+10.2f} {nw:>10,} "
          f"{mp:>10.6f} {nearest[0]:>12s} (Δ={dist_mev:.0f} MeV)")

# ═══════════════════════════════════════════════════════════
#  VISUALIZATION
# ═══════════════════════════════════════════════════════════

print("\n[viz] Generating fine-sweep plot...")

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

fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(20, 16),
                                     gridspec_kw={"height_ratios": [3, 2, 2]})

fig.suptitle("ACS Blind Discovery — Fine Mass Sweep (5 MeV resolution)\n"
             f"{n_targets} mass hypotheses × {total_events:,} events "
             f"in {elapsed:.0f}s on RTX 5090",
             fontsize=14, fontweight="bold", color="white", y=0.98)

# Panel 1: |Z| vs mass — the main result
ax1.fill_between(sweep_masses, absZ_scores, alpha=0.3, color="#00ccff")
ax1.plot(sweep_masses, absZ_scores, color="#00ccff", linewidth=1.5, alpha=0.9)

# Mark peaks
for p in peaks:
    ax1.plot(sweep_masses[p], absZ_scores[p], "v", color="#ff6b6b",
             markersize=10, zorder=10)

# Mark PDG positions
for pname, pmass in PDG.items():
    if 0.3 <= pmass <= 2.0:
        ax1.axvline(pmass, color="#ffd93d", linewidth=1.5, alpha=0.4,
                     linestyle="--")
        # Find |Z| at this mass
        idx = np.argmin(np.abs(sweep_masses - pmass))
        ax1.annotate(f"{pname}\n{pmass:.3f} GeV\n|Z|={absZ_scores[idx]:.1f}σ",
                     (pmass, absZ_scores[idx]),
                     textcoords="offset points", xytext=(15, 10),
                     ha="left", fontsize=8, color="#ffd93d",
                     arrowprops=dict(arrowstyle="->", color="#ffd93d", alpha=0.5),
                     bbox=dict(boxstyle="round,pad=0.2", facecolor="#1a1a2e",
                              edgecolor="#ffd93d", alpha=0.8))

ax1.axhline(5, color="lime", linestyle="--", alpha=0.3, linewidth=1)
ax1.text(1.9, 5.5, "5σ", color="lime", alpha=0.5, fontsize=9)
ax1.set_ylabel("|Z| [σ]", fontsize=12)
ax1.set_title("ACS Convergence Significance — Fine Mass Sweep (0.3 – 2.0 GeV)",
              fontsize=13, fontweight="bold")
ax1.set_xlim(0.3, 2.0)
ax1.grid(alpha=0.15)

# Panel 2: Signed Z (reflexive)
ax2.fill_between(sweep_masses, Z_scores, 0, where=Z_scores > 0,
                  alpha=0.4, color="#00ff88", label="Z > 0 (concentration)")
ax2.fill_between(sweep_masses, Z_scores, 0, where=Z_scores < 0,
                  alpha=0.4, color="#ff6b6b", label="Z < 0 (anti-concentration)")
ax2.plot(sweep_masses, Z_scores, color="white", linewidth=0.8, alpha=0.5)

for pname, pmass in PDG.items():
    if 0.3 <= pmass <= 2.0:
        ax2.axvline(pmass, color="#ffd93d", linewidth=1, alpha=0.3, linestyle="--")

ax2.axhline(0, color="white", linewidth=0.5, alpha=0.3)
ax2.axhline(5, color="lime", linestyle="--", alpha=0.2)
ax2.axhline(-5, color="lime", linestyle="--", alpha=0.2)
ax2.set_ylabel("Z [σ] (signed)", fontsize=12)
ax2.set_title("Reflexive Z — Polarity of ACS Convergence", fontsize=13, fontweight="bold")
ax2.set_xlim(0.3, 2.0)
ax2.legend(fontsize=9, loc="lower left")
ax2.grid(alpha=0.15)

# Panel 3: N_window (event density) — to show this isn't just statistics
ax3.fill_between(sweep_masses, accum_n_win, alpha=0.4, color="#888888")
ax3.plot(sweep_masses, accum_n_win, color="#aaaaaa", linewidth=1)
for pname, pmass in PDG.items():
    if 0.3 <= pmass <= 2.0:
        ax3.axvline(pmass, color="#ffd93d", linewidth=1, alpha=0.3, linestyle="--")
        idx = np.argmin(np.abs(sweep_masses - pmass))
        ax3.annotate(pname, (pmass, accum_n_win[idx]),
                     textcoords="offset points", xytext=(5, 10),
                     fontsize=7, color="#ffd93d")

ax3.set_xlabel("M_target [GeV]", fontsize=12)
ax3.set_ylabel("N events in window", fontsize=12)
ax3.set_title("Event Density per Mass Window — Not Correlated with |Z|",
              fontsize=13, fontweight="bold")
ax3.set_xlim(0.3, 2.0)
ax3.grid(alpha=0.15)

plt.tight_layout(rect=[0, 0, 1, 0.94])
outpath = os.path.join(cfg.OUTPUT_DIR, "acs_blind_discovery_rho_omega.png")
fig.savefig(outpath, dpi=200, bbox_inches="tight", facecolor="#0a0a0f")
plt.close()
print(f"[viz] Saved: {outpath}")

print("\n" + "=" * 70)
print("  BLIND DISCOVERY ANALYSIS COMPLETE")
print("=" * 70)

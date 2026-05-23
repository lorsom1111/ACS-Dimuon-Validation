"""
ACS Blind Discovery — 230 GeV Dark Scalar Search
=================================================
Dedicated search in the 200 - 260 GeV region to look for
the predicted Koch scalar state (mt * 4/3 ~ 230.3 GeV).
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
    print("[230GeV] GPU MODE — CuPy")
else:
    xp = np
    print("[230GeV] CPU MODE")

cfg.ACTIVE_SOURCE = "run2_nanoaod_13tev"

ACS_ATTRACTOR = float(cfg.ACS_ATTRACTOR)
SIG_HALF = float(cfg.PHASE_SIGNAL_HALFWIDTH)
SB_WIDTH = float(cfg.PHASE_SIDEBAND_WIDTH)

# ═══════════════════════════════════════════════════════════
#  HIGH MASS SWEEP: 200 – 260 GeV in 0.5 GeV steps
# ═══════════════════════════════════════════════════════════

sweep_masses = np.arange(200.0, 260.1, 0.5)
n_targets = len(sweep_masses)
print(f"\n[230GeV] High-mass sweep: {n_targets} mass points from "
      f"{sweep_masses[0]:.1f} to {sweep_masses[-1]:.1f} GeV (0.5 GeV steps)")

# Mass window for each hypothesis: ±15 GeV
windows_lo = sweep_masses - 15.0
windows_hi = sweep_masses + 15.0

sig_lo = ACS_ATTRACTOR - SIG_HALF
sig_hi = ACS_ATTRACTOR + SIG_HALF
sb_left_lo = sig_lo - SB_WIDTH
sb_right_hi = sig_hi + SB_WIDTH

# Accumulators
accum_n_win   = np.zeros(n_targets, dtype=np.int64)
accum_n_sig   = np.zeros(n_targets, dtype=np.int64)
accum_n_lsb   = np.zeros(n_targets, dtype=np.int64)
accum_n_rsb   = np.zeros(n_targets, dtype=np.int64)

if _GPU_AVAILABLE:
    g_targets = cp.asarray(sweep_masses)
    g_wlo = cp.asarray(windows_lo)
    g_whi = cp.asarray(windows_hi)

# ═══════════════════════════════════════════════════════════
#  SINGLE-PASS SCAN
# ═══════════════════════════════════════════════════════════

print(f"\n[230GeV] Single-pass scan over {n_targets} targets...")
t0 = time.time()
total_events = 0
chunk_idx = 0

for chunk_data in load_data():
    chunk_idx += 1
    pt1, pt2 = chunk_data["pt1"], chunk_data["pt2"]
    eta1, eta2 = chunk_data["eta1"], chunk_data["eta2"]
    phi1, phi2 = chunk_data["phi1"], chunk_data["phi2"]
    q1, q2 = chunk_data["q1"], chunk_data["q2"]

    if _GPU_AVAILABLE:
        pt1, pt2 = cp.asarray(pt1), cp.asarray(pt2)
        eta1, eta2 = cp.asarray(eta1), cp.asarray(eta2)
        phi1, phi2 = cp.asarray(phi1), cp.asarray(phi2)
        q1, q2 = cp.asarray(q1), cp.asarray(q2)

    cut_mask = apply_quality_cuts(pt1, pt2, eta1, eta2, q1, q2)
    if _GPU_AVAILABLE: cut_mask = cp.asarray(cut_mask).astype(bool)
    else: cut_mask = np.asarray(cut_mask).astype(bool)

    if int(cut_mask.sum()) == 0: continue

    masses = calculate_kinematics(
        pt1[cut_mask], pt2[cut_mask], eta1[cut_mask], eta2[cut_mask],
        phi1[cut_mask], phi2[cut_mask]
    )
    total_events += len(masses)

    if _GPU_AVAILABLE:
        g_m = masses if isinstance(masses, cp.ndarray) else cp.asarray(masses)
        m_col = g_m[:, None]
        mt_row = g_targets[None, :]
        wlo_row = g_wlo[None, :]
        whi_row = g_whi[None, :]

        in_win = (m_col >= wlo_row) & (m_col <= whi_row)
        phases = cp.arctan(m_col / mt_row)

        in_sig = in_win & (phases >= sig_lo) & (phases <= sig_hi)
        in_lsb = in_win & (phases >= sb_left_lo) & (phases < sig_lo)
        in_rsb = in_win & (phases > sig_hi) & (phases <= sb_right_hi)

        accum_n_win += cp.asnumpy(cp.sum(in_win, axis=0))
        accum_n_sig += cp.asnumpy(cp.sum(in_sig, axis=0))
        accum_n_lsb += cp.asnumpy(cp.sum(in_lsb, axis=0))
        accum_n_rsb += cp.asnumpy(cp.sum(in_rsb, axis=0))
        
        del in_win, phases, in_sig, in_lsb, in_rsb
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

    if chunk_idx % 10 == 0:
        print(f"  [{chunk_idx} chunks | {total_events:,} events | {time.time()-t0:.0f}s]")

elapsed = time.time() - t0
print(f"\n[230GeV] Complete: {total_events:,} events in {elapsed:.1f}s")

# ═══════════════════════════════════════════════════════════
#  COMPUTE Z-SCORES
# ═══════════════════════════════════════════════════════════
sig_width = sig_hi - sig_lo
sb_width_total = 2.0 * SB_WIDTH

Z_scores = np.zeros(n_targets)
for i in range(n_targets):
    n_sig = accum_n_sig[i]
    total_sb = accum_n_lsb[i] + accum_n_rsb[i]
    B = total_sb * (sig_width / sb_width_total) if sb_width_total > 0 else 0
    S = n_sig - B
    Z_scores[i] = S / np.sqrt(B) if B > 0 else 0

# ═══════════════════════════════════════════════════════════
#  FIND PEAKS & OUTPUT
# ═══════════════════════════════════════════════════════════
print("\n── |Z| Peaks near 230 GeV ──")
print(f"  {'M [GeV]':>10s} {'|Z| [σ]':>10s} {'Z [σ]':>10s} {'N_window':>10s}")
print("-" * 50)

from scipy.signal import find_peaks
peaks, _ = find_peaks(np.abs(Z_scores), height=1.5, distance=3)

for p in sorted(peaks, key=lambda x: -np.abs(Z_scores[x])):
    m = sweep_masses[p]
    Z = Z_scores[p]
    aZ = abs(Z)
    nw = accum_n_win[p]
    print(f"  {m:>10.1f} {aZ:>10.2f} {Z:>+10.2f} {nw:>10,}")

# ═══════════════════════════════════════════════════════════
#  VISUALIZATION
# ═══════════════════════════════════════════════════════════
fig, ax1 = plt.subplots(1, 1, figsize=(14, 6))
fig.suptitle("ACS Blind Discovery — Dark Scalar Region (200 - 260 GeV)", color="white")
fig.patch.set_facecolor("#0a0a0f")
ax1.set_facecolor("#0d0d15")

ax1.plot(sweep_masses, np.abs(Z_scores), color="#00ccff", linewidth=2)
ax1.fill_between(sweep_masses, np.abs(Z_scores), alpha=0.3, color="#00ccff")
ax1.axvline(230.3, color="#ff6b6b", linestyle="--", alpha=0.8, linewidth=2, label="Koch Prediction: 230.3 GeV")

for p in peaks:
    if np.abs(Z_scores[p]) > 2.0:
        ax1.annotate(f"{sweep_masses[p]:.1f} GeV\n|Z|={np.abs(Z_scores[p]):.1f}σ",
                     (sweep_masses[p], np.abs(Z_scores[p])),
                     textcoords="offset points", xytext=(0, 10), ha="center", color="white")

ax1.set_xlabel("Mass [GeV]", color="white")
ax1.set_ylabel("|Z| [σ]", color="white")
ax1.tick_params(colors="white")
ax1.grid(alpha=0.15)
ax1.legend()

outpath = os.path.join(cfg.OUTPUT_DIR, "acs_blind_230gev.png")
fig.savefig(outpath, dpi=200, bbox_inches="tight", facecolor="#0a0a0f")
plt.close()
print(f"\n[viz] Saved: {outpath}")

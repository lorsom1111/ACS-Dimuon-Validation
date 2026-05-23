"""
ACS NEW CANDIDATE VALIDATION
==============================
Three-pronged validation of the anomalous signals:

1. RAW MASS SPECTRUM — plot invariant mass in 7-9 GeV (and 20-27 GeV)
   to check for visible bumps independent of ACS.

2. SPLIT-SAMPLE CROSS-VALIDATION — divide 57 ROOT files into two
   independent halves. Run ACS on each half separately. Signal must
   appear in BOTH halves to be real.

3. LOOK-ELSEWHERE EFFECT (LEE) — correct the local p-values for
   the 2131 mass hypotheses tested (trial factor correction).
"""

import os, sys, time, math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats
from scipy.signal import find_peaks

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as cfg
from pipeline import calculate_kinematics, apply_quality_cuts, _GPU_AVAILABLE
from ingest import load_data

if _GPU_AVAILABLE:
    import cupy as cp
    xp = cp
    print("[VAL] GPU MODE")
else:
    xp = np
    print("[VAL] CPU MODE")

cfg.ACTIVE_SOURCE = "run2_nanoaod_13tev"

ACS_ATTRACTOR = float(cfg.ACS_ATTRACTOR)
SIG_HALF = float(cfg.PHASE_SIGNAL_HALFWIDTH)
SB_WIDTH = float(cfg.PHASE_SIDEBAND_WIDTH)
sig_lo = ACS_ATTRACTOR - SIG_HALF
sig_hi = ACS_ATTRACTOR + SIG_HALF
sb_left_lo = sig_lo - SB_WIDTH
sb_right_hi = sig_hi + SB_WIDTH
sig_width = sig_hi - sig_lo
sb_width_total = 2.0 * SB_WIDTH

# ═══════════════════════════════════════════════════════════
#  CANDIDATE REGIONS FOR VALIDATION
# ═══════════════════════════════════════════════════════════

# Fine ACS sweep around candidates
sweep_bbbar = np.arange(7.50, 8.60, 0.002)   # 2 MeV, bb̄ threshold
sweep_dy    = np.arange(20.0, 27.0, 0.010)    # 10 MeV, DY desert
sweep = np.concatenate([sweep_bbbar, sweep_dy])
n_targets = len(sweep)
n_bbbar = len(sweep_bbbar)
n_dy = len(sweep_dy)

# Mass windows
def get_window(m):
    if m < 12:
        return (m * 0.80, m * 1.20)
    else:
        return (m * 0.85, m * 1.15)

windows_lo = np.array([get_window(m)[0] for m in sweep])
windows_hi = np.array([get_window(m)[1] for m in sweep])

# Raw mass histogram bins
hist_bins_bb = np.arange(5.0, 12.0, 0.010)     # 10 MeV bins, 5-12 GeV
hist_bins_dy = np.arange(15.0, 35.0, 0.050)     # 50 MeV bins, 15-35 GeV

# Split accumulators: A = odd files, B = even files
# ACS accumulators
acc = {}
for label in ["A", "B", "ALL"]:
    acc[label] = {
        "n_sig": np.zeros(n_targets, dtype=np.int64),
        "n_lsb": np.zeros(n_targets, dtype=np.int64),
        "n_rsb": np.zeros(n_targets, dtype=np.int64),
        "n_win": np.zeros(n_targets, dtype=np.int64),
        "n_evt": 0,
    }
    # Raw mass histograms
    acc[label]["hist_bb"] = np.zeros(len(hist_bins_bb) - 1, dtype=np.int64)
    acc[label]["hist_dy"] = np.zeros(len(hist_bins_dy) - 1, dtype=np.int64)

if _GPU_AVAILABLE:
    g_targets = cp.asarray(sweep)
    g_wlo = cp.asarray(windows_lo)
    g_whi = cp.asarray(windows_hi)

BATCH_T = 80

# ═══════════════════════════════════════════════════════════
#  SINGLE-PASS: ACS + RAW HISTOGRAMS + SPLIT-SAMPLE
# ═══════════════════════════════════════════════════════════

print(f"\n[VAL] Validation scan: {n_targets} ACS targets + raw histograms")
print(f"[VAL] Split: A = odd files (1,3,5,...), B = even files (2,4,6,...)\n")

t0 = time.time()
file_idx = 0

for chunk_data in load_data():
    file_idx += 1
    # Determine split: odd = A, even = B
    split_label = "A" if (file_idx % 2 == 1) else "B"

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

    if int(cut_mask.sum()) == 0:
        continue

    masses = calculate_kinematics(
        pt1[cut_mask], pt2[cut_mask], eta1[cut_mask], eta2[cut_mask],
        phi1[cut_mask], phi2[cut_mask]
    )
    n_evt = len(masses)

    if _GPU_AVAILABLE:
        masses_cpu = cp.asnumpy(masses)
        g_m = masses if isinstance(masses, cp.ndarray) else cp.asarray(masses)
    else:
        masses_cpu = np.asarray(masses)
        g_m = masses_cpu

    # ── Raw mass histograms ──
    for label in [split_label, "ALL"]:
        acc[label]["hist_bb"] += np.histogram(masses_cpu, bins=hist_bins_bb)[0]
        acc[label]["hist_dy"] += np.histogram(masses_cpu, bins=hist_bins_dy)[0]
        acc[label]["n_evt"] += n_evt

    # ── ACS phase analysis ──
    if _GPU_AVAILABLE:
        for t_start in range(0, n_targets, BATCH_T):
            t_end = min(t_start + BATCH_T, n_targets)
            t_slice = slice(t_start, t_end)

            m_col = g_m[:, None]
            mt_row = g_targets[None, t_slice]

            in_win = (m_col >= g_wlo[None, t_slice]) & (m_col <= g_whi[None, t_slice])
            phases = cp.arctan(m_col / mt_row)

            in_sig = in_win & (phases >= sig_lo) & (phases <= sig_hi)
            in_lsb = in_win & (phases >= sb_left_lo) & (phases < sig_lo)
            in_rsb = in_win & (phases > sig_hi) & (phases <= sb_right_hi)

            for label in [split_label, "ALL"]:
                acc[label]["n_win"][t_slice] += cp.asnumpy(cp.sum(in_win, axis=0))
                acc[label]["n_sig"][t_slice] += cp.asnumpy(cp.sum(in_sig, axis=0))
                acc[label]["n_lsb"][t_slice] += cp.asnumpy(cp.sum(in_lsb, axis=0))
                acc[label]["n_rsb"][t_slice] += cp.asnumpy(cp.sum(in_rsb, axis=0))

            del in_win, phases, in_sig, in_lsb, in_rsb
            cp.get_default_memory_pool().free_all_blocks()

    if file_idx % 10 == 0:
        elapsed = time.time() - t0
        print(f"  [file {file_idx:2d} | {acc['ALL']['n_evt']/1e6:.1f}M events | {elapsed:.0f}s]")

elapsed = time.time() - t0
print(f"\n[VAL] Complete: {acc['ALL']['n_evt']:,} events "
      f"(A: {acc['A']['n_evt']:,}, B: {acc['B']['n_evt']:,}) in {elapsed:.1f}s")

# ═══════════════════════════════════════════════════════════
#  COMPUTE Z-SCORES FOR ALL THREE SAMPLES
# ═══════════════════════════════════════════════════════════

def compute_Z(a):
    Z = np.zeros(n_targets)
    for i in range(n_targets):
        total_sb = a["n_lsb"][i] + a["n_rsb"][i]
        B = total_sb * (sig_width / sb_width_total) if sb_width_total > 0 else 0
        S = a["n_sig"][i] - B
        Z[i] = S / np.sqrt(B) if B > 0 else 0
    return Z

Z_all = compute_Z(acc["ALL"])
Z_a   = compute_Z(acc["A"])
Z_b   = compute_Z(acc["B"])

absZ_all = np.abs(Z_all)
absZ_a   = np.abs(Z_a)
absZ_b   = np.abs(Z_b)

# ═══════════════════════════════════════════════════════════
#  TEST 1: RAW MASS SPECTRUM
# ═══════════════════════════════════════════════════════════

print("\n" + "=" * 90)
print("  TEST 1: RAW INVARIANT MASS SPECTRUM")
print("=" * 90)

# Look for bumps in bb̄ region
bb_centers = 0.5 * (hist_bins_bb[:-1] + hist_bins_bb[1:])
bb_counts = acc["ALL"]["hist_bb"]

# Fit smooth background in 7-9 GeV (exclude 7.8-8.2 for signal window)
mask_bg = ((bb_centers >= 6.0) & (bb_centers < 7.5)) | \
          ((bb_centers > 8.5) & (bb_centers < 10.0))
mask_sig = (bb_centers >= 7.5) & (bb_centers <= 8.5)

# Log-polynomial background fit
valid_bg = mask_bg & (bb_counts > 0)
if np.sum(valid_bg) > 5:
    log_counts = np.log(bb_counts[valid_bg].astype(float))
    bg_masses = bb_centers[valid_bg]
    coeffs = np.polyfit(bg_masses, log_counts, 3)
    bg_predicted = np.exp(np.polyval(coeffs, bb_centers))

    # Residuals in signal region
    residual = bb_counts.astype(float) - bg_predicted
    sigma_bg = np.sqrt(bg_predicted)
    pull = residual / sigma_bg

    sig_mask = mask_sig & (bb_counts > 0)
    if np.any(sig_mask):
        max_pull_idx = np.argmax(np.abs(pull[sig_mask]))
        max_pull_mass = bb_centers[sig_mask][max_pull_idx]
        max_pull_val = pull[sig_mask][max_pull_idx]
        print(f"\n  bb̄ region (7.5-8.5 GeV):")
        print(f"    Background model: 3rd-order log-polynomial fit")
        print(f"    Max pull in signal region: {max_pull_val:+.2f}σ at {max_pull_mass:.3f} GeV")
        print(f"    Mean pull: {np.mean(pull[sig_mask]):+.2f}σ")

        # Integrated excess
        total_obs = np.sum(bb_counts[sig_mask])
        total_bg = np.sum(bg_predicted[sig_mask])
        total_excess = total_obs - total_bg
        excess_sigma = total_excess / np.sqrt(total_bg) if total_bg > 0 else 0
        print(f"    Observed: {total_obs:,.0f}")
        print(f"    Background: {total_bg:,.0f}")
        print(f"    Excess: {total_excess:+,.0f} ({excess_sigma:+.2f}σ)")
else:
    print("  [WARNING] Not enough background data for fit")
    bg_predicted = np.ones_like(bb_counts, dtype=float)
    pull = np.zeros_like(bb_counts, dtype=float)

# Same for DY region
dy_centers = 0.5 * (hist_bins_dy[:-1] + hist_bins_dy[1:])
dy_counts = acc["ALL"]["hist_dy"]

mask_dy_bg = ((dy_centers >= 15) & (dy_centers < 21)) | \
             ((dy_centers > 26) & (dy_centers < 35))
mask_dy_sig = (dy_centers >= 21) & (dy_centers <= 26)

valid_dy_bg = mask_dy_bg & (dy_counts > 0)
if np.sum(valid_dy_bg) > 5:
    log_dy = np.log(dy_counts[valid_dy_bg].astype(float))
    bg_dy_m = dy_centers[valid_dy_bg]
    coeffs_dy = np.polyfit(bg_dy_m, log_dy, 3)
    bg_dy_pred = np.exp(np.polyval(coeffs_dy, dy_centers))

    residual_dy = dy_counts.astype(float) - bg_dy_pred
    sigma_dy = np.sqrt(bg_dy_pred)
    pull_dy = residual_dy / sigma_dy

    dy_sig_mask = mask_dy_sig & (dy_counts > 0)
    if np.any(dy_sig_mask):
        max_dy_idx = np.argmax(np.abs(pull_dy[dy_sig_mask]))
        max_dy_mass = dy_centers[dy_sig_mask][max_dy_idx]
        max_dy_val = pull_dy[dy_sig_mask][max_dy_idx]
        print(f"\n  DY desert (21-26 GeV):")
        print(f"    Max pull in signal region: {max_dy_val:+.2f}σ at {max_dy_mass:.3f} GeV")
        print(f"    Mean pull: {np.mean(pull_dy[dy_sig_mask]):+.2f}σ")

        total_dy_obs = np.sum(dy_counts[dy_sig_mask])
        total_dy_bg = np.sum(bg_dy_pred[dy_sig_mask])
        total_dy_excess = total_dy_obs - total_dy_bg
        dy_excess_sigma = total_dy_excess / np.sqrt(total_dy_bg) if total_dy_bg > 0 else 0
        print(f"    Observed: {total_dy_obs:,.0f}")
        print(f"    Background: {total_dy_bg:,.0f}")
        print(f"    Excess: {total_dy_excess:+,.0f} ({dy_excess_sigma:+.2f}σ)")
else:
    bg_dy_pred = np.ones_like(dy_counts, dtype=float)
    pull_dy = np.zeros_like(dy_counts, dtype=float)

# ═══════════════════════════════════════════════════════════
#  TEST 2: SPLIT-SAMPLE CROSS-VALIDATION
# ═══════════════════════════════════════════════════════════

print("\n\n" + "=" * 90)
print("  TEST 2: SPLIT-SAMPLE CROSS-VALIDATION")
print("=" * 90)

print(f"\n  Sample A: {acc['A']['n_evt']:,} events (odd files)")
print(f"  Sample B: {acc['B']['n_evt']:,} events (even files)")

# Check candidate peaks in both halves
print(f"\n  bb̄ region (7.5 – 8.5 GeV):")
print(f"  {'M [GeV]':>10s} {'Z_ALL':>8s} {'Z_A':>8s} {'Z_B':>8s} {'Consistent?':>15s}")
print("  " + "-" * 55)

# Find peaks in the full sample bb̄ region
bb_slice = slice(0, n_bbbar)
pks_bb, _ = find_peaks(absZ_all[bb_slice], height=5.0, distance=10, prominence=2.0)

for p in sorted(pks_bb, key=lambda x: -absZ_all[x]):
    m = sweep[p]
    za = Z_all[p]
    z1 = Z_a[p]
    z2 = Z_b[p]
    # Consistent = same sign AND both >2σ individually (since each has ~half stats, expect ~Z/√2)
    same_sign = (z1 * z2 > 0)
    both_above_2 = (abs(z1) > 2) and (abs(z2) > 2)
    if same_sign and both_above_2:
        verdict = "✅ CONSISTENT"
    elif same_sign:
        verdict = "⚠️ WEAK"
    else:
        verdict = "❌ INCONSISTENT"

    print(f"  {m:>10.4f} {za:>+8.2f} {z1:>+8.2f} {z2:>+8.2f} {verdict:>15s}")

print(f"\n  DY desert (20 – 27 GeV):")
print(f"  {'M [GeV]':>10s} {'Z_ALL':>8s} {'Z_A':>8s} {'Z_B':>8s} {'Consistent?':>15s}")
print("  " + "-" * 55)

dy_slice = slice(n_bbbar, n_bbbar + n_dy)
pks_dy, _ = find_peaks(absZ_all[dy_slice], height=5.0, distance=10, prominence=2.0)

for p in sorted(pks_dy, key=lambda x: -absZ_all[n_bbbar + x]):
    idx = n_bbbar + p
    m = sweep[idx]
    za = Z_all[idx]
    z1 = Z_a[idx]
    z2 = Z_b[idx]
    same_sign = (z1 * z2 > 0)
    both_above_2 = (abs(z1) > 2) and (abs(z2) > 2)
    if same_sign and both_above_2:
        verdict = "✅ CONSISTENT"
    elif same_sign:
        verdict = "⚠️ WEAK"
    else:
        verdict = "❌ INCONSISTENT"

    print(f"  {m:>10.4f} {za:>+8.2f} {z1:>+8.2f} {z2:>+8.2f} {verdict:>15s}")

# ═══════════════════════════════════════════════════════════
#  TEST 3: LOOK-ELSEWHERE EFFECT (LEE)
# ═══════════════════════════════════════════════════════════

print("\n\n" + "=" * 90)
print("  TEST 3: LOOK-ELSEWHERE EFFECT CORRECTION")
print("=" * 90)

# Method: Estimate effective number of independent trials
# Using the full-spectrum scan (2131 targets over 0.2-200 GeV)
N_total = 2131

# The signals are correlated because mass windows overlap.
# Effective trials = total mass range / typical decorrelation length
# For bb̄ region: decorrelation ~ 100 MeV (typical resonance width), range 7.5-8.5 = 10 trials
# For DY region: decorrelation ~ 500 MeV, range 20-27 = 14 trials
# Total effective: ~24 trials in candidate regions
# But globally: 0.2-200 GeV with varying resolution → ~200-500 effective trials

# Conservative: use Bonferroni with full N_total
# Also compute Sidak correction (less conservative)

print(f"\n  Total mass hypotheses tested: {N_total}")
print()

candidates_for_lee = [
    ("7.906 GeV (bb̄)", 8.13, "bb̄ threshold"),
    ("8.104 GeV (bb̄)", 6.29, "bb̄ threshold"),
    ("7.842 GeV (bb̄)", 6.15, "bb̄ threshold"),
    ("23.31 GeV (DY)",  7.43, "DY desert"),
    ("23.55 GeV (DY)",  6.42, "DY desert"),
]

print(f"  {'Candidate':>20s} {'Z_local':>8s} {'p_local':>12s} "
      f"{'p_global':>12s} {'Z_global':>10s} {'Survives?':>12s}")
print("  " + "-" * 80)

for name, z_local, region in candidates_for_lee:
    p_local = 2 * stats.norm.sf(abs(z_local))  # two-sided

    # Bonferroni (most conservative)
    p_global_bonf = min(1.0, N_total * p_local)

    # Šidák (less conservative, exact)
    p_global_sidak = 1 - (1 - p_local) ** N_total

    # Convert back to Z
    if p_global_bonf < 1:
        z_global = stats.norm.isf(p_global_bonf / 2)
    else:
        z_global = 0.0

    survives = "✅ YES (>3σ)" if z_global > 3 else \
               "⚠️ MARGINAL" if z_global > 2 else "❌ NO"

    print(f"  {name:>20s} {z_local:>8.2f} {p_local:>12.2e} "
          f"{p_global_bonf:>12.2e} {z_global:>10.2f} {survives:>12s}")

# Effective trials estimate (Gross-Vitells approximation)
print(f"\n  ── Gross-Vitells effective trials estimate ──")

# Count upcrossings of threshold in the full scan Z-score profile
for threshold in [2.0, 3.0]:
    # Count upcrossings in bb̄ region
    z_bb = Z_all[:n_bbbar]
    upcross_bb = np.sum((z_bb[:-1] < threshold) & (z_bb[1:] >= threshold))
    upcross_bb += np.sum((z_bb[:-1] > -threshold) & (z_bb[1:] <= -threshold))

    z_dy = Z_all[n_bbbar:]
    upcross_dy = np.sum((z_dy[:-1] < threshold) & (z_dy[1:] >= threshold))
    upcross_dy += np.sum((z_dy[:-1] > -threshold) & (z_dy[1:] <= -threshold))

    print(f"    Upcrossings at ±{threshold}σ: bb̄ region = {upcross_bb}, DY region = {upcross_dy}")

# Effective trials via Euler characteristic
# N_eff ≈ <N_upcrossings(u0)> for threshold u0
# For 2σ upcrossings: N_eff_bb ≈ upcrossings_bb, N_eff_dy ≈ upcrossings_dy

# ═══════════════════════════════════════════════════════════
#  COMPREHENSIVE VISUALIZATION
# ═══════════════════════════════════════════════════════════

print("\n[viz] Generating validation plots...")

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

fig = plt.figure(figsize=(26, 30))
gs = fig.add_gridspec(4, 2, hspace=0.35, wspace=0.25)

fig.suptitle(
    "ACS NEW CANDIDATE VALIDATION\n"
    f"45.3M CMS events | Split-sample + Mass spectrum + LEE correction",
    fontsize=16, fontweight="bold", color="white", y=0.995)

# ── Panel 1: Raw mass spectrum bb̄ region ──
ax1 = fig.add_subplot(gs[0, 0])
ax1.semilogy(bb_centers, bb_counts, color="#00ccff", linewidth=0.8, alpha=0.8)
ax1.semilogy(bb_centers, bg_predicted, color="#ff6b6b", linewidth=1.5,
             linestyle="--", label="Background fit", alpha=0.8)
ax1.axvspan(7.5, 8.5, alpha=0.08, color="yellow", label="Signal region")
ax1.axvline(7.906, color="#ffd93d", linewidth=1, alpha=0.6, linestyle=":")
ax1.axvline(8.104, color="#ffd93d", linewidth=1, alpha=0.6, linestyle=":")
ax1.set_title("Raw Mass Spectrum: 5 – 12 GeV", fontsize=12, fontweight="bold")
ax1.set_xlabel("M(μ⁺μ⁻) [GeV]")
ax1.set_ylabel("Events / 10 MeV")
ax1.legend(fontsize=9)
ax1.grid(alpha=0.15)

# ── Panel 2: Pull distribution bb̄ ──
ax2 = fig.add_subplot(gs[0, 1])
sig_region = (bb_centers >= 7.0) & (bb_centers <= 9.0) & (bb_counts > 0)
colors = ["#ff6b6b" if abs(p) > 2 else "#00ccff" for p in pull[sig_region]]
ax2.bar(bb_centers[sig_region], pull[sig_region], width=0.01,
        color=colors, alpha=0.7)
ax2.axhline(2, color="lime", linestyle="--", alpha=0.3)
ax2.axhline(-2, color="lime", linestyle="--", alpha=0.3)
ax2.axhline(0, color="white", linewidth=0.3, alpha=0.3)
ax2.axvspan(7.5, 8.5, alpha=0.08, color="yellow")
ax2.set_title("Pull = (Data - Fit) / √Fit: 7 – 9 GeV", fontsize=12, fontweight="bold")
ax2.set_xlabel("M(μ⁺μ⁻) [GeV]")
ax2.set_ylabel("Pull [σ]")
ax2.grid(alpha=0.15)

# ── Panel 3: Raw mass spectrum DY region ──
ax3 = fig.add_subplot(gs[1, 0])
ax3.semilogy(dy_centers, dy_counts, color="#00ccff", linewidth=0.8, alpha=0.8)
valid_dy = dy_counts > 0
if np.sum(valid_dy_bg) > 5:
    ax3.semilogy(dy_centers, bg_dy_pred, color="#ff6b6b", linewidth=1.5,
                 linestyle="--", label="Background fit", alpha=0.8)
ax3.axvspan(21, 26, alpha=0.08, color="yellow", label="Signal region")
ax3.axvline(23.31, color="#ffd93d", linewidth=1, alpha=0.6, linestyle=":")
ax3.set_title("Raw Mass Spectrum: 15 – 35 GeV", fontsize=12, fontweight="bold")
ax3.set_xlabel("M(μ⁺μ⁻) [GeV]")
ax3.set_ylabel("Events / 50 MeV")
ax3.legend(fontsize=9)
ax3.grid(alpha=0.15)

# ── Panel 4: Pull distribution DY ──
ax4 = fig.add_subplot(gs[1, 1])
dy_sig_reg = (dy_centers >= 18) & (dy_centers <= 30) & (dy_counts > 0)
colors_dy = ["#ff6b6b" if abs(p) > 2 else "#00ccff" for p in pull_dy[dy_sig_reg]]
ax4.bar(dy_centers[dy_sig_reg], pull_dy[dy_sig_reg], width=0.05,
        color=colors_dy, alpha=0.7)
ax4.axhline(2, color="lime", linestyle="--", alpha=0.3)
ax4.axhline(-2, color="lime", linestyle="--", alpha=0.3)
ax4.axhline(0, color="white", linewidth=0.3, alpha=0.3)
ax4.axvspan(21, 26, alpha=0.08, color="yellow")
ax4.set_title("Pull = (Data - Fit) / √Fit: 18 – 30 GeV", fontsize=12, fontweight="bold")
ax4.set_xlabel("M(μ⁺μ⁻) [GeV]")
ax4.set_ylabel("Pull [σ]")
ax4.grid(alpha=0.15)

# ── Panel 5: Split-sample bb̄ ──
ax5 = fig.add_subplot(gs[2, 0])
m_bb = sweep[:n_bbbar]
ax5.plot(m_bb, Z_all[:n_bbbar], color="white", linewidth=1.5, alpha=0.9, label="ALL")
ax5.plot(m_bb, Z_a[:n_bbbar], color="#00ff88", linewidth=1, alpha=0.7, label="Sample A (odd files)")
ax5.plot(m_bb, Z_b[:n_bbbar], color="#ff88ff", linewidth=1, alpha=0.7, label="Sample B (even files)")
ax5.axhline(5, color="lime", linestyle="--", alpha=0.2)
ax5.axhline(-5, color="lime", linestyle="--", alpha=0.2)
ax5.axhline(0, color="white", linewidth=0.3, alpha=0.3)
ax5.set_title("Split-Sample: bb̄ Threshold", fontsize=12, fontweight="bold")
ax5.set_xlabel("M [GeV]")
ax5.set_ylabel("Z [σ] (signed)")
ax5.legend(fontsize=9)
ax5.grid(alpha=0.15)

# ── Panel 6: Split-sample DY ──
ax6 = fig.add_subplot(gs[2, 1])
m_dy = sweep[n_bbbar:]
ax6.plot(m_dy, Z_all[n_bbbar:], color="white", linewidth=1.5, alpha=0.9, label="ALL")
ax6.plot(m_dy, Z_a[n_bbbar:], color="#00ff88", linewidth=1, alpha=0.7, label="Sample A (odd files)")
ax6.plot(m_dy, Z_b[n_bbbar:], color="#ff88ff", linewidth=1, alpha=0.7, label="Sample B (even files)")
ax6.axhline(5, color="lime", linestyle="--", alpha=0.2)
ax6.axhline(-5, color="lime", linestyle="--", alpha=0.2)
ax6.axhline(0, color="white", linewidth=0.3, alpha=0.3)
ax6.set_title("Split-Sample: DY Desert", fontsize=12, fontweight="bold")
ax6.set_xlabel("M [GeV]")
ax6.set_ylabel("Z [σ] (signed)")
ax6.legend(fontsize=9)
ax6.grid(alpha=0.15)

# ── Panel 7: Correlation plot A vs B ──
ax7 = fig.add_subplot(gs[3, 0])
ax7.scatter(Z_a[:n_bbbar], Z_b[:n_bbbar], s=3, alpha=0.4, color="#00ccff", label="bb̄ region")
ax7.scatter(Z_a[n_bbbar:], Z_b[n_bbbar:], s=3, alpha=0.4, color="#ff6b6b", label="DY region")
lims = [-12, 12]
ax7.plot(lims, lims, "--", color="lime", alpha=0.3)
ax7.set_xlim(lims)
ax7.set_ylim(lims)
ax7.set_xlabel("Z (Sample A)")
ax7.set_ylabel("Z (Sample B)")
ax7.set_title("Split-Sample Correlation", fontsize=12, fontweight="bold")
ax7.legend(fontsize=9)
ax7.grid(alpha=0.15)
ax7.set_aspect("equal")

# Compute Pearson correlation
r_bb = np.corrcoef(Z_a[:n_bbbar], Z_b[:n_bbbar])[0, 1]
r_dy = np.corrcoef(Z_a[n_bbbar:], Z_b[n_bbbar:])[0, 1]
ax7.text(0.05, 0.95, f"r(bb̄) = {r_bb:.3f}\nr(DY) = {r_dy:.3f}",
         transform=ax7.transAxes, fontsize=10, color="white",
         verticalalignment="top",
         bbox=dict(boxstyle="round", facecolor="#1a1a2e", edgecolor="#555577"))

# ── Panel 8: LEE summary ──
ax8 = fig.add_subplot(gs[3, 1])
ax8.axis("off")
lee_text = "LOOK-ELSEWHERE EFFECT (LEE)\n"
lee_text += "=" * 45 + "\n\n"
lee_text += f"Total hypotheses tested: {N_total}\n\n"
lee_text += f"{'Candidate':<22s} {'Z_local':>7s} {'Z_global':>8s} {'Status':>10s}\n"
lee_text += "-" * 50 + "\n"

for name, z_local, region in candidates_for_lee:
    p_local = 2 * stats.norm.sf(abs(z_local))
    p_global = min(1.0, N_total * p_local)
    z_global = stats.norm.isf(p_global / 2) if p_global < 1 else 0
    status = "✅ >3σ" if z_global > 3 else "⚠️ ~3σ" if z_global > 2.5 else "❌ <3σ"
    short = name.split("(")[0].strip()
    lee_text += f"{short:<22s} {z_local:>7.2f} {z_global:>8.2f} {status:>10s}\n"

lee_text += "\n" + "-" * 50 + "\n"
lee_text += "Method: Bonferroni (most conservative)\n"
lee_text += "p_global = N_trials × p_local\n"

ax8.text(0.05, 0.95, lee_text, transform=ax8.transAxes,
         fontsize=11, color="#ccccee", verticalalignment="top",
         fontfamily="monospace",
         bbox=dict(boxstyle="round", facecolor="#1a1a2e", edgecolor="#555577"))

plt.savefig(os.path.join(cfg.OUTPUT_DIR, "acs_candidate_validation.png"),
            dpi=200, bbox_inches="tight", facecolor="#0a0a0f")
plt.close()
print(f"[viz] Saved: output/acs_candidate_validation.png")

# ═══════════════════════════════════════════════════════════
#  FINAL VERDICT
# ═══════════════════════════════════════════════════════════

print("\n\n" + "=" * 90)
print("  FINAL VERDICT")
print("=" * 90)

for name, z_local, region in candidates_for_lee:
    p_local = 2 * stats.norm.sf(abs(z_local))
    p_global = min(1.0, N_total * p_local)
    z_global = stats.norm.isf(p_global / 2) if p_global < 1 else 0

    print(f"\n  {name}:")
    print(f"    Local significance:   {z_local:.2f}σ")
    print(f"    Global significance:  {z_global:.2f}σ (Bonferroni, N={N_total})")

    # Check split-sample
    if "bb̄" in name:
        mass_target = float(name.split()[0])
        idx = np.argmin(np.abs(sweep[:n_bbbar] - mass_target))
    else:
        mass_target = float(name.split()[0])
        idx = n_bbbar + np.argmin(np.abs(sweep[n_bbbar:] - mass_target))

    za = Z_a[idx]
    zb = Z_b[idx]
    consistent = (za * zb > 0) and (abs(za) > 2) and (abs(zb) > 2)
    print(f"    Split-sample:         A={za:+.2f}σ, B={zb:+.2f}σ → "
          f"{'CONSISTENT' if consistent else 'INCONSISTENT'}")

    # Overall
    if z_global > 3 and consistent:
        print(f"    ═══ SURVIVES ALL TESTS ═══")
    elif z_global > 3:
        print(f"    ⚠️ Survives LEE but fails split-sample")
    elif consistent:
        print(f"    ⚠️ Split-sample consistent but fails LEE")
    else:
        print(f"    ❌ DOES NOT SURVIVE VALIDATION")

print("\n[done]")

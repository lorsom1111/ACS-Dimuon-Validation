"""
ACS FULL-SPECTRUM BLIND SCAN
==============================
Complete mass sweep from 0.2 to 200 GeV with fine resolution.
Finds EVERY resonance accessible in the dimuon channel.
GPU-batched for RTX 5090 VRAM management.

Goal: Prove ACS universality by blind-detecting ALL known particles.
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
    print("[FULL] GPU MODE — CuPy on RTX 5090")
else:
    xp = np
    print("[FULL] CPU MODE")

cfg.ACTIVE_SOURCE = "run2_nanoaod_13tev"

ACS_ATTRACTOR = float(cfg.ACS_ATTRACTOR)
SIG_HALF = float(cfg.PHASE_SIGNAL_HALFWIDTH)
SB_WIDTH = float(cfg.PHASE_SIDEBAND_WIDTH)

sig_lo = ACS_ATTRACTOR - SIG_HALF
sig_hi = ACS_ATTRACTOR + SIG_HALF
sb_left_lo = sig_lo - SB_WIDTH
sb_right_hi = sig_hi + SB_WIDTH

# ═══════════════════════════════════════════════════════════
#  FULL MASS GRID — 0.2 to 200 GeV
# ═══════════════════════════════════════════════════════════

sweep = np.concatenate([
    np.arange(0.20,  1.20, 0.005),  # 5 MeV — light mesons (ρ,ω,η,φ,f₀)
    np.arange(1.20,  4.00, 0.010),  # 10 MeV — charmonium region
    np.arange(4.00, 12.00, 0.010),  # 10 MeV — bottomonium region
    np.arange(12.0,  50.0, 0.100),  # 100 MeV — mid-range
    np.arange(50.0, 130.0, 0.200),  # 200 MeV — Z/Higgs region
    np.arange(130.0, 200.5, 1.000), # 1 GeV — high mass
])
sweep = np.unique(np.round(sweep, 4))
n_targets = len(sweep)

print(f"\n[FULL] FULL-SPECTRUM BLIND SCAN")
print(f"[FULL] {n_targets} mass hypotheses: {sweep[0]:.3f} – {sweep[-1]:.3f} GeV")

# ─── Complete PDG reference for dimuon channel ───
PDG_PARTICLES = {
    # Light mesons
    "η(548)":       0.54786,
    "ρ(770)":       0.77526,
    "ω(782)":       0.78265,
    "η'(958)":      0.95778,
    "f₀(980)":      0.990,
    "a₀(980)":      0.980,
    "φ(1020)":      1.01946,
    "h₁(1170)":     1.166,
    "f₂(1270)":     1.2755,
    "f₁(1285)":     1.2819,
    "a₂(1320)":     1.3183,
    "f₀(1370)":     1.370,
    "f₁(1420)":     1.4264,
    "ω(1420)":      1.410,
    "f₀(1500)":     1.506,
    "f₂'(1525)":    1.525,
    "ρ(1450)":      1.465,
    "ρ₃(1690)":     1.6888,
    "φ(1680)":      1.680,
    "ω(1650)":      1.670,
    # Charmonium
    "ηc(1S)":       2.9839,
    "J/ψ":          3.09690,
    "χc0(1P)":      3.41471,
    "χc1(1P)":      3.51067,
    "hc(1P)":       3.52538,
    "χc2(1P)":      3.55617,
    "ηc(2S)":       3.6392,
    "ψ(2S)":        3.68610,
    "ψ(3770)":      3.7737,
    "ψ(4040)":      4.039,
    "ψ(4160)":      4.191,
    "ψ(4415)":      4.421,
    # Bottomonium
    "Υ(1S)":        9.4603,
    "χb0(1P)":      9.8594,
    "χb1(1P)":      9.8928,
    "χb2(1P)":      9.9122,
    "Υ(2S)":       10.0233,
    "χb0(2P)":     10.2325,
    "χb1(2P)":     10.2555,
    "χb2(2P)":     10.2686,
    "Υ(3S)":       10.3552,
    "Υ(4S)":       10.5794,
    "Υ(10860)":    10.8852,
    "Υ(11020)":    11.000,
    # Electroweak
    "Z":           91.1876,
    "H":          125.10,
}

# Mass windows
def get_window(m):
    if m < 2:
        return (m * 0.70, m * 1.30)
    elif m < 12:
        return (m * 0.80, m * 1.20)
    elif m < 50:
        return (m * 0.85, m * 1.15)
    else:
        return (m - 15, m + 15)

windows_lo = np.array([get_window(m)[0] for m in sweep])
windows_hi = np.array([get_window(m)[1] for m in sweep])

# Accumulators
accum_n_win = np.zeros(n_targets, dtype=np.int64)
accum_n_sig = np.zeros(n_targets, dtype=np.int64)
accum_n_lsb = np.zeros(n_targets, dtype=np.int64)
accum_n_rsb = np.zeros(n_targets, dtype=np.int64)

if _GPU_AVAILABLE:
    g_targets = cp.asarray(sweep)
    g_wlo = cp.asarray(windows_lo)
    g_whi = cp.asarray(windows_hi)

# ═══════════════════════════════════════════════════════════
#  SINGLE-PASS SCAN WITH GPU BATCHING
# ═══════════════════════════════════════════════════════════

BATCH_T = 80  # targets per GPU batch
n_batches = (n_targets + BATCH_T - 1) // BATCH_T
print(f"[FULL] GPU batching: {n_batches} batches × {BATCH_T} targets")
print(f"[FULL] Starting scan over 57 files...\n")

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

            del in_win, phases, in_sig, in_lsb, in_rsb
            cp.get_default_memory_pool().free_all_blocks()
    else:
        for t_start in range(0, n_targets, BATCH_T):
            t_end = min(t_start + BATCH_T, n_targets)
            t_slice = slice(t_start, t_end)

            m_col = masses[:, None]
            mt_row = sweep[None, t_slice]
            wlo_row = windows_lo[None, t_slice]
            whi_row = windows_hi[None, t_slice]

            in_win = (m_col >= wlo_row) & (m_col <= whi_row)
            phases = np.arctan(m_col / mt_row)

            in_sig = in_win & (phases >= sig_lo) & (phases <= sig_hi)
            in_lsb = in_win & (phases >= sb_left_lo) & (phases < sig_lo)
            in_rsb = in_win & (phases > sig_hi) & (phases <= sb_right_hi)

            accum_n_win[t_slice] += np.sum(in_win, axis=0)
            accum_n_sig[t_slice] += np.sum(in_sig, axis=0)
            accum_n_lsb[t_slice] += np.sum(in_lsb, axis=0)
            accum_n_rsb[t_slice] += np.sum(in_rsb, axis=0)

    if chunk_idx % 5 == 0:
        elapsed = time.time() - t0
        rate = total_events / elapsed if elapsed > 0 else 0
        print(f"  [{chunk_idx:2d} chunks | {total_events/1e6:5.1f}M events | "
              f"{elapsed:.0f}s | {rate/1e6:.2f}M evt/s]")

elapsed = time.time() - t0
total_evals = n_targets * total_events
print(f"\n[FULL] ═══ SCAN COMPLETE ═══")
print(f"[FULL] {total_events:,} events × {n_targets} targets = "
      f"{total_evals/1e9:.1f}B evaluations in {elapsed:.1f}s")
print(f"[FULL] Throughput: {total_evals/elapsed/1e9:.2f}B eval/s")

# ═══════════════════════════════════════════════════════════
#  COMPUTE Z-SCORES
# ═══════════════════════════════════════════════════════════

sig_width = sig_hi - sig_lo
sb_width_total = 2.0 * SB_WIDTH

Z_scores = np.zeros(n_targets)
for i in range(n_targets):
    total_sb = accum_n_lsb[i] + accum_n_rsb[i]
    B = total_sb * (sig_width / sb_width_total) if sb_width_total > 0 else 0
    S = accum_n_sig[i] - B
    Z_scores[i] = S / np.sqrt(B) if B > 0 else 0

absZ = np.abs(Z_scores)

# ═══════════════════════════════════════════════════════════
#  PEAK DETECTION
# ═══════════════════════════════════════════════════════════

from scipy.signal import find_peaks

print("\n" + "=" * 110)
print("  ACS FULL-SPECTRUM BLIND DETECTIONS")
print("=" * 110)

# Different peak-finding for different mass regions
all_peaks = set()

# Fine region: < 5 GeV — min distance = 10 bins (50 MeV)
mask_lo = sweep < 5.0
idx_lo = np.where(mask_lo)[0]
if len(idx_lo) > 0:
    pks, _ = find_peaks(absZ[mask_lo], height=5.0, distance=10, prominence=2.0)
    all_peaks.update(idx_lo[pks])

# Mid region: 5 - 12 GeV — min distance = 20 bins (200 MeV)
mask_mid = (sweep >= 5.0) & (sweep < 12.0)
idx_mid = np.where(mask_mid)[0]
if len(idx_mid) > 0:
    pks, _ = find_peaks(absZ[mask_mid], height=5.0, distance=20, prominence=2.0)
    all_peaks.update(idx_mid[pks])

# High region: > 12 GeV — min distance = 10 bins (1-2 GeV)
mask_hi = sweep >= 12.0
idx_hi = np.where(mask_hi)[0]
if len(idx_hi) > 0:
    pks, _ = find_peaks(absZ[mask_hi], height=5.0, distance=10, prominence=2.0)
    all_peaks.update(idx_hi[pks])

# Sort peaks by |Z|
peaks_sorted = sorted(all_peaks, key=lambda x: -absZ[x])

print(f"\n  {'#':>3s} {'M_ACS [GeV]':>12s} {'|Z| [σ]':>10s} {'N_window':>10s} "
      f"{'PDG Match':>15s} {'M_PDG [GeV]':>12s} {'ΔM [MeV]':>10s} {'Status':>10s}")
print("-" * 110)

detected_particles = []
for rank, p in enumerate(peaks_sorted, 1):
    m = sweep[p]
    z = absZ[p]
    nw = accum_n_win[p]

    # Find nearest PDG particle
    nearest_name = "???"
    nearest_mass = 0
    min_dist = 999
    for pname, pmass in PDG_PARTICLES.items():
        d = abs(m - pmass) * 1000  # MeV
        if d < min_dist:
            min_dist = d
            nearest_name = pname
            nearest_mass = pmass

    # Check if within reasonable matching distance
    rel_err = abs(m - nearest_mass) / nearest_mass * 100
    if rel_err < 5:
        status = "✅ MATCH"
    elif rel_err < 10:
        status = "⚠️ CLOSE"
    elif rel_err < 20:
        status = "❓ FAR"
    else:
        status = "🆕 NEW?"

    print(f"  {rank:>3d} {m:>12.4f} {z:>10.1f} {nw:>10,} "
          f"{nearest_name:>15s} {nearest_mass:>12.4f} {min_dist:>10.0f} {status:>10s}")

    detected_particles.append({
        "rank": rank, "m_acs": m, "absZ": z, "n_win": nw,
        "pdg_name": nearest_name, "pdg_mass": nearest_mass,
        "delta_mev": min_dist, "rel_err": rel_err, "status": status,
    })

# ─── Summary ───
n_total_peaks = len(detected_particles)
n_matched = sum(1 for d in detected_particles if "MATCH" in d["status"])
n_close = sum(1 for d in detected_particles if "CLOSE" in d["status"])
n_new = sum(1 for d in detected_particles if "NEW" in d["status"])

print(f"\n  ═══════════════════════════════════════════════")
print(f"  TOTAL DETECTIONS:       {n_total_peaks}")
print(f"  PDG MATCHED (<5%):      {n_matched}")
print(f"  CLOSE MATCH (<10%):     {n_close}")
print(f"  POTENTIAL NEW:          {n_new}")
print(f"  ═══════════════════════════════════════════════")

# ─── Check coverage: which PDG particles did we detect? ───
print("\n\n── PDG COVERAGE CHECK ──")
print(f"  {'PDG Particle':>18s} {'M [GeV]':>10s} {'Detected?':>12s} {'ACS |Z|':>10s}")
print("-" * 60)

for pname, pmass in sorted(PDG_PARTICLES.items(), key=lambda x: x[1]):
    # Find sweep point closest to this PDG mass
    idx = np.argmin(np.abs(sweep - pmass))
    z_at_pdg = absZ[idx]

    # Check if any peak was found near this mass
    detected = any(abs(d["pdg_mass"] - pmass) < 0.001 and "MATCH" in d["status"]
                   for d in detected_particles)
    close = any(abs(d["m_acs"] - pmass) / pmass < 0.05 and d["absZ"] > 5.0
                for d in detected_particles)

    if detected or close:
        marker = f"✅ YES ({z_at_pdg:.1f}σ)"
    elif z_at_pdg > 5:
        marker = f"⚠️ PEAK ({z_at_pdg:.1f}σ)"
    elif z_at_pdg > 3:
        marker = f"~ MARGINAL ({z_at_pdg:.1f}σ)"
    else:
        marker = f"✗ NO ({z_at_pdg:.1f}σ)"

    print(f"  {pname:>18s} {pmass:>10.4f} {marker:>30s}")

# ═══════════════════════════════════════════════════════════
#  VISUALIZATION — 4-panel full spectrum
# ═══════════════════════════════════════════════════════════

print("\n[viz] Generating full-spectrum plot...")

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

fig, axes = plt.subplots(4, 1, figsize=(24, 24),
    gridspec_kw={"height_ratios": [2, 2, 2, 2]})

fig.suptitle(
    f"ACS FULL-SPECTRUM BLIND SCAN\n"
    f"{n_targets:,} mass hypotheses × {total_events:,} events = "
    f"{total_evals/1e9:.1f}B evaluations in {elapsed:.0f}s on RTX 5090",
    fontsize=16, fontweight="bold", color="white", y=0.995)

regions = [
    (axes[0], 0.2,  1.3,  "Light Mesons (0.2 – 1.3 GeV)"),
    (axes[1], 2.5,  4.5,  "Charmonium (2.5 – 4.5 GeV)"),
    (axes[2], 8.5, 11.5,  "Bottomonium (8.5 – 11.5 GeV)"),
    (axes[3], 50,  140,   "Electroweak (50 – 140 GeV)"),
]

for ax, mlo, mhi, title in regions:
    mask = (sweep >= mlo) & (sweep <= mhi)
    ax.fill_between(sweep[mask], absZ[mask], alpha=0.3, color="#00ccff")
    ax.plot(sweep[mask], absZ[mask], color="#00ccff", linewidth=1.2, alpha=0.9)

    # 5σ line
    ax.axhline(5, color="lime", linestyle="--", alpha=0.3, linewidth=1)

    # Mark PDG particles in this range
    for pname, pmass in PDG_PARTICLES.items():
        if mlo <= pmass <= mhi:
            idx = np.argmin(np.abs(sweep - pmass))
            z_here = absZ[idx]
            ax.axvline(pmass, color="#ffd93d", linewidth=1, alpha=0.3, linestyle="--")
            # Only label if significant or notable
            if z_here > 3 or pmass in [3.097, 9.460, 91.188, 125.1]:
                ax.annotate(
                    f"{pname}\n{z_here:.0f}σ",
                    (pmass, min(z_here, ax.get_ylim()[1] * 0.9 if ax.get_ylim()[1] > 0 else z_here)),
                    textcoords="offset points", xytext=(8, 5),
                    fontsize=7, color="#ffd93d",
                    bbox=dict(boxstyle="round,pad=0.15", facecolor="#1a1a2e",
                             edgecolor="#ffd93d", alpha=0.7))

    # Mark detected peaks
    for d in detected_particles:
        if mlo <= d["m_acs"] <= mhi:
            ax.plot(d["m_acs"], d["absZ"], "v", color="#ff6b6b",
                    markersize=8, zorder=10)

    ax.set_ylabel("|Z| [σ]", fontsize=11)
    ax.set_title(title, fontsize=13, fontweight="bold")
    ax.set_xlim(mlo, mhi)
    ax.grid(alpha=0.15)

axes[3].set_xlabel("M [GeV]", fontsize=12)

plt.tight_layout(rect=[0, 0, 1, 0.96])
outpath = os.path.join(cfg.OUTPUT_DIR, "acs_full_spectrum.png")
fig.savefig(outpath, dpi=200, bbox_inches="tight", facecolor="#0a0a0f")
plt.close()
print(f"[viz] Saved: {outpath}")

# ─── Save raw data ───
np.savez(os.path.join(cfg.OUTPUT_DIR, "full_spectrum_data.npz"),
         masses=sweep, absZ=absZ, Z=Z_scores,
         n_window=accum_n_win, n_signal=accum_n_sig)
print(f"[data] Saved: output/full_spectrum_data.npz")

print("\n" + "=" * 70)
print("  FULL-SPECTRUM SCAN COMPLETE")
print("=" * 70)

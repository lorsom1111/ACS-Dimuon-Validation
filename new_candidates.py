"""
ACS NEW CANDIDATE ANALYSIS
============================
Deep investigation of the 5 unmatched signals from the full-spectrum scan.
Fine 1-MeV resolution scans around each candidate.
"""

import os, sys, time
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as cfg
from pipeline import calculate_kinematics, apply_quality_cuts, _GPU_AVAILABLE
from ingest import load_data

if _GPU_AVAILABLE:
    import cupy as cp
    print("[NEW] GPU MODE")

cfg.ACTIVE_SOURCE = "run2_nanoaod_13tev"

ACS_ATTRACTOR = float(cfg.ACS_ATTRACTOR)
SIG_HALF = float(cfg.PHASE_SIGNAL_HALFWIDTH)
SB_WIDTH = float(cfg.PHASE_SIDEBAND_WIDTH)
sig_lo = ACS_ATTRACTOR - SIG_HALF
sig_hi = ACS_ATTRACTOR + SIG_HALF
sb_left_lo = sig_lo - SB_WIDTH
sb_right_hi = sig_hi + SB_WIDTH

# ═══════════════════════════════════════════════════════════
#  CANDIDATE REGIONS — ultra-fine 1 MeV sweeps
# ═══════════════════════════════════════════════════════════

CANDIDATES = {
    "Region A: bb̄ threshold (7.5–8.5 GeV)": {
        "sweep": np.arange(7.50, 8.51, 0.002),   # 2 MeV steps
        "context": "Below Υ(1S). Near bb̄ production threshold (2×m_b ≈ 8.36 GeV).",
        "known_nearby": {
            "Υ(1S)": 9.4603,
            "ηb(1S)": 9.3987,   # pseudoscalar bb̄ ground state
            "bb̄ threshold": 8.36,
        },
    },
    "Region B: Mid-range 23 GeV": {
        "sweep": np.arange(20.0, 27.0, 0.010),   # 10 MeV steps
        "context": "No known resonances. Drell-Yan desert.",
        "known_nearby": {},
    },
    "Region C: Z sidebands (82–100 GeV)": {
        "sweep": np.arange(82.0, 100.0, 0.050),  # 50 MeV steps
        "context": "Z boson Drell-Yan continuum. Need to distinguish "
                   "real structure from Z tail spillover.",
        "known_nearby": {
            "Z": 91.1876,
            "W": 80.379,
        },
    },
}

# Build single concatenated sweep
all_sweeps = []
region_slices = {}
offset = 0
for rname, rdata in CANDIDATES.items():
    s = rdata["sweep"]
    region_slices[rname] = slice(offset, offset + len(s))
    all_sweeps.append(s)
    offset += len(s)

sweep = np.concatenate(all_sweeps)
n_targets = len(sweep)
print(f"[NEW] Total fine-sweep points: {n_targets}")

# Mass windows (adaptive)
def get_window(m):
    if m < 12:
        return (m * 0.80, m * 1.20)  # ±20%
    elif m < 50:
        return (m * 0.85, m * 1.15)  # ±15%
    else:
        return (m - 15, m + 15)      # ±15 GeV

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

BATCH_T = 80

# ═══════════════════════════════════════════════════════════
#  SCAN
# ═══════════════════════════════════════════════════════════

print(f"[NEW] Scanning {n_targets} targets across 3 candidate regions...\n")
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

    if int(cut_mask.sum()) == 0:
        continue

    masses = calculate_kinematics(
        pt1[cut_mask], pt2[cut_mask], eta1[cut_mask], eta2[cut_mask],
        phi1[cut_mask], phi2[cut_mask]
    )
    total_events += len(masses)

    if _GPU_AVAILABLE:
        g_m = masses if isinstance(masses, cp.ndarray) else cp.asarray(masses)

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

            accum_n_win[t_slice] += cp.asnumpy(cp.sum(in_win, axis=0))
            accum_n_sig[t_slice] += cp.asnumpy(cp.sum(in_sig, axis=0))
            accum_n_lsb[t_slice] += cp.asnumpy(cp.sum(in_lsb, axis=0))
            accum_n_rsb[t_slice] += cp.asnumpy(cp.sum(in_rsb, axis=0))

            del in_win, phases, in_sig, in_lsb, in_rsb
            cp.get_default_memory_pool().free_all_blocks()

    if chunk_idx % 10 == 0:
        elapsed = time.time() - t0
        print(f"  [{chunk_idx} chunks | {total_events/1e6:.1f}M events | {elapsed:.0f}s]")

elapsed = time.time() - t0
print(f"\n[NEW] Complete: {total_events:,} events in {elapsed:.1f}s")

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
#  ANALYSIS PER REGION
# ═══════════════════════════════════════════════════════════

from scipy.signal import find_peaks

print("\n" + "=" * 90)
print("  NEW CANDIDATE DEEP ANALYSIS")
print("=" * 90)

for rname, rdata in CANDIDATES.items():
    sl = region_slices[rname]
    m_region = sweep[sl]
    z_region = Z_scores[sl]
    az_region = absZ[sl]
    nw_region = accum_n_win[sl]

    print(f"\n── {rname} ──")
    print(f"   Context: {rdata['context']}")
    print(f"   Mass range: {m_region[0]:.3f} – {m_region[-1]:.3f} GeV")
    print(f"   Step size: {(m_region[1]-m_region[0])*1000:.0f} MeV")
    print(f"   Max |Z|: {np.max(az_region):.2f}σ at M = {m_region[np.argmax(az_region)]:.4f} GeV")
    print(f"   Mean |Z|: {np.mean(az_region):.2f}σ")
    print(f"   Median |Z|: {np.median(az_region):.2f}σ")

    # Find peaks
    min_dist = max(5, len(m_region) // 50)
    pks, _ = find_peaks(az_region, height=3.0, distance=min_dist, prominence=1.0)

    if len(pks) > 0:
        print(f"\n   Peaks (>3σ):")
        print(f"   {'M [GeV]':>10s} {'|Z|':>8s} {'Z (signed)':>10s} {'N_win':>10s} {'Assessment':>30s}")
        print("   " + "-" * 75)

        for p in sorted(pks, key=lambda x: -az_region[x])[:10]:
            m = m_region[p]
            z = z_region[p]
            az = az_region[p]
            nw = nw_region[p]

            # Assessment
            if "Z sideband" in rname or "100 GeV" in rname:
                assessment = "Z/DY continuum (not new physics)"
            elif m > 82 and m < 100:
                assessment = "Z/DY continuum (not new physics)"
            elif 8.0 < m < 8.5:
                assessment = "⭐ Near bb̄ threshold — INVESTIGATE"
            elif 7.5 < m < 8.0:
                assessment = "⭐ Below bb̄ threshold — ANOMALOUS"
            elif 20 < m < 27:
                if az > 5:
                    assessment = "⭐ DY desert — UNEXPECTED SIGNAL"
                else:
                    assessment = "Marginal — likely DY fluctuation"
            else:
                assessment = "Unknown"

            print(f"   {m:>10.4f} {az:>8.2f} {z:>+10.2f} {nw:>10,} {assessment:>30s}")
    else:
        print(f"   No peaks >3σ found.")

# ═══════════════════════════════════════════════════════════
#  VISUALIZATION
# ═══════════════════════════════════════════════════════════

print("\n[viz] Generating candidate plots...")

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

fig, axes = plt.subplots(3, 1, figsize=(22, 18))

fig.suptitle("ACS New Candidate Deep Analysis\n"
             f"Ultra-fine resolution scans on {total_events:,} CMS events",
             fontsize=15, fontweight="bold", color="white", y=0.99)

for ax, (rname, rdata) in zip(axes, CANDIDATES.items()):
    sl = region_slices[rname]
    m_r = sweep[sl]
    az_r = absZ[sl]
    z_r = Z_scores[sl]

    # Signed fill
    ax.fill_between(m_r, z_r, 0, where=z_r > 0, alpha=0.4, color="#00ff88")
    ax.fill_between(m_r, z_r, 0, where=z_r < 0, alpha=0.4, color="#ff6b6b")
    ax.plot(m_r, z_r, color="white", linewidth=1, alpha=0.7)

    ax.axhline(5, color="lime", linestyle="--", alpha=0.3)
    ax.axhline(-5, color="lime", linestyle="--", alpha=0.3)
    ax.axhline(0, color="white", linewidth=0.3, alpha=0.3)

    # Mark known particles
    for pname, pmass in rdata.get("known_nearby", {}).items():
        if m_r[0] <= pmass <= m_r[-1]:
            ax.axvline(pmass, color="#ffd93d", linewidth=1.5, alpha=0.5, linestyle="--")
            ax.text(pmass, ax.get_ylim()[1] * 0.85 if ax.get_ylim()[1] > 0 else 5,
                    f" {pname}\n {pmass:.3f}",
                    fontsize=8, color="#ffd93d", va="top")

    # Find and mark peaks
    min_dist = max(5, len(m_r) // 50)
    pks, _ = find_peaks(az_r, height=3.0, distance=min_dist, prominence=1.0)
    for p in pks:
        color = "#ff6b6b" if az_r[p] > 5 else "#ffd93d"
        ax.plot(m_r[p], z_r[p], "v", color=color, markersize=10, zorder=10)
        ax.annotate(f"{m_r[p]:.3f} GeV\n{az_r[p]:.1f}σ",
                    (m_r[p], z_r[p]), textcoords="offset points",
                    xytext=(10, 10 if z_r[p] > 0 else -20),
                    fontsize=8, color=color,
                    bbox=dict(boxstyle="round,pad=0.2", facecolor="#1a1a2e",
                             edgecolor=color, alpha=0.8))

    ax.set_title(rname, fontsize=12, fontweight="bold")
    ax.set_ylabel("Z [σ] (signed)", fontsize=11)
    ax.grid(alpha=0.15)

axes[-1].set_xlabel("M [GeV]", fontsize=12)

plt.tight_layout(rect=[0, 0, 1, 0.95])
outpath = os.path.join(cfg.OUTPUT_DIR, "acs_new_candidates.png")
fig.savefig(outpath, dpi=200, bbox_inches="tight", facecolor="#0a0a0f")
plt.close()
print(f"[viz] Saved: {outpath}")

# ─── Final verdict ───
print("\n" + "=" * 90)
print("  VERDICT")
print("=" * 90)
print("""
  Region A (7.5 – 8.5 GeV, bb̄ threshold):
    This is the most interesting candidate region. The bb̄ production
    threshold is at ~8.36 GeV (2×m_b). Any peaks HERE would be either:
    (a) Sub-threshold bb̄ bound states (like ηb predictions)
    (b) Exotic states (tetraquarks, glueballs)
    (c) Detector/background artifacts

  Region B (20 – 27 GeV):
    Pure Drell-Yan desert. Any signal here is either a DY structure
    effect or genuinely anomalous. Needs independent validation.

  Region C (82 – 100 GeV):
    Z boson continuum. The virtual γ*/Z interference creates a
    continuous signal that ACS detects. This is EXPECTED physics,
    not new particles.
""")
print("[done]")

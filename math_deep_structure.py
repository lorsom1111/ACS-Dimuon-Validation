"""
ACS MATHEMATICAL DEEP STRUCTURE ANALYSIS
==========================================
Search for fractals, Fibonacci, Euler, Pi, Golden Ratio
at ALL levels of the ACS phase structure.

1. MULTI-ATTRACTOR SCAN — test ALL mathematical constants as attractors
2. MASS RATIO MATRIX — do particle mass ratios encode π, φ, e?
3. FRACTAL ANALYSIS — self-similarity, box-counting, Hurst exponent
4. FIBONACCI PATTERN — do resonance masses follow Fibonacci spacing?
5. PHASE DISTRIBUTION TOPOLOGY — full angular structure
"""

import os, sys, time, math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from itertools import combinations

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as cfg

# ═══════════════════════════════════════════════════════════
#  DETECTED PARTICLES FROM FULL-SPECTRUM SCAN
# ═══════════════════════════════════════════════════════════

# All 29 particles detected by ACS with their masses and |Z|
DETECTED = {
    # Light mesons
    "η(548)":        (0.5479,    5.5),
    "ρ(770)":        (0.7753,   61.2),
    "ω(782)":        (0.7827,   24.8),
    "η'(958)":       (0.9578,   62.3),
    "a₀(980)":       (0.9800,   67.2),
    "f₀(980)":       (0.9900,  143.5),
    "φ(1020)":       (1.0195,   19.7),
    # Charmonium
    "ηc(1S)":        (2.9839,  598.2),
    "J/ψ":           (3.0969, 2136.1),
    "χc0(1P)":       (3.4147,   14.7),
    "χc1(1P)":       (3.5107,   82.5),
    "hc(1P)":        (3.5254,   96.3),
    "χc2(1P)":       (3.5562,   91.8),
    "ηc(2S)":        (3.6392,  183.1),
    "ψ(2S)":         (3.6861,  293.4),
    "ψ(3770)":       (3.7737,   82.1),
    # Bottomonium
    "Υ(1S)":         (9.4603,  614.0),
    "χb0(1P)":       (9.8594,  150.8),
    "χb1(1P)":       (9.8928,   93.5),
    "χb2(1P)":       (9.9122,   47.2),
    "Υ(2S)":        (10.0233,  169.6),
    "χb0(2P)":      (10.2325,   55.6),
    "χb1(2P)":      (10.2555,   77.5),
    "χb2(2P)":      (10.2686,   85.5),
    "Υ(3S)":        (10.3552,  115.1),
    "Υ(4S)":        (10.5794,   95.0),
    "Υ(10860)":     (10.8852,   49.7),
    "Υ(11020)":     (11.0000,   18.2),
    # Electroweak
    "Z":            (91.1876, 1439.3),
}

names = list(DETECTED.keys())
masses = np.array([DETECTED[n][0] for n in names])
sigmas = np.array([DETECTED[n][1] for n in names])
n_particles = len(masses)

# ═══════════════════════════════════════════════════════════
#  MATHEMATICAL CONSTANTS CATALOG
# ═══════════════════════════════════════════════════════════

PI = np.pi
PHI = (1 + np.sqrt(5)) / 2          # Golden ratio ≈ 1.6180
E = np.e                             # Euler's number ≈ 2.7183
SQRT2 = np.sqrt(2)                   # ≈ 1.4142
SQRT3 = np.sqrt(3)                   # ≈ 1.7321
LN2 = np.log(2)                      # ≈ 0.6931
EULER_GAMMA = 0.5772156649           # Euler-Mascheroni

CONSTANTS = {
    # Core constants
    "π":        PI,
    "π/2":      PI/2,
    "π/3":      PI/3,
    "π/4":      PI/4,
    "π/6":      PI/6,
    "2π/3":     2*PI/3,
    "π²":       PI**2,
    "√π":       np.sqrt(PI),
    "1/π":      1/PI,
    # Golden ratio
    "φ":        PHI,
    "1/φ":      1/PHI,
    "φ²":       PHI**2,
    "ln(φ)":    np.log(PHI),
    "2/φ":      2/PHI,
    "π/φ":      PI/PHI,
    # Euler
    "e":        E,
    "1/e":      1/E,
    "e/π":      E/PI,
    "ln(2)":    LN2,
    "γ":        EULER_GAMMA,
    "e²":       E**2,
    # Roots
    "√2":       SQRT2,
    "√3":       SQRT3,
    "√5":       np.sqrt(5),
    "1/√2":     1/SQRT2,
    # Combinations
    "φ/π":      PHI/PI,
    "e/φ":      E/PHI,
    "π·φ":      PI * PHI,
    "e·φ":      E * PHI,
    "π+φ":      PI + PHI,
    "π·e":      PI * E,
    # Integer ratios
    "2":        2.0,
    "3":        3.0,
    "3/2":      1.5,
    "4/3":      4/3,
    "5/3":      5/3,
}

print("=" * 100)
print("  ACS MATHEMATICAL DEEP STRUCTURE ANALYSIS")
print("=" * 100)
print(f"  {n_particles} detected particles, {len(CONSTANTS)} mathematical constants")

# ═══════════════════════════════════════════════════════════
#  1. MASS RATIO MATRIX — ALL pairwise ratios
# ═══════════════════════════════════════════════════════════

print("\n\n" + "─" * 100)
print("  1. MASS RATIO ANALYSIS")
print("─" * 100)

# Compute all pairwise mass ratios (larger/smaller)
ratios = []
ratio_labels = []
for i, j in combinations(range(n_particles), 2):
    r = max(masses[i], masses[j]) / min(masses[i], masses[j])
    ratios.append(r)
    ratio_labels.append((names[i], names[j]))

ratios = np.array(ratios)

# For each constant, find how many mass ratios are close to it or its multiples
print(f"\n  {len(ratios)} pairwise mass ratios computed")
print(f"\n  {'Constant':>12s} {'Value':>10s} {'#Matches':>10s} {'Closest ratio':>14s} {'Pair':>35s} {'Error':>8s}")
print("  " + "-" * 95)

hits = {}
for cname, cval in sorted(CONSTANTS.items(), key=lambda x: x[1]):
    if cval <= 0 or cval > 200:
        continue
    # Check ratios near c, 2c, 3c, c/2, c/3 etc.
    for mult_name, mult in [("", 1), ("2×", 2), ("3×", 3)]:
        target = cval * mult
        if target < 1.001 or target > 200:
            continue
        # Find matches within 2%
        rel_err = np.abs(ratios - target) / target
        close = rel_err < 0.02
        n_match = np.sum(close)
        if n_match > 0:
            best_idx = np.argmin(rel_err)
            best_err = rel_err[best_idx] * 100
            pair = f"{ratio_labels[best_idx][0]} / {ratio_labels[best_idx][1]}"
            label = f"{mult_name}{cname}"
            hits[label] = (target, n_match, best_err, pair)
            if best_err < 1.0:  # Only show <1% matches
                print(f"  {label:>12s} {target:>10.4f} {n_match:>10d} "
                      f"{ratios[best_idx]:>14.4f} {pair:>35s} {best_err:>7.3f}%")

# ── Significance test: compare to random ratios ──
print(f"\n  ── Monte Carlo significance test ──")
np.random.seed(42)
n_mc = 10000
n_real_hits = sum(1 for k, v in hits.items() if v[2] < 0.5)
mc_hits = []
for _ in range(n_mc):
    fake_masses = np.random.uniform(0.3, 100, n_particles)
    fake_ratios = []
    for i, j in combinations(range(n_particles), 2):
        fake_ratios.append(max(fake_masses[i], fake_masses[j]) /
                          min(fake_masses[i], fake_masses[j]))
    fake_ratios = np.array(fake_ratios)

    count = 0
    for cname, cval in CONSTANTS.items():
        for mult in [1, 2, 3]:
            target = cval * mult
            if target < 1.001 or target > 200:
                continue
            rel_err = np.abs(fake_ratios - target) / target
            if np.any(rel_err < 0.005):
                count += 1
    mc_hits.append(count)

mc_mean = np.mean(mc_hits)
mc_std = np.std(mc_hits)
z_score = (n_real_hits - mc_mean) / mc_std if mc_std > 0 else 0
print(f"  Real data: {n_real_hits} ratios within 0.5% of a constant")
print(f"  MC random: {mc_mean:.1f} ± {mc_std:.1f}")
print(f"  Significance: {z_score:.1f}σ")

# ═══════════════════════════════════════════════════════════
#  2. MULTI-ATTRACTOR PHASE SCAN
# ═══════════════════════════════════════════════════════════

print("\n\n" + "─" * 100)
print("  2. MULTI-ATTRACTOR PHASE SCAN")
print("─" * 100)
print("  For each detected particle, compute arctan(M_other/M_self)")
print("  and check which mathematical constants appear as clustering angles\n")

# For all pairs of detected particles, compute arctan(m_i / m_j)
all_phases = []
phase_weights = []  # weight by significance
for i in range(n_particles):
    for j in range(n_particles):
        if i == j:
            continue
        phase = np.arctan(masses[i] / masses[j])
        all_phases.append(phase)
        phase_weights.append(np.sqrt(sigmas[i] * sigmas[j]))  # geometric mean σ

all_phases = np.array(all_phases)
phase_weights = np.array(phase_weights)

# Test each constant as potential attractor
print(f"  {len(all_phases)} inter-particle phases computed")
print(f"\n  {'Attractor':>12s} {'Angle [rad]':>12s} {'#Within 1%':>12s} "
      f"{'#Within 5%':>12s} {'Weighted density':>18s}")
print("  " + "-" * 75)

attractor_scores = {}
for cname, cval in sorted(CONSTANTS.items(), key=lambda x: x[1]):
    if cval <= 0 or cval > PI / 2:  # arctan range is [0, π/2]
        continue
    # Count phases within 1% and 5% of this constant
    rel_diff = np.abs(all_phases - cval) / cval
    n_1pct = np.sum(rel_diff < 0.01)
    n_5pct = np.sum(rel_diff < 0.05)
    w_density = np.sum(phase_weights[rel_diff < 0.02])
    attractor_scores[cname] = (cval, n_1pct, n_5pct, w_density)
    if n_1pct > 0:
        print(f"  {cname:>12s} {cval:>12.6f} {n_1pct:>12d} {n_5pct:>12d} {w_density:>18.1f}")

# ═══════════════════════════════════════════════════════════
#  3. FIBONACCI IN THE MASS SPECTRUM
# ═══════════════════════════════════════════════════════════

print("\n\n" + "─" * 100)
print("  3. FIBONACCI PATTERN SEARCH")
print("─" * 100)

# Test 1: consecutive mass ratios → Fibonacci ratios?
sorted_m = np.sort(masses)
consec_ratios = sorted_m[1:] / sorted_m[:-1]

fib_ratios = [PHI, 2.0, 1.5, 5/3, 8/5, 13/8, 21/13, 34/21]
fib_names = ["φ", "2/1", "3/2", "5/3", "8/5", "13/8", "21/13", "34/21"]

print(f"\n  Consecutive mass ratios (sorted by mass):")
print(f"  {'m_i':>8s} → {'m_j':>8s} {'Ratio':>8s} {'Nearest Fib':>12s} {'Error':>8s}")
print("  " + "-" * 55)

fib_hits = 0
for i in range(len(consec_ratios)):
    r = consec_ratios[i]
    # Find nearest Fibonacci ratio
    min_err = 999
    best_fib = ""
    for fn, fv in zip(fib_names, fib_ratios):
        err = abs(r - fv) / fv * 100
        if err < min_err:
            min_err = err
            best_fib = fn
    if min_err < 5:
        fib_hits += 1
        marker = "⭐" if min_err < 1 else "✓"
    else:
        marker = ""
    if min_err < 10 or r > 1.3:  # Only show interesting ones
        print(f"  {sorted_m[i]:>8.4f} → {sorted_m[i+1]:>8.4f} {r:>8.4f} "
              f"{best_fib:>12s} {min_err:>7.2f}% {marker}")

# Test 2: Fibonacci-like additive property
print(f"\n  Fibonacci additive test: m_k ≈ m_i + m_j ?")
print(f"  {'m_i':>8s} + {'m_j':>8s} = {'Sum':>8s} {'Nearest m_k':>10s} {'Error':>8s}")
print("  " + "-" * 55)

fib_add_hits = 0
for i in range(n_particles):
    for j in range(i+1, n_particles):
        target = masses[i] + masses[j]
        # Find nearest actual mass
        dists = np.abs(masses - target)
        k = np.argmin(dists)
        if k != i and k != j:
            err = dists[k] / target * 100
            if err < 2:
                fib_add_hits += 1
                print(f"  {masses[i]:>8.4f} + {masses[j]:>8.4f} = {target:>8.4f} "
                      f"{masses[k]:>10.4f} {err:>7.2f}% ⭐ {names[k]}")

# ═══════════════════════════════════════════════════════════
#  4. FRACTAL / SELF-SIMILARITY ANALYSIS
# ═══════════════════════════════════════════════════════════

print("\n\n" + "─" * 100)
print("  4. FRACTAL / SELF-SIMILARITY ANALYSIS")
print("─" * 100)

# Load the full spectrum data
data_path = os.path.join(cfg.OUTPUT_DIR, "full_spectrum_data.npz")
if os.path.exists(data_path):
    fdata = np.load(data_path)
    full_masses = fdata["masses"]
    full_absZ = fdata["absZ"]
    full_Z = fdata["Z"]

    # Test 1: Self-similarity across scales
    # Compare Z-score pattern in different mass windows
    regions = {
        "Light (0.3-1.3)": (0.3, 1.3),
        "Charm (2.5-4.5)": (2.5, 4.5),
        "Bottom (8.5-11.5)": (8.5, 11.5),
    }

    print(f"\n  Self-similarity test: correlate Z-score profiles across scales")
    normalized_profiles = {}

    for rname, (mlo, mhi) in regions.items():
        mask = (full_masses >= mlo) & (full_masses <= mhi)
        z_region = full_absZ[mask]
        if len(z_region) > 10:
            # Normalize to [0,1] in both x and y
            z_norm = (z_region - z_region.min()) / (z_region.max() - z_region.min() + 1e-10)
            # Resample to 100 points
            x_orig = np.linspace(0, 1, len(z_norm))
            x_resamp = np.linspace(0, 1, 100)
            z_resamp = np.interp(x_resamp, x_orig, z_norm)
            normalized_profiles[rname] = z_resamp

    if len(normalized_profiles) >= 2:
        print(f"\n  Cross-correlation matrix (normalized Z-profiles):")
        rnames = list(normalized_profiles.keys())
        print(f"  {'':>20s}", end="")
        for rn in rnames:
            print(f" {rn:>18s}", end="")
        print()
        for i, rn1 in enumerate(rnames):
            print(f"  {rn1:>20s}", end="")
            for j, rn2 in enumerate(rnames):
                corr = np.corrcoef(normalized_profiles[rn1], normalized_profiles[rn2])[0, 1]
                print(f" {corr:>18.4f}", end="")
            print()

    # Test 2: Hurst exponent (fractal dimension indicator)
    # H > 0.5 = persistent (fractal trend), H = 0.5 = random, H < 0.5 = anti-persistent
    def hurst_exponent(series, max_lag=None):
        n = len(series)
        if max_lag is None:
            max_lag = n // 4
        lags = range(2, max_lag)
        tau = []
        for lag in lags:
            chunks = [series[i:i+lag] for i in range(0, n - lag, lag)]
            rs_values = []
            for chunk in chunks:
                if len(chunk) < 2:
                    continue
                mean_c = np.mean(chunk)
                dev = np.cumsum(chunk - mean_c)
                R = np.max(dev) - np.min(dev)
                S = np.std(chunk, ddof=1)
                if S > 0:
                    rs_values.append(R / S)
            if rs_values:
                tau.append((lag, np.mean(rs_values)))

        if len(tau) < 3:
            return 0.5
        lags_arr = np.array([t[0] for t in tau])
        rs_arr = np.array([t[1] for t in tau])
        valid = rs_arr > 0
        if np.sum(valid) < 3:
            return 0.5
        H = np.polyfit(np.log(lags_arr[valid]), np.log(rs_arr[valid]), 1)[0]
        return H

    for rname, (mlo, mhi) in regions.items():
        mask = (full_masses >= mlo) & (full_masses <= mhi)
        z_region = full_Z[mask]
        if len(z_region) > 20:
            H = hurst_exponent(z_region)
            D = 2 - H  # Fractal dimension
            print(f"\n  {rname}:")
            print(f"    Hurst exponent H = {H:.4f}")
            print(f"    Fractal dimension D = {D:.4f}")
            if H > 0.6:
                print(f"    → PERSISTENT (trending/correlated structure)")
            elif H < 0.4:
                print(f"    → ANTI-PERSISTENT (oscillatory)")
            else:
                print(f"    → NEAR-RANDOM")

    # Test 3: Power spectrum — look for 1/f noise (fractal signature)
    print(f"\n  Power spectrum analysis (1/f^α test):")
    for rname, (mlo, mhi) in regions.items():
        mask = (full_masses >= mlo) & (full_masses <= mhi)
        z_region = full_Z[mask]
        if len(z_region) > 50:
            fft = np.fft.rfft(z_region - np.mean(z_region))
            power = np.abs(fft) ** 2
            freqs = np.fft.rfftfreq(len(z_region))
            # Fit log-log slope (exclude DC and highest freq)
            valid = (freqs > 0) & (power > 0)
            if np.sum(valid) > 5:
                slope, _ = np.polyfit(np.log10(freqs[valid][1:]),
                                     np.log10(power[valid][1:]), 1)
                print(f"    {rname}: α = {-slope:.3f} "
                      f"({'1/f (pink noise)' if -1.5 < slope < -0.5 else '1/f² (brown)' if slope < -1.5 else 'white noise'})")

# ═══════════════════════════════════════════════════════════
#  5. EULER'S IDENTITY & π IN PHASE STRUCTURE
# ═══════════════════════════════════════════════════════════

print("\n\n" + "─" * 100)
print("  5. EULER / π DEEP STRUCTURE")
print("─" * 100)

# The ACS attractor is at π/4. Let's see what happens at ALL π/n:
print(f"\n  Phase concentration at π/n for detected particles:")
print(f"  {'n':>4s} {'π/n [rad]':>12s} {'Mean |Z| at π/n':>18s} {'Peak near π/n?':>15s}")
print("  " + "-" * 55)

if os.path.exists(data_path):
    for n_div in range(1, 13):
        target_angle = PI / n_div
        # For each detected particle, check Z at mass where arctan(m/M₀) = π/n
        # → m = M₀ × tan(π/n)
        total_z = 0
        count = 0
        for m0 in masses:
            m_target = m0 * np.tan(target_angle) if target_angle < PI/2 else None
            if m_target is not None and 0.2 < m_target < 200:
                idx = np.argmin(np.abs(full_masses - m_target))
                total_z += full_absZ[idx]
                count += 1
        if count > 0:
            mean_z = total_z / count
            peak = "⭐⭐⭐" if mean_z > 50 else "⭐⭐" if mean_z > 10 else \
                   "⭐" if mean_z > 5 else ""
            print(f"  {n_div:>4d} {target_angle:>12.6f} {mean_z:>18.2f} {peak:>15s}")

# Check e^(iπθ) structure — does the phase relate to Euler's formula?
print(f"\n  Euler's formula test: e^(iπ·θ/θ₀) at resonances")
print(f"  For each detected particle, θ = arctan(1) = π/4")
print(f"  e^(iπ·(π/4)/(π/4)) = e^(iπ) = -1 ← Euler's identity!")
print(f"  → At the ACS attractor, the phase factor IS Euler's identity.")

# ═══════════════════════════════════════════════════════════
#  6. GOLDEN RATIO IN MASS HIERARCHIES
# ═══════════════════════════════════════════════════════════

print("\n\n" + "─" * 100)
print("  6. GOLDEN RATIO φ IN MASS HIERARCHIES")
print("─" * 100)

# Check: is the spacing between particle families related to φ?
families = {
    "Light mesons": masses[masses < 1.2],
    "Charmonium":   masses[(masses > 2.5) & (masses < 4.5)],
    "Bottomonium":  masses[(masses > 8.5) & (masses < 12)],
    "Electroweak":  masses[masses > 50],
}

family_means = {k: np.mean(v) for k, v in families.items() if len(v) > 0}
family_names = list(family_means.keys())
family_vals = list(family_means.values())

print(f"\n  Family mean masses:")
for fn, fv in family_means.items():
    print(f"    {fn:>15s}: {fv:.4f} GeV")

print(f"\n  Inter-family mass ratios vs φ:")
for i in range(len(family_names)):
    for j in range(i+1, len(family_names)):
        r = max(family_vals[i], family_vals[j]) / min(family_vals[i], family_vals[j])
        # Test against powers of φ
        for p in range(-5, 10):
            phi_p = PHI ** p
            if phi_p > 0.01 and abs(r - phi_p) / phi_p < 0.05:
                err = abs(r - phi_p) / phi_p * 100
                print(f"    {family_names[j]} / {family_names[i]} = {r:.4f} ≈ φ^{p} = {phi_p:.4f} ({err:.2f}%)")

# Individual mass ratios vs φ powers
print(f"\n  Individual mass ratios matching φ^n (< 2% error):")
for i in range(n_particles):
    for j in range(i+1, n_particles):
        r = masses[j] / masses[i] if masses[j] > masses[i] else masses[i] / masses[j]
        for p in range(-5, 10):
            phi_p = PHI ** p
            if 0.5 < phi_p < 200:
                err = abs(r - phi_p) / phi_p * 100
                if err < 2.0:
                    n1 = names[i] if masses[i] < masses[j] else names[j]
                    n2 = names[j] if masses[i] < masses[j] else names[i]
                    print(f"    {n2:>12s} / {n1:<12s} = {r:.5f} ≈ φ^{p} = {phi_p:.5f} ({err:.2f}%)")

# ═══════════════════════════════════════════════════════════
#  VISUALIZATION
# ═══════════════════════════════════════════════════════════

print("\n[viz] Generating mathematical structure plots...")

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

fig = plt.figure(figsize=(28, 32))
gs = GridSpec(4, 2, hspace=0.35, wspace=0.25, figure=fig)

fig.suptitle("ACS MATHEMATICAL DEEP STRUCTURE\n"
             "Fractals · Fibonacci · Euler · π · φ",
             fontsize=18, fontweight="bold", color="white", y=0.995)

# ── Panel 1: Mass ratio histogram vs constants ──
ax1 = fig.add_subplot(gs[0, 0])
ax1.hist(ratios, bins=100, range=(1, 15), color="#00ccff", alpha=0.5,
         density=True, label="Mass ratios")
for cname, cval in [("π", PI), ("φ", PHI), ("e", E), ("√2", SQRT2),
                     ("√3", SQRT3), ("φ²", PHI**2), ("π²", PI**2)]:
    if 1 < cval < 15:
        ax1.axvline(cval, color="#ffd93d", linewidth=1.5, alpha=0.7)
        ax1.text(cval, ax1.get_ylim()[1] * 0.9 if ax1.get_ylim()[1] > 0 else 0.5,
                 f" {cname}", fontsize=9, color="#ffd93d", rotation=90, va="top")
ax1.set_title("Mass Ratio Distribution vs Constants", fontsize=12, fontweight="bold")
ax1.set_xlabel("m_i / m_j")
ax1.set_ylabel("Density")
ax1.grid(alpha=0.15)

# ── Panel 2: Inter-particle phase distribution ──
ax2 = fig.add_subplot(gs[0, 1])
ax2.hist(all_phases, bins=100, color="#00ff88", alpha=0.5, density=True)
# Mark key angles
for cname, cval in [("π/6", PI/6), ("π/4", PI/4), ("π/3", PI/3),
                     ("1/φ", 1/PHI), ("1/e", 1/E), ("ln2", LN2)]:
    if 0 < cval < PI/2:
        ax2.axvline(cval, color="#ffd93d", linewidth=1.5, alpha=0.7)
        ax2.text(cval, ax2.get_ylim()[1] * 0.9 if ax2.get_ylim()[1] > 0 else 0.5,
                 f" {cname}", fontsize=9, color="#ffd93d", rotation=90, va="top")
ax2.set_title("Inter-Particle Phase Distribution", fontsize=12, fontweight="bold")
ax2.set_xlabel("arctan(m_i / m_j) [rad]")
ax2.set_ylabel("Density")
ax2.grid(alpha=0.15)

# ── Panel 3: Consecutive mass ratios vs Fibonacci ──
ax3 = fig.add_subplot(gs[1, 0])
ax3.bar(range(len(consec_ratios)), consec_ratios, color="#00ccff", alpha=0.7)
for fn, fv in zip(fib_names[:5], fib_ratios[:5]):
    if 1 < fv < max(consec_ratios) * 1.1:
        ax3.axhline(fv, color="#ffd93d", linewidth=1, alpha=0.5, linestyle="--")
        ax3.text(len(consec_ratios) - 1, fv, f" {fn}={fv:.3f}",
                 fontsize=8, color="#ffd93d", va="bottom")
ax3.set_title("Consecutive Mass Ratios vs Fibonacci", fontsize=12, fontweight="bold")
ax3.set_xlabel("Particle index (sorted by mass)")
ax3.set_ylabel("m(n+1) / m(n)")
ax3.grid(alpha=0.15)

# ── Panel 4: Log-mass spectrum (looking for equal spacing = geometric series) ──
ax4 = fig.add_subplot(gs[1, 1])
log_masses = np.log(sorted_m)
ax4.scatter(range(len(sorted_m)), log_masses, c=np.log10(sigmas[np.argsort(masses)]),
            cmap="plasma", s=40, zorder=5)
ax4.plot(range(len(sorted_m)), log_masses, color="white", alpha=0.3)
# Fit line (geometric progression)
coeffs = np.polyfit(range(len(sorted_m)), log_masses, 1)
ax4.plot(range(len(sorted_m)), np.polyval(coeffs, range(len(sorted_m))),
         color="#ff6b6b", linewidth=2, linestyle="--",
         label=f"Fit: growth rate = {np.exp(coeffs[0]):.3f}×/particle")
ax4.set_title("Log-Mass Spectrum (Geometric Progression?)", fontsize=12, fontweight="bold")
ax4.set_xlabel("Particle index (sorted)")
ax4.set_ylabel("ln(mass)")
ax4.legend(fontsize=9)
ax4.grid(alpha=0.15)

# ── Panel 5: Fractal self-similarity ──
ax5 = fig.add_subplot(gs[2, 0])
if len(normalized_profiles) >= 2:
    colors = ["#00ccff", "#ff6b6b", "#00ff88"]
    for (rname, profile), color in zip(normalized_profiles.items(), colors):
        ax5.plot(np.linspace(0, 1, len(profile)), profile,
                 color=color, linewidth=1.5, alpha=0.8, label=rname)
ax5.set_title("Fractal Self-Similarity: Normalized |Z| Profiles", fontsize=12, fontweight="bold")
ax5.set_xlabel("Normalized position in region")
ax5.set_ylabel("Normalized |Z|")
ax5.legend(fontsize=9)
ax5.grid(alpha=0.15)

# ── Panel 6: Phase wheel — all inter-particle phases on unit circle ──
ax6 = fig.add_subplot(gs[2, 1], projection="polar")
theta_phases = all_phases
r_weights = phase_weights / phase_weights.max()
ax6.scatter(theta_phases, r_weights, s=3, alpha=0.3, color="#00ccff")
# Mark constants
for cname, cval in [("π/4", PI/4), ("π/3", PI/3), ("π/6", PI/6)]:
    if 0 < cval < PI/2:
        ax6.axvline(cval, color="#ffd93d", linewidth=2, alpha=0.5)
ax6.set_title("Phase Wheel\n(arctan of all mass ratios)", fontsize=12, fontweight="bold", pad=20)
ax6.set_thetamin(0)
ax6.set_thetamax(90)

# ── Panel 7: Mass ratio distance from φ ──
ax7 = fig.add_subplot(gs[3, 0])
phi_distances = []
for r in ratios:
    min_d = min(abs(r - PHI**p) for p in range(-3, 8) if PHI**p > 0.1)
    phi_distances.append(min_d)
phi_distances = np.array(phi_distances)
ax7.hist(phi_distances, bins=50, color="#ff88ff", alpha=0.7)
ax7.axvline(0, color="lime", linewidth=2)
ax7.set_title("Distance of Mass Ratios from Nearest φ^n", fontsize=12, fontweight="bold")
ax7.set_xlabel("|ratio - φⁿ|")
ax7.set_ylabel("Count")
ax7.grid(alpha=0.15)

# ── Panel 8: π relationships ──
ax8 = fig.add_subplot(gs[3, 1])
pi_distances = []
for r in ratios:
    min_d = min(abs(r - PI**p * k) for p in range(-2, 3) for k in [1, 0.5, 2, 1/3, 3]
                if 0.1 < PI**p * k < 200)
    pi_distances.append(min_d)
pi_distances = np.array(pi_distances)
ax8.hist(pi_distances, bins=50, color="#00ff88", alpha=0.7, label="π^n·k")
ax8.hist(phi_distances, bins=50, color="#ff88ff", alpha=0.5, label="φ^n")
ax8.set_title("Distance from π vs φ Power Laws", fontsize=12, fontweight="bold")
ax8.set_xlabel("Min distance to nearest π^n·k or φ^n")
ax8.set_ylabel("Count")
ax8.legend(fontsize=9)
ax8.grid(alpha=0.15)

plt.savefig(os.path.join(cfg.OUTPUT_DIR, "acs_mathematical_structure.png"),
            dpi=200, bbox_inches="tight", facecolor="#0a0a0f")
plt.close()
print(f"[viz] Saved: output/acs_mathematical_structure.png")

print("\n" + "=" * 100)
print("  ANALYSIS COMPLETE")
print("=" * 100)

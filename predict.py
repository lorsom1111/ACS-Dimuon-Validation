"""
ACS Testable Prediction — Mass Spectrum from First Principles
==============================================================
Uses the ACS algebraic sequence Z_n = 1/(2n+1) to derive
the mass spectrum of dimuon resonances and predict new states.

The ACS phase: θ = arctan(M / M_ref) converges to π/4.
At convergence: M = M_ref (trivial).
Off-convergence: θ_n = π/4 - Z_n = π/4 - 1/(2n+1)

This means allowed mass ratios are:
    M_i / M_j = tan(π/4 - 1/(2n+1))

For each "generation" n, this defines a discrete mass spectrum.
We fit the observed spectrum, find gaps, and predict.
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os

OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ─── Known resonances (PDG 2024) ───
KNOWN = {
    "φ(1020)":   1.01946,
    "J/ψ":       3.0969,
    "ψ(2S)":     3.6861,
    "Υ(1S)":     9.4603,
    "Υ(2S)":    10.0233,
    "Υ(3S)":    10.3552,
    "Z":        91.1876,
    "H":       125.1,
}

# Additional known but not in our dataset
KNOWN_EXTRA = {
    "ρ(770)":    0.77526,
    "ω(782)":    0.78265,
    "ψ(3770)":   3.7737,
    "Υ(4S)":    10.5794,
    "Υ(10860)": 10.8852,
    "Υ(11020)": 11.0190,
    "W":        80.3692,
}

ACS_ATTRACTOR = np.pi / 4

# ─── ACS Sequence Analysis ───
print("=" * 70)
print("  ACS PREDICTION ENGINE — Mass Spectrum from π/4")
print("=" * 70)

# For each pair of known resonances, compute the ACS generation n
# From: arctan(M_i / M_j) = π/4 - 1/(2n+1)
# So: 1/(2n+1) = π/4 - arctan(M_i / M_j)
# And: n = (1/(π/4 - arctan(M_i/M_j)) - 1) / 2

print("\n── Phase deviations from π/4 ──")
masses = sorted(KNOWN.items(), key=lambda x: x[1])
for name, m in masses:
    # Phase when this mass IS the target (self-referential)
    # But more useful: phase relative to neighboring resonances
    theta = np.arctan(m / m)  # = π/4 exactly (trivial)
    print(f"  {name:12s}  M = {m:9.4f} GeV")

# ─── The key insight: mass ratios and ACS generations ───
print("\n── ACS Generation Mapping ──")
print("  For each resonance pair (M_heavy / M_light):")
print(f"  {'Pair':<25s} {'M_h/M_l':>8s} {'θ':>10s} {'Δθ':>10s} {'n_acs':>8s}")
print("-" * 70)

pairs = []
names = [n for n, _ in masses]
mvals = [m for _, m in masses]

for i in range(len(masses)):
    for j in range(i + 1, len(masses)):
        n1, m1 = masses[i]
        n2, m2 = masses[j]
        ratio = m2 / m1
        theta = np.arctan(ratio)
        delta = theta - ACS_ATTRACTOR
        # Compute effective n: 1/(2n+1) = |delta|
        if abs(delta) > 1e-10:
            n_eff = (1.0 / abs(delta) - 1) / 2
        else:
            n_eff = float('inf')
        pairs.append((n1, n2, ratio, theta, delta, n_eff))
        if n_eff < 50:  # Only show interesting ones
            print(f"  {n1:>10s}/{n2:<12s} {ratio:8.4f} {theta:10.6f} "
                  f"{delta:+10.6f} {n_eff:8.2f}")

# ─── Find the ACS harmonic structure ───
# The sequence Z_n = 1/(2n+1) for n = 0,1,2,3,...
# gives Δθ = 1, 1/3, 1/5, 1/7, 1/9, ...
# Find which n-values are "occupied" by real particles

print("\n\n── ACS Harmonic Table ──")
print(f"  {'n':>3s} {'Z_n = 1/(2n+1)':>15s} {'tan(π/4 - Z_n)':>15s} {'M predicted':>15s} {'Known?':>20s}")
print("-" * 75)

# Use M_ref = Z boson mass (strongest convergence, most events)
M_ref = KNOWN["Z"]

predictions = []
for n in range(1, 30):
    z_n = 1.0 / (2 * n + 1)
    theta_n = ACS_ATTRACTOR - z_n
    if theta_n <= 0:
        continue
    # Mass from ratio: M = M_ref * tan(theta_n)
    m_predicted = M_ref * np.tan(theta_n)
    
    # Also compute the "inverse": M_ref / tan(theta_n)
    m_predicted_inv = M_ref / np.tan(theta_n)
    
    # Check if any known particle is near this mass
    known_match = ""
    for name, m_known in {**KNOWN, **KNOWN_EXTRA}.items():
        if abs(m_predicted - m_known) / m_known < 0.15:
            known_match = f"← {name} ({m_known:.4f})"
            break
    
    if not known_match:
        known_match = "⚡ PREDICTION"
        predictions.append((n, z_n, m_predicted))
    
    print(f"  {n:3d} {z_n:15.6f} {np.tan(theta_n):15.6f} "
          f"{m_predicted:15.4f} {known_match:>20s}")

# ─── Also try with J/ψ as reference ───
print("\n\n── ACS Harmonics (M_ref = J/ψ = 3.097 GeV) ──")
M_ref2 = KNOWN["J/ψ"]
predictions2 = []
for n in range(1, 30):
    z_n = 1.0 / (2 * n + 1)
    theta_n = ACS_ATTRACTOR - z_n
    if theta_n <= 0:
        continue
    m_predicted = M_ref2 * np.tan(theta_n)
    
    known_match = ""
    for name, m_known in {**KNOWN, **KNOWN_EXTRA}.items():
        if abs(m_predicted - m_known) / m_known < 0.15:
            known_match = f"← {name} ({m_known:.4f})"
            break
    
    if not known_match:
        known_match = "⚡ PREDICTION"
        predictions2.append((n, z_n, m_predicted))
    
    print(f"  {n:3d} {z_n:15.6f} {np.tan(theta_n):15.6f} "
          f"{m_predicted:15.4f} {known_match:>20s}")

# ─── Cross-reference: masses that appear from MULTIPLE references ───
print("\n\n" + "=" * 70)
print("  CROSS-REFERENCED PREDICTIONS")
print("  Masses predicted from multiple reference frames:")
print("=" * 70)

# Build predictions from ALL known masses as reference
all_predictions = {}
for ref_name, ref_mass in KNOWN.items():
    for n in range(1, 50):
        z_n = 1.0 / (2 * n + 1)
        theta_n = ACS_ATTRACTOR - z_n
        if theta_n <= 0:
            continue
        m_pred = ref_mass * np.tan(theta_n)
        if m_pred < 0.1 or m_pred > 500:
            continue
        
        # Check if it matches any known particle
        is_known = False
        for name, m_k in {**KNOWN, **KNOWN_EXTRA}.items():
            if abs(m_pred - m_k) / m_k < 0.10:
                is_known = True
                break
        
        if not is_known:
            # Bin to nearest 0.5 GeV for clustering
            bin_key = round(m_pred * 2) / 2
            if bin_key not in all_predictions:
                all_predictions[bin_key] = []
            all_predictions[bin_key].append({
                "ref": ref_name,
                "n": n,
                "mass": m_pred,
            })

# Find masses predicted by multiple references (convergent predictions)
convergent = {k: v for k, v in all_predictions.items() if len(v) >= 2}
convergent_sorted = sorted(convergent.items(), key=lambda x: -len(x[1]))

print(f"\n  {'M_pred [GeV]':>12s} {'# refs':>7s} {'References':>40s}")
print("-" * 70)
for m_bin, refs in convergent_sorted[:15]:
    m_avg = np.mean([r["mass"] for r in refs])
    ref_list = ", ".join([f"{r['ref']}(n={r['n']})" for r in refs[:4]])
    n_refs = len(refs)
    marker = " ⭐" if n_refs >= 3 else ""
    print(f"  {m_avg:12.3f} {n_refs:7d} {ref_list:>40s}{marker}")


# ─── Generate prediction plot ───
print("\n\n[viz] Generating prediction spectrum...")

plt.style.use('dark_background')
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 10), 
                                gridspec_kw={'height_ratios': [3, 2]})
fig.suptitle("ACS Mass Spectrum — Observed vs Predicted",
             fontsize=16, fontweight='bold', color='white', y=0.96)

# Panel 1: Mass line with known and predicted
known_masses = sorted(KNOWN.items(), key=lambda x: x[1])
known_x = [m for _, m in known_masses]
known_labels = [n for n, _ in known_masses]

ax1.scatter(known_x, [1]*len(known_x), s=200, c='#00ff88', marker='D',
            zorder=10, edgecolors='white', linewidth=1, label='Observed (7/8 converged)')

# Plot predictions
pred_masses = []
pred_strengths = []
for m_bin, refs in convergent_sorted[:20]:
    m_avg = np.mean([r["mass"] for r in refs])
    if 0.3 < m_avg < 200:
        pred_masses.append(m_avg)
        pred_strengths.append(len(refs))

ax1.scatter(pred_masses, [0.5]*len(pred_masses), 
            s=[s*60 for s in pred_strengths],
            c='#ff6b6b', marker='*', zorder=5, alpha=0.8,
            edgecolors='white', linewidth=0.5, label='ACS Predictions')

# Labels
for name, m in known_masses:
    ax1.annotate(f"{name}\n{m:.3f}", (m, 1), textcoords="offset points",
                 xytext=(0, 15), ha='center', fontsize=8, color='#00ff88')

for m_avg, strength in zip(pred_masses[:8], pred_strengths[:8]):
    ax1.annotate(f"{m_avg:.2f}?", (m_avg, 0.5), textcoords="offset points",
                 xytext=(0, -20), ha='center', fontsize=7, color='#ff6b6b',
                 fontstyle='italic')

ax1.set_xscale('log')
ax1.set_xlim(0.5, 200)
ax1.set_ylim(0, 1.8)
ax1.set_xlabel("Mass [GeV]", fontsize=12)
ax1.set_ylabel("", fontsize=1)
ax1.set_yticks([])
ax1.legend(fontsize=10, loc='upper left')
ax1.set_title("Dimuon Mass Spectrum: Known Resonances + ACS Predictions",
              fontsize=13, fontweight='bold')
ax1.grid(axis='x', alpha=0.2)

# Panel 2: ACS generation occupation
ns = list(range(1, 25))
z_ns = [1.0/(2*n+1) for n in ns]

# Check which n-values are occupied
occupied = {}
for ref_name, ref_mass in KNOWN.items():
    for n in range(1, 25):
        z_n = 1.0 / (2*n + 1)
        theta_n = ACS_ATTRACTOR - z_n
        if theta_n <= 0:
            continue
        m_pred = ref_mass * np.tan(theta_n)
        for name, m_k in KNOWN.items():
            if name != ref_name and abs(m_pred - m_k) / m_k < 0.10:
                if n not in occupied:
                    occupied[n] = set()
                occupied[n].add(f"{ref_name}→{name}")

colors = ['#00ff88' if n in occupied else '#333333' for n in ns]
bars = ax2.bar(ns, z_ns, color=colors, edgecolor='white', linewidth=0.5, alpha=0.85)
ax2.axhline(y=0, color='cyan', linewidth=0.5)
ax2.set_xlabel("ACS Generation n", fontsize=12)
ax2.set_ylabel("Z_n = 1/(2n+1)", fontsize=12)
ax2.set_title("ACS Harmonic Occupation (green = matched to known particles)",
              fontsize=13, fontweight='bold')
ax2.set_xticks(ns)
ax2.grid(axis='y', alpha=0.2)

plt.tight_layout(rect=[0, 0, 1, 0.94])
outpath = os.path.join(OUTPUT_DIR, "acs_mass_predictions.png")
plt.savefig(outpath, dpi=200, bbox_inches='tight', facecolor='#1a1a2e')
plt.close()
print(f"[viz] Saved: {outpath}")

print("\n" + "=" * 70)
print("  DONE — Predictions generated from ACS first principles")
print("=" * 70)

"""
Cross-Energy ACS Comparison — 8 TeV vs 13 TeV
================================================
Grand comparison plot showing ACS convergence is energy-independent.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import os

OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ─── Data ───
# Format: (label, Z_8tev, Z_13tev, dtheta_8tev, dtheta_13tev, mass_gev)
resonances = [
    ("J/ψ",     2316,   655.82,  0.00349, 0.003458, 3.097),
    ("Z",        883,   405.45,  0.00521, 0.010218, 91.188),
    ("Υ(1S)",    873,   285.29,  0.00074, 0.000740, 9.460),
    ("ψ(2S)",    331,   100.14,  0.00273, 0.002704, 3.686),
    ("φ",         42,    15.55,  0.00292, 0.002184, 1.020),
    ("Higgs",   -0.18,   -2.22,    None,     None,  125.1),
]

labels     = [r[0] for r in resonances]
z_8        = [r[1] for r in resonances]
z_13       = [r[2] for r in resonances]
dt_8       = [r[3] for r in resonances]
dt_13      = [r[4] for r in resonances]
masses     = [r[5] for r in resonances]

# ─── Color palette ───
colors_8  = ['#FF6B6B', '#4ECDC4', '#FFE66D', '#A8E6CF', '#DDA0DD', '#FF9999']
colors_13 = ['#CC4444', '#2E8B7B', '#CCAA00', '#6BBF8B', '#9B59B6', '#CC6666']

plt.style.use('dark_background')

fig = plt.figure(figsize=(22, 14))
fig.suptitle("ACS Cross-Energy Validation — 8 TeV vs 13 TeV CMS Open Data",
             fontsize=20, fontweight='bold', color='white', y=0.97)

# ═══ Panel 1: Z-score comparison bar chart ═══
ax1 = fig.add_subplot(2, 2, 1)
x = np.arange(len(labels))
width = 0.35

# Clip Higgs negative for log scale display
z_8_plot  = [max(z, 0.1) for z in z_8]
z_13_plot = [max(z, 0.1) for z in z_13]

bars1 = ax1.bar(x - width/2, z_8_plot, width, label='8 TeV (53M events)',
                color='#4ECDC4', alpha=0.85, edgecolor='white', linewidth=0.5)
bars2 = ax1.bar(x + width/2, z_13_plot, width, label='13 TeV (6.4M events)',
                color='#FF6B6B', alpha=0.85, edgecolor='white', linewidth=0.5)

# Color Higgs bars differently
bars1[-1].set_color('#555555')
bars1[-1].set_alpha(0.4)
bars2[-1].set_color('#555555')
bars2[-1].set_alpha(0.4)

ax1.set_yscale('log')
ax1.set_ylabel('Significance Z [σ]', fontsize=13)
ax1.set_title('Convergence Significance', fontsize=15, fontweight='bold')
ax1.set_xticks(x)
ax1.set_xticklabels(labels, fontsize=12)
ax1.legend(fontsize=11, loc='upper right')
ax1.axhline(y=5, color='lime', linestyle='--', alpha=0.4, linewidth=1)
ax1.text(len(labels)-0.5, 6, '5σ discovery', color='lime', alpha=0.6, fontsize=9)
ax1.set_ylim(0.08, 5000)
ax1.grid(axis='y', alpha=0.2)

# Add value labels
for bar, val in zip(bars1, z_8):
    if val > 0:
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height()*1.1,
                 f'{val:.0f}σ', ha='center', va='bottom', fontsize=8, color='#4ECDC4')
for bar, val in zip(bars2, z_13):
    if val > 0:
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height()*1.1,
                 f'{val:.1f}σ', ha='center', va='bottom', fontsize=8, color='#FF6B6B')

# ═══ Panel 2: Phase deviation comparison ═══
ax2 = fig.add_subplot(2, 2, 2)

# Only plot resonances with valid Δθ (exclude Higgs)
valid = [(l, d8, d13, m) for l, d8, d13, m in zip(labels, dt_8, dt_13, masses) if d8 is not None]
v_labels = [v[0] for v in valid]
v_dt8    = [v[1] for v in valid]
v_dt13   = [v[2] for v in valid]
v_masses = [v[3] for v in valid]

x2 = np.arange(len(v_labels))
bars3 = ax2.bar(x2 - width/2, v_dt8, width, label='8 TeV',
                color='#4ECDC4', alpha=0.85, edgecolor='white', linewidth=0.5)
bars4 = ax2.bar(x2 + width/2, v_dt13, width, label='13 TeV',
                color='#FF6B6B', alpha=0.85, edgecolor='white', linewidth=0.5)

ax2.set_ylabel('Δθ from π/4 [rad]', fontsize=13)
ax2.set_title('Attractor Alignment (closer = tighter)', fontsize=15, fontweight='bold')
ax2.set_xticks(x2)
ax2.set_xticklabels(v_labels, fontsize=12)
ax2.legend(fontsize=11)
ax2.axhline(y=0, color='cyan', linestyle='-', alpha=0.3)
ax2.grid(axis='y', alpha=0.2)

# ═══ Panel 3: Z vs Mass scatter ═══
ax3 = fig.add_subplot(2, 2, 3)

for i, (label, z8, z13, m) in enumerate(zip(labels[:-1], z_8[:-1], z_13[:-1], masses[:-1])):
    ax3.scatter(m, z8, s=120, color='#4ECDC4', marker='o', zorder=5, edgecolors='white', linewidth=0.5)
    ax3.scatter(m, z13, s=120, color='#FF6B6B', marker='s', zorder=5, edgecolors='white', linewidth=0.5)
    ax3.annotate(label, (m, max(z8, z13)*1.15), fontsize=9, ha='center', color='white')

# Draw connecting lines between 8 and 13 TeV for same resonance
for m, z8, z13 in zip(masses[:-1], z_8[:-1], z_13[:-1]):
    ax3.plot([m, m], [z8, z13], color='white', alpha=0.3, linewidth=1, linestyle=':')

ax3.set_xscale('log')
ax3.set_yscale('log')
ax3.set_xlabel('Resonance Mass [GeV]', fontsize=13)
ax3.set_ylabel('Z [σ]', fontsize=13)
ax3.set_title('Convergence vs Mass (log-log)', fontsize=15, fontweight='bold')
ax3.scatter([], [], color='#4ECDC4', marker='o', label='8 TeV', s=60)
ax3.scatter([], [], color='#FF6B6B', marker='s', label='13 TeV', s=60)
ax3.legend(fontsize=11, loc='lower right')
ax3.grid(alpha=0.2)

# ═══ Panel 4: Ratio plot (Z_13TeV / Z_8TeV scaled by event ratio) ═══
ax4 = fig.add_subplot(2, 2, 4)

# Scale by sqrt(N_events) since Z ~ √N for a fixed S/B
event_ratio = 6_358_636 / 53_300_000  # ~0.12
sqrt_ratio  = np.sqrt(event_ratio)    # ~0.35
# If convergence is energy-independent, Z_13 / Z_8 ≈ sqrt_ratio

scaled_ratios = []
for z8, z13 in zip(z_8[:-1], z_13[:-1]):
    # Normalize: (Z_13 / Z_8) / sqrt(N_13/N_8)
    ratio = (z13 / z8) / sqrt_ratio
    scaled_ratios.append(ratio)

x4 = np.arange(len(labels[:-1]))
bar_colors = ['#FF6B6B' if r > 0.8 else '#FFE66D' for r in scaled_ratios]
bars5 = ax4.bar(x4, scaled_ratios, 0.5, color=bar_colors, alpha=0.85,
                edgecolor='white', linewidth=0.5)
ax4.axhline(y=1.0, color='cyan', linestyle='--', alpha=0.6, linewidth=2,
            label='Perfect energy independence')
ax4.set_ylabel('Normalized Z ratio\n(Z₁₃/Z₈) / √(N₁₃/N₈)', fontsize=12)
ax4.set_title('Energy Independence Test', fontsize=15, fontweight='bold')
ax4.set_xticks(x4)
ax4.set_xticklabels(labels[:-1], fontsize=12)
ax4.legend(fontsize=10)
ax4.grid(axis='y', alpha=0.2)
ax4.set_ylim(0, 2.0)

for bar, val in zip(bars5, scaled_ratios):
    ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.03,
             f'{val:.2f}', ha='center', va='bottom', fontsize=11, fontweight='bold', color='white')

plt.tight_layout(rect=[0, 0, 1, 0.94])
outpath = os.path.join(OUTPUT_DIR, "acs_cross_energy_comparison.png")
plt.savefig(outpath, dpi=200, bbox_inches='tight', facecolor='#1a1a2e')
print(f"[viz] Saved: {outpath}")
plt.close()
print("Done.")

"""Generate Fig 6 (mass chain) and Fig 7 (contraction/geodesics) for paper."""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch

plt.rcParams.update({
    'font.family': 'serif',
    'font.size': 9,
    'axes.linewidth': 0.8,
    'figure.dpi': 300,
})

# ═══════════════════════════════════════════════════════════
# FIGURE 6: Geometric Mass Chain
# ═══════════════════════════════════════════════════════════

fig, ax = plt.subplots(figsize=(3.4, 2.8))

states = [
    (0.548, r'$\eta$', 'C2'),
    (0.783, r'$\omega$', 'C0'),
    (1.020, r'$\phi$', 'C0'),
    (3.097, r'$J/\psi$', 'C3'),
    (9.460, r'$\Upsilon$', 'C1'),
    (91.19, r'$Z$', 'C4'),
]

y_base = 0
for m, name, color in states:
    ax.plot([m, m], [y_base, y_base + 0.8], color=color, lw=2.5, solid_capstyle='round')
    ax.text(m, y_base + 0.95, name, ha='center', va='bottom', fontsize=8, fontweight='bold')

# Arrows for ratios
arrows = [
    (0.548, 0.783, r'$\times\sqrt{2}$', -0.3, 'C2'),
    (0.783, 1.020, r'$\times\frac{4}{3}$', -0.6, 'C5'),
    (0.783, 3.097, r'$\times 4$ (Tet V)', -1.0, 'C3'),
    (0.783, 9.460, r'$\times 12$ (Cube E)', -1.5, 'C1'),
    (3.774, 91.19, r'$\times 24$ ($|2T|$)', -2.0, 'C4'),
]

for m1, m2, label, y, color in arrows:
    ax.annotate('', xy=(m2, y), xytext=(m1, y),
                arrowprops=dict(arrowstyle='->', color=color, lw=1.2))
    mid = np.sqrt(m1 * m2)
    ax.text(mid, y + 0.12, label, ha='center', va='bottom', fontsize=6.5, color=color)

# Euler bridge
ax.annotate('', xy=(10.023, -2.5), xytext=(3.686, -2.5),
            arrowprops=dict(arrowstyle='->', color='C6', lw=1.2, linestyle='--'))
ax.text(np.sqrt(3.686*10.023), -2.35, r'$\psi(2S) \to \Upsilon(2S)$: $\times e$ (0.03%)',
        ha='center', va='bottom', fontsize=5.5, color='C6')

ax.set_xscale('log')
ax.set_xlabel('Mass [GeV]')
ax.set_xlim(0.3, 200)
ax.set_ylim(-3.0, 2.0)
ax.set_yticks([])
ax.spines['left'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

fig.tight_layout()
fig.savefig('paper/figures/fig6_mass_chain.pdf', bbox_inches='tight')
fig.savefig('paper/figures/fig6_mass_chain.png', dpi=300, bbox_inches='tight')
plt.close()
print('Fig 6 saved.')

# ═══════════════════════════════════════════════════════════
# FIGURE 7: Contraction + Geodesics (2 panels)
# ═══════════════════════════════════════════════════════════

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.0, 3.0))

# --- Left panel: Quarkonium contraction ---
# Bottomonium
bb_masses = np.array([9460.3, 10023.3, 10355.2, 10579.4])
bb_dm = np.diff(bb_masses)
bb_n = np.arange(1, len(bb_dm) + 1)

# Charmonium
cc_masses = np.array([3096.9, 3686.1, 3773.7])
cc_dm = np.diff(cc_masses)
cc_n = np.arange(1, len(cc_dm) + 1)

ax1.semilogy(bb_n, bb_dm, 'o-', color='C0', lw=1.5, ms=6, label=r'$b\bar{b}$ ($r=0.631$)')
ax1.semilogy(cc_n, cc_dm, 's-', color='C3', lw=1.5, ms=6, label=r'$c\bar{c}$ ($r=0.149$)')

# Geometric fits
r_bb = 0.631
r_cc = 0.149
n_fit = np.linspace(1, 4, 50)
ax1.semilogy(n_fit, bb_dm[0] * r_bb**(n_fit - 1), '--', color='C0', alpha=0.5, lw=1)
ax1.semilogy(n_fit, cc_dm[0] * r_cc**(n_fit - 1), '--', color='C3', alpha=0.5, lw=1)

# Threshold annotations
ax1.axhline(y=10, color='gray', ls=':', alpha=0.3)
ax1.text(3.5, 15, 'threshold', fontsize=6, color='gray', ha='right')

ax1.set_xlabel(r'Splitting index $n$')
ax1.set_ylabel(r'$\Delta m_n$ [MeV]')
ax1.set_xlim(0.5, 4.0)
ax1.set_ylim(30, 1000)
ax1.legend(fontsize=7, loc='upper right')
ax1.set_title('(a) Geometric contraction', fontsize=9)

# --- Right panel: Two geodesics ---
r = 0.631
dm0 = 563.0
ks = np.arange(0, 7)

short_path = dm0 * r**ks
long_path = dm0 * r**ks / (1 - r)

ax2.semilogy(ks, short_path, 'o-', color='C0', lw=1.5, ms=5,
             label=r'Short path $\Delta m \cdot r^k$')
ax2.semilogy(ks, long_path, 's-', color='C3', lw=1.5, ms=5,
             label=r'Long path $\Delta m \cdot r^k/(1{-}r)$')

# Fill between to show the ratio
ax2.fill_between(ks, short_path, long_path, alpha=0.1, color='C5')

# Annotate ratio
ax2.annotate(r'$\frac{dt}{d\tau} = \frac{1}{1-r} = 2.71 \approx e$',
             xy=(3, (short_path[3] + long_path[3])/2),
             fontsize=7, ha='center', va='center',
             bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow', edgecolor='gray', alpha=0.9))

# Horizon line
ax2.axhline(y=1, color='red', ls='--', alpha=0.5, lw=0.8)
ax2.text(6.3, 1.5, 'horizon', fontsize=6, color='red', ha='right')

ax2.set_xlabel(r'Koch iteration $k$')
ax2.set_ylabel('Path length [MeV]')
ax2.set_xlim(-0.3, 6.5)
ax2.legend(fontsize=6.5, loc='upper right')
ax2.set_title(r'(b) Koch geodesics ($b\bar{b}$)', fontsize=9)

fig.tight_layout()
fig.savefig('paper/figures/fig7_contraction.pdf', bbox_inches='tight')
fig.savefig('paper/figures/fig7_contraction.png', dpi=300, bbox_inches='tight')
plt.close()
print('Fig 7 saved.')
print('Done.')

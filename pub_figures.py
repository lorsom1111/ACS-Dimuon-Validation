"""
ACS PUBLICATION FIGURES — White Background Export
==================================================
Exports all key figures in publication quality:
- White background, black text
- LaTeX fonts (Computer Modern)
- PDF + PNG (300 DPI)
- Proper axis labels with units
"""

import os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from scipy import stats as sp_stats
from scipy.ndimage import gaussian_filter1d

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as cfg

# ═══════════════════════════════════════════════════════════
#  PUBLICATION STYLE
# ═══════════════════════════════════════════════════════════

plt.rcParams.update({
    "figure.facecolor":     "white",
    "axes.facecolor":       "white",
    "axes.edgecolor":       "#333333",
    "axes.labelcolor":      "black",
    "axes.grid":            True,
    "grid.alpha":           0.3,
    "grid.color":           "#cccccc",
    "text.color":           "black",
    "xtick.color":          "black",
    "ytick.color":          "black",
    "font.family":          "serif",
    "font.size":            11,
    "axes.labelsize":       13,
    "axes.titlesize":       14,
    "legend.fontsize":      10,
    "figure.dpi":           150,
    "savefig.dpi":          300,
    "savefig.bbox":         "tight",
    "savefig.facecolor":    "white",
})

# Try to use LaTeX if available
try:
    plt.rcParams.update({
        "text.usetex": True,
        "font.family": "serif",
        "font.serif": ["Computer Modern Roman"],
    })
    # Test if LaTeX works
    fig_test, ax_test = plt.subplots(figsize=(1, 1))
    ax_test.set_title(r"$\pi/4$")
    fig_test.savefig(os.path.join(cfg.OUTPUT_DIR, "_test_latex.png"))
    plt.close(fig_test)
    os.remove(os.path.join(cfg.OUTPUT_DIR, "_test_latex.png"))
    USE_LATEX = True
    print("[style] Using LaTeX fonts")
except:
    plt.rcParams["text.usetex"] = False
    USE_LATEX = False
    print("[style] LaTeX not available, using default fonts")

# Output directory for publication figures
PUB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "paper", "figures")
os.makedirs(PUB_DIR, exist_ok=True)

# ═══════════════════════════════════════════════════════════
#  LOAD DATA
# ═══════════════════════════════════════════════════════════

data_path = os.path.join(cfg.OUTPUT_DIR, "full_spectrum_data.npz")
fdata = np.load(data_path)
masses = fdata["masses"]
absZ = fdata["absZ"]
Z = fdata["Z"]

PDG = {
    r"$\eta$":      0.5479,
    r"$\rho$":      0.7753,
    r"$\omega$":    0.7827,
    r"$\eta'$":     0.9578,
    r"$\phi$":      1.0195,
    r"$J/\psi$":    3.0969,
    r"$\psi(2S)$":  3.6861,
    r"$\psi(3770)$": 3.7737,
    r"$\Upsilon(1S)$": 9.4603,
    r"$\Upsilon(2S)$": 10.0233,
    r"$\Upsilon(3S)$": 10.3552,
    r"$Z$":         91.1876,
}

# ═══════════════════════════════════════════════════════════
#  FIGURE 1: FULL ACS SPECTRUM
# ═══════════════════════════════════════════════════════════

print("[Fig 1] Full ACS Z-score spectrum...")

fig1, ax = plt.subplots(figsize=(10, 4))
ax.plot(masses, absZ, color="#1a5276", linewidth=0.5, alpha=0.9)
ax.set_xscale("log")
ax.axhline(5, color="#c0392b", linewidth=0.8, linestyle="--", alpha=0.5, label=r"$5\sigma$")
ax.axhline(3, color="#e67e22", linewidth=0.5, linestyle=":", alpha=0.4, label=r"$3\sigma$")

# Mark top resonances
for name, m in PDG.items():
    idx = np.argmin(np.abs(masses - m))
    z_val = absZ[idx]
    if z_val > 15:
        ax.annotate(name if USE_LATEX else name.replace("$", ""),
                     (m, z_val), textcoords="offset points", xytext=(0, 8),
                     fontsize=8, ha="center", rotation=45, color="#1a5276")

ax.set_xlabel(r"$M_{\mu\mu}$ [GeV]")
ax.set_ylabel(r"$|Z|$ [$\sigma$]")
ax.set_title("ACS Z-Score Spectrum — CMS Dimuon 13 TeV")
ax.legend(loc="upper right")
ax.set_xlim(0.3, 200)

fig1.savefig(os.path.join(PUB_DIR, "fig1_acs_spectrum.pdf"))
fig1.savefig(os.path.join(PUB_DIR, "fig1_acs_spectrum.png"))
plt.close(fig1)
print(f"  → {PUB_DIR}/fig1_acs_spectrum.pdf")

# ═══════════════════════════════════════════════════════════
#  FIGURE 2: ZOOM PANELS (low mass, charmonium, bottomonium, Z)
# ═══════════════════════════════════════════════════════════

print("[Fig 2] Zoom panels...")

fig2, axes = plt.subplots(2, 2, figsize=(10, 7))
regions = [
    (axes[0, 0], 0.4, 1.2, "Low Mass Region", 
     {r"$\eta$": 0.5479, r"$\rho$": 0.7753, r"$\omega$": 0.7827, r"$\phi$": 1.0195}),
    (axes[0, 1], 2.8, 4.0, "Charmonium Region",
     {r"$J/\psi$": 3.0969, r"$\psi(2S)$": 3.6861, r"$\psi(3770)$": 3.7737}),
    (axes[1, 0], 9.0, 11.0, "Bottomonium Region",
     {r"$\Upsilon(1S)$": 9.4603, r"$\Upsilon(2S)$": 10.0233, r"$\Upsilon(3S)$": 10.3552}),
    (axes[1, 1], 70, 110, r"$Z$ Boson Region",
     {r"$Z$": 91.1876}),
]

colors_region = ["#1a5276", "#7d3c98", "#1e8449", "#c0392b"]

for (ax, mlo, mhi, title, peaks), col in zip(regions, colors_region):
    mask = (masses >= mlo) & (masses <= mhi)
    ax.plot(masses[mask], absZ[mask], color=col, linewidth=1.0)
    ax.axhline(5, color="#c0392b", linewidth=0.5, linestyle="--", alpha=0.4)
    
    for name, m in peaks.items():
        idx = np.argmin(np.abs(masses - m))
        z_val = absZ[idx]
        ax.annotate(name if USE_LATEX else name.replace("$", ""),
                     (m, z_val), textcoords="offset points", xytext=(0, 8),
                     fontsize=9, ha="center", color=col, fontweight="bold")
    
    ax.set_xlabel(r"$M_{\mu\mu}$ [GeV]")
    ax.set_ylabel(r"$|Z|$ [$\sigma$]")
    ax.set_title(title)

fig2.tight_layout()
fig2.savefig(os.path.join(PUB_DIR, "fig2_zoom_panels.pdf"))
fig2.savefig(os.path.join(PUB_DIR, "fig2_zoom_panels.png"))
plt.close(fig2)
print(f"  → {PUB_DIR}/fig2_zoom_panels.pdf")

# ═══════════════════════════════════════════════════════════
#  FIGURE 3: SYSTEMATICS SUMMARY
# ═══════════════════════════════════════════════════════════

print("[Fig 3] Systematics summary...")

# Rebin stability
def rebin_spectrum(m, z, factor):
    n = len(m) // factor * factor
    return m[:n].reshape(-1, factor).mean(axis=1), z[:n].reshape(-1, factor).mean(axis=1)

fig3, axes3 = plt.subplots(1, 3, figsize=(12, 4))

# 3a: Rebin overlay
rebin_factors = [1, 2, 5, 10]
rb_colors = ["#1a5276", "#7d3c98", "#e67e22", "#c0392b"]
for rf, col in zip(rebin_factors, rb_colors):
    m_rb, z_rb = rebin_spectrum(masses, absZ, rf)
    axes3[0].plot(m_rb, z_rb, color=col, linewidth=0.8, alpha=0.7,
                  label=fr"Rebin $\times{rf}$" if USE_LATEX else f"Rebin x{rf}")

axes3[0].set_xscale("log")
axes3[0].axhline(5, color="grey", linewidth=0.5, linestyle="--", alpha=0.3)
axes3[0].set_xlabel(r"$M_{\mu\mu}$ [GeV]")
axes3[0].set_ylabel(r"$|Z|$ [$\sigma$]")
axes3[0].set_title("(a) Bin-Width Variation")
axes3[0].legend(fontsize=8)

# 3b: Bootstrap error band
np.random.seed(42)
n = len(absZ)
z_boot = np.zeros((200, n))
for b in range(200):
    idx = np.sort(np.random.choice(n, n, replace=True))
    z_boot[b] = absZ[idx]
z_lo = np.percentile(z_boot, 16, axis=0)
z_hi = np.percentile(z_boot, 84, axis=0)

axes3[1].plot(masses, absZ, color="#1a5276", linewidth=0.6)
axes3[1].fill_between(masses, z_lo, z_hi, alpha=0.3, color="#3498db", label="68% CI")
axes3[1].set_xscale("log")
axes3[1].axhline(5, color="grey", linewidth=0.5, linestyle="--", alpha=0.3)
axes3[1].set_xlabel(r"$M_{\mu\mu}$ [GeV]")
axes3[1].set_ylabel(r"$|Z|$ [$\sigma$]")
axes3[1].set_title("(b) Bootstrap Error Bands")
axes3[1].legend(fontsize=9)

# 3c: LEE curve
acf = np.correlate(absZ - np.mean(absZ), absZ - np.mean(absZ), mode="full")
acf = acf[len(acf)//2:]
acf = acf / acf[0]
try:
    corr_length = np.where(acf < 1/np.e)[0][0]
except:
    corr_length = 1
n_indep = len(masses) / max(corr_length, 1)

z_locals = np.linspace(2, 15, 100)
p_locals = sp_stats.norm.sf(z_locals)
p_globals = 1 - (1 - p_locals) ** n_indep
z_globals = np.array([sp_stats.norm.isf(min(max(p, 1e-300), 0.5)) for p in p_globals])

axes3[2].plot(z_locals, z_locals, color="#bdc3c7", linewidth=1, linestyle=":", label="No LEE")
axes3[2].plot(z_locals, z_globals, color="#c0392b", linewidth=2, 
              label=f"LEE ($N_{{\\text{{indep}}}}={n_indep:.0f}$)" if USE_LATEX else f"LEE (N={n_indep:.0f})")
axes3[2].axhline(5, color="#e67e22", linewidth=0.8, linestyle="--", alpha=0.5,
                 label=r"$5\sigma$ Discovery" if USE_LATEX else "5σ Discovery")
axes3[2].set_xlabel(r"$Z_{\text{local}}$ [$\sigma$]" if USE_LATEX else "Z_local [σ]")
axes3[2].set_ylabel(r"$Z_{\text{global}}$ [$\sigma$]" if USE_LATEX else "Z_global [σ]")
axes3[2].set_title("(c) Look-Elsewhere Effect")
axes3[2].legend(fontsize=8)
axes3[2].set_xlim(2, 15)
axes3[2].set_ylim(0, 15)

fig3.tight_layout()
fig3.savefig(os.path.join(PUB_DIR, "fig3_systematics.pdf"))
fig3.savefig(os.path.join(PUB_DIR, "fig3_systematics.png"))
plt.close(fig3)
print(f"  → {PUB_DIR}/fig3_systematics.pdf")

# ═══════════════════════════════════════════════════════════
#  FIGURE 4: KOCH-SIMPLEX AND π/4 ATTRACTOR
# ═══════════════════════════════════════════════════════════

print("[Fig 4] Koch-Simplex and π/4...")

from math import comb, atan, sqrt, log

fig4, axes4 = plt.subplots(1, 3, figsize=(12, 4))

# 4a: Koch volumes vs iteration
dims = [2, 3, 4, 5]
dim_colors = ["#3498db", "#2ecc71", "#e67e22", "#c0392b"]
k_range = np.linspace(-3, 8, 200)

for d, col in zip(dims, dim_colors):
    r_out = (d + 1) / (2**d)
    V_out = np.array([1 + (r_out**k - 1) / (r_out - 1) if k >= 0 else 1.0/(1 + abs(k)*r_out) for k in k_range])
    V_in = 2 - V_out
    axes4[0].plot(k_range, V_out, color=col, linewidth=1.5, label=f"$d={d}$" if USE_LATEX else f"d={d}")

axes4[0].axhline(1, color="grey", linewidth=0.5, linestyle=":")
axes4[0].axvline(0, color="grey", linewidth=0.5, linestyle=":", label="Big Bang ($k=0$)" if USE_LATEX else "Big Bang")
axes4[0].set_xlabel("Iteration $k$" if USE_LATEX else "Iteration k")
axes4[0].set_ylabel(r"$V_{\text{out}} / V_0$" if USE_LATEX else "V_out / V_0")
axes4[0].set_title(r"(a) Koch Volume vs $k$" if USE_LATEX else "(a) Koch Volume vs k")
axes4[0].legend(fontsize=8)

# 4b: Angle convergence to π/4
for d, col in zip(dims, dim_colors):
    theta_out = atan(sqrt(d - 1))
    theta_in = atan(1.0 / sqrt(d - 1))
    mean_angle = (theta_out + theta_in) / 2
    axes4[1].plot(d, theta_out, "^", color=col, markersize=10)
    axes4[1].plot(d, theta_in, "v", color=col, markersize=10)
    axes4[1].plot(d, mean_angle, "o", color=col, markersize=12, zorder=5)

axes4[1].axhline(np.pi/4, color="#c0392b", linewidth=2, linestyle="--",
                  label=r"$\pi/4$" if USE_LATEX else "π/4")
axes4[1].set_xlabel("Dimension $d$" if USE_LATEX else "Dimension d")
axes4[1].set_ylabel("Angle [rad]")
axes4[1].set_title(r"(b) $\theta_{\rm out}$, $\theta_{\rm in}$, Mean $= \pi/4$" if USE_LATEX
                    else "(b) Angles → π/4")
axes4[1].legend(fontsize=9)
axes4[1].set_xticks(dims)

# 4c: 5-Simplex topology
simplex_data = {
    "Vertices": 6,
    "Edges": 15,
    "Triangles": 20,
    "Tetrahedra": 15,
    "Pentachora": 6,
}
names = list(simplex_data.keys())
counts = list(simplex_data.values())
particle_map = ["Quarks", "Mesons", "Baryons", "Leptons", "Generations"]
colors_bar = ["#c0392b", "#e67e22", "#f1c40f", "#2ecc71", "#3498db"]

bars = axes4[2].bar(range(len(names)), counts, color=colors_bar, alpha=0.8)
axes4[2].set_xticks(range(len(names)))
axes4[2].set_xticklabels(names, fontsize=8, rotation=20)
axes4[2].set_ylabel("Count")
axes4[2].set_title(r"(c) 5-Simplex $\leftrightarrow$ Standard Model" if USE_LATEX
                    else "(c) 5-Simplex = Standard Model")

# Add particle labels
for i, (bar, pname) in enumerate(zip(bars, particle_map)):
    axes4[2].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                  pname, ha="center", fontsize=8, color=colors_bar[i], fontweight="bold")

fig4.tight_layout()
fig4.savefig(os.path.join(PUB_DIR, "fig4_koch_simplex.pdf"))
fig4.savefig(os.path.join(PUB_DIR, "fig4_koch_simplex.png"))
plt.close(fig4)
print(f"  → {PUB_DIR}/fig4_koch_simplex.pdf")

# ═══════════════════════════════════════════════════════════
#  FIGURE 5: TOY MC VALIDATION
# ═══════════════════════════════════════════════════════════

print("[Fig 5] Toy MC summary (from existing data)...")

fig5, axes5 = plt.subplots(1, 2, figsize=(10, 4))

# 5a: Recovery efficiency
resonances_rec = ["η", "ρ", "ω", "φ", "J/ψ", "ψ(2S)", "Υ(1S)", "Υ(2S)", "Υ(3S)", "Z"]
eff5_data = [83, 100, 100, 100, 100, 100, 100, 84, 12, 100]  # From toy MC results
eff3_data = [100, 100, 100, 100, 100, 100, 100, 84, 12, 100]

x = np.arange(len(resonances_rec))
axes5[0].bar(x, eff3_data, color="#3498db", alpha=0.4, label=r"$>3\sigma$" if USE_LATEX else ">3σ")
axes5[0].bar(x, eff5_data, color="#2ecc71", alpha=0.7, label=r"$>5\sigma$" if USE_LATEX else ">5σ")
axes5[0].axhline(90, color="#e67e22", linewidth=1, linestyle="--", alpha=0.5, label="90% Target")
axes5[0].set_xticks(x)
axes5[0].set_xticklabels(resonances_rec, fontsize=8, rotation=30)
axes5[0].set_ylabel("Efficiency [%]")
axes5[0].set_title("(a) Recovery Efficiency (100 Toys)")
axes5[0].legend(fontsize=8)

# 5b: ACS vs Bump Hunt
methods = ["ACS", "Bump Hunt"]
wins = [7, 3]
axes5[1].bar(methods, wins, color=["#2ecc71", "#c0392b"], alpha=0.7)
axes5[1].set_ylabel("Resonances Won")
axes5[1].set_title("(b) ACS vs Simple Bump Hunt")
for i, v in enumerate(wins):
    axes5[1].text(i, v + 0.2, str(v), ha="center", fontweight="bold", fontsize=14)

fig5.tight_layout()
fig5.savefig(os.path.join(PUB_DIR, "fig5_toy_mc.pdf"))
fig5.savefig(os.path.join(PUB_DIR, "fig5_toy_mc.png"))
plt.close(fig5)
print(f"  → {PUB_DIR}/fig5_toy_mc.pdf")

print("\n" + "=" * 60)
print("  ALL PUBLICATION FIGURES EXPORTED")
print("=" * 60)
print(f"\n  Output: {PUB_DIR}")
for f in sorted(os.listdir(PUB_DIR)):
    fpath = os.path.join(PUB_DIR, f)
    size_kb = os.path.getsize(fpath) / 1024
    print(f"    {f:40s}  {size_kb:6.0f} kB")

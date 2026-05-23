"""
ACS MASS RESOLUTION & PEAK SEPARATION ANALYSIS
================================================
Quantifies the mass resolution and peak-separation capability of the
Asymmetric Convergence Sequence (ACS) method applied to CMS dimuon data.

Analyses performed:
  1. Gaussian fits to each detected resonance → σ_mass
  2. Close-pair separation (ω/ρ, Υ family, ψ family)
  3. Rayleigh criterion check for neighbouring peaks
  4. Relative resolution (σ_mass / M) vs M
  5. Detector + natural width convolution model
  6. Comprehensive 6-panel visualisation

Author : ACS-CERN pipeline
Data   : full_spectrum_data.npz from ACS full-spectrum blind scan
"""

import os
import sys
import numpy as np
from scipy.optimize import curve_fit
from scipy.signal import find_peaks
from scipy.interpolate import interp1d

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as cfg

# ═══════════════════════════════════════════════════════════
#  CONFIGURATION
# ═══════════════════════════════════════════════════════════

DATA_FILE = os.path.join(cfg.OUTPUT_DIR, "full_spectrum_data.npz")
OUT_PLOT  = os.path.join(cfg.OUTPUT_DIR, "acs_resolution_limit.png")

# PDG resonances to analyse  {name: (mass_GeV, natural_width_GeV)}
PDG_RESONANCES = {
    "η(548)":    (0.5479,  1.31e-6),
    "ρ(770)":    (0.7753,  0.1491),
    "ω(782)":    (0.7827,  8.68e-3),
    "φ(1020)":   (1.0195,  4.249e-3),
    "J/ψ":       (3.0969,  92.9e-6),
    "ψ(2S)":     (3.6861,  294e-6),
    "ψ(3770)":   (3.7737,  27.2e-3),
    "Υ(1S)":     (9.4603,  54.02e-6),
    "Υ(2S)":    (10.0233,  31.98e-6),
    "Υ(3S)":    (10.3552,  20.32e-6),
    "Z":        (91.1876,  2.4952),
}

# Close pairs to test separation
CLOSE_PAIRS = [
    ("ρ(770)",  "ω(782)",   "ρ/ω doublet"),
    ("ψ(2S)",   "ψ(3770)",  "ψ family"),
    ("Υ(1S)",   "Υ(2S)",    "Υ(1S–2S)"),
    ("Υ(2S)",   "Υ(3S)",    "Υ(2S–3S)"),
    ("J/ψ",     "ψ(2S)",    "J/ψ – ψ(2S)"),
]

# ═══════════════════════════════════════════════════════════
#  LOAD DATA
# ═══════════════════════════════════════════════════════════

print("=" * 80)
print("  ACS MASS RESOLUTION & PEAK SEPARATION ANALYSIS")
print("=" * 80)

if not os.path.exists(DATA_FILE):
    print(f"\n[ERROR] Data file not found: {DATA_FILE}")
    print("        Run full_spectrum.py first to generate the scan data.")
    sys.exit(1)

data = np.load(DATA_FILE)
masses = data["masses"]       # mass sweep grid [GeV]
Z      = data["Z"]            # signed Z-scores
absZ   = data["absZ"]         # |Z| scores

print(f"\n[data] Loaded {len(masses)} mass points: "
      f"{masses[0]:.3f} – {masses[-1]:.3f} GeV")
print(f"[data] Max |Z| = {absZ.max():.1f}σ at M = {masses[np.argmax(absZ)]:.4f} GeV")


# ═══════════════════════════════════════════════════════════
#  1. GAUSSIAN FITS → σ_mass FOR EACH RESONANCE
# ═══════════════════════════════════════════════════════════

def gaussian(x, A, mu, sigma, C):
    """Gaussian + constant baseline."""
    return A * np.exp(-0.5 * ((x - mu) / sigma) ** 2) + C


def fit_resonance(masses, absZ, m_pdg, name, fit_half_width=None):
    """
    Fit a Gaussian to the |Z| peak near m_pdg.
    Returns dict with fit results or None on failure.
    """
    # Adaptive fit window based on mass
    if fit_half_width is None:
        if m_pdg < 2:
            fit_half_width = 0.08
        elif m_pdg < 5:
            fit_half_width = 0.20
        elif m_pdg < 15:
            fit_half_width = 0.40
        else:
            fit_half_width = 8.0

    mask = (masses >= m_pdg - fit_half_width) & (masses <= m_pdg + fit_half_width)
    x = masses[mask]
    y = absZ[mask]

    if len(x) < 5:
        return None

    # Initial guesses
    idx_peak = np.argmax(y)
    A0 = y[idx_peak]
    mu0 = x[idx_peak]
    sig0 = fit_half_width * 0.3
    C0 = np.percentile(y, 10)

    if A0 < 3.0:  # skip sub-3σ peaks
        return None

    try:
        popt, pcov = curve_fit(
            gaussian, x, y,
            p0=[A0, mu0, sig0, C0],
            bounds=([0, m_pdg - fit_half_width, 1e-5, 0],
                    [A0 * 3, m_pdg + fit_half_width, fit_half_width, A0]),
            maxfev=5000
        )
        perr = np.sqrt(np.diag(pcov))
        A, mu, sigma, C = popt
        sigma = abs(sigma)

        # Residual χ²
        y_fit = gaussian(x, *popt)
        chi2 = np.sum((y - y_fit) ** 2) / max(len(x) - 4, 1)

        return {
            "name": name,
            "m_pdg": m_pdg,
            "A": A, "mu": mu, "sigma": sigma, "C": C,
            "A_err": perr[0], "mu_err": perr[1], "sigma_err": perr[2],
            "chi2_red": chi2,
            "x_fit": x, "y_fit": y_fit, "y_data": y,
            "FWHM": 2.355 * sigma,
            "rel_resolution": sigma / mu,
        }
    except (RuntimeError, ValueError):
        return None


print("\n" + "─" * 90)
print("  GAUSSIAN PEAK FITS — σ_mass FOR EACH RESONANCE")
print("─" * 90)
print(f"\n  {'Resonance':<12s} {'M_PDG':>10s} {'M_fit':>10s} {'σ_mass':>10s} "
      f"{'FWHM':>10s} {'σ/M':>10s} {'|Z|_peak':>10s} {'χ²/ndf':>8s}")
print("  " + "─" * 82)

fit_results = {}
for name, (m_pdg, gamma) in PDG_RESONANCES.items():
    result = fit_resonance(masses, absZ, m_pdg, name)
    if result is not None:
        fit_results[name] = result
        r = result
        print(f"  {name:<12s} {m_pdg:>10.4f} {r['mu']:>10.4f} "
              f"{r['sigma']*1e3:>8.1f} MeV {r['FWHM']*1e3:>8.1f} MeV "
              f"{r['rel_resolution']:>10.4f} {r['A']:>10.1f} {r['chi2_red']:>8.2f}")
    else:
        print(f"  {name:<12s} {m_pdg:>10.4f}    — fit failed or sub-threshold —")


# ═══════════════════════════════════════════════════════════
#  2. PEAK SEPARATION — CLOSE PAIRS
# ═══════════════════════════════════════════════════════════

print("\n\n" + "─" * 100)
print("  PEAK SEPARATION — CLOSE DOUBLETS")
print("─" * 100)
print(f"\n  {'Pair':<18s} {'Δm [MeV]':>10s} {'σ₁ [MeV]':>10s} {'σ₂ [MeV]':>10s} "
      f"{'Δm/σ_avg':>10s} {'Resolved?':>12s} {'Rayleigh?':>12s}")
print("  " + "─" * 88)

separation_results = []
for name1, name2, label in CLOSE_PAIRS:
    m1 = PDG_RESONANCES[name1][0]
    m2 = PDG_RESONANCES[name2][0]
    delta_m = abs(m2 - m1) * 1e3  # MeV

    sig1 = fit_results[name1]["sigma"] * 1e3 if name1 in fit_results else None
    sig2 = fit_results[name2]["sigma"] * 1e3 if name2 in fit_results else None

    # Check Rayleigh criterion: dip between peaks > 0.81 × min(peak heights)
    mask_between = (masses >= min(m1, m2)) & (masses <= max(m1, m2))
    if mask_between.sum() > 2:
        z_between = absZ[mask_between]
        idx1 = np.argmin(np.abs(masses - m1))
        idx2 = np.argmin(np.abs(masses - m2))
        z_peak1 = absZ[idx1]
        z_peak2 = absZ[idx2]
        z_min_between = z_between.min()
        rayleigh_threshold = 0.81 * min(z_peak1, z_peak2)
        rayleigh_ok = z_min_between < rayleigh_threshold  # dip below 81%
    else:
        rayleigh_ok = False
        z_min_between = 0
        rayleigh_threshold = 0

    if sig1 is not None and sig2 is not None:
        sigma_avg = (sig1 + sig2) / 2
        separation_ratio = delta_m / sigma_avg
        resolved = separation_ratio > 2.0  # Rayleigh-like criterion in σ
    else:
        sigma_avg = None
        separation_ratio = None
        resolved = None

    sep_str = f"{separation_ratio:.2f}" if separation_ratio else "  —"
    res_str = "✅ YES" if resolved else ("✗ NO" if resolved is not None else "  —")
    ray_str = "✅ YES" if rayleigh_ok else "✗ NO"

    sig1_str = f"{sig1:.1f}" if sig1 else "  —"
    sig2_str = f"{sig2:.1f}" if sig2 else "  —"

    print(f"  {label:<18s} {delta_m:>10.1f} {sig1_str:>10s} {sig2_str:>10s} "
          f"{sep_str:>10s} {res_str:>12s} {ray_str:>12s}")

    separation_results.append({
        "label": label, "name1": name1, "name2": name2,
        "m1": m1, "m2": m2, "delta_m_mev": delta_m,
        "sig1_mev": sig1, "sig2_mev": sig2,
        "sep_ratio": separation_ratio, "resolved": resolved,
        "rayleigh": rayleigh_ok, "z_dip": z_min_between,
        "rayleigh_thresh": rayleigh_threshold,
    })


# ═══════════════════════════════════════════════════════════
#  3. RAYLEIGH CRITERION — ALL NEIGHBOURING PEAKS
# ═══════════════════════════════════════════════════════════

print("\n\n" + "─" * 100)
print("  RAYLEIGH CRITERION — ALL CONSECUTIVE PEAK PAIRS")
print("─" * 100)

# Find all peaks in the |Z| spectrum
all_peak_idx, all_peak_props = find_peaks(absZ, height=5.0, distance=5, prominence=2.0)
all_peak_masses = masses[all_peak_idx]
all_peak_z = absZ[all_peak_idx]

# Sort by mass
sort_order = np.argsort(all_peak_masses)
all_peak_idx = all_peak_idx[sort_order]
all_peak_masses = all_peak_masses[sort_order]
all_peak_z = all_peak_z[sort_order]

print(f"\n  Found {len(all_peak_idx)} peaks above 5σ\n")
print(f"  {'Peak 1':<14s} {'M₁ [GeV]':>10s} {'Peak 2':<14s} {'M₂ [GeV]':>10s} "
      f"{'Δm [MeV]':>10s} {'Z_dip':>8s} {'0.81×Z_min':>10s} {'Rayleigh':>10s}")
print("  " + "─" * 90)

rayleigh_results = []
for i in range(len(all_peak_idx) - 1):
    idx1, idx2 = all_peak_idx[i], all_peak_idx[i + 1]
    m1, m2 = masses[idx1], masses[idx2]
    z1, z2 = absZ[idx1], absZ[idx2]

    # Find minimum |Z| between the two peaks
    between_mask = (np.arange(len(masses)) > idx1) & (np.arange(len(masses)) < idx2)
    if between_mask.sum() > 0:
        z_dip = absZ[between_mask].min()
    else:
        z_dip = min(z1, z2)

    threshold = 0.81 * min(z1, z2)
    rayleigh_satisfied = z_dip < threshold

    # Find nearest PDG names
    def nearest_pdg(m):
        best_name, best_dist = "???", 999
        for pn, (pm, _) in PDG_RESONANCES.items():
            d = abs(m - pm)
            if d < best_dist:
                best_dist = d
                best_name = pn
        return best_name if best_dist < m * 0.1 else f"{m:.3f}"

    n1 = nearest_pdg(m1)
    n2 = nearest_pdg(m2)
    delta = (m2 - m1) * 1e3

    ray_str = "✅ YES" if rayleigh_satisfied else "✗ NO"
    print(f"  {n1:<14s} {m1:>10.4f} {n2:<14s} {m2:>10.4f} "
          f"{delta:>10.1f} {z_dip:>8.1f} {threshold:>10.1f} {ray_str:>10s}")

    rayleigh_results.append({
        "name1": n1, "name2": n2, "m1": m1, "m2": m2,
        "delta_mev": delta, "z_dip": z_dip, "threshold": threshold,
        "rayleigh": rayleigh_satisfied,
    })


# ═══════════════════════════════════════════════════════════
#  4. DETECTOR RESOLUTION MODEL
# ═══════════════════════════════════════════════════════════

print("\n\n" + "─" * 80)
print("  DETECTOR RESOLUTION MODEL")
print("─" * 80)

# CMS dimuon mass resolution model (approximate):
#   σ_det(m) ≈ a × m + b × m²
# where a ~ 0.01 (1% from multiple scattering at low mass)
#       b ~ 5e-5 (curvature measurement at high mass)
# Plus natural width convolved in quadrature:
#   σ_meas² = σ_det² + (Γ/2.355)²

def cms_resolution_model(m, a=0.01, b=5e-5):
    """Approximate CMS dimuon mass resolution (σ in GeV)."""
    return a * m + b * m ** 2


def convolved_width(m, gamma, a=0.01, b=5e-5):
    """Total measured width = sqrt(σ_det² + σ_natural²)."""
    sigma_det = cms_resolution_model(m, a, b)
    sigma_nat = gamma / 2.355  # convert FWHM-like Γ to σ
    return np.sqrt(sigma_det ** 2 + sigma_nat ** 2)


# Fit the detector model to measured σ values (excluding naturally broad ρ, Z)
narrow_peaks = [n for n in fit_results
                if n not in ("ρ(770)", "Z", "ψ(3770)")]  # exclude broad states

if len(narrow_peaks) >= 2:
    fit_m = np.array([fit_results[n]["mu"] for n in narrow_peaks])
    fit_s = np.array([fit_results[n]["sigma"] for n in narrow_peaks])
    fit_g = np.array([PDG_RESONANCES[n][1] for n in narrow_peaks])

    # Remove natural width contribution
    sigma_det_meas = np.sqrt(np.maximum(fit_s ** 2 - (fit_g / 2.355) ** 2, fit_s ** 2 * 0.9))

    try:
        popt_det, _ = curve_fit(
            cms_resolution_model, fit_m, sigma_det_meas,
            p0=[0.01, 5e-5], bounds=([0, 0], [0.1, 1e-3])
        )
        a_fit, b_fit = popt_det
        print(f"\n  Fitted detector model: σ_det = {a_fit:.4f}×M + {b_fit:.2e}×M²")
        print(f"  (a = {a_fit*100:.2f}% linear, b = {b_fit*1e6:.1f} ppm quadratic)")
        det_model_ok = True
    except RuntimeError:
        a_fit, b_fit = 0.01, 5e-5
        print(f"\n  Using default model: σ_det = 0.01×M + 5e-5×M²")
        det_model_ok = False
else:
    a_fit, b_fit = 0.01, 5e-5
    det_model_ok = False
    print(f"\n  Too few narrow peaks for fit. Using default model.")


print(f"\n  {'Resonance':<12s} {'σ_meas':>10s} {'σ_det(model)':>12s} "
      f"{'Γ_nat/2.355':>12s} {'σ_conv':>10s} {'σ_m/σ_c':>8s}")
print("  " + "─" * 70)

for name, (m_pdg, gamma) in PDG_RESONANCES.items():
    sigma_det = cms_resolution_model(m_pdg, a_fit, b_fit)
    sigma_nat = gamma / 2.355
    sigma_conv = np.sqrt(sigma_det ** 2 + sigma_nat ** 2)

    if name in fit_results:
        sigma_meas = fit_results[name]["sigma"]
        ratio = sigma_meas / sigma_conv if sigma_conv > 0 else 0
        print(f"  {name:<12s} {sigma_meas*1e3:>8.1f} MeV {sigma_det*1e3:>10.1f} MeV "
              f"{sigma_nat*1e3:>10.1f} MeV {sigma_conv*1e3:>8.1f} MeV {ratio:>8.2f}")
    else:
        print(f"  {name:<12s}      — MeV {sigma_det*1e3:>10.1f} MeV "
              f"{sigma_nat*1e3:>10.1f} MeV {sigma_conv*1e3:>8.1f} MeV    —")


# ═══════════════════════════════════════════════════════════
#  5. SUMMARY TABLE
# ═══════════════════════════════════════════════════════════

print("\n\n" + "═" * 80)
print("  RESOLUTION SUMMARY")
print("═" * 80)

if fit_results:
    masses_fit = np.array([fit_results[n]["mu"] for n in fit_results])
    sigmas_fit = np.array([fit_results[n]["sigma"] for n in fit_results])
    rel_res = sigmas_fit / masses_fit

    print(f"\n  Best relative resolution:  σ/M = {rel_res.min():.4f} "
          f"({list(fit_results.keys())[np.argmin(rel_res)]})")
    print(f"  Worst relative resolution: σ/M = {rel_res.max():.4f} "
          f"({list(fit_results.keys())[np.argmax(rel_res)]})")
    print(f"  Median relative resolution: σ/M = {np.median(rel_res):.4f}")

n_rayleigh_pass = sum(1 for r in rayleigh_results if r["rayleigh"])
print(f"\n  Rayleigh-resolved pairs: {n_rayleigh_pass} / {len(rayleigh_results)}")
n_sep_pass = sum(1 for s in separation_results if s["resolved"])
n_sep_total = sum(1 for s in separation_results if s["resolved"] is not None)
print(f"  Close-pair separated:    {n_sep_pass} / {n_sep_total}")


# ═══════════════════════════════════════════════════════════
#  6. VISUALIZATION — 6-PANEL FIGURE
# ═══════════════════════════════════════════════════════════

print("\n[viz] Generating 6-panel resolution figure...")

plt.rcParams.update({
    "figure.facecolor": "#0a0a0f",
    "axes.facecolor":   "#0d0d15",
    "axes.edgecolor":   "#333355",
    "axes.labelcolor":  "#ccccee",
    "text.color":       "#ccccee",
    "xtick.color":      "#8888aa",
    "ytick.color":      "#8888aa",
    "font.family":      "monospace",
    "grid.color":       "#222244",
    "grid.alpha":       0.3,
})

fig = plt.figure(figsize=(22, 28))
gs = fig.add_gridspec(3, 2, hspace=0.32, wspace=0.28,
                      left=0.07, right=0.97, top=0.94, bottom=0.04)

fig.suptitle(
    "ACS MASS RESOLUTION & PEAK SEPARATION ANALYSIS\n"
    "CMS dimuon data — Asymmetric Convergence Sequence method",
    fontsize=17, fontweight="bold", color="white", y=0.975)

# ─── Panel 1: Full |Z| spectrum with fit overlays ───
ax1 = fig.add_subplot(gs[0, :])
ax1.fill_between(masses, absZ, alpha=0.15, color="#00ccff")
ax1.plot(masses, absZ, color="#00ccff", linewidth=0.7, alpha=0.8, label="|Z| spectrum")

colors_cycle = ["#ff6b6b", "#ffd93d", "#51cf66", "#cc5de8",
                 "#339af0", "#ff922b", "#20c997", "#e64980",
                 "#845ef7", "#f06595", "#22b8cf"]

for i, (name, res) in enumerate(fit_results.items()):
    col = colors_cycle[i % len(colors_cycle)]
    ax1.plot(res["x_fit"], res["y_fit"], "--", color=col, linewidth=1.5, alpha=0.85)
    ax1.annotate(f"{name}\nσ={res['sigma']*1e3:.1f} MeV",
                 (res["mu"], res["A"]),
                 textcoords="offset points", xytext=(6, 8),
                 fontsize=6.5, color=col,
                 bbox=dict(boxstyle="round,pad=0.15", facecolor="#0d0d15",
                          edgecolor=col, alpha=0.75))

ax1.set_xlabel("M [GeV]", fontsize=11)
ax1.set_ylabel("|Z| [σ]", fontsize=11)
ax1.set_title("① Full Spectrum with Gaussian Fits", fontsize=13, fontweight="bold")
ax1.set_xlim(masses[0], masses[-1])
ax1.set_xscale("log")
ax1.grid(True, alpha=0.15)

# ─── Panel 2: Relative resolution σ/M vs M ───
ax2 = fig.add_subplot(gs[1, 0])

if fit_results:
    m_arr = np.array([fit_results[n]["mu"] for n in fit_results])
    s_arr = np.array([fit_results[n]["sigma"] for n in fit_results])
    s_err = np.array([fit_results[n]["sigma_err"] for n in fit_results])
    rel_arr = s_arr / m_arr
    rel_err = s_err / m_arr

    for i, name in enumerate(fit_results):
        col = colors_cycle[i % len(colors_cycle)]
        ax2.errorbar(m_arr[i], rel_arr[i] * 100, yerr=rel_err[i] * 100,
                     fmt="o", color=col, markersize=8, capsize=4, capthick=1.5,
                     markeredgecolor="white", markeredgewidth=0.5, zorder=5)
        ax2.annotate(name, (m_arr[i], rel_arr[i] * 100),
                     textcoords="offset points", xytext=(8, 4),
                     fontsize=7, color=col)

    # Overlay detector model curve
    m_model = np.logspace(np.log10(0.3), np.log10(120), 200)
    s_model = cms_resolution_model(m_model, a_fit, b_fit)
    ax2.plot(m_model, s_model / m_model * 100, "--", color="#aaaacc",
             linewidth=1.2, alpha=0.6, label=f"σ_det model (a={a_fit:.3f})")

ax2.set_xlabel("M [GeV]", fontsize=11)
ax2.set_ylabel("σ / M  [%]", fontsize=11)
ax2.set_title("② Relative Mass Resolution vs Mass", fontsize=12, fontweight="bold")
ax2.set_xscale("log")
ax2.set_yscale("log")
ax2.legend(fontsize=8, loc="upper right", facecolor="#0d0d15", edgecolor="#333355")
ax2.grid(True, alpha=0.15)

# ─── Panel 3: Close-pair separation ───
ax3 = fig.add_subplot(gs[1, 1])

pair_labels = []
pair_ratios = []
pair_colors = []

for sr in separation_results:
    if sr["sep_ratio"] is not None:
        pair_labels.append(sr["label"])
        pair_ratios.append(sr["sep_ratio"])
        pair_colors.append("#51cf66" if sr["resolved"] else "#ff6b6b")

if pair_ratios:
    y_pos = np.arange(len(pair_labels))
    bars = ax3.barh(y_pos, pair_ratios, color=pair_colors, alpha=0.8,
                    edgecolor="white", linewidth=0.5, height=0.6)
    ax3.axvline(2.0, color="#ffd93d", linestyle="--", linewidth=1.5,
                alpha=0.7, label="Rayleigh (Δm/σ = 2)")
    ax3.set_yticks(y_pos)
    ax3.set_yticklabels(pair_labels, fontsize=9)
    ax3.set_xlabel("Δm / σ_avg", fontsize=11)
    for j, (ratio, label) in enumerate(zip(pair_ratios, pair_labels)):
        ax3.text(ratio + 0.1, j, f"{ratio:.2f}", va="center",
                 fontsize=9, color="white", fontweight="bold")

ax3.set_title("③ Peak Separation (Close Doublets)", fontsize=12, fontweight="bold")
ax3.legend(fontsize=8, loc="lower right", facecolor="#0d0d15", edgecolor="#333355")
ax3.grid(True, alpha=0.15, axis="x")

# ─── Panel 4: ρ/ω region zoom ───
ax4 = fig.add_subplot(gs[2, 0])

rho_omega_mask = (masses >= 0.65) & (masses <= 0.90)
ax4.fill_between(masses[rho_omega_mask], absZ[rho_omega_mask],
                 alpha=0.2, color="#00ccff")
ax4.plot(masses[rho_omega_mask], absZ[rho_omega_mask],
         color="#00ccff", linewidth=1.5)

for name in ["ρ(770)", "ω(782)"]:
    m_pdg = PDG_RESONANCES[name][0]
    ax4.axvline(m_pdg, color="#ffd93d", linestyle="--", linewidth=1, alpha=0.5)
    ax4.annotate(name, (m_pdg, absZ[np.argmin(np.abs(masses - m_pdg))]),
                 textcoords="offset points", xytext=(5, 8),
                 fontsize=9, color="#ffd93d",
                 bbox=dict(boxstyle="round,pad=0.2", facecolor="#0d0d15",
                          edgecolor="#ffd93d", alpha=0.7))
    if name in fit_results:
        r = fit_results[name]
        ax4.plot(r["x_fit"], r["y_fit"], "--", color="#ff6b6b",
                 linewidth=1.5, alpha=0.8)

ax4.set_xlabel("M [GeV]", fontsize=11)
ax4.set_ylabel("|Z| [σ]", fontsize=11)
ax4.set_title("④ ρ(770) / ω(782) Separation (Δm = 7.4 MeV)",
              fontsize=12, fontweight="bold")
ax4.grid(True, alpha=0.15)

# ─── Panel 5: Υ family zoom ───
ax5 = fig.add_subplot(gs[2, 1])

ups_mask = (masses >= 9.0) & (masses <= 10.8)
ax5.fill_between(masses[ups_mask], absZ[ups_mask], alpha=0.2, color="#00ccff")
ax5.plot(masses[ups_mask], absZ[ups_mask], color="#00ccff", linewidth=1.5)

for name in ["Υ(1S)", "Υ(2S)", "Υ(3S)"]:
    m_pdg = PDG_RESONANCES[name][0]
    ax5.axvline(m_pdg, color="#ffd93d", linestyle="--", linewidth=1, alpha=0.5)
    ax5.annotate(name, (m_pdg, absZ[np.argmin(np.abs(masses - m_pdg))]),
                 textcoords="offset points", xytext=(5, 8),
                 fontsize=9, color="#ffd93d",
                 bbox=dict(boxstyle="round,pad=0.2", facecolor="#0d0d15",
                          edgecolor="#ffd93d", alpha=0.7))
    if name in fit_results:
        r = fit_results[name]
        ax5.plot(r["x_fit"], r["y_fit"], "--", color="#cc5de8",
                 linewidth=1.5, alpha=0.8)

ax5.set_xlabel("M [GeV]", fontsize=11)
ax5.set_ylabel("|Z| [σ]", fontsize=11)
ax5.set_title("⑤ Υ(1S,2S,3S) Family Separation",
              fontsize=12, fontweight="bold")
ax5.grid(True, alpha=0.15)

# ─── Add text panel (panel 6) as summary annotation ───
# We overlay a text box on the top-right area of the figure
summary_lines = ["─── RESOLUTION SUMMARY ───\n"]

if fit_results:
    for name in fit_results:
        r = fit_results[name]
        summary_lines.append(
            f"  {name:<10s}  σ = {r['sigma']*1e3:>6.1f} MeV  "
            f"  σ/M = {r['rel_resolution']*100:>5.2f}%  "
            f"  |Z| = {r['A']:>5.1f}σ"
        )

summary_lines.append("\n─── CLOSE PAIRS ───\n")
for sr in separation_results:
    sep_str = f"Δm/σ = {sr['sep_ratio']:.2f}" if sr['sep_ratio'] else "—"
    res_str = "✅" if sr['resolved'] else ("✗" if sr['resolved'] is not None else "—")
    ray_str = "✅" if sr['rayleigh'] else "✗"
    summary_lines.append(
        f"  {sr['label']:<16s}  {sep_str:<14s}  Sep: {res_str}  Ray: {ray_str}"
    )

summary_lines.append(f"\n─── STATISTICS ───\n")
summary_lines.append(f"  Peaks fitted:          {len(fit_results)}")
summary_lines.append(f"  Rayleigh-resolved:     {n_rayleigh_pass}/{len(rayleigh_results)}")
summary_lines.append(f"  Close-pair separated:  {n_sep_pass}/{n_sep_total}")
if fit_results:
    summary_lines.append(f"  Best σ/M:              {rel_res.min()*100:.3f}%")
    summary_lines.append(f"  Detector model:        σ = {a_fit:.4f}M + {b_fit:.2e}M²")

summary_text = "\n".join(summary_lines)

fig.text(0.50, 0.005, summary_text,
         fontsize=7.5, fontfamily="monospace", color="#aaaacc",
         ha="center", va="bottom",
         bbox=dict(boxstyle="round,pad=0.5", facecolor="#0d0d15",
                  edgecolor="#333355", alpha=0.9))

fig.savefig(OUT_PLOT, dpi=cfg.DPI, bbox_inches="tight", facecolor="#0a0a0f")
plt.close()
print(f"\n[viz] Saved: {OUT_PLOT}")

print("\n" + "=" * 80)
print("  ANALYSIS COMPLETE")
print("=" * 80)

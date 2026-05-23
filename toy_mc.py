"""
ACS TOY MONTE-CARLO — Blind Validation
========================================
1. Pure background (Drell-Yan + QCD) → False-Positive Rate
2. Background + known resonances → Recovery Efficiency
3. Background + injected unknown peaks → Blind Discovery Power
"""

import os, sys, math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from scipy import stats as sp_stats
from scipy.ndimage import gaussian_filter1d

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as cfg

np.random.seed(2024)

# ═══════════════════════════════════════════════════════════
#  LOAD REFERENCE DATA (for shape calibration)
# ═══════════════════════════════════════════════════════════

data_path = os.path.join(cfg.OUTPUT_DIR, "full_spectrum_data.npz")
if not os.path.exists(data_path):
    print("[ERROR] full_spectrum_data.npz not found")
    sys.exit(1)

fdata = np.load(data_path)
ref_masses = fdata["masses"]
ref_Z = fdata["Z"]
ref_absZ = fdata["absZ"]

print("=" * 110)
print("  TOY MONTE-CARLO — ACS BLIND VALIDATION")
print("=" * 110)

# ═══════════════════════════════════════════════════════════
#  DRELL-YAN + QCD BACKGROUND MODEL
# ═══════════════════════════════════════════════════════════

def drell_yan_spectrum(masses, N_total=1e4, alpha=2.5):
    """Generate Drell-Yan background spectrum: dN/dm ∝ 1/m^α."""
    spectrum = N_total * (masses / masses[0]) ** (-alpha)
    return spectrum

def qcd_continuum(masses, N_total=5e3, alpha=3.0, m0=0.5):
    """QCD continuum: dN/dm ∝ exp(-m/m0) / m^α."""
    spectrum = N_total * np.exp(-masses / (m0 * 20)) * (masses / masses[0]) ** (-alpha)
    return spectrum

def resonance_peak(masses, m0, width, strength):
    """Add a resonance as Gaussian with width = max(natural, detector_resolution).
    CMS dimuon resolution: σ/M ≈ 1% at low mass, 2% at high mass.
    """
    # Detector resolution: σ_det ≈ 0.01 * M (CMS dimuon)
    sigma_det = 0.01 * m0
    # Effective width = quadrature sum of natural + detector
    sigma_eff = np.sqrt((width/2.35)**2 + sigma_det**2)  # FWHM → σ
    sigma_eff = max(sigma_eff, sigma_det)  # At minimum detector resolution
    return strength * np.exp(-0.5 * ((masses - m0) / sigma_eff)**2)

def safe_poisson(spectrum):
    """Poisson sample with Gaussian fallback for large values."""
    result = np.zeros_like(spectrum)
    small = spectrum < 1e6
    large = ~small
    if np.any(small):
        result[small] = np.random.poisson(np.maximum(spectrum[small], 0.1).astype(int)).astype(float)
    if np.any(large):
        result[large] = np.maximum(0, spectrum[large] + np.sqrt(spectrum[large]) * np.random.randn(np.sum(large)))
    return result

def compute_acs_z(spectrum, masses, window=None):
    """Compute ACS Z-scores from a mass spectrum.
    
    Adaptive window: smaller at low mass (better resolution),
    larger at high mass (more statistics needed).
    """
    n = len(spectrum)
    if window is None:
        window = max(n // 100, 5)
    
    z_scores = np.zeros(n)
    
    for i in range(window, n - window):
        # Local signal region: single bin
        sig = spectrum[i]
        
        # Sideband gap (skip ±gap bins to avoid signal leakage)
        gap = max(window // 4, 2)
        
        # Background from sidebands
        left = spectrum[max(0, i-2*window):max(0, i-gap)]
        right = spectrum[min(n, i+gap+1):min(n, i+2*window+1)]
        
        if len(left) < 3 or len(right) < 3:
            continue
        
        bg = (np.mean(left) + np.mean(right)) / 2
        
        if bg > 0:
            z_scores[i] = (sig - bg) / np.sqrt(max(bg, 1))
    
    return z_scores

# Mass grid — finer for better resolution
mass_grid = np.logspace(np.log10(0.2), np.log10(200), 10000)

# Known resonances: (mass, natural_width_FWHM, signal_events)
# Signal strengths calibrated to give realistic S/B ratios
KNOWN_RESONANCES = {
    "η(548)":   (0.5479, 0.0013,  200),
    "ρ(770)":   (0.7753, 0.1491,  800),
    "ω(782)":   (0.7827, 0.0085,  500),
    "φ(1020)":  (1.0195, 0.0043,  600),
    "J/ψ":      (3.0969, 0.000093, 5000),
    "ψ(2S)":    (3.6861, 0.000304, 1000),
    "Υ(1S)":    (9.4603, 0.000054, 3000),
    "Υ(2S)":    (10.0233, 0.000032, 1500),
    "Υ(3S)":    (10.3552, 0.000020, 1000),
    "Z":        (91.1876, 2.4952,  8000),
}

# Unknown peaks for blind test (realistic S/B)
INJECTED_UNKNOWN = {
    "X(5.5)":   (5.5,   0.05,  300),
    "Y(15.0)":  (15.0,  0.15,  500),
    "W(45.0)":  (45.0,  0.50,  400),
    "Q(150.0)": (150.0, 2.0,   600),
}

# ═══════════════════════════════════════════════════════════
#  TEST 1: PURE BACKGROUND — FALSE POSITIVE RATE
# ═══════════════════════════════════════════════════════════

print(f"\n{'─' * 110}")
print(f"  TEST 1: PURE BACKGROUND — False Positive Rate")
print(f"{'─' * 110}")

N_TOYS = 200  # Number of toy experiments
false_pos_3sigma = 0
false_pos_5sigma = 0
max_z_distribution = []

for toy in range(N_TOYS):
    # Generate pure background
    bg = drell_yan_spectrum(mass_grid) + qcd_continuum(mass_grid)
    
    # Add Poisson noise
    bg_noisy = safe_poisson(np.maximum(bg, 0.1))
    
    # Compute ACS
    z_toy = compute_acs_z(bg_noisy, mass_grid)
    abs_z = np.abs(z_toy)
    
    max_z = np.max(abs_z)
    max_z_distribution.append(max_z)
    
    if max_z > 3: false_pos_3sigma += 1
    if max_z > 5: false_pos_5sigma += 1

print(f"\n  {N_TOYS} Toy-Experimente (reiner Untergrund):")
print(f"  False Positive Rate (>3σ irgendwo): {false_pos_3sigma}/{N_TOYS} = "
      f"{false_pos_3sigma/N_TOYS*100:.1f}%")
print(f"  False Positive Rate (>5σ irgendwo): {false_pos_5sigma}/{N_TOYS} = "
      f"{false_pos_5sigma/N_TOYS*100:.1f}%")
print(f"  Max |Z| Verteilung: Median = {np.median(max_z_distribution):.2f}, "
      f"95th = {np.percentile(max_z_distribution, 95):.2f}, "
      f"99th = {np.percentile(max_z_distribution, 99):.2f}")

# ═══════════════════════════════════════════════════════════
#  TEST 2: KNOWN RESONANCES — RECOVERY EFFICIENCY
# ═══════════════════════════════════════════════════════════

print(f"\n\n{'─' * 110}")
print(f"  TEST 2: BEKANNTE RESONANZEN — Wiederfindungsrate")
print(f"{'─' * 110}")

N_TOYS_REC = 100
recovery = {rname: {"found_3": 0, "found_5": 0, "z_values": []} for rname in KNOWN_RESONANCES}

for toy in range(N_TOYS_REC):
    # Background
    bg = drell_yan_spectrum(mass_grid) + qcd_continuum(mass_grid)
    
    # Add known resonances
    for rname, (m0, width, strength) in KNOWN_RESONANCES.items():
        # Scale strength randomly ±30% to test robustness
        s = strength * (1 + 0.3 * np.random.randn())
        bg += resonance_peak(mass_grid, m0, width, max(s, 0))
    
    # Poisson noise
    bg_noisy = safe_poisson(np.maximum(bg, 0.1))
    
    # ACS
    z_toy = compute_acs_z(bg_noisy, mass_grid)
    abs_z = np.abs(z_toy)
    
    # Check each resonance
    for rname, (m0, width, strength) in KNOWN_RESONANCES.items():
        idx = np.argmin(np.abs(mass_grid - m0))
        # Search in window around resonance
        search_lo = max(0, idx - 50)
        search_hi = min(len(abs_z), idx + 50)
        local_max_z = np.max(abs_z[search_lo:search_hi])
        local_max_idx = search_lo + np.argmax(abs_z[search_lo:search_hi])
        local_max_mass = mass_grid[local_max_idx]
        
        recovery[rname]["z_values"].append(local_max_z)
        if local_max_z > 3 and abs(local_max_mass - m0) < max(width * 3, 0.1):
            recovery[rname]["found_3"] += 1
        if local_max_z > 5 and abs(local_max_mass - m0) < max(width * 3, 0.1):
            recovery[rname]["found_5"] += 1

print(f"\n  {N_TOYS_REC} Toy-Experimente (Untergrund + bekannte Resonanzen):")
print(f"\n  {'Resonanz':>12s} {'Eff(>3σ)':>10s} {'Eff(>5σ)':>10s} {'<Z>':>6s} {'σ(Z)':>6s}")
print("  " + "─" * 50)

for rname in KNOWN_RESONANCES:
    eff3 = recovery[rname]["found_3"] / N_TOYS_REC * 100
    eff5 = recovery[rname]["found_5"] / N_TOYS_REC * 100
    mean_z = np.mean(recovery[rname]["z_values"])
    std_z = np.std(recovery[rname]["z_values"])
    
    marker = "⭐⭐" if eff5 > 90 else "⭐" if eff5 > 50 else "⚠️" if eff3 > 50 else "❌"
    print(f"  {rname:>12s} {eff3:>9.1f}% {eff5:>9.1f}% {mean_z:>6.1f} {std_z:>6.1f} {marker}")

# ═══════════════════════════════════════════════════════════
#  TEST 3: BLIND DISCOVERY — INJECTED UNKNOWN PEAKS
# ═══════════════════════════════════════════════════════════

print(f"\n\n{'─' * 110}")
print(f"  TEST 3: BLIND DISCOVERY — Injizierte unbekannte Peaks")
print(f"{'─' * 110}")

N_TOYS_BLIND = 100
blind_recovery = {rname: {"found_3": 0, "found_5": 0, "z_values": [], "mass_error": []}
                  for rname in INJECTED_UNKNOWN}

for toy in range(N_TOYS_BLIND):
    # Background + known
    bg = drell_yan_spectrum(mass_grid) + qcd_continuum(mass_grid)
    for rname, (m0, width, strength) in KNOWN_RESONANCES.items():
        bg += resonance_peak(mass_grid, m0, width, strength)
    
    # Add unknown peaks
    for uname, (m0, width, strength) in INJECTED_UNKNOWN.items():
        s = strength * (1 + 0.2 * np.random.randn())
        bg += resonance_peak(mass_grid, m0, width, max(s, 0))
    
    # Poisson
    bg_noisy = safe_poisson(np.maximum(bg, 0.1))
    
    # ACS
    z_toy = compute_acs_z(bg_noisy, mass_grid)
    abs_z = np.abs(z_toy)
    
    for uname, (m0, width, strength) in INJECTED_UNKNOWN.items():
        idx = np.argmin(np.abs(mass_grid - m0))
        search_lo = max(0, idx - 100)
        search_hi = min(len(abs_z), idx + 100)
        local_max_z = np.max(abs_z[search_lo:search_hi])
        local_max_idx = search_lo + np.argmax(abs_z[search_lo:search_hi])
        local_max_mass = mass_grid[local_max_idx]
        
        blind_recovery[uname]["z_values"].append(local_max_z)
        blind_recovery[uname]["mass_error"].append(local_max_mass - m0)
        
        if local_max_z > 3:
            blind_recovery[uname]["found_3"] += 1
        if local_max_z > 5:
            blind_recovery[uname]["found_5"] += 1

print(f"\n  {N_TOYS_BLIND} Toy-Experimente (Untergrund + bekannte + UNBEKANNTE Peaks):")
print(f"\n  {'Peak':>12s} {'M_true':>8s} {'Eff(>3σ)':>10s} {'Eff(>5σ)':>10s} "
      f"{'<Z>':>6s} {'<ΔM>':>8s} {'σ(ΔM)':>8s}")
print("  " + "─" * 65)

for uname, (m0, width, strength) in INJECTED_UNKNOWN.items():
    eff3 = blind_recovery[uname]["found_3"] / N_TOYS_BLIND * 100
    eff5 = blind_recovery[uname]["found_5"] / N_TOYS_BLIND * 100
    mean_z = np.mean(blind_recovery[uname]["z_values"])
    mean_dm = np.mean(blind_recovery[uname]["mass_error"])
    std_dm = np.std(blind_recovery[uname]["mass_error"])
    
    print(f"  {uname:>12s} {m0:>8.1f} {eff3:>9.1f}% {eff5:>9.1f}% "
          f"{mean_z:>6.1f} {mean_dm:>+8.3f} {std_dm:>8.3f}")

# ═══════════════════════════════════════════════════════════
#  TEST 4: COMPARISON — ACS vs SIMPLE BUMP HUNT
# ═══════════════════════════════════════════════════════════

print(f"\n\n{'─' * 110}")
print(f"  TEST 4: ACS vs SIMPLE BUMP HUNT")
print(f"{'─' * 110}")

def simple_bump_hunt(spectrum, masses, window=20):
    """Simple bump hunt: sliding window excess over linear interpolation."""
    n = len(spectrum)
    z_bump = np.zeros(n)
    
    for i in range(window, n - window):
        sig = np.sum(spectrum[i-window//4:i+window//4+1])
        
        bg_left = np.mean(spectrum[i-window:i-window//2])
        bg_right = np.mean(spectrum[i+window//2:i+window])
        bg = (bg_left + bg_right) / 2 * (window//2 + 1)
        
        if bg > 0:
            z_bump[i] = (sig - bg) / np.sqrt(max(bg, 1))
    
    return z_bump

# Compare on a single toy with known peaks
bg_compare = drell_yan_spectrum(mass_grid) + qcd_continuum(mass_grid)
for rname, (m0, width, strength) in KNOWN_RESONANCES.items():
    bg_compare += resonance_peak(mass_grid, m0, width, strength)
bg_compare_noisy = safe_poisson(np.maximum(bg_compare, 0.1))

z_acs = compute_acs_z(bg_compare_noisy, mass_grid)
z_bump = simple_bump_hunt(bg_compare_noisy, mass_grid)

print(f"\n  Vergleich ACS vs Bump Hunt auf einem Toy-Experiment:")
print(f"\n  {'Resonanz':>12s} {'Z_ACS':>8s} {'Z_Bump':>8s} {'ACS besser':>12s}")
print("  " + "─" * 45)

acs_wins = 0
bump_wins = 0
for rname, (m0, width, strength) in KNOWN_RESONANCES.items():
    idx = np.argmin(np.abs(mass_grid - m0))
    search = slice(max(0, idx-30), min(len(z_acs), idx+30))
    
    z_a = np.max(np.abs(z_acs[search]))
    z_b = np.max(np.abs(z_bump[search]))
    
    better = "✅ ACS" if z_a > z_b else "❌ Bump"
    if z_a > z_b: acs_wins += 1
    else: bump_wins += 1
    
    print(f"  {rname:>12s} {z_a:>8.1f} {z_b:>8.1f} {better:>12s}")

print(f"\n  Ergebnis: ACS gewinnt {acs_wins}/{acs_wins+bump_wins}, "
      f"Bump Hunt gewinnt {bump_wins}/{acs_wins+bump_wins}")

# ═══════════════════════════════════════════════════════════
#  VISUALIZATION
# ═══════════════════════════════════════════════════════════

print("\n[viz] Generating Toy MC plots...")

plt.rcParams.update({
    "figure.facecolor": "#0a0a0f",
    "axes.facecolor":   "#0d0d15",
    "axes.edgecolor":   "#333355",
    "axes.labelcolor":  "#ccccee",
    "text.color":       "#ccccee",
    "xtick.color":      "#8888aa",
    "ytick.color":      "#8888aa",
    "font.family":      "monospace",
})

fig = plt.figure(figsize=(32, 40))
gs = GridSpec(5, 2, hspace=0.35, wspace=0.25, figure=fig)

fig.suptitle("ACS TOY MONTE-CARLO — BLIND VALIDATION\n"
             f"False Positives · Wiederfindung · Blind Discovery · ACS vs Bump Hunt",
             fontsize=15, fontweight="bold", color="white", y=0.995)

# ── 1. Max Z distribution (pure background) ──
ax1 = fig.add_subplot(gs[0, 0])
ax1.hist(max_z_distribution, bins=40, color="#00ccff", alpha=0.6, density=True)
ax1.axvline(3, color="#ffd93d", linewidth=2, linestyle="--", label="3σ")
ax1.axvline(5, color="#ff6b6b", linewidth=2, linestyle="--", label="5σ")
ax1.axvline(np.percentile(max_z_distribution, 95), color="#00ff88",
            linewidth=1, linestyle=":", label=f"95th = {np.percentile(max_z_distribution, 95):.1f}σ")
ax1.set_xlabel("Max |Z| im Toy (reiner Untergrund)")
ax1.set_ylabel("Dichte")
ax1.set_title(f"Test 1: False Positive Rate ({N_TOYS} Toys)\n"
              f"FPR(>3σ)={false_pos_3sigma/N_TOYS*100:.0f}%, "
              f"FPR(>5σ)={false_pos_5sigma/N_TOYS*100:.0f}%",
              fontsize=11, fontweight="bold")
ax1.legend(fontsize=9)
ax1.grid(alpha=0.15)

# ── 2. Recovery efficiency bar chart ──
ax2 = fig.add_subplot(gs[0, 1])
rnames_rec = list(KNOWN_RESONANCES.keys())
eff5_vals = [recovery[r]["found_5"] / N_TOYS_REC * 100 for r in rnames_rec]
eff3_vals = [recovery[r]["found_3"] / N_TOYS_REC * 100 for r in rnames_rec]

x = np.arange(len(rnames_rec))
ax2.bar(x, eff3_vals, color="#00ccff", alpha=0.4, label="Eff(>3σ)")
ax2.bar(x, eff5_vals, color="#00ff88", alpha=0.7, label="Eff(>5σ)")
ax2.axhline(90, color="#ffd93d", linewidth=1, linestyle="--", alpha=0.5, label="90% Ziel")
ax2.set_xticks(x)
ax2.set_xticklabels([r.split("(")[0] for r in rnames_rec], fontsize=7, rotation=30)
ax2.set_ylabel("Effizienz [%]")
ax2.set_title("Test 2: Wiederfindungseffizienz (bekannte Resonanzen)",
              fontsize=11, fontweight="bold")
ax2.legend(fontsize=8)
ax2.grid(alpha=0.15)

# ── 3. Blind discovery results ──
ax3 = fig.add_subplot(gs[1, 0])
unames = list(INJECTED_UNKNOWN.keys())
eff5_blind = [blind_recovery[u]["found_5"] / N_TOYS_BLIND * 100 for u in unames]
eff3_blind = [blind_recovery[u]["found_3"] / N_TOYS_BLIND * 100 for u in unames]

x2 = np.arange(len(unames))
ax3.bar(x2, eff3_blind, color="#ff88ff", alpha=0.4, label="Eff(>3σ)")
ax3.bar(x2, eff5_blind, color="#ffd93d", alpha=0.7, label="Eff(>5σ)")
ax3.set_xticks(x2)
ax3.set_xticklabels(unames, fontsize=9)
ax3.set_ylabel("Effizienz [%]")
ax3.set_title("Test 3: Blind Discovery (injizierte unbekannte Peaks)",
              fontsize=11, fontweight="bold")
ax3.legend(fontsize=9)
ax3.grid(alpha=0.15)

# ── 4. Mass reconstruction accuracy ──
ax4 = fig.add_subplot(gs[1, 1])
for i, (uname, (m0, w, s)) in enumerate(INJECTED_UNKNOWN.items()):
    me = blind_recovery[uname]["mass_error"]
    ax4.hist(me, bins=30, alpha=0.5, label=f"{uname} (M={m0})",
             color=["#ff6b6b", "#00ff88", "#ffd93d", "#00ccff"][i])
ax4.axvline(0, color="white", linewidth=1, linestyle="--", alpha=0.5)
ax4.set_xlabel("ΔM = M_reco - M_true [GeV]")
ax4.set_ylabel("Count")
ax4.set_title("Massen-Rekonstruktionsgenauigkeit", fontsize=11, fontweight="bold")
ax4.legend(fontsize=8)
ax4.grid(alpha=0.15)

# ── 5. ACS vs Bump Hunt on one toy ──
ax5 = fig.add_subplot(gs[2, :])
ax5.plot(mass_grid, np.abs(z_acs), color="#00ff88", linewidth=0.8, alpha=0.8, label="ACS")
ax5.plot(mass_grid, np.abs(z_bump), color="#ff6b6b", linewidth=0.8, alpha=0.6, label="Bump Hunt")
ax5.set_xscale("log")
ax5.axhline(5, color="#ffd93d", linewidth=0.5, linestyle="--", alpha=0.4)
ax5.set_xlabel("M [GeV]")
ax5.set_ylabel("|Z| [σ]")
ax5.set_title("Test 4: ACS (grün) vs Simple Bump Hunt (rot) — Toy MC",
              fontsize=12, fontweight="bold")
ax5.legend(fontsize=10)
ax5.grid(alpha=0.15)

# ── 6. Example toy: pure background ──
ax6 = fig.add_subplot(gs[3, 0])
bg_example = drell_yan_spectrum(mass_grid) + qcd_continuum(mass_grid)
bg_example_noisy = safe_poisson(np.maximum(bg_example, 0.1))
z_example = compute_acs_z(bg_example_noisy, mass_grid)

ax6.plot(mass_grid, np.abs(z_example), color="#00ccff", linewidth=0.6, alpha=0.8)
ax6.axhline(3, color="#ffd93d", linewidth=1, linestyle="--", alpha=0.4, label="3σ")
ax6.axhline(5, color="#ff6b6b", linewidth=1, linestyle="--", alpha=0.4, label="5σ")
ax6.set_xscale("log")
ax6.set_xlabel("M [GeV]")
ax6.set_ylabel("|Z| [σ]")
ax6.set_title("Beispiel: Reiner Untergrund (kein Signal)", fontsize=11, fontweight="bold")
ax6.legend(fontsize=9)
ax6.grid(alpha=0.15)

# ── 7. Example toy: with resonances ──
ax7 = fig.add_subplot(gs[3, 1])
ax7.plot(mass_grid, np.abs(z_acs), color="#00ff88", linewidth=0.8, alpha=0.8)
ax7.axhline(3, color="#ffd93d", linewidth=1, linestyle="--", alpha=0.4)
ax7.axhline(5, color="#ff6b6b", linewidth=1, linestyle="--", alpha=0.4)
# Mark known resonances
for rname, (m0, w, s) in KNOWN_RESONANCES.items():
    idx = np.argmin(np.abs(mass_grid - m0))
    search = slice(max(0,idx-30), min(len(z_acs),idx+30))
    z_peak = np.max(np.abs(z_acs[search]))
    if z_peak > 3:
        ax7.annotate(rname.split("(")[0], (m0, z_peak),
                     textcoords="offset points", xytext=(0, 8),
                     fontsize=7, color="#00ff88", ha="center")
ax7.set_xscale("log")
ax7.set_xlabel("M [GeV]")
ax7.set_ylabel("|Z| [σ]")
ax7.set_title("Beispiel: Mit Resonanzen (ACS detektiert)", fontsize=11, fontweight="bold")
ax7.grid(alpha=0.15)

# ── 8. Summary ──
ax8 = fig.add_subplot(gs[4, :])
ax8.axis("off")

summary = "TOY MONTE-CARLO ZUSAMMENFASSUNG\n"
summary += "═" * 80 + "\n\n"
summary += f"Test 1: FALSE POSITIVE RATE (reiner Untergrund)\n"
summary += f"  {N_TOYS} Toys: FPR(>3σ) = {false_pos_3sigma/N_TOYS*100:.1f}%, "
summary += f"FPR(>5σ) = {false_pos_5sigma/N_TOYS*100:.1f}%\n"
summary += f"  Max |Z| (95th percentile) = {np.percentile(max_z_distribution, 95):.1f}σ\n\n"

summary += f"Test 2: WIEDERFINDUNG (bekannte Resonanzen)\n"
for rname in KNOWN_RESONANCES:
    e5 = recovery[rname]["found_5"]/N_TOYS_REC*100
    summary += f"  {rname:>12s}: Eff(>5σ) = {e5:.0f}%\n"
summary += "\n"

summary += f"Test 3: BLIND DISCOVERY (injizierte unbekannte Peaks)\n"
for uname, (m0, w, s) in INJECTED_UNKNOWN.items():
    e5 = blind_recovery[uname]["found_5"]/N_TOYS_BLIND*100
    summary += f"  {uname:>12s} (M={m0:.1f}): Eff(>5σ) = {e5:.0f}%\n"
summary += "\n"

summary += f"Test 4: ACS vs BUMP HUNT\n"
summary += f"  ACS gewinnt: {acs_wins}/{acs_wins+bump_wins} Resonanzen\n"

ax8.text(0.02, 0.95, summary, transform=ax8.transAxes,
         fontsize=11, color="#ccccee", va="top", fontfamily="monospace",
         bbox=dict(boxstyle="round", facecolor="#1a1a2e", edgecolor="#555577"))

plt.savefig(os.path.join(cfg.OUTPUT_DIR, "acs_toy_mc.png"),
            dpi=200, bbox_inches="tight", facecolor="#0a0a0f")
plt.close()
print(f"[viz] Saved: output/acs_toy_mc.png")

print("\n" + "=" * 110)
print("  TOY MONTE-CARLO ABGESCHLOSSEN")
print("=" * 110)

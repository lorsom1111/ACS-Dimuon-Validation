import numpy as np
import scipy.signal as signal
from scipy.stats import entropy
import matplotlib.pyplot as plt
import os

print("--- SETI at the LHC: Searching for Artificial Signatures in Quantum Noise ---")

# 1. Load Data
data = np.load('output/full_spectrum_data.npz')
masses = data['masses']
z_scores = data['Z']

# 2. Define natural resonances to mask out
# Format: (center_mass, mask_half_width)
natural_resonances = [
    (0.775, 0.1),    # rho/omega
    (1.020, 0.05),   # phi
    (3.097, 0.1),    # J/psi
    (3.686, 0.05),   # psi(2S)
    (9.460, 0.2),    # Upsilon(1S)
    (10.023, 0.1),   # Upsilon(2S)
    (10.355, 0.1),   # Upsilon(3S)
    (75.95, 2.0),    # New 76 GeV state
    (91.188, 5.0)    # Z boson
]

mask = np.ones_len = np.ones(len(masses), dtype=bool)
for m_center, width in natural_resonances:
    mask &= ~((masses > m_center - width) & (masses < m_center + width))

res_masses = masses[mask]
res_z = z_scores[mask]

print(f"Total bins: {len(masses)}, Residual bins (after masking natural resonances): {len(res_masses)}")

# 3. Entropy Analysis
# Discretize Z-scores into bins to compute Shannon entropy
hist, bin_edges = np.histogram(res_z, bins=50, density=True)
p_z = hist[hist > 0] * np.diff(bin_edges)[hist > 0]
shannon_entropy = entropy(p_z)
print(f"Shannon Entropy of residual Z-scores: {shannon_entropy:.4f} bits")
# For a perfect standard normal distribution, entropy is 0.5 * ln(2*pi*e) ~ 1.418 nats = 2.04 bits.
# If entropy is significantly different, there's hidden structure.

# 4. Search for Koch Formula Constants in Residual Peaks
# Find peaks in the residual background
peaks, _ = signal.find_peaks(res_z, height=2.5, distance=5)
peak_masses = res_masses[peaks]
peak_z = res_z[peaks]

print(f"Found {len(peak_masses)} micro-peaks (Z > 2.5) in the residual noise.")

# Compute all pairwise mass ratios
ratios = []
for i in range(len(peak_masses)):
    for j in range(i+1, len(peak_masses)):
        r = peak_masses[j] / peak_masses[i]
        ratios.append(r)

ratios = np.array(ratios)

# Histogram of ratios to see if certain "communication keys" are favored
plt.figure(figsize=(10, 6))
counts, bins, _ = plt.hist(ratios, bins=500, range=(1, 10), color='cyan', alpha=0.7, edgecolor='k')
plt.title("Mass Ratio Distribution of Residual Micro-Peaks (SETI Search)")
plt.xlabel("Mass Ratio $M_j / M_i$")
plt.ylabel("Frequency")

# Check for specific keys: e, pi, 3, 4/3, sqrt(3)
keys = {
    'e': np.e,
    'pi': np.pi,
    '3 (Koch)': 3.0,
    '4/3 (QCD/Koch)': 4/3,
    'phi (Golden Ratio)': (1 + np.sqrt(5))/2,
    'sqrt(3)': np.sqrt(3)
}

for name, val in keys.items():
    plt.axvline(val, color='r', linestyle='--', alpha=0.6)
    plt.text(val, max(counts)*0.8, f" {name}", rotation=90, color='red', fontsize=9)

plt.tight_layout()
plt.savefig('output/seti_ratios.png')
print("Saved ratio distribution to output/seti_ratios.png")

# 5. Lomb-Scargle Periodogram (FFT equivalent for non-uniform data)
# Look for hidden carrier waves in mass space
frequencies = np.linspace(0.1, 10.0, 1000) # Carrier frequencies
pgram = signal.lombscargle(res_masses, res_z, frequencies, normalize=True)

plt.figure(figsize=(10, 6))
plt.plot(frequencies, pgram, color='lime')
plt.title("Lomb-Scargle Periodogram of Residual Z-scores (Carrier Wave Search)")
plt.xlabel("Frequency (1/GeV)")
plt.ylabel("Normalized Power")
plt.tight_layout()
plt.savefig('output/seti_carrier.png')
print("Saved carrier periodogram to output/seti_carrier.png")

# Identify dominant carrier
best_freq = frequencies[np.argmax(pgram)]
print(f"Strongest hidden carrier wave frequency: f = {best_freq:.3f} GeV^-1 (Period T = {1/best_freq:.3f} GeV)")

print("--- Analysis Complete ---")

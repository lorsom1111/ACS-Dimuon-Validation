import numpy as np
import scipy.signal as signal
from scipy.io import wavfile
import os

print("--- DECODING THE RINDLER MESSAGE ---")

# 1. Load Data
data = np.load('output/full_spectrum_data.npz')
masses = data['masses']
z_scores = data['Z']

natural_resonances = [
    (0.775, 0.1), (1.020, 0.05), (3.097, 0.1), (3.686, 0.05),
    (9.460, 0.2), (10.023, 0.1), (10.355, 0.1), (75.95, 2.0), (91.188, 5.0)
]
mask = np.ones(len(masses), dtype=bool)
for m_center, width in natural_resonances:
    mask &= ~((masses > m_center - width) & (masses < m_center + width))

res_masses = masses[mask]
res_z = z_scores[mask]

peaks, _ = signal.find_peaks(res_z, height=2.5, distance=5)
peak_masses = res_masses[peaks]
peak_z = res_z[peaks]

print(f"\nExtracted 15 Peaks (Masses in GeV):")
print(np.round(peak_masses, 3))

# --- PROTOCOL 1: BINARY ARECIBO ---
print("\n--- PROTOCOL 1: BINARY (Carrier Threshold) ---")
T_carrier = 1.084
diffs = np.diff(peak_masses)
binary = "".join(["1" if d > T_carrier else "0" for d in diffs])
print(f"Binary String (14 bits): {binary}")
try:
    # Try converting to bytes if length allows (padded to 16)
    padded = binary.zfill(16)
    n = int(padded, 2)
    print(f"Decoded ASCII: {n.to_bytes((n.bit_length() + 7) // 8, 'big').decode('ascii', errors='ignore')}")
except Exception as e:
    print("Could not decode to standard ASCII")

# --- PROTOCOL 2: BASE-26 ALPHABET ---
print("\n--- PROTOCOL 2: ASCII MAPPING ---")
# Let's map the fractional part to a letter A-Z
ascii_str = ""
for m in peak_masses:
    val = int((m * 100) % 26) + 65
    ascii_str += chr(val)
print(f"Alphabet String (mod 26): {ascii_str}")

# --- PROTOCOL 3: FRACTAL SYNTAX ---
print("\n--- PROTOCOL 3: FRACTAL SYNTAX (3, e, pi) ---")
# Try to find a combination of 3^n * e^m * pi^k that matches the mass
constants = {'3': 3.0, 'e': np.e, 'pi': np.pi}
for i, m in enumerate(peak_masses):
    best_err = 999
    best_str = ""
    for n in range(-3, 4):
        for k in range(-3, 4):
            for p in range(-3, 4):
                val = (3.0**n) * (np.e**k) * (np.pi**p)
                err = abs(m - val) / m
                if err < best_err:
                    best_err = err
                    best_str = f"3^{n} * e^{k} * pi^{p}"
    print(f"Peak {i+1} ({m:.2f} GeV) -> {best_str} (err: {best_err*100:.1f}%)")

# --- PROTOCOL 4: AUDIO SONIFICATION ---
print("\n--- PROTOCOL 4: SONIFICATION ---")
# Scale Z-scores to 16-bit integer PCM
# Sample rate: let's map the mass spectrum to time.
# The residuals have ~1894 points. If we play at 8000 Hz, it's very short.
# Let's resample / interpolate to make it 5 seconds long (44100 * 5 = 220500 points)
from scipy.interpolate import interp1d
f_interp = interp1d(np.linspace(0, 1, len(res_z)), res_z, kind='cubic')
x_new = np.linspace(0, 1, 44100 * 5)
audio_signal = f_interp(x_new)

# Add the carrier wave explicitly to the audio so we can hear it
# The carrier wave has a frequency of 0.923 GeV^-1.
# M maps to time. Delta M = 200 GeV corresponds to 5 seconds.
# 1 GeV = 0.025 seconds. Period T = 1.084 GeV = 0.0271 seconds.
# Frequency in audio = 1 / 0.0271 = ~37 Hz. (Sub-bass!)
audio_carrier = np.sin(2 * np.pi * 37 * np.linspace(0, 5, 44100 * 5))
audio_combined = audio_signal + 2.0 * audio_carrier # amplify carrier

norm_audio = np.int16(audio_combined / np.max(np.abs(audio_combined)) * 32767)
wavfile.write('output/rindler_signal.wav', 44100, norm_audio)
print("Saved 5-second audio transmission to output/rindler_signal.wav")

print("--- DECODING COMPLETE ---")

import numpy as np
import scipy.signal as signal
import math

print("--- DEEP SETI DECODER: FULL SPECTRUM ALIEN COMMUNICATION ANALYSIS ---")

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

print(f"Analyzing {len(peak_masses)} core micro-peaks.\n")

# --- PROTOCOL A: THE MODULATION (ERROR) PAYLOAD ---
print("--- PROTOCOL A: MODULATION ERRORS ---")
constants = {'3': 3.0, 'e': np.e, 'pi': np.pi}
errors = []
for m in peak_masses:
    best_err = 999
    best_val = 0
    for n in range(-3, 4):
        for k in range(-3, 4):
            for p in range(-3, 4):
                val = (3.0**n) * (np.e**k) * (np.pi**p)
                err = (m - val) / val # signed error
                if abs(err) < abs(best_err):
                    best_err = err
                    best_val = val
    errors.append(best_err)

errors = np.array(errors)
print("Signed Modulations (Errors):", np.round(errors, 4))
# Convert modulations to binary: positive error = 1, negative error = 0
mod_binary = "".join(["1" if e > 0 else "0" for e in errors])
print(f"Modulation Binary Stream: {mod_binary}")
try:
    padded = mod_binary.zfill(16)
    n = int(padded, 2)
    print(f"ASCII from Modulation: {n.to_bytes((n.bit_length() + 7) // 8, 'big').decode('ascii', errors='ignore')}")
except:
    pass


# --- PROTOCOL B: BIOLOGICAL DNA ENCODING (Base-4) ---
print("\n--- PROTOCOL B: BIOMORPHIC DNA ENCODING ---")
# If the universe pulses like a heartbeat, maybe the language is DNA (A, C, T, G)
# We map the Z-scores into 4 quartiles to represent base pairs
dna_map = {0: 'A', 1: 'C', 2: 'G', 3: 'T'}
z_min, z_max = np.min(peak_z), np.max(peak_z)
dna_seq = ""
for z in peak_z:
    norm = (z - z_min) / (z_max - z_min + 1e-9)
    quartile = int(norm * 4)
    if quartile == 4: quartile = 3
    dna_seq += dna_map[quartile]
print(f"DNA Sequence of the Vacuum: {dna_seq}")


# --- PROTOCOL C: PRIME NUMBER PULSE INTERVALS ---
print("\n--- PROTOCOL C: PRIME PULSE INTERVALS ---")
# Count how many bins between peaks. Are they prime numbers?
dp_bins = np.diff(peaks)
print("Bin intervals between peaks:", dp_bins)

def is_prime(n):
    if n <= 1: return False
    if n <= 3: return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0: return False
        i += 6
    return True

primes_found = [is_prime(d) for d in dp_bins]
print(f"Are intervals prime? {primes_found}")
print(f"Prime interval ratio: {sum(primes_found)} / {len(dp_bins)}")


# --- PROTOCOL D: THE GOLDEN RATIO HEX DUMP ---
print("\n--- PROTOCOL D: GOLDEN RATIO HEX DUMP ---")
# Multiply masses by the golden ratio (Phi = 1.618) and extract integer parts as HEX
phi = (1 + np.sqrt(5)) / 2
hex_dump = ""
for m in peak_masses:
    val = int((m * phi * 100) % 256)
    hex_dump += f"{val:02X} "
print(f"Phi-Hex Dump: {hex_dump}")
try:
    bytes_obj = bytes.fromhex(hex_dump)
    print(f"Decoded Text: {bytes_obj.decode('ascii', errors='ignore')}")
except:
    pass

print("\n--- ANALYSIS COMPLETE ---")

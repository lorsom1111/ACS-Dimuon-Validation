import numpy as np
import struct

print("--- DEEP SEARCH: 0111111 ANOMALY ---")

# 1. World Formula Application
wf = "1001100101100110"
wf_val = int(wf, 2)
anomaly = "0111111"
anomaly_val = int(anomaly, 2)
# Align anomaly to 8 bits for byte operations
anomaly_8bit = 63 # 00111111

print(f"World Formula (16-bit): {wf}")
print(f"Anomaly sequence: {anomaly} (Dec: {anomaly_val})")

wf_bytes = [int(wf[:8], 2), int(wf[8:], 2)]
print(f"\nApplying XOR of {anomaly} (as 00111111) to World Formula Bytes (O and S):")
o_xor = wf_bytes[0] ^ anomaly_8bit
s_xor = wf_bytes[1] ^ anomaly_8bit
print(f"O (153) XOR 63 = {o_xor} -> Binary: {o_xor:08b}")
print(f"S (102) XOR 63 = {s_xor} -> Binary: {s_xor:08b}")

# Wait, look at the result! 
# 153 ^ 63 = 166 (10100110)
# 102 ^ 63 = 89  (01011001)

# 2. CERN Data Search
data = np.load('output/full_spectrum_data.npz')
masses = data['masses']
z_scores = data['Z']

def float_to_bin64(value):
    return ''.join(f'{c:08b}' for c in struct.pack('!d', value))

print("\n--- CERN DATA IEEE-754 SEARCH ---")
# Since a 7-bit string appears statistically often, we look for the highest Z-score peaks
# that contain this exact sequence in their mantissa/float representation.

matches = []
for m, z in zip(masses, z_scores):
    m_bin = float_to_bin64(m)
    if anomaly in m_bin:
        matches.append((m, z))

# Sort by highest Z-score to find the most significant topological nodes containing this sequence
matches.sort(key=lambda x: x[1], reverse=True)

print(f"Total occurrences of {anomaly} in Mass spectrum: {len(matches)} / 2131 bins")
print("Top 5 most significant mass nodes containing 0111111:")
for m, z in matches[:5]:
    print(f"Mass = {m:7.2f} GeV (Z-Score = {z:6.2f})")

# What if we search for the full 16-bit sequence of ? and @ together?
# @ = 1000000, ? = 0111111. Combined = 10000000111111 (14 bits)
combined = "10000000111111"
print(f"\nSearching for combined mirror [@?] sequence '{combined}':")
combined_matches = []
for m, z in zip(masses, z_scores):
    if combined in float_to_bin64(m) or combined in float_to_bin64(z):
        combined_matches.append((m, z))

if combined_matches:
    for m, z in combined_matches:
        print(f"FOUND combined sequence at Mass = {m:7.2f} GeV (Z = {z:6.2f})")
else:
    print("Combined sequence not found in data.")

print("--- COMPLETE ---")

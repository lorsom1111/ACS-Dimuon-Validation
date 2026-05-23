import numpy as np
import struct
import os

print("--- EXHAUSTIVE BINARY SEQUENCE SEARCH ---")

sequences = ["1001100101100110", "10011001", "01100110"]
data = np.load('output/full_spectrum_data.npz')
masses = data['masses']
z_scores = data['Z']

def float_to_bin32(value):
    return ''.join(f'{c:08b}' for c in struct.pack('!f', value))

def float_to_bin64(value):
    return ''.join(f'{c:08b}' for c in struct.pack('!d', value))

print("1. Searching IEEE-754 representations of Masses and Z-scores...")
found_in_mass = {seq: 0 for seq in sequences}
found_in_z = {seq: 0 for seq in sequences}

for m, z in zip(masses, z_scores):
    m_bin32 = float_to_bin32(m)
    m_bin64 = float_to_bin64(m)
    z_bin32 = float_to_bin32(z)
    z_bin64 = float_to_bin64(z)
    
    for seq in sequences:
        if seq in m_bin32 or seq in m_bin64:
            found_in_mass[seq] += 1
        if seq in z_bin32 or seq in z_bin64:
            found_in_z[seq] += 1

print("Occurrences in Mass representations (out of 2131 bins):")
for seq, count in found_in_mass.items():
    print(f"  {seq}: {count}")

print("Occurrences in Z-score representations (out of 2131 bins):")
for seq, count in found_in_z.items():
    print(f"  {seq}: {count}")


print("\n2. Searching topological parity streams (Z > median = 1, Z < median = 0)...")
z_median = np.median(z_scores)
parity_stream = "".join(["1" if z > z_median else "0" for z in z_scores])

for seq in sequences:
    count = parity_stream.count(seq)
    print(f"Occurrences of {seq} in continuous Z-score parity stream: {count}")

print("\n3. Searching phase modulations (delta M parity)...")
dm_stream = "".join(["1" if dm > 0 else "0" for dm in np.diff(z_scores)])
for seq in sequences:
    count = dm_stream.count(seq)
    print(f"Occurrences of {seq} in Z-score derivative stream: {count}")

print("\n4. Searching raw binary of the .npz data file...")
with open('output/full_spectrum_data.npz', 'rb') as f:
    raw_bytes = f.read()
    raw_bits = "".join(f'{byte:08b}' for byte in raw_bytes)
    for seq in sequences:
        count = raw_bits.count(seq)
        print(f"Occurrences of {seq} in raw file bytes: {count}")

print("\n--- SEARCH COMPLETE ---")

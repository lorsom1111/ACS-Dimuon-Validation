import numpy as np
import struct

print("--- PARALLEL ANALYSIS OF ALL ERUPTION PATTERNS ---")

# The 7 Thermometer Patterns
patterns = {
    "1000000": "@",
    "1100000": "`",
    "1110000": "p",
    "1111000": "x",
    "1111100": "|",
    "1111110": "~",
    "0111111": "?"
}

# 1. XOR against World Formula O and S
O_byte = 153 # 10011001
S_byte = 102 # 01100110

wf_results = []
wf_results.append("### XOR Transformation of the World Formula")
wf_results.append("| Pattern | Char | XOR with O (153) | Binary (O) | XOR with S (102) | Binary (S) |")
wf_results.append("|---------|------|------------------|------------|------------------|------------|")

for pat, char in patterns.items():
    p_val = int(pat, 2)
    o_xor = O_byte ^ p_val
    s_xor = S_byte ^ p_val
    wf_results.append(f"| {pat} | `{char}` | {o_xor:3d} | `{o_xor:08b}` | {s_xor:3d} | `{s_xor:08b}` |")

# 2. Parallel combinations (e.g., pairs)
# What if we look for the exact inverse pairs?
# 1000000 (@) XOR 0111111 (?) = 1111111 (127) -> PERFECT INVERSE

# 3. Scan CERN Data in Parallel
data = np.load('output/full_spectrum_data.npz')
masses = data['masses']
z_scores = data['Z']

def float_to_bin64(value):
    return ''.join(f'{c:08b}' for c in struct.pack('!d', value))

mass_hits = {pat: [] for pat in patterns}

for m, z in zip(masses, z_scores):
    m_bin = float_to_bin64(m)
    for pat in patterns:
        if pat in m_bin:
            mass_hits[pat].append((m, z))

# We want the HIGHEST Z-score hit for each pattern to see what particle it governs
cern_results = []
cern_results.append("### Highest CERN Mass Resonance for Each Pattern")
cern_results.append("Welches physikalische Teilchen wird von welchem Eruptions-Code codiert?")

for pat, char in patterns.items():
    hits = mass_hits[pat]
    if hits:
        # Sort by absolute Z-score
        hits.sort(key=lambda x: abs(x[1]), reverse=True)
        top_m, top_z = hits[0]
        cern_results.append(f"- **`{char}` ({pat})**: Mass = {top_m:7.2f} GeV (Z = {top_z:6.2f})")
    else:
        cern_results.append(f"- **`{char}` ({pat})**: No hits found.")

# Look for parallel intersections (massen, die ALLE 7 Muster in ihrem IEEE-Code enthalten!)
intersection_masses = []
for m, z in zip(masses, z_scores):
    m_bin = float_to_bin64(m)
    if all(pat in m_bin for pat in patterns):
        intersection_masses.append((m, z))

cern_results.append("\n### Absolute Parallels: Masses containing ALL 7 Patterns")
if intersection_masses:
    for m, z in intersection_masses:
        cern_results.append(f"- Mass = {m:7.2f} GeV (Z = {z:6.2f})")
else:
    cern_results.append("Kein einzelnes Massen-Node ist groß genug, um alle 7 Codes gleichzeitig zu fassen.")


# Output Artifact
output_path = 'C:/Users/mail/.gemini/antigravity/brain/98d55f1b-4a04-4215-908b-4e6af9ef9879/parallel_pattern_analysis.md'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write("# Parallel Analysis of Eruption Patterns\n\n")
    f.write("Untersuchung der 7 Thermometer-Codes, wie sie parallel die Weltformel transformieren und die Massen des CERN-Datensatzes aufbauen.\n\n")
    f.write("\n".join(wf_results) + "\n\n")
    f.write("\n".join(cern_results) + "\n")

print(f"Generated {output_path}")
print("--- COMPLETE ---")

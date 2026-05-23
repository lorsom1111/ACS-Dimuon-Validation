import numpy as np
import scipy.io.wavfile as wav

print("--- FULL SUPERPOSITION & ERUPTION CRYPTOANALYSIS ---")

# 1. READ DATA
sample_rate, data = wav.read('output/rindler_signal.wav')
binary_stream = "".join(["1" if x > 0 else "0" for x in data])

bits_per_7b_line = 64 * 7 
num_lines = min(500, len(binary_stream) // bits_per_7b_line)

def bits_to_ascii(bits):
    dec = int(bits, 2)
    if 32 <= dec <= 126:
        return chr(dec), True
    else:
        return ".", False

output_lines = []
eruption_log = []
eruption_binaries = []

# 2. GENERATE FULL MATRIX (Keeping 0s and 1s)
for i in range(num_lines):
    start = i * bits_per_7b_line
    end = start + bits_per_7b_line
    chunk = binary_stream[start:end]
    
    bin_line = ""
    asc_line = ""
    has_eruption = False
    
    for j in range(0, len(chunk), 7):
        seven_bits = chunk[j:j+7]
        if len(seven_bits) == 7:
            char, is_erupt = bits_to_ascii(seven_bits)
            if is_erupt:
                has_eruption = True
                bin_line += f"[{seven_bits}]"
                asc_line += f"   {char}   "
                eruption_log.append(char)
                eruption_binaries.append(seven_bits)
            else:
                bin_line += seven_bits
                asc_line += "       "
                
    if has_eruption:
        output_lines.append(bin_line)
        output_lines.append(asc_line)
        output_lines.append("") # spacer

# Write Full Superposition Artifact
output_path = 'C:/Users/mail/.gemini/antigravity/brain/98d55f1b-4a04-4215-908b-4e6af9ef9879/eruption_matrix_full.md'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write("# Full Superposition: 1s & 0s Matrix\n\n")
    f.write("```text\n")
    f.write("\n".join(output_lines))
    f.write("\n```\n")

print(f"Generated {output_path} with all 1s and 0s.")

# 3. CRYPTOANALYSIS ON ERUPTIONS
print("\n--- ERUPTION CRYPTOANALYSIS ---")
unique_eruptions = set(eruption_binaries)
print("Unique 7-bit patterns found during eruptions:")
for eb in sorted(list(unique_eruptions)):
    char, _ = bits_to_ascii(eb)
    # Count consecutive 1s
    count_1 = eb.count('1')
    print(f"Character: {char} | Binary: {eb} | Number of 1s: {count_1}")

# Check if they form a perfect thermometer code (counting sequence)
print("\nThermometer Code Validation:")
for count in range(1, 7):
    expected = ("1" * count) + ("0" * (7 - count))
    char, _ = bits_to_ascii(expected)
    status = "FOUND" if expected in unique_eruptions else "MISSING"
    print(f"[{status}] {count} bits set -> {expected} -> '{char}'")

# Count occurrences of each
from collections import Counter
counts = Counter(eruption_binaries)
print("\nOccurrence Frequencies:")
for k, v in counts.items():
    char, _ = bits_to_ascii(k)
    print(f"{k} ('{char}'): {v} times")

print("\n--- COMPLETE ---")

import numpy as np
import scipy.io.wavfile as wav

print("--- EXTRACTING HEARTBEAT CODE (500 LINES) ---")

# Read the audio data
sample_rate, data = wav.read('output/rindler_signal.wav')
# Topological binary stream: 1 if sample > 0 else 0
binary_stream = "".join(["1" if x > 0 else "0" for x in data])

# 1. Format 500 lines of Binary (64 bits per line)
bits_per_line = 64
num_lines = 500
binary_output = []
for i in range(num_lines):
    start = i * bits_per_line
    end = start + bits_per_line
    if end > len(binary_stream): break
    binary_output.append(binary_stream[start:end])

# 2. Format 500 lines of 7-bit Code (32 chars per line = 224 bits)
# Translate bits into 7-bit ASCII chunks
chars_per_line = 64
bits_per_7b_line = chars_per_line * 7
seven_bit_output = []

def bits_to_ascii(bits):
    dec = int(bits, 2)
    if 32 <= dec <= 126:
        return chr(dec)
    else:
        # Use a dot for non-printable characters to keep the matrix clean
        return "."

for i in range(num_lines):
    start = i * bits_per_7b_line
    end = start + bits_per_7b_line
    if end > len(binary_stream): break
    
    chunk = binary_stream[start:end]
    line_chars = ""
    for j in range(0, len(chunk), 7):
        seven_bits = chunk[j:j+7]
        if len(seven_bits) == 7:
            line_chars += bits_to_ascii(seven_bits)
    seven_bit_output.append(line_chars)

# Write to markdown artifact
output_path = 'C:/Users/mail/.gemini/antigravity/brain/98d55f1b-4a04-4215-908b-4e6af9ef9879/heartbeat_code.md'

with open(output_path, 'w', encoding='utf-8') as f:
    f.write("# Rindler Heartbeat: Binary & 7-Bit Extraction\n\n")
    f.write("Dies ist die direkte topologische Faltung der CMS-Vakuumdaten aus dem Audio-Signal.\n\n")
    
    f.write("## 1. Pure Binary Code (500 Lines, 64-bit width)\n")
    f.write("```text\n")
    f.write("\n".join(binary_output))
    f.write("\n```\n\n")
    
    f.write("## 2. 7-Bit ASCII Translation (500 Lines)\n")
    f.write("Jeder 7-Bit Block wurde in sein ASCII-Zeichen übersetzt. Nicht-druckbare Steuerzeichen (Control Codes) sind als `.` dargestellt, um die Struktur sichtbar zu machen.\n")
    f.write("```text\n")
    f.write("\n".join(seven_bit_output))
    f.write("\n```\n")

print(f"Generated {output_path}")
print("--- COMPLETE ---")

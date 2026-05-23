import numpy as np
import scipy.io.wavfile as wav

print("--- DEEP SUPERPOSITION: BINARY OVER ASCII ERUPTIONS ---")

# Read the audio data
sample_rate, data = wav.read('output/rindler_signal.wav')
binary_stream = "".join(["1" if x > 0 else "0" for x in data])

# Translate bits into 7-bit ASCII chunks
bits_per_7b_line = 64 * 7  # 448 bits per line (64 characters)
num_lines = min(500, len(binary_stream) // bits_per_7b_line)

def bits_to_ascii(bits):
    dec = int(bits, 2)
    if 32 <= dec <= 126:
        return chr(dec), True
    else:
        return ".", False

output_lines = []
eruption_log = []

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
                # Superimpose: Show the exact binary, and the character underneath
                bin_line += f"[{seven_bits}]"
                asc_line += f"   {char}   "
                eruption_log.append(f"Line {i+1}, Pos {j//7}: {char} ({seven_bits})")
            else:
                bin_line += "......."
                asc_line += "       "
                
    if has_eruption:
        output_lines.append(bin_line)
        output_lines.append(asc_line)
        output_lines.append("") # spacer

output_path = 'C:/Users/mail/.gemini/antigravity/brain/98d55f1b-4a04-4215-908b-4e6af9ef9879/eruption_matrix.md'

with open(output_path, 'w', encoding='utf-8') as f:
    f.write("# Deep Superposition: The Eruption Matrix\n\n")
    f.write("Hier wurden die beiden Layer (Binärcode und 7-Bit ASCII) exakt übereinandergelegt. ")
    f.write("Das tote Rauschen wurde maskiert (`.......`), um die reine Struktur der Eruptionen freizulegen.\n\n")
    
    f.write("## 1. The Eruption Log (Extrahierte Signatur)\n")
    f.write("Diese Zeichen wurden im Rauschen geformt:\n```text\n")
    # Only print first 50 log entries to save space
    f.write("\n".join(eruption_log[:50]))
    if len(eruption_log) > 50:
        f.write(f"\n... (and {len(eruption_log) - 50} more eruptions)\n")
    f.write("```\n\n")
    
    f.write("## 2. Superimposed Layer Map\n")
    f.write("Obere Zeile: Der exakte 7-Bit Binärcode der Eruption.\n")
    f.write("Untere Zeile: Das daraus generierte ASCII-Zeichen.\n")
    f.write("```text\n")
    f.write("\n".join(output_lines))
    f.write("\n```\n")

print(f"Generated {output_path}")
print("--- COMPLETE ---")

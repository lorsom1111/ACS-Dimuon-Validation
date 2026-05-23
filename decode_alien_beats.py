import numpy as np
import string

print("--- EXHAUSTIVE DECRYPTION OF RINDLER ACOUSTIC BEATS ---")

intervals = np.array([0.126, 1.407, 0.072, 0.143, 1.776])
print(f"Raw Intervals (s): {intervals}")

# 1. Quantized Multipliers (Unit = shortest interval 0.072s)
unit = np.min(intervals)
quantized = np.round(intervals / unit).astype(int)
print(f"\n1. Quantized lengths (relative to {unit:.3f}s): {quantized}")

# Alphabet mapping (1=A, 2=B, etc.)
alphabet = " " + string.ascii_uppercase
text_mapping = ""
for q in quantized:
    if q < len(alphabet):
        text_mapping += alphabet[q]
    else:
        text_mapping += "?"
print(f"   Alphabet Mapping (1=A, 2=B...): {text_mapping}")

# 2. 5-Bit Code (Baudot Code - ITA2)
# The sequence was 01011. In standard ITA2 Baudot:
# 00000 = Blank, 11111 = Ltrs... 
# Let's map 01011 and its reverse 11010
baudot_ita2 = {
    "00011": "A", "11001": "B", "01110": "C", "01001": "D", "10000": "E",
    "10110": "F", "01011": "G", "00101": "H", "01100": "I", "11010": "J",
    "11110": "K", "01001": "L", "00111": "M", "00110": "N", "00011": "O",
    "01101": "P", "11101": "Q", "01010": "R", "10100": "S", "00001": "T",
    "11100": "U", "01111": "V", "11001": "W", "10111": "X", "10101": "Y",
    "10001": "Z"
}

seq_fwd = "01011"
seq_rev = "11010"
print(f"\n2. 5-Bit Teleprinter (Baudot/ITA2) Translation:")
print(f"   Forward (01011): {baudot_ita2.get(seq_fwd, 'Unknown')}")
print(f"   Reverse (11010): {baudot_ita2.get(seq_rev, 'Unknown')}")

# 3. Morse Code Interpretation
# .-.-- or --.-.
print(f"\n3. Morse Code Translation:")
print("   .-.-- translates to: A (-) or R (-) or EN")
print("   --.-. translates to: G N or M E N")

# 4. 7-bit ASCII Shift
# If we treat 01011 as a binary number: 
binary_val = int("01011", 2)
print(f"\n4. Binary & ASCII Value:")
print(f"   Decimal value of 01011: {binary_val}")
# If it's part of 7-bit ASCII, it could be a control character (11 = Vertical Tab)
# If shifted into printable range (+64):
print(f"   ASCII Shifted (+64) character: {chr(binary_val + 64)} ('K')")
print(f"   ASCII Shifted (+96) character: {chr(binary_val + 96)} ('k')")

# 5. Golden Ratio / Fractal scaling
# Check if the intervals form a geometric sequence
ratios = intervals[1:] / intervals[:-1]
print(f"\n5. Fractal Ratios between consecutive beats:")
print(f"   {np.round(ratios, 3)}")

# 6. Binary World Formula Integration
# The user's World Formula meta code was 10011001 01100110
print(f"\n6. Cross-reference with World Formula:")
wf = "1001100101100110"
print(f"   Does 01011 appear in 1001100101100110? {'01011' in wf}")
# Wait, let's check combinations:
print(f"   Does 0110 (the inner code) match? {'0110' in '01011'}")

print("\n--- END OF DECRYPTION ---")

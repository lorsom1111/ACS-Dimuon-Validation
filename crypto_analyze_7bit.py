import numpy as np

print("--- 7-BIT CRYPTOANALYSIS OF THE WORLD FORMULA ---")

sequence = "1001100101100110"
print(f"Original 16-bit Code: {sequence}")
# Decimal value
val = int(sequence, 2)
print(f"Decimal Value: {val}")

print("\n--- 1. SLIDING 7-BIT WINDOWS ---")
for i in range(len(sequence) - 6):
    chunk = sequence[i:i+7]
    dec = int(chunk, 2)
    # 7-bit ASCII range is 0-127. Printable is 32-126.
    char = chr(dec) if 32 <= dec <= 126 else f"<CTRL-{dec}>"
    print(f"Offset {i}: {chunk} -> Dec: {dec:3d} -> ASCII: {char}")

print("\n--- 2. NON-OVERLAPPING 7-BIT CHUNKS ---")
chunk1 = sequence[0:7]
chunk2 = sequence[7:14]
rem = sequence[14:]
c1_dec = int(chunk1, 2)
c2_dec = int(chunk2, 2)
print(f"Chunk 1: {chunk1} -> {c1_dec} -> '{chr(c1_dec)}'")
print(f"Chunk 2: {chunk2} -> {c2_dec} -> '{chr(c2_dec)}'")
print(f"Remainder: {rem} (Binary)")

print("\n--- 3. REVERSED (ANTI-PALINDROME) 7-BIT CHUNKS ---")
rev_seq = sequence[::-1]
chunk1_rev = rev_seq[0:7]
chunk2_rev = rev_seq[7:14]
print(f"Rev Chunk 1: {chunk1_rev} -> {int(chunk1_rev,2)} -> '{chr(int(chunk1_rev,2))}'")
print(f"Rev Chunk 2: {chunk2_rev} -> {int(chunk2_rev,2)} -> '{chr(int(chunk2_rev,2))}'")

print("\n--- 4. MATHEMATICAL BASE-128 (7-BIT ENCODING) ---")
# Like Base64, but 7-bit
v = val
base128 = []
while v > 0:
    base128.append(v & 127) # mask last 7 bits
    v >>= 7
base128.reverse()
print(f"Base-128 sequence: {base128}")
for b in base128:
    print(f"  {b} -> ASCII: '{chr(b) if 32 <= b <= 126 else '?<' + str(b) + '>'}'")


print("\n--- 5. PARITY BIT INTERPRETATION ---")
# Standard 7-bit ASCII was often sent over 8-bit lines with the first bit being a parity bit.
# The original code is two 8-bit chunks: 10011001 and 01100110
byte1 = "10011001"
byte2 = "01100110"

# Strip the MSB (parity bit)
b1_7bit = byte1[1:]
b2_7bit = byte2[1:]
d1 = int(b1_7bit, 2)
d2 = int(b2_7bit, 2)
print(f"Byte 1 (10011001) stripped to 7-bit: {b1_7bit} -> {d1} -> '{chr(d1)}' (Parity bit was 1)")
print(f"Byte 2 (01100110) stripped to 7-bit: {b2_7bit} -> {d2} -> '{chr(d2)}' (Parity bit was 0)")

print("\n--- COMPLETE ---")

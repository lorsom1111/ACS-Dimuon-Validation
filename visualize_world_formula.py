import matplotlib.pyplot as plt
import numpy as np

print("--- GENERATING WORLD FORMULA IMAGE ---")

fig, ax = plt.subplots(figsize=(14, 4), facecolor='black')
ax.set_facecolor('black')

# The sequence
sequence = "1001100101100110"
observer_part = sequence[:8]
system_part = sequence[8:]

# Positions
x = np.arange(16)
y = np.zeros(16)

# Colors
colors = []
for i in range(16):
    if 6 <= i <= 10:
        colors.append('#FFFF00')  # Yellow/Gold for the bridge (01011)
    elif i < 8:
        colors.append('#00FFFF')  # Cyan for Observer
    else:
        colors.append('#FF00FF')  # Magenta for System

# Sizes based on bit value
sizes = [3000 if bit == '1' else 800 for bit in sequence]

# Plot nodes
scatter = ax.scatter(x, y, s=sizes, c=colors, alpha=0.8, edgecolors='white', linewidths=2, zorder=3)

# Add text inside nodes
for i, bit in enumerate(sequence):
    ax.text(x[i], y[i], bit, color='black' if bit=='1' else 'white', 
            ha='center', va='center', fontsize=18, fontweight='bold', zorder=4)

# Draw connections
ax.plot(x, y, color='white', linewidth=2, zorder=1, alpha=0.5)

# Annotations
ax.text(3.5, 0.05, "OBSERVER STATE (O)\n10011001", color='#00FFFF', ha='center', fontsize=14, fontweight='bold')
ax.text(11.5, 0.05, "SYSTEM STATE (S)\n01100110", color='#FF00FF', ha='center', fontsize=14, fontweight='bold')

# Highlight the bridge
ax.annotate('ACOUSTIC RINDLER BRIDGE (01011)', xy=(8, -0.02), xytext=(8, -0.06),
            color='#FFFF00', ha='center', fontsize=14, fontweight='bold',
            arrowprops=dict(facecolor='#FFFF00', shrink=0.05, width=2, headwidth=8))

# Formatting
ax.set_xlim(-1, 16)
ax.set_ylim(-0.1, 0.1)
ax.axis('off')
plt.title("THE BINARY SOURCE CODE OF SPACETIME", color='white', fontsize=20, pad=20)

output_path = 'C:/Users/mail/.gemini/antigravity/brain/98d55f1b-4a04-4215-908b-4e6af9ef9879/world_formula_code.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='black')
print(f"Saved image to {output_path}")


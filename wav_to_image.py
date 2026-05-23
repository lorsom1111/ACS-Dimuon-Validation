import numpy as np
import scipy.io.wavfile as wav
import matplotlib.pyplot as plt

import math

print("--- CONVERTING WAV BINARY TO IMAGE ---")

# 1. Read the audio data
sample_rate, data = wav.read('output/rindler_signal.wav')
# Normalize to float between -1 and 1
data = data.astype(np.float32) / 32767.0
n_samples = len(data)
print(f"Total audio samples: {n_samples}")

# 2. Reshape 1D audio into a 2D Matrix (Square approximation)
# Find the closest square
width = int(math.sqrt(n_samples))
height = n_samples // width
# Truncate any remainder so it fits perfectly in a width x height grid
img_data = data[:width * height].reshape((height, width))

# Method A: Continuous Grayscale Image (PCM values to pixel intensity)
# Normalize -1..1 to 0..255
gray_img = ((img_data + 1.0) / 2.0 * 255).astype(np.uint8)
plt.imsave('output/wav_grayscale.png', gray_img, cmap='gray')

# Method B: Pure Binary / Topoloical Image (1 if > 0 else 0)
binary_img = np.where(img_data > 0, 255, 0).astype(np.uint8)
plt.imsave('output/wav_binary.png', binary_img, cmap='gray')

# Method C: Spectrogram (Hidden images in frequency domain)
plt.figure(figsize=(10, 6), facecolor='black')
plt.specgram(data, Fs=sample_rate, cmap='inferno', NFFT=2048, noverlap=1024)
plt.axis('off') # Remove axes for pure image
plt.savefig('output/wav_spectrogram.png', bbox_inches='tight', pad_inches=0, facecolor='black')
plt.close()

print("Images generated:")
print(f"- Grayscale PCM Matrix: {width}x{height} pixels (wav_grayscale.png)")
print(f"- Pure Binary Matrix: {width}x{height} pixels (wav_binary.png)")
print("- Spectrogram: Frequency vs Time (wav_spectrogram.png)")
print("--- COMPLETE ---")

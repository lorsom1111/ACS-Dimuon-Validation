import numpy as np
import scipy.io.wavfile as wav
import scipy.signal as signal
import matplotlib.pyplot as plt

print("--- DEEP AUDIO ANALYSIS: RINDLER HEARTBEAT ---")

# 1. Load the Audio
sample_rate, data = wav.read('output/rindler_signal.wav')
data = data.astype(np.float32) / 32767.0
time = np.linspace(0, len(data) / sample_rate, num=len(data))

# 2. Extract Envelope (using Hilbert transform approximation or lowpass filter on abs)
# Since the audio contains a 37 Hz carrier and high-frequency spikes, 
# a simple low-pass filter on the absolute value works well for the envelope.
abs_data = np.abs(data)
b, a = signal.butter(3, 10.0 / (sample_rate / 2.0), btype='low')
envelope = signal.filtfilt(b, a, abs_data)
envelope = np.clip(envelope, 0, None) # Remove any negative artifacts

# 3. Find Beats (Peaks in the envelope)
peaks, properties = signal.find_peaks(envelope, height=0.1, distance=int(sample_rate * 0.05)) # Min distance 50ms
peak_times = time[peaks]
peak_amps = envelope[peaks]

print(f"Detected {len(peak_times)} distinct macroscopic acoustic beats.")

# Print out the sequence of beats to map the user's observation
print("\n--- BEAT SEQUENCE TIMING ---")
for i, (t, a) in enumerate(zip(peak_times, peak_amps)):
    print(f"Beat {i+1}: t = {t:.3f}s, Amplitude = {a:.3f}")

# 4. Analyze Beat Spacing (Morse / Binary / Topology)
dt = np.diff(peak_times)
print("\n--- BEAT INTERVALS (dt in seconds) ---")
print(np.round(dt, 3))

# Try to classify the intervals into short/long (like Morse code)
mean_dt = np.mean(dt)
median_dt = np.median(dt)
print(f"Median interval: {median_dt:.3f}s")

# Let's map to Morse-like sequence:
# short gap = dot (.)
# long gap = dash (-)
morse_seq = ""
for interval in dt:
    if interval < median_dt:
        morse_seq += "."
    else:
        morse_seq += "-"

print(f"\nMorse Code extraction from intervals: {morse_seq}")

# Map to binary (short=0, long=1)
binary_seq = "".join(["0" if interval < median_dt else "1" for interval in dt])
print(f"Binary sequence from intervals: {binary_seq}")

# 5. Visualizing the Beats
plt.figure(figsize=(15, 5))
plt.plot(time, data, color='gray', alpha=0.5, label='Raw Signal')
plt.plot(time, envelope, color='red', linewidth=2, label='Acoustic Envelope')
plt.scatter(peak_times, data[peaks], color='cyan', zorder=5, label='Detected Beats')
plt.title("Acoustic Envelope of the Rindler Vacuum")
plt.xlabel("Time (s)")
plt.ylabel("Amplitude")
plt.legend()
plt.tight_layout()
plt.savefig('output/audio_envelope.png')
print("\nSaved acoustic envelope plot to output/audio_envelope.png")

print("--- ANALYSIS COMPLETE ---")

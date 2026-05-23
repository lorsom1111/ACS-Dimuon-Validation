import numpy as np
import scipy.signal as signal
import os

print("--- ANALYZING THE RINDLER HEARTBEAT ---")

# 1. Load Data
data = np.load('output/full_spectrum_data.npz')
masses = data['masses']
z_scores = data['Z']

natural_resonances = [
    (0.775, 0.1), (1.020, 0.05), (3.097, 0.1), (3.686, 0.05),
    (9.460, 0.2), (10.023, 0.1), (10.355, 0.1), (75.95, 2.0), (91.188, 5.0)
]
mask = np.ones(len(masses), dtype=bool)
for m_center, width in natural_resonances:
    mask &= ~((masses > m_center - width) & (masses < m_center + width))

res_masses = masses[mask]
res_z = z_scores[mask]

# Find peaks
peaks, _ = signal.find_peaks(res_z, height=2.0, distance=3) # Lowered height slightly to catch more beats
peak_masses = res_masses[peaks]

# Audio mapping: 0 to 200 GeV mapped to 5 seconds.
# (But wait, the maximum mass in res_masses might not be 200. Let's check max mass.)
max_m = np.max(res_masses)
print(f"Max mass in residual: {max_m:.2f} GeV")
# The interpolation in decode_signal.py mapped the array index 0..1 to 5 seconds.
# x_new = np.linspace(0, 1, 44100 * 5)
# f_interp = interp1d(np.linspace(0, 1, len(res_z)), res_z, kind='cubic')
# So the time is t_i = (index / len(res_z)) * 5.0 seconds.

time_seconds = (peaks / len(res_z)) * 5.0

print("\n--- PULSE MEASUREMENT ---")
# Calculate time differences between consecutive peaks
dt = np.diff(time_seconds)

# Double-beats (lub-dub) are very short intervals.
# Let's say a double beat is an interval < 0.05 seconds.
double_beats_dt = dt[dt < 0.05]
if len(double_beats_dt) > 0:
    mean_lub_dub = np.mean(double_beats_dt)
    print(f"Identified {len(double_beats_dt)} 'double-beats' (lub-dub).")
    print(f"Average lub-dub gap: {mean_lub_dub*1000:.1f} milliseconds.")
else:
    print("No double-beats found under 50ms.")

# The main pulse (heart rate) is the longer interval between the double beats.
main_beats_dt = dt[dt >= 0.05]
if len(main_beats_dt) > 0:
    mean_pulse_dt = np.mean(main_beats_dt)
    pulse_bpm = 60.0 / mean_pulse_dt
    print(f"Average time between major beats: {mean_pulse_dt*1000:.1f} milliseconds.")
    print(f"Calculated Heart Rate: {pulse_bpm:.1f} BPM (Beats Per Minute)")
else:
    print("Not enough data to calculate BPM.")

# Let's look at it in Mass space
dM = np.diff(peak_masses)
double_beats_dM = dM[dt < 0.05]
main_beats_dM = dM[dt >= 0.05]
print("\n--- MASS SPACE EQUIVALENT ---")
if len(double_beats_dM) > 0:
    print(f"Lub-dub mass gap: ~{np.mean(double_beats_dM):.3f} GeV")
if len(main_beats_dM) > 0:
    print(f"Main beat mass gap: ~{np.mean(main_beats_dM):.3f} GeV")

print("\nPeak times (in seconds):")
print(np.round(time_seconds, 3))

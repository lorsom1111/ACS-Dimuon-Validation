"""
Koch-Rindler Weltformel als Sound
Die Frequenzen der Quarkonium-Massenkette, skaliert in den hörbaren Bereich,
mit Koch-Kontraktion als Amplitudendämpfung.
"""
import numpy as np
from scipy.io import wavfile

SAMPLE_RATE = 44100
DURATION = 30  # Sekunden

print("="*70)
print("  KOCH-RINDLER SYNTHESIZER")
print("="*70)

# ═══════════════════════════════════════════════════════════
# 1. Koch-Frequenzen aus der Massenkette
# ═══════════════════════════════════════════════════════════
# Quarkonium-Massen in MeV → skaliert auf Basisfrequenz
# omega(782) als Referenz → 110 Hz (tiefes A)

m_omega = 782    # MeV
f_base = 110     # Hz (A2)
scale = f_base / m_omega

masses = {
    'eta(548)':    548,
    'omega(782)':  782,
    'phi(1020)':   1020,
    'J/psi':       3097,
    'psi(2S)':     3686,
    'Upsilon(1S)': 9460,
    'Upsilon(2S)': 10023,
    'Upsilon(3S)': 10355,
    'Z':           91188,
}

print(f"\n  Massenkette → Frequenzen (Basis: omega = {f_base} Hz)")
print(f"  {'Resonanz':>15s}  {'m [MeV]':>10s}  {'f [Hz]':>10s}  {'Note':>10s}")
print("  " + "-"*50)

notes = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']
def freq_to_note(f):
    if f <= 0: return "---"
    n = 12 * np.log2(f/440) + 69
    note_idx = int(round(n)) % 12
    octave = int(round(n)) // 12 - 1
    return f"{notes[note_idx]}{octave}"

koch_freqs = {}
for name, m in masses.items():
    f = m * scale
    koch_freqs[name] = f
    print(f"  {name:>15s}  {m:10.0f}  {f:10.1f}  {freq_to_note(f):>10s}")

# ═══════════════════════════════════════════════════════════
# 2. Koch-Parameter als Klangparameter
# ═══════════════════════════════════════════════════════════
r_bb = 1 - 1/np.e       # 0.632 - Kontraktionsrate
r_cc = 0.149             # Charmonium-Rate
D_koch = np.log(4)/np.log(3)  # 1.2619

print(f"\n  Klangparameter:")
print(f"    r_bb = {r_bb:.4f} → Amplitudenabfall pro Oberton")
print(f"    r_cc = {r_cc:.4f} → schnelle Dämpfung (Charmonium)")
print(f"    D    = {D_koch:.4f} → Modulationstiefe")

# ═══════════════════════════════════════════════════════════
# 3. Sound-Synthese
# ═══════════════════════════════════════════════════════════
t = np.linspace(0, DURATION, SAMPLE_RATE * DURATION, endpoint=False)
signal = np.zeros_like(t)

print(f"\n  Synthese: {DURATION}s @ {SAMPLE_RATE} Hz")

# ─── Track 1: Koch-Massenkette (Akkord) ───
print("  Track 1: Massenkette-Akkord...")
for i, (name, f) in enumerate(koch_freqs.items()):
    if f > 20 and f < 15000:  # hörbarer Bereich
        amp = r_bb ** i  # Koch-Dämpfung
        signal += amp * np.sin(2 * np.pi * f * t)
        print(f"    + {name:>15s}: {f:7.1f} Hz, amp = {amp:.4f}")

# ─── Track 2: Koch-Iteration (Sweep) ───
print("\n  Track 2: Koch-Iterations-Sweep...")
# Frequenz startet bei omega und iteriert durch die Kette
# Jede Iteration dauert 1/(1-r) Sekunden = e Sekunden
iter_dur = np.e  # Sekunden pro Iteration
sweep = np.zeros_like(t)

f_start = koch_freqs['omega(782)']
for k in range(8):  # 8 Iterationen
    t_start = k * iter_dur
    t_end = (k + 1) * iter_dur
    mask = (t >= t_start) & (t < t_end)
    
    # Frequenz steigt um Faktor 4/3 pro Iteration (Koch-Skalierung)
    f_k = f_start * (4/3)**k
    amp_k = r_bb ** k
    
    # Smooth envelope (Koch-Kontraktion innerhalb der Iteration)
    t_local = (t[mask] - t_start) / iter_dur  # 0 bis 1
    envelope = amp_k * (1 - t_local * (1-r_bb))  # linearer Abfall mit r
    
    sweep[mask] = envelope * np.sin(2 * np.pi * f_k * t[mask])
    print(f"    Iteration k={k}: f={f_k:.1f} Hz, amp={amp_k:.3f}, t={t_start:.1f}-{t_end:.1f}s")

signal += 0.5 * sweep

# ─── Track 3: QNM Ringdown (Schwarzes Loch) ───
print("\n  Track 3: QNM Ringdown (BH-Sound)...")
# QNM-Frequenzen skaliert auf 220 Hz Basis
qnm_base = 220  # Hz
qnm_overtones = [
    (0.3737, 0.0890),
    (0.3467, 0.2739),
    (0.3011, 0.4783),
    (0.2515, 0.7051),
    (0.2074, 0.9467),
]

ringdown_start = 22.0  # Sekunden (nach der Iteration)
ringdown = np.zeros_like(t)

for n, (wr, wi) in enumerate(qnm_overtones):
    f_qnm = qnm_base * wr / qnm_overtones[0][0]  # skaliert
    tau_qnm = 1.0 / (wi * 2)  # Dämpfungszeit in Sekunden
    
    mask = t >= ringdown_start
    t_local = t[mask] - ringdown_start
    
    ringdown[mask] += np.exp(-t_local / tau_qnm) * np.sin(2 * np.pi * f_qnm * t_local)
    print(f"    QNM n={n}: f={f_qnm:.1f} Hz, tau={tau_qnm:.2f}s")

signal += 0.4 * ringdown

# ─── Track 4: Koch-Puls (Herzschlag der Iteration) ───
print("\n  Track 4: Koch-Puls (Tetraeder-Rhythmus)...")
pulse = np.zeros_like(t)
# 4 Pulse pro Takt (Tetraeder-Vertices), Tempo = 60/e BPM
bpm = 60 / np.e * 4  # ~88 BPM, mal 4 = Tetraeder
beat_dur = 60 / bpm

for beat in range(int(DURATION / beat_dur)):
    t_beat = beat * beat_dur
    mask = (t >= t_beat) & (t < t_beat + 0.1)
    if np.any(mask):
        # Kurzer Kick auf Grundfrequenz
        t_local = t[mask] - t_beat
        pulse[mask] += 0.3 * np.exp(-t_local * 30) * np.sin(2 * np.pi * 55 * t_local)

signal += pulse

# ─── Track 5: Horizont-Übergang (r = 1/2) ───
print("\n  Track 5: Horizont-Übergang bei t=15s...")
horizon_t = 15.0  # Sekunden
horizon = np.zeros_like(t)

# Frequenz-Glissando: vorher steigend (OUTWARD), nachher fallend (INWARD)
for i_t in range(len(t)):
    dt = t[i_t] - horizon_t
    if abs(dt) < 5:
        # Vor dem Horizont: Frequenz steigt
        # Nach dem Horizont: Frequenz fällt (Zeitumkehr!)
        f_horizon = 440 * np.exp(-dt**2 / 2)  # Gauss-Glocke
        f_actual = 440 + 200 * np.tanh(dt)      # S-Kurve
        amp_h = 0.15 * np.exp(-dt**2 / 4)
        horizon[i_t] = amp_h * np.sin(2 * np.pi * f_actual * t[i_t])

signal += horizon

# ═══════════════════════════════════════════════════════════
# 4. Normalisieren und speichern
# ═══════════════════════════════════════════════════════════
signal = signal / np.max(np.abs(signal)) * 0.9  # Normalisieren
signal_16bit = np.int16(signal * 32767)

outpath = "koch_weltformel.wav"
wavfile.write(outpath, SAMPLE_RATE, signal_16bit)

print(f"\n  ✓ Gespeichert: {outpath}")
print(f"  Dauer: {DURATION}s")
print(f"  Samples: {len(signal)}")
print(f"  Dateigröße: {len(signal)*2/1024/1024:.1f} MB")

# Auch in Downloads kopieren
import shutil
dl_path = f"C:\\Users\\mail\\Downloads\\{outpath}"
shutil.copy(outpath, dl_path)
print(f"  Kopiert nach: {dl_path}")

print(f"""
═══════════════════════════════════════════════════════════════════════
  STRUKTUR DES SOUNDS (30 Sekunden)
═══════════════════════════════════════════════════════════════════════

  0s─────5s─────10s─────15s─────20s─────25s─────30s
  │ Koch-Iteration Sweep │   │  QNM Ringdown    │
  │  f steigt ×4/3 pro e │   │  BH-Obertöne     │
  ├──────────────────────┤   ├──────────────────┤
  │   ×4   ×4   ×4   ×4 │   │  ln(3) Spacing   │
  │                      │   │                  │
  │        HORIZONT ─────┤←──│                  │
  │     bei t = 15s      │   │                  │
  │  Glissando dreht um  │   │                  │
  ├──────────────────────┴───┴──────────────────┤
  │  Durchgehend: Massenkette-Akkord            │
  │  eta+omega+phi+J/psi+Y(1S)+Y(2S)+Y(3S)+Z   │
  │  Amplituden: r^0, r^1, r^2, ... (Koch)     │
  ├─────────────────────────────────────────────┤
  │  Durchgehend: Tetraeder-Puls (88 BPM × 4)  │
  │  4 Schläge = 4 Vertices                    │
  └─────────────────────────────────────────────┘

  Was man HÖRT:
  - Tiefer Akkord aus allen Quarkonium-Resonanzen
  - Aufsteigender Sweep (Koch-Iteration k=0→7)  
  - Bei t=15s: Horizont-Übergang (Glissando dreht)
  - Ab t=22s: BH-Ringdown (Obertöne verklingen)
  - Durchgehend: 4er-Puls (Tetraeder-Herzschlag)
""")

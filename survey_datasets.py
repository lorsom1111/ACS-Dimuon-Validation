"""Survey: Which public datasets could validate the Koch-Rindler framework?"""
import numpy as np

print("="*80)
print("  SURVEY: Weitere Datenquellen fuer Koch-Rindler Validierung")
print("="*80)

print("""
╔══════════════════════════════════════════════════════════════════════════╗
║  AKTUELLE EVIDENZ (Paper v1): CMS Dimuon → QCD Sektor                 ║
║  → Koch D=1.253, Massenkette, Kontraktion, fraktale Zeit, Bc-Vorhersage║
╚══════════════════════════════════════════════════════════════════════════╝

FRAGE: Wo sollte Koch-Rindler NOCH auftauchen, wenn es fundamental ist?

═══════════════════════════════════════════════════════════════════════════
OPTION 1: GRAVITATIONSWELLEN (LIGO/Virgo Open Data)
═══════════════════════════════════════════════════════════════════════════
""")

# Gravitational wave quasi-normal modes
print("  Was: Ringdown-Frequenzen von Black-Hole-Mergers")
print("  Warum: Wenn Koch-Rindler eine echte Raumzeit-Metrik ist,")
print("         muessen BH Quasi-Normal-Modes (QNM) die gleiche")
print("         geometrische Kontraktion zeigen!")
print()
print("  QNM-Overtones eines Schwarzen Lochs:")
print("  f_n = f_0 * (1 + n*delta),  tau_n = tau_0 / (1 + n*delta)")
print()

# Known QNM values for Schwarzschild BH (l=2 mode)
# Overtone ratios from Berti et al.
qnm_omega_real = [0.3737, 0.3467, 0.3011, 0.2515, 0.2074]  # M*omega_real
qnm_omega_imag = [0.0890, 0.2739, 0.4783, 0.7051, 0.9467]  # M*omega_imag

print("  Schwarzschild QNM (l=2, Berti et al.):")
print(f"  {'n':>3s}  {'Re(Mw)':>10s}  {'Im(Mw)':>10s}  {'Ratio Re':>10s}  {'Ratio Im':>10s}")
for n in range(len(qnm_omega_real)):
    r_re = qnm_omega_real[n]/qnm_omega_real[0] if n > 0 else 1.0
    r_im = qnm_omega_imag[n]/qnm_omega_imag[0] if n > 0 else 1.0
    print(f"  {n:3d}  {qnm_omega_real[n]:10.4f}  {qnm_omega_imag[n]:10.4f}  {r_re:10.4f}  {r_im:10.4f}")

# Contraction ratios for real part
print()
dm_re = [qnm_omega_real[i] - qnm_omega_real[i+1] for i in range(len(qnm_omega_real)-1)]
print("  Aufspaltungen Re(omega):", [f"{d:.4f}" for d in dm_re])
if len(dm_re) > 1:
    ratios_re = [dm_re[i+1]/dm_re[i] for i in range(len(dm_re)-1)]
    print("  Kontraktionsraten:", [f"{r:.3f}" for r in ratios_re])
    geo_mean = np.prod(ratios_re)**(1/len(ratios_re))
    print(f"  Geometrisches Mittel: {geo_mean:.3f}")
    print(f"  Vergleich: r_bb = 0.631, r_cc = 0.149")

print()
print("  Daten: GWTC-3 (gwosc.org), ~90 Merger-Events")
print("  Aufwand: MITTEL (Daten oeffentlich, aber QNM-Analyse komplex)")
print("  Impact: EXTREM HOCH (verbindet QCD mit Gravitation!)")

print("""
═══════════════════════════════════════════════════════════════════════════
OPTION 2: CMS DIELECTRON SPEKTRUM (gleicher Detektor, anderer Kanal)
═══════════════════════════════════════════════════════════════════════════
""")
print("  Was: e+e- statt mu+mu- Massenspektrum")
print("  Warum: Identische Physik, unabhaengige Systematiken")
print("  → Wenn ACS dort die GLEICHEN Resonanzen mit gleichen Verhaeltnissen")
print("    findet = starke Bestaetigung (kein Artefakt)")
print()
print("  Daten: CMS Open Data, bereits auf opendata.cern.ch")
print("  Aufwand: NIEDRIG (gleiche Pipeline, nur Datensatz tauschen)")
print("  Impact: HOCH (systematische Kreuzpruefung)")

print("""
═══════════════════════════════════════════════════════════════════════════
OPTION 3: WASSERSTOFF-SPEKTRUM (Rydberg → Koch?)
═══════════════════════════════════════════════════════════════════════════
""")

# Hydrogen energy levels
print("  Rydberg-Formel: E_n = -13.6 eV / n^2")
E = [-13.6/n**2 for n in range(1, 8)]
dE = [E[i+1] - E[i] for i in range(len(E)-1)]
print(f"  Energieniveaus: {[f'{e:.3f}' for e in E]} eV")
print(f"  Aufspaltungen:  {[f'{d:.3f}' for d in dE]} eV")
ratios_H = [dE[i+1]/dE[i] for i in range(len(dE)-1)]
print(f"  Kontraktionsraten: {[f'{r:.3f}' for r in ratios_H]}")
print(f"  → NICHT geometrisch! (1/n^2 ist kein Koch-Pattern)")
print(f"  → ABER: Lamb Shift / Feinstruktur koennte Koch zeigen")
print()
print("  Aufwand: NIEDRIG (analytisch)")
print("  Impact: MITTEL (bestaetigt Koch ≠ triviale 1/n^2 Serie)")

print("""
═══════════════════════════════════════════════════════════════════════════
OPTION 4: KERNPHYSIK — Magische Zahlen
═══════════════════════════════════════════════════════════════════════════
""")
magic = [2, 8, 20, 28, 50, 82, 126]
print(f"  Magische Zahlen: {magic}")
ratios_magic = [magic[i+1]/magic[i] for i in range(len(magic)-1)]
print(f"  Verhaeltnisse: {[f'{r:.2f}' for r in ratios_magic]}")
print(f"  → {ratios_magic[0]:.1f}, {ratios_magic[1]:.1f}, {ratios_magic[2]:.1f}, {ratios_magic[3]:.1f}, {ratios_magic[4]:.1f}, {ratios_magic[5]:.1f}")
print(f"  Interessant: 8/2=4 (Tet!), 20/8=2.5, 50/28=1.79~sqrt(pi)?")
print(f"  Aufwand: NIEDRIG")
print(f"  Impact: MITTEL")

print("""
═══════════════════════════════════════════════════════════════════════════
OPTION 5: CMB POWER SPECTRUM (Planck-Daten)
═══════════════════════════════════════════════════════════════════════════
""")
# CMB acoustic peaks
ell_peaks = [220, 546, 800, 1120, 1444]
print(f"  CMB Akustische Peaks (Multipol l): {ell_peaks}")
ratios_cmb = [ell_peaks[i+1]/ell_peaks[i] for i in range(len(ell_peaks)-1)]
print(f"  Verhaeltnisse: {[f'{r:.3f}' for r in ratios_cmb]}")
print(f"  → Nicht streng geometrisch (Baryon-Photon-Ratio beeinflusst)")
print(f"  Aufwand: HOCH (Planck-Daten komplex)")
print(f"  Impact: EXTREM HOCH (verbindet QCD mit Kosmologie)")

print("""
═══════════════════════════════════════════════════════════════════════════
OPTION 6: LHCb DATEN (andere CERN-Experimente)
═══════════════════════════════════════════════════════════════════════════
""")
print("  Was: LHCb hat die BESTEN Bc-Messungen!")
print("  → Direkte Pruefung unserer Vorhersage r_Bc ≈ 0.5")
print("  → Bc(2S) wurde 2019 beobachtet: m = 6871.2 MeV")
print()
bc_1s = 6274.9
bc_2s = 6871.2
dm_bc = bc_2s - bc_1s
print(f"  Bc(1S) = {bc_1s} MeV")
print(f"  Bc(2S) = {bc_2s} MeV")
print(f"  Delta_m(1-2) = {dm_bc:.1f} MeV")
print(f"  → Brauchen Bc(3S) fuer r_Bc = dm(2-3)/dm(1-2)")
print(f"  → Bc(3S) noch nicht beobachtet (LHCb Run 3 koennte!)")
print()
print("  Aufwand: KEINER (warten auf LHCb Run 3)")
print("  Impact: EXTREM HOCH (direkte Falsifikation/Bestaetigung)")

print("""
═══════════════════════════════════════════════════════════════════════════
  EMPFEHLUNG: STRATEGIE
═══════════════════════════════════════════════════════════════════════════

  SOFORT (heute/morgen):
  ├─ [2] CMS Dielectron Cross-Check     → gleiches Script, neue Daten
  └─ [3] Wasserstoff analytisch         → schneller Gegentest
  
  NAECHSTE WOCHE:
  └─ [1] LIGO/Virgo QNM-Analyse         → Game-Changer
  
  WARTEN:
  └─ [6] LHCb Bc(3S)                    → ultimativer Test, LHC Run 3
  
  OPTIONAL:
  ├─ [4] Magische Zahlen                 → quick check
  └─ [5] CMB                            → separates Paper
""")

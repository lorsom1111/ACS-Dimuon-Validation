"""
RESONANZ-SCAN: Geometrische Strukturen in CMS Dimuon-Daten
===========================================================
Sucht nach Massenverhaeltnissen, die geometrischen Zahlen entsprechen:
Tetraeder (4,6,4), Wuerfel (8,12,6), Oktaeder (6,12,8), Stella (24)
"""

import numpy as np
import os, sys
from scipy.signal import find_peaks
from scipy.optimize import curve_fit

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as cfg

data = np.load(os.path.join(cfg.OUTPUT_DIR, 'full_spectrum_data.npz'))
masses = data['masses']
absZ = data['absZ']
Z = data['Z']

print('=' * 90)
print('  RESONANZ-SCAN: Geometrische Strukturen in CMS Dimuon-Daten')
print('=' * 90)

# ══════════════════════════════════════════════════════════════════
#  1. ALLE signifikanten Peaks finden
# ══════════════════════════════════════════════════════════════════

peaks_idx, props = find_peaks(absZ, height=5, distance=3, prominence=2)
peak_m = masses[peaks_idx]
peak_z = absZ[peaks_idx]

order = np.argsort(peak_z)[::-1]
peak_m = peak_m[order]
peak_z = peak_z[order]

# PDG resonances
pdg_all = {}
pdg_all['eta(548)'] = 0.5479
pdg_all['rho(770)'] = 0.7753
pdg_all['omega(782)'] = 0.7827
pdg_all['eta_prime(958)'] = 0.9578
pdg_all['f0(980)'] = 0.990
pdg_all['phi(1020)'] = 1.0195
pdg_all['f2(1270)'] = 1.2754
pdg_all['f0(1500)'] = 1.506
pdg_all['rho3(1690)'] = 1.689
pdg_all['phi(1680)'] = 1.680
pdg_all['f0(1710)'] = 1.720
pdg_all['J/psi'] = 3.0969
pdg_all['chi_c1(3511)'] = 3.5107
pdg_all['psi(2S)'] = 3.6861
pdg_all['psi(3770)'] = 3.7737
pdg_all['X(3872)'] = 3.8718
pdg_all['psi(4040)'] = 4.039
pdg_all['psi(4160)'] = 4.191
pdg_all['psi(4415)'] = 4.421
pdg_all['Y(1S)'] = 9.4603
pdg_all['Y(2S)'] = 10.0233
pdg_all['Y(3S)'] = 10.3552
pdg_all['Y(4S)'] = 10.5794
pdg_all['Y(10860)'] = 10.8852
pdg_all['Z'] = 91.1876

print(f'\n  Gefundene Peaks (|Z| > 5): {len(peak_m)}')
print(f'\n  Top 30 nach Signifikanz:')
print(f'  {"#":>3s}  {"M [GeV]":>10s}  {"Z [sigma]":>10s}  PDG-Kandidat')
print('  ' + '-' * 60)

for i in range(min(30, len(peak_m))):
    m = peak_m[i]
    z = peak_z[i]
    best_name = '???'
    best_dist = 999
    for name, m_pdg in pdg_all.items():
        dist = abs(m - m_pdg) / m_pdg
        if dist < best_dist:
            best_dist = dist
            best_name = name
    if best_dist < 0.05:
        match = best_name
    else:
        match = f'??? (nahe {best_name}, {best_dist*100:.1f}%)'
    print(f'  {i+1:3d}  {m:10.4f}  {z:10.1f}  {match}')

# ══════════════════════════════════════════════════════════════════
#  2. MASSENVERHAELTNISSE: Geometrische Zahlen
# ══════════════════════════════════════════════════════════════════

print()
print('=' * 90)
print('  MASSENVERHAELTNISSE: Suche nach geometrischen Zahlen')
print('=' * 90)

geo_numbers = {
    'sqrt(2)': np.sqrt(2),
    '4/3 (color)': 4/3,
    'sqrt(3)': np.sqrt(3),
    'phi (golden)': (1 + np.sqrt(5)) / 2,
    'e/pi': np.e / np.pi,
    'pi/4': np.pi / 4,
    '3/4': 0.75,
    'e': np.e,
    'pi': np.pi,
    'Tet V=4': 4.0,
    'Tet E=6': 6.0,
    'Cube V=8': 8.0,
    'Oct V=6': 6.0,
    'Cube E=12': 12.0,
    'Stella F=24': 24.0,
    '|A4|=12': 12.0,
    '|2T|=24': 24.0,
}

# Use well-identified peaks only
known_peaks = {
    'eta': 0.5479,
    'rho/omega': 0.7790,  # combined
    'phi': 1.0195,
    'J/psi': 3.0969,
    'psi(2S)': 3.6861,
    'psi(3770)': 3.7737,
    'Y(1S)': 9.4603,
    'Y(2S)': 10.0233,
    'Y(3S)': 10.3552,
    'Z': 91.1876,
}

top_names = list(known_peaks.keys())
top_masses = np.array(list(known_peaks.values()))

matches = []
for i in range(len(top_masses)):
    for j in range(i + 1, len(top_masses)):
        m1 = min(top_masses[i], top_masses[j])
        m2 = max(top_masses[i], top_masses[j])
        ratio = m2 / m1
        n1 = top_names[i] if top_masses[i] < top_masses[j] else top_names[j]
        n2 = top_names[j] if top_masses[i] < top_masses[j] else top_names[i]
        
        for gname, gval in geo_numbers.items():
            if gval > 0.5:
                err = abs(ratio - gval) / gval * 100
                if err < 3.0:
                    matches.append((n1, n2, m1, m2, ratio, gval, gname, err))

matches.sort(key=lambda x: x[7])
print(f'\n  Treffer (< 3% Abweichung):')
print(f'  {"Peak 1":>12s}  {"Peak 2":>12s}  {"m1":>8s}  {"m2":>8s}  {"m2/m1":>8s}  {"Geo":>8s}  {"Name":>15s}  {"Err%":>5s}')
print('  ' + '-' * 90)
for n1, n2, m1, m2, ratio, gval, gname, err in matches:
    print(f'  {n1:>12s}  {n2:>12s}  {m1:8.4f}  {m2:8.4f}  {ratio:8.4f}  {gval:8.4f}  {gname:>15s}  {err:5.2f}%')

# ══════════════════════════════════════════════════════════════════
#  3. ERWEITERT: Dreier-Verhaeltnisse (a:b:c = Polyeder V:E:F?)
# ══════════════════════════════════════════════════════════════════

print()
print('=' * 90)
print('  DREIER-VERHAELTNISSE: Polyeder-Signaturen V:E:F')
print('=' * 90)

# Tetrahedron: 4:6:4 = 2:3:2
# Cube: 8:12:6 = 4:6:3
# Octahedron: 6:12:8 = 3:6:4
# Icosahedron: 12:30:20 = 6:15:10

polyhedra = {
    'Tetraeder (2:3:2)': (2, 3, 2),
    'Wuerfel (4:6:3)': (4, 6, 3),
    'Oktaeder (3:6:4)': (3, 6, 4),
    'Ikosaeder (6:15:10)': (6, 15, 10),
    'Dodekaeder (10:15:6)': (10, 15, 6),
}

print(f'\n  Suche Tripel (m_a, m_b, m_c) mit m_a:m_b:m_c ~ V:E:F')
print()

for pname, (v, e, f) in polyhedra.items():
    # Normalize
    vn, en, fn = v/v, e/v, f/v  # ratios relative to smallest
    
    for i in range(len(top_masses)):
        for j in range(i+1, len(top_masses)):
            for k in range(j+1, len(top_masses)):
                ms = sorted([top_masses[i], top_masses[j], top_masses[k]])
                rs = [ms[0]/ms[0], ms[1]/ms[0], ms[2]/ms[0]]
                
                # Try all permutations of v,e,f
                import itertools
                for perm in itertools.permutations([v/min(v,e,f), e/min(v,e,f), f/min(v,e,f)]):
                    err = sum(abs(rs[q] - perm[q])/max(perm[q], 0.01) for q in range(3)) / 3 * 100
                    if err < 5:
                        ns = sorted([(top_masses[i], top_names[i]), 
                                    (top_masses[j], top_names[j]),
                                    (top_masses[k], top_names[k])])
                        print(f'  {pname}:')
                        print(f'    {ns[0][1]:>12s} ({ns[0][0]:.3f}) : {ns[1][1]:>12s} ({ns[1][0]:.3f}) : {ns[2][1]:>12s} ({ns[2][0]:.3f})')
                        print(f'    Ratios: {rs[0]:.3f} : {rs[1]:.3f} : {rs[2]:.3f}')
                        print(f'    Target: {perm[0]:.3f} : {perm[1]:.3f} : {perm[2]:.3f}')
                        print(f'    Error: {err:.1f}%')
                        print()

# ══════════════════════════════════════════════════════════════════
#  4. VERSCHRAENKUNG: IN/OUT Paare bei gleicher Masse
# ══════════════════════════════════════════════════════════════════

print()
print('=' * 90)
print('  VERSCHRAENKUNG: Z_positive vs Z_negative (IN/OUT) bei Resonanzen')
print('=' * 90)

for name, m_pdg in sorted(known_peaks.items(), key=lambda x: x[1]):
    # Window around peak
    window = m_pdg * 0.05  # 5% window
    mask = (masses >= m_pdg - window) & (masses <= m_pdg + window)
    z_window = Z[mask]
    
    n_pos = np.sum(z_window > 3)
    n_neg = np.sum(z_window < -3)
    z_max = np.max(z_window) if len(z_window) > 0 else 0
    z_min = np.min(z_window) if len(z_window) > 0 else 0
    
    ratio_str = f'{n_pos}/{n_neg}' if n_neg > 0 else f'{n_pos}/0'
    print(f'  {name:>12s} ({m_pdg:.3f} GeV): Z_max={z_max:+8.1f}  Z_min={z_min:+8.1f}  OUT/IN(>3s)={ratio_str:>6s}')

# ══════════════════════════════════════════════════════════════════
#  5. STELLA OCTANGULA: 24-fold pattern
# ══════════════════════════════════════════════════════════════════

print()
print('=' * 90)
print('  STELLA OCTANGULA: 24-fache Struktur im Spektrum?')
print('=' * 90)

# Divide spectrum into 24 equal log-bins
log_m = np.log10(masses)
log_range = log_m[-1] - log_m[0]
bin_size = log_range / 24

print(f'\n  Spektrum in 24 log-Bins (Stella-Faechen):')
print(f'  Log-Range: {log_m[0]:.3f} bis {log_m[-1]:.3f}, Bin-Breite: {bin_size:.4f}')
print()

n_peaks_per_bin = []
for b in range(24):
    lo = log_m[0] + b * bin_size
    hi = lo + bin_size
    mask = (log_m >= lo) & (log_m < hi)
    z_bin = absZ[mask]
    n_above_5 = np.sum(z_bin > 5)
    max_z = np.max(z_bin) if len(z_bin) > 0 else 0
    m_lo = 10**lo
    m_hi = 10**hi
    marker = '*' * min(n_above_5, 20)
    n_peaks_per_bin.append(n_above_5)
    print(f'  Bin {b+1:2d} [{m_lo:7.3f}-{m_hi:7.3f} GeV]: {n_above_5:3d} peaks  max|Z|={max_z:7.1f}  {marker}')

print(f'\n  Total peaks: {sum(n_peaks_per_bin)}')
print(f'  Bins with peaks: {sum(1 for n in n_peaks_per_bin if n > 0)}/24')
print(f'  Shannon-Entropie: ', end='')
p = np.array(n_peaks_per_bin, dtype=float)
p = p[p > 0]
p = p / p.sum()
S = -np.sum(p * np.log2(p))
S_max = np.log2(24)
print(f'{S:.3f} / {S_max:.3f} = {S/S_max:.3f} (1.0 = gleichverteilt)')

# ══════════════════════════════════════════════════════════════════
#  6. FUNDAMENTALE VERHAELTNISSE
# ══════════════════════════════════════════════════════════════════

print()
print('=' * 90)
print('  FUNDAMENTALE VERHAELTNISSE: Resonanz-Massen / Grundzustaende')
print('=' * 90)

m_jpsi = 3.0969
m_y1s = 9.4603
m_z = 91.1876
m_phi = 1.0195
m_omega = 0.7827

# Key ratios
ratios_fund = [
    ('Z / Y(1S)', m_z / m_y1s),
    ('Z / J/psi', m_z / m_jpsi),
    ('Y(1S) / J/psi', m_y1s / m_jpsi),
    ('J/psi / phi', m_jpsi / m_phi),
    ('J/psi / omega', m_jpsi / m_omega),
    ('phi / omega', m_phi / m_omega),
    ('Y(1S) / phi', m_y1s / m_phi),
    ('Z / phi', m_z / m_phi),
]

print()
for name, ratio in ratios_fund:
    # Find closest geometric match
    best_match = None
    best_err = 999
    
    # Extended comparisons
    test_vals = {
        'pi^2': np.pi**2,
        '3*pi': 3*np.pi,
        '4*pi': 4*np.pi,
        'e^2': np.e**2,
        'e*pi': np.e * np.pi,
        '8*pi': 8*np.pi,
        '24/pi': 24/np.pi,
        '12/pi': 12/np.pi,
        'pi^2/e': np.pi**2/np.e,
        '24': 24.0,
        '12': 12.0,
        '8': 8.0,
        '6': 6.0,
        '4': 4.0,
        '3': 3.0,
        'e': np.e,
        'pi': np.pi,
        'pi/e': np.pi/np.e,
        '4/pi': 4/np.pi,
        'sqrt(6)': np.sqrt(6),
        'sqrt(8)': np.sqrt(8),
        'sqrt(12)': np.sqrt(12),
        'sqrt(24)': np.sqrt(24),
        '4*e': 4*np.e,
        '3*e': 3*np.e,
        '29.44=Z/J/psi': m_z/m_jpsi,
        'D_Koch': np.log(4)/np.log(3),
        'D_Koch^2': (np.log(4)/np.log(3))**2,
        '12*D_Koch': 12*np.log(4)/np.log(3),
    }
    
    for tname, tval in test_vals.items():
        err = abs(ratio - tval) / tval * 100
        if err < best_err:
            best_err = err
            best_match = tname
    
    print(f'  {name:>18s} = {ratio:8.4f}  ~  {best_match} = {test_vals[best_match]:.4f}  ({best_err:.1f}%)')

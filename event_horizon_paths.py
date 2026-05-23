"""Event Horizon as Path Choice: Short vs Long Way between iterations"""
import numpy as np

print('='*80)
print('  EREIGNISHORIZONT = PFADWAHL zwischen JETZT und NAECHSTEM JETZT')
print('='*80)

print()
print('  Bei jeder Iteration k gibt es ZWEI Wege zum naechsten k+1:')
print('  - KURZER WEG (direkt, schnell): Dm_short = Dm_k * r')
print('  - LANGER WEG (Summe aller verbl.): Dm_long = Dm_k * r/(1-r)')
print()

r_cc = 0.149
r_bb_12 = 0.590
r_bb_23 = 0.676
r_bb_geo = 0.631

print('  Verhaeltnis langer/kurzer Weg = 1/(1-r):')
print('  ' + '-'*55)

for name, r, m0, dm0 in [
    ('Charmonium', r_cc, 3097, 589),
    ('Bottomonium(1-2)', r_bb_12, 9460, 563),
    ('Bottomonium(2-3)', r_bb_23, 10023, 332),
    ('Bottomonium(geo)', r_bb_geo, 9460, 563),
]:
    long_short = 1/(1-r)
    short = dm0 * r
    long_path = dm0 * r / (1-r)
    
    print(f'  {name:20s}: r={r:.3f}')
    print(f'    Kurzer Weg:  {short:.1f} MeV')
    print(f'    Langer Weg:  {long_path:.1f} MeV')
    print(f'    Lang/Kurz:   {long_short:.4f}')
    
    for cname, cval in [('1', 1.0), ('phi_gold', (1+np.sqrt(5))/2), ('2', 2.0), ('e', np.e), ('3', 3.0), ('pi', np.pi)]:
        if abs(long_short - cval)/cval < 0.05:
            print(f'    >>> = {cname} = {cval:.4f} ({abs(long_short-cval)/cval*100:.2f}% Abw.!)')
    print()

print('='*80)
print('  DER HORIZONT: Wo liegt r = 1/2 (beide Wege gleich lang)?')
print('='*80)

m_c = 1.27  # charm quark mass
m_b = 4.18  # bottom quark mass

b_coeff = (r_bb_geo - r_cc) / (np.log(m_b) - np.log(m_c))
a_coeff = r_cc - b_coeff * np.log(m_c)
m_horizon = np.exp((0.5 - a_coeff) / b_coeff)

print(f'\n  r = 0.5 bei m_quark = {m_horizon:.2f} GeV')
print(f'  Meson-Masse ~ {2*m_horizon:.1f} GeV')
print(f'  B_c Meson (b+cbar): m = 6.274 GeV, Abw.: {abs(2*m_horizon - 6.274)/6.274*100:.1f}%')
print(f'\n  >>> Der HORIZONT liegt beim B_c Meson!')
print(f'  >>> = Grenze zwischen Charm- und Bottom-Welt')
print(f'  >>> = Das einzige Meson aus ZWEI schweren Quarks verschiedener Art')

print()
print('='*80)
print('  PFAD-TABELLE: Von JETZT zu NAECHSTEM JETZT')
print('='*80)

m = 9460.3
dm = 563.0
r = r_bb_geo

print(f'\n  Bottomonium (r = {r:.3f}):')
headers = ['k', 'Jetzt [MeV]', 'Kurz [MeV]', 'Lang [MeV]', 'L/K', 'Naechstes [MeV]']
print(f'  {headers[0]:>5s}  {headers[1]:>12s}  {headers[2]:>12s}  {headers[3]:>12s}  {headers[4]:>8s}  {headers[5]:>15s}')
print('  ' + '-'*75)

for k in range(6):
    short = dm * r
    remaining = dm * r / (1-r)
    next_m = m + dm
    ratio_lk = remaining / short if short > 0 else float('inf')
    
    print(f'  {k:5d}  {m:12.1f}  {short:12.1f}  {remaining:12.1f}  {ratio_lk:8.3f}  {next_m:15.1f}')
    m = next_m
    dm = dm * r

print(f'\n  Lang/Kurz = KONSTANT = 1/(1-r) = {1/(1-r):.4f}')
print(f'  Vergleich mit e = {np.e:.4f}: Abweichung {abs(1/(1-r)-np.e)/np.e*100:.1f}%')

print()
print('='*80)
print('  ENTSCHEIDENDE EINSICHT')
print('='*80)
print()
print('  1. Das VERHAELTNIS Lang/Kurz ist iterations-UNABHAENGIG')
print('     -> Die lokale Geometrie (Kruemmung) ist ueberall gleich')
print('     -> Wie ein gleichmaessig beschleunigter Beobachter (Rindler)')
print()
print('  2. Die ABSOLUTEN Wege schrumpfen mit jeder Iteration')
print('     -> Das Koordinatengitter wird dichter')  
print('     -> Wie ein fallender Beobachter: immer naechstes "Jetzt",')
print('        aber die Schritte werden kleiner')
print()
print('  3. Am HORIZONT (Schwelle DD/BB):')
print('     -> Beide Wege -> 0')
print('     -> Kein "naechstes Jetzt" mehr moeglich')
print('     -> String bricht = Horizont ueberschritten')
print()
print('  4. HINTER dem Horizont:')
print('     -> Offene Flavour-Zustaende (nicht gebunden)')
print('     -> Neues "Jetzt" in anderem Raum (Meson-Paar statt Quarkonium)')
print('     -> = Anderes Universum hinter ER-Bruecke')
print()

# The key formula
print('='*80)
print('  DIE METRIK DER KOCH-ZEIT')
print('='*80)
print()
print('  Gegeben: r = Kontraktionsrate (0 < r < 1)')
print()
print('  Kurzer Weg:  ds_kurz = Dm * r^k')
print('  Langer Weg:  ds_lang = Dm * r^k / (1-r)')
print()
print('  Eigenzeit:   dtau = ds_kurz = Dm * r^k')
print('  Koordinatenzeit: dt = ds_lang = Dm * r^k / (1-r)')
print()
print('  Zeitdilatation: dt/dtau = 1/(1-r)')
print()

# This IS the metric!
print('  Das ergibt die Koch-Metrik:')
print()
print('    ds^2 = -(1-r)^2 * dt^2 + dk^2')
print()
print('  Vergleich:')
print('    Schwarzschild: ds^2 = -(1-rs/R) dt^2 + (1-rs/R)^-1 dR^2')
print('    Rindler:       ds^2 = -(ax)^2 dt^2 + dx^2')
print('    Koch:          ds^2 = -(1-r)^2 dt^2 + dk^2')
print()
print('  Koch-Metrik hat die Form einer RINDLER-Metrik!')
print('  -> Gleichmaessige Beschleunigung, nicht Schwarzschild')
print('  -> ABER: r = r(k) aendert sich -> nicht-uniform')
print()

# For bottomonium: r changes
print('  Da r sich aendert (r_12=0.590, r_23=0.676):')
print(f'    dt/dtau bei k=1: {1/(1-r_bb_12):.3f}')
print(f'    dt/dtau bei k=2: {1/(1-r_bb_23):.3f}')
print(f'    Aenderung: {(1/(1-r_bb_23))/(1/(1-r_bb_12)):.3f}')
print(f'    -> Zeitdilatation NIMMT ZU mit der Iteration')
print(f'    -> = Beschleunigung wird staerker = Annaeherung an Horizont')
print()
print('  Fuer Charmonium (r=0.149):')
print(f'    dt/dtau = {1/(1-r_cc):.3f}')
print(f'    -> Fast keine Zeitdilatation (nahe flach)')
print(f'    -> Aber: nur 1 Iteration bis Horizont!')
print(f'    -> = Schon fast AM Horizont, nur ein Schritt entfernt')

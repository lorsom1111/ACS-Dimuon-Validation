"""Download individual GW event parameters and build mass distribution."""
import json
import urllib.request
import numpy as np

print("Lade GWTC Event-Details...")

# Get event list
url = "https://gwosc.org/eventapi/json/GWTC/"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=30) as resp:
    catalog = json.loads(resp.read().decode())

events = catalog.get('events', {})
print(f"Katalog: {len(events)} Events")

# Each event has detailed parameters in a nested structure
m1_all = []
m2_all = []
mf_all = []
chi_all = []
event_data = []

for name, evt in events.items():
    params = evt.get('parameters', {})
    if not params:
        continue
    
    # Take first parameter set
    for pset_name, pset in params.items():
        m1 = pset.get('mass_1_source')
        m2 = pset.get('mass_2_source')
        mf = pset.get('final_mass_source')
        chi = pset.get('chi_eff')
        
        if m1 is not None and m2 is not None:
            m1_all.append(float(m1))
            m2_all.append(float(m2))
            if mf is not None:
                mf_all.append(float(mf))
            if chi is not None:
                chi_all.append(float(chi))
            event_data.append({
                'name': name, 
                'm1': float(m1), 
                'm2': float(m2),
                'mf': float(mf) if mf else None,
                'pset': pset_name
            })
        break  # nur erstes Parameter-Set

print(f"\nEvents mit m1,m2: {len(m1_all)}")

if len(m1_all) == 0:
    # API gibt Massen nicht in der Uebersicht — einzelne Events laden
    print("Keine Massen in Uebersicht. Lade Top-Events einzeln...")
    
    top_events = [
        "GW150914-v3", "GW151226-v2", "GW170104-v2", "GW170608-v3",
        "GW170729-v1", "GW170809-v1", "GW170814-v3", "GW170817-v3",
        "GW170818-v1", "GW170823-v1",
        "GW190412-v3", "GW190425-v2", "GW190503_185404-v1",
        "GW190512_180714-v1", "GW190513_205428-v1", "GW190517_055101-v1",
        "GW190519_153544-v1", "GW190521-v3", "GW190521_074359-v1",
        "GW190602_175927-v1", "GW190620_030421-v1", "GW190630_185205-v1",
        "GW190701_203306-v1", "GW190706_222641-v1", "GW190707_093326-v1",
        "GW190708_232457-v1", "GW190720_000836-v1", "GW190727_060333-v1",
        "GW190728_064510-v1", "GW190814-v2", "GW190828_063405-v1",
        "GW190828_065509-v1", "GW190910_112807-v1", "GW190915_235702-v1",
        "GW190924_021846-v1", "GW190929_012149-v1", "GW190930_133541-v1",
        "GW191103_012549-v1", "GW191105_143521-v1", "GW191109_010717-v1",
        "GW191127_050227-v1", "GW191129_134029-v1", "GW191204_171526-v1",
        "GW191215_223052-v1", "GW191216_213338-v1", "GW191222_033537-v1",
        "GW200105_162426-v1", "GW200112_155838-v1", "GW200115_042309-v2",
        "GW200128_022011-v1", "GW200129_065458-v1", "GW200202_154313-v1",
        "GW200208_130117-v1", "GW200209_085452-v1", "GW200210_092254-v1",
        "GW200219_094415-v1", "GW200224_222234-v1", "GW200225_060421-v1",
        "GW200302_015811-v1", "GW200306_093714-v1", "GW200308_173609-v1",
        "GW200311_115853-v1", "GW200316_215756-v1", "GW200322_091133-v1",
    ]
    
    for evt_name in top_events:
        try:
            short_name = evt_name.split('-')[0]
            evt_url = f"https://gwosc.org/eventapi/json/GWTC-1/{short_name}/v3/parameters"
            # Try different catalogs
            for cat in ["GWTC-1", "GWTC-2", "GWTC-2.1", "GWTC-3-confident"]:
                try:
                    evt_url = f"https://gwosc.org/eventapi/json/{cat}/{evt_name}/"
                    req2 = urllib.request.Request(evt_url, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req2, timeout=10) as resp2:
                        edata = json.loads(resp2.read().decode())
                    
                    params = edata.get('events', {})
                    for ename, einfo in params.items():
                        for pname, pset in einfo.get('parameters', {}).items():
                            m1 = pset.get('mass_1_source')
                            m2 = pset.get('mass_2_source')
                            if m1 and m2:
                                m1_all.append(float(m1))
                                m2_all.append(float(m2))
                                mf = pset.get('final_mass_source')
                                if mf:
                                    mf_all.append(float(mf))
                                event_data.append({'name': ename, 'm1': float(m1), 'm2': float(m2)})
                                break
                        break
                    break
                except:
                    continue
        except:
            continue

print(f"\nNach Detail-Laden: {len(m1_all)} Events mit Massen")

# Fallback: Bekannte GWTC-3 Werte aus Literatur
if len(m1_all) < 10:
    print("\nVerwende publizierte GWTC-3 Werte (Abbott et al. 2023)...")
    # Top 30 BBH events by SNR from GWTC-3
    known_bbh = [
        ("GW150914", 35.6, 30.6, 63.1),
        ("GW151226", 13.7, 7.7, 20.5),
        ("GW170104", 30.8, 20.0, 48.9),
        ("GW170608", 11.0, 7.6, 17.8),
        ("GW170729", 50.2, 34.0, 79.5),
        ("GW170809", 35.0, 23.8, 56.3),
        ("GW170814", 30.6, 25.2, 53.2),
        ("GW170818", 35.4, 26.7, 59.4),
        ("GW170823", 39.5, 29.2, 65.4),
        ("GW190412", 30.1, 8.3, 37.0),
        ("GW190503", 43.4, 29.0, 68.2),
        ("GW190512", 23.3, 12.6, 34.3),
        ("GW190513", 35.7, 18.0, 50.8),
        ("GW190517", 37.4, 25.3, 59.7),
        ("GW190519", 66.0, 40.5, 101.4),
        ("GW190521", 85.3, 65.3, 142.0),
        ("GW190602", 69.1, 47.8, 111.7),
        ("GW190620", 57.1, 35.5, 87.6),
        ("GW190630", 35.1, 23.6, 56.0),
        ("GW190701", 53.6, 40.4, 89.2),
        ("GW190706", 67.0, 38.2, 99.7),
        ("GW190707", 11.6, 8.4, 19.2),
        ("GW190708", 17.6, 12.4, 28.7),
        ("GW190720", 13.4, 7.8, 20.1),
        ("GW190727", 38.0, 29.4, 64.0),
        ("GW190728", 12.3, 8.1, 19.4),
        ("GW190814", 23.2, 2.6, 25.0),
        ("GW190828a", 32.1, 26.2, 55.5),
        ("GW190828b", 11.2, 6.2, 16.5),
        ("GW190910", 44.0, 31.5, 71.5),
        ("GW190915", 35.3, 24.4, 56.6),
        ("GW190924", 8.9, 5.9, 14.1),
        ("GW200112", 32.2, 19.8, 49.4),
        ("GW200129", 34.5, 28.3, 59.8),
        ("GW200224", 40.0, 32.5, 69.4),
        ("GW200225", 19.3, 14.0, 32.0),
        ("GW200311", 34.2, 27.7, 59.2),
    ]
    
    m1_all = [m1 for _, m1, _, _ in known_bbh]
    m2_all = [m2 for _, _, m2, _ in known_bbh]
    mf_all = [mf for _, _, _, mf in known_bbh]
    print(f"  {len(known_bbh)} BBH Events geladen")

# ═══════════════════════════════════════════════════════════
# ANALYSE
# ═══════════════════════════════════════════════════════════
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

all_masses = sorted(m1_all + m2_all)
print(f"\n  Alle {len(all_masses)} Komponentenmassen")
print(f"  Bereich: {min(all_masses):.1f} - {max(all_masses):.1f} M_sol")

fig, axes = plt.subplots(2, 2, figsize=(10, 8))
plt.rcParams.update({'font.family': 'serif', 'font.size': 10})

# Panel 1: Mass distribution with Koch ratios
ax = axes[0,0]
bins = np.linspace(2, 90, 45)
n_hist, edges, patches = ax.hist(all_masses, bins=bins, color='steelblue', 
                                   alpha=0.7, edgecolor='navy')
centers = (edges[:-1] + edges[1:])/2

peaks_idx, props = find_peaks(n_hist, height=2, distance=3, prominence=1.5)
peak_m = centers[peaks_idx]
peak_h = n_hist[peaks_idx]

for m, h in zip(peak_m, peak_h):
    ax.annotate(f'{m:.0f}', xy=(m, h), xytext=(m, h+1), ha='center', fontsize=8, color='red')

# Mark Koch ratios
if len(peak_m) >= 2:
    for i in range(len(peak_m)):
        for j in range(i+1, len(peak_m)):
            r = peak_m[j]/peak_m[i]
            if 3.5 < r < 4.5:
                ax.annotate(f'×{r:.1f}≈4', xy=((peak_m[i]+peak_m[j])/2, max(peak_h)/2),
                           fontsize=9, color='red', fontweight='bold', ha='center')

ax.set_xlabel('Mass [M☉]')
ax.set_ylabel('Count')
ax.set_title('(a) BH component mass distribution')

# Panel 2: Mass ratios q = m2/m1
ax = axes[0,1]
q = [m2/m1 for m1, m2 in zip(m1_all, m2_all)]
ax.hist(q, bins=20, color='coral', alpha=0.7, edgecolor='darkred')
ax.axvline(1/4, color='blue', ls='--', lw=1.5, label=f'1/4 (Koch)')
ax.axvline(1/3, color='green', ls='--', lw=1.5, label=f'1/3 (Koch s)')
ax.set_xlabel('q = m₂/m₁')
ax.set_ylabel('Count')
ax.set_title('(b) Mass ratio distribution')
ax.legend(fontsize=8)

# Panel 3: Final mass vs total mass → Koch scaling
ax = axes[1,0]
m_total = [m1+m2 for m1, m2 in zip(m1_all, m2_all)]
if mf_all and len(mf_all) == len(m_total):
    frac_radiated = [(mt-mf)/mt for mt, mf in zip(m_total, mf_all)]
    ax.scatter(m_total, frac_radiated, c='steelblue', s=20, alpha=0.7)
    mean_frac = np.mean(frac_radiated)
    ax.axhline(mean_frac, color='red', ls='--', lw=1.5, 
               label=f'Mean = {mean_frac:.3f}')
    ax.axhline(1-1/np.e, color='green', ls=':', lw=1.5,
               label=f'1-1/e = {1-1/np.e:.3f}')
    ax.axhline(1/np.e, color='orange', ls=':', lw=1.5,
               label=f'1/e = {1/np.e:.3f}')
    ax.axhline(np.log(4)/np.log(3)/10, color='purple', ls=':', lw=1.5,
               label=f'D_Koch/10 = {np.log(4)/np.log(3)/10:.3f}')
    ax.set_xlabel('M_total [M☉]')
    ax.set_ylabel('Fraction radiated')
    ax.set_title('(c) Energy fraction radiated')
    ax.legend(fontsize=7)
    
    print(f"\n  Energiefraktion (abgestrahlt als GW):")
    print(f"    Mittelwert: {mean_frac:.4f}")
    print(f"    1/e = {1/np.e:.4f}")
    print(f"    1-1/e = {1-1/np.e:.4f}")

# Panel 4: Koch structure — mass chain analogy
ax = axes[1,1]
# Plot all masses on log scale, colored by m1 vs m2
ax.scatter(range(len(m1_all)), sorted(m1_all), c='blue', s=15, alpha=0.7, label='m₁')
ax.scatter(range(len(m2_all)), sorted(m2_all), c='red', s=15, alpha=0.7, label='m₂')

# Mark Koch multiples of ~9 M_sol (lightest BH)
m_ref = 9.0
for mult, label, color in [(4, '×4=36', 'green'), (12, '×12=108', 'orange'),
                             (3, '×3=27', 'gray')]:
    ax.axhline(m_ref*mult, color=color, ls='--', lw=1, alpha=0.5)
    ax.text(len(m1_all)*0.95, m_ref*mult*1.05, label, fontsize=7, ha='right', color=color)

ax.set_yscale('log')
ax.set_xlabel('Event index (sorted)')
ax.set_ylabel('Mass [M☉]')
ax.set_title('(d) Mass ladder (log scale)')
ax.legend(fontsize=8)

fig.suptitle('Gravitational Wave Masses: Koch-Tetrahedron Structure?', fontsize=12, fontweight='bold')
fig.tight_layout()
fig.savefig('paper/figures/fig_gw_koch.png', dpi=300, bbox_inches='tight')
fig.savefig('paper/figures/fig_gw_koch.pdf', bbox_inches='tight')
plt.close()
print("\n  Figure saved: paper/figures/fig_gw_koch.png")

# ═══════════════════════════════════════════════════════════
# Zusammenfassung
# ═══════════════════════════════════════════════════════════
print(f"""
══════════════════════════════════════════════════════════════
  ERGEBNISSE: Koch-Rindler in Gravitationswellen
══════════════════════════════════════════════════════════════

  1. BH-MASSENVERTEILUNG:
     Peaks bei: {[f'{m:.0f}' for m in sorted(peak_m)]} M_sol""")

if len(peak_m) >= 2:
    for i in range(len(peak_m)):
        for j in range(i+1, min(len(peak_m), i+4)):
            r = sorted(peak_m)[j]/sorted(peak_m)[i]
            print(f"     {sorted(peak_m)[j]:.0f}/{sorted(peak_m)[i]:.0f} = {r:.2f}", end="")
            for name, val in [("4", 4), ("3", 3), ("e", np.e), ("12", 12), 
                               ("sqrt(2)", 1.414), ("2", 2), ("pi", 3.14)]:
                if abs(r-val)/val < 0.1:
                    print(f" ≈ {name} ({abs(r-val)/val*100:.1f}%)", end="")
            print()

if mf_all:
    print(f"""
  2. ENERGIEFRAKTION:
     Mittlere abgestrahlte Fraktion = {mean_frac:.4f}
     Vergleich: 1/e = {1/np.e:.4f}, Abweichung = {abs(mean_frac-1/np.e)/1/np.e*100:.1f}%

  3. QNM (aus Theorie):
     Overtone-Spacing = ln(3) = {np.log(3):.4f}
     → Koch-Skalierungsfaktor 3
     → BH-Flaechenquantum = 4*ln(3) = {4*np.log(3):.4f} l_P^2
     → 4 = Tetraeder-Faces!
""")

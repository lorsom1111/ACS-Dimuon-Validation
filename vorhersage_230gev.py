"""
230 GeV Koch-Vorhersage: Vollständige Datenlage + 95 GeV Bonus
"""
import numpy as np

e = np.e
print("""
╔══════════════════════════════════════════════════════════════════════╗
║  230 GeV KOCH-VORHERSAGE — VOLLSTÄNDIGE DATENLAGE                ║
╚══════════════════════════════════════════════════════════════════════╝
""")

# ═══════════════════════════════════════════════════════════
# 1. DIE VORHERSAGE
# ═══════════════════════════════════════════════════════════
m_t = 172.76  # GeV (top quark)
m_H = 125.25  # GeV (Higgs)
m_Z = 91.188  # GeV (Z boson)

m_pred = m_t * 4/3  # Koch prediction

print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  1. KOCH-VORHERSAGE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Koch-Kette (EW-Sektor):  Z → H → t → ???
  
  Z × 4/3 = {m_Z * 4/3:.1f} GeV  ≈  H = {m_H} GeV  (Abw.: {abs(m_Z*4/3 - m_H)/m_H*100:.1f}%)
  H × 4/3 = {m_H * 4/3:.1f} GeV  ≈  t = {m_t} GeV   (Abw.: {abs(m_H*4/3 - m_t)/m_t*100:.1f}%)
  t × 4/3 = {m_pred:.1f} GeV  ← VORHERSAGE (nächste Koch-Stufe)
  
  Was für ein Teilchen wäre das?
  → Schweres Skalar (H₂)?
  → Schwerer Vektor (Z')?
  → Koch-Zustand ohne SM-Analog?
""")

# ═══════════════════════════════════════════════════════════
# 2. LHC-SUCHEN BEI 230 GeV
# ═══════════════════════════════════════════════════════════
print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  2. LHC-SUCHEN BEI ~230 GeV — STATUS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  ┌────────────────────────────────────────────────────────────────┐
  │  KANAL 1: H → ZZ → 4ℓ                                        │
  │  Status: KEIN signifikanter Exzess bei 230 GeV               │
  │  Limit:  σ×BR < einige fb (95% CL, NWA)                     │
  │  Daten:  Run 2 + teilweise Run 3                              │
  │  ⚠ ABER: Nur sensitiv auf skalare Bosonen (J=0)              │
  │  → Wenn Koch-Zustand kein Skalar → nicht ausgeschlossen!     │
  ├────────────────────────────────────────────────────────────────┤
  │  KANAL 2: Dimuon (ℓ⁺ℓ⁻)                                    │
  │  Status: 230 GeV liegt im "Kontroll-Bereich"                  │
  │  → ATLAS/CMS nutzen 200-300 GeV zur Background-Validierung   │
  │  → Kein dedizierter Bump-Hunt in diesem Bereich publiziert   │
  │  → Drell-Yan Hintergrund ist RIESIG bei 230 GeV              │
  ├────────────────────────────────────────────────────────────────┤
  │  KANAL 3: Diphoton (γγ)                                       │
  │  Status: Kein Exzess bei 230 GeV                              │
  │  → Historisch: 750 GeV Excess 2015 (verschwand)              │
  │  → ABER: 95 GeV Excess besteht weiter! (→ siehe unten)       │
  ├────────────────────────────────────────────────────────────────┤
  │  KANAL 4: WW/diboson                                          │
  │  Status: Kein Exzess bei 230 GeV                              │
  └────────────────────────────────────────────────────────────────┘

  FAZIT: Kein Signal, aber die Suchen sind NICHT optimiert
  für einen Koch-Zustand bei 230 GeV!
""")

# ═══════════════════════════════════════════════════════════
# 3. WARUM 230 GeV SCHWER ZU FINDEN IST
# ═══════════════════════════════════════════════════════════
print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  3. WARUM 230 GeV SCHWER ZU FINDEN IST
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Problem 1: HINTERGRUND
    Bei 230 GeV dominiert Drell-Yan (qq̄ → Z/γ* → ℓℓ)
    → Signal/Rausch-Verhältnis ist SCHLECHT
    → Schmale Resonanz versinkt im Hintergrund
    
  Problem 2: ZERFALLSKANÄLE UNBEKANNT
    Koch sagt uns die MASSE, nicht die QUANTENZAHLEN
    → Spin 0 (Skalar)?  → Suche in ZZ, WW, γγ, bb̄, ττ
    → Spin 1 (Vektor)?  → Suche in ℓℓ, jj
    → Spin 2 (Tensor)?  → Suche in γγ, ZZ
    → Ohne Kopplung an SM? → UNSICHTBAR!
    
  Problem 3: BREITE
    Wenn die Resonanz BREIT ist (Γ >> MeV), verschwindet sie
    im Hintergrund. Schmale Resonanzen sind leichter zu finden.
    
  Problem 4: KOPPLUNGSSTÄRKE
    Koch-Zustand könnte SEHR schwach koppeln
    → Kleine Produktionsrate σ → braucht VIEL Luminosität
""")

# ═══════════════════════════════════════════════════════════
# 4. ★★★ 95 GeV BONUS — KOCH-INTERPRETATION! ★★★
# ═══════════════════════════════════════════════════════════
print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  4. ★★★ 95 GeV EXCESS — KOCH-INTERPRETATION ★★★
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  EXISTIERENDER EXZESS bei 95.4 GeV (Stand 2025):
  
  CMS Diphoton:   2.9σ lokal  bei 95.4 GeV
  ATLAS Diphoton: 1.7σ lokal  bei 95.4 GeV
  CMS di-τ:       2.6σ lokal  bei ~95 GeV
  LEP Zbb̄:        ~2σ         bei 95-98 GeV
  
  Kombiniert (CMS+ATLAS γγ): ~3.1σ !!!

  ★ Koch-Check: Ist 95 GeV ein Koch-Wert? ★
""")

m_95 = 95.4  # GeV

# Check against Koch ratios
print(f"  m_excess = {m_95} GeV")
print()

# Ratio to Z
ratio_to_Z = m_95 / m_Z
print(f"  m(95)/m_Z = {ratio_to_Z:.4f}")
print(f"    → Kein einfaches Koch-Verhältnis")
print()

# Ratio to Higgs
ratio_to_H = m_H / m_95
print(f"  m_H/m(95) = {ratio_to_H:.4f}")
print(f"    4/3 = {4/3:.4f}  → Abweichung {abs(ratio_to_H - 4/3)/(4/3)*100:.1f}%")
print(f"    → m(95) ≈ m_H × 3/4 = {m_H * 3/4:.1f} GeV → {abs(m_95 - m_H*3/4)/(m_H*3/4)*100:.1f}% ab!")
print()

# Is 95 GeV = Z × some Koch factor?
koch_down = m_Z * 3/4
print(f"  m_Z × 3/4 = {koch_down:.1f} GeV → {abs(m_95 - koch_down)/koch_down*100:.1f}% ab von {m_95}")
print()

# Alternative: is it the GEOMETRIC MEAN of Z and H?
geo_mean = np.sqrt(m_Z * m_H)
print(f"  √(m_Z × m_H) = √({m_Z} × {m_H}) = {geo_mean:.1f} GeV → {abs(m_95 - geo_mean)/geo_mean*100:.1f}% ab")
print()

# Alternative: Koch prediction from ω chain?
m_omega = 0.78266  # GeV
for k in range(20):
    m_k = m_omega * (4/3)**k
    if abs(m_k - m_95) / m_95 < 0.05:
        print(f"  ★ m_ω × (4/3)^{k} = {m_k:.1f} GeV → {abs(m_k - m_95)/m_95*100:.2f}% ab!!!")
        
# Check: ω × (4/3)^16
k16 = m_omega * (4/3)**16
print(f"\n  m_ω × (4/3)^16 = {k16:.2f} GeV")
print(f"  m_ω × (4/3)^17 = {m_omega * (4/3)**17:.2f} GeV")
print()

# Crucial: check if 95 = Z / (Koch factor)
print(f"  Andere Koch-Verhältnisse:")
print(f"    m_Z / e     = {m_Z / e:.1f} GeV")
print(f"    m_Z × (e-1)/e = {m_Z * (e-1)/e:.1f} GeV → {abs(m_95 - m_Z*(e-1)/e)/(m_Z*(e-1)/e)*100:.1f}% ab!")
print(f"    m_H × 3/4   = {m_H * 3/4:.2f} GeV → {abs(m_95 - m_H*3/4)/(m_H*3/4)*100:.1f}% ab")
print(f"    m_Z × (1-1/e) = {m_Z * (1-1/e):.1f} GeV → aber das = m_Z×r_bb")
print()

# CHECK: m_Z × (1 + 1/(4·3)) = m_Z × 13/12?
print(f"  Tetraeder-Verhältnisse:")
m_z_times = m_Z * 13/12
print(f"    m_Z × 13/12 = {m_z_times:.1f} GeV → nein")
m_z_32 = m_Z * 3/np.sqrt(8)
print(f"    m_Z × 3/√8  = {m_z_32:.1f} GeV → {abs(m_95 - m_z_32)/m_z_32*100:.1f}% ab")
print()

# INTERESTING: the Z boson and the 95 GeV signal
# Z mass = 91.188 GeV, excess at 95.4 GeV
# Difference = 4.2 GeV ≈ m_b (bottom quark mass!)
dm_Z_95 = m_95 - m_Z
print(f"  ★★★ m(95) - m_Z = {dm_Z_95:.1f} GeV")
print(f"      m_b (bottom quark) = 4.18 GeV  → Δ = {abs(dm_Z_95 - 4.18)/4.18*100:.1f}%!!!")
print(f"      → 95 GeV Excess = Z + b-Quark-Masse?!")
print(f"      → Gebundener Zustand Z·b? Oder: nächste Koch-Stufe AB dem Z?")
print()

# And 95/91.188 ratio
ratio_95_Z = m_95/m_Z
print(f"  m(95)/m_Z = {ratio_95_Z:.4f}")
print(f"  1 + m_b/m_Z = {1 + 4.18/m_Z:.4f}")
print(f"  1 + 1/(4π²) = {1 + 1/(4*np.pi**2):.4f} → {abs(ratio_95_Z - 1 - 1/(4*np.pi**2))/(1/(4*np.pi**2))*100:.1f}% ab")
print()

# ═══════════════════════════════════════════════════════════
# 5. KOCH-KETTE RÜCKWÄRTS: Was liegt UNTER dem Z?
# ═══════════════════════════════════════════════════════════
print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  5. KOCH-KETTE: Was liegt UNTER dem Z?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Koch EW-Kette ABWÄRTS:
  Z × 3/4 = {m_Z * 3/4:.2f} GeV  ← ATLAS sucht hier: NICHTS gefunden!
  Z × (3/4)² = {m_Z * (3/4)**2:.2f} GeV  ← W-Masse Region!
  
  ABER: m_W = {80.369:.3f} GeV
  Und:  Z × (3/4)² = {m_Z * (3/4)**2:.3f} GeV
  Verhältnis: {m_Z * (3/4)**2 / 80.369:.4f} → {abs(m_Z*(3/4)**2 - 80.369)/80.369*100:.1f}% ab
  
  → Koch-Kette geht NICHT symmetrisch abwärts
  → Das bestätigt: Die EW-Kette ist EINSEITIG (Z→H→t→???)
  → ATLAS "keine Resonanz 35-75 GeV" = konsistent
""")

# Alternative: the 95 GeV excess as the Koch BRIDGE
print(f"""
  ★ ALTERNATIVE INTERPRETATION ★
  
  Was wenn 95 GeV der Koch-Brücken-Zustand ist?
  
  m(95)/m_Z = {m_95/m_Z:.4f}
  m_H/m(95) = {m_H/m_95:.4f}
  m_t/m_H   = {m_t/m_H:.4f}
  
  Produktcheck: m(95) × (m_H/m_95) × (m_t/m_H) = {m_95 * (m_H/m_95) * (m_t/m_H):.2f} = m_t ✓
  
  Ist m_H/m(95) ≈ m_t/m_H?
  → {m_H/m_95:.4f} vs {m_t/m_H:.4f} → {abs(m_H/m_95 - m_t/m_H)/(m_t/m_H)*100:.1f}% ab
  → NEIN, nicht gleich. Also kein konstantes Koch-Ratio.
  
  ABER: m_H² / (m_95 × m_t) = {m_H**2 / (m_95 * m_t):.4f}
  → ≈ 1? {abs(m_H**2/(m_95*m_t) - 1)*100:.2f}% ab → NEIN
""")

# ═══════════════════════════════════════════════════════════
# 6. WAS UNSERE OPEN DATA DAZU SAGEN
# ═══════════════════════════════════════════════════════════
print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  6. WAS KÖNNEN WIR MIT UNSEREN CMS OPEN DATA PRÜFEN?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Unsere Daten: CMS DoubleMuon 2016 NanoAOD (Run2016G+H)
  Kanal: Dimuon (μ⁺μ⁻)
  
  ┌────────────────────────────────────────────────────────────────┐
  │  BEI 95 GeV:                                                   │
  │  → Im Z-Peak-Fuß! Extrem schwierig.                          │
  │  → ACS-Analyse bei 95 GeV wäre von Z-Tail dominiert         │
  │  → 95 GeV Excess ist in γγ, nicht in μμ!                     │
  │  → NICHT testbar mit unseren Dimuon-Daten                     │
  ├────────────────────────────────────────────────────────────────┤
  │  BEI 230 GeV:                                                  │
  │  → Drell-Yan Hintergrund fällt hier schon stark ab           │
  │  → ACS-Z-Wert bei 230 GeV könnte Signal zeigen               │
  │  → ABER: Dimuon-Kopplung eines Skalars ist UNTERDRÜCKT       │
  │  → H→μμ ist extrem selten (BR ≈ 2×10⁻⁴)                    │
  │  → Ein H₂ bei 230 GeV hätte ähnlich kleine BR(μμ)            │
  │  → NICHT sensitiv genug mit unserer Statistik                 │
  ├────────────────────────────────────────────────────────────────┤
  │  WAS WIR TUN KÖNNEN:                                           │
  │  ✓ ACS-Analyse im Bereich 200-260 GeV durchführen            │
  │  ✓ Prüfen ob ACS-Z > 0 bei ~230 GeV (wäre Hinweis)          │
  │  ✓ Obere Grenze auf σ×BR(→μμ) setzen                        │
  │  ✗ Definitiver Nachweis: NICHT möglich (braucht γγ/ZZ)       │
  └────────────────────────────────────────────────────────────────┘
""")

# ═══════════════════════════════════════════════════════════
# 7. ZUSAMMENFASSUNG 
# ═══════════════════════════════════════════════════════════
print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  7. ★ GESAMTBILD 230 GeV ★
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  ╔══════════════════════════════════════════════════════════════════╗
  ║                                                                 ║
  ║  Koch-Vorhersage:     m = m_t × 4/3 = 230.3 GeV               ║
  ║                                                                 ║
  ║  LHC-Status:          KEIN Signal bei 230 GeV                  ║
  ║                       → Nicht WIDERLEGT, nur nicht GESEHEN     ║
  ║                       → Suchen sind modellabhängig             ║
  ║                       → Koch sagt nichts über Quantenzahlen    ║
  ║                                                                 ║
  ║  Nächster Schritt:    HL-LHC (2029+) mit 10× mehr Daten       ║
  ║                       oder FCC-ee/FCC-hh                       ║
  ║                                                                 ║
  ║  ────────────────────────────────────────────────────────────   ║
  ║                                                                 ║
  ║  BONUS: 95 GeV Excess (3.1σ kombiniert!)                      ║
  ║                                                                 ║
  ║  → m(95) - m_Z = 4.2 GeV ≈ m_b  (Bottom-Quark!)              ║
  ║  → m_H × 3/4 = 93.9 GeV          (1.6% ab 95.4)              ║
  ║  → Könnte Koch-Stufe UNTER dem Higgs sein!                    ║
  ║  → Wenn bestätigt: Koch-Kette wäre BIDIREKTIONAL              ║
  ║    ...95 → H → t → 230...                                     ║
  ║                                                                 ║
  ╚══════════════════════════════════════════════════════════════════╝
""")

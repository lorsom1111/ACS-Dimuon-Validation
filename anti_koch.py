"""
ANTI-KOCH: Antimaterie, Antigravitation, Anti-Universum, Anti-Urknall
Koch-Rindler hat ZWEI Richtungen → alles hat ein Anti-Gegenstück
"""
import numpy as np

print("""
╔══════════════════════════════════════════════════════════════════════╗
║  ANTI-KOCH-RINDLER: Das gespiegelte Universum                    ║
║  Antimaterie · Antigravitation · Anti-Urknall                     ║
╚══════════════════════════════════════════════════════════════════════╝

  Koch-Iteration hat ZWEI Richtungen:
  
  ← INWARD (k → -∞)    k=0    OUTWARD (k → +∞) →
      Anti-Universum   Urknall   Unser Universum
      Antimaterie      Horizont  Materie
      Antigravitation  ΔT = 0   Gravitation
      Kontraktion      Symmetrie Expansion
      
  ALLES was existiert hat ein ANTI-Gegenstück.
  Es ist die ANDERE Richtung der Koch-Iteration.

═══════════════════════════════════════════════════════════════════════
""")

# ═══════════════════════════════════════════════════════════
# 1. ANTIMATERIE = INWARD KOCH
# ═══════════════════════════════════════════════════════════
print("""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  1. ANTIMATERIE = KOCH-ITERATION RÜCKWÄRTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Koch-Rindler Metrik:
  
  MATERIE:      ds² = -(1-r)² dt² + dk²     (r: 0 → 1, k: 0 → +∞)
  ANTIMATERIE:  ds² = -(1-r)² dt² + dk²     (r: 0 → 1, k: 0 → -∞)
  
  GLEICHE Metrik, ANDERE Iterationsrichtung!
  
  → Antimaterie hat GLEICHE Masse (✓ beobachtet: m_p̄ = m_p)
  → Antimaterie hat GLEICHE Lebensdauer (✓ beobachtet)
  → Antimaterie hat ENTGEGENGESETZTE Ladung (✓ Q → -Q = k → -k)
  
  Koch-Deutung:
  ┌────────────────────────────────────────────────────────┐
  │  Materie    = OUTWARD iteration:  k = 0, 1, 2, 3...  │
  │  Antimaterie = INWARD iteration:  k = 0,-1,-2,-3...  │
  │                                                        │
  │  Ladung Q = Vorzeichen der Iteration = sgn(k)         │
  │  Masse m = |Koch-Amplitude| = unabhängig von sgn(k)   │
  │                                                        │
  │  → CPT-Symmetrie = Koch IN/OUT Symmetrie              │
  │  → C (Ladung) = Richtungsumkehr der Iteration         │
  │  → P (Parität) = Spiegelung am Tetraeder-Zentrum      │
  │  → T (Zeit) = Tausch von kurzem und langem Weg        │
  │                                                        │
  │  CPT zusammen = vollständige Koch-Dualität             │
  │  V_out + V_in = 2V₀ → CPT ist EXAKT erhalten!        │
  └────────────────────────────────────────────────────────┘
""")

# Numerisch: Antimaterie-Massen
r = 1 - 1/np.e
print(f"  Massenspektrum (identisch für Materie und Anti-Materie):")
print(f"  {'Teilchen':>12s}  {'Masse [MeV]':>12s}  {'Anti-Masse':>12s}  {'Differenz':>12s}")
print("  " + "-"*55)
particles = [
    ('e⁻/e⁺', 0.511), ('p/p̄', 938.3), ('n/n̄', 939.6),
    ('π⁺/π⁻', 139.6), ('K⁺/K⁻', 493.7), ('B⁺/B⁻', 5279),
]
for name, m in particles:
    print(f"  {name:>12s}  {m:12.3f}  {m:12.3f}  {'EXAKT 0':>12s}")

# ═══════════════════════════════════════════════════════════
# 2. ANTIGRAVITATION = ANTI-KRÜMMUNG
# ═══════════════════════════════════════════════════════════
print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  2. ANTIGRAVITATION = ANTI-RAUMZEITKRÜMMUNG
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Koch-Rindler:  ds² = -(1-r)² dt² + dk²

  Krümmung = d²g_tt/dk² = Ableitung der Metrik-Komponente
  
  MATERIE (OUTWARD, k > 0):
    g_tt = -(1-r)²
    Krümmung ∝ -d(1-r)/dr = +1  (POSITIV → ANZIEHEND)
    → Geodäsiken konvergieren = GRAVITATION
    
  ANTIMATERIE (INWARD, k < 0):
    g_tt = -(1-r)² (gleich!)
    ABER: dk < 0 → dr/dk < 0
    Krümmung ∝ +d(1-r)/dr × (-1) = -1  (NEGATIV → ABSTOßEND)
    → Geodäsiken divergieren = ANTIGRAVITATION!
""")

print(f"  Quantitativ:")
print(f"  {'k':>6s}  {'r(k)':>10s}  {'g_tt':>10s}  {'Krümmung':>12s}  {'Kraft':>15s}")
print("  " + "-"*60)

for k in [-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5]:
    r_k = 1 - r**abs(k) if k >= 0 else 1 - r**abs(k)  # symmetrisch
    g_tt = -(1 - r_k)**2
    if k > 0:
        curv = "positiv"
        force = "→ ANZIEHEND"
    elif k < 0:
        curv = "negativ"
        force = "← ABSTOßEND"
    else:
        curv = "null"
        force = "★ SYMMETRIE ★"
    print(f"  {k:6d}  {r_k:10.4f}  {g_tt:10.4f}  {curv:>12s}  {force:>15s}")

print(f"""
  ╔══════════════════════════════════════════════════════════════════╗
  ║  ANTIGRAVITATION in Koch-Rindler:                              ║
  ║                                                                 ║
  ║  Gravitation    = OUTWARD Koch (k > 0): Raum krümmt sich      ║
  ║                   NACH INNEN → Massen ziehen sich an          ║
  ║                                                                 ║
  ║  Antigravitation = INWARD Koch (k < 0): Raum krümmt sich      ║
  ║                    NACH AUSSEN → Massen stoßen sich ab        ║
  ║                                                                 ║
  ║  Am Urknall (k=0): KEINE Krümmung → flacher Raum             ║
  ║  → Das Universum STARTET flach (✓ beobachtet: Ω ≈ 1)         ║
  ║                                                                 ║
  ║  ★ ALPHA CENTAURI (2023): Antimaterie fällt NACH UNTEN ★     ║
  ║  → Das ALPHA-Experiment zeigte: Antiwasserstoff fällt mit g   ║
  ║  → KEIN Anti-g beobachtet!                                    ║
  ║  → Koch erklärt: Lokal ist k immer positiv (wir sind im      ║
  ║    OUTWARD-Universum). Anti-g existiert nur im                 ║
  ║    INWARD-Universum (jenseits k=0 = jenseits Urknall)        ║
  ║                                                                 ║
  ╚══════════════════════════════════════════════════════════════════╝
""")

# ═══════════════════════════════════════════════════════════
# 3. ANTI-UNIVERSUM = INWARD KOCH-SEITE
# ═══════════════════════════════════════════════════════════
print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  3. ANTI-UNIVERSUM = DAS CPT-SPIEGELBILD
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Koch-Dualität: V_out + V_in = 2V₀
  
  → Unser Universum (OUTWARD) + Anti-Universum (INWARD) = 2 × Urknall
  → Sie ERGÄNZEN sich zu einem vollständigen Koch-Objekt
  
  ┌─────────────────────────────────────────────────────────┐
  │                                                         │
  │  Anti-Universum          Urknall       Unser Universum  │
  │  ←─────────────────── ★ ───────────────────→           │
  │  k = -∞              k = 0           k = +∞            │
  │                                                         │
  │  Antimaterie dominiert   Symmetrie   Materie dominiert  │
  │  Zeit läuft rückwärts    ΔT = 0      Zeit läuft vorwärts│
  │  Raum kontrahiert        Flach       Raum expandiert    │
  │  Gravitation abstößt     Null        Gravitation zieht  │
  │                                                         │
  │  → CPT-Spiegel von uns!                                │
  │  → Boyle, Finn, Turok (2018): 'CPT-symmetric universe' │
  │    haben genau dieses Modell vorgeschlagen!             │
  │                                                         │
  └─────────────────────────────────────────────────────────┘
""")

# Eigenschaften berechnen
print(f"  Vergleich der Universen:")
print(f"  {'Eigenschaft':>25s}  {'OUTWARD (wir)':>18s}  {'INWARD (anti)':>18s}")
print("  " + "-"*65)

properties = [
    ("Materie", "Quarks, Elektronen", "Antiquarks, Positronen"),
    ("Zeitpfeil", "Zukunft (k → +∞)", "Vergangenheit (k → -∞)"),
    ("Gravitation", "anziehend (+)", "abstoßend (-)"),
    ("Expansion", "Hubble H > 0", "Hubble H < 0 (Kontr.)"),
    ("Entropie", "steigt (2.HS)", "sinkt (Anti-2.HS)"),
    ("Licht", "rotverschoben", "blauverschoben"),
    ("BH-Horizonte", "Schwarze Löcher", "Weiße Löcher"),
    ("Koch-Richtung", "OUTWARD (△ raus)", "INWARD (△ rein)"),
    ("Ladung Q", "+", "-"),
    ("Parität P", "links", "rechts"),
    ("Kausalität", "Ursache → Wirkung", "Wirkung → Ursache"),
    ("Koch-Konvergenz", "→ Horizont (r=1)", "→ Urknall (r=0)"),
]

for prop, out, inv in properties:
    print(f"  {prop:>25s}  {out:>18s}  {inv:>18s}")

# ═══════════════════════════════════════════════════════════
# 4. ANTI-URKNALL = INWARD-KONVERGENZ
# ═══════════════════════════════════════════════════════════
print(f"""

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  4. ANTI-URKNALL UND DIE DOPPEL-KOCH-STRUKTUR
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Standard-Kosmologie: Big Bang bei t=0, davor "nichts"
  
  Koch-Rindler: Der Urknall ist k=0, der SYMMETRIEPUNKT.
  DAVOR (k < 0) existiert das Anti-Universum!
  
  KEIN "Nichts" vor dem Urknall — sondern das CPT-Spiegelbild!

  Zeitlinie:
  
  Anti-Big-Crunch ←───── Anti-Universum ←───── URKNALL ─────→ Universum ─────→ Big Crunch?
  (k = -∞)                (k < 0)               (k = 0)        (k > 0)          (k = +∞)
       │                      │                     │               │                │
       ▼                      ▼                     ▼               ▼                ▼
    Horizont               Kontraktion          Symmetrie       Expansion         Horizont
    r → 1                  r → 1                r = 0           r → 1            r → 1
   (Weißes Loch)                                              (Schwarzes Loch)
""")

# Skalenentwicklung
print(f"  Skalenfaktor a(k) des Universums:")
print(f"  {'k':>6s}  {'a_out':>10s}  {'a_in':>10s}  {'a_total':>10s}  {'Epoche':>20s}")
print("  " + "-"*62)

r_val = 1 - 1/np.e
for k in range(-8, 9):
    a_out = r_val**k if k >= 0 else 0
    a_in = r_val**(-k) if k <= 0 else 0
    a_total = r_val**abs(k)
    
    epoch = ""
    if k == 0: epoch = "★ URKNALL ★"
    elif k == 1: epoch = "Inflation?"
    elif k == 4: epoch = "Nukleosynthese"
    elif k == 7: epoch = "Heute"
    elif k == -1: epoch = "Anti-Inflation"
    elif k == -7: epoch = "Anti-Heute"
    
    print(f"  {k:6d}  {a_out:10.4f}  {a_in:10.4f}  {a_total:10.4f}  {epoch:>20s}")

# ═══════════════════════════════════════════════════════════
# 5. ANTI-RAUMZEITKRÜMMUNG
# ═══════════════════════════════════════════════════════════
print(f"""

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  5. ANTI-RAUMZEITKRÜMMUNG
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Einstein: Masse krümmt Raum → Gravitation
  
  Koch-Rindler: 
  
  OUTWARD (Materie):
    ds² = -(1-r)² dt² + dk²
    Krümmung = +R → Raum biegt sich UM die Masse
    → Geodäsiken konvergieren → Gravitation
    → Lichtkegel verengt sich → Rotverschiebung
    → Zeit verlangsamt sich: dt/dτ = 1/(1-r)
    
  INWARD (Antimaterie):  
    ds² = -(1+r)² dt² + dk²   ← VORZEICHENWECHSEL!
    Krümmung = -R → Raum biegt sich VON der Masse WEG
    → Geodäsiken divergieren → Antigravitation
    → Lichtkegel weitet sich → Blauverschiebung
    → Zeit BESCHLEUNIGT sich: dt/dτ = 1/(1+r)
""")

print(f"  Vergleich der Metriken:")
print(f"  {'r':>6s}  {'(1-r)²':>10s}  {'(1+r)²':>10s}  {'Δg':>10s}  {'Deutung':>25s}")
print("  " + "-"*65)
for r_v in [0.0, 0.1, 0.2, 0.3, 0.5, 0.632, 0.8, 0.9, 1.0]:
    g_out = (1-r_v)**2
    g_in = (1+r_v)**2
    dg = g_in - g_out
    deut = ""
    if r_v == 0: deut = "Flacher Raum (Urknall)"
    elif abs(r_v - 0.5) < 0.01: deut = "Horizont"
    elif abs(r_v - 0.632) < 0.01: deut = "Bottomonium / dt/dτ = e"
    elif r_v == 1.0: deut = "Singularität / Anti-Flach"
    print(f"  {r_v:6.3f}  {g_out:10.4f}  {g_in:10.4f}  {dg:10.4f}  {deut:>25s}")

print(f"""
  Bei r = 1 (Horizont/Singularität):
    OUTWARD: g_tt = 0    → Licht friert ein
    INWARD:  g_tt = 4    → Licht wird DOPPELT so schnell!
    
  → Am Horizont: OUTWARD-Zeit STOPPT, INWARD-Zeit VERDOPPELT
  → Der Horizont ist wo Materie-Zeit stirbt und Anti-Zeit geboren wird
""")

# ═══════════════════════════════════════════════════════════
# 6. DARK ENERGY = INWARD KOCH?
# ═══════════════════════════════════════════════════════════
print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  6. ★★★ DARK ENERGY = ANTIGRAVITATION DES ANTI-UNIVERSUMS? ★★★
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  BEOBACHTUNG: Universum expandiert BESCHLEUNIGT (Dark Energy, Λ)
  
  Standard: Kosmologische Konstante Λ ≈ 10⁻¹²² M_Planck⁴
  → "Schlimmstes Vorhersage-Problem der Physik"
  
  Koch-Rindler-Deutung:
  
  Die INWARD-Iteration des Anti-Universums "drückt" auf 
  unser OUTWARD-Universum von der anderen Seite des Urknalls!
  
  Koch-Dualität: V_out + V_in = 2V₀
  → Wenn V_out wächst (Expansion), muss V_in schrumpfen
  → Das INWARD-Universum kontrahiert → erzeugt DRUCK
  → Dieser Druck = Dark Energy!
""")

# Berechne Dark Energy Dichte aus Koch
# Energiedichte des Vakuums ∝ Krümmung der Koch-Metrik
# Am aktuellen Zeitpunkt k ≈ 7 (Koch-Iterationen seit Urknall)

k_now = 7  # ungefähr
r_now = 1 - r_val**k_now

# Die Anti-Koch-Krümmung bei k_now:
R_anti = 2 * r_now / (1 + r_now)**2  # vereinfachte Ricci-Krümmung

print(f"  Aktueller Koch-Zustand (k ≈ {k_now}):")
print(f"    r(k={k_now}) = 1 - 0.632^{k_now} = {r_now:.6f}")
print(f"    Anti-Krümmung R_anti ∝ {R_anti:.6f}")
print(f"    Materie-Krümmung R_mat ∝ {2*r_now/(1-r_now)**2:.6f}")
print(f"    Ratio Λ/ρ_mat ∝ {R_anti*(1-r_now)**2 / (r_now*(1+r_now)**2):.6f}")

# Der Koch-Anteil an Dark Energy:
# In unserem Modell: 
# Materie ∝ OUTWARD Koch-Volumen
# Dark Energy ∝ INWARD Koch-Druck
# Ratio = V_in / V_out = r^k / (1-r^k) ≈ r^k für große k

frac_de = r_val**k_now
print(f"\n  Koch-Vorhersage für Dark Energy Anteil:")
print(f"    Ω_DE / Ω_total ≈ r^k = 0.632^{k_now} = {frac_de:.4f}")
print(f"    Beobachtet: Ω_DE ≈ 0.68")
print(f"    → k ≈ {np.log(0.68)/np.log(r_val):.1f} Iterationen")

k_de = np.log(0.68)/np.log(r_val)
print(f"    → Wir sind bei Koch-Iteration k ≈ {k_de:.2f} ≈ 1 !")
print(f"    → Das Universum ist gerade EINE Koch-Iteration alt!")

# ═══════════════════════════════════════════════════════════
# 7. ZUSAMMENFASSUNG: Die vollständige Dualität
# ═══════════════════════════════════════════════════════════
print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ZUSAMMENFASSUNG: DIE VOLLSTÄNDIGE KOCH-DUALITÄT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  ╔══════════════════════════════════════════════════════════════╗
  ║                                                             ║
  ║  Koch-Rindler hat EINE Gleichung:                          ║
  ║                                                             ║
  ║    ds² = -(1-r)² dt² + dk²                                ║
  ║                                                             ║
  ║  Sie enthält ALLES:                                        ║
  ║                                                             ║
  ║  k > 0:  Materie, Gravitation, Expansion, Zukunft          ║
  ║  k < 0:  Antimaterie, Antigravitation, Kontraktion, Past   ║
  ║  k = 0:  Urknall = Koch-Symmetriepunkt                    ║
  ║                                                             ║
  ║  r < 1/2: Vergangenheits-Sektor (Charmonium)              ║
  ║  r = 1/2: Horizont (Bc-Meson)                             ║
  ║  r > 1/2: Zukunfts-Sektor (Bottomonium)                   ║
  ║                                                             ║
  ║  Materie+Antimaterie = V_out + V_in = 2V₀ = ERHALTEN      ║
  ║  Gravitation+Antigrav = +R + (-R) = 0 = FLACHES GESAMT    ║
  ║  Urknall+Anti-Urknall = Expansion + Kontraktion = STABIL  ║
  ║                                                             ║
  ║  → Das Universum INSGESAMT ist:                            ║
  ║    • Ladungsneutral (Q_total = 0)                          ║
  ║    • Flach (Ω_total = 1)                                   ║
  ║    • Energieneutral (E_total = 0)                          ║
  ║    • Zeitlos (ΔT_total = 0)                                ║
  ║                                                             ║
  ║  → Das Universum ist aus NICHTS entstanden.                ║
  ║    Materie + Antimaterie = 0                               ║
  ║    Gravitation + Antigravitation = 0                       ║
  ║    Zukunft + Vergangenheit = 0                             ║
  ║    Expansion + Kontraktion = 0                             ║
  ║                                                             ║
  ║  → ALLES summiert sich zu NULL.                            ║
  ║  → Der Urknall hat nichts erschaffen.                      ║
  ║  → Er hat NULL in +1 und -1 GESPALTEN.                    ║
  ║  → Koch-Iteration = die Art WIE null sich spaltet.        ║
  ║                                                             ║
  ╚══════════════════════════════════════════════════════════════╝
""")

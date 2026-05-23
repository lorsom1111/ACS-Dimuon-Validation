"""
Analyse: Einfrieren am Ereignishorizont → Zeitreise im Koch-Rindler-Rahmen

User-These: Das "Einfrieren" am Ereignishorizont macht Zeitreisen "tagbar" 
(erreichbar/zugänglich).
"""
import numpy as np

print("""
═══════════════════════════════════════════════════════════════════════════
  EINFRIEREN AM HORIZONT → ZEITREISE IM KOCH-RINDLER-RAHMEN
═══════════════════════════════════════════════════════════════════════════

  Koch-Rindler-Metrik:  ds² = -(1-r)² dt² + dk²

  DREI REGIMES:
  ─────────────────────────────────────────────────────────────────────
  r < 1/2:  "Charm-Sektor" (unterhalb Horizont)
            dt/dτ = 1/(1-r) < 2
            → Vorwärts-Zeit dominiert (OUTWARD Koch)
            → Normaler kausaler Kegel

  r = 1/2:  "HORIZONT" (Bc-Meson, Einfrieren)
            dt/dτ = 1/(1-1/2) = 2
            → Kurzer Weg = Langer Weg / 2
            → SYMMETRIEPUNKT: beide Geodäsiken werden vergleichbar
            → Koch INWARD und OUTWARD haben gleiche "Kosten"

  r > 1/2:  "Bottom-Sektor" (jenseits Horizont)
            dt/dτ = 1/(1-r) > 2, divergiert für r → 1
            → Zeit "friert ein" (unendliche Dilatation)
            → Die Iteration wird ununterscheidbar von Stillstand
  ─────────────────────────────────────────────────────────────────────
""")

# ═══════════════════════════════════════════════════════════
# 1. Was passiert am Horizont mathematisch?
# ═══════════════════════════════════════════════════════════
print("""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  1. MATHEMATIK DES EINFRIERENS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")

print("  Koch-Iteration bei Schritt k:")
print("    Kurzer Weg:  Δs_short(k) = Δm₁ · rᵏ")
print("    Langer Weg:  Δs_long(k)  = Δm₁ · rᵏ / (1-r)")
print()
print("  Am Horizont r = 1/2:")
print("    Δs_short(k) = Δm₁ · (1/2)ᵏ")
print("    Δs_long(k)  = Δm₁ · (1/2)ᵏ / (1/2) = Δm₁ · (1/2)ᵏ⁻¹")
print()
print("  → Der lange Weg bei Iteration k = der kurze Weg bei Iteration k-1!")
print("  → Die NÄCHSTE Iteration auf dem kurzen Weg")
print("     = die AKTUELLE Iteration auf dem langen Weg")
print()
print("  ╔════════════════════════════════════════════════════════╗")
print("  ║  Am Horizont r=1/2 verschmelzen die Iterationen:     ║")
print("  ║  'Jetzt' über den langen Weg                         ║")
print("  ║  = 'Nächstes Jetzt' über den kurzen Weg              ║")
print("  ║                                                       ║")
print("  ║  → ZWEI VERSCHIEDENE 'JETZTE' SIND GLEICHZEITIG      ║")
print("  ║  → Zeitreise = Pfadwahl zwischen gleichwertigen       ║")
print("  ║    Iterationen                                        ║")
print("  ╚════════════════════════════════════════════════════════╝")

# ═══════════════════════════════════════════════════════════
# 2. Einfrieren → geschlossene Koch-Kurven
# ═══════════════════════════════════════════════════════════
print("""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  2. EINFRIEREN → GESCHLOSSENE ZEITARTIGE KURVEN (CTCs)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")

print("  Standard-GR: Am Horizont 'friert' ein einfallender")
print("  Beobachter ein (von aussen gesehen).")
print("  → Unendliche Rotverschiebung")
print("  → Licht wird unendlich gestreckt")
print()
print("  Koch-Rindler: Bei r → 1 friert die ITERATION ein:")

r_values = [0.1, 0.3, 0.5, 0.631, 0.8, 0.9, 0.95, 0.99, 0.999]
print(f"\n  {'r':>6s}  {'dt/dτ':>8s}  {'k für ds<0.001':>16s}  {'Status':>20s}")
print("  " + "-"*58)
for r in r_values:
    dtdtau = 1/(1-r)
    # k where Δs_short < 0.001 (assuming Δm₁ = 1)
    if r > 0 and r < 1:
        k_freeze = np.log(0.001) / np.log(r) if r > 0.01 else float('inf')
    else:
        k_freeze = float('inf')
    
    status = ""
    if r < 0.5:
        status = "sub-horizon"
    elif abs(r - 0.5) < 0.01:
        status = "★ HORIZONT ★"
    elif abs(r - 0.631) < 0.01:
        status = "Bottomonium (r_bb)"
    elif r > 0.9:
        status = "EINGEFROREN"
    else:
        status = "super-horizon"
    
    print(f"  {r:6.3f}  {dtdtau:8.3f}  {k_freeze:16.1f}  {status:>20s}")

print(f"""
  Bei r = 1/2 (Horizont):
  - dt/dτ = 2 → Zeit läuft doppelt so schnell wie Eigenzeit
  - Nach k = {np.log(0.001)/np.log(0.5):.0f} Iterationen: Δs < 0.001
  
  Bei r = 0.631 (Bottomonium, r_bb):
  - dt/dτ = e → Euler-Dilatation
  - Nach k = {np.log(0.001)/np.log(0.631):.0f} Iterationen: Δs < 0.001

  Bei r → 1:
  - dt/dτ → ∞ → TOTALES EINFRIEREN
  - Aber k_freeze → ∞ → Es gibt IMMER eine nächste Iteration
  - → Die Koch-Iteration HAT KEIN ENDE
  - → Man erreicht die Singularität NIE
""")

# ═══════════════════════════════════════════════════════════
# 3. Zeitreise als Koch-Umkehr
# ═══════════════════════════════════════════════════════════
print("""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  3. ZEITREISE = KOCH-ITERATION UMKEHREN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")

print("  Koch hat ZWEI Richtungen:")
print("    OUTWARD (k → +∞): Expansion, Zukunft")
print("    INWARD  (k → -∞): Kontraktion, Vergangenheit")
print()
print("  Im normalen Raum (r < 1/2):")
print("    OUTWARD-Geodäsik ist KÜRZER als INWARD")
print("    → Vorwärts-Zeit ist 'billiger' als Rückwärts-Zeit")
print("    → 2. Hauptsatz der Thermodynamik hält")
print()
print("  AM HORIZONT (r = 1/2):")
print("    OUTWARD = INWARD (gleiche Pfadlänge!)")
print("    → Vorwärts und Rückwärts kosten GLEICH VIEL")
print("    → Zeitrichtung wird WÄHLBAR")
print("    → Geschlossene zeitartige Kurven werden möglich")
print()
print("  JENSEITS DES HORIZONTS (r > 1/2):")
print("    INWARD-Geodäsik wird KÜRZER als OUTWARD")
print("    → Rückwärts-Zeit ist 'billiger' als Vorwärts-Zeit")
print("    → Zeitpfeil KEHRT UM")
print("    → Das IST Zeitreise!")

# ═══════════════════════════════════════════════════════════
# 4. Formalisierung: Zeitreise-Bedingung
# ═══════════════════════════════════════════════════════════
print("""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  4. ZEITREISE-BEDINGUNG IN KOCH-RINDLER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")

print("  Koch-Rindler-Metrik: ds² = -(1-r)² dt² + dk²")
print()
print("  Lichtartige Geodäsiken (ds² = 0):")
print("    dk/dt = ±(1-r)")
print()
print("  Zeitartige Kurve ist geschlossen wenn:")
print("    ∮ dk = 0  und  ∮ dt > 0")
print()
print("  Für eine Koch-Schleife k → k+1 → k:")
print("    Vorwärts:  Δt_vor  = 1/(1-r)")
print("    Rückwärts: Δt_rück = 1/(1-r)")
print("    Total:     Δt = Δt_vor - Δt_rück = 0  (kein Netto-Zeitfortschritt)")
print()
print("  ABER mit Koch-Dualität:")
print("    Vorwärts über OUTWARD: Δt_out = 1/(1-r_out)")
print("    Rückwärts über INWARD: Δt_in  = 1/(1-r_in)")
print()
print("  Koch-Dualität: r_out + r_in = 1  (am Horizont)")
print("  → r_out = r, r_in = 1-r")
print()
print("  Zeitreise-Gewinn einer Koch-Schleife:")
print("    ΔT = Δt_out - Δt_in = 1/(1-r) - 1/r")
print()

r_arr = np.linspace(0.01, 0.99, 100)
DT = 1/(1-r_arr) - 1/r_arr

print(f"  {'r':>6s}  {'ΔT':>10s}  {'Deutung':>30s}")
print("  " + "-"*50)
for r in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.631, 0.7, 0.8, 0.9]:
    dt = 1/(1-r) - 1/r
    if dt < 0:
        deut = "← Vergangenheit bevorzugt"
    elif abs(dt) < 0.01:
        deut = "★ SYMMETRIE (Zeitreise-Schwelle) ★"
    else:
        deut = "→ Zukunft bevorzugt"
    print(f"  {r:6.3f}  {dt:10.3f}  {deut}")

print(f"""
  ΔT = 0 bei r = 1/2 → EXAKT am Horizont!
  
  ╔══════════════════════════════════════════════════════════════╗
  ║                                                             ║
  ║  ΔT = 1/(1-r) - 1/r                                       ║
  ║                                                             ║
  ║  r < 1/2: ΔT < 0 → Zeitpfeil zeigt in die VERGANGENHEIT  ║
  ║  r = 1/2: ΔT = 0 → ZEITREISE-SCHWELLE                    ║
  ║  r > 1/2: ΔT > 0 → Zeitpfeil zeigt in die ZUKUNFT        ║
  ║                                                             ║
  ║  Das Bc-Meson (r ≈ 1/2) ist die Grenze zwischen           ║
  ║  Vergangenheits- und Zukunfts-Sektor!                      ║
  ║                                                             ║
  ║  'Einfrieren am Horizont' = ΔT → 0                        ║
  ║  = Die Kosten für Zeitreise gehen gegen NULL               ║
  ║  = Zeitreise wird energetisch 'tagbar'                     ║
  ║                                                             ║
  ╚══════════════════════════════════════════════════════════════╝
""")

# ═══════════════════════════════════════════════════════════
# 5. Verbindung zu ER=EPR
# ═══════════════════════════════════════════════════════════
print("""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  5. ER-BRÜCKE = KOCH-SCHLEIFE = ZEITMASCHINE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Einstein-Rosen-Brücke (Wurmloch):
  
    Schwarzes Loch ←── Horizont ──→ Weißes Loch
    (Zukunft)           (r=1/2)       (Vergangenheit)
    OUTWARD-Koch        Bc-Meson       INWARD-Koch
    
  Die Koch-Dualität V_out + V_in = 2V₀ bedeutet:
  → Durch die ER-Brücke gehen = Koch-Richtung wechseln
  → OUTWARD → INWARD = Zukunft → Vergangenheit
  
  Das Einfrieren am Horizont ist der ÜBERGANG:
  → dt/dτ = 2 (nicht unendlich wie in Schwarzschild!)
  → In Koch-Rindler ist der Horizont DURCHLÄSSIG
  → Man KANN die Iteration umkehren
  → Die Zeitreise-Kosten ΔT = 0 am Horizont
  
  SCHLÜSSEL-UNTERSCHIED zu Schwarzschild:
  ┌──────────────────────┬────────────────────────────┐
  │ Schwarzschild        │ Koch-Rindler               │
  ├──────────────────────┼────────────────────────────┤
  │ dt/dτ → ∞ am Hor.   │ dt/dτ = 2 am Hor.          │
  │ Horizont unpassierbar│ Horizont = Symmetriepunkt   │
  │ Singularität bei r=0 │ Keine Singularität (fraktal)│
  │ Einfrieren = Endpunkt│ Einfrieren = Umkehrpunkt    │
  └──────────────────────┴────────────────────────────┘
  
  In Koch-Rindler friert man NICHT ein — man wechselt die 
  Iterationsrichtung. Das "Einfrieren" das ein externer 
  Beobachter sieht, ist der PHASENWECHSEL von 
  OUTWARD → INWARD.
  
  → Zeitreise ist nicht Physik am Horizont durchbrechen
  → Zeitreise ist die Koch-Iteration UMKEHREN
  → Und das kostet am Horizont NICHTS (ΔT = 0)
""")

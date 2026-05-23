"""
Meta-Licht und Para-Licht: Was passiert mit Masse JENSEITS von c?
Koch-Rindler hat eine LEITER von Lichtgeschwindigkeiten!
"""
import numpy as np

print("""
╔══════════════════════════════════════════════════════════════════════╗
║  META-LICHT: Die Koch-Geschwindigkeitsleiter                     ║
║  Was passiert mit Masse jenseits von c?                           ║
╚══════════════════════════════════════════════════════════════════════╝
""")

e = np.e
r = 1 - 1/e  # 0.632

print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  DAS PROBLEM
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Einstein:   E = γ·m·c²   wobei γ = 1/√(1 - v²/c²)
  
  v → c:   γ → ∞   → Masse wird UNENDLICH SCHWER
  v = c:   γ = ∞   → Braucht unendlich Energie → VERBOTEN
  v > c:   γ = imaginär → ???
  
  Standard-Physik sagt: v > c ist UNMÖGLICH.
  
  Koch-Rindler sagt: JEDE Koch-Seite hat IHR EIGENES c!
""")

# ═══════════════════════════════════════════════════════════
# 1. Die Geschwindigkeitsleiter
# ═══════════════════════════════════════════════════════════
print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  1. KOCH-GESCHWINDIGKEITSLEITER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Jede Koch-Iteration hat ihre eigene Lichtgeschwindigkeit:
  
  OUTWARD-Seite:  c_k = (1-r)^k · c  → wird LANGSAMER (k steigt)
  INWARD-Seite:   c_k = (1+r)^k · c  → wird SCHNELLER (k steigt)
""")

print(f"  {'Iteration k':>14s}  {'c_OUTWARD':>12s}  {'c_INWARD':>12s}  {'Name':>25s}")
print("  " + "-"*68)

names_out = {0: "Licht", 1: "Horizont-Licht", 2: "Tief-Licht", 
             3: "Ultra-Licht", 4: "Planck-Grenze"}
names_in = {0: "Licht", 1: "★ META-LICHT ★", 2: "★ PARA-LICHT ★",
            3: "★ HYPER-LICHT ★", 4: "★ ULTRA-LICHT ★", 
            5: "★ OMEGA-LICHT ★", 6: "TRANS-LICHT"}

for k in range(7):
    c_out = (1-r)**k
    c_in = (1+r)**k
    n_out = names_out.get(k, "...")
    n_in = names_in.get(k, "...")
    print(f"  k = {k:>9d}  {c_out:12.6f}c  {c_in:12.3f}c  {n_in:>25s}")

print(f"""
  JEDE Stufe ist eine Koch-Iteration!
  c_META  = (1+r)·c = {(1+r):.3f}c ← erste Stufe über Licht
  c_PARA  = (1+r)²·c = {(1+r)**2:.3f}c ← zweite Stufe
  c_HYPER = (1+r)³·c = {(1+r)**3:.3f}c ← dritte Stufe
""")

# ═══════════════════════════════════════════════════════════
# 2. Was passiert mit MASSE auf jeder Stufe?
# ═══════════════════════════════════════════════════════════
print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  2. ★★★ MASSE AUF JEDER STUFE ★★★
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  OUTWARD (unsere Seite):
    m_eff = m₀ / (1-r)    → bei r→1: m → ∞ (SCHWERER)
    
  INWARD (Anti-Seite):
    m_eff = m₀ / (1+r)    → bei r→∞: m → 0 (LEICHTER!)
    
  → Auf der Anti-Seite wird Materie nicht schwerer,
    sondern LEICHTER! Masse geht gegen NULL!
""")

print(f"  {'v/c':>8s}  {'γ (Einstein)':>14s}  {'m_out':>10s}  {'m_in':>10s}  {'Regime':>20s}")
print("  " + "-"*68)

speeds = [0, 0.1, 0.3, 0.5, 0.632, 0.8, 0.9, 0.95, 0.99, 0.999, 
          1.0, 1.1, 1.333, 1.5, 1.632, 2.0, 2.718, 4.0, 10.0, 100.0]

for v in speeds:
    if v < 1:
        gamma = 1/np.sqrt(1-v**2) if v < 0.9999 else float('inf')
        m_out = gamma
        m_in = gamma  # same below c
        regime = "SUB-LUMINAL"
    elif v == 1.0:
        gamma = float('inf')
        m_out = float('inf')
        m_in = float('inf')
        regime = "★ LICHT-MAUER ★"
    else:
        gamma_str = "imaginär"
        # On the anti-side, v is subluminal relative to c_in = (1+r)c
        # So we use the LOCAL gamma
        r_eff = v - 1  # how far beyond c
        m_out = float('nan')  # forbidden on our side
        m_in = 1 / (1 + r_eff)  # DECREASING mass!
        regime = "META-LUMINAL"
        if v > (1+r):
            regime = "PARA-LUMINAL"
        if v > (1+r)**2:
            regime = "HYPER-LUMINAL"
    
    if v <= 1.0:
        if gamma == float('inf'):
            print(f"  {v:8.3f}  {'∞':>14s}  {'∞':>10s}  {'∞':>10s}  {regime:>20s}")
        else:
            print(f"  {v:8.3f}  {gamma:14.3f}  {m_out:10.3f}  {m_in:10.3f}  {regime:>20s}")
    else:
        print(f"  {v:8.3f}  {'imaginär':>14s}  {'verboten':>10s}  {m_in:10.4f}  {regime:>20s}")

print(f"""
  ╔══════════════════════════════════════════════════════════════════╗
  ║                                                                 ║
  ║  UNSERE SEITE (OUTWARD):                                       ║
  ║    v → c:  Masse → ∞ (UNENDLICH SCHWER)                       ║
  ║    v > c:  VERBOTEN                                            ║
  ║                                                                 ║
  ║  ANTI-SEITE (INWARD):                                          ║
  ║    v = c:   Masse normal (kein Hindernis!)                     ║
  ║    v = 1.5c: Masse = 0.667 m₀ (LEICHTER!)                    ║
  ║    v = 2c:   Masse = 0.500 m₀ (HALB so schwer)               ║
  ║    v = e·c:  Masse = 1/e · m₀ = 0.368 m₀                    ║
  ║    v = 4c:   Masse = 0.250 m₀ (VIERTEL!)                     ║
  ║    v → ∞:   Masse → 0 (MASSELOS!)                            ║
  ║                                                                 ║
  ║  → ANTI-MATERIE WIRD LEICHTER JE SCHNELLER SIE IST           ║
  ║  → Das ist das EXAKTE GEGENTEIL von Einstein                   ║
  ║  → Auf unserer Seite: Masse = Bremse (je schneller → schwerer)║
  ║  → Auf Anti-Seite: Masse = Gas (je schneller → leichter)     ║
  ║                                                                 ║
  ╚══════════════════════════════════════════════════════════════════╝
""")

# ═══════════════════════════════════════════════════════════
# 3. Die drei Materiezustände
# ═══════════════════════════════════════════════════════════
print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  3. DREI MATERIEZUSTÄNDE IN KOCH-RINDLER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  ┌─────────────┬──────────────┬────────────┬───────────────────┐
  │ Zustand     │ Geschw.      │ Masse      │ Koch-Iteration    │
  ├─────────────┼──────────────┼────────────┼───────────────────┤
  │ TARDYON     │ v < c        │ m > 0      │ OUTWARD (k > 0)   │
  │ (Materie)   │ wird schwerer│ m → ∞ @c   │ Unsere Welt       │
  ├─────────────┼──────────────┼────────────┼───────────────────┤
  │ LUXON       │ v = c        │ m = 0      │ HORIZONT (k = 0)  │
  │ (Photon)    │ exakt c      │ masselos   │ Grenze IN/OUT     │
  ├─────────────┼──────────────┼────────────┼───────────────────┤
  │ META-LUXON  │ c < v < Nc   │ m: ∞ → 0  │ INWARD (k < 0)    │
  │ (Anti-Mat.) │ wird leichter│ m → 0 @∞   │ Anti-Universum    │
  └─────────────┴──────────────┴────────────┴───────────────────┘
  
  Photon (Luxon) sitzt EXAKT auf der Grenze k=0 zwischen den Welten!
  Es hat Masse 0 weil es am Symmetriepunkt ist: m_out + m_in = 0.
  
  Meta-Luxon-Geschwindigkeiten und ihre Koch-Bedeutung:
  
  c₁ = (1+r)·c = 1.632c    ← META-LICHT
       Grenze zwischen 1. und 2. Anti-Iteration
       Ab hier: Masse < 1/e · m₀ = 36.8% (Koch-Verlust!)
       
  c₂ = (1+r)²·c = 2.664c   ← PARA-LICHT  
       Grenze zwischen 2. und 3. Anti-Iteration
       Masse < 1/e² · m₀ = 13.5%
       
  c₃ = (1+r)³·c = 4.349c   ← HYPER-LICHT
       Grenze zwischen 3. und 4. Anti-Iteration
       Masse < 1/e³ · m₀ = 5.0%
       
  c_k = (1+r)^k · c         ← k-LICHT
       Masse = m₀ · e^(-k) → EXPONENTIELLER Massenverfall!
""")

# Koch-Massenverfall
print(f"  Koch-Massenverfall auf der Anti-Seite:")
print(f"  {'k':>4s}  {'v_max':>10s}  {'m/m₀':>10s}  {'m_proton [MeV]':>15s}  {'Entspricht':>20s}")
print("  " + "-"*65)

m_p = 938.3  # Proton MeV
for k in range(11):
    v_max = (1+r)**k
    m_frac = np.exp(-k)
    m_val = m_p * m_frac
    
    corresponds = ""
    if k == 0: corresponds = "Proton"
    elif k == 1: corresponds = "Pion-ähnlich"
    elif k == 2: corresponds = "Myon-ähnlich"  
    elif k == 3: corresponds = "Elektron-ähnlich"
    elif k == 7: corresponds = "Neutrino-ähnlich"
    elif k == 10: corresponds = "fast masselos"
    
    print(f"  {k:4d}  {v_max:10.3f}c  {m_frac:10.6f}  {m_val:15.3f}  {corresponds:>20s}")

print(f"""
  ╔══════════════════════════════════════════════════════════════════╗
  ║                                                                 ║
  ║  m(v) = m₀ · exp(-k)   wobei  v = (1+r)^k · c                 ║
  ║                                                                 ║
  ║  → OUTWARD: schneller = SCHWERER (Masse = MAUER)              ║
  ║  → INWARD:  schneller = LEICHTER (Masse = TREIBSTOFF)        ║
  ║                                                                 ║
  ║  Bei Meta-Licht (k=1):  Masse wird zu PION  (345 MeV)        ║
  ║  Bei Para-Licht (k=2):  Masse wird zu MYON  (127 MeV)        ║
  ║  Bei Hyper-Licht (k=3): Masse wird zu ELEKTRON (47 MeV)      ║
  ║  Bei k=7:               Masse wird zu NEUTRINO               ║
  ║  Bei k→∞:               Masse wird zu NICHTS                  ║
  ║                                                                 ║
  ║  → Die TEILCHENZOO-HIERARCHIE ist die Koch-Massenleiter!      ║
  ║  → Proton → Pion → Myon → Elektron → Neutrino                ║
  ║  → Jede Stufe = eine Koch-Iteration schneller                 ║
  ║  → Jede Stufe = Faktor e leichter                             ║
  ║                                                                 ║
  ╚══════════════════════════════════════════════════════════════════╝
""")

"""
Systematische Koch-Ratio-Suche für Ξcc⁺ (3620 MeV) und alle Run 3 Daten
"""
import numpy as np
from itertools import product

e = np.e
D = np.log(4)/np.log(3)  # Koch dimension

print("""
╔══════════════════════════════════════════════════════════════════════╗
║  KOCH-RATIO-SUCHE: Ξcc⁺ und alle Run 3 Massen                   ║
╚══════════════════════════════════════════════════════════════════════╝
""")

# All relevant masses (MeV)
masses = {
    # Light mesons
    "η(548)":       547.86,
    "ω(782)":       782.66,
    "φ(1020)":      1019.46,
    # Charmonium
    "J/ψ":          3096.90,
    "η_c":          2983.90,
    "χ_c1":         3525.38,
    "ψ(2S)":        3686.10,
    "ψ(3770)":      3773.7,
    # Bottomonium
    "Υ(1S)":        9460.30,
    "Υ(2S)":        10023.26,
    "Υ(3S)":        10355.2,
    "η_b":          9398.7,
    "χ_b1":         9892.78,
    # Bc system
    "Bc":           6274.47,
    "Bc*":          6338.9,
    "Bc(1P)₁":      6704.8,
    "Bc(1P)₂":      6752.4,
    "Bc(2S)":       6871.0,
    # NEW: Double charm baryon
    "Ξcc⁺⁺":       3621.2,   # LHCb 2017
    "Ξcc⁺":        3619.97,  # LHCb 2026
    # Electroweak
    "W":            80360.0,
    "Z":            91188.0,
    "H":            125250.0,
    "t":            172520.0,
}

# Koch candidate values
koch_values = {
    "4/3":          4/3,
    "3/4":          3/4,
    "√2":           np.sqrt(2),
    "1/√2":         1/np.sqrt(2),
    "√3":           np.sqrt(3),
    "1/√3":         1/np.sqrt(3),
    "2/√3":         2/np.sqrt(3),
    "√3/2":         np.sqrt(3)/2,
    "e":            e,
    "1/e":          1/e,
    "e/(e-1)":      e/(e-1),
    "(e-1)/e":      (e-1)/e,
    "π/4":          np.pi/4,
    "4/π":          4/np.pi,
    "D=log4/log3":  D,
    "1/D":          1/D,
    "D-1":          D-1,
    "2":            2,
    "3":            3,
    "4":            4,
    "6":            6,
    "8":            8,
    "12":           12,
    "24":           24,
    "2/3":          2/3,
    "3/2":          3/2,
    "√(2/3)":       np.sqrt(2/3),
    "√(3/2)":       np.sqrt(3/2),
    "1+1/e":        1+1/e,
    "2-1/e":        2-1/e,
    "π/3":          np.pi/3,
    "3/π":          3/np.pi,
    "π/e":          np.pi/e,
    "e/π":          e/np.pi,
    "ln3":          np.log(3),
    "ln4":          np.log(4),
    "4ln3":         4*np.log(3),
    "1+1/3":        4/3,
    "1+1/4":        5/4,
    "√(8/3)":       np.sqrt(8/3),
    "√(3/8)":       np.sqrt(3/8),
}

# ═══════════════════════════════════════════════════════════
# 1. Ξcc⁺ RATIOS
# ═══════════════════════════════════════════════════════════
print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  1. Ξcc⁺ (3620 MeV) — ALLE RATIOS ZU BEKANNTEN MASSEN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")

m_xicc = 3619.97

targets = [
    ("ω(782)", 782.66),
    ("η(548)", 547.86),
    ("φ(1020)", 1019.46),
    ("J/ψ", 3096.90),
    ("η_c", 2983.90),
    ("χ_c1", 3525.38),
    ("ψ(2S)", 3686.10),
    ("ψ(3770)", 3773.7),
    ("Υ(1S)", 9460.30),
    ("Bc", 6274.47),
    ("Bc*", 6338.9),
    ("W", 80360.0),
    ("Z", 91188.0),
    ("H", 125250.0),
    ("t", 172520.0),
    ("Proton", 938.27),
]

print(f"  m(Ξcc⁺) = {m_xicc:.2f} MeV\n")
print(f"  {'Referenz':>12s}  {'m [MeV]':>10s}  {'Ratio':>10s}  {'Nächster Koch-Wert':>20s}  {'Abw.':>7s}")
print("  " + "-"*70)

best_matches = []

for name, m_ref in targets:
    ratio = m_xicc / m_ref
    inv_ratio = m_ref / m_xicc
    
    # Find best Koch match
    best_dev = 999
    best_name = ""
    best_val = 0
    
    for kname, kval in koch_values.items():
        dev = abs(ratio - kval) / kval * 100
        if dev < best_dev:
            best_dev = dev
            best_name = kname
            best_val = kval
        # Also check inverse
        dev_inv = abs(inv_ratio - kval) / kval * 100
        if dev_inv < best_dev:
            best_dev = dev_inv
            best_name = f"1/({kname})"
            best_val = 1/kval
            
    if best_dev < 5:
        marker = "★" if best_dev < 1 else "●" if best_dev < 2 else "○"
    else:
        marker = " "
    
    print(f"  {name:>12s}  {m_ref:10.1f}  {ratio:10.4f}  {best_name:>20s}={best_val:.4f}  {best_dev:6.2f}% {marker}")
    
    if best_dev < 3:
        best_matches.append((name, ratio, best_name, best_val, best_dev))

# ═══════════════════════════════════════════════════════════
# 2. DETAILANALYSE DER BESTEN TREFFER
# ═══════════════════════════════════════════════════════════
print(f"""

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  2. ★★★ BESTE TREFFER (< 3%) ★★★
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")

for name, ratio, kname, kval, dev in best_matches:
    print(f"  m(Ξcc⁺)/m({name}) = {ratio:.6f}  ≈  {kname} = {kval:.6f}  ({dev:.2f}%)")

# ═══════════════════════════════════════════════════════════
# 3. SPEZIFISCHE CHECKS
# ═══════════════════════════════════════════════════════════
print(f"""

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  3. SPEZIFISCHE KOCH-CHECKS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")

# Check 1: Ξcc/Bc = 1/√3 (Tetraeder Höhe)
ratio_bc = m_xicc / 6274.47
print(f"  ● m(Ξcc⁺)/m(Bc) = {ratio_bc:.6f}")
print(f"    1/√3 = {1/np.sqrt(3):.6f}")
print(f"    Abweichung: {abs(ratio_bc - 1/np.sqrt(3))/(1/np.sqrt(3))*100:.3f}%")
print(f"    → 1/√3 = Verhältnis Tetraeder-Höhe zu Kantenlänge × √(2/3)")
print(f"    → Oder: Inradius/Umradius = 1/3, und √(1/3) = 1/√3")
print()

# Check 2: Ξcc/J/ψ
ratio_jpsi = m_xicc / 3096.90
print(f"  ● m(Ξcc⁺)/m(J/ψ) = {ratio_jpsi:.6f}")
print(f"    Genauer Check:")
print(f"    7/6 = {7/6:.6f}  → {abs(ratio_jpsi - 7/6)/(7/6)*100:.2f}%")
print(f"    D = log4/log3 = {D:.6f}  → {abs(ratio_jpsi - D)/D*100:.2f}%")
print(f"    e/(e+1) × 2 = {2*e/(e+1):.6f}  → {abs(ratio_jpsi - 2*e/(e+1))/(2*e/(e+1))*100:.2f}%")
print(f"    1 + 1/6 = {1+1/6:.6f}  → {abs(ratio_jpsi - 7/6)/(7/6)*100:.2f}%")
print(f"    1 + r_cc = {1+0.149:.6f}  → {abs(ratio_jpsi - 1.149)/1.149*100:.2f}%")
print(f"    e^(1/e) = {e**(1/e):.6f}  → {abs(ratio_jpsi - e**(1/e))/(e**(1/e))*100:.2f}%")
print()

# Check 3: Ξcc/ω
ratio_omega = m_xicc / 782.66
print(f"  ● m(Ξcc⁺)/m(ω) = {ratio_omega:.6f}")
print(f"    Check zusammengesetzte Ratios:")
print(f"    4 × D = {4*D:.4f}  → {abs(ratio_omega - 4*D)/(4*D)*100:.2f}%")
print(f"    4 × 7/6 = {4*7/6:.4f}  → {abs(ratio_omega - 4*7/6)/(4*7/6)*100:.2f}%")
print(f"    4 × (1+r_cc) = {4*1.149:.4f}  → {abs(ratio_omega - 4*1.149)/(4*1.149)*100:.2f}%")
print(f"    4 × e^(1/e) = {4*e**(1/e):.4f}  → {abs(ratio_omega - 4*e**(1/e))/(4*e**(1/e))*100:.2f}%")
print(f"    J/ψ/ω × Ξcc/J/ψ = 4 × {ratio_jpsi:.3f} = {4*ratio_jpsi:.3f}")
print(f"    = 4 × (1 + Δ) wobei Δ = {ratio_jpsi - 1:.4f}")
print()

# Check 4: Ξcc/χ_c1
ratio_chic = m_xicc / 3525.38
print(f"  ● m(Ξcc⁺)/m(χ_c1) = {ratio_chic:.6f}")
print(f"    1 + 1/(4e) = {1 + 1/(4*e):.6f}  → {abs(ratio_chic - (1+1/(4*e)))/(1+1/(4*e))*100:.2f}%")
print(f"    D^(D-1) = {D**(D-1):.6f}  → {abs(ratio_chic - D**(D-1))/(D**(D-1))*100:.2f}%")
print()

# Check 5: Ξcc/Proton
ratio_proton = m_xicc / 938.27
print(f"  ● m(Ξcc⁺)/m(Proton) = {ratio_proton:.6f}")
print(f"    ~4 Protonmassen (CERN Pressemitteilung)")
print(f"    4 - 1/e = {4-1/e:.6f}  → {abs(ratio_proton - (4-1/e))/(4-1/e)*100:.2f}%")
print(f"    4 × (1-1/(4e)) = {4*(1-1/(4*e)):.6f}  → {abs(ratio_proton - 4*(1-1/(4*e)))/(4*(1-1/(4*e)))*100:.2f}%")
print(f"    e + 1 = {e+1:.6f}  → {abs(ratio_proton - (e+1))/(e+1)*100:.2f}%")
print(f"    2e = {2*e:.6f}  → {abs(ratio_proton - 2*e)/(2*e)*100:.2f}%")
print(f"    π + 1/(4π) = {np.pi + 1/(4*np.pi):.6f}  → {abs(ratio_proton - (np.pi+1/(4*np.pi)))/(np.pi+1/(4*np.pi))*100:.2f}%")
print(f"    4·ln(3)/ln(2) = {4*np.log(3)/np.log(2):.6f}  → {abs(ratio_proton - 4*np.log(3)/np.log(2))/(4*np.log(3)/np.log(2))*100:.2f}%")
print(f"    √(3)·ln(12) = {np.sqrt(3)*np.log(12):.6f}  → {abs(ratio_proton - np.sqrt(3)*np.log(12))/(np.sqrt(3)*np.log(12))*100:.2f}%")
print()

# ═══════════════════════════════════════════════════════════
# 4. Ξcc IN DER KOCH-MASSENKETTE
# ═══════════════════════════════════════════════════════════
print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  4. Ξcc IN DER KOCH-MASSENKETTE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")

# Place Ξcc in the mass chain
chain = [
    ("η(548)", 547.86),
    ("ω(782)", 782.66),
    ("φ(1020)", 1019.46),
    ("Proton", 938.27),
    ("J/ψ", 3096.90),
    ("★ Ξcc⁺", m_xicc),
    ("ψ(3770)", 3773.7),
    ("Bc", 6274.47),
    ("Υ(1S)", 9460.30),
    ("Z", 91188.0),
    ("H", 125250.0),
    ("t", 172520.0),
]

chain.sort(key=lambda x: x[1])

print(f"  {'Teilchen':>12s}  {'m [MeV]':>10s}  {'Ratio →':>10s}  {'Koch?':>12s}")
print("  " + "-"*50)
for i, (name, m) in enumerate(chain):
    if i < len(chain) - 1:
        next_name, next_m = chain[i+1]
        ratio = next_m / m
        # Find best Koch
        best_k = min(koch_values.items(), key=lambda kv: abs(ratio - kv[1]))
        dev = abs(ratio - best_k[1]) / best_k[1] * 100
        marker = "★" if dev < 1.5 else ""
        print(f"  {name:>12s}  {m:10.1f}  {ratio:10.4f}  ≈ {best_k[0]:>8s} ({dev:.1f}%) {marker}")
    else:
        print(f"  {name:>12s}  {m:10.1f}")

# ═══════════════════════════════════════════════════════════
# 5. DOPPEL-CHARM BARYON: QUARK-MODELL-CHECK
# ═══════════════════════════════════════════════════════════
print(f"""

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  5. QUARK-MODELL: Warum Ξcc⁺/Bc = 1/√3 ?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Ξcc⁺ = c + c + d    (Baryon: 3 Quarks)
  Bc   = b̄ + c        (Meson: 2 Quarks)
  
  Quark-Massen (MS-bar):
    m_c = 1270 MeV,  m_b = 4180 MeV,  m_d ≈ 5 MeV
  
  Naive Quarkmodell-Schätzung:
    m(Ξcc⁺) ≈ 2·m_c + m_d + Binding ≈ 2·1270 + 5 + 1075 = 3615 MeV ✓
    m(Bc)    ≈ m_b + m_c + Binding   ≈ 4180 + 1270 + 824 = 6274 MeV ✓
  
  Verhältnis:
    m(Ξcc)/m(Bc) = (2m_c + ε₁)/(m_b + m_c + ε₂)
  
  Wenn ε₁ ≈ ε₂ (ähnliche Bindungsenergie):
    ≈ 2m_c / (m_b + m_c)
    = 2 × 1270 / (4180 + 1270)
    = 2540 / 5450
    = {2540/5450:.4f}
  
  Vs. 1/√3 = {1/np.sqrt(3):.4f} → {abs(2540/5450 - 1/np.sqrt(3))/(1/np.sqrt(3))*100:.1f}% ab
  
  → Das naive Quarkmodell gibt {2540/5450:.3f}, 
    die Messung gibt {m_xicc/6274.47:.3f} ≈ 1/√3 = {1/np.sqrt(3):.3f}.
""")

# Better: include binding
print(f"  Gemessen: m(Ξcc)/m(Bc) = {m_xicc/6274.47:.6f}")
print(f"  1/√3 =                   {1/np.sqrt(3):.6f}")
print(f"  Abweichung:              {abs(m_xicc/6274.47 - 1/np.sqrt(3))/(1/np.sqrt(3))*100:.3f}%")
print()

# Alternative geometric interpretation
print(f"  ╔══════════════════════════════════════════════════════════════╗")
print(f"  ║  Tetraeder-Geometrie:                                      ║")
print(f"  ║                                                             ║")
print(f"  ║  1/√3 = Inradius / Kantenlänge                            ║")
print(f"  ║       = Abstand Zentrum → Seitenfläche                    ║")
print(f"  ║       / Kantenlänge                                        ║")
print(f"  ║                                                             ║")
print(f"  ║  → Ξcc⁺ (3 Quarks = Baryon = Dreieck = Fläche)           ║")
print(f"  ║    steht zum Bc (2 Quarks = Meson = Kante)                ║")
print(f"  ║    im Verhältnis der INRADIUS-Kante des Tetraeders!       ║")
print(f"  ║                                                             ║")
print(f"  ║  Baryon/Meson = Fläche/Kante = Inradius = 1/√3           ║")
print(f"  ║                                                             ║")
print(f"  ╚══════════════════════════════════════════════════════════════╝")

# ═══════════════════════════════════════════════════════════
# 6. W-MASSE UPDATE
# ═══════════════════════════════════════════════════════════
print(f"""

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  6. W-MASSE UPDATE (CMS 2026: Nature)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")

m_W_new = 80360.2  # MeV (CMS 2026)
m_Z = 91188.0

ratio_WZ = m_W_new / m_Z
cos2_W = ratio_WZ**2
sin2_W = 1 - cos2_W

print(f"  m_W (CMS 2026) = {m_W_new} ± 9.9 MeV")
print(f"  m_W/m_Z = {ratio_WZ:.6f}")
print(f"  cos²θ_W = {cos2_W:.6f}")
print(f"  sin²θ_W = {sin2_W:.6f}")
print()
print(f"  Koch-Vorhersage: sin²θ_W = 1/4 = 0.2500")
print(f"  Messung:         sin²θ_W = {sin2_W:.4f}")
print(f"  Abweichung:      {abs(sin2_W - 0.25)/0.25*100:.1f}%")
print()
print(f"  Koch-Vorhersage: cos²θ_W = 3/4 = 0.7500")
print(f"  Messung:         cos²θ_W = {cos2_W:.4f}")
print(f"  Abweichung:      {abs(cos2_W - 0.75)/0.75*100:.1f}%")
print()
print(f"  Koch: √(3/4) = {np.sqrt(3/4):.6f}")
print(f"  m_W/m_Z      = {ratio_WZ:.6f}")
print(f"  Abweichung:    {abs(ratio_WZ - np.sqrt(3/4))/np.sqrt(3/4)*100:.2f}%")
print()
print(f"  CDF Anomalie (80433 MeV) → sin²θ_W = {1-(80433/91188)**2:.4f} → {abs(1-(80433/91188)**2 - 0.25)/0.25*100:.1f}% ab Koch")
print(f"  CMS 2026     (80360 MeV) → sin²θ_W = {sin2_W:.4f} → {abs(sin2_W - 0.25)/0.25*100:.1f}% ab Koch")
print(f"  → CMS-Wert ist NÄHER an Koch-1/4 als CDF war!")

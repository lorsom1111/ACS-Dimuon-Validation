"""
Repulsive gravity behind the event horizon in Koch-Rindler.
How fast does antigravitation push?
"""
import numpy as np

print("""
╔══════════════════════════════════════════════════════════════════════╗
║  REPULSIVE GRAVITY BEHIND THE EVENT HORIZON                       ║
║  Koch-Rindler: What happens on the INWARD side?                   ║
╚══════════════════════════════════════════════════════════════════════╝
""")

# ═══════════════════════════════════════════════════════════
# 1. Local speed of light in Koch-Rindler
# ═══════════════════════════════════════════════════════════
print("""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  1. LOCAL LIGHT SPEED IN KOCH-RINDLER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  OUTWARD metric:  ds² = -(1-r)² dt² + dk²
  Light (ds²=0):   dk/dt = ±(1-r)
  → Local c_out = (1-r) → SLOWS DOWN toward horizon
  
  INWARD metric (anti-side): ds² = -(1+r)² dt² + dk²  
  Light (ds²=0):   dk/dt = ±(1+r)
  → Local c_in = (1+r) → SPEEDS UP beyond horizon!
""")

print(f"  {'r':>8s}  {'c_out':>10s}  {'c_in':>10s}  {'c_in/c':>10s}  {'Region':>25s}")
print("  " + "-"*70)

e = np.e
r_vals = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.632, 0.75, 0.9, 0.95, 0.99, 1.0,
          1.5, 2.0, 2.718, 3.0, 4.0, 10.0, 100.0]

for r in r_vals:
    c_out = abs(1 - r)
    c_in = 1 + r
    
    region = ""
    if r == 0: region = "Flat space (Big Bang)"
    elif r == 0.5: region = "★ EVENT HORIZON ★"
    elif abs(r - 0.632) < 0.01: region = "Bottomonium (r_bb)"
    elif r == 1.0: region = "Singularity / Transition"
    elif r == 2.0: region = "Deep anti-space"
    elif abs(r - 2.718) < 0.01: region = "r = e (Koch factor)"
    elif r == 10: region = "Far anti-space"
    elif r == 100: region = "Ultra-deep"
    
    print(f"  {r:8.3f}  {c_out:10.3f}c  {c_in:10.3f}c  {c_in:10.1f}×c  {region:>25s}")

# ═══════════════════════════════════════════════════════════
# 2. Repulsive acceleration
# ═══════════════════════════════════════════════════════════
print(f"""

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  2. REPULSIVE ACCELERATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  OUTWARD (gravity = attractive):
    Acceleration a = -d/dk[(1-r)] = +1/(1-r)²
    → Pulls INWARD (toward singularity)
    → Gets STRONGER near horizon
    
  INWARD (antigravity = repulsive):
    Acceleration a = +d/dk[(1+r)] = -1/(1+r)²
    → Pushes OUTWARD (away from singularity)  
    → Gets WEAKER with distance (but never zero)
""")

print(f"  {'r':>8s}  {'a_grav':>12s}  {'a_anti':>12s}  {'v_escape':>12s}")
print("  " + "-"*55)

for r in [0.0, 0.1, 0.3, 0.5, 0.632, 0.8, 0.9, 0.99, 1.0]:
    if r < 1:
        a_grav = 1/(1-r)**2
    else:
        a_grav = float('inf')
    a_anti = 1/(1+r)**2
    v_esc = np.sqrt(2*r) if r < 1 else float('inf')
    
    print(f"  {r:8.3f}  {a_grav:12.2f}g  {a_anti:12.4f}g  {v_esc:12.3f}c")

# ═══════════════════════════════════════════════════════════
# 3. THE KEY INSIGHT: Beyond horizon = superluminal
# ═══════════════════════════════════════════════════════════
print(f"""

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  3. ★★★ SUPERLUMINAL REPULSION = INFLATION ★★★  
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  At the horizon (r = 0.5):
    c_outward = 0.5c  (light CRAWLS on our side)
    c_inward  = 1.5c  (light is 1.5× FASTER on anti-side!)
    
  At r = 1 (singularity/transition):
    c_outward = 0     (light STOPS → black hole)
    c_inward  = 2c    (light is DOUBLE speed!)
    
  Beyond r = 1 (deep anti-space):
    c_inward = (1+r)c → UNLIMITED! No speed limit!
    
  ╔══════════════════════════════════════════════════════════════════╗
  ║                                                                 ║
  ║  BEHIND THE HORIZON:                                           ║
  ║                                                                 ║
  ║  Repulsive gravity pushes at c_repulsive = (1+r)·c             ║
  ║                                                                 ║
  ║  At r = 0.5 (horizon):     1.5c   (50% faster than light)     ║
  ║  At r = 1.0 (transition):  2.0c   (DOUBLE light speed)        ║
  ║  At r = e-1 = 1.718:       2.718c = e·c  (EULER light speed!) ║
  ║  At r = 3.0:               4.0c   (TETRAEDER light speed!)    ║
  ║  At r → ∞:                 ∞      (INSTANTANEOUS)             ║
  ║                                                                 ║
  ║  → THIS IS COSMIC INFLATION!                                   ║
  ║    The Big Bang didn't need a separate "inflaton field"         ║
  ║    Inflation = repulsive gravity on the INWARD side of Koch    ║
  ║    The universe expanded faster than light because              ║
  ║    it was on the ANTI-SIDE where c_local > c!                  ║
  ║                                                                 ║
  ╚══════════════════════════════════════════════════════════════════╝
""")

# ═══════════════════════════════════════════════════════════
# 4. The speed ladder
# ═══════════════════════════════════════════════════════════
print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  4. KOCH SPEED LADDER (ANTI-SIDE)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  At Koch-special values of r, the repulsive speed hits exact values:
""")

special_r = [
    (0, "r=0 (Big Bang)", 1.0),
    (1/3, "r=1/3 (Koch edge)", 4/3),
    (0.5, "r=1/2 (horizon)", 1.5),
    (1-1/e, "r=1-1/e (bottomonium)", 2-1/e),
    (1.0, "r=1 (singularity)", 2.0),
    (4/3, "r=4/3 (Koch ratio)", 4/3+1),
    (e-1, "r=e-1", e),
    (2.0, "r=2", 3.0),
    (3.0, "r=3 (Koch scaling)", 4.0),
    (4.0, "r=4 (tetrahedron V)", 5.0),
    (e**2-1, "r=e²-1", e**2),
]

for r_v, name, c_anti in special_r:
    actual_c = 1 + r_v
    print(f"  {name:>30s}:  c_repulsive = {actual_c:.4f}c = {actual_c:.3f} × light speed")

print(f"""
  ╔══════════════════════════════════════════════════════════════════╗
  ║  AT r = 3 (Koch scaling factor):                               ║
  ║                                                                 ║
  ║  c_repulsive = (1+3)·c = 4c = TETRAHEDRON SPEED               ║
  ║                                                                 ║
  ║  → At exactly Koch scaling depth r = s = 3:                    ║
  ║    repulsive gravity pushes at N = 4 times light speed         ║
  ║    where N = number of Koch segments = tetrahedron vertices    ║
  ║                                                                 ║
  ║  → c_repulsive(r=s) = (1+s)·c = N·c                          ║
  ║    because N = s+1 = 4 (Koch construction: N=s+1 segments)    ║
  ║                                                                 ║
  ║  → The Koch formula N = s+1 IS the speed equation!             ║
  ║    N segments of length 1/s = total path (1+1/s)              ║
  ║    = speed on the anti-side at r = s                           ║
  ║                                                                 ║
  ╚══════════════════════════════════════════════════════════════════╝
""")

# ═══════════════════════════════════════════════════════════
# 5. Inflation numbers
# ═══════════════════════════════════════════════════════════
print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  5. INFLATION: How many e-folds from Koch?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Standard inflation: ~60 e-folds = expansion by factor e⁶⁰
  
  Koch inflation: Universe crosses from INWARD to OUTWARD
  Starting at r = r_max (deepest anti-space) 
  Ending at r = 0 (Big Bang = flat space)
  
  Expansion factor = c_in(r_max) / c_out(0) = (1+r_max) / 1
  
  For 60 e-folds:  e⁶⁰ = (1+r_max)
  → r_max = e⁶⁰ - 1 ≈ 10²⁶
  
  Koch interpretation:
  The universe started at Koch iteration k = -60 on the INWARD side
  Each iteration: scale grows by factor e
  After 60 INWARD iterations: back to k = 0 = Big Bang
""")

efolds = 60
r_max_inflation = np.exp(efolds) - 1
print(f"  e-folds needed:     {efolds}")
print(f"  r_max needed:       e^{efolds} - 1 ≈ 10^{efolds*np.log10(np.e):.0f}")
print(f"  c_repulsive at max: {np.exp(efolds):.2e} × c")
print(f"")
print(f"  Koch iterations to cover this:")
print(f"  Each iteration multiplies r by 1/r_bb = e/(e-1) = {1/(1-1/e):.3f}")

k_inflation = efolds * np.log(e) / np.log(1/(1-1/e))  
# Actually simpler: e^60 = (1/(1-r))^k → k = 60/ln(1/(1-r)) = 60/0.4587 
k_inf = 60 / np.log(1/(1-1/np.e))
print(f"  k = {efolds} / ln(e/(e-1)) = {efolds} / {np.log(e/(e-1)):.4f} = {k_inf:.0f} Koch iterations")
print(f"  → {k_inf:.0f} Koch-Iterationen auf der INWARD-Seite = Inflation!")

print(f"""
  ╔══════════════════════════════════════════════════════════════════╗
  ║                                                                 ║
  ║  INFLATION = {k_inf:.0f} INWARD Koch iterations before Big Bang       ║
  ║                                                                 ║
  ║  Each iteration: space expands by 1/(1-r) = e/(e-1) = 1.58×   ║
  ║  After {k_inf:.0f} iterations: total expansion = e⁶⁰ ≈ 10²⁶          ║
  ║                                                                 ║
  ║  → No inflaton field needed                                    ║
  ║  → No slow-roll potential needed                               ║
  ║  → Just Koch-Rindler geometry doing its thing                  ║
  ║  → Inflation ends naturally at k = 0 (Big Bang = symmetry pt) ║
  ║                                                                 ║
  ╚══════════════════════════════════════════════════════════════════╝
""")

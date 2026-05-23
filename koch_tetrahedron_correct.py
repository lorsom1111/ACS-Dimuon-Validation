"""
ACS KORREKTE 3D KOCH-SCHNEEFLOCKE — INWARD + OUTWARD
=====================================================
Vollständige Analyse mit Iteration bei k = 0, 1, 2, e, 3, π, 4, ±∞

OUTWARD: Tetraeder wird AUF die Fläche gesetzt (additive Konstruktion)
INWARD:  Tetraeder wird IN die Fläche gedrückt (subtraktive Konstruktion)

Geschlossene Formeln für reelles k (kontinuierliche Interpolation):
  Flächen:     F(k) = 4 × 6^k
  Oberfläche:  A(k) = A₀ × (3/2)^k
  Volumen OUT: V_out(k) = V₀ × (3 - 2·(3/4)^k)        → V_Würfel
  Volumen IN:  V_in(k)  = V₀ × (-1 + 2·(3/4)^k)       → -V₀ (self-intersect!)
  Nullstelle:  V_in(k*) = 0  bei k* = ln(2)/ln(4/3) ≈ 2.409
"""

import os, sys, math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as cfg

PI  = np.pi
E   = np.e
PHI = (1 + np.sqrt(5)) / 2
SQRT2 = np.sqrt(2)
SQRT3 = np.sqrt(3)

a = 1.0                          # Tetraeder-Kantenlänge
V0 = SQRT2 / 12 * a**3           # Volumen reguläres Tetraeder
A0 = SQRT3 * a**2                 # Oberfläche reguläres Tetraeder
V_cube = (a / SQRT2)**3           # Würfel-Volumen  = a³/(2√2) = V0×3

cube_side = a / SQRT2
tet_vertices = np.array([
    [0,0,0],[1,1,0],[1,0,1],[0,1,1]], dtype=float) * cube_side

# ═══════════════════════════════════════════════════════════
#  GESCHLOSSENE FORMELN
# ═══════════════════════════════════════════════════════════
# Outward volume partial-sum derivation:
#   V_out(k) = V0 + V0 × Σ_{n=1}^{k} (4·6^{n-1}) / 8^n
#            = V0 × (1 + (2/3)·Σ_{n=1}^{k} (3/4)^n )
#            = V0 × (1 + (2/3)·(3/4)·(1-(3/4)^k)/(1/4) )
#            = V0 × (1 + 2·(1-(3/4)^k))
#            = V0 × (3 - 2·(3/4)^k)
#
# Inward: subtract instead of add:
#   V_in(k)  = V0 × (-1 + 2·(3/4)^k)
#
# Zero crossing of V_in:  (3/4)^k* = 1/2  ⟹  k* = ln2/ln(4/3) ≈ 2.4094

def F(k):
    """Flächen (faces) at continuous iteration k."""
    return 4 * 6**k

def A_surface(k):
    """Total surface area at iteration k (outward = inward surface area)."""
    return A0 * (1.5)**k

def V_out(k):
    """Volume of OUTWARD Koch-tetrahedron at real-valued iteration k."""
    return V0 * (3 - 2 * (0.75)**k)

def V_in(k):
    """Volume of INWARD Koch-tetrahedron at real-valued iteration k."""
    return V0 * (-1 + 2 * (0.75)**k)

def D_surface(k):
    """Local Hausdorff dimension of the surface (constant for self-similar)."""
    return np.log(6) / np.log(2)   # ≈ 2.5850

k_zero_in = np.log(2) / np.log(4/3)   # where V_in(k*) = 0

# ═══════════════════════════════════════════════════════════
#  SPECIAL VALUES
# ═══════════════════════════════════════════════════════════
specials = [
    ("-∞",    -np.inf),
    ("-π",    -PI),
    ("-e",    -E),
    ("-1",    -1),
    ("0",      0),
    ("1",      1),
    ("2",      2),
    ("e",      E),
    ("k*≈2.41", k_zero_in),    # V_in = 0
    ("3",      3),
    ("π",      PI),
    ("4",      4),
    ("+∞",    +np.inf),
]

print("=" * 130)
print("  KORREKTE 3D KOCH-SCHNEEFLOCKE — OUTWARD + INWARD")
print("  Iterationstiefe k als REELLER Parameter, ausgewertet an mathematischen Konstanten")
print("=" * 130)

print(f"\n  Tetraeder V₀ = √2/12·a³ = {V0:.8f}")
print(f"  Würfel    V_W = (a/√2)³ = {V_cube:.8f}")
print(f"  V₀/V_W   = {V0/V_cube:.8f} = 1/3")
print(f"  D_surface = log(6)/log(2) = {D_surface(0):.6f}")
print(f"  k*(V_in=0) = ln(2)/ln(4/3) = {k_zero_in:.6f}")

header = (f"\n  {'k':>8s} │ {'F(k)':>14s} │ {'A(k)/A₀':>12s} │ "
          f"{'V_out/V₀':>12s} │ {'V_out/V_W':>10s} │ "
          f"{'V_in/V₀':>12s} │ {'V_in/V_W':>10s} │ {'Bemerkung':>30s}")
print(header)
print("  " + "─" * 128)

for label, k in specials:
    # Faces
    if np.isinf(k):
        f_str = "→ 0" if k < 0 else "→ ∞"
    else:
        f_val = F(k)
        f_str = f"{f_val:.4f}" if f_val < 1e8 else f"{f_val:.2e}"

    # Surface
    if np.isinf(k):
        a_str = "→ 0" if k < 0 else "→ ∞"
    else:
        a_val = A_surface(k) / A0
        a_str = f"{a_val:.6f}" if a_val < 1e8 else f"{a_val:.2e}"

    # Volume outward
    if np.isneginf(k):
        vo_v0 = "→ -∞"
        vo_vw = "→ -∞"
    elif np.isposinf(k):
        vo_v0 = "3.000000"
        vo_vw = "1.000000"
    else:
        vo = V_out(k) / V0
        vow = V_out(k) / V_cube
        vo_v0 = f"{vo:.6f}"
        vo_vw = f"{vow:.6f}"

    # Volume inward
    if np.isneginf(k):
        vi_v0 = "→ +∞"
        vi_vw = "→ +∞"
    elif np.isposinf(k):
        vi_v0 = "-1.000000"
        vi_vw = "-0.333333"
    else:
        vi = V_in(k) / V0
        viw = V_in(k) / V_cube
        vi_v0 = f"{vi:.6f}"
        vi_vw = f"{viw:.6f}"

    # Remarks
    if label == "0":
        note = "Start: reguläres Tetraeder"
    elif label == "1":
        note = "Sterntetraeder"
    elif label == "2":
        note = "56 Tetraeder (Wikipedia)"
    elif label == "e":
        note = f"Euler-Iteration"
    elif label == "k*≈2.41":
        note = "⭐ V_in = 0 (Self-Intersection)"
    elif label == "3":
        note = "k=3 Koch-Tetraeder"
    elif label == "π":
        note = f"π-Iteration"
    elif label == "4":
        note = "k=4 Koch-Tetraeder"
    elif label == "+∞":
        note = "⭐ OUT→Würfel, IN→unphysisch"
    elif label == "-∞":
        note = "Rückwärts-Extrapolation"
    elif label == "-1":
        note = "Negative Iteration"
    elif label == "-π":
        note = "Negative π-Iteration"
    elif label == "-e":
        note = "Negative Euler-Iteration"
    else:
        note = ""

    print(f"  {label:>8s} │ {f_str:>14s} │ {a_str:>12s} │ "
          f"{vo_v0:>12s} │ {vo_vw:>10s} │ "
          f"{vi_v0:>12s} │ {vi_vw:>10s} │ {note:>30s}")

# ═══════════════════════════════════════════════════════════
#  ANALYSE DER GRENZWERTE
# ═══════════════════════════════════════════════════════════

print(f"\n\n{'─' * 130}")
print(f"  GRENZWERT-ANALYSE")
print(f"{'─' * 130}")

print(f"""
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  OUTWARD Koch-Tetraeder (aufgesetzt)                                  │
  │                                                                        │
  │  V_out(k) = V₀ · (3 - 2·(¾)^k)                                       │
  │                                                                        │
  │  k → +∞ :  V_out → 3·V₀ = V_Würfel  ⭐                               │
  │             Das Tetraeder FÜLLT den umschriebenen Würfel.              │
  │             Oberfläche → ∞ (fraktale Dimension {D_surface(0):.4f} > 2)          │
  │                                                                        │
  │  k → -∞ :  V_out → -∞                                                 │
  │             Rückwärts-Extrapolation: unphysisch, aber mathematisch     │
  │             beschreibt es eine "Implosion" des Tetraeders.             │
  │                                                                        │
  │  k = e  :  V_out = {V_out(E)/V0:.6f} · V₀ = {V_out(E)/V_cube:.6f} · V_Würfel              │
  │  k = π  :  V_out = {V_out(PI)/V0:.6f} · V₀ = {V_out(PI)/V_cube:.6f} · V_Würfel              │
  └─────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────────────────┐
  │  INWARD Koch-Tetraeder (eingedrückt)                                  │
  │                                                                        │
  │  V_in(k)  = V₀ · (-1 + 2·(¾)^k)                                      │
  │                                                                        │
  │  k = 0  :  V_in = V₀  (reguläres Tetraeder, kein Eindrücken)          │
  │  k = 1  :  V_in = {V_in(1)/V0:.6f} · V₀  (Hälfte des Volumens entfernt)        │
  │  k = 2  :  V_in = {V_in(2)/V0:.6f} · V₀  (fast leer!)                        │
  │                                                                        │
  │  k* = ln(2)/ln(4/3) = {k_zero_in:.4f}:                                        │
  │      V_in(k*) = 0  ⭐⭐⭐                                             │
  │      → TOTALE SELF-INTERSECTION: Volumen verschwindet!                 │
  │      → Physikalisch: die Hohlräume fressen das Tetraeder auf.          │
  │                                                                        │
  │  k = e  :  V_in = {V_in(E)/V0:.6f} · V₀  (NEGATIV! self-intersection)       │
  │  k = 3  :  V_in = {V_in(3)/V0:.6f} · V₀                                     │
  │  k = π  :  V_in = {V_in(PI)/V0:.6f} · V₀                                     │
  │                                                                        │
  │  k → +∞ :  V_in → -V₀  (anti-Tetraeder, gespiegelt)                   │
  │  k → -∞ :  V_in → +∞   (Expansion)                                    │
  └─────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────────────────┐
  │  DUALITÄT: OUTWARD + INWARD                                           │
  │                                                                        │
  │  V_out(k) + V_in(k) = V₀·(3 - 2·(¾)^k) + V₀·(-1 + 2·(¾)^k)         │
  │                      = V₀ · 2 = 2·V₀                                  │
  │                      = (2/3) · V_Würfel                                │
  │                                                                        │
  │  → Die SUMME ist KONSTANT für alle k!  ⭐⭐⭐                         │
  │  → Outward und Inward sind DUAL: was einer gewinnt, verliert der      │
  │    andere — perfekte Symmetrie um den Gleichgewichtspunkt V₀.          │
  │                                                                        │
  │  Gleichgewichtspunkt:                                                  │
  │    V_out = V_in  bei  3 - 2r = -1 + 2r  →  r = 1  →  k = 0           │
  │    → Nur beim START (k=0) sind beide Volumina gleich (= V₀)           │
  └─────────────────────────────────────────────────────────────────────────┘
""")

# ═══════════════════════════════════════════════════════════
#  WINKEL-ANALYSE MIT INWARD
# ═══════════════════════════════════════════════════════════

print(f"\n{'─' * 130}")
print(f"  WINKEL: INWARD vs OUTWARD — Gleichgewicht bei π/4")
print(f"{'─' * 130}")

# When you PLACE a tet on a face (outward), the angle from centroid to new peak
# is related to arctan(√2) = 54.74°
# When you PUSH a tet INTO a face (inward), it's arctan(1/√2) = 35.26°
# Their AVERAGE is exactly 45° = π/4

angle_out = np.arctan(SQRT2)       # 54.7356°
angle_in  = np.arctan(1/SQRT2)     # 35.2644°
angle_avg = (angle_out + angle_in) / 2

print(f"\n  OUTWARD angle: arctan(√2) = {np.degrees(angle_out):.4f}°")
print(f"  INWARD  angle: arctan(1/√2) = {np.degrees(angle_in):.4f}°")
print(f"  Mittelwert:     = {np.degrees(angle_avg):.4f}° = π/4 = 45°  "
      f"{'⭐⭐⭐ EXAKT!' if abs(angle_avg - PI/4) < 1e-14 else ''}")
print(f"\n  arctan(√2) + arctan(1/√2) = {np.degrees(angle_out + angle_in):.4f}° = π/2")
print(f"  → Sie sind KOMPLEMENTÄRWINKEL: inward + outward = 90°")

# Dihedral angle of regular tetrahedron
dihedral = np.arccos(1/3)
print(f"\n  Tetraeder Dihedral: arccos(1/3) = {np.degrees(dihedral):.4f}°")
print(f"  Dihedral / (π/4) = {dihedral / (PI/4):.6f}")
print(f"  Dihedral / arctan(√2) = {dihedral / angle_out:.6f}")

# ═══════════════════════════════════════════════════════════
#  ACS-VERGLEICH
# ═══════════════════════════════════════════════════════════

print(f"\n\n{'─' * 130}")
print(f"  ACS-DATEN vs KOCH-3D")
print(f"{'─' * 130}")

data_path = os.path.join(cfg.OUTPUT_DIR, "full_spectrum_data.npz")
if not os.path.exists(data_path):
    print("[ERROR] full_spectrum_data.npz not found")
    sys.exit(1)

fdata = np.load(data_path)
full_masses = fdata["masses"]
full_Z = fdata["Z"]

def hurst_rs(series, max_lag=None):
    n = len(series)
    if max_lag is None: max_lag = min(n // 4, 500)
    lags = list(range(10, max_lag, max(1, max_lag // 30)))
    log_lags, log_rs = [], []
    for lag in lags:
        rs_vals = []
        for start in range(0, n - lag, lag):
            chunk = series[start:start + lag]
            if len(chunk) < 2: continue
            mean_c = np.mean(chunk)
            cumdev = np.cumsum(chunk - mean_c)
            R = np.ptp(cumdev); S = np.std(chunk, ddof=1)
            if S > 0: rs_vals.append(R / S)
        if rs_vals:
            log_lags.append(np.log(lag))
            log_rs.append(np.log(np.mean(rs_vals)))
    if len(log_lags) < 3: return 0.5
    H, _ = np.polyfit(log_lags, log_rs, 1)
    return H

regions = {
    "Light (0.2-1.3)": (0.2, 1.3),
    "Charm (2.5-4.5)": (2.5, 4.5),
    "Bottom (8.5-12)": (8.5, 12.0),
    "EWK (50-130)":    (50, 130),
    "FULL (0.2-200)":  (0.2, 200),
}

D_koch_surf = D_surface(0)

print(f"\n  Koch-3D Oberfläche D = {D_koch_surf:.4f}")
print(f"\n  {'Region':>20s} {'H':>7s} {'D=2-H':>7s} {'Δ(Koch3D)':>10s} "
      f"{'out%':>6s} {'in%':>6s} {'k_eff':>7s} {'Match':>15s}")
print("  " + "─" * 90)

acs_data = {}
for rname, (mlo, mhi) in regions.items():
    mask = (full_masses >= mlo) & (full_masses <= mhi)
    z_r = full_Z[mask]
    if len(z_r) < 30: continue

    H  = hurst_rs(z_r)
    DH = 2 - H
    delta = abs(DH - D_koch_surf)

    n_pos = np.sum(z_r > 0)
    n_neg = np.sum(z_r < 0)
    pct_out = n_pos / len(z_r) * 100
    pct_in  = n_neg / len(z_r) * 100

    # Effective Koch iteration from sign-change pattern
    sign_ch = np.sum(np.diff(np.sign(z_r)) != 0)
    n_faces = max(sign_ch / 2, 1)
    k_eff = np.log(n_faces / 4) / np.log(6) if n_faces > 4 else 0

    match = "⭐⭐ KOCH-3D" if delta < 0.1 else "⭐ ~Koch-3D" if delta < 0.3 else "—"

    print(f"  {rname:>20s} {H:>7.4f} {DH:>7.4f} {delta:>10.4f} "
          f"{pct_out:>5.1f}% {pct_in:>5.1f}% {k_eff:>7.2f} {match:>15s}")

    acs_data[rname] = dict(H=H, DH=DH, pct_out=pct_out, pct_in=pct_in, k_eff=k_eff)

# ═══════════════════════════════════════════════════════════
#  INWARD KOCH — DETAILANALYSE
# ═══════════════════════════════════════════════════════════

print(f"\n\n{'─' * 130}")
print(f"  INWARD KOCH — DETAILANALYSE (negative Z-Bereiche)")
print(f"{'─' * 130}")

for rname, (mlo, mhi) in regions.items():
    mask = (full_masses >= mlo) & (full_masses <= mhi)
    z_r = full_Z[mask]
    m_r = full_masses[mask]
    if len(z_r) < 30: continue

    neg_mask = z_r < 0
    pos_mask = z_r > 0

    if np.sum(neg_mask) < 10 or np.sum(pos_mask) < 10:
        continue

    H_pos = hurst_rs(np.abs(z_r[pos_mask]))
    H_neg = hurst_rs(np.abs(z_r[neg_mask]))
    D_pos = 2 - H_pos
    D_neg = 2 - H_neg

    # Mean absolute Z for inward vs outward
    mean_z_out = np.mean(z_r[pos_mask])
    mean_z_in  = np.mean(np.abs(z_r[neg_mask]))

    # Volume-analogy: ratio of outward/inward "amplitudes"
    ratio = mean_z_out / mean_z_in if mean_z_in > 0 else float('inf')

    # At which k does V_out/V_in = ratio?
    # V_out/V_in = (3 - 2r) / (-1 + 2r) where r = (3/4)^k
    # ratio = (3 - 2r)/(-1 + 2r) → ratio(-1+2r) = 3-2r → -ratio + 2r·ratio = 3-2r
    # 2r(ratio+1) = 3+ratio → r = (3+ratio)/(2(ratio+1))
    r_solve = (3 + ratio) / (2 * (ratio + 1))
    if 0 < r_solve < 1:
        k_match = np.log(r_solve) / np.log(0.75)
    else:
        k_match = float('nan')

    print(f"\n  {rname}:")
    print(f"    OUTWARD (Z>0): D = {D_pos:.4f}, <Z> = {mean_z_out:.2f}σ")
    print(f"    INWARD  (Z<0): D = {D_neg:.4f}, <|Z|> = {mean_z_in:.2f}σ")
    print(f"    <Z_out>/<|Z_in|> = {ratio:.4f}")
    print(f"    Koch-k bei diesem Verhältnis: k ≈ {k_match:.4f}" if not np.isnan(k_match) else
          f"    Koch-k: außerhalb des gültigen Bereichs")

# ═══════════════════════════════════════════════════════════
#  VISUALIZATION
# ═══════════════════════════════════════════════════════════

print("\n[viz] Generiere vollständige Koch IN/OUT Analyse...")

plt.rcParams.update({
    "figure.facecolor": "#0a0a0f",
    "axes.facecolor":   "#0d0d15",
    "axes.edgecolor":   "#333355",
    "axes.labelcolor":  "#ccccee",
    "text.color":       "#ccccee",
    "xtick.color":      "#8888aa",
    "ytick.color":      "#8888aa",
    "font.family":      "monospace",
})

fig = plt.figure(figsize=(34, 48))
gs = GridSpec(6, 2, hspace=0.35, wspace=0.28, figure=fig)

fig.suptitle(
    "3D KOCH-SCHNEEFLOCKE: OUTWARD + INWARD\n"
    "Tetraeder → Würfel (out) · Tetraeder → Null (in) · π/4 Gleichgewicht\n"
    "Iteration k ∈ {−∞, −π, −e, −1, 0, 1, 2, e, k*, 3, π, 4, +∞}",
    fontsize=15, fontweight="bold", color="white", y=0.998)

# ── 1. V_out(k) and V_in(k) continuous ──
ax1 = fig.add_subplot(gs[0, 0])
k_cont = np.linspace(-3, 12, 500)
v_out_cont = V_out(k_cont) / V0
v_in_cont  = V_in(k_cont) / V0
v_sum_cont = v_out_cont + v_in_cont  # constant = 2

ax1.plot(k_cont, v_out_cont, color="#00ff88", linewidth=2.5, label="V_out(k) / V₀")
ax1.plot(k_cont, v_in_cont,  color="#ff6b6b", linewidth=2.5, label="V_in(k) / V₀")
ax1.plot(k_cont, v_sum_cont, color="#ffd93d", linewidth=1.5, linestyle="--",
         label="V_out + V_in = 2·V₀ (const)")
ax1.axhline(3, color="#00ff88", linewidth=0.8, linestyle=":", alpha=0.5)
ax1.axhline(-1, color="#ff6b6b", linewidth=0.8, linestyle=":", alpha=0.5)
ax1.axhline(0, color="white", linewidth=0.5, alpha=0.3)
ax1.axhline(1, color="white", linewidth=0.5, alpha=0.3)

# Mark special k values
sp_marks = [(0,"0"), (1,"1"), (2,"2"), (E,"e"), (k_zero_in,"k*"), (3,"3"), (PI,"π"), (4,"4")]
for kv, lbl in sp_marks:
    ax1.axvline(kv, color="#888888", linewidth=0.5, alpha=0.3)
    ax1.plot(kv, V_out(kv)/V0, "o", color="#00ff88", markersize=8, zorder=5)
    ax1.plot(kv, V_in(kv)/V0,  "s", color="#ff6b6b", markersize=8, zorder=5)
    # small label above
    y_top = max(V_out(kv)/V0, V_in(kv)/V0) + 0.15
    ax1.text(kv, y_top, lbl, ha="center", fontsize=8, color="white", fontweight="bold")

ax1.fill_between(k_cont, v_in_cont, 0, where=v_in_cont < 0,
                  alpha=0.15, color="#ff6b6b")
ax1.set_xlabel("Koch-Iteration k (reell)")
ax1.set_ylabel("Volumen / V₀")
ax1.set_title("Volumen: OUTWARD → Würfel, INWARD → Self-Intersection",
              fontsize=11, fontweight="bold")
ax1.legend(fontsize=8, loc="upper left")
ax1.set_xlim(-3, 10)
ax1.set_ylim(-2, 4)
ax1.grid(alpha=0.15)

# ── 2. Surface area A(k) and face count F(k) ──
ax2 = fig.add_subplot(gs[0, 1])
a_cont = A_surface(k_cont) / A0
f_cont = F(k_cont)

ax2b = ax2.twinx()
l1, = ax2.plot(k_cont, a_cont, color="#00ccff", linewidth=2.5, label="A(k)/A₀ = (3/2)^k")
l2, = ax2b.semilogy(k_cont[k_cont >= 0], F(k_cont[k_cont >= 0]),
                     color="#ff88ff", linewidth=2, linestyle="--", label="F(k) = 4·6^k")
for kv, lbl in sp_marks:
    ax2.plot(kv, A_surface(kv)/A0, "o", color="#00ccff", markersize=7, zorder=5)
ax2.set_xlabel("Koch-Iteration k")
ax2.set_ylabel("Oberfläche A(k)/A₀", color="#00ccff")
ax2b.set_ylabel("Flächenzahl F(k)", color="#ff88ff")
ax2.set_title("Oberfläche (divergent!) & Flächenzahl", fontsize=11, fontweight="bold")
ax2.set_xlim(-1, 8)
ax2.legend(handles=[l1, l2], fontsize=9, loc="upper left")
ax2.grid(alpha=0.15)

# ── 3. ACS Z-Profil: inward/outward Koch-Flächen ──
ax3 = fig.add_subplot(gs[1, :])
ax3.fill_between(full_masses, full_Z, 0, where=full_Z > 0,
                  alpha=0.5, color="#00ff88", label="OUTWARD (Z>0) → aufgesetzt")
ax3.fill_between(full_masses, full_Z, 0, where=full_Z < 0,
                  alpha=0.5, color="#ff6b6b", label="INWARD (Z<0) → eingedrückt")
ax3.set_xscale("log")
ax3.axhline(0, color="white", linewidth=0.5, alpha=0.3)
ax3.set_xlabel("M [GeV]")
ax3.set_ylabel("Z [σ]")
ax3.set_title("ACS als Koch-Schneeflocke: OUTWARD (grün) vs INWARD (rot)",
              fontsize=12, fontweight="bold")
ax3.legend(fontsize=10)
ax3.grid(alpha=0.15)

# ── 4. Winkeldiagramm: inward/outward → π/4 ──
ax4 = fig.add_subplot(gs[2, 0])
angles_info = [
    ("arctan(1/√2)\nINWARD", angle_in, "#ff6b6b"),
    ("π/4\nATTRAKTOR", PI/4, "#ffd93d"),
    ("arctan(√2)\nOUTWARD", angle_out, "#00ff88"),
    ("Dihedral\narccos(1/3)", dihedral, "#00ccff"),
]

bars = ax4.barh(range(len(angles_info)),
                [np.degrees(a[1]) for a in angles_info],
                color=[a[2] for a in angles_info], alpha=0.7, height=0.6)
for i, (lbl, ang, col) in enumerate(angles_info):
    ax4.text(np.degrees(ang) + 0.8, i, f"{np.degrees(ang):.2f}°",
             va="center", fontsize=10, color=col, fontweight="bold")

ax4.axvline(45, color="#ffd93d", linewidth=2, linestyle="--", alpha=0.6)
ax4.set_yticks(range(len(angles_info)))
ax4.set_yticklabels([a[0] for a in angles_info], fontsize=9)
ax4.set_xlabel("Winkel [°]")
ax4.set_title("π/4 = Mittelwert(INWARD, OUTWARD) ⭐", fontsize=11, fontweight="bold")
ax4.grid(alpha=0.15)

# ── 5. V_out/V_in ratio vs k ──
ax5 = fig.add_subplot(gs[2, 1])
k_ratio = np.linspace(0.01, 10, 400)
# V_out/V_in = (3 - 2r)/(-1 + 2r) where r = (3/4)^k
r_vals = (3/4)**k_ratio
v_ratio = (3 - 2*r_vals) / (-1 + 2*r_vals)
# Only plot where V_in > 0 (k < k*)
valid_region = k_ratio < k_zero_in
invalid_region = k_ratio >= k_zero_in

ax5.plot(k_ratio[valid_region], v_ratio[valid_region],
         color="#00ccff", linewidth=2.5, label="V_out/V_in (V_in > 0)")
ax5.plot(k_ratio[invalid_region], v_ratio[invalid_region],
         color="#ff6b6b", linewidth=1.5, linestyle=":", alpha=0.5,
         label="V_out/V_in (V_in < 0)")
ax5.axvline(k_zero_in, color="#ffd93d", linewidth=2, linestyle="--",
            label=f"k* = {k_zero_in:.4f} (V_in=0)")
ax5.axhline(1, color="white", linewidth=0.5, alpha=0.3)
ax5.axhline(0, color="white", linewidth=0.5, alpha=0.3)

for kv, lbl in sp_marks:
    if kv > 0:
        r_k = (3/4)**kv
        vi_k = -1 + 2*r_k
        if abs(vi_k) > 0.001:
            ratio_k = (3 - 2*r_k) / vi_k
            if -50 < ratio_k < 50:
                ax5.plot(kv, ratio_k, "o", color="white", markersize=6, zorder=5)
                ax5.annotate(lbl, (kv, ratio_k), textcoords="offset points",
                            xytext=(5, 8), fontsize=8, color="white")

ax5.set_xlabel("Koch-Iteration k")
ax5.set_ylabel("V_out / V_in")
ax5.set_title("Verhältnis OUTWARD/INWARD Volumen", fontsize=11, fontweight="bold")
ax5.set_ylim(-10, 30)
ax5.legend(fontsize=8)
ax5.grid(alpha=0.15)

# ── 6. Dualität: V_out + V_in = const ──
ax6 = fig.add_subplot(gs[3, 0])
ax6.fill_between(k_cont, 0, v_out_cont,
                  where=v_out_cont > 0, alpha=0.3, color="#00ff88")
ax6.fill_between(k_cont, 0, v_in_cont,
                  where=v_in_cont > 0, alpha=0.3, color="#ff6b6b")
ax6.fill_between(k_cont, 0, v_in_cont,
                  where=v_in_cont <= 0, alpha=0.15, color="#ff6b6b")

ax6.plot(k_cont, v_out_cont, color="#00ff88", linewidth=2, label="V_out/V₀")
ax6.plot(k_cont, v_in_cont,  color="#ff6b6b", linewidth=2, label="V_in/V₀")
ax6.axhline(2, color="#ffd93d", linewidth=2, linestyle="--",
            label="V_out + V_in = 2·V₀ = const")
ax6.axhline(1, color="white", linewidth=0.5, alpha=0.3)
ax6.axhline(0, color="white", linewidth=0.5, alpha=0.5)

# Shade the DUAL region (area between curves is always 2V₀)
ax6.fill_between(k_cont, v_in_cont, v_out_cont, alpha=0.08, color="#ffd93d")

ax6.set_xlabel("Koch-Iteration k")
ax6.set_ylabel("Volumen / V₀")
ax6.set_title("DUALITÄT: V_out(k) + V_in(k) = 2·V₀ ∀k ⭐⭐⭐",
              fontsize=11, fontweight="bold")
ax6.set_xlim(-2, 10)
ax6.set_ylim(-2, 4)
ax6.legend(fontsize=9)
ax6.grid(alpha=0.15)

# ── 7. ACS fractal dimensions ──
ax7 = fig.add_subplot(gs[3, 1])
rnames_p = [r for r in acs_data]
d_vals = [acs_data[r]["DH"] for r in rnames_p]
k_effs = [acs_data[r]["k_eff"] for r in rnames_p]
colors_p = ["#ff6b6b", "#00ff88", "#ffd93d", "#ff88ff", "#00ccff"][:len(rnames_p)]

x_pos = np.arange(len(rnames_p))
width = 0.35
ax7.bar(x_pos - width/2, d_vals, width, color=colors_p, alpha=0.7, label="D = 2 - H")
ax7b = ax7.twinx()
ax7b.bar(x_pos + width/2, k_effs, width, color=colors_p, alpha=0.3, label="k_eff")

ax7.axhline(D_koch_surf, color="#ff6b6b", linewidth=2, linestyle="--",
            label=f"Koch-3D: D = {D_koch_surf:.3f}")
ax7b.axhline(k_zero_in, color="#ffd93d", linewidth=1, linestyle=":",
             label=f"k* = {k_zero_in:.2f}")

ax7.set_xticks(x_pos)
ax7.set_xticklabels([r.split("(")[0].strip() for r in rnames_p], fontsize=8, rotation=15)
ax7.set_ylabel("Fraktale Dimension D")
ax7b.set_ylabel("Effektive Koch-Tiefe k_eff")
ax7.set_title("ACS Dimensionen & Koch-Iterationstiefe", fontsize=11, fontweight="bold")
ax7.legend(fontsize=8, loc="upper left")
ax7b.legend(fontsize=8, loc="upper right")
ax7.grid(alpha=0.15)

# ── 8. Koch Tetraeder 3D: outward/inward concept ──
ax8 = fig.add_subplot(gs[4, 0], projection="3d")
ax8.set_facecolor("#0d0d15")

c = cube_side
# Original tetrahedron
faces_tet = [
    [tet_vertices[0], tet_vertices[1], tet_vertices[2]],
    [tet_vertices[0], tet_vertices[1], tet_vertices[3]],
    [tet_vertices[0], tet_vertices[2], tet_vertices[3]],
    [tet_vertices[1], tet_vertices[2], tet_vertices[3]],
]
poly_out = Poly3DCollection(faces_tet, alpha=0.12, facecolor="#00ff88",
                            edgecolor="#00ff88", linewidth=0.5)
ax8.add_collection3d(poly_out)

# Draw one outward tet on top face (illustrative)
top_face = [tet_vertices[1], tet_vertices[2], tet_vertices[3]]
tf = np.array(top_face)
mid_face = np.mean(tf, axis=0)
# Midpoints of edges of the face
m01 = 0.5*(tf[0] + tf[1])
m12 = 0.5*(tf[1] + tf[2])
m02 = 0.5*(tf[0] + tf[2])
# Central sub-triangle
central_tri = [m01, m12, m02]
# Normal to the face (outward)
normal = np.cross(tf[1]-tf[0], tf[2]-tf[0])
normal = normal / np.linalg.norm(normal)
# Height of small tetrahedron with edge a/2
h_small = (a/2) * SQRT2/SQRT3
peak_out = np.mean(central_tri, axis=0) + normal * h_small

# Draw outward tet
for pt in central_tri:
    ax8.plot3D(*zip(pt, peak_out), color="#00ff88", linewidth=1.5, alpha=0.8)
for i in range(3):
    ax8.plot3D(*zip(central_tri[i], central_tri[(i+1)%3]),
               color="#00ff88", linewidth=1, alpha=0.6)

# Draw inward tet (push into face)
peak_in = np.mean(central_tri, axis=0) - normal * h_small
for pt in central_tri:
    ax8.plot3D(*zip(pt, peak_in), color="#ff6b6b", linewidth=1.5, alpha=0.8)
for i in range(3):
    ax8.plot3D(*zip(central_tri[i], central_tri[(i+1)%3]),
               color="#ff6b6b", linewidth=1, alpha=0.6)

# Labels
ax8.text(*peak_out, " OUT", fontsize=10, color="#00ff88", fontweight="bold")
ax8.text(*peak_in, " IN", fontsize=10, color="#ff6b6b", fontweight="bold")

centroid = np.mean(tet_vertices, axis=0)
ax8.scatter(*centroid, color="white", s=100, marker="*", zorder=15)
ax8.text(*centroid, "  π/4", fontsize=10, color="#ffd93d", fontweight="bold")

ax8.set_title("Koch: OUTWARD (grün) vs INWARD (rot)\nauf einer Fläche des Tetraeders",
              fontsize=10, fontweight="bold")
ax8.set_xlim(-0.1, c+0.1)
ax8.set_ylim(-0.1, c+0.1)
ax8.set_zlim(-0.15, c+0.15)

# ── 9. Summary text ──
ax9 = fig.add_subplot(gs[4, 1])
ax9.axis("off")

txt = "ZUSAMMENFASSUNG\n"
txt += "═" * 50 + "\n\n"
txt += "Wikipedia 3D Koch-Schneeflocke:\n"
txt += "  Start: Reguläres Tetraeder\n"
txt += "  Pro Iteration:\n"
txt += "    Jede Fläche → 4 Teil-△ (½ Kante)\n"
txt += "    Neues Tet auf mittleres △\n\n"
txt += f"  D_surface = log(6)/log(2) = {D_koch_surf:.4f}\n\n"
txt += "OUTWARD (aufgesetzt):\n"
txt += f"  V_out(k) = V₀·(3 - 2·(¾)^k)\n"
txt += f"  k→∞: V → V_Würfel = 3·V₀ ⭐\n\n"
txt += "INWARD (eingedrückt):\n"
txt += f"  V_in(k) = V₀·(-1 + 2·(¾)^k)\n"
txt += f"  k* = ln2/ln(4/3) = {k_zero_in:.4f}\n"
txt += f"  → V_in(k*) = 0 ⭐ (Self-Intersect)\n"
txt += f"  k→∞: V_in → -V₀ (anti-Tetraeder)\n\n"
txt += "DUALITÄT:\n"
txt += f"  V_out(k) + V_in(k) = 2·V₀ ∀k\n"
txt += f"  → Erhaltungssatz! ⭐⭐⭐\n\n"
txt += "π/4 GLEICHGEWICHT:\n"
txt += f"  arctan(√2)   = {np.degrees(angle_out):.2f}° (OUT)\n"
txt += f"  arctan(1/√2) = {np.degrees(angle_in):.2f}° (IN)\n"
txt += f"  Mittelwert   = 45.00° = π/4\n"
txt += f"  → EXAKT! ⭐⭐⭐\n"

ax9.text(0.03, 0.97, txt, transform=ax9.transAxes,
         fontsize=10.5, color="#ccccee", va="top",
         fontfamily="monospace",
         bbox=dict(boxstyle="round", facecolor="#1a1a2e", edgecolor="#555577"))

# ── 10. Spezialwerte-Tabelle ──
ax10 = fig.add_subplot(gs[5, :])
ax10.axis("off")

tbl  = "ITERATION BEI MATHEMATISCHEN KONSTANTEN\n"
tbl += "═" * 105 + "\n\n"
tbl += f"{'k':>8s} │ {'F(k)':>12s} │ {'A/A₀':>10s} │ {'V_out/V₀':>10s} │ {'V_out/V_W':>10s}"
tbl += f" │ {'V_in/V₀':>10s} │ {'V_in/V_W':>10s} │ {'Bemerkung':>22s}\n"
tbl += "─" * 105 + "\n"

for label, k in specials:
    if np.isinf(k):
        f_s = "→∞" if k > 0 else "→0"
        a_s = "→∞" if k > 0 else "→0"
        vo = "3.0" if k > 0 else "→-∞"
        vw = "1.0" if k > 0 else "→-∞"
        vi = "-1.0" if k > 0 else "→+∞"
        viw = "-1/3" if k > 0 else "→+∞"
    else:
        fv = F(k)
        f_s = f"{fv:.2f}" if fv < 1e6 else f"{fv:.1e}"
        a_s = f"{A_surface(k)/A0:.4f}"
        vo = f"{V_out(k)/V0:.6f}"
        vw = f"{V_out(k)/V_cube:.6f}"
        vi = f"{V_in(k)/V0:.6f}"
        viw = f"{V_in(k)/V_cube:.6f}"

    note = ""
    if label == "0": note = "Start"
    elif label == "1": note = "Sterntetraeder"
    elif label == "2": note = "56 Sub-Tets"
    elif label == "e": note = "Euler-Punkt"
    elif "k*" in label: note = "⭐ V_in = 0!"
    elif label == "3": note = "3. Iteration"
    elif label == "π": note = "π-Punkt"
    elif label == "4": note = "4. Iteration"
    elif label == "+∞": note = "OUT→Würfel"
    elif label == "-∞": note = "Rückwärts"

    tbl += f"{label:>8s} │ {f_s:>12s} │ {a_s:>10s} │ {vo:>10s} │ {vw:>10s}"
    tbl += f" │ {vi:>10s} │ {viw:>10s} │ {note:>22s}\n"

tbl += "\n" + "─" * 105 + "\n"
tbl += f"Schlüssel: V₀ = √2/12 = {V0:.6f},  V_Würfel = 3·V₀ = {V_cube:.6f}\n"
tbl += f"           k* = ln(2)/ln(4/3) = {k_zero_in:.6f}  (V_in verschwindet)\n"
tbl += f"           V_out + V_in = 2·V₀ = {2*V0:.6f}  (IMMER!)\n"

ax10.text(0.02, 0.97, tbl, transform=ax10.transAxes,
          fontsize=9.5, color="#ccccee", va="top",
          fontfamily="monospace",
          bbox=dict(boxstyle="round", facecolor="#1a1a2e", edgecolor="#555577"))

plt.savefig(os.path.join(cfg.OUTPUT_DIR, "acs_koch_correct.png"),
            dpi=200, bbox_inches="tight", facecolor="#0a0a0f")
plt.close()
print(f"[viz] Saved: output/acs_koch_correct.png")

print("\n" + "=" * 130)
print("  KORREKTE 3D KOCH-SCHNEEFLOCKE ANALYSE ABGESCHLOSSEN")
print("=" * 130)

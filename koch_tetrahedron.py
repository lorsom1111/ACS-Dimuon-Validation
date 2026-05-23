"""
ACS KOCH-TETRAHEDRON FRACTAL ANALYSIS (3D – 5D)
=================================================
Tests whether the ACS phase structure exhibits Koch fractal geometry
in 3–5 dimensional simplex space, both INWARD and OUTWARD.

Key insight: ACS Z-scores are SIGNED.
  Positive Z → outward convergence (Koch outward)
  Negative Z → anti-convergence (Koch inward)
  → The structure has both orientations — like a Koch tetrahedron!

Connections tested:
1. Koch fractal dimensions vs ACS Hurst exponents
2. Tetrahedral angles vs π/4 attractor
3. Simplex geometry in 3D,4D,5D — does π/4 emerge naturally?
4. Self-similarity scaling: Koch 1/3 rule in mass ratios
5. Box-counting fractal dimension of ACS Z-profiles
6. Koch iteration depth from mass hierarchy levels
"""

import os, sys, math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as cfg

PI = np.pi
PHI = (1 + np.sqrt(5)) / 2

# ═══════════════════════════════════════════════════════════
#  SIMPLEX GEOMETRY IN N DIMENSIONS
# ═══════════════════════════════════════════════════════════

def regular_simplex_vertices(n_dim):
    """Vertices of a regular n-simplex (n+1 vertices in n dimensions)."""
    # Standard construction via embedding
    vertices = np.zeros((n_dim + 1, n_dim))
    for i in range(n_dim):
        # Place vertex i
        vertices[i, i] = 1.0
        for j in range(i):
            vertices[i, j] = vertices[j, j] * (-1.0 / n_dim)
        # Normalize distance
        vertices[i] *= 1.0 / np.linalg.norm(vertices[i])
    # Last vertex
    vertices[n_dim] = -np.sum(vertices[:n_dim], axis=0) / n_dim
    vertices[n_dim] *= 1.0 / np.linalg.norm(vertices[n_dim])

    # Rescale so edge length = 1
    edge_len = np.linalg.norm(vertices[0] - vertices[1])
    vertices /= edge_len
    return vertices

def simplex_angles(n_dim):
    """Compute all characteristic angles of a regular n-simplex."""
    verts = regular_simplex_vertices(n_dim)
    n_verts = len(verts)
    center = np.mean(verts, axis=0)

    angles = {}

    # 1. Dihedral angle (angle between adjacent faces)
    # For regular simplex: arccos(1/n)
    dihedral = np.arccos(1.0 / n_dim)
    angles["dihedral"] = dihedral

    # 2. Edge-to-center angle
    # Angle subtended by an edge at the centroid
    v0 = verts[0] - center
    v1 = verts[1] - center
    cos_angle = np.dot(v0, v1) / (np.linalg.norm(v0) * np.linalg.norm(v1))
    angles["edge_center"] = np.arccos(np.clip(cos_angle, -1, 1))

    # 3. Vertex-center-face angle
    # Angle between centroid-vertex and centroid-face-center
    face_center = np.mean(verts[1:], axis=0)
    vc = verts[0] - center
    fc = face_center - center
    cos_vf = np.dot(vc, fc) / (np.linalg.norm(vc) * np.linalg.norm(fc) + 1e-15)
    angles["vertex_face"] = np.arccos(np.clip(cos_vf, -1, 1))

    # 4. Face-edge-face angle
    # Angle at an edge between two adjacent faces
    # For regular simplex this equals the dihedral angle
    angles["face_edge_face"] = dihedral

    # 5. All vertex-vertex-vertex angles
    vertex_angles = []
    for i in range(n_verts):
        for j in range(n_verts):
            for k in range(n_verts):
                if i != j and j != k and i != k:
                    v1 = verts[i] - verts[j]
                    v2 = verts[k] - verts[j]
                    cos_a = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-15)
                    vertex_angles.append(np.arccos(np.clip(cos_a, -1, 1)))
    angles["vertex_angle_mean"] = np.mean(vertex_angles)
    angles["vertex_angle_unique"] = list(set([round(a, 6) for a in vertex_angles]))

    # 6. arctan relationships
    # In a regular tetrahedron inscribed in a cube:
    # The face normal makes arctan(√2) with the edge
    angles["arctan_sqrt2"] = np.arctan(np.sqrt(2))
    angles["arctan_1_over_sqrt_n"] = np.arctan(1.0 / np.sqrt(n_dim))
    angles["arctan_sqrt_n"] = np.arctan(np.sqrt(n_dim))

    return angles

# ═══════════════════════════════════════════════════════════
#  KOCH FRACTAL ON N-SIMPLEX
# ═══════════════════════════════════════════════════════════

def koch_simplex_dimension(n_dim, variant="standard"):
    """
    Fractal dimension of Koch construction on n-simplex.

    Standard Koch (outward): Each (n-1)-face is divided into sub-faces,
    and a smaller simplex is raised on the center.

    For Koch snowflake (2D, n=2): D = ln(4)/ln(3) ≈ 1.2619
    For Koch tetrahedron (3D, n=3): depends on subdivision scheme
    """
    if variant == "standard":
        # Each face divided into n^(n-1) sub-faces at scale 1/n
        # New faces added: additional from raised simplex
        if n_dim == 2:
            # Koch curve: 4 pieces at scale 1/3
            N, s = 4, 3
        elif n_dim == 3:
            # Koch tetrahedron: each triangular face → 4 sub-triangles
            # Raise tetrahedron on central sub-triangle
            # 3 outer + 3 new exposed faces of raised tet = 6 pieces at scale 1/2
            N, s = 6, 2
        elif n_dim == 4:
            # 4-simplex (5-cell): each tetrahedral face → 8 sub-tetrahedra (scale 1/2)
            # Raise 4-simplex on central sub-tet
            # 7 outer + 4 new exposed faces = 11 pieces at scale 1/2
            N, s = 11, 2  # approximate
        elif n_dim == 5:
            # 5-simplex: each 4-face → 16 sub-cells
            # More complex, approximate
            N, s = 22, 2  # approximate
        else:
            N, s = 2**(n_dim), 2

        D = np.log(N) / np.log(s)
        return D, N, s

    elif variant == "inward":
        # Inward Koch: subtract instead of add
        # Same fractal dimension, different topology
        D, N, s = koch_simplex_dimension(n_dim, "standard")
        return D, N, s  # D is the same, but topology differs


print("=" * 100)
print("  ACS KOCH-TETRAHEDRON FRACTAL ANALYSIS (3D – 5D)")
print("=" * 100)

# ═══════════════════════════════════════════════════════════
#  PART 1: SIMPLEX ANGLES — WHERE IS π/4?
# ═══════════════════════════════════════════════════════════

print("\n\n" + "─" * 100)
print("  1. SIMPLEX GEOMETRY — SEARCHING FOR π/4")
print("─" * 100)
print(f"     ACS attractor: π/4 = {PI/4:.6f} rad = 45°")

all_simplex_angles = {}

for dim in range(2, 7):
    angles = simplex_angles(dim)
    all_simplex_angles[dim] = angles

    print(f"\n  ── {dim}D Simplex ({dim+1} vertices) ──")
    for aname, aval in sorted(angles.items()):
        if isinstance(aval, list):
            for v in aval:
                dist_to_pi4 = abs(v - PI/4)
                marker = " ⭐⭐⭐ MATCH!" if dist_to_pi4 < 0.01 else \
                         " ⭐⭐" if dist_to_pi4 < 0.05 else \
                         " ⭐" if dist_to_pi4 < 0.1 else ""
                print(f"    {aname:>25s}: {v:.6f} rad = {np.degrees(v):>8.3f}°  "
                      f"(Δ from π/4: {dist_to_pi4:.6f}){marker}")
        elif isinstance(aval, float):
            dist_to_pi4 = abs(aval - PI/4)
            marker = " ⭐⭐⭐ = π/4!" if dist_to_pi4 < 0.001 else \
                     " ⭐⭐ ≈ π/4!" if dist_to_pi4 < 0.05 else \
                     " ⭐" if dist_to_pi4 < 0.1 else ""
            print(f"    {aname:>25s}: {aval:.6f} rad = {np.degrees(aval):>8.3f}°  "
                  f"(Δ from π/4: {dist_to_pi4:.6f}){marker}")

# Special: cube-inscribed tetrahedron
print(f"\n  ── CUBE-INSCRIBED TETRAHEDRON ──")
print(f"    Body diagonal / face diagonal angle: arctan(1) = π/4 = {PI/4:.6f} ⭐⭐⭐")
print(f"    This IS the ACS attractor!")
print(f"    → A tetrahedron inscribed in a cube has π/4 as its")
print(f"       body-to-face diagonal angle. ACS 'sees' this geometry.")

# ═══════════════════════════════════════════════════════════
#  PART 2: KOCH FRACTAL DIMENSIONS (3D – 5D)
# ═══════════════════════════════════════════════════════════

print("\n\n" + "─" * 100)
print("  2. KOCH FRACTAL DIMENSIONS (3D – 5D, INWARD & OUTWARD)")
print("─" * 100)

print(f"\n  {'Dim':>4s} {'Variant':>10s} {'N pieces':>10s} {'Scale':>8s} "
      f"{'D_fractal':>10s} {'D - dim':>8s} {'Notes':>30s}")
print("  " + "-" * 85)

koch_dims = {}
for dim in range(2, 6):
    for variant in ["standard", "inward"]:
        D, N, s = koch_simplex_dimension(dim, variant)
        koch_dims[(dim, variant)] = D
        direction = "OUTWARD ↑" if variant == "standard" else "INWARD ↓"
        excess = D - (dim - 1)  # How much above the base dimension
        notes = ""
        if dim == 2:
            notes = "Koch snowflake curve"
        elif dim == 3 and variant == "standard":
            notes = "Koch tetrahedron (surface)"
        elif dim == 3 and variant == "inward":
            notes = "Anti-Koch tetrahedron (holes)"
        elif dim == 4:
            notes = "Koch 5-cell (4D simplex)"
        elif dim == 5:
            notes = "Koch 5-simplex (5D)"

        print(f"  {dim:>4d} {direction:>10s} {N:>10d} {f'1/{s}':>8s} "
              f"{D:>10.4f} {f'+{excess:.4f}':>8s} {notes:>30s}")

# ═══════════════════════════════════════════════════════════
#  PART 3: ACS DATA FRACTAL DIMENSION — COMPARE TO KOCH
# ═══════════════════════════════════════════════════════════

print("\n\n" + "─" * 100)
print("  3. ACS DATA vs KOCH FRACTAL DIMENSIONS")
print("─" * 100)

# Load full spectrum data
data_path = os.path.join(cfg.OUTPUT_DIR, "full_spectrum_data.npz")
if not os.path.exists(data_path):
    print("  [ERROR] full_spectrum_data.npz not found. Run full_spectrum.py first.")
    sys.exit(1)

fdata = np.load(data_path)
full_masses = fdata["masses"]
full_absZ = fdata["absZ"]
full_Z = fdata["Z"]

# Box-counting fractal dimension
def box_counting_dim(signal, n_scales=20):
    """Estimate fractal dimension via box-counting on a 1D signal."""
    signal = (signal - signal.min()) / (signal.max() - signal.min() + 1e-15)
    N = len(signal)

    scales = np.logspace(0, np.log10(N/4), n_scales).astype(int)
    scales = np.unique(np.clip(scales, 1, N))

    counts = []
    for s in scales:
        n_boxes_x = N // s
        if n_boxes_x < 1:
            continue
        n_boxes_y = int(1.0 / (s / N)) + 1
        total_boxes = 0
        for bx in range(n_boxes_x):
            chunk = signal[bx*s : (bx+1)*s]
            y_min = int(np.floor(chunk.min() * n_boxes_y))
            y_max = int(np.ceil(chunk.max() * n_boxes_y))
            total_boxes += max(1, y_max - y_min)
        counts.append((s / N, total_boxes))

    if len(counts) < 3:
        return 1.0

    eps = np.array([c[0] for c in counts])
    Ns = np.array([c[1] for c in counts])
    valid = (eps > 0) & (Ns > 0)
    if np.sum(valid) < 3:
        return 1.0

    slope, _ = np.polyfit(np.log(eps[valid]), np.log(Ns[valid]), 1)
    return -slope

# Hurst exponent
def hurst_rs(series, max_lag=None):
    """Rescaled range Hurst exponent."""
    n = len(series)
    if max_lag is None:
        max_lag = min(n // 4, 500)
    lags = list(range(10, max_lag, max(1, max_lag // 30)))

    log_lags = []
    log_rs = []
    for lag in lags:
        rs_vals = []
        for start in range(0, n - lag, lag):
            chunk = series[start:start + lag]
            if len(chunk) < 2:
                continue
            mean_c = np.mean(chunk)
            cumdev = np.cumsum(chunk - mean_c)
            R = np.ptp(cumdev)  # max - min
            S = np.std(chunk, ddof=1)
            if S > 0:
                rs_vals.append(R / S)
        if rs_vals:
            log_lags.append(np.log(lag))
            log_rs.append(np.log(np.mean(rs_vals)))

    if len(log_lags) < 3:
        return 0.5
    H, _ = np.polyfit(log_lags, log_rs, 1)
    return H

# Analyze each mass region
regions = {
    "Light (0.2-1.3)":  (0.2,  1.3),
    "Charm (2.5-4.5)":  (2.5,  4.5),
    "Bottom (8.5-12)":  (8.5, 12.0),
    "EWK (50-130)":     (50,  130),
    "FULL (0.2-200)":   (0.2, 200),
}

print(f"\n  {'Region':>20s} {'D_box':>8s} {'H (Hurst)':>10s} {'D_H=2-H':>8s} "
      f"{'Koch match':>30s}")
print("  " + "-" * 85)

acs_fractals = {}
for rname, (mlo, mhi) in regions.items():
    mask = (full_masses >= mlo) & (full_masses <= mhi)
    z_region = full_Z[mask]

    if len(z_region) < 30:
        continue

    D_box = box_counting_dim(z_region)
    H = hurst_rs(z_region)
    D_H = 2 - H  # Fractal dimension from Hurst

    acs_fractals[rname] = {"D_box": D_box, "H": H, "D_H": D_H}

    # Compare to Koch dimensions
    best_match = ""
    best_dist = 999
    for (dim, variant), D_koch in koch_dims.items():
        dist = abs(D_H - D_koch)
        if dist < best_dist:
            best_dist = dist
            dir_label = "OUT" if variant == "standard" else "IN"
            best_match = f"Koch-{dim}D-{dir_label} (D={D_koch:.4f}, Δ={dist:.4f})"

    print(f"  {rname:>20s} {D_box:>8.4f} {H:>10.4f} {D_H:>8.4f} {best_match:>30s}")

# ═══════════════════════════════════════════════════════════
#  PART 4: INWARD vs OUTWARD — SIGNED Z STRUCTURE
# ═══════════════════════════════════════════════════════════

print("\n\n" + "─" * 100)
print("  4. KOCH INWARD (Z<0) vs OUTWARD (Z>0)")
print("─" * 100)

for rname, (mlo, mhi) in regions.items():
    mask = (full_masses >= mlo) & (full_masses <= mhi)
    z_region = full_Z[mask]
    m_region = full_masses[mask]

    if len(z_region) < 30:
        continue

    pos_mask = z_region > 0
    neg_mask = z_region < 0
    n_pos = np.sum(pos_mask)
    n_neg = np.sum(neg_mask)
    n_total = len(z_region)
    ratio_pos = n_pos / n_total * 100

    # Fractal dimension of positive and negative parts separately
    if np.sum(pos_mask) > 20:
        H_pos = hurst_rs(np.abs(z_region[pos_mask]))
        D_pos = 2 - H_pos
    else:
        D_pos = 0

    if np.sum(neg_mask) > 20:
        H_neg = hurst_rs(np.abs(z_region[neg_mask]))
        D_neg = 2 - H_neg
    else:
        D_neg = 0

    # Sign-change frequency (Koch iteration proxy)
    sign_changes = np.sum(np.diff(np.sign(z_region)) != 0)
    sign_change_freq = sign_changes / len(z_region)

    print(f"\n  {rname}:")
    print(f"    Outward (Z>0): {n_pos:>5d} ({ratio_pos:.1f}%)  D_fractal = {D_pos:.4f}")
    print(f"    Inward  (Z<0): {n_neg:>5d} ({100-ratio_pos:.1f}%)  D_fractal = {D_neg:.4f}")
    print(f"    Sign changes: {sign_changes} ({sign_change_freq:.4f} per point)")
    print(f"    D_out/D_in ratio: {D_pos/D_neg:.4f}" if D_neg > 0 else "    D_out/D_in: N/A")

    # Koch iteration depth estimate
    # Koch at iteration k has 4^k segments (2D) or 6^k faces (3D)
    # If sign_changes ~ N * (1/3)^k, then k ≈ log(sign_changes/N) / log(1/3)
    if sign_change_freq > 0:
        # Estimate Koch iteration from sign-change pattern
        k_est = -np.log(sign_change_freq) / np.log(3)
        print(f"    Koch iteration estimate: k ≈ {k_est:.2f}")

# ═══════════════════════════════════════════════════════════
#  PART 5: 1/3 SCALING LAW (KOCH SIGNATURE)
# ═══════════════════════════════════════════════════════════

print("\n\n" + "─" * 100)
print("  5. KOCH 1/3 SCALING LAW IN MASS HIERARCHY")
print("─" * 100)

# The Koch curve uses scale factor 1/3.
# Check if mass ratios between ACS families follow powers of 3.

DETECTED = {
    "η(548)": 0.5479, "ρ(770)": 0.7753, "ω(782)": 0.7827,
    "η'(958)": 0.9578, "f₀(980)": 0.9900, "φ(1020)": 1.0195,
    "J/ψ": 3.0969, "ψ(2S)": 3.6861, "ψ(3770)": 3.7737,
    "Υ(1S)": 9.4603, "Υ(2S)": 10.0233, "Υ(3S)": 10.3552,
    "Z": 91.1876,
}

masses_key = np.array(list(DETECTED.values()))
names_key = list(DETECTED.keys())

print(f"\n  Testing mass ratios for powers of 3:")
print(f"  {'Pair':>30s} {'Ratio':>10s} {'log₃(ratio)':>12s} {'Nearest int':>12s} {'Error':>8s}")
print("  " + "-" * 80)

for i in range(len(masses_key)):
    for j in range(i+1, len(masses_key)):
        r = masses_key[j] / masses_key[i] if masses_key[j] > masses_key[i] \
            else masses_key[i] / masses_key[j]
        log3 = np.log(r) / np.log(3)
        nearest_int = round(log3)
        if nearest_int == 0:
            continue
        err = abs(log3 - nearest_int) / abs(nearest_int) * 100
        if err < 15:  # Within 15%
            n1 = names_key[j] if masses_key[j] > masses_key[i] else names_key[i]
            n2 = names_key[i] if masses_key[j] > masses_key[i] else names_key[j]
            marker = "⭐⭐" if err < 5 else "⭐" if err < 10 else ""
            print(f"  {n1:>14s}/{n2:<14s} {r:>10.4f} {log3:>12.4f} "
                  f"{nearest_int:>12d} {err:>7.2f}% {marker}")

# Also check 1/3 scaling between family MEANS
family_centers = {
    "Light mesons": np.mean([0.5479, 0.7753, 0.7827, 0.9578, 0.9900, 1.0195]),
    "Charmonium": np.mean([3.0969, 3.6861, 3.7737]),
    "Bottomonium": np.mean([9.4603, 10.0233, 10.3552]),
    "Z": 91.1876,
}

print(f"\n  Family center mass ratios:")
fc_names = list(family_centers.keys())
fc_vals = list(family_centers.values())
for i in range(len(fc_names)):
    for j in range(i+1, len(fc_names)):
        r = fc_vals[j] / fc_vals[i]
        log3 = np.log(r) / np.log(3)
        print(f"    {fc_names[j]:>15s} / {fc_names[i]:<15s} = {r:.4f}  "
              f"(log₃ = {log3:.4f}, 3^{log3:.2f})")

# ═══════════════════════════════════════════════════════════
#  PART 6: TETRAHEDRAL PHASE SPACE PROJECTION
# ═══════════════════════════════════════════════════════════

print("\n\n" + "─" * 100)
print("  6. ACS AS TETRAHEDRAL PHASE PROJECTION")
print("─" * 100)

# Key insight: arctan(M/M₀) = π/4 means M = M₀
# This is the DIAGONAL of a 2D square (or the body diagonal of higher-dim cube)
# A regular tetrahedron inscribed in a cube has its edges along face diagonals

# The connection: if we embed 4 particle families as vertices of a tetrahedron
# in phase space, the ACS attractor π/4 corresponds to the cube diagonal
# that passes through the tetrahedron's centroid.

print(f"\n  Tetrahedron inscribed in unit cube:")
print(f"  Vertices: (0,0,0), (1,1,0), (1,0,1), (0,1,1)")
print(f"  Face diagonal angle: arctan(1) = π/4 = {PI/4:.6f}")
print(f"  Body diagonal angle: arctan(√2) = {np.arctan(np.sqrt(2)):.6f}")
print(f"  Edge length: √2 = {np.sqrt(2):.6f}")

# The 4 families map to tetrahedron vertices:
tet_verts = np.array([
    [0, 0, 0],   # Light mesons
    [1, 1, 0],   # Charmonium
    [1, 0, 1],   # Bottomonium
    [0, 1, 1],   # Z/Electroweak
])

# Centroid
centroid = np.mean(tet_verts, axis=0)
print(f"\n  Centroid: {centroid}")
print(f"  Centroid = ({centroid[0]:.1f}, {centroid[1]:.1f}, {centroid[2]:.1f}) = (1/2, 1/2, 1/2)")
print(f"  → The centroid is the CENTER of the cube!")
print(f"  → arctan(centroid_y/centroid_x) = arctan(1) = π/4 ⭐⭐⭐")

# Map masses to tetrahedral coordinates
# Use log-mass as the scale coordinate
log_masses_fam = np.log([0.84, 3.52, 9.95, 91.19])  # family centers
log_range = log_masses_fam[-1] - log_masses_fam[0]
# Normalize to [0,1]
t = (log_masses_fam - log_masses_fam[0]) / log_range

print(f"\n  Normalized family positions (log-mass):")
fam_names = ["Light", "Charm", "Bottom", "Z"]
for fn, tv in zip(fam_names, t):
    print(f"    {fn:>10s}: t = {tv:.4f}")

# Check: are these positions related to 1/3?
print(f"\n  Spacing in normalized log-mass:")
for i in range(len(t) - 1):
    spacing = t[i+1] - t[i]
    ratio_to_third = spacing / (1/3) if spacing > 0 else 0
    print(f"    {fam_names[i]:>10s} → {fam_names[i+1]:<10s}: "
          f"Δt = {spacing:.4f} ({ratio_to_third:.3f} × 1/3)")

# ═══════════════════════════════════════════════════════════
#  VISUALIZATION
# ═══════════════════════════════════════════════════════════

print("\n[viz] Generating Koch-tetrahedron analysis plots...")

plt.rcParams.update({
    "figure.facecolor": "#0a0a0f",
    "axes.facecolor": "#0d0d15",
    "axes.edgecolor": "#333355",
    "axes.labelcolor": "#ccccee",
    "text.color": "#ccccee",
    "xtick.color": "#8888aa",
    "ytick.color": "#8888aa",
    "font.family": "monospace",
})

fig = plt.figure(figsize=(26, 30))
gs = GridSpec(4, 2, hspace=0.35, wspace=0.3, figure=fig)

fig.suptitle("ACS KOCH-TETRAHEDRON FRACTAL ANALYSIS\n"
             "Simplex Geometry · Koch Dimensions · Inward/Outward · 3D–5D",
             fontsize=16, fontweight="bold", color="white", y=0.995)

# ── Panel 1: 3D Koch Tetrahedron (conceptual) ──
ax1 = fig.add_subplot(gs[0, 0], projection="3d")
ax1.set_facecolor("#0d0d15")
# Draw tetrahedron inscribed in cube
cube_verts = tet_verts
faces = [
    [cube_verts[0], cube_verts[1], cube_verts[2]],
    [cube_verts[0], cube_verts[1], cube_verts[3]],
    [cube_verts[0], cube_verts[2], cube_verts[3]],
    [cube_verts[1], cube_verts[2], cube_verts[3]],
]
poly = Poly3DCollection(faces, alpha=0.15, facecolor="#00ccff", edgecolor="#00ccff")
ax1.add_collection3d(poly)
# Mark vertices with family names
for v, fn, c in zip(cube_verts, fam_names, ["#ff6b6b", "#00ff88", "#ffd93d", "#ff88ff"]):
    ax1.scatter(*v, color=c, s=100, zorder=10)
    ax1.text(v[0], v[1], v[2]+0.08, fn, fontsize=9, color=c, ha="center")
# Centroid
ax1.scatter(*centroid, color="white", s=150, marker="*", zorder=15)
ax1.text(centroid[0], centroid[1], centroid[2]+0.08, "π/4",
         fontsize=12, color="white", ha="center", fontweight="bold")
# Draw cube wireframe
for start, end in [(0,0), (0,1), (1,0), (1,1)]:
    for dim in range(3):
        p1 = [start if d != dim else 0 for d in range(3)]
        p2 = [end if d != dim else 1 for d in range(3)]
        # This is getting complex, skip full wireframe
ax1.set_title("Tetrahedron in Cube\nπ/4 = Centroid Angle", fontsize=11, fontweight="bold")
ax1.set_xlim(0, 1)
ax1.set_ylim(0, 1)
ax1.set_zlim(0, 1)

# ── Panel 2: Fractal dimensions comparison ──
ax2 = fig.add_subplot(gs[0, 1])
# Koch dimensions
dims_out = [koch_dims[(d, "standard")] for d in range(2, 6)]
dims_in = [koch_dims[(d, "inward")] for d in range(2, 6)]
x_dims = [2, 3, 4, 5]

ax2.plot(x_dims, dims_out, "o-", color="#00ff88", linewidth=2, markersize=10, label="Koch OUTWARD")
ax2.plot(x_dims, dims_in, "s--", color="#ff6b6b", linewidth=2, markersize=10, label="Koch INWARD")

# ACS measured dimensions
acs_d_vals = [v["D_H"] for v in acs_fractals.values() if v["D_H"] > 0]
if acs_d_vals:
    ax2.axhspan(min(acs_d_vals), max(acs_d_vals), alpha=0.15, color="#ffd93d",
                label=f"ACS measured range")
    ax2.axhline(np.mean(acs_d_vals), color="#ffd93d", linewidth=2, linestyle=":",
                label=f"ACS mean D={np.mean(acs_d_vals):.3f}")

ax2.set_xlabel("Spatial Dimension")
ax2.set_ylabel("Fractal Dimension D")
ax2.set_title("Koch Simplex Dimensions vs ACS Data", fontsize=12, fontweight="bold")
ax2.legend(fontsize=9)
ax2.grid(alpha=0.15)

# ── Panel 3: Signed Z-score with Koch coloring ──
ax3 = fig.add_subplot(gs[1, :])
for rname, (mlo, mhi) in [("Light", (0.2, 1.3)), ("Charm", (2.5, 4.5)),
                            ("Bottom", (8.5, 12.0))]:
    mask = (full_masses >= mlo) & (full_masses <= mhi)
    m_r = full_masses[mask]
    z_r = full_Z[mask]
    # Normalize x to [0, 1]
    x_norm = (m_r - m_r[0]) / (m_r[-1] - m_r[0])

    ax3.fill_between(x_norm + {"Light": 0, "Charm": 1.2, "Bottom": 2.4}[rname],
                      z_r / np.max(np.abs(z_r)), 0,
                      where=z_r > 0, alpha=0.4, color="#00ff88")
    ax3.fill_between(x_norm + {"Light": 0, "Charm": 1.2, "Bottom": 2.4}[rname],
                      z_r / np.max(np.abs(z_r)), 0,
                      where=z_r < 0, alpha=0.4, color="#ff6b6b")
    offset = {"Light": 0, "Charm": 1.2, "Bottom": 2.4}[rname]
    ax3.text(offset + 0.5, 1.1, rname, fontsize=11, color="white",
             ha="center", fontweight="bold")

ax3.set_title("Koch Structure: OUTWARD (green, Z>0) vs INWARD (red, Z<0)\n"
              "Three mass regions normalized and stacked",
              fontsize=12, fontweight="bold")
ax3.set_xlabel("Normalized mass position within region")
ax3.set_ylabel("Normalized Z")
ax3.axhline(0, color="white", linewidth=0.5, alpha=0.3)
ax3.grid(alpha=0.15)

# ── Panel 4: Log₃ mass ratio distribution ──
ax4 = fig.add_subplot(gs[2, 0])
all_masses = np.array(list(DETECTED.values()))
all_ratios = []
for i in range(len(all_masses)):
    for j in range(i+1, len(all_masses)):
        r = max(all_masses[i], all_masses[j]) / min(all_masses[i], all_masses[j])
        all_ratios.append(r)
all_ratios = np.array(all_ratios)
log3_ratios = np.log(all_ratios) / np.log(3)

ax4.hist(log3_ratios, bins=60, color="#00ccff", alpha=0.6)
for k in range(1, 6):
    ax4.axvline(k, color="#ffd93d", linewidth=2, alpha=0.5, linestyle="--")
    ax4.text(k, ax4.get_ylim()[1] * 0.9 if ax4.get_ylim()[1] > 0 else 5,
             f" 3^{k}", fontsize=10, color="#ffd93d")
ax4.set_title("Mass Ratios in Powers of 3 (Koch Scale Factor)",
              fontsize=12, fontweight="bold")
ax4.set_xlabel("log₃(m_i / m_j)")
ax4.set_ylabel("Count")
ax4.grid(alpha=0.15)

# ── Panel 5: Simplex angle table ──
ax5 = fig.add_subplot(gs[2, 1])
ax5.axis("off")
table_text = "SIMPLEX ANGLES vs π/4\n"
table_text += "=" * 50 + "\n\n"
table_text += f"{'Dim':>4s} {'Dihedral':>10s} {'arctan(1/√n)':>14s} {'Δ from π/4':>12s}\n"
table_text += "-" * 42 + "\n"

for dim in range(2, 7):
    dihedral = np.arccos(1.0 / dim)
    atan_inv = np.arctan(1.0 / np.sqrt(dim))
    delta = abs(atan_inv - PI/4)
    marker = " ⭐" if delta < 0.1 else ""
    table_text += f"{dim:>4d} {np.degrees(dihedral):>9.2f}° {np.degrees(atan_inv):>13.2f}° {delta:>12.6f}{marker}\n"

table_text += "\n" + "-" * 42 + "\n"
table_text += f"\nπ/4 = 45.000° = {PI/4:.6f} rad\n"
table_text += f"\narctan(1/√2) = 35.264° (3D tetrahedron)\n"
table_text += f"arctan(1/√1) = 45.000° = π/4 ← 2D! ⭐⭐⭐\n"
table_text += f"\n→ π/4 is the 2-simplex (triangle)\n"
table_text += f"   inscribed in the 2-cube (square)\n"
table_text += f"   diagonal angle.\n"
table_text += f"\n→ ACS projects N-dim resonance\n"
table_text += f"   structure onto 2D phase plane\n"
table_text += f"   where π/4 is the diagonal.\n"

ax5.text(0.05, 0.95, table_text, transform=ax5.transAxes,
         fontsize=11, color="#ccccee", verticalalignment="top",
         fontfamily="monospace",
         bbox=dict(boxstyle="round", facecolor="#1a1a2e", edgecolor="#555577"))

# ── Panel 6: Power spectrum (1/f^α) ──
ax6 = fig.add_subplot(gs[3, 0])
for rname, (mlo, mhi), color in [("Light", (0.2, 1.3), "#00ccff"),
                                   ("Charm", (2.5, 4.5), "#ff6b6b"),
                                   ("Bottom", (8.5, 12.0), "#00ff88")]:
    mask = (full_masses >= mlo) & (full_masses <= mhi)
    z_region = full_Z[mask]
    if len(z_region) > 50:
        fft = np.fft.rfft(z_region - np.mean(z_region))
        power = np.abs(fft) ** 2
        freqs = np.fft.rfftfreq(len(z_region))
        valid = (freqs > 0) & (power > 0)
        if np.sum(valid) > 5:
            ax6.loglog(freqs[valid], power[valid], color=color, alpha=0.6,
                      linewidth=1, label=rname)
            slope, _ = np.polyfit(np.log10(freqs[valid][1:]),
                                 np.log10(power[valid][1:]), 1)
            ax6.text(0.95, 0.9 - list(regions.keys()).index(rname + f" ({mlo}-{mhi})")
                     * 0.1 if rname in ["Light"] else 0.8,
                     f"α={-slope:.2f}", transform=ax6.transAxes,
                     fontsize=9, color=color, ha="right")

ax6.set_title("Power Spectra — Fractal Noise Signature", fontsize=12, fontweight="bold")
ax6.set_xlabel("Frequency")
ax6.set_ylabel("Power")
ax6.legend(fontsize=9)
ax6.grid(alpha=0.15)

# ── Panel 7: Hurst exponents ──
ax7 = fig.add_subplot(gs[3, 1])
ax7.axis("off")
summary = "FRACTAL SUMMARY\n"
summary += "=" * 55 + "\n\n"
summary += f"{'Region':>18s} {'H':>6s} {'D=2-H':>7s} {'Type':>20s}\n"
summary += "-" * 55 + "\n"

for rname, vals in acs_fractals.items():
    H = vals["H"]
    D = vals["D_H"]
    if H > 0.7:
        ftype = "STRONGLY PERSISTENT"
    elif H > 0.55:
        ftype = "PERSISTENT (fractal)"
    elif H > 0.45:
        ftype = "RANDOM"
    else:
        ftype = "ANTI-PERSISTENT"
    summary += f"{rname:>18s} {H:>6.3f} {D:>7.3f} {ftype:>20s}\n"

summary += "\n" + "-" * 55 + "\n"
summary += "\nKoch fractal reference:\n"
for dim in range(2, 6):
    D = koch_dims[(dim, "standard")]
    summary += f"  Koch-{dim}D: D = {D:.4f}\n"

summary += f"\n→ If ACS D matches Koch-3D ({koch_dims[(3,'standard')]:.4f}),\n"
summary += f"  the attractor has tetrahedral fractal geometry.\n"

ax7.text(0.05, 0.95, summary, transform=ax7.transAxes,
         fontsize=11, color="#ccccee", verticalalignment="top",
         fontfamily="monospace",
         bbox=dict(boxstyle="round", facecolor="#1a1a2e", edgecolor="#555577"))

plt.savefig(os.path.join(cfg.OUTPUT_DIR, "acs_koch_tetrahedron.png"),
            dpi=200, bbox_inches="tight", facecolor="#0a0a0f")
plt.close()
print(f"[viz] Saved: output/acs_koch_tetrahedron.png")

print("\n" + "=" * 100)
print("  KOCH-TETRAHEDRON ANALYSIS COMPLETE")
print("=" * 100)

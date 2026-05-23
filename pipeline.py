"""
ACS Pipeline — Core Kinematics & Phase Mapping
================================================
Latest approved version + minimal-invasive GPU upgrade.

Preserved functions:
  - calculate_kinematics(data)  → invariant mass
  - map_acs_phase(masses, target_mass) → ACS phase θ

Added (surgical):
  - GPU dispatch via CuPy when available
  - apply_quality_cuts(pt1, pt2, eta1, eta2, q1, q2)
  - select_mass_window(masses, low, high)
"""

import numpy as np
import config as cfg

# ─────────────────────────────────────────────
# GPU / CPU dispatch
# ─────────────────────────────────────────────
_GPU_AVAILABLE = False
try:
    if cfg.USE_GPU:
        import cupy as cp
        cp.cuda.Device(cfg.GPU_DEVICE).use()
        _GPU_AVAILABLE = True
except Exception:
    pass


def xp():
    """Return the active array library (cupy or numpy)."""
    return cp if _GPU_AVAILABLE else np


def to_gpu(arr):
    """Move numpy array to GPU if available."""
    if _GPU_AVAILABLE and not isinstance(arr, cp.ndarray):
        return cp.asarray(arr)
    return arr


def to_cpu(arr):
    """Ensure array is on CPU (numpy)."""
    if _GPU_AVAILABLE and isinstance(arr, cp.ndarray):
        return cp.asnumpy(arr)
    return np.asarray(arr)


# ─────────────────────────────────────────────
# APPROVED: Invariant Mass Calculation
# ─────────────────────────────────────────────
def calculate_kinematics(pt1, pt2, eta1, eta2, phi1, phi2):
    """
    Relativistic invariant mass for a dimuon pair.

    M = sqrt(2·pT1·pT2·(cosh(Δη) − cos(Δφ)))

    All inputs are array-like (numpy or cupy).
    Returns: masses (same backend as input).
    """
    lib = xp()
    pt1, pt2 = to_gpu(pt1), to_gpu(pt2)
    eta1, eta2 = to_gpu(eta1), to_gpu(eta2)
    phi1, phi2 = to_gpu(phi1), to_gpu(phi2)

    deta = eta1 - eta2
    dphi = phi1 - phi2

    M = lib.sqrt(
        2.0 * pt1 * pt2 * (lib.cosh(deta) - lib.cos(dphi))
    )
    return M


# ─────────────────────────────────────────────
# APPROVED: ACS Phase Mapping
# ─────────────────────────────────────────────
def map_acs_phase(masses, target_mass):
    """
    Map invariant masses onto the ACS phase space.

    θ = arctan(M / M_target)

    Theoretical attractor: π/4 when M → M_target.
    """
    lib = xp()
    masses = to_gpu(masses)
    return lib.arctan(masses / target_mass)


# ─────────────────────────────────────────────
# ADDED: Quality Cuts  (minimal-invasive)
# ─────────────────────────────────────────────
def apply_quality_cuts(pt1, pt2, eta1, eta2, q1, q2):
    """
    Return a boolean mask for events passing standard dimuon cuts.

    Cuts:
      - Both muons pT > MIN_PT
      - Both muons |η| < MAX_ETA
      - Opposite charge (if configured)
    """
    lib = xp()
    pt1, pt2 = to_gpu(pt1), to_gpu(pt2)
    eta1, eta2 = to_gpu(eta1), to_gpu(eta2)
    q1, q2 = to_gpu(q1), to_gpu(q2)

    mask = (pt1 > cfg.MIN_PT) & (pt2 > cfg.MIN_PT)
    mask &= (lib.abs(eta1) < cfg.MAX_ETA) & (lib.abs(eta2) < cfg.MAX_ETA)

    if cfg.OPPOSITE_CHARGE:
        mask &= (q1 * q2 < 0)

    return mask


# ─────────────────────────────────────────────
# ADDED: Mass Window Selection  (minimal-invasive)
# ─────────────────────────────────────────────
def select_mass_window(masses, low=None, high=None):
    """Return boolean mask for masses within [low, high] GeV."""
    if low is None:
        low = cfg.MASS_WINDOW[0]
    if high is None:
        high = cfg.MASS_WINDOW[1]

    lib = xp()
    masses = to_gpu(masses)
    return (masses >= low) & (masses <= high)

"""
ACS Statistics — Signal / Background / Significance
=====================================================
Estimates signal (S), background (B), and local significance (Z = S/√B)
in the ACS phase space around the π/4 attractor.

Method: Sideband interpolation.
  - Signal region:   [π/4 − δ, π/4 + δ]
  - Left sideband:   [π/4 − δ − w, π/4 − δ]
  - Right sideband:  [π/4 + δ, π/4 + δ + w]
  - B_estimate = (left + right) / 2 × (signal_width / sideband_width)
  - S_estimate = N_signal − B_estimate
  - Z = S / √B
"""

import numpy as np
import config as cfg
from pipeline import to_cpu


def compute_phase_statistics(phases, attractor=None,
                              signal_half=None, sideband_width=None):
    """
    Compute signal, background, and significance around the ACS attractor.

    Args:
        phases: array of ACS phase values (θ) — can be GPU or CPU
        attractor: phase attractor (default: π/4)
        signal_half: half-width of signal window (radians)
        sideband_width: width of each sideband (radians)

    Returns:
        dict with keys:
          N_total, N_signal, N_left_sb, N_right_sb,
          B_estimate, S_estimate, significance_Z,
          signal_window, left_sideband, right_sideband,
          mean_phase, std_phase, median_phase
    """
    if attractor is None:
        attractor = cfg.ACS_ATTRACTOR
    if signal_half is None:
        signal_half = cfg.PHASE_SIGNAL_HALFWIDTH
    if sideband_width is None:
        sideband_width = cfg.PHASE_SIDEBAND_WIDTH

    # Ensure CPU for counting
    phases = np.asarray(to_cpu(phases))

    # Define regions
    sig_lo = attractor - signal_half
    sig_hi = attractor + signal_half
    sb_left_lo  = sig_lo - sideband_width
    sb_left_hi  = sig_lo
    sb_right_lo = sig_hi
    sb_right_hi = sig_hi + sideband_width

    # Count events in each region
    N_total    = len(phases)
    N_signal   = np.sum((phases >= sig_lo) & (phases <= sig_hi))
    N_left_sb  = np.sum((phases >= sb_left_lo) & (phases < sb_left_hi))
    N_right_sb = np.sum((phases > sb_right_lo) & (phases <= sb_right_hi))

    # Background estimate: scale sidebands to signal region width
    signal_width = sig_hi - sig_lo
    total_sb_width = 2.0 * sideband_width
    total_sb_events = N_left_sb + N_right_sb

    if total_sb_width > 0:
        B_estimate = total_sb_events * (signal_width / total_sb_width)
    else:
        B_estimate = 0.0

    S_estimate = N_signal - B_estimate

    # Significance
    if B_estimate > 0:
        significance_Z = S_estimate / np.sqrt(B_estimate)
    else:
        significance_Z = 0.0

    # Descriptive statistics
    mean_phase   = np.mean(phases)
    std_phase    = np.std(phases)
    median_phase = np.median(phases)

    return {
        "N_total":       int(N_total),
        "N_signal":      int(N_signal),
        "N_left_sb":     int(N_left_sb),
        "N_right_sb":    int(N_right_sb),
        "B_estimate":    float(B_estimate),
        "S_estimate":    float(S_estimate),
        "significance_Z": float(significance_Z),
        "signal_window": (float(sig_lo), float(sig_hi)),
        "left_sideband": (float(sb_left_lo), float(sb_left_hi)),
        "right_sideband": (float(sb_right_lo), float(sb_right_hi)),
        "mean_phase":    float(mean_phase),
        "std_phase":     float(std_phase),
        "median_phase":  float(median_phase),
        "attractor":     float(attractor),
    }


def format_results(results):
    """Pretty-print the statistical results."""
    lines = [
        "=" * 60,
        " ACS Phase-Space Statistics — Higgs Window",
        "=" * 60,
        f"  Attractor (π/4):      {results['attractor']:.6f}",
        f"  Signal window:        [{results['signal_window'][0]:.6f}, {results['signal_window'][1]:.6f}]",
        f"  Left sideband:        [{results['left_sideband'][0]:.6f}, {results['left_sideband'][1]:.6f}]",
        f"  Right sideband:       [{results['right_sideband'][0]:.6f}, {results['right_sideband'][1]:.6f}]",
        "-" * 60,
        f"  Total events (window): {results['N_total']:,}",
        f"  N in signal region:    {results['N_signal']:,}",
        f"  N in left sideband:    {results['N_left_sb']:,}",
        f"  N in right sideband:   {results['N_right_sb']:,}",
        "-" * 60,
        f"  Background estimate B: {results['B_estimate']:.1f}",
        f"  Signal estimate S:     {results['S_estimate']:.1f}",
        f"  Significance Z=S/√B:   {results['significance_Z']:.2f} σ",
        "-" * 60,
        f"  Mean phase:            {results['mean_phase']:.6f}",
        f"  Median phase:          {results['median_phase']:.6f}",
        f"  Std phase:             {results['std_phase']:.6f}",
        "=" * 60,
    ]
    return "\n".join(lines)

"""
ACS Run — Orchestrator
=======================
Entry point for the full ACS analysis pipeline.

Usage:
    python run.py                           # Full Run 1 NanoAOD (61.5M events)
    python run.py --source edu_csv          # Educational CSV (small, fast test)
    python run.py --local path/to/file.root # Use a local ROOT file
    python run.py --no-gpu                  # Force CPU mode
"""

import argparse
import time
import sys
import os
import numpy as np

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config as cfg
from pipeline import (calculate_kinematics, map_acs_phase,
                       apply_quality_cuts, select_mass_window,
                       to_cpu, _GPU_AVAILABLE)
from ingest import load_data
from stats import compute_phase_statistics, format_results
from viz import plot_acs_phase, plot_mass_spectrum, plot_full_spectrum


def main():
    parser = argparse.ArgumentParser(
        description="ACS Analysis — Asymmetric Convergence Sequence on CMS Open Data"
    )
    parser.add_argument("--source", default=None,
                        help="Data source key (e.g., run1_nanoaod, edu_csv)")
    parser.add_argument("--local", default=None,
                        help="Path to a local ROOT or CSV file")
    parser.add_argument("--no-gpu", action="store_true",
                        help="Force CPU mode (disable CuPy)")
    parser.add_argument("--target-mass", type=float, default=None,
                        help=f"Target resonance mass in GeV (default: {cfg.TARGET_MASS})")
    parser.add_argument("--mass-window", type=float, nargs=2, default=None,
                        help="Mass window [low high] in GeV")
    parser.add_argument("--label", default=None,
                        help="Resonance label for output filenames (e.g., z, jpsi, upsilon)")
    args = parser.parse_args()

    # Override config from CLI
    if args.no_gpu:
        cfg.USE_GPU = False
    if args.target_mass:
        cfg.TARGET_MASS = args.target_mass
    if args.mass_window:
        cfg.MASS_WINDOW = tuple(args.mass_window)

    source_key = args.source or cfg.ACTIVE_SOURCE
    label = args.label or "higgs"

    # ─── Banner ───
    print("=" * 70)
    print("  ╔═══════════════════════════════════════════════════════╗")
    print("  ║  ASYMMETRIC CONVERGENCE SEQUENCE — MISSION CONTROL   ║")
    print(f"  ║  Target: {label.upper():^12s}  |  Attractor: π/4           ║")
    print("  ╚═══════════════════════════════════════════════════════╝")
    print("=" * 70)
    print(f"  Resonance:     {label}")
    print(f"  Data source:   {source_key}")
    print(f"  Target mass:   {cfg.TARGET_MASS} GeV")
    print(f"  Mass window:   {cfg.MASS_WINDOW} GeV")
    print(f"  GPU:           {'RTX 5090 (CuPy)' if _GPU_AVAILABLE else 'CPU (NumPy)'}")
    print(f"  Chunk size:    {cfg.CHUNK_SIZE:,}")
    print("=" * 70)

    # ─── Accumulators ───
    all_masses_higgs = []   # masses in Higgs window (for stats/viz)
    all_masses_full  = []   # all masses (for full spectrum)
    all_phases       = []   # ACS phases in Higgs window
    total_events     = 0
    total_passed     = 0
    total_higgs      = 0

    t_start = time.perf_counter()

    # ─── Streaming Processing ───
    for chunk_data in load_data(source_key=source_key, local_path=args.local):
        pt1  = chunk_data["pt1"]
        pt2  = chunk_data["pt2"]
        eta1 = chunk_data["eta1"]
        eta2 = chunk_data["eta2"]
        phi1 = chunk_data["phi1"]
        phi2 = chunk_data["phi2"]
        q1   = chunk_data["q1"]
        q2   = chunk_data["q2"]

        n_chunk = len(pt1)
        total_events += n_chunk

        # 1. Quality cuts (GPU-accelerated)
        quality_mask = apply_quality_cuts(pt1, pt2, eta1, eta2, q1, q2)
        quality_mask_cpu = to_cpu(quality_mask).astype(bool)

        pt1_q  = pt1[quality_mask_cpu]
        pt2_q  = pt2[quality_mask_cpu]
        eta1_q = eta1[quality_mask_cpu]
        eta2_q = eta2[quality_mask_cpu]
        phi1_q = phi1[quality_mask_cpu]
        phi2_q = phi2[quality_mask_cpu]

        n_passed = len(pt1_q)
        total_passed += n_passed

        if n_passed == 0:
            continue

        # 2. Invariant mass (GPU-accelerated)
        masses = calculate_kinematics(pt1_q, pt2_q, eta1_q, eta2_q,
                                       phi1_q, phi2_q)
        masses_cpu = to_cpu(masses)

        # Store a subsample for full spectrum (max 5M to avoid OOM on CPU)
        if len(all_masses_full) == 0 or sum(len(m) for m in all_masses_full) < 5_000_000:
            all_masses_full.append(masses_cpu.copy())

        # 3. Higgs window selection (GPU-accelerated)
        higgs_mask = select_mass_window(masses)
        higgs_mask_cpu = to_cpu(higgs_mask).astype(bool)
        masses_higgs = masses_cpu[higgs_mask_cpu]
        n_higgs = len(masses_higgs)
        total_higgs += n_higgs

        if n_higgs == 0:
            continue

        # 4. ACS phase mapping (GPU-accelerated)
        phases = map_acs_phase(masses_higgs, cfg.TARGET_MASS)
        phases_cpu = to_cpu(phases)

        all_masses_higgs.append(masses_higgs.copy())
        all_phases.append(phases_cpu.copy())

    t_elapsed = time.perf_counter() - t_start

    # ─── Aggregate Results ───
    print("\n" + "=" * 70)
    print(f"  Processing complete in {t_elapsed:.1f}s")
    print(f"  Total events:     {total_events:,}")
    print(f"  Passed cuts:      {total_passed:,}")
    print(f"  In Higgs window:  {total_higgs:,}")
    print("=" * 70)

    if total_higgs == 0:
        print("\n[WARN] No events in Higgs window. Check data source and cuts.")
        return

    # Concatenate
    masses_higgs_all = np.concatenate(all_masses_higgs)
    phases_all       = np.concatenate(all_phases)
    masses_full_all  = np.concatenate(all_masses_full)

    # ─── Statistics ───
    stat_results = compute_phase_statistics(phases_all)
    print("\n" + format_results(stat_results))

    # ─── Visualization ───
    print("\n[run] Generating plots...")

    plot_acs_phase(phases_all, stat_results,
                   title_suffix=f"[{label}]",
                   filename=f"acs_phase_{label}.png")
    plot_mass_spectrum(masses_higgs_all,
                       filename=f"mass_spectrum_{label}.png")
    plot_full_spectrum(masses_full_all,
                       filename=f"mass_spectrum_full_{label}.png")

    # ─── Final Summary ───
    print("\n" + "=" * 70)
    print("  ╔═══════════════════════════════════════════════════════╗")
    print(f"  ║  ACS RESULT: Z = {stat_results['significance_Z']:.2f} σ")
    print(f"  ║  Phase attractor π/4 = {cfg.ACS_ATTRACTOR:.6f}")
    print(f"  ║  Mean observed phase = {stat_results['mean_phase']:.6f}")
    print(f"  ║  Δ(θ) = {abs(stat_results['mean_phase'] - cfg.ACS_ATTRACTOR):.6f} rad")
    print("  ╚═══════════════════════════════════════════════════════╝")
    print("=" * 70)
    print(f"\n  Output: {os.path.abspath(cfg.OUTPUT_DIR)}/")
    print("  Done.\n")


if __name__ == "__main__":
    main()

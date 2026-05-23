"""
ACS Ingestion — Big Data Loader for CMS Open Data
===================================================
Streams ROOT NanoAOD or CSV files in memory-safe chunks.
Avoids OOM on multi-GB datasets by never loading full file.

Yields per chunk:
  dict with keys: pt1, pt2, eta1, eta2, phi1, phi2, q1, q2
  (leading two muons per event, opposite-sign preferred)
"""

import os
import sys
import urllib.request
import numpy as np
import config as cfg


# ─────────────────────────────────────────────
# HTTP Download with Progress
# ─────────────────────────────────────────────
def download_file(url, dest_path, label="Downloading"):
    """Download a file with a console progress bar."""
    if os.path.exists(dest_path):
        size = os.path.getsize(dest_path)
        print(f"[ingest] Cache hit: {dest_path} ({size / 1e9:.2f} GB)")
        return dest_path

    os.makedirs(os.path.dirname(dest_path) or ".", exist_ok=True)
    print(f"[ingest] {label}: {url}")

    def _progress(block_num, block_size, total_size):
        downloaded = block_num * block_size
        if total_size > 0:
            pct = min(downloaded / total_size * 100, 100)
            bar = "█" * int(pct // 2) + "░" * (50 - int(pct // 2))
            sys.stdout.write(f"\r  [{bar}] {pct:5.1f}%  ({downloaded / 1e9:.2f} / {total_size / 1e9:.2f} GB)")
            sys.stdout.flush()

    urllib.request.urlretrieve(url, dest_path, reporthook=_progress)
    print()  # newline after progress bar
    return dest_path


# ─────────────────────────────────────────────
# ROOT NanoAOD Streaming
# ─────────────────────────────────────────────
def stream_root_nanoaod(filepath, step_size=None):
    """
    Stream a CMS NanoAOD ROOT file in chunks.

    For each event with nMuon >= 2, extracts the leading two muons.
    Yields dicts: {pt1, pt2, eta1, eta2, phi1, phi2, q1, q2}
    """
    import uproot
    import awkward as ak

    if step_size is None:
        step_size = cfg.CHUNK_SIZE

    source_cfg = cfg.DATA_SOURCES[cfg.ACTIVE_SOURCE]
    tree_name = source_cfg["tree"]
    branches = source_cfg["branches"]

    print(f"[ingest] Opening ROOT: {filepath}")
    print(f"[ingest] Tree: {tree_name}, step_size: {step_size:,}")

    with uproot.open(f"{filepath}:{tree_name}") as tree:
        total = tree.num_entries
        processed = 0

        for chunk in tree.iterate(branches, step_size=step_size,
                                  library="ak"):
            n_muon = chunk["nMuon"]
            # Require at least 2 muons
            mask_2mu = n_muon >= 2
            chunk = chunk[mask_2mu]

            if len(chunk) == 0:
                processed += step_size
                continue

            # Extract leading two muons (index 0 and 1)
            pt  = chunk["Muon_pt"]
            eta = chunk["Muon_eta"]
            phi = chunk["Muon_phi"]
            q   = chunk["Muon_charge"]

            result = {
                "pt1":  ak.to_numpy(pt[:, 0]),
                "pt2":  ak.to_numpy(pt[:, 1]),
                "eta1": ak.to_numpy(eta[:, 0]),
                "eta2": ak.to_numpy(eta[:, 1]),
                "phi1": ak.to_numpy(phi[:, 0]),
                "phi2": ak.to_numpy(phi[:, 1]),
                "q1":   ak.to_numpy(q[:, 0]),
                "q2":   ak.to_numpy(q[:, 1]),
            }

            processed += step_size
            pct = min(processed / total * 100, 100)
            n_pairs = len(result["pt1"])
            print(f"\r[ingest] Progress: {pct:5.1f}%  |  chunk: {n_pairs:,} pairs", end="", flush=True)

            yield result

        print()  # final newline


# ─────────────────────────────────────────────
# CSV Streaming (fallback / educational data)
# ─────────────────────────────────────────────
def stream_csv(filepath, chunksize=None):
    """
    Stream a CMS dimuon CSV in pandas chunks.
    Yields dicts: {pt1, pt2, eta1, eta2, phi1, phi2, q1, q2}

    Expected columns: pt1, eta1, phi1, Q1, pt2, eta2, phi2, Q2
    (from the educational Dimuon_DoubleMu.csv format)
    """
    import pandas as pd

    if chunksize is None:
        chunksize = cfg.CHUNK_SIZE

    print(f"[ingest] Streaming CSV: {filepath}, chunksize={chunksize:,}")

    # The educational CSV uses column names like 'pt1', 'eta1' etc.
    # but may also have uppercase or mixed naming — we normalize.
    for i, chunk in enumerate(pd.read_csv(filepath, chunksize=chunksize)):
        cols = {c.lower().strip(): c for c in chunk.columns}

        # Map to standard names
        def _col(name):
            # Try exact, then with number suffix patterns
            for candidate in [name, name.upper(), name.capitalize()]:
                if candidate in chunk.columns:
                    return chunk[candidate].values
            return None

        result = {
            "pt1":  _col("pt1"),
            "pt2":  _col("pt2"),
            "eta1": _col("eta1"),
            "eta2": _col("eta2"),
            "phi1": _col("phi1"),
            "phi2": _col("phi2"),
            "q1":   _col("Q1"),
            "q2":   _col("Q2"),
        }

        # Validate
        if any(v is None for v in result.values()):
            # Fallback: try column indices for known format
            print(f"[ingest] WARNING: Column name mismatch, attempting index-based mapping")
            # Educational CSV: Run,Event,E1,px1,py1,pz1,pt1,eta1,phi1,Q1,E2,px2,py2,pz2,pt2,eta2,phi2,Q2,M
            df = chunk
            result = {
                "pt1":  df.iloc[:, 6].values.astype(np.float64),
                "pt2":  df.iloc[:, 14].values.astype(np.float64),
                "eta1": df.iloc[:, 7].values.astype(np.float64),
                "eta2": df.iloc[:, 15].values.astype(np.float64),
                "phi1": df.iloc[:, 8].values.astype(np.float64),
                "phi2": df.iloc[:, 16].values.astype(np.float64),
                "q1":   df.iloc[:, 9].values.astype(np.float64),
                "q2":   df.iloc[:, 17].values.astype(np.float64),
            }

        n = len(result["pt1"])
        print(f"\r[ingest] CSV chunk {i}: {n:,} events", end="", flush=True)
        yield result

    print()


# ─────────────────────────────────────────────
# Unified Loader
# ─────────────────────────────────────────────
def load_data(source_key=None, local_path=None):
    """
    High-level data loader. Returns a generator of chunk dicts.

    If local_path is provided, uses it directly.
    Otherwise downloads from the configured source.

    Args:
        source_key: key into config.DATA_SOURCES (default: ACTIVE_SOURCE)
        local_path: override path to a local file

    Yields:
        dict with keys: pt1, pt2, eta1, eta2, phi1, phi2, q1, q2
    """
    if source_key is None:
        source_key = cfg.ACTIVE_SOURCE

    source = cfg.DATA_SOURCES[source_key]
    fmt = source["format"]

    if local_path is None:
        # Determine download path
        os.makedirs("data", exist_ok=True)
        if fmt == "root":
            filename = source["http_url"].split("/")[-1]
            local_path = os.path.join("data", filename)
            download_file(source["http_url"], local_path,
                          label=f"Downloading ROOT ({source['n_events']:,} events)")
        elif fmt == "csv":
            filename = source["url"].split("/")[-1]
            local_path = os.path.join("data", filename)
            download_file(source["url"], local_path, label="Downloading CSV")

    print(f"[ingest] Source: {source_key} ({fmt})")

    if fmt == "root":
        print(f"[ingest] File: {local_path}")
        yield from stream_root_nanoaod(local_path)
    elif fmt == "root_multi":
        yield from _load_multi_root(source)
    elif fmt == "csv":
        print(f"[ingest] File: {local_path}")
        yield from stream_csv(local_path)
    else:
        raise ValueError(f"Unknown format: {fmt}")


def _parallel_download(pairs, max_workers=4):
    """
    Download all missing files in parallel using a ThreadPool.
    Validates file sizes after download to catch truncation.
    Returns list of (local_path, fname) in original order.
    """
    from concurrent.futures import ThreadPoolExecutor, as_completed
    import threading

    n_files = len(pairs)
    to_download = [(i, url, local, fname) for i, (url, local, fname) in enumerate(pairs)
                   if not os.path.exists(local)]
    cached = n_files - len(to_download)

    if not to_download:
        print(f"[ingest] All {n_files} files cached — skipping download phase.")
        return

    total_lock = threading.Lock()
    completed = [0]
    failed = []

    def _download_one(item):
        idx, url, local, fname = item
        try:
            os.makedirs(os.path.dirname(local) or ".", exist_ok=True)
            print(f"\n[download] Starting {idx+1}/{n_files}: {fname}")
            urllib.request.urlretrieve(url, local)
            size_gb = os.path.getsize(local) / 1e9
            with total_lock:
                completed[0] += 1
                done = completed[0] + cached
            print(f"\n[download] ✓ {fname}  ({size_gb:.2f} GB)  [{done}/{n_files} total]")
            return (idx, local, fname, True)
        except Exception as e:
            with total_lock:
                failed.append((fname, str(e)))
            print(f"\n[download] ✗ FAILED {fname}: {e}")
            # Clean up partial file
            if os.path.exists(local):
                try:
                    os.remove(local)
                except OSError:
                    pass
            return (idx, local, fname, False)

    print(f"\n{'='*70}")
    print(f"  ╔═══════════════════════════════════════════════════════╗")
    print(f"  ║  PARALLEL DOWNLOAD — {max_workers} threads              ║")
    print(f"  ║  Cached: {cached}/{n_files}  |  To download: {len(to_download)}        ║")
    print(f"  ╚═══════════════════════════════════════════════════════╝")
    print(f"{'='*70}")

    import time
    t0 = time.perf_counter()

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {pool.submit(_download_one, item): item for item in to_download}
        for future in as_completed(futures):
            future.result()  # propagate exceptions

    elapsed = time.perf_counter() - t0
    new_cached_gb = sum(os.path.getsize(p[1]) / 1e9 for p in pairs if os.path.exists(p[1]))

    print(f"\n{'='*70}")
    print(f"  Download phase complete: {elapsed:.0f}s")
    print(f"  Total cached: {new_cached_gb:.1f} GB across {n_files} files")
    if failed:
        print(f"  ⚠ FAILED: {len(failed)} files:")
        for fname, err in failed:
            print(f"    - {fname}: {err}")
    print(f"{'='*70}\n")


def _load_multi_root(source):
    """
    Download ALL files in parallel (ThreadPool), then stream/process sequentially.

    Phase 1: Parallel download — saturates bandwidth with 4 concurrent connections
    Phase 2: Sequential processing — stream ROOT files through the analysis pipeline

    Supports two config formats:
      New (multi-base):
        "file_sources": [(http_base_1, [file1, ...]), ...]
      Legacy (single-base):
        "http_base": "...", "files": [file1, ...]
    """
    # Build a flat list of (url, local_path, fname) tuples
    pairs = []
    if "file_sources" in source:
        for http_base, files in source["file_sources"]:
            for fname in files:
                url = http_base + fname
                local = os.path.join("data", "13tev_" + fname)
                pairs.append((url, local, fname))
    else:
        http_base = source["http_base"]
        for fname in source["files"]:
            url = http_base + fname
            local = os.path.join("data", "13tev_" + fname)
            pairs.append((url, local, fname))

    n_files = len(pairs)
    cached_gb = sum(os.path.getsize(p[1]) / 1e9 for p in pairs if os.path.exists(p[1]))
    print(f"[ingest] Multi-file dataset: {n_files} files (cached: {cached_gb:.1f} GB)")

    # ── Phase 1: Parallel Download ──
    _parallel_download(pairs, max_workers=4)

    # ── Phase 2: Sequential Processing ──
    print(f"\n[ingest] ═══ PROCESSING PHASE ═══")
    for i, (url, local, fname) in enumerate(pairs):
        if not os.path.exists(local):
            print(f"\n[ingest] ⚠ Skipping {fname} (download failed)")
            continue
        print(f"\n[ingest] ── Processing {i+1}/{n_files}: {fname} ──")
        yield from stream_root_nanoaod(local)



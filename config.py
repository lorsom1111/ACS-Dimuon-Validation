"""
ACS-CERN Configuration
======================
Central configuration for the Asymmetric Convergence Sequence analysis
on CMS Open Data (Run 1/2 DoubleMuon).

All physics constants, data URIs, GPU parameters, and analysis windows.
"""

import numpy as np

# ─────────────────────────────────────────────
# Physics Constants
# ─────────────────────────────────────────────
HIGGS_MASS      = 125.1    # GeV — PDG 2024 central value
Z_MASS          = 91.1876  # GeV
JPSI_MASS       = 3.0969   # GeV
PSI2S_MASS      = 3.6861   # GeV
PHI_MASS        = 1.01946  # GeV
UPSILON_1S_MASS = 9.4603   # GeV
UPSILON_2S_MASS = 10.0233  # GeV
UPSILON_3S_MASS = 10.3552  # GeV
MUON_MASS       = 0.10566  # GeV

# ACS Attractor
ACS_ATTRACTOR = np.pi / 4  # ≈ 0.785398

# ─────────────────────────────────────────────
# Target Resonance (active analysis)
# ─────────────────────────────────────────────
TARGET_MASS   = HIGGS_MASS
MASS_WINDOW   = (115.0, 135.0)  # GeV — Higgs search window

# ─────────────────────────────────────────────
# Data Sources — CERN Open Data Portal
# ─────────────────────────────────────────────
DATA_SOURCES = {
    # 61.5M events, 2.2 GB ROOT, NanoAOD reduced on muons (Run 2012 B+C)
    "run1_nanoaod": {
        "url": "root://eospublic.cern.ch//eos/opendata/cms/derived-data/"
               "AOD2NanoAODOutreachTool/Run2012BC_DoubleMuParked_Muons.root",
        "http_url": "https://opendata.cern.ch/record/12341/files/"
                    "Run2012BC_DoubleMuParked_Muons.root",
        "record": 12341,
        "tree": "Events",
        "branches": ["nMuon", "Muon_pt", "Muon_eta", "Muon_phi",
                      "Muon_mass", "Muon_charge"],
        "n_events": 61_540_413,
        "size_bytes": 2_244_449_133,
        "format": "root",
    },
    # Run 2016G+H DoubleMuon NanoAOD — 13 TeV, full dataset
    # Record 30522 (G, 29 files, 42.2 GB) + Record 30555 (H, 28 files, 46.0 GB)
    # Total: 57 files, 88.3 GB
    "run2_nanoaod_13tev": {
        "file_sources": [
            # ── Run2016G (Record 30522) ──
            ("http://opendata.cern.ch/eos/opendata/cms/Run2016G/DoubleMuon/NANOAOD/UL2016_MiniAODv2_NanoAODv9-v2/2430000/",
             [
                "4E3A26DE-E53B-A844-8048-36376617AE8D.root",   # 0.07 GB
                "8E86856A-A894-CE4E-8D07-060C9633C368.root",   # 0.13 GB
                "F1D0DAC7-256C-0E47-AA8E-679FBAA2E47D.root",   # 0.27 GB
                "4AAF4AB2-171D-F54C-8FE3-0D709B049A8A.root",   # 0.38 GB
                "F20C428E-C7D7-BB46-BA0F-BCB31B79F1AC.root",   # 0.46 GB
                "BA67D74C-A071-104C-BE33-AF82B10BAEB7.root",   # 0.74 GB
                "ED3359B9-BF1E-044C-8418-ACDDE2B11FF0.root",   # 0.93 GB
                "3B20EB8F-4FD1-D041-9513-1A82351756E1.root",   # 1.01 GB
                "78FA0801-28AF-3A45-A36A-AB7CC9A5506E.root",   # 1.02 GB
                "8FA6C301-684B-9E46-B901-87FCD68FC02F.root",   # 1.04 GB
                "D535680D-169D-094E-B424-D79C59C6687F.root",   # 1.11 GB
                "EF0619CE-F699-5942-BA8B-206D2D434A33.root",   # 1.20 GB
                "E243437A-C5B2-E543-AD00-931CE36A3935.root",   # 1.20 GB
                "58749C91-2895-334A-8546-D163C2E05718.root",   # 1.39 GB
                "2631F9B1-3B3E-7E4A-BE75-FC57E322C981.root",   # 1.39 GB
                "26A77DF8-54A5-7B44-B1BB-5B93CFF5C9C6.root",   # 1.53 GB
                "28E0E7C4-3DA1-6C47-8EBB-89C9507BC283.root",   # 1.62 GB
                "D1989538-A8AE-854E-9F7B-6638D5D45817.root",   # 1.75 GB
                "8B0B7376-00E2-BF47-A0B2-7CD4E77FC2CB.root",   # 1.90 GB
                "A3CE8422-11FF-5D4C-922D-B592FDD76682.root",   # 1.96 GB
                "23A0C786-B116-F346-81C1-18EF4716C097.root",   # 2.11 GB
                "05DD095C-F6C3-9A4F-9FB3-348A5A6403D5.root",   # 2.16 GB
                "7B6069C4-7ED4-C34B-BD4C-8DE972F9206C.root",   # 2.16 GB
                "718C97EB-8F87-E644-9371-E04760201AE4.root",   # 2.27 GB
                "209D94D9-B6D5-A34B-A2A3-CBB7E4EA8ADF.root",   # 2.28 GB
                "A4201268-368C-D74F-B79E-8C01803D8608.root",   # 2.31 GB
                "87162F7A-6440-6F41-B61C-DD84BF000C35.root",   # 2.49 GB
                "99BE333D-5E3F-5D4B-A24A-A250B8B2C2EC.root",   # 2.58 GB
                "A492FDC6-77B1-5745-A129-50784E0B3028.root",   # 2.79 GB
             ]),
            # ── Run2016H (Record 30555) ──
            ("http://opendata.cern.ch/eos/opendata/cms/Run2016H/DoubleMuon/NANOAOD/UL2016_MiniAODv2_NanoAODv9-v1/2510000/",
             [
                "EEB2FE3F-7CF3-BF4A-9F70-3F89FACE698E.root",   # 0.28 GB
                "1BE226A3-7A8D-1B43-AADC-201B563F3319.root",   # 0.98 GB
                "CD267D88-E57D-3B44-AC45-0712E2E12B87.root",   # 0.99 GB
                "F5E234F9-1E9C-0042-B395-AB6407E4A336.root",   # 1.00 GB
                "CAA285FF-7A12-F945-9183-DC7042178535.root",   # 1.04 GB
                "4F0B53A7-6440-924B-AF48-B5B61D3CE23F.root",   # 1.14 GB
                "EBC200F4-C06F-CE45-BAAA-7CAECDD3076F.root",   # 1.36 GB
                "B2DC29E0-8679-1D4F-A5AE-E7D0284A20D4.root",   # 1.39 GB
                "B93B57BF-4239-A049-9531-4C542C370185.root",   # 1.42 GB
                "3676E287-A650-8F44-BBCB-3B8556966406.root",   # 1.42 GB
                "46A8960A-E58F-4648-9C12-2708FE7C12FB.root",   # 1.44 GB
                "B7AA7F04-5D5F-514A-83A6-9A275198852C.root",   # 1.55 GB
                "1DE780E2-BCC2-DC48-815D-9A97B2A4A2CD.root",   # 1.60 GB
                "2C6A0345-8E2E-9B41-BB51-DB56DFDFB89A.root",   # 1.63 GB
                "790F8A75-8256-3B46-8209-850DE0BE3C77.root",   # 1.64 GB
                "E7C51551-7A75-5C41-B468-46FB922F36A9.root",   # 1.69 GB
                "411A019C-7058-FD42-AD50-DE74433E6859.root",   # 1.84 GB
                "21DA4CE5-4E50-024F-9CE1-50C77254DD4E.root",   # 1.87 GB
                "7F53D1DE-439E-AD48-871E-D3458DABA798.root",   # 1.91 GB
                "B450B2B3-BEF8-8C43-82BF-7AD0EF2EA7EA.root",   # 1.96 GB
                "183BFB78-7B5E-734F-BBF5-174A73020F89.root",   # 2.01 GB
                "127C2975-1B1C-A046-AABF-62B77E757A86.root",   # 2.02 GB
                "A6605227-0B58-864E-8422-B8990D18F622.root",   # 2.18 GB
                "9528EA75-1C0B-9047-A9A3-6A47564F7A98.root",   # 2.20 GB
                "C8CFC890-D4B8-8A4F-8699-C6ACCDF1620A.root",   # 2.28 GB
                "8B253755-51F2-CB49-A4B6-C79637CAE23F.root",   # 2.37 GB
                "C4558F81-9F2C-1349-B528-6B9DD6838D6D.root",   # 2.38 GB
                "8A696857-C147-B04A-905A-F85FB76EDA23.root",   # 2.45 GB
             ]),
        ],
        "record": "30522+30555",
        "tree": "Events",
        "branches": ["nMuon", "Muon_pt", "Muon_eta", "Muon_phi",
                      "Muon_mass", "Muon_charge"],
        "n_events": 90_000_000,
        "energy_tev": 13,
        "format": "root_multi",
    },
    # Educational CSV — small, ~100k events, direct HTTP download
    "edu_csv": {
        "url": "http://opendata.cern.ch/record/545/files/Dimuon_DoubleMu.csv",
        "record": 545,
        "columns": ["Run", "Event", "E1", "px1", "py1", "pz1",
                     "pt1", "eta1", "phi1", "Q1",
                     "E2", "px2", "py2", "pz2",
                     "pt2", "eta2", "phi2", "Q2", "M"],
        "format": "csv",
    },
}

# Active data source key
ACTIVE_SOURCE = "run1_nanoaod"

# ─────────────────────────────────────────────
# Processing Parameters
# ─────────────────────────────────────────────
CHUNK_SIZE     = 2_000_000   # events per chunk (ROOT step_size / CSV chunksize)
USE_GPU        = True        # attempt CuPy acceleration on RTX 5090
GPU_DEVICE     = 0           # CUDA device index

# ─────────────────────────────────────────────
# Quality Cuts
# ─────────────────────────────────────────────
MIN_PT         = 5.0    # GeV — minimum muon pT
MAX_ETA        = 2.4    # pseudorapidity acceptance
OPPOSITE_CHARGE = True  # require μ⁺μ⁻

# ─────────────────────────────────────────────
# ACS Statistics
# ─────────────────────────────────────────────
# Phase signal window around π/4 attractor
PHASE_SIGNAL_HALFWIDTH = 0.005  # radians
# Sideband regions for background estimation
PHASE_SIDEBAND_WIDTH   = 0.020  # radians each side

# ─────────────────────────────────────────────
# Visualization
# ─────────────────────────────────────────────
PHASE_HIST_BINS   = 500
MASS_HIST_BINS    = 200
DPI               = 200
OUTPUT_DIR        = "output"

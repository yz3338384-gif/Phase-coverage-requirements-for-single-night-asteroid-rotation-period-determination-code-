# Phase-coverage requirements for single-night asteroid rotation period determination

Code for the manuscript:

> **Phase-coverage requirements for single-night asteroid rotation period determination**
> *Astronomische Nachrichten* (submitted)

This repository reproduces all simulations, figures, and the real-data validation
of the paper. It contains **only** the minimal code set needed for the AN paper
(the v10 Coverage-Aware Fourier Periodometry framework is a separate project).

## Structure

```
an_paper_code/
├── core/                          # simulation + period-search modules
│   ├── truth_generator.py         #   noise-free Fourier light-curve generator
│   ├── obs_simulator.py           #   single-night observing session simulator
│   └── period_searcher.py         #   Lomb-Scargle period search (×2 correction)
├── experiments/
│   ├── amp_scan.py                # main simulation: 16,200 trials
│   │                              #   (6 amplitudes × 9 coverages × 3 periods × 100 repeats)
│   ├── amp_scan_tol10.py          # robustness check with 10% tolerance
│   ├── final_targets_56.py        # 56-target list (32 clean + 24 expansion; 54 with LCDB U≥2)
│   ├── alcdef_validation.py       # ALCDEF parsing + session splitting
│   └── run_56_validation.py       # real-data validation: 54 targets (U≥2) / 2,091 sessions
├── analysis/
│   ├── make_amp_figs.py           # Figure: coverage×amplitude heatmap + curves
│   └── make_real_fig.py           # Figure: real-data vs simulation recovery curve
├── output/final_experiments/      # pre-computed simulation results (CSV)
│   ├── amp_scan_20260813.csv
│   └── amp_scan_tol10_20260814.csv
└── requirements.txt
```

## Quick start

```bash
pip install -r requirements.txt

# 1. Run the main simulation (16,200 trials; ~minutes)
python experiments/amp_scan.py

# 2. Run the 10%-tolerance robustness check
python experiments/amp_scan_tol10.py

# 3. Generate figures (reads the CSVs above)
python analysis/make_amp_figs.py
python analysis/make_real_fig.py

# 4. Real-data validation (54 targets / 2,091 sessions, LCDB U≥2)
#    Requires raw ALCDEF files. Set the data directory via env var:
set ALCDEF_DIR=C:\path\to\alcdef_data     # Windows
# export ALCDEF_DIR=/path/to/alcdef_data   # Linux/macOS
python experiments/run_56_validation.py
```

## Data sources

- **ALCDEF** (Asteroid Light Curve Data Exchange Format):
  http://www.alcdef.org — raw photometric sessions.
- **LCDB** (Asteroid Light Curve Database; 2023 October summary):
  https://minplanobs.org/mpinfo/php/lcdb.php — ground-truth periods and
  quality codes (U).

The pre-computed simulation CSVs are committed so the figures can be
regenerated without re-running the full simulation.

## Simulation setup (paper Section 2)

- Fixed: `P_true ∈ {6, 12, 24} h`, `K_true = 4`, `σ = 0.02 mag`, 5-min cadence.
- Coverage grid: `C ∈ {0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50, 0.60, 0.75}`.
- Amplitude grid: `{0.05, 0.08, 0.10, 0.15, 0.20, 0.30} mag`.
- Success criterion: `|P_est/P_true − 1| < 0.20` (paper-wide).
- 100 Monte-Carlo repeats per (amplitude, coverage, period) cell.
- Continuous equal-spaced sampling (realistic single-night cadence),
  which matches real data to within a factor of 1.6 (random sampling in the
  earlier framework differed by 4.5×).

## License / citation

If you use this code, please cite the manuscript (DOI to be added after
acceptance) and the data sources above.

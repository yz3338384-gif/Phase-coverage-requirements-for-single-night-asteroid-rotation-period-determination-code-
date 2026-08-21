"""
Amplitude x coverage scan for single-night period recovery.
Fixed: P_true=12h, K_true=4, sigma=0.02 mag, 5-min cadence.
Success: |P_est/P_true - 1| < 0.20 (paper-wide criterion).
Output: output/final_experiments/amp_scan_tol10_20260814.csv
"""
import os
import sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import numpy as np
import pandas as pd
from core.obs_simulator import make_single_night
from core.period_searcher import search

PERIODS = [6, 12, 24]
K_TRUE = 4
SIGMA = 0.02
INTERVAL = 5.0
AMPLITUDES = [0.05, 0.08, 0.10, 0.15, 0.20, 0.30]
COVERAGES = [0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50, 0.60, 0.75]
N_REPEATS = 100
TOL = 0.10

rows = []
for PERIOD in PERIODS:
  for amp in AMPLITUDES:
    for C in COVERAGES:
        dur = C * PERIOD
        succ = 0
        n_valid = 0
        for i in range(N_REPEATS):
            seed = 100000 + int(PERIOD * 1000) + int(round(amp * 1000)) * 100 + int(round(C * 100)) * 10 + i
            d = make_single_night(PERIOD, K_TRUE, dur, INTERVAL, SIGMA, amp, seed=seed)
            try:
                res = search(d['times_h'], d['mag'],
                             period_min=PERIOD*0.3, period_max=PERIOD*3.0)
                P_est = res.best_period
            except Exception:
                continue
            n_valid += 1
            if abs(P_est / PERIOD - 1) < TOL:
                succ += 1
        rate = succ / n_valid if n_valid else 0.0
        rows.append({'period_h': PERIOD, 'amplitude_mag': amp, 'coverage': C,
                     'n_trials': n_valid, 'recovery_rate': rate})
        print(f"P={PERIOD}h amp={amp:.2f} C={C:.2f} rate={rate:.3f} ({succ}/{n_valid})", flush=True)

df = pd.DataFrame(rows)
outdir = os.path.join(ROOT, 'output', 'final_experiments')
os.makedirs(outdir, exist_ok=True)
out = os.path.join(outdir, 'amp_scan_tol10_20260814.csv')
df.to_csv(out, index=False)
print("Saved:", out)

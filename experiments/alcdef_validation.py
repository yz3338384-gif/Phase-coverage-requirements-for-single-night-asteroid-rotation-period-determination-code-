"""
Real-data validation: process ALCDEF files, compare with identifiability model.
"""
import sys
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pandas as pd
import os, glob, sys
sys.path.insert(0, os.path.dirname(__file__))

# ALCDEF raw data directory: set env var ALCDEF_DIR, or place files in ./data/alcdef
ALCDEF_DIR = os.environ.get('ALCDEF_DIR', os.path.join(ROOT, 'data', 'alcdef'))
OUTPUT_DIR = os.path.join(ROOT, 'output', 'validation')
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ============================================================================
# Known targets with U=3 (or U=2+) from LCDB + our work
# ============================================================================
KNOWN_TARGETS = {
    '78_Diana': {'P_h': 7.2991, 'U': 3, 'K_est': 4},
    '4460_Bihoro': {'P_h': 4.9127, 'U': 2, 'K_est': 4},
    '717_Wisibada': {'P_h': 24.28, 'U': 1, 'K_est': 4},
    '1397_Umtata': {'P_h': 30.03, 'U': 2, 'K_est': 4},
    '1965_van_de_Kamp': {'P_h': 24.13, 'U': 1, 'K_est': 4},
    '3731_Hancock': {'P_h': 3.22, 'U': 1, 'K_est': 4},  # estimated
}

# Additional known U=3 asteroids from literature
ADDITIONAL_U3 = {
    '1580_Betulia': {'P_h': 6.138, 'U': 3, 'K_est': 4},
    '1620_Geographos': {'P_h': 5.223, 'U': 3, 'K_est': 4},
    '1862_Apollo': {'P_h': 3.065, 'U': 3, 'K_est': 4},
    '2063_Bacchus': {'P_h': 14.9, 'U': 3, 'K_est': 4},
    '2100_Ra_Shalom': {'P_h': 19.79, 'U': 3, 'K_est': 4},
    '3103_Eger': {'P_h': 5.705, 'U': 3, 'K_est': 4},
    '4015_Wilson_Harrington': {'P_h': 3.5736, 'U': 3, 'K_est': 4},
    '4179_Toutatis': {'P_h': 176.0, 'U': 3, 'K_est': 4},
}

# Merge
ALL_TARGETS = {**KNOWN_TARGETS, **ADDITIONAL_U3}


def parse_alcdef(filepath):
    """
    Parse an ALCDEF file into (metadata, data_arrays).
    
    Returns
    -------
    metadata : dict
    jd, mag, mag_err : np.ndarrays
    """
    metadata = {}
    data_jd, data_mag, data_err = [], [], []
    in_meta = False
    
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        for line in f:
            line = line.strip()
            if line == 'STARTMETADATA':
                in_meta = True
                continue
            elif line == 'ENDMETADATA':
                in_meta = False
                continue
            elif in_meta:
                if '=' in line:
                    k, v = line.split('=', 1)
                    metadata[k.strip()] = v.strip()
            elif line.startswith('DATA='):
                parts = line[5:].split('|')
                if len(parts) >= 3:
                    try:
                        jd = float(parts[0])
                        mag = float(parts[1])
                        err = float(parts[2])
                        # filter invalid values
                        if 2400000 < jd < 2500000 and -10 < mag < 30 and err > 0:
                            data_jd.append(jd)
                            data_mag.append(mag)
                            data_err.append(err)
                    except:
                        pass
    
    return metadata, np.array(data_jd), np.array(data_mag), np.array(data_err)


def split_sessions(jd, mag, mag_err, gap_hours=12):
    """
    Split data into observing sessions based on JD gaps.
    A gap > gap_hours indicates a new session.
    """
    jd = np.asarray(jd)
    mag = np.asarray(mag)
    mag_err = np.asarray(mag_err)
    
    # Sort by JD
    order = np.argsort(jd)
    jd = jd[order]
    mag = mag[order]
    mag_err = mag_err[order]
    
    gap_jd = gap_hours / 24.0
    splits = [0]
    for i in range(1, len(jd)):
        if jd[i] - jd[i-1] > gap_jd:
            splits.append(i)
    splits.append(len(jd))
    
    sessions = []
    for i in range(len(splits)-1):
        s, e = splits[i], splits[i+1]
        if e - s >= 5:  # ?喳? 5 ??
            sessions.append({
                'jd': jd[s:e],
                'mag': mag[s:e],
                'mag_err': mag_err[s:e],
                'n_points': e - s,
            })
    
    return sessions


def validate_session(session, P_true, K_est, sigma_est=0.02):
    """
    Validate one observing session against known period.
    Returns coverage, LS success, and model prediction.
    """
    from obs_simulator import compute_coverage
    from period_searcher import search as ls_search
    # Model prediction (optional: requires the v10 identifiability module,
    # which is NOT part of this repository)
    try:
        from identifiability_calculator import IdentifiabilityCalculator
        calc = IdentifiabilityCalculator()
        pred = calc.predict(coverage, K_est, sigma_est)
        model_P_period = pred.P_period_success
        model_P_combined = pred.P_combined
        model_recommendation = pred.recommendation.split('|')[0].strip()
    except Exception:
        model_P_period = np.nan
        model_P_combined = np.nan
        model_recommendation = 'n/a'
    
    jd = session['jd']
    mag = session['mag']
    mag_err = session['mag_err']
    
    # Compute coverage at known period
    times_h = (jd - jd[0]) * 24.0  # convert to hours from start
    phase = (times_h % P_true) / P_true
    coverage = compute_coverage(phase)
    
    # LS period search
    try:
        ls_result = ls_search(
            times_h, mag,
            period_min=P_true * 0.3,
            period_max=P_true * 3.0
        )
        P_ls = ls_result.best_period
        ls_power = ls_result.best_power
        
        # LS success = period within 20% of true
        ls_ok = int(abs(P_ls - P_true) / P_true < 0.20)
    except:
        P_ls = -1
        ls_power = -1
        ls_ok = 0
    
    # Model prediction
    
    return {
        'n_points': len(mag),
        'duration_h': float(times_h[-1] - times_h[0]) if len(times_h) > 1 else 0,
        'P_true': P_true,
        'coverage': coverage,
        'P_ls': P_ls,
        'ls_power': ls_power,
        'ls_ok': ls_ok,
        'model_P_period': model_P_period,
        'model_P_combined': model_P_combined,
        'model_recommendation': model_recommendation,
    }


def validate_target(name, target_info):
    """Run validation for one target asteroid."""
    filepath = os.path.join(ALCDEF_DIR, f'ALCDEF_{name}.txt')
    if not os.path.exists(filepath):
        print(f"  SKIP: {filepath} not found")
        return []
    
    P_true = target_info['P_h']
    K_est = target_info.get('K_est', 4)
    
    # Parse
    meta, jd, mag, mag_err = parse_alcdef(filepath)
    obj_name = meta.get('OBJECTNAME', name)
    
    # Split into sessions
    sessions = split_sessions(jd, mag, mag_err, gap_hours=12)
    
    print(f"  {name}: {len(sessions)} sessions ({len(jd)} data points, P={P_true}h)")
    
    # Validate each session
    results = []
    for i, sess in enumerate(sessions):
        result = validate_session(sess, P_true, K_est)
        result['target'] = name
        result['object_name'] = obj_name
        result['session_id'] = i
        result['session_jd_start'] = sess['jd'][0]
        results.append(result)
    
    return results


def run_alcdef_validation(targets=None):
    """Run validation on selected targets."""
    if targets is None:
        targets = ALL_TARGETS
    
    all_results = []
    total_sessions = 0
    
    print(f"ALCDEF Validation: {len(targets)} targets")
    print("=" * 60)
    
    for name, info in targets.items():
        results = validate_target(name, info)
        all_results.extend(results)
        total_sessions += len(results)
        
        # Per-target summary
        if results:
            ls_rate = np.mean([r['ls_ok'] for r in results])
            avg_cov = np.mean([r['coverage'] for r in results])
            print(f"    LS recovery rate: {ls_rate:.0%} ({sum(r['ls_ok'] for r in results)}/{len(results)})")
            print(f"    Avg coverage: {avg_cov:.0%}")
    
    print(f"\nTotal: {len(targets)} targets, {total_sessions} sessions")
    
    df = pd.DataFrame(all_results)
    return df


def print_validation_summary(df):
    """Print validation results vs model predictions."""
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    
    print(f"\nTotal sessions: {len(df)}")
    print(f"LS overall recovery: {df['ls_ok'].mean():.0%}")
    
    # By coverage bins
    cov_bins = [0, 0.15, 0.25, 0.35, 0.45, 0.55, 0.70, 1.0]
    df['cov_bin'] = pd.cut(df['coverage'], bins=cov_bins)
    
    print(f"\n{'Coverage':>12s} {'n':>5s} {'LS rec':>10s} {'Model':>10s} {'Bias':>8s}")
    print("-" * 45)
    
    for bin_name, g in df.groupby('cov_bin', observed=True):
        n = len(g)
        ls_rate = g['ls_ok'].mean()
        model_pred = g['model_P_period'].mean()
        bias = ls_rate - model_pred
        print(f"{str(bin_name):>12s} {n:>5d} {ls_rate:>9.0%} {model_pred:>9.0%} {bias:>+7.0%}")

    # By target
    print(f"\n{'Target':>20s} {'n':>5s} {'LS rec':>10s} {'Model':>10s} {'Bias':>8s}")
    print("-" * 55)
    for name, g in df.groupby('target'):
        n = len(g)
        ls_rate = g['ls_ok'].mean()
        model_pred = g['model_P_period'].mean()
        bias = ls_rate - model_pred
        print(f"{name:>20s} {n:>5d} {ls_rate:>9.0%} {model_pred:>9.0%} {bias:>+7.0%}")


if __name__ == '__main__':
    import time
    ts = time.strftime('%Y%m%d_%H%M%S')
    
    # Start with just our known targets (U=1-3)
    print("Starting ALCDEF validation...")
    df = run_alcdef_validation(KNOWN_TARGETS)
    
    csv_path = os.path.join(OUTPUT_DIR, f'alcdef_validation_{ts}.csv')
    df.to_csv(csv_path, index=False)
    print(f"\nSaved: {csv_path}")
    
    if df.empty:
        print('No sessions processed. Set ALCDEF_DIR to the folder containing ALCDEF_*.txt files.')
        sys.exit(1)
    print_validation_summary(df)
    
    # List sessions with largest model-reality gap
    print("\n" + "=" * 60)
    print("LARGEST MODEL-DATA GAPS")
    print("=" * 60)
    df['gap'] = df['ls_ok'] - df['model_P_period']
    for _, row in df.sort_values('gap', ascending=False).head(10).iterrows():
        print(f"  {row['target']:>20s} cov={row['coverage']:.0%} "
              f"n={int(row['n_points']):>4d} ls_ok={row['ls_ok']} "
              f"pred={row['model_P_period']:.0%} gap={row['gap']:+.0%}")
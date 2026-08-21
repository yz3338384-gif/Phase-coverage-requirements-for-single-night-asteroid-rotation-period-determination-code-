"""
56-target real-data validation (32 clean + 24 expansion).
Per-session LS recovery vs coverage -> upgraded Table 2.
"""
import os
import sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import numpy as np
import pandas as pd
from experiments.alcdef_validation import (parse_alcdef, split_sessions,
                                           ALCDEF_DIR)
from experiments.final_targets_56 import FINAL_TARGETS_56

OUTPUT_DIR = os.path.join(ROOT, 'output', 'validation')
os.makedirs(OUTPUT_DIR, exist_ok=True)

from core.obs_simulator import compute_coverage
from core.period_searcher import search as ls_search


def validate_target(name, info):
    path = os.path.join(ALCDEF_DIR, f'ALCDEF_{name}.txt')
    if not os.path.exists(path):
        return []
    P_true = info['P_h']
    meta, jd, mag, mag_err = parse_alcdef(path)
    sessions = split_sessions(jd, mag, mag_err, gap_hours=12)
    rows = []
    for i, sess in enumerate(sessions):
        times_h = (sess['jd'] - sess['jd'][0]) * 24.0
        phase = (times_h % P_true) / P_true
        cov = compute_coverage(phase)
        try:
            r = ls_search(times_h, sess['mag'],
                          period_min=P_true*0.3, period_max=P_true*3.0)
            P_ls = r.best_period
            ok = int(abs(P_ls - P_true)/P_true < 0.20)
        except Exception:
            P_ls, ok = -1, 0
        rows.append(dict(target=name, session_id=i, n_points=len(sess['mag']),
                         coverage=cov, P_true=P_true, P_ls=P_ls, ls_ok=ok,
                         U=info['U'], set_='expansion' if name in
                         __import__('experiments.final_targets_56',
                                    fromlist=['EXPANSION_TARGETS']).EXPANSION_TARGETS
                         else 'original'))
    return rows


all_rows = []
for name, info in FINAL_TARGETS_56.items():
    rows = validate_target(name, info)
    all_rows.extend(rows)
    if rows:
        n_sess = len(rows)
        n_ok = sum(r['ls_ok'] for r in rows)
        print(f"  {name:<26s} U={info['U']} sessions={n_sess:3d} ls_ok={n_ok:3d} ({n_ok/max(n_sess,1):5.1%})")

df = pd.DataFrame(all_rows)
out = os.path.join(OUTPUT_DIR, f'alcdef_validation_56targets_{pd.Timestamp.now():%Y%m%d_%H%M%S}.csv')
df.to_csv(out, index=False)
print(f"\nSaved: {out}")
print(f"Total sessions: {len(df)} | targets: {df.target.nunique()}")

print("\n=== LS success by coverage (56 targets, U>=2 only) ===")
bins = [0, 0.10, 0.20, 0.25, 0.35, 0.50, 1.01]
labels = ['<10%', '10-20%', '20-25%', '25-35%', '35-50%', '>50%']
u2 = df[df.U >= 2]
print(f"{'Coverage':>8s} {'n':>5s} {'ls_ok':>8s}  (all: n / rate)")
for i in range(len(bins)-1):
    sub = u2[(u2.coverage >= bins[i]) & (u2.coverage < bins[i+1])]
    sub_all = df[(df.coverage >= bins[i]) & (df.coverage < bins[i+1])]
    if len(sub):
        print(f"  [{labels[i]:>6s}] {len(sub):5d} {sub.ls_ok.mean():8.1%}  (all: {len(sub_all):4d} / {sub_all.ls_ok.mean():5.1%})")

print("\n=== Original 32 vs expansion 24 (independent P1 check) ===")
for sname in ['original', 'expansion']:
    sub = df[df.set_ == sname]
    print(f"\n--- {sname} ({sub.target.nunique()} targets, {len(sub)} sessions) ---")
    for i in range(len(bins)-1):
        b = sub[(sub.coverage >= bins[i]) & (sub.coverage < bins[i+1])]
        if len(b):
            print(f"  [{labels[i]:>6s}] n={len(b):4d} ls_ok={b.ls_ok.mean():6.1%}")

print("\n=== By U quality ===")
for u in sorted(df.U.unique()):
    sub = df[df.U == u]
    print(f"  U={u}: n={len(sub)} ls_ok={sub.ls_ok.mean():.1%}")

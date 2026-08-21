"""Heatmap: recovery rate as function of (coverage x amplitude), 3 periods."""
import os
import sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams.update({'font.size': 13, 'axes.labelsize': 14, 'axes.titlesize': 14, 'xtick.labelsize': 11, 'ytick.labelsize': 11, 'legend.fontsize': 12})

df = pd.read_csv(os.path.join(ROOT, 'output', 'final_experiments', 'amp_scan_20260813.csv'))

amps = sorted(df['amplitude_mag'].unique())
coves = sorted(df['coverage'].unique())
periods = sorted(df['period_h'].unique())

# Summary table printout
print("===== KEY THRESHOLDS (C where rate >= 0.5 first reached, by amp & P) =====")
for P in periods:
    sub = df[df['period_h'] == P]
    for amp in amps:
        s = sub[sub['amplitude_mag'] == amp].sort_values('coverage')
        reach = s[s['recovery_rate'] >= 0.5]
        c50 = reach['coverage'].min() if len(reach) else None
        r75 = s[s['coverage'] == 0.75]['recovery_rate'].values
        r75 = r75[0] if len(r75) else None
        print(f"P={P}h amp={amp:.2f}: C>=50% first at {c50}, rate@C=75% = {r75:.3f}" if r75 is not None else f"P={P}h amp={amp:.2f}: never>=50%, rate@C=75% = {r75}")

# Pivot per period
fig, axes = plt.subplots(1, 3, figsize=(15, 4.2), sharey=True)
for ax, P in zip(axes, periods):
    sub = df[df['period_h'] == P]
    piv = sub.pivot(index='amplitude_mag', columns='coverage', values='recovery_rate')
    im = ax.imshow(piv.values, aspect='auto', origin='lower', cmap='inferno',
                   extent=[coves[0], coves[-1], amps[0], amps[-1]], vmin=0, vmax=1)
    ax.set_title(f'P = {P} h')
    ax.set_xlabel('Phase coverage C')
    ax.set_ylabel('Amplitude (mag)')
    ax.set_xticks(coves)
    ax.set_yticks(amps)
    # contour at 0.5
    X, Y = np.meshgrid(coves, amps)
    Z = piv.values
    cs = ax.contour(X, Y, Z, levels=[0.3, 0.5, 0.7], colors='w', linewidths=1.4)
    ax.clabel(cs, fmt='%.1f', fontsize=10)
fig.colorbar(im, ax=axes, orientation='vertical', shrink=0.85, label='Recovery rate')
fig.suptitle('Single-night LS period recovery rate (K_true=4, noise=0.02 mag, 5-min cadence)', fontsize=11)
plt.tight_layout(rect=[0, 0, 1, 0.93])
out = os.path.join(ROOT, 'paper', 'figures', 'amp_scan_heatmap.png')
os.makedirs(os.path.dirname(out), exist_ok=True)
plt.savefig(out, dpi=300, bbox_inches='tight')
print("Saved:", out)

# Also a coverage-recovery curve figure per amplitude for P=12h (for the paper)
plt.figure(figsize=(7, 5))
sub = df[df['period_h'] == 12]
for amp in amps:
    s = sub[sub['amplitude_mag'] == amp].sort_values('coverage')
    plt.plot(s['coverage'], s['recovery_rate'], 'o-', lw=1.8, ms=6, label=f'A = {amp:.2f} mag')
plt.axvline(0.25, color='k', ls='--', lw=1.2, alpha=0.6)
plt.text(0.255, 0.9, 'C = 0.25', fontsize=11)
plt.xlabel('Phase coverage C')
plt.ylabel('Period recovery rate')
plt.title('P = 12 h, sigma = 0.02 mag')
plt.legend(fontsize=10)
plt.grid(alpha=0.3)
out2 = os.path.join(ROOT, 'paper', 'figures', 'amp_scan_curves_p12.png')
plt.savefig(out2, dpi=300, bbox_inches='tight')
print("Saved:", out2)

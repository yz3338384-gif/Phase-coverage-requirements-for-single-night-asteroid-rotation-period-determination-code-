"""Figure 2: real-data coverage-recovery curve (56 targets, 2166 sessions) + simulation comparison."""
import os
import sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams.update({'font.size': 13, 'axes.labelsize': 14, 'xtick.labelsize': 12, 'ytick.labelsize': 12, 'legend.fontsize': 12})

# v10 Table 1 (56 targets, U>=2 subset)
bins = ['<10%', '10-20%', '20-25%', '25-35%', '35-50%', '>50%']
centers = [0.05, 0.15, 0.225, 0.30, 0.425, 0.60]
rates = [0.001, 0.070, 0.048, 0.087, 0.112, 0.167]
ns = [869, 285, 166, 253, 224, 294]

# simulation (P=12h, averaged over amplitudes) at comparable nominal coverage
sim_c = [0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50, 0.60, 0.75]
import pandas as pd
df = pd.read_csv(os.path.join(ROOT, 'output', 'final_experiments', 'amp_scan_20260813.csv'))
sub = df[df['period_h'] == 12].groupby('coverage')['recovery_rate'].mean()

fig, ax = plt.subplots(figsize=(7, 5))
ax.errorbar(centers, rates, yerr=[1.96*np.sqrt(r*(1-r)/n) for r, n in zip(rates, ns)],
            fmt='o-', color='C0', lw=2, ms=7, capsize=5, label='Real ALCDEF (56 targets, 2166 sessions)')
ax.plot(sim_c, [sub[c] for c in sim_c], 's--', color='C1', lw=2, ms=7, label='Simulation (P=12 h, avg over amplitudes)')
ax.axvline(0.25, color='k', ls=':', lw=1.5)
ax.text(0.255, 0.42, 'C = 0.25', fontsize=11)
ax.set_xlabel('Phase coverage C')
ax.set_ylabel('Period recovery rate')
ax.set_ylim(0, 0.55)
ax.grid(alpha=0.3)
ax.legend(fontsize=11)
plt.tight_layout()
out = os.path.join(ROOT, 'paper', 'figures', 'real_vs_sim.png')
plt.savefig(out, dpi=300, bbox_inches='tight')
print('Saved:', out)

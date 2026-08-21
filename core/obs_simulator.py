"""
Module 2: Observation Simulator
================================
Simulate realistic observations: sample a truth curve, add noise, 
handle single/multi-night and missing points.
"""
import numpy as np
from dataclasses import dataclass, field
from typing import List, Optional
from core.truth_generator import generate_standard


@dataclass
class NightConfig:
    """Configuration for one night of observation."""
    duration_h: float          # hours of observation
    sampling_interval_min: float  # minutes between exposures
    noise_sigma_mag: float     # measurement noise (mag)
    drop_rate: float = 0.0     # fraction of points randomly dropped


@dataclass
class SimConfig:
    """Full simulation configuration."""
    period_h: float            # asteroid rotation period (hours)
    K_true: int                # true Fourier order
    amplitude: float = 0.3     # light curve half-amplitude (mag)
    nights: List[NightConfig] = field(default_factory=list)
    seed: int = 42
    phase_offset: Optional[float] = None  # random if None


def simulate(config: SimConfig) -> dict:
    """
    Run one simulation.
    
    Returns dict with keys:
        times_h, mag, mag_err, phase, night_id, 
        true_mag, coverage, n_data, n_eff
    """
    rng = np.random.default_rng(config.seed)
    
    # Determine phase offset
    if config.phase_offset is not None:
        phi0 = config.phase_offset
    else:
        phi0 = rng.uniform(0, config.period_h)
    
    all_t = []
    all_mag = []
    all_err = []
    all_night = []
    all_phase = []
    
    for night_idx, night in enumerate(config.nights):
        n_points = int(night.duration_h * 60 / night.sampling_interval_min)
        if n_points < 5:
            n_points = 5
        
        # Generate observation times within this night
        t_start = phi0 + night_idx * 1000  # nights separated by ~1000h
        times = t_start + np.sort(rng.uniform(0, night.duration_h, n_points))
        
        # Random drop
        if night.drop_rate > 0:
            keep = rng.uniform(size=n_points) > night.drop_rate
            times = times[keep]
            if len(times) < 3:
                continue
        
        # Phase folding
        phase = (times % config.period_h) / config.period_h
        
        # True magnitude
        true_mag = generate_standard(phase, config.K_true, config.amplitude)
        
        # Add noise
        err = np.full(len(times), night.noise_sigma_mag)
        observed = true_mag + rng.normal(0, night.noise_sigma_mag, len(times))
        
        all_t.append(times)
        all_mag.append(observed)
        all_err.append(err)
        all_night.append(np.full(len(times), night_idx))
        all_phase.append(phase)
    
    if not all_t:
        raise ValueError("No data points after simulation")
    
    return {
        'times_h': np.concatenate(all_t),
        'mag': np.concatenate(all_mag),
        'mag_err': np.concatenate(all_err),
        'night_id': np.concatenate(all_night),
        'phase': np.concatenate(all_phase),
        'n_data': sum(len(t) for t in all_t),
    }


def compute_coverage(phase: np.ndarray, n_bins: int = 100) -> float:
    """Compute phase coverage as fraction of occupied bins."""
    bins = np.linspace(0, 1, n_bins + 1)
    hist, _ = np.histogram(phase, bins=bins)
    return float(np.sum(hist > 0) / n_bins)


def make_single_night(period_h: float, K_true: int,
                      duration_h: float, interval_min: float,
                      sigma: float, amplitude: float = 0.3,
                      seed: int = 42) -> dict:
    """Convenience: single night simulation."""
    config = SimConfig(
        period_h=period_h,
        K_true=K_true,
        amplitude=amplitude,
        nights=[NightConfig(duration_h, interval_min, sigma)],
        seed=seed
    )
    result = simulate(config)
    result['coverage'] = compute_coverage(result['phase'])
    result['config'] = config
    return result

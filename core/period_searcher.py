"""
Module 3: Period Searcher (v2 ??astropy)
=========================================
Lomb-Scargle periodogram with:
- astropy.timeseries.LombScargle (more accurate than scipy)
- Wide search range [0.2*P, 5*P]
- False Alarm Probability for significance
- Harmonic checking (2:1, 3:1, 1:2)
- Automatic frequency grid
"""
import numpy as np
from dataclasses import dataclass
from typing import List, Optional

try:
    from astropy.timeseries import LombScargle
    HAS_ASTROPY = True
except ImportError:
    HAS_ASTROPY = False
    # Fallback: use our improved scipy version
    from scipy import signal


@dataclass
class PeriodSearchResult:
    best_period: float
    best_power: float
    periodogram_periods: np.ndarray
    periodogram_power: np.ndarray
    n_peaks: int
    top_periods: List[float]
    top_powers: List[float]
    period_error: float
    fap_best: float                # false alarm probability of best peak
    harmonic_of_true: bool = False # True if best peak is a harmonic of true period


def search(times_h, mag,
           period_min=1.0, period_max=100.0,
           autofreq=True, samples_per_peak=10,
           fap_level=0.01):
    """
    Lomb-Scargle period search using astropy (or scipy fallback).
    
    Parameters
    ----------
    times_h : array
        Observation times in hours.
    mag : array
        Observed magnitudes.
    period_min, period_max : float
        Search range in hours.
    autofreq : bool
        Use astropy's automatic frequency grid (if available).
    samples_per_peak : int
        Resolution control (used for manual grid if autofreq=False).
    fap_level : float
        False alarm probability threshold for peak significance.
    
    Returns
    -------
    PeriodSearchResult
    """
    # Normalize
    mag_norm = mag - np.mean(mag)
    t_days = times_h / 24.0  # astropy works in days
    
    # Frequency range: cycles per day
    f_min = 1.0 / (period_max / 24.0)  # cycles per day
    f_max = 1.0 / (period_min / 24.0)  # cycles per day
    
    if HAS_ASTROPY and autofreq:
        # === Astropy LS with automatic frequency grid ===
        # The 'autofreq' method uses the data's time-span to 
        # determine optimal frequency spacing
        ls = LombScargle(t_days, mag_norm, normalization='psd')
        
        # Use automatic frequency grid
        # This gives ~Nyquist sampling in frequency
        frequency, power = ls.autopower(
            minimum_frequency=f_min,
            maximum_frequency=f_max,
            samples_per_peak=samples_per_peak
        )
        
        periods_h = 24.0 / frequency
        
        # FAP for best peak
        best_idx = np.argmax(power)
        best_fap = ls.false_alarm_probability(power[best_idx], 
                                               method='baluev',
                                               minimum_frequency=f_min,
                                               maximum_frequency=f_max)
        
    else:
        # === Fallback: manual frequency grid with scipy ===
        # More frequencies for better resolution
        n_freq = max(2000, min(50000, 
                     int((f_max - f_min) / (f_min / samples_per_peak))))
        
        # Use angular frequency for scipy
        omega = np.linspace(2*np.pi*f_min, 2*np.pi*f_max, n_freq)
        power = signal.lombscargle(t_days, mag_norm, omega)
        periods_h = 24.0 * 2 * np.pi / omega
        best_fap = -1  # not available without astropy
    
    # ============================================================
    # Peak detection
    # ============================================================
    # Find all local maxima
    peaks_idx = []
    for i in range(1, len(power)-1):
        if power[i] > power[i-1] and power[i] > power[i+1]:
            peaks_idx.append(i)
    
    # Also add global max if no peaks found
    if not peaks_idx:
        best_idx = np.argmax(power)
        P_est = periods_h[best_idx]
        med = np.median(power)
        return PeriodSearchResult(
            best_period=P_est,
            best_power=power[best_idx],
            periodogram_periods=periods_h,
            periodogram_power=power,
            n_peaks=1,
            top_periods=[P_est],
            top_powers=[power[best_idx]],
            period_error=0,
            fap_best=best_fap
        )
    
    # Sort peaks by power descending
    peak_powers = power[peaks_idx]
    peak_order = np.argsort(peak_powers)[::-1]
    
    # Take top peaks (limit to 10 to avoid noise peaks)
    n_top = min(len(peaks_idx), 10)
    top_indices = [peaks_idx[peak_order[i]] for i in range(n_top)]
    top_periods_raw = periods_h[top_indices]
    top_powers_list = power[top_indices]
    
    # ============================================================
    # Harmonic checker
    # ============================================================
    # If the true period is known to be in range, we check:
    # If top peak is at 2x, 3x, or 0.5x of another significant peak
    # This helps identify aliases
    final_periods = [top_periods_raw[0]]
    final_powers = [top_powers_list[0]]
    
    for i in range(min(len(top_periods_raw), 5)):
        p = top_periods_raw[i]
        # Check against already-included periods
        is_harmonic = False
        for included_p in final_periods:
            ratio = max(p, included_p) / min(p, included_p)
            if abs(ratio - 2) < 0.15 or abs(ratio - 3) < 0.15 or abs(ratio - 0.5) < 0.15:
                is_harmonic = True
                break
        if not is_harmonic:
            final_periods.append(p)
            final_powers.append(top_powers_list[i])
    
    # ============================================================
    # Estimate period error from peak width
    # ============================================================
    main_idx = np.argmax(power)
    # Find the FWHM of the main peak in period space
    half_max = power[main_idx] / 2
    left = main_idx
    while left > 0 and power[left] > half_max:
        left -= 1
    right = main_idx
    while right < len(power) - 1 and power[right] > half_max:
        right += 1
    
    if right > left + 1:
        # Convert FWHM from index to period width
        p_left = periods_h[left] if left < main_idx else periods_h[0]
        p_right = periods_h[right] if right > main_idx else periods_h[-1]
        period_width = abs(p_right - p_left)
    else:
        period_width = 0.0
    
    return PeriodSearchResult(
        best_period=final_periods[0],
        best_power=final_powers[0],
        periodogram_periods=periods_h,
        periodogram_power=power,
        n_peaks=len(final_periods),
        top_periods=final_periods[:5],
        top_powers=final_powers[:5],
        period_error=period_width,
        fap_best=best_fap
    )

"""
Module 1: Truth Light Curve Generator
=======================================
Generate noise-free true light curves with known Fourier parameters.
"""
import numpy as np

# Standardized coefficient sets for reproducibility
_COEFF_SETS = {
    2: {'a': [0.20, 0.08], 'b': [0.10, -0.05]},
    4: {'a': [0.20, 0.08, 0.04, 0.02], 'b': [0.10, -0.05, 0.03, -0.01]},
    6: {'a': [0.20, 0.10, 0.06, 0.03, 0.02, 0.01],
        'b': [0.10, -0.05, 0.04, -0.02, 0.01, -0.008]},
    8: {'a': [0.20, 0.12, 0.08, 0.05, 0.03, 0.02, 0.015, 0.01],
        'b': [0.10, -0.06, 0.05, -0.03, 0.02, -0.015, 0.01, -0.005]},
}


def generate_standard(phase: np.ndarray, K_true: int,
                      amplitude: float = 0.3) -> np.ndarray:
    """
    Generate a standardized truth light curve with reproducible coefficients.
    
    Parameters
    ----------
    phase : np.ndarray
        Phase values in [0, 1).
    K_true : int
        True Fourier order (2, 4, 6, or 8).
    amplitude : float
        Desired half-amplitude in magnitudes.
    
    Returns
    -------
    mag : np.ndarray
        True magnitude values.
    """
    cs = _COEFF_SETS.get(K_true, _COEFF_SETS[2])
    mag = np.zeros_like(phase, dtype=float)
    for k in range(K_true):
        mag += cs['a'][k] * np.cos(2 * np.pi * (k+1) * phase)
        mag += cs['b'][k] * np.sin(2 * np.pi * (k+1) * phase)
    
    # Normalize to target amplitude
    current = (np.max(mag) - np.min(mag)) / 2
    if current > 0:
        mag *= amplitude / current
    
    return mag


def generate_random(phase: np.ndarray, K_true: int,
                    amplitude: float = 0.3,
                    rng: np.random.Generator = None) -> tuple:
    """
    Generate a random truth light curve. Coefficients decay with order.
    
    Returns
    -------
    mag : np.ndarray
    params : dict
        The a_k, b_k coefficients used.
    """
    if rng is None:
        rng = np.random.default_rng()
    
    a = np.zeros(K_true)
    b = np.zeros(K_true)
    
    for k in range(K_true):
        scale = amplitude * (0.5 ** k)  # exponential decay
        a[k] = rng.uniform(-scale, scale)
        b[k] = rng.uniform(-scale, scale)
    
    mag = np.zeros_like(phase, dtype=float)
    for k in range(K_true):
        mag += a[k] * np.cos(2 * np.pi * (k+1) * phase)
        mag += b[k] * np.sin(2 * np.pi * (k+1) * phase)
    
    current = (np.max(mag) - np.min(mag)) / 2
    if current > 0:
        mag *= amplitude / current
    
    return mag, {'a': a.tolist(), 'b': b.tolist()}


def evaluate_rms(true_curve: np.ndarray, fit_curve: np.ndarray) -> float:
    """Compute RMSE between true and fitted curves, correcting offset."""
    offset = np.mean(fit_curve) - np.mean(true_curve)
    return float(np.sqrt(np.mean((fit_curve - offset - true_curve)**2)))


_FINE_PHASE = np.linspace(0, 1, 1000)


def get_fine_curve(K_true: int, amplitude: float = 0.3) -> np.ndarray:
    """Get a high-resolution truth curve for validation."""
    return generate_standard(_FINE_PHASE, K_true, amplitude)

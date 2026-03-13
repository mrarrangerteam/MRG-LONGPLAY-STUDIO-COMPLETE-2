"""Shared test fixtures for LongPlay Studio tests."""
import sys
import os
import numpy as np
import pytest

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def sine_stereo():
    """Generate 1 second of 440Hz stereo sine at -6dBFS, 44100Hz."""
    sr = 44100
    t = np.arange(sr, dtype=np.float32) / sr
    amplitude = 0.5  # -6 dBFS
    left = np.sin(2 * np.pi * 440 * t) * amplitude
    right = np.sin(2 * np.pi * 440 * t + 0.3) * amplitude
    return np.stack([left, right]), sr


@pytest.fixture
def multi_freq_stereo():
    """Generate stereo signal with 100Hz + 1kHz + 8kHz components."""
    sr = 44100
    t = np.arange(sr, dtype=np.float32) / sr
    signal = (np.sin(2 * np.pi * 100 * t) +
              np.sin(2 * np.pi * 1000 * t) +
              np.sin(2 * np.pi * 8000 * t)) * 0.15
    return np.stack([signal, signal.copy()]), sr


@pytest.fixture
def silence_stereo():
    """Generate 1 second of stereo silence."""
    sr = 44100
    return np.zeros((2, sr), dtype=np.float32), sr


@pytest.fixture
def loud_stereo():
    """Generate 1 second of near-0dBFS stereo sine."""
    sr = 44100
    t = np.arange(sr, dtype=np.float32) / sr
    signal = np.sin(2 * np.pi * 440 * t) * 0.95
    return np.stack([signal, signal.copy()]), sr


@pytest.fixture
def noise_stereo():
    """Generate 1 second of stereo pink-ish noise."""
    sr = 44100
    rng = np.random.default_rng(42)
    noise = rng.standard_normal((2, sr)).astype(np.float32) * 0.3
    return noise, sr

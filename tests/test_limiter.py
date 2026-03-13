"""Tests for the LookAheadLimiter module."""
import numpy as np
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules.master.limiter import LookAheadLimiter


class TestLimiter:
    def test_init(self):
        lim = LookAheadLimiter()
        assert lim is not None
        assert lim.ceiling_db == -1.0
        assert lim.ceiling_linear == pytest.approx(10 ** (-1.0 / 20.0), rel=1e-4)

    def test_init_custom_ceiling(self):
        lim = LookAheadLimiter(ceiling_db=-6.0)
        assert lim.ceiling_db == -6.0
        assert lim.ceiling_linear == pytest.approx(10 ** (-6.0 / 20.0), rel=1e-4)

    def test_set_ceiling(self):
        lim = LookAheadLimiter()
        lim.set_ceiling(-3.0)
        assert lim.ceiling_db == -3.0
        assert lim.ceiling_linear == pytest.approx(10 ** (-3.0 / 20.0), rel=1e-4)

    def test_set_release(self):
        lim = LookAheadLimiter()
        lim.set_release(200.0)
        assert lim.release_ms == 200.0

    def test_set_release_clamped(self):
        lim = LookAheadLimiter()
        lim.set_release(1.0)
        assert lim.release_ms == 5.0
        lim.set_release(1000.0)
        assert lim.release_ms == 500.0

    def test_ceiling_enforcement(self, loud_stereo):
        """Limiter should prevent peaks from exceeding ceiling."""
        audio, sr = loud_stereo
        # Transpose from (2, samples) to (samples, 2) for limiter API
        audio_t = audio.T.astype(np.float64)

        lim = LookAheadLimiter(ceiling_db=-6.0)
        output = lim.process(audio_t, sr)

        ceiling_linear = 10.0 ** (-6.0 / 20.0)
        output_peak = np.max(np.abs(output))
        assert output_peak <= ceiling_linear + 0.05, (
            f"Peak {output_peak:.4f} > ceiling {ceiling_linear:.4f}"
        )

    def test_silence_stays_silent(self, silence_stereo):
        audio, sr = silence_stereo
        audio_t = audio.T.astype(np.float64)

        lim = LookAheadLimiter(ceiling_db=-6.0)
        output = lim.process(audio_t, sr)
        assert np.max(np.abs(output)) < 0.001

    def test_quiet_signal_passes_through(self, sine_stereo):
        """Signal well below ceiling should pass through mostly unchanged."""
        audio, sr = sine_stereo
        # sine_stereo is at -6 dBFS, set ceiling at -1 dBFS => no limiting needed
        audio_t = audio.T.astype(np.float64)

        lim = LookAheadLimiter(ceiling_db=-1.0)
        output = lim.process(audio_t, sr)

        # Output should be very close to input (allowing for look-ahead delay)
        assert output.shape == audio_t.shape

    def test_no_nan(self, noise_stereo):
        audio, sr = noise_stereo
        audio_t = audio.T.astype(np.float64)

        lim = LookAheadLimiter(ceiling_db=-3.0)
        output = lim.process(audio_t, sr)
        assert not np.any(np.isnan(output))
        assert not np.any(np.isinf(output))

    def test_mono_input(self):
        """Limiter should handle mono (1D) input."""
        sr = 44100
        t = np.arange(sr, dtype=np.float64) / sr
        mono = np.sin(2 * np.pi * 440 * t) * 0.95

        lim = LookAheadLimiter(ceiling_db=-6.0)
        output = lim.process(mono, sr)
        assert output.ndim == 1
        ceiling_linear = 10.0 ** (-6.0 / 20.0)
        assert np.max(np.abs(output)) <= ceiling_linear + 0.05

    def test_gain_reduction_tracking(self, loud_stereo):
        """After processing, gain reduction should be tracked."""
        audio, sr = loud_stereo
        audio_t = audio.T.astype(np.float64)

        lim = LookAheadLimiter(ceiling_db=-6.0)
        lim.process(audio_t, sr)
        gr = lim.last_gain_reduction_db
        # Loud signal with -6 dB ceiling should have negative GR
        assert gr < 0.0, f"Expected negative gain reduction, got {gr}"

    def test_empty_audio(self):
        """Limiter should handle empty arrays gracefully."""
        lim = LookAheadLimiter()
        empty = np.array([], dtype=np.float64)
        output = lim.process(empty, 44100)
        assert output.size == 0

    def test_output_shape_preserved(self, sine_stereo):
        audio, sr = sine_stereo
        audio_t = audio.T.astype(np.float64)  # (samples, 2)

        lim = LookAheadLimiter()
        output = lim.process(audio_t, sr)
        assert output.shape == audio_t.shape

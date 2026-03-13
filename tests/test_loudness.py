"""Tests for the Loudness module."""
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules.master.loudness import LoudnessMeter, LoudnessAnalysis


class TestLoudnessAnalysis:
    def test_init_defaults(self):
        analysis = LoudnessAnalysis()
        assert hasattr(analysis, 'integrated_lufs')
        assert hasattr(analysis, 'true_peak_dbtp')
        assert hasattr(analysis, 'lra')
        assert analysis.integrated_lufs == -24.0
        assert analysis.true_peak_dbtp == -6.0
        assert analysis.lra == 0.0

    def test_additional_fields(self):
        analysis = LoudnessAnalysis()
        assert hasattr(analysis, 'input_i')
        assert hasattr(analysis, 'input_tp')
        assert hasattr(analysis, 'input_lra')
        assert hasattr(analysis, 'duration_sec')
        assert hasattr(analysis, 'sample_rate')
        assert hasattr(analysis, 'channels')

    def test_to_dict(self):
        analysis = LoudnessAnalysis()
        analysis.integrated_lufs = -14.0
        analysis.true_peak_dbtp = -1.0
        analysis.lra = 7.0
        d = analysis.to_dict()
        assert isinstance(d, dict)
        assert d["integrated_lufs"] == -14.0
        assert d["true_peak_dbtp"] == -1.0
        assert d["lra"] == 7.0

    def test_meets_target_youtube(self):
        analysis = LoudnessAnalysis()
        analysis.integrated_lufs = -14.0
        analysis.true_peak_dbtp = -1.0
        result = analysis.meets_target("YouTube")
        assert isinstance(result, dict)
        assert result["passes"] is True
        assert result["platform"] == "YouTube"

    def test_meets_target_fails(self):
        analysis = LoudnessAnalysis()
        analysis.integrated_lufs = -8.0  # Too loud
        analysis.true_peak_dbtp = 0.5    # Over true peak limit
        result = analysis.meets_target("YouTube")
        assert result["passes"] is False

    def test_meets_target_spotify(self):
        analysis = LoudnessAnalysis()
        analysis.integrated_lufs = -14.0
        analysis.true_peak_dbtp = -1.0
        result = analysis.meets_target("Spotify")
        assert result["passes"] is True

    def test_meets_target_apple_music(self):
        analysis = LoudnessAnalysis()
        analysis.integrated_lufs = -16.0
        analysis.true_peak_dbtp = -1.0
        result = analysis.meets_target("Apple Music")
        assert result["passes"] is True


class TestLoudnessMeter:
    def test_init(self):
        meter = LoudnessMeter()
        assert meter is not None
        assert meter.ffmpeg_path == "ffmpeg"

    def test_init_custom_path(self):
        meter = LoudnessMeter(ffmpeg_path="/usr/local/bin/ffmpeg")
        assert meter.ffmpeg_path == "/usr/local/bin/ffmpeg"

    def test_analyze_nonexistent_file(self):
        meter = LoudnessMeter()
        result = meter.analyze("/nonexistent/path/audio.wav")
        assert result is None

    def test_quick_measure_nonexistent_file(self):
        meter = LoudnessMeter()
        result = meter.quick_measure("/nonexistent/path/audio.wav")
        assert result is None

    def test_get_loudnorm_filter(self):
        meter = LoudnessMeter()
        analysis = LoudnessAnalysis()
        analysis.input_i = -18.0
        analysis.input_lra = 8.0
        analysis.input_tp = -2.0
        analysis.input_thresh = -28.0
        analysis.target_offset_lu = 0.0

        filter_str = meter.get_loudnorm_filter(analysis, target_lufs=-14.0)
        assert "loudnorm" in filter_str
        assert "measured_I=-18.0" in filter_str
        assert "I=-14" in filter_str
        assert "linear=true" in filter_str

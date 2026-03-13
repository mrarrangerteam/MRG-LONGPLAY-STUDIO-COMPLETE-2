"""Tests for the Maximizer module."""
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules.master.maximizer import Maximizer


class TestMaximizer:
    def test_init(self):
        m = Maximizer()
        assert m is not None
        assert m.enabled is True
        assert m.gain_db == 0.0
        assert m.ceiling == -1.0
        assert m.irc_mode == "IRC 4"
        assert m.true_peak is True

    def test_set_gain(self):
        m = Maximizer()
        m.set_gain(6.0)
        assert m.gain_db == 6.0

    def test_set_gain_clamped(self):
        m = Maximizer()
        m.set_gain(25.0)
        assert m.gain_db == 20.0
        m.set_gain(-5.0)
        assert m.gain_db == 0.0

    def test_set_ceiling(self):
        m = Maximizer()
        m.set_ceiling(-0.5)
        assert m.ceiling == -0.5

    def test_set_ceiling_clamped(self):
        m = Maximizer()
        m.set_ceiling(-5.0)
        assert m.ceiling == -3.0
        m.set_ceiling(0.0)
        assert m.ceiling == -0.1

    def test_set_character(self):
        m = Maximizer()
        m.set_character(7.0)
        assert m.character == 7.0

    def test_set_character_clamped(self):
        m = Maximizer()
        m.set_character(15.0)
        assert m.character == 10.0
        m.set_character(-1.0)
        assert m.character == 0.0

    def test_set_irc_mode(self):
        m = Maximizer()
        m.set_irc_mode("IRC 3", "Balanced")
        assert m.irc_mode == "IRC 3"
        assert m.irc_sub_mode == "Balanced"

    def test_set_irc_mode_legacy(self):
        m = Maximizer()
        m.set_irc_mode("IRC IV")
        assert m.irc_mode == "IRC 4"

    def test_set_upward_compress(self):
        m = Maximizer()
        m.set_upward_compress(6.0)
        assert m.upward_compress_db == 6.0
        m.set_upward_compress(20.0)
        assert m.upward_compress_db == 12.0

    def test_set_soft_clip(self):
        m = Maximizer()
        m.set_soft_clip(True, 50)
        assert m.soft_clip_enabled is True
        assert m.soft_clip_pct == 50

    def test_set_transient_emphasis(self):
        m = Maximizer()
        m.set_transient_emphasis(60, "H")
        assert m.transient_emphasis_pct == 60
        assert m.transient_band == "H"

    def test_set_stereo_independence(self):
        m = Maximizer()
        m.set_stereo_independence(40, 60)
        assert m.stereo_ind_transient == 40
        assert m.stereo_ind_sustain == 60

    def test_get_ffmpeg_filters_default(self):
        m = Maximizer()
        filters = m.get_ffmpeg_filters()
        assert isinstance(filters, list)
        # Default: gain=0, so minimal filters, but limiter always present
        assert any("alimiter" in f for f in filters)

    def test_get_ffmpeg_filters_with_gain(self):
        m = Maximizer()
        m.set_gain(6.0)
        filters = m.get_ffmpeg_filters()
        assert any("volume=" in f for f in filters)
        assert any("alimiter" in f for f in filters)

    def test_get_ffmpeg_filters_disabled(self):
        m = Maximizer()
        m.enabled = False
        assert m.get_ffmpeg_filters() == []

    def test_get_ffmpeg_filters_soft_clip(self):
        m = Maximizer()
        m.set_soft_clip(True, 50)
        filters = m.get_ffmpeg_filters()
        # Soft clip adds volume drive + alimiter + volume restore
        assert len(filters) >= 3

    def test_get_ffmpeg_filters_upward_compress(self):
        m = Maximizer()
        m.set_upward_compress(6.0)
        filters = m.get_ffmpeg_filters()
        assert any("acompressor" in f for f in filters)

    def test_get_ffmpeg_filters_transient_emphasis(self):
        m = Maximizer()
        m.set_transient_emphasis(60, "M")
        filters = m.get_ffmpeg_filters()
        assert any("equalizer" in f for f in filters)

    def test_get_ffmpeg_filters_transient_emphasis_high(self):
        m = Maximizer()
        m.set_transient_emphasis(60, "H")
        filters = m.get_ffmpeg_filters()
        assert any("highshelf" in f for f in filters)

    def test_character_affects_limiter(self):
        m = Maximizer()
        m.set_gain(6.0)
        m.set_character(0.0)  # Smooth
        smooth_filters = m.get_ffmpeg_filters()
        m.set_character(10.0)  # Aggressive
        aggressive_filters = m.get_ffmpeg_filters()
        # Both should produce limiter, but with different attack/release
        assert any("alimiter" in f for f in smooth_filters)
        assert any("alimiter" in f for f in aggressive_filters)

    def test_settings_roundtrip(self):
        m = Maximizer()
        m.set_gain(8.0)
        m.set_ceiling(-0.5)
        m.set_character(7.0)
        m.set_soft_clip(True, 30)
        settings = m.get_settings_dict()
        assert isinstance(settings, dict)

        m2 = Maximizer()
        m2.load_settings_dict(settings)
        assert abs(m2.gain_db - 8.0) < 0.01
        assert abs(m2.ceiling - (-0.5)) < 0.01
        assert abs(m2.character - 7.0) < 0.01
        assert m2.soft_clip_enabled is True
        assert m2.soft_clip_pct == 30

    def test_get_display_info(self):
        m = Maximizer()
        m.set_gain(6.0)
        info = m.get_display_info()
        assert "gain_db" in info
        assert "ceiling_dbtp" in info
        assert "irc_mode" in info

    def test_legacy_set_threshold(self):
        m = Maximizer()
        m.set_threshold(-10.0)
        assert m.gain_db == 10.0

    def test_repr(self):
        m = Maximizer()
        r = repr(m)
        assert "Maximizer" in r

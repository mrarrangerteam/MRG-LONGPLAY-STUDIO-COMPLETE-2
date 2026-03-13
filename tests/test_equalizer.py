"""Tests for the Equalizer module."""
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules.master.equalizer import Equalizer, EQBand, EQ_TONE_PRESETS


class TestEQBand:
    def test_default_band(self):
        band = EQBand()
        assert band.freq == 1000
        assert band.gain == 0.0
        assert band.width == 1.0
        assert band.band_type == "equalizer"
        assert band.enabled is True

    def test_custom_band(self):
        band = EQBand(freq=440, gain=3.0, width=2.0, band_type="lowshelf", enabled=False)
        assert band.freq == 440
        assert band.gain == 3.0
        assert band.width == 2.0
        assert band.band_type == "lowshelf"
        assert band.enabled is False

    def test_to_ffmpeg_filter_equalizer(self):
        band = EQBand(freq=1000, gain=3.0, width=1.0, band_type="equalizer")
        result = band.to_ffmpeg_filter()
        assert result is not None
        assert "equalizer" in result
        assert "f=1000" in result
        assert "g=3.0" in result

    def test_to_ffmpeg_filter_disabled(self):
        band = EQBand(freq=1000, gain=3.0, enabled=False)
        assert band.to_ffmpeg_filter() is None

    def test_to_ffmpeg_filter_zero_gain(self):
        band = EQBand(freq=1000, gain=0.0, band_type="equalizer")
        assert band.to_ffmpeg_filter() is None

    def test_to_ffmpeg_filter_highpass(self):
        band = EQBand(freq=80, band_type="highpass")
        result = band.to_ffmpeg_filter()
        assert result is not None
        assert "highpass" in result

    def test_to_ffmpeg_filter_lowpass(self):
        band = EQBand(freq=16000, band_type="lowpass")
        result = band.to_ffmpeg_filter()
        assert result is not None
        assert "lowpass" in result

    def test_to_ffmpeg_filter_shelves(self):
        low = EQBand(freq=200, gain=2.0, band_type="lowshelf")
        high = EQBand(freq=8000, gain=-1.5, band_type="highshelf")
        assert "lowshelf" in low.to_ffmpeg_filter()
        assert "highshelf" in high.to_ffmpeg_filter()

    def test_intensity_scaling(self):
        band = EQBand(freq=1000, gain=6.0, band_type="equalizer")
        full = band.to_ffmpeg_filter(intensity=1.0)
        half = band.to_ffmpeg_filter(intensity=0.5)
        assert "g=6.0" in full
        assert "g=3.0" in half

    def test_to_dict_from_dict_roundtrip(self):
        band = EQBand(freq=440, gain=-2.5, width=0.8, band_type="highshelf", enabled=False)
        d = band.to_dict()
        band2 = EQBand.from_dict(d)
        assert band2.freq == 440
        assert band2.gain == -2.5
        assert band2.width == 0.8
        assert band2.band_type == "highshelf"
        assert band2.enabled is False

    def test_valid_types(self):
        assert "equalizer" in EQBand.TYPES
        assert "lowshelf" in EQBand.TYPES
        assert "highshelf" in EQBand.TYPES
        assert "highpass" in EQBand.TYPES
        assert "lowpass" in EQBand.TYPES


class TestEqualizerBasic:
    def test_init_default(self):
        eq = Equalizer()
        assert eq is not None
        assert len(eq.bands) == 8
        assert eq.enabled is True
        assert eq.preset_mode is True
        assert eq.current_preset == "Flat"

    def test_default_bands_flat(self):
        eq = Equalizer()
        for band in eq.bands:
            assert band.gain == 0.0

    def test_num_bands_constant(self):
        assert Equalizer.NUM_BANDS == 8

    def test_default_freqs_span_spectrum(self):
        eq = Equalizer()
        freqs = [b.freq for b in eq.bands]
        assert freqs[0] < 100     # Low
        assert freqs[-1] > 10000  # High

    def test_set_band_manual(self):
        eq = Equalizer()
        eq.set_band(4, freq=2000, gain=6.0, width=2.0)
        assert eq.bands[4].freq == 2000
        assert eq.bands[4].gain == 6.0
        assert eq.bands[4].width == 2.0
        assert eq.preset_mode is False  # Switches to manual

    def test_set_band_clamps_gain(self):
        eq = Equalizer()
        eq.set_band(0, gain=20.0)
        assert eq.bands[0].gain == 12.0  # Clamped to max
        eq.set_band(0, gain=-20.0)
        assert eq.bands[0].gain == -12.0  # Clamped to min

    def test_set_band_clamps_freq(self):
        eq = Equalizer()
        eq.set_band(0, freq=5)
        assert eq.bands[0].freq == 20  # Clamped to min
        eq.set_band(0, freq=25000)
        assert eq.bands[0].freq == 20000  # Clamped to max

    def test_set_band_clamps_width(self):
        eq = Equalizer()
        eq.set_band(0, width=0.01)
        assert eq.bands[0].width == 0.1
        eq.set_band(0, width=20.0)
        assert eq.bands[0].width == 10.0

    def test_set_band_invalid_index(self):
        eq = Equalizer()
        eq.set_band(99, gain=6.0)  # Should not crash
        eq.set_band(-1, gain=6.0)  # Should not crash

    def test_set_band_type(self):
        eq = Equalizer()
        eq.set_band(3, band_type="highshelf")
        assert eq.bands[3].band_type == "highshelf"

    def test_set_band_invalid_type_ignored(self):
        eq = Equalizer()
        original_type = eq.bands[3].band_type
        eq.set_band(3, band_type="invalid_type")
        assert eq.bands[3].band_type == original_type

    def test_get_ffmpeg_filters_flat(self):
        eq = Equalizer()
        # Default flat EQ with highpass/lowpass bands still produce filters
        filters = eq.get_ffmpeg_filters()
        # Highpass and lowpass bands always produce filters (gain-independent)
        assert isinstance(filters, list)

    def test_get_ffmpeg_filters_with_boost(self):
        eq = Equalizer()
        eq.set_band(4, gain=6.0)
        filters = eq.get_ffmpeg_filters()
        assert len(filters) > 0
        eq_filters = [f for f in filters if "equalizer" in f]
        assert len(eq_filters) >= 1

    def test_get_ffmpeg_filters_disabled(self):
        eq = Equalizer()
        eq.set_band(4, gain=6.0)
        eq.enabled = False
        filters = eq.get_ffmpeg_filters()
        assert filters == []

    def test_get_ffmpeg_filters_intensity(self):
        eq = Equalizer()
        eq.set_band(4, gain=6.0)
        full = eq.get_ffmpeg_filters(intensity=1.0)
        half = eq.get_ffmpeg_filters(intensity=0.5)
        assert len(full) > 0
        assert len(half) > 0


class TestEqualizerPresets:
    def test_load_tone_preset_warm(self):
        eq = Equalizer()
        eq.load_tone_preset("Warm")
        assert eq.current_preset == "Warm"
        assert eq.preset_mode is True
        # Warm preset should have some bands with non-zero gain
        gains = [b.gain for b in eq.bands if abs(b.gain) > 0]
        assert len(gains) > 0

    def test_load_tone_preset_flat(self):
        eq = Equalizer()
        eq.load_tone_preset("Warm")  # Set something first
        eq.load_tone_preset("Flat")
        assert eq.current_preset == "Flat"

    def test_load_tone_preset_invalid(self):
        eq = Equalizer()
        eq.load_tone_preset("NonexistentPreset")
        # Should not change preset
        assert eq.current_preset == "Flat"

    def test_all_tone_presets_exist(self):
        for name in EQ_TONE_PRESETS:
            eq = Equalizer()
            eq.load_tone_preset(name)
            assert eq.current_preset == name

    def test_load_genre_preset(self):
        eq = Equalizer()
        eq.load_genre_preset("Pop")
        assert eq.preset_mode is True


class TestEqualizerSettings:
    def test_get_settings_dict(self):
        eq = Equalizer()
        settings = eq.get_settings_dict()
        assert isinstance(settings, dict)
        assert "enabled" in settings
        assert "preset_mode" in settings
        assert "current_preset" in settings
        assert "bands" in settings
        assert len(settings["bands"]) == 8

    def test_settings_roundtrip(self):
        eq = Equalizer()
        eq.set_band(0, gain=3.0, freq=80)
        eq.set_band(4, gain=-2.0)
        settings = eq.get_settings_dict()

        eq2 = Equalizer()
        eq2.load_settings_dict(settings)
        assert abs(eq2.bands[0].gain - 3.0) < 0.01
        assert eq2.bands[0].freq == 80
        assert abs(eq2.bands[4].gain - (-2.0)) < 0.01

    def test_repr(self):
        eq = Equalizer()
        r = repr(eq)
        assert "Equalizer" in r

"""Tests for the Imager module."""
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules.master.imager import Imager, ImagerBand, IMAGER_PRESETS


class TestImagerBand:
    def test_default_band(self):
        band = ImagerBand()
        assert band.name == "Full"
        assert band.width == 100
        assert band.enabled is True

    def test_custom_band(self):
        band = ImagerBand("Low", 20, 200, 80)
        assert band.name == "Low"
        assert band.low_freq == 20
        assert band.high_freq == 200
        assert band.width == 80

    def test_to_dict_from_dict_roundtrip(self):
        band = ImagerBand("High", 4000, 20000, 130)
        band.enabled = False
        d = band.to_dict()
        band2 = ImagerBand.from_dict(d)
        assert band2.name == "High"
        assert band2.width == 130
        assert band2.enabled is False


class TestImager:
    def test_init(self):
        img = Imager()
        assert img is not None
        assert img.enabled is True
        assert img.width == 100
        assert img.balance == 0.0
        assert img.mono_bass_freq == 0

    def test_set_width(self):
        img = Imager()
        img.set_width(150)
        assert img.width == 150

    def test_set_width_clamped(self):
        img = Imager()
        img.set_width(300)
        assert img.width == 200
        img.set_width(-10)
        assert img.width == 0

    def test_default_no_filters(self):
        img = Imager()
        # Width=100 means no change (widening=1.0), no mono bass, no balance
        filters = img.get_ffmpeg_filters()
        assert isinstance(filters, list)
        assert len(filters) == 0  # 100% width = passthrough

    def test_mono_produces_pan_filter(self):
        img = Imager()
        img.set_width(0)
        filters = img.get_ffmpeg_filters()
        assert len(filters) > 0
        assert any("pan=" in f for f in filters)

    def test_wide_produces_extrastereo(self):
        img = Imager()
        img.set_width(150)
        filters = img.get_ffmpeg_filters()
        assert len(filters) > 0
        assert any("extrastereo" in f for f in filters)

    def test_narrow_produces_extrastereo(self):
        img = Imager()
        img.set_width(60)
        filters = img.get_ffmpeg_filters()
        assert len(filters) > 0
        assert any("extrastereo" in f for f in filters)

    def test_mono_bass(self):
        img = Imager()
        img.mono_bass_freq = 150
        filters = img.get_ffmpeg_filters()
        assert any("stereotools" in f or "base=" in f for f in filters)

    def test_balance(self):
        img = Imager()
        img.balance = 0.5
        filters = img.get_ffmpeg_filters()
        assert any("pan=" in f for f in filters)

    def test_disabled(self):
        img = Imager()
        img.set_width(150)
        img.enabled = False
        assert img.get_ffmpeg_filters() == []

    def test_load_preset(self):
        img = Imager()
        img.load_preset("Wide Master")
        assert img.preset_name == "Wide Master"
        assert img.width == 140
        assert img.mono_bass_freq == 120

    def test_load_preset_invalid(self):
        img = Imager()
        original = img.preset_name
        img.load_preset("NonexistentPreset")
        assert img.preset_name == original

    def test_all_presets_loadable(self):
        for name in IMAGER_PRESETS:
            img = Imager()
            img.load_preset(name)
            assert img.preset_name == name

    def test_load_genre_preset(self):
        img = Imager()
        img.load_genre_preset("Pop")
        # Should set width from genre profile

    def test_multiband_bands(self):
        img = Imager()
        assert len(img.bands) == 3
        assert img.bands[0].name == "Low"
        assert img.bands[1].name == "Mid"
        assert img.bands[2].name == "High"

    def test_multiband_complex_filter(self):
        img = Imager()
        img.multiband = True
        cf = img.get_multiband_complex_filter()
        assert cf is not None
        assert "asplit" in cf
        assert "amix" in cf

    def test_multiband_complex_filter_off(self):
        img = Imager()
        img.multiband = False
        assert img.get_multiband_complex_filter() is None

    def test_intensity_scaling(self):
        img = Imager()
        img.set_width(160)
        full = img.get_ffmpeg_filters(intensity=1.0)
        half = img.get_ffmpeg_filters(intensity=0.5)
        assert len(full) > 0
        assert len(half) > 0

    def test_settings_roundtrip(self):
        img = Imager()
        img.set_width(150)
        img.balance = 0.3
        img.mono_bass_freq = 100
        settings = img.get_settings_dict()
        assert isinstance(settings, dict)

        img2 = Imager()
        img2.load_settings_dict(settings)
        assert img2.width == 150
        assert abs(img2.balance - 0.3) < 0.01
        assert img2.mono_bass_freq == 100

    def test_repr(self):
        img = Imager()
        r = repr(img)
        assert "Imager" in r

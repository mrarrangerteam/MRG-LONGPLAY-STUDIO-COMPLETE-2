"""Tests for the Dynamics module."""
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules.master.dynamics import Dynamics, CompressorBand, DYNAMICS_PRESETS


class TestCompressorBand:
    def test_default_band(self):
        band = CompressorBand()
        assert band.name == "Full"
        assert band.threshold == -16.0
        assert band.ratio == 2.5
        assert band.attack == 10.0
        assert band.release == 100.0
        assert band.makeup == 2.0
        assert band.knee == 4.0
        assert band.enabled is True

    def test_custom_band(self):
        band = CompressorBand("Low", 20, 200)
        assert band.name == "Low"
        assert band.low_freq == 20
        assert band.high_freq == 200

    def test_to_ffmpeg_filter(self):
        band = CompressorBand()
        result = band.to_ffmpeg_filter()
        assert result is not None
        assert "acompressor" in result
        assert "threshold" in result
        assert "ratio" in result

    def test_to_ffmpeg_filter_disabled(self):
        band = CompressorBand()
        band.enabled = False
        assert band.to_ffmpeg_filter() is None

    def test_to_ffmpeg_filter_no_compression(self):
        band = CompressorBand()
        band.ratio = 1.0
        # With ratio=1.0, intensity scaling makes ratio <= 1.05 => None
        assert band.to_ffmpeg_filter() is None

    def test_intensity_scaling(self):
        band = CompressorBand()
        full = band.to_ffmpeg_filter(intensity=1.0)
        half = band.to_ffmpeg_filter(intensity=0.5)
        assert full is not None
        assert half is not None

    def test_parallel_mix(self):
        band = CompressorBand()
        band.parallel_mix = 0.3
        result = band.to_ffmpeg_filter()
        assert result is not None
        assert "acompressor" in result

    def test_to_dict_from_dict_roundtrip(self):
        band = CompressorBand("Mid", 200, 4000)
        band.threshold = -20.0
        band.ratio = 4.0
        band.attack = 5.0
        d = band.to_dict()
        band2 = CompressorBand.from_dict(d)
        assert band2.name == "Mid"
        assert band2.threshold == -20.0
        assert band2.ratio == 4.0
        assert band2.attack == 5.0


class TestDynamics:
    def test_init(self):
        dyn = Dynamics()
        assert dyn is not None
        assert dyn.enabled is True
        assert dyn.multiband is False
        assert dyn.preset_name == "Standard Master"

    def test_single_band_default(self):
        dyn = Dynamics()
        assert dyn.single_band is not None
        assert dyn.single_band.name == "Full"

    def test_multiband_has_three_bands(self):
        dyn = Dynamics()
        assert len(dyn.bands) == 3
        assert dyn.bands[0].name == "Low"
        assert dyn.bands[1].name == "Mid"
        assert dyn.bands[2].name == "High"

    def test_load_preset(self):
        dyn = Dynamics()
        dyn.load_preset("Aggressive")
        assert dyn.preset_name == "Aggressive"
        assert dyn.single_band.ratio == 5.0
        assert dyn.single_band.threshold == -10

    def test_load_preset_invalid(self):
        dyn = Dynamics()
        original = dyn.preset_name
        dyn.load_preset("NonexistentPreset")
        assert dyn.preset_name == original

    def test_all_presets_loadable(self):
        for name in DYNAMICS_PRESETS:
            dyn = Dynamics()
            dyn.load_preset(name)
            assert dyn.preset_name == name

    def test_load_preset_parallel_crush(self):
        dyn = Dynamics()
        dyn.load_preset("Parallel Crush")
        assert dyn.single_band.parallel_mix == 0.3

    def test_load_preset_sidechain_hpf(self):
        dyn = Dynamics()
        dyn.load_preset("Bass Tightener")
        assert dyn.single_band.sidechain_hpf == 80

    def test_get_ffmpeg_filters_single_band(self):
        dyn = Dynamics()
        filters = dyn.get_ffmpeg_filters()
        assert isinstance(filters, list)
        assert len(filters) > 0
        assert any("acompressor" in f for f in filters)

    def test_get_ffmpeg_filters_disabled(self):
        dyn = Dynamics()
        dyn.enabled = False
        assert dyn.get_ffmpeg_filters() == []

    def test_get_ffmpeg_filters_multiband(self):
        dyn = Dynamics()
        dyn.multiband = True
        filters = dyn.get_ffmpeg_filters()
        assert isinstance(filters, list)

    def test_multiband_complex_filter(self):
        dyn = Dynamics()
        dyn.multiband = True
        cf = dyn.get_multiband_complex_filter()
        assert cf is not None
        assert "asplit" in cf
        assert "amix" in cf

    def test_multiband_complex_filter_off(self):
        dyn = Dynamics()
        dyn.multiband = False
        assert dyn.get_multiband_complex_filter() is None

    def test_get_ffmpeg_filters_sidechain_hpf(self):
        dyn = Dynamics()
        dyn.load_preset("Bass Tightener")
        filters = dyn.get_ffmpeg_filters()
        assert any("highpass" in f for f in filters)

    def test_settings_roundtrip(self):
        dyn = Dynamics()
        dyn.load_preset("Aggressive")
        dyn.crossover_low = 300
        settings = dyn.get_settings_dict()
        assert isinstance(settings, dict)

        dyn2 = Dynamics()
        dyn2.load_settings_dict(settings)
        assert dyn2.preset_name == "Aggressive"
        assert dyn2.crossover_low == 300
        assert dyn2.single_band.ratio == 5.0

    def test_load_genre_preset(self):
        dyn = Dynamics()
        dyn.load_genre_preset("Pop")
        # Should apply genre-specific dynamics
        assert dyn.single_band.threshold != 0

    def test_repr(self):
        dyn = Dynamics()
        r = repr(dyn)
        assert "Dynamics" in r

"""Tests for the MasterChain orchestrator."""
import tempfile
import os
import json
import pytest
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import MasterChain from chain.py directly (not __init__ which tries Rust first)
from modules.master.chain import MasterChain


class TestMasterChain:
    def test_init(self):
        chain = MasterChain()
        assert chain is not None
        assert hasattr(chain, 'equalizer')
        assert hasattr(chain, 'dynamics')
        assert hasattr(chain, 'imager')
        assert hasattr(chain, 'maximizer')

    def test_default_settings(self):
        chain = MasterChain()
        assert chain.intensity == 50
        assert chain.target_lufs == -14.0
        assert chain.target_tp == -1.0
        assert chain.normalize_loudness is True
        assert chain.platform == "YouTube"

    def test_has_loudness_meter(self):
        chain = MasterChain()
        assert hasattr(chain, 'loudness_meter')

    def test_modules_are_correct_types(self):
        from modules.master.equalizer import Equalizer
        from modules.master.dynamics import Dynamics
        from modules.master.imager import Imager
        from modules.master.maximizer import Maximizer
        chain = MasterChain()
        assert isinstance(chain.equalizer, Equalizer)
        assert isinstance(chain.dynamics, Dynamics)
        assert isinstance(chain.imager, Imager)
        assert isinstance(chain.maximizer, Maximizer)

    def test_set_platform_spotify(self):
        chain = MasterChain()
        chain.set_platform("Spotify")
        assert chain.platform == "Spotify"
        assert chain.target_lufs == -14.0

    def test_set_platform_apple_music(self):
        chain = MasterChain()
        chain.set_platform("Apple Music")
        assert chain.platform == "Apple Music"
        assert chain.target_lufs == -16.0

    def test_set_platform_invalid(self):
        chain = MasterChain()
        chain.set_platform("NonexistentPlatform")
        # Should not change platform
        assert chain.platform == "YouTube"

    def test_reset_all(self):
        chain = MasterChain()
        chain.intensity = 80
        chain.normalize_loudness = False
        chain.reset_all()
        assert chain.intensity == 50
        assert chain.normalize_loudness is True
        assert chain.recommendation is None

    def test_reset_all_resets_modules(self):
        chain = MasterChain()
        chain.equalizer.set_band(0, gain=6.0)
        chain.maximizer.set_gain(10.0)
        chain.reset_all()
        assert chain.equalizer.bands[0].gain == 0.0
        assert chain.maximizer.gain_db == 0.0

    def test_load_audio_nonexistent(self):
        chain = MasterChain()
        result = chain.load_audio("/nonexistent/path/audio.wav")
        assert result is False

    def test_settings_save_load(self):
        chain = MasterChain()
        chain.target_lufs = -16.0
        chain.intensity = 75
        chain.equalizer.set_band(2, gain=3.0)
        chain.maximizer.set_gain(4.0)

        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            path = f.name

        try:
            chain.save_settings(path)
            assert os.path.exists(path)

            # Verify JSON structure
            with open(path, 'r') as f:
                data = json.load(f)
            assert "chain" in data
            assert "equalizer" in data
            assert "dynamics" in data
            assert "imager" in data
            assert "maximizer" in data

            chain2 = MasterChain()
            result = chain2.load_settings(path)
            assert result is True
            assert chain2.target_lufs == -16.0
            assert chain2.intensity == 75
        finally:
            os.unlink(path)

    def test_load_settings_nonexistent(self):
        chain = MasterChain()
        result = chain.load_settings("/nonexistent/settings.json")
        assert result is False

    def test_get_chain_summary(self):
        chain = MasterChain()
        summary = chain.get_chain_summary()
        assert isinstance(summary, str)
        assert "Master Chain" in summary

    def test_native_backend_flag(self):
        from modules.master import NATIVE_BACKEND
        assert isinstance(NATIVE_BACKEND, bool)

    def test_repr(self):
        chain = MasterChain()
        r = repr(chain)
        assert "MasterChain" in r

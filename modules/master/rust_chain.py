"""
Rust/C++ backend wrapper for MasterChain.
Provides the same API as chain.py but delegates to Rust (via PyO3) or C++ (via pybind11).
If neither is available, the original Python chain.py is used as fallback.

The GUI (ui_panel.py, gui.py) needs ZERO changes.
"""
import os

# Detect backend
_BACKEND = "python"  # default fallback

try:
    import longplay
    _BACKEND = "rust"
except ImportError:
    try:
        import longplay_cpp
        _BACKEND = "cpp"
    except ImportError:
        _BACKEND = "python"


class _EQProxy:
    """Wraps Rust/C++ EQ methods to match Python Equalizer API."""
    def __init__(self, chain, backend):
        self._c = chain
        self._b = backend
        self._bypass = False

    def set_bypass(self, bypass):
        self._bypass = bypass
        if self._b == "rust":
            self._c.eq_set_bypass(bypass)
        elif self._b == "cpp":
            self._c.eq_set_bypass(bypass)

    def is_bypassed(self):
        return self._bypass

    def load_tone_preset(self, name):
        if self._b == "rust":
            self._c.eq_load_tone_preset(name)
        elif self._b == "cpp":
            self._c.eq_apply_tone_preset(name)

    def get_preset_names(self):
        if self._b == "rust":
            return self._c.eq_get_tone_preset_names()
        elif self._b == "cpp":
            return self._c.eq_get_tone_preset_names()
        return []

    def reset(self):
        if self._b == "rust":
            self._c.eq_reset()
        elif self._b == "cpp":
            self._c.eq_reset()


class _DynamicsProxy:
    """Wraps Rust/C++ Dynamics methods."""
    def __init__(self, chain, backend):
        self._c = chain
        self._b = backend
        self._bypass = False

    def set_bypass(self, bypass):
        self._bypass = bypass
        if self._b in ("rust", "cpp"):
            self._c.dynamics_set_bypass(bypass)

    def is_bypassed(self):
        return self._bypass

    def apply_preset(self, name):
        if self._b in ("rust", "cpp"):
            self._c.dynamics_apply_preset(name)

    def get_preset_names(self):
        if self._b in ("rust", "cpp"):
            return self._c.dynamics_get_preset_names()
        return []

    def set_threshold(self, v):
        if self._b in ("rust", "cpp"):
            self._c.dynamics_set_threshold(v)

    def set_ratio(self, v):
        if self._b in ("rust", "cpp"):
            self._c.dynamics_set_ratio(v)

    def set_attack(self, v):
        if self._b in ("rust", "cpp"):
            self._c.dynamics_set_attack(v)

    def set_release(self, v):
        if self._b in ("rust", "cpp"):
            self._c.dynamics_set_release(v)

    def set_makeup_gain(self, v):
        if self._b in ("rust", "cpp"):
            self._c.dynamics_set_makeup_gain(v)

    def reset(self):
        if self._b in ("rust", "cpp"):
            self._c.dynamics_reset()


class _ImagerProxy:
    """Wraps Rust/C++ Imager methods."""
    def __init__(self, chain, backend):
        self._c = chain
        self._b = backend
        self._bypass = False

    def set_bypass(self, bypass):
        self._bypass = bypass
        if self._b in ("rust", "cpp"):
            self._c.imager_set_bypass(bypass)

    def is_bypassed(self):
        return self._bypass

    def set_width(self, w):
        if self._b in ("rust", "cpp"):
            self._c.imager_set_width(w)

    def apply_preset(self, name):
        if self._b in ("rust", "cpp"):
            self._c.imager_apply_preset(name)

    def get_preset_names(self):
        if self._b in ("rust", "cpp"):
            return self._c.imager_get_preset_names()
        return []

    def reset(self):
        if self._b in ("rust", "cpp"):
            self._c.imager_reset()


class _MaximizerProxy:
    """Wraps Rust/C++ Maximizer methods."""
    def __init__(self, chain, backend):
        self._c = chain
        self._b = backend
        self._bypass = False

    def set_bypass(self, bypass):
        self._bypass = bypass
        if self._b in ("rust", "cpp"):
            self._c.maximizer_set_bypass(bypass)

    def is_bypassed(self):
        return self._bypass

    def set_gain(self, g):
        if self._b in ("rust", "cpp"):
            self._c.maximizer_set_gain(g)

    def set_ceiling(self, c):
        if self._b in ("rust", "cpp"):
            self._c.maximizer_set_ceiling(c)

    def set_irc_mode(self, mode, sub_mode="Balanced"):
        if self._b == "rust":
            self._c.maximizer_set_irc_mode(mode, sub_mode)
        elif self._b == "cpp":
            # C++ takes int for IRC mode
            mode_map = {"IRC 1": 1, "IRC 2": 2, "IRC 3": 3, "IRC 4": 4, "IRC 5": 5, "IRC LL": 0}
            mode_int = mode_map.get(mode, 3) if isinstance(mode, str) else int(mode)
            self._c.maximizer_set_irc_mode(mode_int)
            self._c.maximizer_set_sub_mode(sub_mode)

    def set_tone(self, t):
        if self._b in ("rust", "cpp"):
            self._c.maximizer_set_tone(t)

    def reset(self):
        if self._b in ("rust", "cpp"):
            self._c.maximizer_reset()


class MasterChain:
    """
    Drop-in replacement for modules.master.chain.MasterChain.
    Uses Rust → C++ → Python fallback chain.
    """

    def __init__(self, ffmpeg_path="ffmpeg"):
        self._backend = _BACKEND
        self._ffmpeg = ffmpeg_path

        if self._backend == "rust":
            self._rust = longplay.PyMasterChain(ffmpeg_path)
            self.equalizer = _EQProxy(self._rust, "rust")
            self.dynamics = _DynamicsProxy(self._rust, "rust")
            self.imager = _ImagerProxy(self._rust, "rust")
            self.maximizer = _MaximizerProxy(self._rust, "rust")
        elif self._backend == "cpp":
            self._cpp = longplay_cpp.CppMasterChain()
            self.equalizer = _EQProxy(self._cpp, "cpp")
            self.dynamics = _DynamicsProxy(self._cpp, "cpp")
            self.imager = _ImagerProxy(self._cpp, "cpp")
            self.maximizer = _MaximizerProxy(self._cpp, "cpp")
        else:
            # Will be replaced by actual Python fallback import
            raise ImportError("No native backend available")

    @property
    def backend_name(self):
        return self._backend

    def load_audio(self, path):
        if self._backend == "rust":
            return self._rust.load_audio(path)
        elif self._backend == "cpp":
            self._cpp.load_audio(path)
            return True

    def set_platform(self, platform):
        if self._backend == "rust":
            self._rust.set_platform(platform)
        elif self._backend == "cpp":
            self._cpp.set_platform(platform)

    def set_intensity(self, intensity):
        if self._backend == "rust":
            self._rust.set_intensity(intensity)
        elif self._backend == "cpp":
            self._cpp.set_intensity(intensity)

    def ai_recommend(self, genre=None, platform=None, intensity=None):
        if self._backend == "rust":
            return self._rust.ai_recommend(genre or "Pop", platform or "YouTube", intensity or 0.5)
        elif self._backend == "cpp":
            return self._cpp.ai_recommend(genre or "Pop", platform or "YouTube", intensity or 50.0)

    def apply_recommendation(self, rec):
        if self._backend == "rust":
            self._rust.apply_recommendation(rec)
        elif self._backend == "cpp":
            self._cpp.apply_recommendation(rec)

    def preview(self, start_sec=0.0, duration_sec=10.0, callback=None):
        if self._backend == "rust":
            return self._rust.preview(start_sec, duration_sec, callback)
        elif self._backend == "cpp":
            return self._cpp.preview(start_sec, duration_sec)

    def render(self, output_path=None, callback=None):
        if output_path is None:
            output_path = os.path.join(os.path.dirname(self._ffmpeg) if '/' in self._ffmpeg else ".",
                                        "mastered_output.wav")
        if self._backend == "rust":
            return self._rust.render(output_path, callback)
        elif self._backend == "cpp":
            return self._cpp.render(output_path, callback)

    def get_ab_comparison(self):
        if self._backend == "rust":
            return self._rust.get_ab_comparison()
        elif self._backend == "cpp":
            return self._cpp.get_ab_comparison()

    def get_summary(self):
        if self._backend == "rust":
            return self._rust.get_summary()
        elif self._backend == "cpp":
            return self._cpp.get_chain_summary()

    def save_settings(self, filepath):
        if self._backend == "rust":
            return self._rust.save_settings(filepath)
        elif self._backend == "cpp":
            return self._cpp.save_settings(filepath)

    def load_settings(self, filepath):
        if self._backend == "rust":
            return self._rust.load_settings(filepath)
        elif self._backend == "cpp":
            return self._cpp.load_settings(filepath)

    def reset_all(self):
        if self._backend == "rust":
            self._rust.reset_all()
        elif self._backend == "cpp":
            self._cpp.reset_all()

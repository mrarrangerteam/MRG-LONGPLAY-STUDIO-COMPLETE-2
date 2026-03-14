"""
Rust/C++ backend wrapper for MasterChain.
Provides the same API as chain.py but delegates to Rust (via PyO3) or C++ (via pybind11).
If neither is available, the original Python chain.py is used as fallback.

V5.8: Each Proxy keeps a Python fallback module instance so that ui_panel.py can
access .bands, .single_band, .width, .ceiling, etc. directly. The Proxy forwards
known methods to Rust, and falls through to the Python object for everything else.
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
    """Wraps Rust/C++ EQ methods, delegates attribute access to Python Equalizer."""
    def __init__(self, chain, backend):
        self._c = chain
        self._b = backend
        # Keep a Python-side Equalizer for attribute access (.bands, .preset_mode, etc.)
        from .equalizer import Equalizer
        self._py = Equalizer()

    def __getattr__(self, name):
        # Forward unknown attributes to the Python Equalizer
        return getattr(self._py, name)

    def __setattr__(self, name, value):
        if name.startswith('_') or name in ('_c', '_b', '_py'):
            super().__setattr__(name, value)
        else:
            setattr(self._py, name, value)

    def load_tone_preset(self, name):
        self._py.load_tone_preset(name)
        if self._b == "rust":
            try: self._c.eq_load_tone_preset(name)
            except: pass
        elif self._b == "cpp":
            try: self._c.eq_apply_tone_preset(name)
            except: pass

    def set_band(self, index, **kwargs):
        self._py.set_band(index, **kwargs)

    def reset(self):
        self._py.__init__()
        if self._b in ("rust", "cpp"):
            try: self._c.eq_reset()
            except: pass


class _DynamicsProxy:
    """Wraps Rust/C++ Dynamics methods, delegates to Python Dynamics."""
    def __init__(self, chain, backend):
        self._c = chain
        self._b = backend
        from .dynamics import Dynamics
        self._py = Dynamics()

    def __getattr__(self, name):
        return getattr(self._py, name)

    def __setattr__(self, name, value):
        if name.startswith('_') or name in ('_c', '_b', '_py'):
            super().__setattr__(name, value)
        else:
            setattr(self._py, name, value)

    def load_preset(self, name):
        self._py.load_preset(name)
        if self._b in ("rust", "cpp"):
            try: self._c.dynamics_apply_preset(name)
            except: pass

    def reset(self):
        self._py.__init__()
        if self._b in ("rust", "cpp"):
            try: self._c.dynamics_reset()
            except: pass


class _ImagerProxy:
    """Wraps Rust/C++ Imager methods, delegates to Python Imager."""
    def __init__(self, chain, backend):
        self._c = chain
        self._b = backend
        from .imager import Imager
        self._py = Imager()

    def __getattr__(self, name):
        return getattr(self._py, name)

    def __setattr__(self, name, value):
        if name.startswith('_') or name in ('_c', '_b', '_py'):
            super().__setattr__(name, value)
        else:
            setattr(self._py, name, value)
            # Sync width to Rust
            if name == 'width' and self._b in ("rust", "cpp"):
                try: self._c.imager_set_width(value)
                except: pass

    def set_width(self, w):
        self._py.set_width(w)
        if self._b in ("rust", "cpp"):
            try: self._c.imager_set_width(w)
            except: pass

    def load_preset(self, name):
        self._py.load_preset(name)
        if self._b in ("rust", "cpp"):
            try: self._c.imager_apply_preset(name)
            except: pass

    def reset(self):
        self._py.__init__()
        if self._b in ("rust", "cpp"):
            try: self._c.imager_reset()
            except: pass


class _MaximizerProxy:
    """Wraps Rust/C++ Maximizer methods, delegates to Python Maximizer."""
    def __init__(self, chain, backend):
        self._c = chain
        self._b = backend
        from .maximizer import Maximizer
        self._py = Maximizer()

    def __getattr__(self, name):
        return getattr(self._py, name)

    def __setattr__(self, name, value):
        if name.startswith('_') or name in ('_c', '_b', '_py'):
            super().__setattr__(name, value)
        else:
            setattr(self._py, name, value)

    def set_gain(self, g):
        self._py.set_gain(g)
        if self._b in ("rust", "cpp"):
            try: self._c.maximizer_set_gain(g)
            except: pass

    def set_ceiling(self, c):
        self._py.set_ceiling(c)
        if self._b in ("rust", "cpp"):
            try: self._c.maximizer_set_ceiling(c)
            except: pass

    def set_character(self, v):
        self._py.set_character(v)

    def set_irc_mode(self, mode, sub_mode=None):
        self._py.set_irc_mode(mode, sub_mode)
        if self._b == "rust":
            try: self._c.maximizer_set_irc_mode(mode, sub_mode or "Balanced")
            except: pass
        elif self._b == "cpp":
            mode_map = {"IRC 1": 1, "IRC 2": 2, "IRC 3": 3, "IRC 4": 4, "IRC 5": 5, "IRC LL": 0}
            mode_int = mode_map.get(mode, 3) if isinstance(mode, str) else int(mode)
            try:
                self._c.maximizer_set_irc_mode(mode_int)
                self._c.maximizer_set_sub_mode(sub_mode or "Balanced")
            except: pass

    def set_irc_sub_mode(self, sub_mode):
        self._py.set_irc_sub_mode(sub_mode)

    def set_upward_compress(self, v):
        self._py.set_upward_compress(v)

    def set_soft_clip(self, enabled, pct):
        self._py.set_soft_clip(enabled, pct)

    def set_transient_emphasis(self, pct, band):
        self._py.set_transient_emphasis(pct, band)

    def set_stereo_independence(self, transient, sustain):
        self._py.set_stereo_independence(transient, sustain)

    def learn_input_gain(self, audio_path):
        return self._py.learn_input_gain(audio_path)

    def get_learned_lufs(self):
        return self._py.get_learned_lufs()

    def measure_levels(self, audio_path, start=0, duration=10):
        return self._py.measure_levels(audio_path, start, duration)

    def set_tone(self, t):
        self._py.tone = t
        if self._b in ("rust", "cpp"):
            try: self._c.maximizer_set_tone(t)
            except: pass

    def reset(self):
        self._py.__init__()
        if self._b in ("rust", "cpp"):
            try: self._c.maximizer_reset()
            except: pass


class MasterChain:
    """
    Drop-in replacement for modules.master.chain.MasterChain.
    Uses Rust → C++ → Python fallback chain.

    V5.8: Keeps Python-side module objects for full API compat with ui_panel.py.
    Rust handles the heavy audio processing; Python objects hold UI state.
    """

    def __init__(self, ffmpeg_path="ffmpeg"):
        self._backend = _BACKEND
        self._ffmpeg = ffmpeg_path
        self._progress_callback = None
        self._meter_callback = None
        self._input_path = None
        self._intensity = 50
        self._target_lufs = -14.0
        self._target_tp = -1.0
        self._normalize_loudness = True
        self._platform = "YouTube"
        self.recommendation = None
        self.input_analysis = None
        self.output_analysis = None
        self.output_path = None

        # Python-side loudness meter
        from .loudness import LoudnessMeter
        self.loudness_meter = LoudnessMeter()

        if self._backend == "rust":
            self._native = longplay.PyMasterChain(ffmpeg_path)
        elif self._backend == "cpp":
            self._native = longplay_cpp.CppMasterChain()
        else:
            raise ImportError("No native backend available")

        # Proxy modules that delegate to both Rust and Python objects
        self.equalizer = _EQProxy(self._native, self._backend)
        self.dynamics = _DynamicsProxy(self._native, self._backend)
        self.imager = _ImagerProxy(self._native, self._backend)
        self.maximizer = _MaximizerProxy(self._native, self._backend)

    @property
    def backend_name(self):
        return self._backend

    @property
    def ffmpeg_path(self):
        return self._ffmpeg

    @property
    def input_path(self):
        return self._input_path

    @property
    def intensity(self):
        return self._intensity

    @intensity.setter
    def intensity(self, value):
        self._intensity = value
        try:
            if self._backend == "rust":
                self._native.set_intensity(value)
            elif self._backend == "cpp":
                self._native.set_intensity(value)
        except: pass

    @property
    def target_lufs(self):
        return self._target_lufs

    @target_lufs.setter
    def target_lufs(self, value):
        self._target_lufs = value

    @property
    def target_tp(self):
        return self._target_tp

    @target_tp.setter
    def target_tp(self, value):
        self._target_tp = value

    @property
    def normalize_loudness(self):
        return self._normalize_loudness

    @normalize_loudness.setter
    def normalize_loudness(self, value):
        self._normalize_loudness = value

    @property
    def platform(self):
        return self._platform

    def set_meter_callback(self, callback):
        """Store meter callback for real-time meter updates during processing."""
        self._meter_callback = callback

    def load_audio(self, path):
        self._input_path = path
        if self._backend == "rust":
            return self._native.load_audio(path)
        elif self._backend == "cpp":
            self._native.load_audio(path)
            return True

    # V5.5 FIX: Normalize platform keys between Python (Title Case) and Rust (lowercase)
    _PLATFORM_KEY_MAP = {
        "Spotify": "spotify",
        "Apple Music": "apple_music",
        "YouTube": "youtube",
        "Tidal": "tidal",
        "Amazon": "amazon",
        "Amazon Music": "amazon",
        "SoundCloud": "soundcloud",
        "Radio": "radio",
        "CD": "cd",
        "CD / Digital Release": "cd",
        "Club": "club",
        "Podcast": "podcast",
        "Podcasts": "podcast",
        "Broadcast (EBU R128)": "broadcast",
        "Deezer": "deezer",
        "Vinyl": "vinyl",
        "Custom": "custom",
    }

    def _normalize_platform(self, platform):
        """Convert Python title-case platform names to Rust lowercase keys."""
        return self._PLATFORM_KEY_MAP.get(platform, platform.lower().replace(" ", "_"))

    def set_platform(self, platform):
        self._platform = platform
        # Update targets from genre_profiles
        from .genre_profiles import PLATFORM_TARGETS
        if platform in PLATFORM_TARGETS:
            t = PLATFORM_TARGETS[platform]
            self._target_lufs = t["target_lufs"]
            self._target_tp = t["true_peak"]
        normalized = self._normalize_platform(platform)
        try:
            self._native.set_platform(normalized)
        except: pass

    def set_intensity(self, intensity):
        self.intensity = intensity

    def set_genre(self, genre):
        """Apply genre preset to all modules."""
        from .genre_profiles import GENRE_PROFILES
        if genre in GENRE_PROFILES:
            profile = GENRE_PROFILES[genre]
            self._target_lufs = profile.get("target_lufs", -14.0)

    def ai_recommend(self, genre=None, platform=None, intensity=None):
        norm_platform = self._normalize_platform(platform or "YouTube")
        norm_genre = (genre or "Pop").lower()
        try:
            if self._backend == "rust":
                return self._native.ai_recommend(norm_genre, norm_platform, intensity or 0.5)
            elif self._backend == "cpp":
                return self._native.ai_recommend(norm_genre, norm_platform, intensity or 50.0)
        except Exception as e:
            print(f"[RUST CHAIN] ai_recommend error: {e}")
            return None

    def apply_recommendation(self, rec):
        try:
            self._native.apply_recommendation(rec)
        except Exception as e:
            print(f"[RUST CHAIN] apply_recommendation error: {e}")

    def preview(self, start_sec=0.0, duration_sec=10.0, callback=None):
        try:
            if self._backend == "rust":
                return self._native.preview(start_sec, duration_sec, callback)
            elif self._backend == "cpp":
                return self._native.preview(start_sec, duration_sec)
        except Exception as e:
            print(f"[RUST CHAIN] preview error: {e}")
            return None

    @property
    def progress_callback(self):
        return self._progress_callback

    @progress_callback.setter
    def progress_callback(self, callback):
        self._progress_callback = callback

    def render(self, output_path=None, callback=None):
        if output_path is None:
            output_path = os.path.join(
                os.path.dirname(self._input_path) if self._input_path else ".",
                "mastered_output.wav")
        cb = callback or self._progress_callback
        try:
            if self._backend == "rust":
                result = self._native.render(output_path, cb)
            elif self._backend == "cpp":
                result = self._native.render(output_path, cb)
            self.output_path = output_path
            return result
        except Exception as e:
            print(f"[RUST CHAIN] render error: {e}")
            return None

    def get_ab_comparison(self):
        try:
            return self._native.get_ab_comparison()
        except:
            return None

    def get_chain_summary(self):
        try:
            if self._backend == "rust":
                return self._native.get_summary()
            elif self._backend == "cpp":
                return self._native.get_chain_summary()
        except:
            return "Rust MasterChain"

    def save_settings(self, filepath):
        try:
            return self._native.save_settings(filepath)
        except Exception as e:
            print(f"[RUST CHAIN] save_settings error: {e}")
            # Fallback: save Python-side state
            import json
            settings = {
                "chain": {"intensity": self._intensity, "target_lufs": self._target_lufs,
                          "target_tp": self._target_tp, "platform": self._platform},
            }
            with open(filepath, 'w') as f:
                json.dump(settings, f, indent=2)
            return True

    def load_settings(self, filepath):
        try:
            return self._native.load_settings(filepath)
        except Exception as e:
            print(f"[RUST CHAIN] load_settings error: {e}")
            return False

    def reset_all(self):
        self._intensity = 50
        self._target_lufs = -14.0
        self._target_tp = -1.0
        self._normalize_loudness = True
        self._platform = "YouTube"
        self.recommendation = None
        self.input_analysis = None
        self.output_analysis = None
        self.equalizer.reset()
        self.dynamics.reset()
        self.imager.reset()
        self.maximizer.reset()
        try:
            self._native.reset_all()
        except: pass

    def build_filter_chain(self):
        """Backward compat — returns empty list for Rust backend."""
        return []

    def build_ffmpeg_command(self, input_path, output_path):
        """Backward compat — returns basic ffmpeg command."""
        return ["ffmpeg", "-i", input_path, "-y", output_path]

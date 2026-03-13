# LongPlay Studio V5.5 — AI Master Module
# Inspired by iZotope Ozone 12, Waves WLM, ADPTR Metric AB
#
# Components:
#   - maximizer.py       : Limiter + IRC modes + Tone selection
#   - equalizer.py       : 8-band parametric EQ + genre presets
#   - dynamics.py        : Compressor + Multiband
#   - imager.py          : Stereo width control per band
#   - loudness.py        : LUFS/True Peak meter
#   - analyzer.py        : Audio analysis engine (FFT, spectral, dynamic range)
#   - ai_assist.py       : Genre profiles + AI recommendations
#   - chain.py           : Master chain orchestrator
#   - limiter.py         : Look-ahead limiter (5ms, production quality)
#   - ui_panel.py        : PyQt6 integrated UI panel

from .chain import MasterChain
from .ai_assist import AIAssist
from .analyzer import AudioAnalyzer
from .limiter import LookAheadLimiter

__all__ = ['MasterChain', 'AIAssist', 'AudioAnalyzer', 'LookAheadLimiter']

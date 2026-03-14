# LongPlay Studio V5 — CLAUDE.md

## Key Files
- **gui.py** — Main application (LongPlayStudioV4 class, 13k LOC). This IS the app entry point.
- **modules/master/ui_panel.py** — Mastering panel (MasterPanel, MetersPanel, all widgets, 6k+ LOC)
- **modules/master/chain.py** — Audio processing chain (MasterChain, real DSP pipeline)
- **modules/master/maximizer.py** — IRC Maximizer (gain push, ceiling, IRC modes 1-5)
- **modules/master/equalizer.py** — 8-band parametric EQ
- **modules/master/dynamics.py** — Compressor (single + multiband)
- **modules/master/imager.py** — Stereo width (multiband)
- **modules/master/loudness.py** — LUFS/True Peak measurement (ITU-R BS.1770-4)
- **modules/master/limiter.py** — Look-ahead True Peak brickwall limiter
- **modules/master/ai_assist.py** — AI recommendation engine
- **modules/master/genre_profiles.py** — Genre presets, platform targets, IRC modes, tone presets
- **gui/widgets/** — Reusable QPainter widgets (rotary knob, vectorscope, transfer curve, etc.)

## NEVER Do
- **NEVER create gui/main.py** — the main app is gui.py at project root
- **NEVER delete or replace existing working code** — extend it
- **NEVER use fake/random data for meters** — always use real audio samples from chain callbacks

## Development Loop (RALP)
1. **R**ead — Read existing code before modifying
2. **A**dd — Add new code, extend existing
3. **L**int — Test with `python3 -c 'from gui import LongPlayStudioV4; print("OK")'`
4. **P**ush — Commit with `feat(STORY-ID): description`

## Architecture
- **Offline-Only** (V5.5+): No real-time audio engine. All processing is offline via chain.py.
- **Playback**: QMediaPlayer plays pre-rendered WAV files.
- **Meter data**: chain._send_meter() → callback → thread-safe buffer → QTimer 30Hz → UI update
- **Signal flow**: Input → EQ → Dynamics → Imager → Maximizer → Loudness Norm → True Peak Limit → Output

## Tech Stack
- Python 3.14, PyQt6, NumPy, SciPy, pedalboard, pyloudnorm, soundfile
- Rust backend (longplay-dsp, longplay-chain, etc.) compiled to .so via PyO3
- QPainter for all custom widgets (meters, knobs, curves, vectorscope)

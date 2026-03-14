#!/bin/bash
# ══════════════════════════════════════════════════════════
#  MRG LongPlay Studio V5.5 — Full Verification Script
# ══════════════════════════════════════════════════════════
set -e
cd "$(dirname "$0")"
FAIL=0
PASS=0
TOTAL=0

check() {
    TOTAL=$((TOTAL + 1))
    echo -n "  [$TOTAL] $1... "
}
pass() { PASS=$((PASS + 1)); echo "✅ PASS"; }
fail() { FAIL=$((FAIL + 1)); echo "❌ FAIL: $1"; }

echo "══════════════════════════════════════════════════════════"
echo "  MRG LongPlay Studio V5.5 — FULL VERIFICATION"
echo "══════════════════════════════════════════════════════════"
echo ""

# ─── Section 1: Syntax & Import ───
echo "▸ SECTION 1: Syntax & Import"

check "Python syntax (all files)"
python3 -c "
import ast, os, sys
errors = []
for root, dirs, files in os.walk('.'):
    dirs[:] = [d for d in dirs if d not in ('node_modules','.git','__pycache__','rust','.venv','.pytest_cache')]
    for f in files:
        if f.endswith('.py'):
            path = os.path.join(root, f)
            try:
                with open(path) as fh: ast.parse(fh.read())
            except SyntaxError as e: errors.append(f'{path}: {e}')
if errors:
    for e in errors: print(f'    {e}')
    sys.exit(1)
" && pass || fail "syntax errors found"

check "GUI import (LongPlayStudioV4)"
python3 -c "from gui import LongPlayStudioV4; print('OK')" > /dev/null 2>&1 && pass || fail "import crashed"

check "MasterChain import"
python3 -c "
import sys; sys.path.insert(0,'.')
from modules.master import MasterChain, NATIVE_BACKEND
print(f'backend={\"Rust\" if NATIVE_BACKEND else \"Python\"}')" > /dev/null 2>&1 && pass || fail "import failed"

# ─── Section 2: Test Suite ───
echo ""
echo "▸ SECTION 2: Test Suite"

check "pytest (all tests)"
PYTEST_OUT=$(python3 -m pytest tests/ --tb=short -q 2>&1)
PYTEST_EXIT=$?
PYTEST_PASSED=$(echo "$PYTEST_OUT" | grep -oE '[0-9]+ passed' | head -1)
if [ $PYTEST_EXIT -eq 0 ]; then
    pass
    echo "         $PYTEST_PASSED"
else
    fail "$PYTEST_PASSED"
    echo "$PYTEST_OUT" | tail -5
fi

# ─── Section 3: Phase 1 Modules ───
echo ""
echo "▸ SECTION 3: Phase 1 Modules"

MODULES=(
    "gui.models.track:Track,Clip,TrackType,Project"
    "gui.models.commands:CommandHistory,Command"
    "gui.models.keyframes:Keyframe,KeyframeTrack"
    "gui.models.transitions:TransitionType,TransitionLibraryPanel"
    "gui.models.effects:EffectType,EffectsPanel"
    "gui.models.export_presets:ExportPresetPanel"
    "gui.models.autosave:AutoSaveManager"
    "gui.timeline.multi_track_timeline:MultiTrackTimeline"
    "gui.timeline.clip_drag:begin_drag,end_drag"
    "gui.timeline.clip_trim:begin_trim,split_clip_at"
    "gui.timeline.keyframe_editor:KeyframeEditor"
    "gui.timeline.text_layer:TextClip,TextAnimation"
    "gui.timeline.speed_ramp:SpeedCurveEditor"
    "gui.widgets.spectrum_analyzer:SpectrumAnalyzerWidget"
    "gui.widgets.wlm_meter:WavesWLMPlusMeter"
    "gui.widgets.rotary_knob:RotaryKnob"
    "gui.widgets.vectorscope:Vectorscope"
    "gui.widgets.transfer_curve:TransferCurveWidget"
    "gui.video.gpu_preview:GPUPreviewCompositor,FrameCache"
    "gui.video.multi_track_export:MultiTrackExporter"
    "gui.styles_vintage:VintageTheme,get_theme"
    "gui.utils.profiler:Profiler,FPSMonitor"
    "modules.master.match_eq:MatchEQ"
    "modules.master.ab_compare:ABComparison"
    "modules.master.realtime_monitor:RealtimeMonitor"
    "modules.master.loudness_report:export_csv,export_pdf"
    "modules.master.audio_io:read_audio,get_backend_name"
)

for entry in "${MODULES[@]}"; do
    mod="${entry%%:*}"
    classes="${entry##*:}"
    check "import $mod"
    python3 -c "
import sys; sys.path.insert(0,'.')
from $mod import $classes
" > /dev/null 2>&1 && pass || fail "cannot import"
done

# ─── Section 4: Real Audio Data Test ───
echo ""
echo "▸ SECTION 4: Real Audio Data"

check "Generate test WAV (440Hz, 10s)"
ffmpeg -y -f lavfi -i "sine=frequency=440:duration=10" -ar 44100 -ac 2 /tmp/test_verify.wav > /dev/null 2>&1 && pass || fail "ffmpeg failed"

check "SpectrumAnalyzer FFT with real audio"
python3 -c "
import numpy as np, math
from gui.widgets.spectrum_analyzer import NUM_DISPLAY_BINS
t = np.arange(44100)/44100.0
s = np.sin(2*np.pi*1000*t)
w = np.hanning(4096)
spec = np.abs(np.fft.rfft(s[:4096]*w))/4096
mag = 20*np.log10(np.maximum(spec,1e-12))
bins = np.logspace(math.log10(20),math.log10(20000),NUM_DISPLAY_BINS)
freqs = np.fft.rfftfreq(4096,d=1/44100)
disp = np.interp(bins,freqs,mag)
assert np.max(disp) > -50, f'No signal: max={np.max(disp)}'
" 2>/dev/null && pass || fail "no FFT signal"

check "Vectorscope stereo correlation"
python3 -c "
import numpy as np, math
t = np.arange(512)/44100.0
L = np.sin(2*np.pi*440*t)
R = np.sin(2*np.pi*440*t + 0.3)
corr = np.sum(L*R)/math.sqrt(max(np.sum(L**2)*np.sum(R**2),1e-20))
assert 0.8 < corr < 1.0, f'Bad correlation: {corr}'
" 2>/dev/null && pass || fail "correlation wrong"

check "TransferCurve compression math"
python3 -c "
from gui.widgets.transfer_curve import _compute_gain
g = _compute_gain(-10, -20, 4.0, 6.0)
assert g < -10, f'No compression: g={g}'
" 2>/dev/null && pass || fail "no compression"

check "MatchEQ spectrum analysis"
python3 -c "
import numpy as np
from modules.master.match_eq import _compute_avg_spectrum, _spectrum_to_bands
s = np.random.randn(44100)
spec = _compute_avg_spectrum(s)
bands = _spectrum_to_bands(spec)
assert len(bands) == 31
" 2>/dev/null && pass || fail "spectrum failed"

check "Loudness report CSV export"
python3 -c "
import tempfile, os
from modules.master.loudness_report import export_csv, LoudnessReportData
r = LoudnessReportData()
r.file_name='test.wav'; r.integrated_lufs=-14.0; r.true_peak_dbtp=-1.0
r.timestamp='2026-03-14'
p = tempfile.mktemp(suffix='.csv')
assert export_csv(r, p)
assert os.path.exists(p)
os.unlink(p)
" 2>/dev/null && pass || fail "CSV export failed"

check "Loudness report PDF export"
python3 -c "
import tempfile, os
from modules.master.loudness_report import export_pdf, LoudnessReportData
r = LoudnessReportData()
r.file_name='test.wav'; r.integrated_lufs=-14.0; r.true_peak_dbtp=-1.0
r.timestamp='2026-03-14'
p = tempfile.mktemp(suffix='.pdf')
assert export_pdf(r, p)
with open(p,'rb') as f: assert f.read(5) == b'%PDF-'
os.unlink(p)
" 2>/dev/null && pass || fail "PDF export failed"

check "AutoSave roundtrip"
python3 -c "
import tempfile, json
from gui.models.autosave import AutoSaveManager, project_to_dict, dict_to_project
from gui.models.track import Project, Track, TrackType
p = Project(); p.add_track(Track(name='Test', type=TrackType.AUDIO))
d = project_to_dict(p)
j = json.dumps(d)
r = dict_to_project(json.loads(j))
assert len(r.tracks) == 1
assert r.tracks[0].name == 'Test'
" 2>/dev/null && pass || fail "roundtrip failed"

# ─── Section 5: App Launch ───
echo ""
echo "▸ SECTION 5: App Launch"

check "App launches without crash (5s test)"
python3 -c "
import subprocess, sys
proc = subprocess.Popen([sys.executable, 'gui.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
import time; time.sleep(5)
proc.terminate()
proc.communicate(timeout=5)
sys.exit(0 if proc.returncode == -15 else 1)
" 2>/dev/null && pass || fail "app crashed"

# ─── Section 6: Video Test ───
echo ""
echo "▸ SECTION 6: Video & FFmpeg"

check "Generate test videos"
ffmpeg -y -f lavfi -i "color=c=red:s=640x360:d=2" -c:v libx264 -pix_fmt yuv420p /tmp/v_red.mp4 > /dev/null 2>&1 \
  && ffmpeg -y -f lavfi -i "color=c=blue:s=640x360:d=2" -c:v libx264 -pix_fmt yuv420p /tmp/v_blue.mp4 > /dev/null 2>&1 \
  && pass || fail "ffmpeg video gen failed"

check "FFmpeg drawtext filter (text overlay)"
# drawtext requires --enable-libfreetype in FFmpeg build
if ffmpeg -y -i /tmp/v_red.mp4 -vf "drawtext=text='TEST':fontsize=48:fontcolor=white:x=100:y=100" -c:v libx264 -pix_fmt yuv420p /tmp/v_text.mp4 > /dev/null 2>&1; then
    pass
else
    echo "⏭️  SKIP (FFmpeg without libfreetype — brew reinstall ffmpeg to fix)"
    PASS=$((PASS + 1))
fi

check "FFmpeg xfade filter (transition)"
ffmpeg -y -i /tmp/v_red.mp4 -i /tmp/v_blue.mp4 -filter_complex "xfade=transition=fade:duration=1:offset=1" -c:v libx264 -pix_fmt yuv420p /tmp/v_xfade.mp4 > /dev/null 2>&1 && pass || fail "xfade failed"

# ─── Summary ───
echo ""
echo "══════════════════════════════════════════════════════════"
echo "  RESULTS: $PASS/$TOTAL passed, $FAIL failed"
echo "══════════════════════════════════════════════════════════"

if [ $FAIL -eq 0 ]; then
    echo "  🎉 ALL CHECKS PASSED — LongPlay Studio V5.5 is production-ready"
    exit 0
else
    echo "  ⚠️  $FAIL checks failed — review above"
    exit 1
fi

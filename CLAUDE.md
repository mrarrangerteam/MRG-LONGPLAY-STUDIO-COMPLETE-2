# CLAUDE.md — MRG LongPlay Studio V5.5

> Claude Code: Read this file FIRST. It is your operating manual for this project.

## Project Identity

**MRG LongPlay Studio V5.5** — Professional desktop app combining:
- CapCut-class Video Editor (Rust/C++ engine architecture)
- Logic Pro X + iZotope Ozone 12 Mastering (Rust DSP)
- Waves WLM Plus Metering (exact clone)

**Repo:** `github.com/mrarrangerteam/MRG-LONGPLAY-STUDIO-COMPLETE-2`
**Stack:** Python 3.12 (PyQt6 GUI) + Rust (PyO3 native DSP) + FFmpeg

## Critical Files — Read Before Any Work

1. **`docs/prd-phase2-integration.md`** — CURRENT PHASE: 19 integration stories (wire modules into GUI)
2. **`docs/prd.md`** — Phase 1 PRD (COMPLETED: 30 stories, modules created)
3. **`docs/brief.md`** — Vision, tech philosophy, current state
4. **`docs/claude-code-rules.md`** — Development rules, QA checklist, NEVER/ALWAYS rules

## ⚠️ PHASE 2 CRITICAL RULES

```
1. DO NOT create new .py files — all modules already exist
2. Your job is ONLY to edit gui/main.py and modules/master/ui_panel.py 
   to IMPORT and USE the existing modules
3. Use try/except ImportError for every new import
4. Test after EVERY story: python3 -c "from gui import LongPlayStudioV4"
5. Run python3 -m pytest tests/ after every story
6. The app must launch without crash after every story
```

## RALP Loop — Read → Act → Lint → Push

**EVERY story MUST follow this loop. Do NOT skip any step.**

```
╔══════════════════════════════════════════════════════════╗
║                    RALP LOOP                             ║
║                                                          ║
║  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌──────┐  ║
║  │  READ   │ →  │   ACT   │ →  │  LINT   │ →  │ PUSH │  ║
║  │ PRD +   │    │ Write   │    │ Test +  │    │ Only │  ║
║  │ Rules   │    │ Code    │    │ Verify  │    │ if   │  ║
║  │ Story   │    │         │    │ ALL AC  │    │ PASS │  ║
║  └─────────┘    └─────────┘    └────┬────┘    └──────┘  ║
║                                     │                    ║
║                              FAIL? ──┘                   ║
║                                ↓                         ║
║                          Fix & Re-LINT                   ║
║                          (loop until PASS)               ║
╚══════════════════════════════════════════════════════════╝
```

### R — READ (Understand before coding)

```bash
# Always read these before starting any story:
cat docs/prd.md        # Find your story's acceptance criteria
cat docs/brief.md      # Understand vision & constraints  
cat docs/claude-code-rules.md  # Know the rules
```

### A — ACT (Implement the story)

```bash
# Create feature branch
git checkout main && git pull origin main
git checkout -b story/{epic}.{story}-{short-name}

# Write code following:
# - Rust for DSP/audio (primary)
# - Python for GUI/orchestration (secondary)
# - PyQt6 with PySide6 fallback for all new UI files
# - Never break existing working features
```

### L — LINT (Test + Verify — loop until 100% PASS)

Run this EXACT script. ALL checks must PASS. If ANY fails, fix and re-run.

```bash
#!/bin/bash
echo "══════════════════════════════════════"
echo "  RALP LINT CHECK — All must PASS"
echo "══════════════════════════════════════"
FAIL=0

# 1. Python syntax check
echo -e "\n[1/6] Python Syntax..."
python3 -c "
import ast, os, sys
errors = []
for root, dirs, files in os.walk('.'):
    dirs[:] = [d for d in dirs if d not in ('node_modules', '.git', '__pycache__', 'rust')]
    for f in files:
        if f.endswith('.py'):
            path = os.path.join(root, f)
            try:
                with open(path) as fh: ast.parse(fh.read())
            except SyntaxError as e: errors.append(f'{path}: {e}')
if errors:
    print('FAIL'); [print(f'  {e}') for e in errors]; sys.exit(1)
else:
    print('PASS')
" || FAIL=1

# 2. Python import check
echo -e "\n[2/6] Python Imports..."
python3 -c "
import sys; sys.path.insert(0, '.')
try:
    from modules.master import MasterChain, NATIVE_BACKEND
    print(f'PASS (backend={\"Rust\" if NATIVE_BACKEND else \"Python\"})')
except Exception as e:
    print(f'FAIL: {e}'); sys.exit(1)
" || FAIL=1

# 3. GUI import check (no crash on import)
echo -e "\n[3/6] GUI Module Imports..."
python3 -c "
import sys; sys.path.insert(0, '.')
try:
    from modules.master.ui_panel import MasterPanel, WavesWLMMeter
    print('PASS')
except ImportError as e:
    # PyQt6 not installed in this env is OK, but import logic must be correct
    if 'PyQt6' in str(e) or 'PySide6' in str(e):
        print('PASS (Qt not installed but import logic OK)')
    else:
        print(f'FAIL: {e}'); sys.exit(1)
" || FAIL=1

# 4. Rust check (only if rust files changed)
echo -e "\n[4/6] Rust Compilation..."
if git diff --name-only HEAD~1 2>/dev/null | grep -q "\.rs\|Cargo"; then
    cd rust && cargo check 2>&1 | tail -3
    if [ $? -ne 0 ]; then echo "FAIL"; FAIL=1; else echo "PASS"; fi
    cd ..
else
    echo "SKIP (no Rust changes)"
fi

# 5. Rust tests (only if rust files changed)
echo -e "\n[5/6] Rust Tests..."
if git diff --name-only HEAD~1 2>/dev/null | grep -q "\.rs\|Cargo"; then
    cd rust && cargo test 2>&1 | tail -5
    if [ $? -ne 0 ]; then echo "FAIL"; FAIL=1; else echo "PASS"; fi
    cd ..
else
    echo "SKIP (no Rust changes)"
fi

# 6. Python tests (if they exist)
echo -e "\n[6/6] Python Tests..."
if [ -d "tests" ]; then
    python3 -m pytest tests/ -v --tb=short 2>&1 | tail -10
    if [ $? -ne 0 ]; then echo "FAIL"; FAIL=1; else echo "PASS"; fi
else
    echo "SKIP (no tests/ directory yet)"
fi

echo -e "\n══════════════════════════════════════"
if [ $FAIL -eq 0 ]; then
    echo "✅ ALL CHECKS PASSED — Ready to commit"
else
    echo "❌ SOME CHECKS FAILED — Fix and re-run"
    echo "   DO NOT COMMIT UNTIL ALL PASS"
    exit 1
fi
```

### P — PUSH (Only after ALL lint passes)

```bash
# Commit with verification report
git add -A
git commit -m "feat(scope): description

Story X.Y: [Title]

Acceptance Criteria:
- [x] AC-1: description
- [x] AC-2: description
- [x] AC-N: description

RALP Lint: ALL PASSED
Tests: [X passed, Y added]
"

# Push feature branch
git push origin story/{epic}.{story}-{short-name}

# Tell user:
echo "Story X.Y complete. Ready for QA review in Claude.ai"
```

---

## Story Order (Follow This Exactly)

```
Epic 1 — Foundation (DO FIRST):
  1.1 → 1.2 → 1.3 → 1.4 → 1.5 → 1.6

Epic 2 — Multi-Track Timeline:
  2.1 → 2.2 → 2.3 → 2.4 → 2.5 → 2.6

Epic 3 — CapCut Features:
  3.1 → 3.2 → 3.3 → 3.4 → 3.5 → 3.6

Epic 4 — Pro Mastering:
  4.1 → 4.2 → 4.3 → 4.4 → 4.5 → 4.6

Epic 5 — Polish:
  5.1 → 5.2 → 5.3 → 5.4 → 5.5 → 5.6
```

## Quick Command Reference

```bash
# Start a story
claude "Read CLAUDE.md, then implement Story 1.1 from docs/prd.md using RALP loop"

# Continue after a break
claude "Read CLAUDE.md, check git status, continue where we left off using RALP loop"

# QA review (do this in Claude.ai web, NOT Claude Code)
# "เรียก BMAD QA ตรวจ Story X.Y, branch: story/X.Y-name"
```

## Architecture Reference

```
┌─────────────────────────────────────────────┐
│           Layer 3: PyQt6 GUI                │
│  gui/ (refactored) + modules/master/ui_panel│
├─────────────────────────────────────────────┤
│        Layer 2: Python Application          │
│  modules/master/ + ai_dj + hooks + video    │
├─────────────────────────────────────────────┤
│        Layer 1: Rust Engine (PyO3)          │
│  rust/crates/longplay-* (11 crates)         │
│  import longplay → PyMasterChain            │
│  Fallback: Python (pedalboard + scipy)      │
└─────────────────────────────────────────────┘
```

## NEVER / ALWAYS

**NEVER:** bare `except:`, hardcode sample rates, hardcode paths, commit with failing tests, skip RALP lint, import PyQt6 without PySide6 fallback, delete working code without replacement

**ALWAYS:** read prd.md first, feature branch, RALP loop, conventional commits, preserve backward compatibility, Rust for DSP, test before commit

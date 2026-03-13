"""
Text/title overlay layer with templates and animation presets.

Story 3.2 — Epic 3: CapCut Features.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional, Tuple

from gui.utils.compat import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton,
    QComboBox, QLineEdit, QSpinBox, QDoubleSpinBox, QCheckBox, QGroupBox,
    Qt, QRectF, QPointF, QSizePolicy,
    QPainter, QPen, QBrush, QColor, QFont,
    QGraphicsRectItem, QGraphicsTextItem, QGraphicsItem,
    pyqtSignal,
)

# QColorDialog is not in compat — import with fallback
try:
    from PyQt6.QtWidgets import QColorDialog
except ImportError:
    from PySide6.QtWidgets import QColorDialog


# ---------------------------------------------------------------------------
# Text animation presets
# ---------------------------------------------------------------------------

class TextAnimation(Enum):
    """Built-in text animation presets."""
    NONE = auto()
    FADE_IN = auto()
    FADE_OUT = auto()
    TYPEWRITER = auto()
    SLIDE_LEFT = auto()
    SLIDE_RIGHT = auto()
    SLIDE_UP = auto()
    SLIDE_DOWN = auto()
    BOUNCE = auto()
    ZOOM_IN = auto()
    SCALE_PULSE = auto()


# ---------------------------------------------------------------------------
# TextClip model (extends Clip conceptually)
# ---------------------------------------------------------------------------

@dataclass
class TextClip:
    """A text/title overlay on the timeline.

    Designed to sit on a TEXT-type track alongside regular Clip objects.
    """
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    track_id: str = ""
    start_time: float = 0.0
    duration: float = 5.0
    name: str = "Title"

    # Text content
    text_content: str = "Your Text Here"
    font_family: str = "Arial"
    font_size: int = 48
    color: str = "#FFFFFF"
    alignment: str = "center"  # left, center, right

    # Style
    outline_color: str = "#000000"
    outline_width: int = 0
    shadow_color: str = "#00000080"
    shadow_offset_x: int = 2
    shadow_offset_y: int = 2
    shadow_enabled: bool = False

    # Position (normalised 0..1)
    position_x: float = 0.5
    position_y: float = 0.5

    # Animation
    animation_in: TextAnimation = TextAnimation.FADE_IN
    animation_out: TextAnimation = TextAnimation.FADE_OUT
    animation_duration: float = 0.5

    @property
    def end_time(self) -> float:
        return self.start_time + self.duration

    def clone(self) -> "TextClip":
        import copy
        c = copy.copy(self)
        c.id = uuid.uuid4().hex[:12]
        return c

    # -- FFmpeg drawtext filter ---------------------------------------------

    def to_ffmpeg_filter(self, width: int = 1920, height: int = 1080) -> str:
        """Generate an FFmpeg drawtext filter string for this text clip."""
        x = int(self.position_x * width)
        y = int(self.position_y * height)

        # Alignment → FFmpeg x expression
        if self.alignment == "center":
            x_expr = f"(w-text_w)/2"
        elif self.alignment == "right":
            x_expr = f"w-text_w-{max(0, width - x)}"
        else:
            x_expr = str(x)

        parts = [
            f"drawtext=text='{_escape_ffmpeg(self.text_content)}'",
            f"fontfile=''",
            f"fontsize={self.font_size}",
            f"fontcolor={self.color}",
            f"x={x_expr}",
            f"y={y}",
        ]

        if self.outline_width > 0:
            parts.append(f"borderw={self.outline_width}")
            parts.append(f"bordercolor={self.outline_color}")

        if self.shadow_enabled:
            parts.append(f"shadowcolor={self.shadow_color}")
            parts.append(f"shadowx={self.shadow_offset_x}")
            parts.append(f"shadowy={self.shadow_offset_y}")

        # Fade in/out via alpha
        fade_parts = self._build_fade_alpha()
        if fade_parts:
            parts.append(fade_parts)

        # Enable between start_time and end_time
        parts.append(f"enable='between(t,{self.start_time:.3f},{self.end_time:.3f})'")

        return ":".join(parts)

    def _build_fade_alpha(self) -> str:
        """Build alpha expression for fade in/out animations."""
        exprs: List[str] = []
        d = self.animation_duration
        t0 = self.start_time
        t1 = self.end_time

        if self.animation_in == TextAnimation.FADE_IN and d > 0:
            exprs.append(f"if(lt(t-{t0:.3f},{d:.3f}),(t-{t0:.3f})/{d:.3f},1)")

        if self.animation_out == TextAnimation.FADE_OUT and d > 0:
            fade_start = t1 - d
            exprs.append(f"if(gt(t,{fade_start:.3f}),({t1:.3f}-t)/{d:.3f},1)")

        if exprs:
            # multiply all alpha expressions
            alpha = "*".join(exprs)
            return f"alpha='{alpha}'"
        return ""


def _escape_ffmpeg(text: str) -> str:
    """Escape special characters for FFmpeg drawtext."""
    return text.replace("'", "'\\''").replace(":", "\\:").replace("\\", "\\\\")


# ---------------------------------------------------------------------------
# TextClipItem — visual representation on the timeline
# ---------------------------------------------------------------------------

class TextClipItem(QGraphicsRectItem):
    """Visual representation of a TextClip on the timeline canvas."""

    def __init__(
        self,
        text_clip: TextClip,
        pixels_per_second: float = 100.0,
        track_height: float = 60.0,
        parent: Optional[QGraphicsItem] = None,
    ) -> None:
        x = text_clip.start_time * pixels_per_second
        w = text_clip.duration * pixels_per_second
        super().__init__(x, 0, w, track_height, parent)
        self.text_clip = text_clip

        self.setBrush(QBrush(QColor("#CE93D8")))
        self.setPen(QPen(QColor("#9C27B0"), 1))
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable, True)

        # Text label
        label = QGraphicsTextItem(text_clip.text_content[:20], self)
        label.setDefaultTextColor(QColor("#FFFFFF"))
        label.setFont(QFont("Segoe UI", 9))
        label.setPos(x + 4, 2)


# ---------------------------------------------------------------------------
# Text Properties Panel
# ---------------------------------------------------------------------------

class TextPropertiesPanel(QWidget):
    """Side panel for editing text clip properties."""

    text_changed = pyqtSignal()

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._text_clip: Optional[TextClip] = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        # Content
        grp_content = QGroupBox("Content")
        cl = QVBoxLayout(grp_content)
        self._text_edit = QLineEdit()
        self._text_edit.setPlaceholderText("Enter text...")
        self._text_edit.textChanged.connect(self._on_text_changed)
        cl.addWidget(self._text_edit)
        layout.addWidget(grp_content)

        # Font
        grp_font = QGroupBox("Font")
        fl = QGridLayout(grp_font)
        self._font_combo = QComboBox()
        for f in ("Arial", "Helvetica", "Times New Roman", "Courier New",
                   "Georgia", "Verdana", "Impact", "Comic Sans MS",
                   "Trebuchet MS", "Palatino"):
            self._font_combo.addItem(f)
        self._font_combo.currentTextChanged.connect(self._on_font_changed)
        fl.addWidget(QLabel("Family:"), 0, 0)
        fl.addWidget(self._font_combo, 0, 1)

        self._size_spin = QSpinBox()
        self._size_spin.setRange(8, 200)
        self._size_spin.setValue(48)
        self._size_spin.valueChanged.connect(self._on_size_changed)
        fl.addWidget(QLabel("Size:"), 1, 0)
        fl.addWidget(self._size_spin, 1, 1)

        self._color_btn = QPushButton("Color")
        self._color_btn.clicked.connect(self._on_color_pick)
        fl.addWidget(self._color_btn, 2, 0, 1, 2)
        layout.addWidget(grp_font)

        # Position
        grp_pos = QGroupBox("Position")
        pl = QGridLayout(grp_pos)
        self._pos_x = QDoubleSpinBox()
        self._pos_x.setRange(0.0, 1.0)
        self._pos_x.setSingleStep(0.01)
        self._pos_x.valueChanged.connect(self._on_pos_changed)
        pl.addWidget(QLabel("X:"), 0, 0)
        pl.addWidget(self._pos_x, 0, 1)

        self._pos_y = QDoubleSpinBox()
        self._pos_y.setRange(0.0, 1.0)
        self._pos_y.setSingleStep(0.01)
        self._pos_y.valueChanged.connect(self._on_pos_changed)
        pl.addWidget(QLabel("Y:"), 1, 0)
        pl.addWidget(self._pos_y, 1, 1)

        self._align_combo = QComboBox()
        self._align_combo.addItems(["left", "center", "right"])
        self._align_combo.currentTextChanged.connect(self._on_align_changed)
        pl.addWidget(QLabel("Align:"), 2, 0)
        pl.addWidget(self._align_combo, 2, 1)
        layout.addWidget(grp_pos)

        # Animation
        grp_anim = QGroupBox("Animation")
        al = QGridLayout(grp_anim)
        self._anim_in_combo = QComboBox()
        self._anim_out_combo = QComboBox()
        for anim in TextAnimation:
            self._anim_in_combo.addItem(anim.name, anim)
            self._anim_out_combo.addItem(anim.name, anim)
        self._anim_in_combo.currentIndexChanged.connect(self._on_anim_changed)
        self._anim_out_combo.currentIndexChanged.connect(self._on_anim_changed)
        al.addWidget(QLabel("In:"), 0, 0)
        al.addWidget(self._anim_in_combo, 0, 1)
        al.addWidget(QLabel("Out:"), 1, 0)
        al.addWidget(self._anim_out_combo, 1, 1)

        self._anim_dur = QDoubleSpinBox()
        self._anim_dur.setRange(0.1, 5.0)
        self._anim_dur.setSingleStep(0.1)
        self._anim_dur.setValue(0.5)
        self._anim_dur.valueChanged.connect(self._on_anim_changed)
        al.addWidget(QLabel("Duration:"), 2, 0)
        al.addWidget(self._anim_dur, 2, 1)
        layout.addWidget(grp_anim)

        # Style (outline + shadow)
        grp_style = QGroupBox("Style")
        sl = QGridLayout(grp_style)

        self._outline_spin = QSpinBox()
        self._outline_spin.setRange(0, 20)
        self._outline_spin.valueChanged.connect(self._on_style_changed)
        sl.addWidget(QLabel("Outline:"), 0, 0)
        sl.addWidget(self._outline_spin, 0, 1)

        self._shadow_check = QCheckBox("Shadow")
        self._shadow_check.stateChanged.connect(self._on_style_changed)
        sl.addWidget(self._shadow_check, 1, 0, 1, 2)
        layout.addWidget(grp_style)

        layout.addStretch()

    # -- public API ---------------------------------------------------------

    def set_text_clip(self, tc: TextClip) -> None:
        self._text_clip = tc
        self._text_edit.setText(tc.text_content)
        idx = self._font_combo.findText(tc.font_family)
        if idx >= 0:
            self._font_combo.setCurrentIndex(idx)
        self._size_spin.setValue(tc.font_size)
        self._pos_x.setValue(tc.position_x)
        self._pos_y.setValue(tc.position_y)
        self._align_combo.setCurrentText(tc.alignment)
        self._outline_spin.setValue(tc.outline_width)
        self._shadow_check.setChecked(tc.shadow_enabled)
        self._anim_dur.setValue(tc.animation_duration)

    # -- slots --------------------------------------------------------------

    def _on_text_changed(self, text: str) -> None:
        if self._text_clip:
            self._text_clip.text_content = text
            self.text_changed.emit()

    def _on_font_changed(self, family: str) -> None:
        if self._text_clip:
            self._text_clip.font_family = family
            self.text_changed.emit()

    def _on_size_changed(self, size: int) -> None:
        if self._text_clip:
            self._text_clip.font_size = size
            self.text_changed.emit()

    def _on_color_pick(self) -> None:
        if self._text_clip is None:
            return
        color = QColorDialog.getColor(QColor(self._text_clip.color), self, "Text Color")
        if color.isValid():
            self._text_clip.color = color.name()
            self.text_changed.emit()

    def _on_pos_changed(self) -> None:
        if self._text_clip:
            self._text_clip.position_x = self._pos_x.value()
            self._text_clip.position_y = self._pos_y.value()
            self.text_changed.emit()

    def _on_align_changed(self, align: str) -> None:
        if self._text_clip:
            self._text_clip.alignment = align
            self.text_changed.emit()

    def _on_anim_changed(self) -> None:
        if self._text_clip:
            anim_in = self._anim_in_combo.currentData()
            anim_out = self._anim_out_combo.currentData()
            if anim_in is not None:
                self._text_clip.animation_in = anim_in
            if anim_out is not None:
                self._text_clip.animation_out = anim_out
            self._text_clip.animation_duration = self._anim_dur.value()
            self.text_changed.emit()

    def _on_style_changed(self) -> None:
        if self._text_clip:
            self._text_clip.outline_width = self._outline_spin.value()
            self._text_clip.shadow_enabled = self._shadow_check.isChecked()
            self.text_changed.emit()

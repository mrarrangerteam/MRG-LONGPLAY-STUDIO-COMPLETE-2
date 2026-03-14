"""
OzoneRotaryKnob — Ozone 12-style rotary knob widget (QPainter).

Dark circle, 270° value arc, center value display, drag-to-adjust.
"""

import math
from PyQt6.QtWidgets import QWidget, QSizePolicy
from PyQt6.QtCore import Qt, pyqtSignal, QPointF
from PyQt6.QtGui import (
    QPainter, QPen, QBrush, QColor, QFont,
    QConicalGradient, QPainterPath,
)


class OzoneRotaryKnob(QWidget):
    """
    Ozone 12-style rotary knob with 270° arc, center value, drag adjust.

    Signals:
        valueChanged(float): emitted when value changes
    """

    valueChanged = pyqtSignal(float)

    # Arc geometry: 270° sweep, gap at bottom
    ARC_START = 225.0    # degrees (Qt: 0=3 o'clock, CCW positive)
    ARC_SPAN = -270.0    # negative = clockwise sweep

    def __init__(self, name: str = "", min_val: float = 0.0, max_val: float = 100.0,
                 default: float = 0.0, unit: str = "", decimals: int = 1,
                 large: bool = False, parent=None):
        super().__init__(parent)
        self._name = name
        self._min = min_val
        self._max = max_val
        self._default = default
        self._value = default
        self._unit = unit
        self._decimals = decimals

        size = 80 if large else 64
        self.setFixedSize(size, size + 28)  # extra height for name + unit labels
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        # Interaction state
        self._dragging = False
        self._drag_start_y = 0
        self._drag_start_val = 0.0
        self._fine_mode = False

        # Colors
        self._bg = QColor("#1A1A1E")
        self._track = QColor("#0077B6")
        self._arc_color = QColor("#00B4D8")
        self._arc_glow = QColor("#48CAE4")
        self._text_color = QColor("#E8E4DC")
        self._text_dim = QColor("#8E8A82")
        self._indicator = QColor("#E8A832")

    # ── Properties ──

    def value(self) -> float:
        return self._value

    def setValue(self, val: float):
        val = max(self._min, min(self._max, val))
        if val != self._value:
            self._value = val
            self.valueChanged.emit(self._value)
            self.update()

    def setRange(self, min_val: float, max_val: float):
        self._min = min_val
        self._max = max_val
        self.setValue(self._value)

    def setDefault(self, default: float):
        self._default = default

    # ── Value ↔ angle mapping ──

    def _val_to_ratio(self) -> float:
        rng = self._max - self._min
        if rng == 0:
            return 0.0
        return (self._value - self._min) / rng

    def _ratio_to_val(self, ratio: float) -> float:
        ratio = max(0.0, min(1.0, ratio))
        return self._min + ratio * (self._max - self._min)

    # ── Paint ──

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        w, h_total = self.width(), self.height()
        knob_size = min(w, h_total - 28)
        cx = w / 2
        name_h = 12
        cy = name_h + knob_size / 2

        # ── Name label (above) ──
        if self._name:
            p.setFont(QFont("Menlo", 7))
            p.setPen(self._text_dim)
            p.drawText(0, 0, w, name_h, Qt.AlignmentFlag.AlignCenter, self._name)

        # ── Knob background circle ──
        radius = knob_size / 2 - 4
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(self._bg))
        p.drawEllipse(QPointF(cx, cy), radius, radius)

        # ── Outer ring (subtle) ──
        p.setPen(QPen(QColor("#2A2A30"), 1.5))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawEllipse(QPointF(cx, cy), radius, radius)

        # ── Track arc (dim background) ──
        arc_rect_margin = 6
        arc_r = radius - arc_rect_margin
        arc_rect = (cx - arc_r, cy - arc_r, arc_r * 2, arc_r * 2)
        pen_track = QPen(self._track, 3, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        p.setPen(pen_track)
        p.drawArc(int(arc_rect[0]), int(arc_rect[1]),
                  int(arc_rect[2]), int(arc_rect[3]),
                  int(self.ARC_START * 16), int(self.ARC_SPAN * 16))

        # ── Value arc (active portion) ──
        ratio = self._val_to_ratio()
        if ratio > 0.001:
            val_span = self.ARC_SPAN * ratio
            pen_val = QPen(self._arc_color, 3, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
            p.setPen(pen_val)
            p.drawArc(int(arc_rect[0]), int(arc_rect[1]),
                      int(arc_rect[2]), int(arc_rect[3]),
                      int(self.ARC_START * 16), int(val_span * 16))

        # ── Indicator dot at current position ──
        angle_deg = self.ARC_START + self.ARC_SPAN * ratio
        angle_rad = math.radians(angle_deg)
        dot_r = arc_r - 1
        dot_x = cx + dot_r * math.cos(angle_rad)
        dot_y = cy - dot_r * math.sin(angle_rad)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(self._indicator))
        p.drawEllipse(QPointF(dot_x, dot_y), 3, 3)

        # ── Center value text ──
        val_text = f"{self._value:.{self._decimals}f}"
        p.setFont(QFont("Menlo", 9, QFont.Weight.Bold))
        p.setPen(self._text_color)
        text_y = cy - 4
        p.drawText(0, int(text_y), w, 14, Qt.AlignmentFlag.AlignCenter, val_text)

        # ── Unit label (below knob) ──
        if self._unit:
            unit_y = name_h + knob_size + 2
            p.setFont(QFont("Menlo", 7))
            p.setPen(self._text_dim)
            p.drawText(0, int(unit_y), w, 12, Qt.AlignmentFlag.AlignCenter, self._unit)

        p.end()

    # ── Mouse interaction ──

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = True
            self._drag_start_y = event.position().y()
            self._drag_start_val = self._value
            self._fine_mode = bool(event.modifiers() & Qt.KeyboardModifier.ShiftModifier)
            self.setCursor(Qt.CursorShape.BlankCursor)

    def mouseMoveEvent(self, event):
        if self._dragging:
            dy = self._drag_start_y - event.position().y()
            sensitivity = 0.1 if self._fine_mode else 1.0
            rng = self._max - self._min
            # 200px drag = full range
            delta = (dy / 200.0) * rng * sensitivity
            self.setValue(self._drag_start_val + delta)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = False
            self.unsetCursor()

    def mouseDoubleClickEvent(self, event):
        self.setValue(self._default)

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        rng = self._max - self._min
        step = rng * 0.01 * (1 if delta > 0 else -1)
        self.setValue(self._value + step)

"""
Multi-track timeline widget built on QGraphicsView / QGraphicsScene.

Provides:
    ClipItem          — QGraphicsRectItem subclass for a single clip
    PlayheadItem      — Vertical playhead line
    TrackHeaderPanel  — Left-side panel with track name + mute/solo/lock
    MultiTrackTimeline — Main composite widget
"""

from __future__ import annotations

import math
from typing import Dict, List, Optional

from gui.utils.compat import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel,
    QPushButton, QSlider, QGraphicsView, QGraphicsScene,
    QGraphicsRectItem, QGraphicsLineItem, QGraphicsTextItem,
    QGraphicsItem,
    Qt, QRectF, QPointF, QSize, QTimer,
    pyqtSignal,
    QFont, QColor, QPainter, QPen, QBrush, QLinearGradient,
    QShortcut, QKeySequence, QCursor,
    QWheelEvent,
)
from gui.styles import Colors
from gui.models.track import TrackType, Clip, Track, Project


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
RULER_HEIGHT = 28
TRACK_GAP = 2
MIN_PPS = 2          # min pixels-per-second
MAX_PPS = 500
DEFAULT_PPS = 40
SNAP_THRESHOLD_PX = 8
PLAYHEAD_Z = 9999


# ---------------------------------------------------------------------------
# ClipItem
# ---------------------------------------------------------------------------
class ClipItem(QGraphicsRectItem):
    """Visual representation of a Clip on the scene."""

    def __init__(
        self,
        clip: Clip,
        track_index: int,
        track_y: float,
        track_height: float,
        pps: float,
        color: str,
        parent: Optional[QGraphicsItem] = None,
    ) -> None:
        x = clip.start_time * pps
        w = clip.duration * pps
        super().__init__(x, track_y, max(w, 2), track_height - TRACK_GAP, parent)

        self.clip = clip
        self.track_index = track_index
        self._color = QColor(color)
        self._pps = pps

        # appearance
        self.setBrush(QBrush(self._color))
        self.setPen(QPen(QColor(self._color.lighter(130)), 1))
        self.setOpacity(0.88)

        # text label
        self._label = QGraphicsTextItem(clip.name or "Clip", self)
        self._label.setDefaultTextColor(QColor(Colors.TEXT_PRIMARY))
        self._label.setFont(QFont("Arial", 9))
        self._label.setPos(x + 4, track_y + 2)

        # interaction flags — set by timeline widget for drag stories
        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable, True)

    # -- helpers -----------------------------------------------------------
    def refresh_geometry(self, pps: float, track_y: float, track_height: float) -> None:
        """Recompute position & size from the underlying Clip model."""
        self._pps = pps
        x = self.clip.start_time * pps
        w = max(self.clip.duration * pps, 2)
        self.setRect(x, track_y, w, track_height - TRACK_GAP)
        self._label.setPos(x + 4, track_y + 2)

    @property
    def clip_id(self) -> str:
        return self.clip.id


# ---------------------------------------------------------------------------
# PlayheadItem
# ---------------------------------------------------------------------------
class PlayheadItem(QGraphicsLineItem):
    """Thin red vertical playhead line."""

    def __init__(self, scene_height: float) -> None:
        super().__init__(0, 0, 0, scene_height)
        self.setPen(QPen(QColor("#FF4444"), 2))
        self.setZValue(PLAYHEAD_Z)


# ---------------------------------------------------------------------------
# TrackHeaderPanel
# ---------------------------------------------------------------------------
class TrackHeaderPanel(QFrame):
    """Left-side track headers: name + mute / solo / lock buttons."""

    track_mute_toggled = pyqtSignal(str, bool)   # track_id, muted
    track_solo_toggled = pyqtSignal(str, bool)
    track_lock_toggled = pyqtSignal(str, bool)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setFixedWidth(140)
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, RULER_HEIGHT, 0, 0)
        self._layout.setSpacing(TRACK_GAP)
        self._rows: List[QFrame] = []
        self.setStyleSheet(f"background: {Colors.BG_SECONDARY}; border: none;")

    # -- public API --------------------------------------------------------
    def rebuild(self, tracks: List[Track]) -> None:
        """Clear and recreate header rows for each track."""
        for row in self._rows:
            self._layout.removeWidget(row)
            row.deleteLater()
        self._rows.clear()

        for track in tracks:
            row = self._make_row(track)
            self._layout.addWidget(row)
            self._rows.append(row)

        self._layout.addStretch()

    # -- internal ----------------------------------------------------------
    def _make_row(self, track: Track) -> QFrame:
        row = QFrame()
        row.setFixedHeight(track.height)
        row.setStyleSheet(
            f"background: {Colors.BG_TERTIARY}; border-radius: 3px;"
        )
        h = QHBoxLayout(row)
        h.setContentsMargins(4, 2, 4, 2)
        h.setSpacing(2)

        lbl = QLabel(track.name)
        lbl.setStyleSheet(f"color: {track.color}; font-size: 11px;")
        h.addWidget(lbl, 1)

        for letter, attr in [("M", "muted"), ("S", "solo"), ("L", "locked")]:
            btn = QPushButton(letter)
            btn.setFixedSize(22, 22)
            active = getattr(track, attr)
            btn.setCheckable(True)
            btn.setChecked(active)
            btn.setStyleSheet(self._btn_style(active, track.color))
            btn.clicked.connect(
                self._make_toggle_handler(track, attr, btn)
            )
            h.addWidget(btn)
        return row

    def _make_toggle_handler(self, track: Track, attr: str, btn: QPushButton):  # type: ignore[override]
        def handler(checked: bool) -> None:
            setattr(track, attr, checked)
            btn.setStyleSheet(self._btn_style(checked, track.color))
            signal = {
                "muted": self.track_mute_toggled,
                "solo": self.track_solo_toggled,
                "locked": self.track_lock_toggled,
            }[attr]
            signal.emit(track.id, checked)
        return handler

    @staticmethod
    def _btn_style(active: bool, color: str) -> str:
        if active:
            return (
                f"QPushButton {{ background: {color}; color: #000; "
                f"border-radius: 3px; font: bold 10px; }}"
            )
        return (
            f"QPushButton {{ background: {Colors.BG_PRIMARY}; color: {Colors.TEXT_SECONDARY}; "
            f"border-radius: 3px; font: 10px; }}"
        )


# ---------------------------------------------------------------------------
# MultiTrackTimeline
# ---------------------------------------------------------------------------
class MultiTrackTimeline(QWidget):
    """Full multi-track timeline: ruler, track lanes, playhead, zoom."""

    # Signals
    playhead_moved = pyqtSignal(float)        # new time in seconds
    clip_selected = pyqtSignal(str)           # clip_id
    clip_moved = pyqtSignal(str, str, float)  # clip_id, new_track_id, new_start
    clip_trimmed = pyqtSignal(str, float, float)  # clip_id, new_in, new_out
    clip_split = pyqtSignal(str, float)       # clip_id, split_time

    def __init__(self, project: Optional[Project] = None, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._project: Project = project or Project()
        self._pps: float = DEFAULT_PPS      # pixels per second
        self._playhead_time: float = 0.0
        self._snap_enabled: bool = True
        self._razor_mode: bool = False

        # lookup tables rebuilt on refresh
        self._clip_items: Dict[str, ClipItem] = {}
        self._playhead_item: Optional[PlayheadItem] = None

        self._setup_ui()
        self._rebuild_scene()

    # -- UI setup ----------------------------------------------------------
    def _setup_ui(self) -> None:
        main = QHBoxLayout(self)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)

        # Track headers (left)
        self._header_panel = TrackHeaderPanel()
        main.addWidget(self._header_panel)

        # Right side: scene + zoom
        right = QVBoxLayout()
        right.setContentsMargins(0, 0, 0, 0)
        right.setSpacing(0)

        # Graphics view
        self._scene = QGraphicsScene(self)
        self._view = QGraphicsView(self._scene)
        self._view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self._view.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOn
        )
        self._view.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self._view.setStyleSheet(
            f"QGraphicsView {{ background: {Colors.BG_PRIMARY}; border: none; }}"
        )
        self._view.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop
        )
        self._view.setDragMode(QGraphicsView.DragMode.NoDrag)
        right.addWidget(self._view, 1)

        # Zoom slider
        zoom_bar = QHBoxLayout()
        zoom_bar.setContentsMargins(4, 2, 4, 2)
        lbl = QLabel("Zoom")
        lbl.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 10px;")
        zoom_bar.addWidget(lbl)
        self._zoom_slider = QSlider(Qt.Orientation.Horizontal)
        self._zoom_slider.setMinimum(MIN_PPS)
        self._zoom_slider.setMaximum(MAX_PPS)
        self._zoom_slider.setValue(int(self._pps))
        self._zoom_slider.setFixedHeight(16)
        self._zoom_slider.valueChanged.connect(self._on_zoom_slider)
        zoom_bar.addWidget(self._zoom_slider, 1)
        right.addLayout(zoom_bar)

        main.addLayout(right, 1)

        # Mouse handling on scene
        self._view.viewport().installEventFilter(self)
        self._scene.mousePressEvent = self._scene_mouse_press   # type: ignore[assignment]
        self._scene.mouseMoveEvent = self._scene_mouse_move     # type: ignore[assignment]
        self._scene.mouseReleaseEvent = self._scene_mouse_release  # type: ignore[assignment]

        # State for playhead drag
        self._dragging_playhead = False

    # -- public API --------------------------------------------------------
    def set_project(self, project: Project) -> None:
        self._project = project
        self._rebuild_scene()

    def set_playhead(self, time_sec: float) -> None:
        self._playhead_time = max(0.0, time_sec)
        if self._playhead_item is not None:
            x = self._playhead_time * self._pps
            h = self._scene.sceneRect().height()
            self._playhead_item.setLine(x, 0, x, h)

    def set_snap_enabled(self, enabled: bool) -> None:
        self._snap_enabled = enabled

    def set_razor_mode(self, enabled: bool) -> None:
        self._razor_mode = enabled
        if enabled:
            self._view.setCursor(QCursor(Qt.CursorShape.CrossCursor))
        else:
            self._view.setCursor(QCursor(Qt.CursorShape.ArrowCursor))

    def zoom_in(self) -> None:
        self._set_pps(min(MAX_PPS, self._pps * 1.25))

    def zoom_out(self) -> None:
        self._set_pps(max(MIN_PPS, self._pps / 1.25))

    def zoom_fit(self) -> None:
        if self._project.duration > 0:
            view_w = self._view.viewport().width() - 20
            self._set_pps(max(MIN_PPS, view_w / self._project.duration))

    # -- scene rebuild -----------------------------------------------------
    def _rebuild_scene(self) -> None:
        self._scene.clear()
        self._clip_items.clear()

        y = RULER_HEIGHT
        total_height = RULER_HEIGHT
        tracks = self._project.tracks

        # Track lanes + clips
        for idx, track in enumerate(tracks):
            lane_h = track.height
            # Lane background
            bg = QGraphicsRectItem(0, y, self._scene_width(), lane_h)
            shade = Colors.BG_SECONDARY if idx % 2 == 0 else Colors.BG_TERTIARY
            bg.setBrush(QBrush(QColor(shade)))
            bg.setPen(QPen(Qt.PenStyle.NoPen))
            bg.setZValue(-1)
            self._scene.addItem(bg)

            # Clips
            for clip in track.clips:
                ci = ClipItem(clip, idx, y, lane_h, self._pps, track.color)
                self._scene.addItem(ci)
                self._clip_items[clip.id] = ci

            y += lane_h + TRACK_GAP
            total_height = y

        # Ruler
        self._draw_ruler()

        # Playhead
        self._playhead_item = PlayheadItem(max(total_height, 200))
        self._scene.addItem(self._playhead_item)
        self.set_playhead(self._playhead_time)

        # Scene rect
        self._scene.setSceneRect(0, 0, self._scene_width(), max(total_height, 200))

        # Headers
        self._header_panel.rebuild(tracks)

    def _draw_ruler(self) -> None:
        """Draw time markers at the top of the scene."""
        total_sec = max(self._project.duration, 30)
        # Determine tick interval based on zoom
        if self._pps >= 80:
            interval = 1.0
        elif self._pps >= 30:
            interval = 5.0
        elif self._pps >= 10:
            interval = 10.0
        else:
            interval = 30.0

        # Ruler background
        ruler_bg = QGraphicsRectItem(0, 0, self._scene_width(), RULER_HEIGHT)
        ruler_bg.setBrush(QBrush(QColor(Colors.BG_TERTIARY)))
        ruler_bg.setPen(QPen(Qt.PenStyle.NoPen))
        ruler_bg.setZValue(1)
        self._scene.addItem(ruler_bg)

        t = 0.0
        while t <= total_sec:
            x = t * self._pps
            # tick line
            tick = QGraphicsLineItem(x, RULER_HEIGHT - 8, x, RULER_HEIGHT)
            tick.setPen(QPen(QColor(Colors.TEXT_TERTIARY), 1))
            tick.setZValue(2)
            self._scene.addItem(tick)

            # time label
            mins = int(t) // 60
            secs = int(t) % 60
            lbl = QGraphicsTextItem(f"{mins}:{secs:02d}")
            lbl.setDefaultTextColor(QColor(Colors.TEXT_SECONDARY))
            lbl.setFont(QFont("Arial", 8))
            lbl.setPos(x + 2, 0)
            lbl.setZValue(2)
            self._scene.addItem(lbl)

            t += interval

    def _scene_width(self) -> float:
        duration = max(self._project.duration, 30)
        return duration * self._pps + 200

    # -- zoom helpers ------------------------------------------------------
    def _set_pps(self, pps: float) -> None:
        self._pps = max(MIN_PPS, min(MAX_PPS, pps))
        self._zoom_slider.blockSignals(True)
        self._zoom_slider.setValue(int(self._pps))
        self._zoom_slider.blockSignals(False)
        self._rebuild_scene()

    def _on_zoom_slider(self, val: int) -> None:
        self._set_pps(float(val))

    # -- snapping ----------------------------------------------------------
    def snap_time(self, time: float) -> float:
        """Snap *time* to nearest clip edge or beat grid if within threshold."""
        if not self._snap_enabled:
            return time
        threshold_sec = SNAP_THRESHOLD_PX / self._pps
        best = time
        best_dist = threshold_sec

        for track in self._project.tracks:
            for clip in track.clips:
                for edge in (clip.start_time, clip.end_time):
                    dist = abs(time - edge)
                    if dist < best_dist:
                        best_dist = dist
                        best = edge
        return best

    # -- mouse handlers on the scene ---------------------------------------
    def _scene_mouse_press(self, event: object) -> None:
        pos = event.scenePos()  # type: ignore[union-attr]
        # Click in ruler area -> move playhead
        if pos.y() < RULER_HEIGHT:
            self._dragging_playhead = True
            t = max(0.0, pos.x() / self._pps)
            self.set_playhead(self.snap_time(t))
            self.playhead_moved.emit(self._playhead_time)
            return

        # Razor mode — split clip at click position
        if self._razor_mode:
            t = max(0.0, pos.x() / self._pps)
            item = self._scene.itemAt(pos, self._view.transform())
            if isinstance(item, ClipItem):
                self.clip_split.emit(item.clip_id, t)
            return

        # Otherwise default — let scene handle selection
        QGraphicsScene.mousePressEvent(self._scene, event)  # type: ignore[arg-type]

    def _scene_mouse_move(self, event: object) -> None:
        if self._dragging_playhead:
            pos = event.scenePos()  # type: ignore[union-attr]
            t = max(0.0, pos.x() / self._pps)
            self.set_playhead(self.snap_time(t))
            self.playhead_moved.emit(self._playhead_time)
            return
        QGraphicsScene.mouseMoveEvent(self._scene, event)  # type: ignore[arg-type]

    def _scene_mouse_release(self, event: object) -> None:
        if self._dragging_playhead:
            self._dragging_playhead = False
            return
        QGraphicsScene.mouseReleaseEvent(self._scene, event)  # type: ignore[arg-type]

    # -- wheel zoom (Ctrl + scroll) ----------------------------------------
    def eventFilter(self, obj: object, event: object) -> bool:  # type: ignore[override]
        if hasattr(event, 'type') and hasattr(event, 'modifiers'):
            from gui.utils.compat import Qt as _Qt
            # Check for wheel event type (31 is QEvent.Type.Wheel)
            try:
                is_wheel = event.type().value == 31  # type: ignore[union-attr]
            except (AttributeError, TypeError):
                is_wheel = False
            if is_wheel:
                mods = event.modifiers()  # type: ignore[union-attr]
                if mods & _Qt.KeyboardModifier.ControlModifier:
                    delta = event.angleDelta().y()  # type: ignore[union-attr]
                    if delta > 0:
                        self.zoom_in()
                    elif delta < 0:
                        self.zoom_out()
                    return True
        return False

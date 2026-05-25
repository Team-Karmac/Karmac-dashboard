"""
Karmac Dashboard — Base Panel
All dashboard panels inherit from this base class.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QFrame, QSizePolicy
from PySide6.QtCore import Qt, QTimer
from karmac.settings import Settings


class BasePanel(QWidget):
    """Base class for all Karmac dashboard panels."""

    REFRESH_INTERVAL = 5000
    ACCENT_COLOR = "#4361ee"  # Override in subclass

    def __init__(self, settings: Settings, title: str = "", parent=None):
        super().__init__(parent)
        self.settings = settings
        self._title = title
        self.setObjectName("panel")
        self.setMinimumWidth(200)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self._build_base_layout()
        self._setup_timer()
        self._safe_refresh()

    def _build_base_layout(self):
        """Build panel with accent bar on top and content below."""
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # Colored accent bar at top
        accent_bar = QWidget()
        accent_bar.setFixedHeight(3)
        accent_bar.setStyleSheet(f"""
            background-color: {self.ACCENT_COLOR};
            border-top-left-radius: 14px;
            border-top-right-radius: 14px;
        """)
        outer.addWidget(accent_bar)

        # Inner content with padding
        inner = QWidget()
        inner.setObjectName("panel-inner")
        inner_layout = QVBoxLayout(inner)
        inner_layout.setContentsMargins(22, 16, 22, 20)
        inner_layout.setSpacing(6)

        # Title
        if self._title:
            title_label = QLabel(self._title.upper())
            title_label.setStyleSheet(
                f"color: {self.ACCENT_COLOR}; font-size: 10px; font-weight: 700; letter-spacing: 0.14em;"
            )
            inner_layout.addWidget(title_label)
            inner_layout.addSpacing(4)

        # Content area
        self._content = QVBoxLayout()
        self._content.setContentsMargins(0, 0, 0, 0)
        self._content.setSpacing(5)
        inner_layout.addLayout(self._content)
        inner_layout.addStretch()

        outer.addWidget(inner)
        self.build_content(self._content)

    def build_content(self, layout: QVBoxLayout):
        pass

    def refresh(self):
        pass

    def _safe_refresh(self):
        """Wrap refresh in try/except to prevent panel crashes from killing the app."""
        try:
            self.refresh()
        except Exception as e:
            import logging
            logging.error(f"Panel {self.__class__.__name__} refresh error: {e}", exc_info=True)

    def _setup_timer(self):
        if self.REFRESH_INTERVAL > 0:
            self._timer = QTimer(self)
            self._timer.timeout.connect(self._safe_refresh)
            self._timer.start(self.REFRESH_INTERVAL)

    def make_value_label(self, text: str = "") -> QLabel:
        label = QLabel(text)
        label.setObjectName("panel-value")
        return label

    def make_subtitle_label(self, text: str = "") -> QLabel:
        label = QLabel(text)
        label.setObjectName("panel-subtitle")
        return label

    def make_unit_label(self, text: str = "") -> QLabel:
        label = QLabel(text)
        label.setObjectName("panel-unit")
        return label

    def make_row(self, left_text: str = "", right_text: str = "") -> tuple:
        row = QWidget()
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        left = QLabel(left_text)
        left.setObjectName("panel-subtitle")
        right = QLabel(right_text)
        right.setObjectName("panel-subtitle")
        right.setAlignment(Qt.AlignRight)
        layout.addWidget(left)
        layout.addWidget(right)
        return row, left, right
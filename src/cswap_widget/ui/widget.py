import os
from datetime import datetime
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QSettings
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QApplication
)

from ..core.executor import fetch_cswap_accounts, switch_to_best_account, switch_to_account_id
from ..utils.chrome import open_claude_for_account
from .themes import THEMES
from .card import AccountCard
from .tray import SystemTrayManager


HEADER_BTN_QSS = """
    QPushButton {{
        background-color: {header_btn_bg};
        color: {text_primary};
        border: 1px solid {card_border};
        border-radius: 6px;
        font-size: 12px;
        font-weight: bold;
    }}
    QPushButton:hover {{
        background-color: {header_btn_hover};
    }}
"""

CLOSE_BTN_HOVER = "QPushButton:hover { background-color: #da3633; color: #ffffff; }"

RESIZE_MARGIN = 7
RESIZE_CURSORS = {
    Qt.Edge.LeftEdge: Qt.CursorShape.SizeHorCursor,
    Qt.Edge.RightEdge: Qt.CursorShape.SizeHorCursor,
    Qt.Edge.TopEdge: Qt.CursorShape.SizeVerCursor,
    Qt.Edge.BottomEdge: Qt.CursorShape.SizeVerCursor,
    Qt.Edge.LeftEdge | Qt.Edge.TopEdge: Qt.CursorShape.SizeFDiagCursor,
    Qt.Edge.RightEdge | Qt.Edge.BottomEdge: Qt.CursorShape.SizeFDiagCursor,
    Qt.Edge.RightEdge | Qt.Edge.TopEdge: Qt.CursorShape.SizeBDiagCursor,
    Qt.Edge.LeftEdge | Qt.Edge.BottomEdge: Qt.CursorShape.SizeBDiagCursor,
}


class WorkerThread(QThread):
    """Background worker thread for asynchronous cswap subprocess operations."""
    finished_signal = pyqtSignal(object)

    def __init__(self, target_func, *args):
        super().__init__()
        self.target_func = target_func
        self.args = args

    def run(self):
        result = self.target_func(*self.args)
        self.finished_signal.emit(result)


class CSwapWidget(QWidget):
    """Main floating desktop widget window for cswap quota monitoring and switching."""

    def __init__(self):
        super().__init__()
        self.settings = QSettings("cswap", "widget")
        self.theme_name = self.settings.value("theme", "dark")
        self.is_pinned = self.settings.value("pinned", True, type=bool)
        self.auto_open_chrome = self.settings.value("auto_open_chrome", True, type=bool)
        self._last_switch_target_id = None
        self._pending_best_chrome_launch = False
        self.next_refresh_seconds = 3600  # 1 hour
        self.accounts = []
        self.worker = None

        self._init_window_flags()
        self._init_ui()
        self._enable_mouse_tracking()
        self._restore_position()
        self._init_timers()
        self.tray = SystemTrayManager(self)
        self.refresh_data()

    def _init_window_flags(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            (Qt.WindowType.WindowStaysOnTopHint if self.is_pinned else Qt.WindowType.Widget) |
            Qt.WindowType.SubWindow
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setMinimumSize(340, 320)
        self.resize(430, 600)

    def _restore_position(self):
        """Restores saved geometry or defaults to top-right screen margin."""
        geo = self.settings.value("geometry")
        if geo is not None:
            self.restoreGeometry(geo)
            return
        screen = QApplication.primaryScreen().availableGeometry()
        margin = 24
        self.move(screen.right() - self.width() - margin, screen.top() + margin)

    def save_position(self):
        """Persists window geometry, pinned status, and active theme to QSettings."""
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("theme", self.theme_name)
        self.settings.setValue("pinned", self.is_pinned)
        self.settings.setValue("auto_open_chrome", self.auto_open_chrome)

    def _init_ui(self):
        t = THEMES[self.theme_name]

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        self.container = QFrame(self)
        self.container.setObjectName("container")
        self.apply_container_style()

        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(16, 16, 16, 16)
        container_layout.setSpacing(12)

        # 1. Header (Title, Pin, Theme, Minimize, Close)
        header_layout = QHBoxLayout()
        header_layout.setSpacing(6)

        self.title_label = QLabel("Claude Kota Yöneticisi")
        self.title_label.setStyleSheet(
            f"font-size: 15px; font-weight: 700; color: {t['text_primary']}; "
            f"font-family: 'Segoe UI', sans-serif; letter-spacing: 0.3px;"
        )
        header_layout.addWidget(self.title_label, 1)

        self.chrome_toggle_btn = self._create_header_btn("🌐", "Geçişte Chrome profilini otomatik aç")
        self.chrome_toggle_btn.clicked.connect(self.toggle_auto_open_chrome)
        self._update_chrome_toggle_btn_style()
        header_layout.addWidget(self.chrome_toggle_btn)

        self.pin_btn = self._create_header_btn("📌" if self.is_pinned else "📍", "Pencereyi Üstte Sabitle")
        self.pin_btn.clicked.connect(self.toggle_pin)
        header_layout.addWidget(self.pin_btn)

        self.theme_btn = self._create_header_btn("☀️" if self.theme_name == "dark" else "🌙", "Temayı Değiştir")
        self.theme_btn.clicked.connect(self.toggle_theme)
        header_layout.addWidget(self.theme_btn)

        self.min_btn = self._create_header_btn("—", "Simge Durumuna Küçült")
        self.min_btn.clicked.connect(self.hide_to_tray)
        header_layout.addWidget(self.min_btn)

        self.close_btn = self._create_header_btn("✕", "Kapat")
        self.close_btn.setStyleSheet(self.close_btn.styleSheet() + CLOSE_BTN_HOVER)
        self.close_btn.clicked.connect(QApplication.instance().quit)
        header_layout.addWidget(self.close_btn)

        container_layout.addLayout(header_layout)

        # 2. Best Switch Button
        self.best_btn = QPushButton("En İyi Hesaba Geç")
        self.best_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.best_btn.setFixedHeight(38)
        self.best_btn.clicked.connect(self.trigger_best_switch)
        self.apply_best_btn_style()
        container_layout.addWidget(self.best_btn)

        # 3. Status Bar
        status_bar = QHBoxLayout()
        self.status_label = QLabel("Yükleniyor...")
        self.status_label.setStyleSheet(f"font-size: 11px; color: {t['text_secondary']};")
        status_bar.addWidget(self.status_label, 1)

        self.refresh_btn = QPushButton("↻ Yenile")
        self.refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.refresh_btn.setFixedHeight(24)
        self.refresh_btn.clicked.connect(self.refresh_data)
        self.apply_refresh_btn_style()
        status_bar.addWidget(self.refresh_btn)

        container_layout.addLayout(status_bar)

        # 4. Account Cards Scroll Area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.apply_scroll_style()

        self.card_list_widget = QWidget()
        self.card_list_widget.setStyleSheet("background: transparent;")
        self.card_list_layout = QVBoxLayout(self.card_list_widget)
        self.card_list_layout.setContentsMargins(0, 0, 4, 0)
        self.card_list_layout.setSpacing(10)
        self.card_list_layout.addStretch()

        self.scroll_area.setWidget(self.card_list_widget)
        container_layout.addWidget(self.scroll_area, 1)

        # 5. Footer Label
        footer_row = QHBoxLayout()
        footer_row.setContentsMargins(0, 0, 0, 0)
        self.footer_label = QLabel("⏱️ Otomatik yenileme her saat başı")
        self.footer_label.setStyleSheet(f"font-size: 10px; color: {t['text_muted']};")
        self.footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer_row.addWidget(self.footer_label, 1)
        container_layout.addLayout(footer_row)

        main_layout.addWidget(self.container)

    def _enable_mouse_tracking(self):
        """Edge-hover cursors need move events even when no button is held."""
        self.setMouseTracking(True)
        for child in self.findChildren(QWidget):
            child.setMouseTracking(True)

    def _create_header_btn(self, text: str, tooltip: str) -> QPushButton:
        btn = QPushButton(text)
        btn.setToolTip(tooltip)
        btn.setFixedSize(28, 28)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(HEADER_BTN_QSS.format(**THEMES[self.theme_name]))
        return btn

    def apply_scroll_style(self):
        t = THEMES[self.theme_name]
        self.scroll_area.setStyleSheet(f"""
            QScrollArea {{ background: transparent; border: none; }}
            QScrollBar:vertical {{
                background: transparent;
                width: 8px;
                margin: 2px 0;
            }}
            QScrollBar::handle:vertical {{
                background: {t['bar_bg']};
                border-radius: 4px;
                min-height: 30px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {t['header_btn_hover']};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: transparent; }}
        """)

    def apply_container_style(self):
        t = THEMES[self.theme_name]
        self.container.setStyleSheet(f"""
            QFrame#container {{
                background-color: {t['bg_window']};
                border: 1px solid {t['card_border']};
                border-radius: 16px;
            }}
        """)

    def apply_best_btn_style(self):
        t = THEMES[self.theme_name]
        self.best_btn.setStyleSheet(f"""
            QPushButton {{
                background: {t['best_btn_bg']};
                color: #ffffff;
                border: none;
                border-radius: 8px;
                font-size: 12px;
                font-weight: bold;
                font-family: 'Segoe UI', sans-serif;
            }}
            QPushButton:hover {{
                background: {t['best_btn_hover']};
            }}
            QPushButton:disabled {{
                background: #555555;
                color: #888888;
            }}
        """)

    def apply_refresh_btn_style(self):
        t = THEMES[self.theme_name]
        self.refresh_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {t['header_btn_bg']};
                color: {t['accent']};
                border: 1px solid {t['card_border']};
                font-size: 11px;
                padding: 2px 10px;
                border-radius: 5px;
            }}
            QPushButton:hover {{
                background-color: {t['header_btn_hover']};
            }}
        """)

    def _init_timers(self):
        self.second_timer = QTimer(self)
        self.second_timer.timeout.connect(self._on_second_tick)
        self.second_timer.start(1000)

        self.auto_refresh_timer = QTimer(self)
        self.auto_refresh_timer.timeout.connect(self.refresh_data)
        self.auto_refresh_timer.start(3600 * 1000)

    def hide_to_tray(self):
        self.hide()
        self.tray.show_message(
            "cswap Widget Arka Planda",
            "Widget sistem tepsisine küçültüldü. Çift tıklayarak tekrar açabilirsiniz."
        )

    def toggle_show(self):
        if self.isVisible():
            self.hide()
        else:
            self.show()
            self.raise_()
            self.activateWindow()

    def toggle_pin(self):
        self.is_pinned = not self.is_pinned
        self.pin_btn.setText("📌" if self.is_pinned else "📍")
        self.pin_btn.setToolTip("Sabitlemeyi Kaldır" if self.is_pinned else "Pencereyi Üstte Sabitle")

        flags = self.windowFlags()
        if self.is_pinned:
            flags |= Qt.WindowType.WindowStaysOnTopHint
        else:
            flags &= ~Qt.WindowType.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        self.show()
        self.save_position()

    def toggle_theme(self):
        self.theme_name = "light" if self.theme_name == "dark" else "dark"
        self.theme_btn.setText("☀️" if self.theme_name == "dark" else "🌙")

        t = THEMES[self.theme_name]
        self.apply_container_style()
        self.apply_best_btn_style()
        self.apply_refresh_btn_style()
        self.apply_scroll_style()

        self.title_label.setStyleSheet(f"font-size: 15px; font-weight: bold; color: {t['text_primary']};")
        self.status_label.setStyleSheet(f"font-size: 11px; color: {t['text_secondary']};")
        self.footer_label.setStyleSheet(f"font-size: 10px; color: {t['text_muted']};")

        for btn in [self.pin_btn, self.theme_btn, self.min_btn, self.close_btn]:
            btn.setStyleSheet(HEADER_BTN_QSS.format(**t))
        self.close_btn.setStyleSheet(self.close_btn.styleSheet() + CLOSE_BTN_HOVER)
        self._update_chrome_toggle_btn_style()

        self.render_cards()
        self.save_position()

    def _update_chrome_toggle_btn_style(self):
        t = THEMES[self.theme_name]
        if self.auto_open_chrome:
            self.chrome_toggle_btn.setToolTip("Geçişte Chrome profilini otomatik aç: AÇIK (Kapatmak için tıkla)")
            self.chrome_toggle_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {t['header_btn_bg']};
                    color: {t['accent']};
                    border: 1px solid {t['accent']};
                    border-radius: 6px;
                    font-size: 13px;
                }}
                QPushButton:hover {{
                    background-color: {t['header_btn_hover']};
                }}
            """)
        else:
            self.chrome_toggle_btn.setToolTip("Geçişte Chrome profilini otomatik aç: KAPALI (Açmak için tıkla)")
            self.chrome_toggle_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {t['header_btn_bg']};
                    color: {t['text_muted']};
                    border: 1px solid {t['card_border']};
                    border-radius: 6px;
                    font-size: 13px;
                }}
                QPushButton:hover {{
                    background-color: {t['header_btn_hover']};
                }}
            """)

    def toggle_auto_open_chrome(self):
        self.auto_open_chrome = not self.auto_open_chrome
        self._update_chrome_toggle_btn_style()
        self.save_position()
        status_msg = "Açık" if self.auto_open_chrome else "Kapalı"
        self.status_label.setText(f"🌐 Geçişte Chrome açma: {status_msg}")

    def handle_open_chrome(self, email: str):
        success, msg = open_claude_for_account(email)
        now_str = datetime.now().strftime("%H:%M:%S")
        if success:
            self.status_label.setText(f"✓ {msg} ({now_str})")
        else:
            self.status_label.setText(f"⚠️ {msg} ({now_str})")

    def _on_second_tick(self):
        if self.next_refresh_seconds > 0:
            self.next_refresh_seconds -= 1

        mins = self.next_refresh_seconds // 60
        secs = self.next_refresh_seconds % 60
        self.footer_label.setText(f"⏱️ Sonraki yenileme: {mins:02d}:{secs:02d}")

    def refresh_data(self):
        self.status_label.setText("🔄 Bilgiler güncelleniyor...")
        self.refresh_btn.setEnabled(False)

        self.worker = WorkerThread(fetch_cswap_accounts)
        self.worker.finished_signal.connect(self._on_data_fetched)
        self.worker.start()

    def _on_data_fetched(self, result):
        accounts, error = result
        self.refresh_btn.setEnabled(True)
        self.next_refresh_seconds = 3600

        now_str = datetime.now().strftime("%H:%M:%S")
        if error:
            self.status_label.setText(f"⚠️ Hata: {error[:30]} ({now_str})")
        else:
            self.accounts = accounts
            if self._pending_best_chrome_launch:
                self._pending_best_chrome_launch = False
                if self.auto_open_chrome:
                    active_acc = next((a for a in accounts if a.is_active), None)
                    if active_acc:
                        self.handle_open_chrome(active_acc.email)

            stale = sum(1 for a in accounts if a.needs_relogin)
            if stale:
                self.status_label.setText(f"⚠️ {stale} hesabın tokeni süresi doldu — yeniden giriş gerekli ({now_str})")
            else:
                self.status_label.setText(f"✓ Son kontrol: {now_str} ({len(accounts)} hesap)")
            self.render_cards()

    def trigger_best_switch(self):
        self._pending_best_chrome_launch = True
        self.best_btn.setEnabled(False)
        self.best_btn.setText("⏳ En iyi hesaba geçiliyor...")

        self.best_worker = WorkerThread(switch_to_best_account)
        self.best_worker.finished_signal.connect(self._on_switch_finished)
        self.best_worker.start()

    def trigger_id_switch(self, acc_id: int):
        self._last_switch_target_id = acc_id
        self.best_btn.setEnabled(False)
        self.best_btn.setText(f"⏳ #{acc_id} hesabına geçiliyor...")

        self.id_worker = WorkerThread(switch_to_account_id, acc_id)
        self.id_worker.finished_signal.connect(self._on_switch_finished)
        self.id_worker.start()

    def _on_switch_finished(self, result):
        success, msg = result
        self.best_btn.setEnabled(True)
        self.apply_best_btn_style()
        self.best_btn.setText("En İyi Hesaba Geç")

        if success and self.auto_open_chrome and self._last_switch_target_id:
            target_acc = next((a for a in self.accounts if a.id == self._last_switch_target_id), None)
            if target_acc:
                self.handle_open_chrome(target_acc.email)
        self._last_switch_target_id = None

        self.refresh_data()

    def render_cards(self):
        while self.card_list_layout.count() > 1:
            item = self.card_list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for acc in self.accounts:
            card = AccountCard(
                acc=acc,
                theme_name=self.theme_name,
                on_switch_callback=self.trigger_id_switch,
                on_chrome_callback=self.handle_open_chrome
            )
            self.card_list_layout.insertWidget(self.card_list_layout.count() - 1, card)

    # --- Drag to move, edge-drag to resize ---
    def _edges_at(self, pos) -> Qt.Edge:
        """Which window edges the cursor is hovering, for frameless resizing."""
        edges = Qt.Edge(0)
        if pos.x() <= RESIZE_MARGIN:
            edges |= Qt.Edge.LeftEdge
        elif pos.x() >= self.width() - RESIZE_MARGIN:
            edges |= Qt.Edge.RightEdge
        if pos.y() <= RESIZE_MARGIN:
            edges |= Qt.Edge.TopEdge
        elif pos.y() >= self.height() - RESIZE_MARGIN:
            edges |= Qt.Edge.BottomEdge
        return edges

    def mousePressEvent(self, event):
        """Hand both move and resize to the OS, so the two can never fight."""
        if event.button() == Qt.MouseButton.LeftButton:
            edges = self._edges_at(event.position().toPoint())
            if edges:
                self.windowHandle().startSystemResize(edges)
            else:
                self.windowHandle().startSystemMove()
            event.accept()

    def mouseMoveEvent(self, event):
        self.setCursor(RESIZE_CURSORS.get(self._edges_at(event.position().toPoint()),
                                          Qt.CursorShape.ArrowCursor))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.save_position()

    def moveEvent(self, event):
        super().moveEvent(event)
        self.save_position()

    def closeEvent(self, event):
        self.save_position()
        super().closeEvent(event)

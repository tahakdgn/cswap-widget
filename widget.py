import sys
import os
import time
from datetime import datetime
from PyQt6.QtCore import Qt, QTimer, QPoint, QThread, pyqtSignal, QSettings
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QScrollArea, QProgressBar, QGraphicsDropShadowEffect,
    QSystemTrayIcon, QMenu
)
from PyQt6.QtGui import QColor, QFont, QAction

from parser import fetch_cswap_accounts, switch_to_best_account, switch_to_account_id, AccountStatus


class WorkerThread(QThread):
    finished_signal = pyqtSignal(object)

    def __init__(self, target_func, *args):
        super().__init__()
        self.target_func = target_func
        self.args = args

    def run(self):
        result = self.target_func(*self.args)
        self.finished_signal.emit(result)


# --- TEMALAR (DARK & LIGHT THEMES) ---
THEMES = {
    "dark": {
        "bg_window": "rgba(22, 27, 34, 0.94)",
        "card_bg": "rgba(33, 38, 45, 0.85)",
        "card_border": "rgba(240, 246, 252, 0.1)",
        "card_active_bg": "rgba(16, 44, 30, 0.85)",
        "card_active_border": "rgba(46, 160, 67, 0.8)",
        "text_primary": "#f0f6fc",
        "text_secondary": "#8b949e",
        "text_muted": "#6e7681",
        "accent": "#58a6ff",
        "accent_hover": "#388bfd",
        "best_btn_bg": "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0d6efd, stop:1 #3d8bfd)",
        "best_btn_hover": "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0b5ed7, stop:1 #0d6efd)",
        "header_btn_bg": "rgba(255, 255, 255, 0.08)",
        "header_btn_hover": "rgba(255, 255, 255, 0.18)",
        "bar_bg": "rgba(255, 255, 255, 0.1)",
        "shadow_color": QColor(0, 0, 0, 160)
    },
    "light": {
        "bg_window": "rgba(246, 248, 250, 0.95)",
        "card_bg": "rgba(255, 255, 255, 0.90)",
        "card_border": "rgba(209, 217, 224, 0.8)",
        "card_active_bg": "rgba(230, 249, 236, 0.95)",
        "card_active_border": "rgba(31, 136, 61, 0.8)",
        "text_primary": "#1f2328",
        "text_secondary": "#57606a",
        "text_muted": "#8c959f",
        "accent": "#0969da",
        "accent_hover": "#0550ae",
        "best_btn_bg": "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0d6efd, stop:1 #3d8bfd)",
        "best_btn_hover": "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0b5ed7, stop:1 #0d6efd)",
        "header_btn_bg": "rgba(0, 0, 0, 0.06)",
        "header_btn_hover": "rgba(0, 0, 0, 0.12)",
        "bar_bg": "rgba(0, 0, 0, 0.08)",
        "shadow_color": QColor(0, 0, 0, 70)
    }
}


def get_progress_color(pct: int) -> str:
    """Kota doluluk oranına göre renk kodu döndürür."""
    if pct < 50:
        return "#2ea043"  # Yeşil
    elif pct < 80:
        return "#d29922"  # Turuncu/Sarı
    else:
        return "#f85149"  # Kırmızı


class AccountCard(QFrame):
    def __init__(self, acc: AccountStatus, theme_name: str, on_switch_callback=None):
        super().__init__()
        self.acc = acc
        self.theme_name = theme_name
        self.theme = THEMES[theme_name]
        self.on_switch_callback = on_switch_callback
        self.init_ui()

    def init_ui(self):
        t = self.theme
        self.setObjectName("accountCard")
        
        is_active = self.acc.is_active
        bg = t["card_active_bg"] if is_active else t["card_bg"]
        border = t["card_active_border"] if is_active else t["card_border"]
        border_width = "2px" if is_active else "1px"

        hover_border = t["card_active_border"] if is_active else t["accent"]
        self.setStyleSheet(f"""
            QFrame#accountCard {{
                background-color: {bg};
                border: {border_width} solid {border};
                border-radius: 14px;
            }}
            QFrame#accountCard:hover {{
                border: {border_width} solid {hover_border};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(8)

        # Üst Satır: E-posta, Aktif Rozeti & Hızlı Geçiş Butonu
        top_row = QHBoxLayout()
        top_row.setSpacing(8)

        # Sıra rozeti (rank badge)
        rank_badge = QLabel(str(self.acc.id))
        rank_color = "#238636" if is_active else t["accent"]
        rank_badge.setFixedSize(22, 22)
        rank_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        rank_badge.setStyleSheet(f"""
            background-color: {rank_color};
            color: #ffffff;
            font-size: 11px;
            font-weight: bold;
            border-radius: 11px;
        """)
        top_row.addWidget(rank_badge)

        # E-posta
        email_label = QLabel(self.acc.email)
        email_label.setStyleSheet(f"font-size: 13px; font-weight: 600; color: {t['text_primary']}; font-family: 'Segoe UI', sans-serif;")
        top_row.addWidget(email_label, 1)

        if is_active:
            active_badge = QLabel("● Aktif Hesap")
            active_badge.setStyleSheet("""
                background-color: #238636;
                color: #ffffff;
                font-weight: bold;
                font-size: 11px;
                padding: 3px 8px;
                border-radius: 10px;
            """)
            top_row.addWidget(active_badge)
        else:
            switch_btn = QPushButton("Geçiş Yap")
            switch_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            switch_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {t['header_btn_bg']};
                    color: {t['accent']};
                    border: 1px solid {t['card_border']};
                    font-size: 11px;
                    padding: 3px 8px;
                    border-radius: 6px;
                }}
                QPushButton:hover {{
                    background-color: {t['accent']};
                    color: #ffffff;
                }}
            """)
            if self.on_switch_callback:
                switch_btn.clicked.connect(lambda: self.on_switch_callback(self.acc.id))
            top_row.addWidget(switch_btn)

        layout.addLayout(top_row)

        # 5 Saatlik (5h) İlerleme Çubuğu
        layout.addLayout(self.create_quota_row(
            title="5 Saatlik Kota",
            pct=self.acc.five_hour_pct,
            reset_time=self.acc.five_hour_reset_time,
            reset_in=self.acc.five_hour_reset_in
        ))

        # 7 Günlük (7d) İlerleme Çubuğu
        layout.addLayout(self.create_quota_row(
            title="7 Günlük Kota",
            pct=self.acc.seven_day_pct,
            reset_time=self.acc.seven_day_reset_time,
            reset_in=self.acc.seven_day_reset_in
        ))

    def create_quota_row(self, title: str, pct: int, reset_time: str, reset_in: str) -> QVBoxLayout:
        t = self.theme
        row_layout = QVBoxLayout()
        row_layout.setSpacing(3)

        info_layout = QHBoxLayout()
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(f"font-size: 11px; color: {t['text_secondary']}; font-weight: 500;")
        
        pct_lbl = QLabel(f"%{pct}")
        bar_color = get_progress_color(pct)
        pct_lbl.setStyleSheet(f"font-size: 11px; font-weight: bold; color: {bar_color};")

        info_layout.addWidget(title_lbl)
        info_layout.addStretch()
        info_layout.addWidget(pct_lbl)
        row_layout.addLayout(info_layout)

        # Progress Bar
        bar = QProgressBar()
        bar.setRange(0, 100)
        bar.setValue(pct)
        bar.setTextVisible(False)
        bar.setFixedHeight(8)
        bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: {t['bar_bg']};
                border-radius: 4px;
                border: none;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {bar_color}, stop:1 {bar_color});
                border-radius: 4px;
            }}
        """)
        row_layout.addWidget(bar)

        # Sıfırlanma süresi bilgisi
        if reset_in:
            time_txt = f"Sıfırlanma: {reset_in} sonra"
            if reset_time:
                time_txt += f" ({reset_time})"
            time_lbl = QLabel(time_txt)
            time_lbl.setStyleSheet(f"font-size: 10px; color: {t['text_muted']};")
            row_layout.addWidget(time_lbl)

        return row_layout


class CSwapWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.settings = QSettings("cswap", "widget")
        self.theme_name = self.settings.value("theme", "dark")
        self.is_pinned = self.settings.value("pinned", True, type=bool)
        self.drag_position = QPoint()
        self.next_refresh_seconds = 3600  # 1 saat (3600 sn)
        self.accounts = []
        self.worker = None

        self.init_window_flags()
        self.init_ui()
        self.restore_position()
        self.init_timers()
        self.init_tray()
        self.refresh_data()

    def init_window_flags(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            (Qt.WindowType.WindowStaysOnTopHint if self.is_pinned else Qt.WindowType.Widget) |
            Qt.WindowType.SubWindow
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setMinimumSize(420, 520)
        self.resize(430, 600)

    def restore_position(self):
        """Son konumu geri yükler; ilk açılışta ekranın sağ üst köşesine sabitler."""
        geo = self.settings.value("geometry")
        if geo is not None:
            self.restoreGeometry(geo)
            return
        screen = QApplication.primaryScreen().availableGeometry()
        margin = 24
        self.move(screen.right() - self.width() - margin, screen.top() + margin)

    def save_position(self):
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("theme", self.theme_name)
        self.settings.setValue("pinned", self.is_pinned)

    def init_ui(self):
        t = THEMES[self.theme_name]

        # Ana layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)

        # Arka plan konteyneri
        self.container = QFrame(self)
        self.container.setObjectName("container")
        self.apply_container_style()

        # Gölge efekti
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(38)
        self.shadow.setColor(t["shadow_color"])
        self.shadow.setOffset(0, 10)
        self.container.setGraphicsEffect(self.shadow)

        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(16, 16, 16, 16)
        container_layout.setSpacing(12)

        # 1. HEADER (Başlık, Pin, Tema, Minimize, Kapat)
        header_layout = QHBoxLayout()
        header_layout.setSpacing(6)

        # Logo / Başlık
        self.title_label = QLabel("Kota Yöneticisi")
        self.title_label.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {t['text_primary']}; font-family: 'Segoe UI', sans-serif; letter-spacing: 0.3px;")
        header_layout.addWidget(self.title_label, 1)

        # Pin Butonu
        self.pin_btn = self.create_header_btn("📌", "Pencereyi Üstte Sabitle")
        self.pin_btn.clicked.connect(self.toggle_pin)
        header_layout.addWidget(self.pin_btn)

        # Tema Değiştirme Butonu (☀️ / 🌙)
        self.theme_btn = self.create_header_btn("☀️" if self.theme_name == "dark" else "🌙", "Temayı Değiştir (Koyu / Açık)")
        self.theme_btn.clicked.connect(self.toggle_theme)
        header_layout.addWidget(self.theme_btn)

        # Küçültme Butonu
        min_btn = self.create_header_btn("—", "Simge Durumuna Küçült")
        min_btn.clicked.connect(self.hide_to_tray)
        header_layout.addWidget(min_btn)

        # Kapat Butonu
        close_btn = self.create_header_btn("✕", "Kapat")
        close_btn.setStyleSheet(close_btn.styleSheet() + "QPushButton:hover { background-color: #da3633; color: white; }")
        close_btn.clicked.connect(QApplication.instance().quit)
        header_layout.addWidget(close_btn)

        container_layout.addLayout(header_layout)

        # 2. EN İYİ HESABA GEÇ BUTONU (BEST STRATEGY)
        self.best_btn = QPushButton("En İyi Hesaba Geç")
        self.best_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.best_btn.setFixedHeight(38)
        self.best_btn.clicked.connect(self.trigger_best_switch)
        self.apply_best_btn_style()
        container_layout.addWidget(self.best_btn)

        # 3. BİLGİ & DURUM ÇUBUĞU (Son güncelleme, geri sayım & yenile butonu)
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

        # 4. HESAP KARTLARI LİSTESİ (Scroll Area)
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

        # 5. ALT BİLGİ (Alt Status)
        self.footer_label = QLabel("⏱️ Otomatik yenileme her saat başı")
        self.footer_label.setStyleSheet(f"font-size: 10px; color: {t['text_muted']}; text-align: center;")
        self.footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(self.footer_label)

        main_layout.addWidget(self.container)

    def create_header_btn(self, text: str, tooltip: str) -> QPushButton:
        t = THEMES[self.theme_name]
        btn = QPushButton(text)
        btn.setToolTip(tooltip)
        btn.setFixedSize(28, 28)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {t['header_btn_bg']};
                color: {t['text_primary']};
                border: 1px solid {t['card_border']};
                border-radius: 6px;
                font-size: 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {t['header_btn_hover']};
            }}
        """)
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

    def init_timers(self):
        # 1 saniyelik geri sayım ve saat sayacı
        self.second_timer = QTimer(self)
        self.second_timer.timeout.connect(self.on_second_tick)
        self.second_timer.start(1000)

        # 1 saatlik otomatik yenileme tetikleyicisi
        self.auto_refresh_timer = QTimer(self)
        self.auto_refresh_timer.timeout.connect(self.refresh_data)
        self.auto_refresh_timer.start(3600 * 1000)

    def init_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        # Basit bir simge çizimi
        self.tray_icon.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_ComputerIcon))
        
        tray_menu = QMenu()
        show_action = QAction("Göster / Gizle", self)
        show_action.triggered.connect(self.toggle_show)
        best_action = QAction("En İyi Hesaba Geç", self)
        best_action.triggered.connect(self.trigger_best_switch)
        refresh_action = QAction("↻ Yenile", self)
        refresh_action.triggered.connect(self.refresh_data)
        quit_action = QAction("Çıkış", self)
        quit_action.triggered.connect(QApplication.instance().quit)

        tray_menu.addAction(show_action)
        tray_menu.addAction(best_action)
        tray_menu.addAction(refresh_action)
        tray_menu.addSeparator()
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.on_tray_activated)
        self.tray_icon.show()

    def hide_to_tray(self):
        self.hide()
        self.tray_icon.showMessage(
            "cswap Widget Arka Planda",
            "Widget sistem tepsisine küçültüldü. Çift tıklayarak tekrar açabilirsiniz.",
            QSystemTrayIcon.MessageIcon.Information,
            2000
        )

    def toggle_show(self):
        if self.isVisible():
            self.hide()
        else:
            self.show()
            self.raise_()
            self.activateWindow()

    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick or reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.toggle_show()

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
        self.shadow.setColor(t["shadow_color"])
        self.apply_container_style()
        self.apply_best_btn_style()
        self.apply_refresh_btn_style()
        self.apply_scroll_style()

        self.title_label.setStyleSheet(f"font-size: 15px; font-weight: bold; color: {t['text_primary']};")
        self.status_label.setStyleSheet(f"font-size: 11px; color: {t['text_secondary']};")
        self.footer_label.setStyleSheet(f"font-size: 10px; color: {t['text_muted']};")
        
        # Header butonlarını güncelle
        for btn in [self.pin_btn, self.theme_btn]:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {t['header_btn_bg']};
                    color: {t['text_primary']};
                    border: 1px solid {t['card_border']};
                    border-radius: 6px;
                    font-size: 12px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {t['header_btn_hover']};
                }}
            """)
            
        self.render_cards()
        self.save_position()

    def on_second_tick(self):
        if self.next_refresh_seconds > 0:
            self.next_refresh_seconds -= 1
        
        mins = self.next_refresh_seconds // 60
        secs = self.next_refresh_seconds % 60
        self.footer_label.setText(f"⏱️ Sonraki yenileme: {mins:02d}:{secs:02d}")

    def refresh_data(self):
        self.status_label.setText("🔄 Bilgiler güncelleniyor...")
        self.refresh_btn.setEnabled(False)

        self.worker = WorkerThread(fetch_cswap_accounts)
        self.worker.finished_signal.connect(self.on_data_fetched)
        self.worker.start()

    def on_data_fetched(self, result):
        accounts, error = result
        self.refresh_btn.setEnabled(True)
        self.next_refresh_seconds = 3600  # Sayacı sıfırla

        now_str = datetime.now().strftime("%H:%M:%S")
        if error:
            self.status_label.setText(f"⚠️ Hata: {error[:30]} ({now_str})")
        else:
            self.accounts = accounts
            self.status_label.setText(f"✓ Son kontrol: {now_str} ({len(accounts)} hesap)")
            self.render_cards()

    def trigger_best_switch(self):
        self.best_btn.setEnabled(False)
        self.best_btn.setText("⏳ En iyi hesaba geçiliyor...")
        
        self.best_worker = WorkerThread(switch_to_best_account)
        self.best_worker.finished_signal.connect(self.on_switch_finished)
        self.best_worker.start()

    def trigger_id_switch(self, acc_id: int):
        self.best_btn.setEnabled(False)
        self.best_btn.setText(f"⏳ #{acc_id} hesabına geçiliyor...")
        
        self.id_worker = WorkerThread(switch_to_account_id, acc_id)
        self.id_worker.finished_signal.connect(self.on_switch_finished)
        self.id_worker.start()

    def on_switch_finished(self, result):
        success, msg = result
        self.best_btn.setEnabled(True)
        self.apply_best_btn_style()
        self.best_btn.setText("En İyi Hesaba Geç")
        
        # Sonucu durum çubuğunda göster ve listeyi yenile
        self.refresh_data()

    def render_cards(self):
        # Önceki kartları temizle
        while self.card_list_layout.count() > 1:
            item = self.card_list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for acc in self.accounts:
            card = AccountCard(
                acc=acc,
                theme_name=self.theme_name,
                on_switch_callback=self.trigger_id_switch
            )
            # Kartı listenin başına (stretch'ten önce) ekle
            self.card_list_layout.insertWidget(self.card_list_layout.count() - 1, card)

    # --- PENCERE SÜRÜKLEME (DRAG & DROP) ---
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        # Sürükleme bitince konumu kalıcı olarak kaydet (sabit dursun)
        self.save_position()
        event.accept()

    def closeEvent(self, event):
        self.save_position()
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    # Modern font ayarı
    font = QFont("Segoe UI", 9)
    app.setFont(font)
    
    widget = CSwapWidget()
    widget.show()
    app.aboutToQuit.connect(widget.save_position)

    sys.exit(app.exec())

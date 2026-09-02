from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QProgressBar, QSizePolicy
)
from ..core.models import AccountStatus
from .themes import THEMES, get_progress_color


class AccountCard(QFrame):
    """Component rendering a single Claude account card with quota progress bars and actions."""

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

        # Top row: Rank badge, email, active badge or switch button
        top_row = QHBoxLayout()
        top_row.setSpacing(8)

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

        email_label = QLabel(self.acc.email)
        email_label.setStyleSheet(
            f"font-size: 13px; font-weight: 600; color: {t['text_primary']}; font-family: 'Segoe UI', sans-serif;"
        )
        # Let the email shrink instead of forcing the card wider than the window
        email_label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        email_label.setToolTip(self.acc.email)
        top_row.addWidget(email_label, 1)

        if self.acc.needs_relogin:
            relogin_badge = QLabel("⚠ Yeniden giriş")
            relogin_badge.setToolTip(
                "Token süresi doldu — bu hesabın verileri eski.\n"
                "Claude Code'da /login ile bu hesaba gir, sonra: cswap add"
            )
            relogin_badge.setStyleSheet("""
                background-color: #b91c1c;
                color: #ffffff;
                font-weight: bold;
                font-size: 10px;
                padding: 2px 8px;
                border-radius: 8px;
            """)
            top_row.addWidget(relogin_badge)

        # Plan Rozeti (MAX PLAN veya PRO)
        if self.acc.is_max_plan:
            plan_badge = QLabel("MAX")
            plan_badge.setStyleSheet("""
                background-color: rgba(124, 58, 237, 0.16);
                color: #a78bfa;
                border: 1px solid rgba(124, 58, 237, 0.45);
                font-weight: 600;
                font-size: 10px;
                letter-spacing: 0.5px;
                padding: 2px 7px;
                border-radius: 6px;
            """)
            top_row.addWidget(plan_badge)
        else:
            pro_badge = QLabel("PRO")
            pro_badge.setStyleSheet(f"""
                background-color: {t['header_btn_bg']};
                color: {t['text_secondary']};
                border: 1px solid {t['card_border']};
                font-weight: bold;
                font-size: 10px;
                padding: 2px 6px;
                border-radius: 8px;
            """)
            top_row.addWidget(pro_badge)

        if is_active:
            active_badge = QLabel("● Aktif")
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

        # 5-hour quota bar
        layout.addLayout(self._create_quota_row(
            title="5 Saatlik Kota" + (" (eski veri)" if self.acc.needs_relogin else ""),
            pct=self.acc.five_hour_pct,
            reset_time=self.acc.five_hour_reset_time,
            reset_in=self.acc.five_hour_reset_in
        ))

        # 7-day quota bar
        layout.addLayout(self._create_quota_row(
            title="7 Günlük Kota" + (" (eski veri)" if self.acc.needs_relogin else ""),
            pct=self.acc.seven_day_pct,
            reset_time=self.acc.seven_day_reset_time,
            reset_in=self.acc.seven_day_reset_in
        ))

        # Scoped / Fable Model Quotas
        for scoped in self.acc.scoped_quotas:
            layout.addLayout(self._create_quota_row(
                title=f"{scoped.name} Modeli Kotası",
                pct=scoped.pct,
                reset_time=None,
                reset_in=None
            ))


    def _create_quota_row(self, title: str, pct: int, reset_time: str, reset_in: str) -> QVBoxLayout:
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

        if reset_in:
            time_txt = f"Sıfırlanma: {reset_in} sonra"
            if reset_time:
                time_txt += f" ({reset_time})"
            time_lbl = QLabel(time_txt)
            time_lbl.setStyleSheet(f"font-size: 10px; color: {t['text_muted']};")
            row_layout.addWidget(time_lbl)

        return row_layout

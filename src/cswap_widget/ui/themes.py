from PyQt6.QtGui import QColor

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
        "shadow_color": QColor(0, 0, 0, 160),
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
        "shadow_color": QColor(0, 0, 0, 70),
    },
}


def get_progress_color(pct: int) -> str:
    """Returns color code based on quota percentage."""
    if pct < 50:
        return "#2ea043"  # Green
    elif pct < 80:
        return "#d29922"  # Yellow / Orange
    else:
        return "#f85149"  # Red

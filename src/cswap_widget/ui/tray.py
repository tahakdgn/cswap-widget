from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PyQt6.QtGui import QAction


class SystemTrayManager:
    """Manages the system tray icon, notification balloon, and context menu."""

    def __init__(self, parent_widget):
        self.parent = parent_widget
        self.tray_icon = QSystemTrayIcon(parent_widget)
        self._init_tray()

    def _init_tray(self):
        # Set default system icon
        icon = self.parent.style().standardIcon(
            self.parent.style().StandardPixmap.SP_ComputerIcon
        )
        self.tray_icon.setIcon(icon)

        tray_menu = QMenu()
        show_action = QAction("Göster / Gizle", self.parent)
        show_action.triggered.connect(self.parent.toggle_show)

        best_action = QAction("En İyi Hesaba Geç", self.parent)
        best_action.triggered.connect(self.parent.trigger_best_switch)

        chrome_action = QAction("🌐 Aktif Hesabı Chrome'da Aç", self.parent)
        chrome_action.triggered.connect(self._open_active_in_chrome)

        refresh_action = QAction("↻ Yenile", self.parent)
        refresh_action.triggered.connect(self.parent.refresh_data)

        quit_action = QAction("Çıkış", self.parent)
        quit_action.triggered.connect(QApplication.instance().quit)

        tray_menu.addAction(show_action)
        tray_menu.addAction(best_action)
        tray_menu.addAction(chrome_action)
        tray_menu.addAction(refresh_action)
        tray_menu.addSeparator()
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self._on_activated)
        self.tray_icon.show()

    def _on_activated(self, reason):
        if reason in (
            QSystemTrayIcon.ActivationReason.DoubleClick,
            QSystemTrayIcon.ActivationReason.Trigger
        ):
            self.parent.toggle_show()

    def show_message(self, title: str, message: str, msecs: int = 2000):
        self.tray_icon.showMessage(
            title,
            message,
            QSystemTrayIcon.MessageIcon.Information,
            msecs
        )

    def _open_active_in_chrome(self):
        active_acc = next((a for a in getattr(self.parent, "accounts", []) if a.is_active), None)
        if active_acc:
            self.parent.handle_open_chrome(active_acc.email)
        elif getattr(self.parent, "accounts", []):
            self.parent.handle_open_chrome(self.parent.accounts[0].email)

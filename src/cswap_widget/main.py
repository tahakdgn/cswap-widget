import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont
from .ui.widget import CSwapWidget


def main():
    """Application entrypoint."""
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    font = QFont("Segoe UI", 9)
    app.setFont(font)

    widget = CSwapWidget()
    widget.show()
    app.aboutToQuit.connect(widget.save_position)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()

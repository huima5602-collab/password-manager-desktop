import os
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication

from ui.main_window import MainWindow


def resource_path(relative_path):
    base_path = getattr(sys, "_MEIPASS", os.path.abspath("."))
    return os.path.join(base_path, relative_path)


def load_stylesheet():
    style_path = resource_path(os.path.join("resources", "style.qss"))
    try:
        with open(style_path, "r", encoding="utf-8") as handle:
            return handle.read()
    except OSError:
        return ""


def main():
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    app = QApplication(sys.argv)
    app.setApplicationName("密码生成与管理器")
    app.setOrganizationName("PasswordManager")
    app.setStyle("Fusion")
    app.setStyleSheet(load_stylesheet())
    icon = QIcon(resource_path(os.path.join("resources", "icon.ico")))
    app.setWindowIcon(icon)

    window = MainWindow()
    window.setWindowIcon(icon)
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

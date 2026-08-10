import sys

from PySide6.QtWidgets import QApplication

from openinteriorcad.desktop.main_window import MainWindow


def run() -> int:
    app = QApplication(sys.argv)

    app.setApplicationName("OpenInteriorCAD")
    app.setOrganizationName("OpenInteriorCAD")

    window = MainWindow()
    window.show()

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(run())
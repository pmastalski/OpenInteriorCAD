from PySide6.QtWidgets import QLabel, QMainWindow

from openinteriorcad.desktop.cad_view import CadView


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("OpenInteriorCAD Desktop 0.1")
        self.resize(1400, 900)

        self.cad_view = CadView()
        self.setCentralWidget(self.cad_view)

        self.coordinate_label = QLabel(
            "X: 0 mm    Y: 0 mm"
        )

        self.statusBar().addPermanentWidget(
            self.coordinate_label
        )

        self.cad_view.mouse_position_changed.connect(
            self.update_coordinates
        )

    def update_coordinates(
        self,
        x: float,
        y: float,
    ) -> None:
        self.coordinate_label.setText(
            f"X: {x:.0f} mm    Y: {y:.0f} mm"
        )
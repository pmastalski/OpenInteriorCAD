"""Task panel for numerical OpenInteriorCAD room drawing."""

import FreeCADGui as Gui
from PySide import QtWidgets


class WallDrawingPanel:
    """FreeCAD Task Panel for numerical room drawing."""

    def __init__(self, tool):
        self.tool = tool

        self.form = QtWidgets.QWidget()
        self.form.setWindowTitle(
            "Rysowanie pomieszczenia"
        )

        self._build_ui()

    def _build_ui(self):
        main_layout = QtWidgets.QVBoxLayout(
            self.form
        )

        title = QtWidgets.QLabel(
            "<b>OpenInteriorCAD</b><br>"
            "Rysowanie pomieszczenia"
        )

        main_layout.addWidget(
            title
        )

        self.status_label = QtWidgets.QLabel(
            "Kliknij w widoku pierwszy narożnik."
        )

        self.status_label.setWordWrap(
            True
        )

        main_layout.addWidget(
            self.status_label
        )

        # --------------------------------------------------
        # AKTUALNY STAN
        # --------------------------------------------------

        current_group = QtWidgets.QGroupBox(
            "Aktualny stan"
        )

        current_layout = QtWidgets.QFormLayout(
            current_group
        )

        self.wall_count_label = QtWidgets.QLabel(
            "0"
        )

        current_layout.addRow(
            "Liczba ścian:",
            self.wall_count_label,
        )

        self.heading_label = QtWidgets.QLabel(
            "—"
        )

        current_layout.addRow(
            "Kierunek:",
            self.heading_label,
        )

        main_layout.addWidget(
            current_group
        )

        # --------------------------------------------------
        # PARAMETRY NOWEJ ŚCIANY
        # --------------------------------------------------

        dimensions_group = QtWidgets.QGroupBox(
            "Nowa ściana"
        )

        dimensions_layout = QtWidgets.QFormLayout(
            dimensions_group
        )

        self.length_input = QtWidgets.QDoubleSpinBox()

        self.length_input.setRange(
            1.0,
            100000.0,
        )

        self.length_input.setDecimals(
            0
        )

        self.length_input.setValue(
            4000.0
        )

        self.length_input.setSuffix(
            " mm"
        )

        dimensions_layout.addRow(
            "Długość:",
            self.length_input,
        )

        self.angle_input = QtWidgets.QDoubleSpinBox()

        self.angle_input.setRange(
            -360.0,
            360.0,
        )

        self.angle_input.setDecimals(
            1
        )

        self.angle_input.setValue(
            0.0
        )

        self.angle_input.setSuffix(
            "°"
        )

        dimensions_layout.addRow(
            "Kąt:",
            self.angle_input,
        )

        self.angle_description = QtWidgets.QLabel(
            "Pierwsza ściana: kąt względem osi X."
        )

        self.angle_description.setWordWrap(
            True
        )

        dimensions_layout.addRow(
            self.angle_description
        )

        # --------------------------------------------------
        # SZYBKIE KĄTY
        # --------------------------------------------------

        angle_buttons_layout = QtWidgets.QHBoxLayout()

        self.right_button = QtWidgets.QPushButton(
            "-90°"
        )

        self.straight_button = QtWidgets.QPushButton(
            "0°"
        )

        self.left_button = QtWidgets.QPushButton(
            "+90°"
        )

        self.reverse_button = QtWidgets.QPushButton(
            "180°"
        )

        angle_buttons_layout.addWidget(
            self.right_button
        )

        angle_buttons_layout.addWidget(
            self.straight_button
        )

        angle_buttons_layout.addWidget(
            self.left_button
        )

        angle_buttons_layout.addWidget(
            self.reverse_button
        )

        dimensions_layout.addRow(
            angle_buttons_layout
        )

        # --------------------------------------------------
        # GRUBOŚĆ
        # --------------------------------------------------

        self.thickness_input = QtWidgets.QDoubleSpinBox()

        self.thickness_input.setRange(
            1.0,
            5000.0,
        )

        self.thickness_input.setDecimals(
            0
        )

        self.thickness_input.setValue(
            120.0
        )

        self.thickness_input.setSuffix(
            " mm"
        )

        dimensions_layout.addRow(
            "Grubość:",
            self.thickness_input,
        )

        # --------------------------------------------------
        # WYSOKOŚĆ
        # --------------------------------------------------

        self.height_input = QtWidgets.QDoubleSpinBox()

        self.height_input.setRange(
            1.0,
            20000.0,
        )

        self.height_input.setDecimals(
            0
        )

        self.height_input.setValue(
            2600.0
        )

        self.height_input.setSuffix(
            " mm"
        )

        dimensions_layout.addRow(
            "Wysokość:",
            self.height_input,
        )

        main_layout.addWidget(
            dimensions_group
        )

        # --------------------------------------------------
        # DODAJ ŚCIANĘ
        # --------------------------------------------------

        self.add_wall_button = QtWidgets.QPushButton(
            "Dodaj ścianę"
        )

        self.add_wall_button.setEnabled(
            False
        )

        main_layout.addWidget(
            self.add_wall_button
        )

        # --------------------------------------------------
        # COFNIJ
        # --------------------------------------------------

        self.undo_wall_button = QtWidgets.QPushButton(
            "Cofnij ostatnią ścianę"
        )

        self.undo_wall_button.setEnabled(
            False
        )

        main_layout.addWidget(
            self.undo_wall_button
        )

        # --------------------------------------------------
        # ZAMKNIJ POMIESZCZENIE
        # --------------------------------------------------

        self.close_room_button = QtWidgets.QPushButton(
            "Zamknij pomieszczenie"
        )

        self.close_room_button.setEnabled(
            False
        )

        main_layout.addWidget(
            self.close_room_button
        )

        # --------------------------------------------------
        # NOWY PUNKT STARTOWY
        # --------------------------------------------------

        self.new_start_button = QtWidgets.QPushButton(
            "Wskaż nowy punkt startowy"
        )

        main_layout.addWidget(
            self.new_start_button
        )

        main_layout.addStretch()

        # --------------------------------------------------
        # ZAMKNIJ PANEL
        # --------------------------------------------------

        self.close_button = QtWidgets.QPushButton(
            "Zamknij"
        )

        self.close_button.setToolTip(
            "Kończy rysowanie i zamyka panel."
        )

        main_layout.addWidget(
            self.close_button
        )

        # --------------------------------------------------
        # SYGNAŁY
        # --------------------------------------------------

        self.right_button.clicked.connect(
            lambda: self.angle_input.setValue(
                -90.0
            )
        )

        self.straight_button.clicked.connect(
            lambda: self.angle_input.setValue(
                0.0
            )
        )

        self.left_button.clicked.connect(
            lambda: self.angle_input.setValue(
                90.0
            )
        )

        self.reverse_button.clicked.connect(
            lambda: self.angle_input.setValue(
                180.0
            )
        )

        self.add_wall_button.clicked.connect(
            self._add_wall
        )

        self.undo_wall_button.clicked.connect(
            self._undo_wall
        )

        self.close_room_button.clicked.connect(
            self._close_room
        )

        self.new_start_button.clicked.connect(
            self._request_new_start
        )

        self.close_button.clicked.connect(
            self._close_panel
        )

    # ------------------------------------------------------
    # OBSŁUGA PRZYCISKÓW
    # ------------------------------------------------------

    def _add_wall(self):
        self.tool.add_wall(
            length=self.length_input.value(),
            relative_angle=self.angle_input.value(),
            thickness=self.thickness_input.value(),
            height=self.height_input.value(),
        )

    def _undo_wall(self):
        self.tool.undo_last_wall()

    def _close_room(self):
        self.tool.close_current_room(
            thickness=self.thickness_input.value(),
            height=self.height_input.value(),
        )

    def _request_new_start(self):
        self.tool.request_start_point()

    def _close_panel(self):
        """
        Completely finish room drawing and close
        the FreeCAD Task Panel.
        """

        self.tool.stop(
            close_panel=True
        )

    # ------------------------------------------------------
    # STANY PANELU
    # ------------------------------------------------------

    def set_start_point_ready(self):
        self.status_label.setText(
            "Punkt startowy ustawiony. "
            "Podaj parametry pierwszej ściany."
        )

        self.wall_count_label.setText(
            "0"
        )

        self.heading_label.setText(
            "—"
        )

        self.add_wall_button.setEnabled(
            True
        )

        self.undo_wall_button.setEnabled(
            False
        )

        self.close_room_button.setEnabled(
            False
        )

        self.angle_input.setValue(
            0.0
        )

        self.angle_description.setText(
            "Pierwsza ściana: kąt względem osi X."
        )

    def set_wall_added(
        self,
        wall_count,
        heading,
    ):
        self.status_label.setText(
            f"Ściana {wall_count} utworzona."
        )

        self.wall_count_label.setText(
            str(wall_count)
        )

        self.heading_label.setText(
            f"{heading:.1f}°"
        )

        self.angle_description.setText(
            "Kąt względem poprzedniej ściany. "
            "+90° = w lewo, -90° = w prawo."
        )

        self.undo_wall_button.setEnabled(
            True
        )

        self.close_room_button.setEnabled(
            wall_count >= 2
        )

        self.angle_input.setValue(
            90.0
        )

        self.length_input.setFocus()

        self.length_input.selectAll()

    def set_after_undo(
        self,
        wall_count,
        heading,
    ):
        self.wall_count_label.setText(
            str(wall_count)
        )

        if heading is None:
            self.heading_label.setText(
                "—"
            )

            self.angle_input.setValue(
                0.0
            )

        else:
            self.heading_label.setText(
                f"{heading:.1f}°"
            )

            self.angle_input.setValue(
                90.0
            )

        self.undo_wall_button.setEnabled(
            wall_count > 0
        )

        self.close_room_button.setEnabled(
            wall_count >= 2
        )

        self.status_label.setText(
            "Ostatnia ściana została cofnięta."
        )

    def set_room_closed(self):
        self.status_label.setText(
            "Pomieszczenie zamknięte. "
            "Kliknij pierwszy narożnik "
            "następnego pomieszczenia."
        )

        self.wall_count_label.setText(
            "0"
        )

        self.heading_label.setText(
            "—"
        )

        self.add_wall_button.setEnabled(
            False
        )

        self.undo_wall_button.setEnabled(
            False
        )

        self.close_room_button.setEnabled(
            False
        )

        self.angle_input.setValue(
            0.0
        )

    def set_waiting_for_start(self):
        self.status_label.setText(
            "Kliknij w widoku pierwszy narożnik."
        )

        self.wall_count_label.setText(
            "0"
        )

        self.heading_label.setText(
            "—"
        )

        self.add_wall_button.setEnabled(
            False
        )

        self.undo_wall_button.setEnabled(
            False
        )

        self.close_room_button.setEnabled(
            False
        )

    # ------------------------------------------------------
    # FREECAD TASK PANEL
    # ------------------------------------------------------

    def getStandardButtons(self):
        return 0

    def accept(self):
        self.tool.stop(
            close_panel=False
        )

        return True

    def reject(self):
        self.tool.stop(
            close_panel=False
        )

        return True
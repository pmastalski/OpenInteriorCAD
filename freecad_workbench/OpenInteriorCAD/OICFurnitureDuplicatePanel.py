"""Panel for duplicating OpenInteriorCAD furniture."""

import FreeCADGui as Gui
from PySide import QtWidgets

from OICFurnitureDuplicate import (
    duplicate_furniture,
)


class FurnitureDuplicatePanel:
    """Choose duplication direction."""

    def __init__(
        self,
        furniture,
    ):
        self.furniture = furniture

        self.form = QtWidgets.QWidget()

        self.form.setWindowTitle(
            "Duplikuj szafkę"
        )

        self._build_ui()

    def _build_ui(self):
        layout = QtWidgets.QVBoxLayout(
            self.form
        )

        title = QtWidgets.QLabel(
            "<b>OpenInteriorCAD</b><br>"
            "Duplikuj szafkę"
        )

        layout.addWidget(
            title
        )

        info = QtWidgets.QLabel(
            f"Wybrany mebel: "
            f"<b>{self.furniture.Label}</b><br><br>"
            "Wybierz stronę, po której ma zostać "
            "utworzona kopia."
        )

        info.setWordWrap(
            True
        )

        layout.addWidget(
            info
        )

        buttons = QtWidgets.QHBoxLayout()

        self.left_button = QtWidgets.QPushButton(
            "← Lewo"
        )

        self.right_button = QtWidgets.QPushButton(
            "Prawo →"
        )

        buttons.addWidget(
            self.left_button
        )

        buttons.addWidget(
            self.right_button
        )

        layout.addLayout(
            buttons
        )

        self.status_label = QtWidgets.QLabel(
            ""
        )

        self.status_label.setWordWrap(
            True
        )

        layout.addWidget(
            self.status_label
        )

        self.close_button = QtWidgets.QPushButton(
            "Zamknij"
        )

        layout.addWidget(
            self.close_button
        )

        layout.addStretch()

        self.left_button.clicked.connect(
            self._duplicate_left
        )

        self.right_button.clicked.connect(
            self._duplicate_right
        )

        self.close_button.clicked.connect(
            self._close
        )

    def _duplicate_left(self):
        self._duplicate(
            "left"
        )

    def _duplicate_right(self):
        self._duplicate(
            "right"
        )

    def _duplicate(
        self,
        side,
    ):
        document = (
            self.furniture.Document
        )

        document.openTransaction(
            "Duplikuj szafkę"
        )

        try:
            new_furniture = (
                duplicate_furniture(
                    self.furniture,
                    side=side,
                )
            )

            document.commitTransaction()

        except Exception as error:
            document.abortTransaction()

            self.status_label.setText(
                f"Błąd: {error}"
            )

            return

        if new_furniture is None:
            return

        # Nowa szafka staje się kolejnym źródłem.
        # Dzięki temu można szybko klikać Prawo →
        # i budować cały ciąg.
        self.furniture = (
            new_furniture
        )

        Gui.Selection.clearSelection()

        Gui.Selection.addSelection(
            new_furniture
        )

        if side == "left":
            self.status_label.setText(
                "Utworzono szafkę po lewej stronie."
            )

        else:
            self.status_label.setText(
                "Utworzono szafkę po prawej stronie."
            )

    def _close(self):
        Gui.Control.closeDialog()

    def getStandardButtons(self):
        return 0

    def accept(self):
        return True

    def reject(self):
        return True
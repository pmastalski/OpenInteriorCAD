from PySide6.QtGui import QAction, QActionGroup, QKeySequence
from PySide6.QtWidgets import (
    QLabel,
    QMainWindow,
    QToolBar,
)

from openinteriorcad.desktop.cad_view import CadView
from openinteriorcad.desktop.tools.select_tool import SelectTool
from openinteriorcad.desktop.tools.wall_tool import WallTool


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle(
            "OpenInteriorCAD Desktop 0.3"
        )

        self.resize(
            1400,
            900,
        )

        self.cad_view = CadView()

        self.setCentralWidget(
            self.cad_view
        )

        self._create_toolbar()
        self._create_edit_actions()

        self.coordinate_label = QLabel(
            "X: 0 mm    Y: 0 mm"
        )

        self.statusBar().addPermanentWidget(
            self.coordinate_label
        )

        self.cad_view.mouse_position_changed.connect(
            self.update_coordinates
        )

    def _create_toolbar(self) -> None:
        toolbar = QToolBar(
            "Tools"
        )

        toolbar.setMovable(
            False
        )

        self.addToolBar(
            toolbar
        )

        self.tool_group = QActionGroup(
            self
        )

        self.tool_group.setExclusive(
            True
        )

        self.select_action = QAction(
            "Zaznacz",
            self,
        )

        self.select_action.setCheckable(
            True
        )

        self.select_action.setChecked(
            True
        )

        self.wall_action = QAction(
            "Ściana",
            self,
        )

        self.wall_action.setCheckable(
            True
        )

        self.tool_group.addAction(
            self.select_action
        )

        self.tool_group.addAction(
            self.wall_action
        )

        toolbar.addAction(
            self.select_action
        )

        toolbar.addAction(
            self.wall_action
        )

        self.select_action.triggered.connect(
            self.activate_select_tool
        )

        self.wall_action.triggered.connect(
            self.activate_wall_tool
        )

    def _create_edit_actions(self) -> None:
        self.undo_action = QAction(
            "Cofnij",
            self,
        )

        self.undo_action.setShortcut(
            QKeySequence.StandardKey.Undo
        )

        self.redo_action = QAction(
            "Ponów",
            self,
        )

        self.redo_action.setShortcut(
            QKeySequence.StandardKey.Redo
        )

        self.undo_action.triggered.connect(
            self.cad_view.undo
        )

        self.redo_action.triggered.connect(
            self.cad_view.redo
        )

        self.addAction(
            self.undo_action
        )

        self.addAction(
            self.redo_action
        )

    def activate_select_tool(self) -> None:
        self.cad_view.set_tool(
            SelectTool(
                self.cad_view
            )
        )

    def activate_wall_tool(self) -> None:
        self.cad_view.set_tool(
            WallTool(
                self.cad_view
            )
        )

    def update_coordinates(
        self,
        x: float,
        y: float,
    ) -> None:
        self.coordinate_label.setText(
            f"X: {x:.0f} mm    Y: {y:.0f} mm"
        )
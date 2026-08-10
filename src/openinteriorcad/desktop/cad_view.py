from PySide6.QtCore import QPoint, Qt, Signal
from PySide6.QtGui import QPainter, QPen
from PySide6.QtWidgets import (
    QGraphicsScene,
    QGraphicsView,
)

from openinteriorcad.domain.room import Room
from openinteriorcad.domain.vertex2d import Vertex2D
from openinteriorcad.domain.wall import Wall
from openinteriorcad.geometry.point2d import Point2D


class CadView(QGraphicsView):
    mouse_position_changed = Signal(
        float,
        float,
    )

    def __init__(self) -> None:
        super().__init__()

        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)

        self._scene.setSceneRect(
            -50000,
            -50000,
            100000,
            100000,
        )

        self.setRenderHint(
            QPainter.RenderHint.Antialiasing
        )

        self.setMouseTracking(True)

        self.setTransformationAnchor(
            QGraphicsView.ViewportAnchor.AnchorUnderMouse
        )

        self.setResizeAnchor(
            QGraphicsView.ViewportAnchor.AnchorUnderMouse
        )

        self.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        self.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        self._panning = False
        self._pan_start = QPoint()

        self.scale(
            0.15,
            0.15,
        )

        self.room = self._create_demo_room()

        self.render_room(
            self.room
        )

    def _create_demo_room(self) -> Room:
        v1 = Vertex2D(
            position=Point2D(
                0,
                0,
            )
        )

        v2 = Vertex2D(
            position=Point2D(
                4000,
                0,
            )
        )

        v3 = Vertex2D(
            position=Point2D(
                4000,
                3000,
            )
        )

        v4 = Vertex2D(
            position=Point2D(
                0,
                3000,
            )
        )

        room = Room(
            name="Demo room"
        )

        room.add_wall(
            Wall(
                name="Wall 1",
                start_vertex=v1,
                end_vertex=v2,
            )
        )

        room.add_wall(
            Wall(
                name="Wall 2",
                start_vertex=v2,
                end_vertex=v3,
            )
        )

        room.add_wall(
            Wall(
                name="Wall 3",
                start_vertex=v3,
                end_vertex=v4,
            )
        )

        room.add_wall(
            Wall(
                name="Wall 4",
                start_vertex=v4,
                end_vertex=v1,
            )
        )

        return room

    def render_room(
        self,
        room: Room,
    ) -> None:
        self._scene.clear()

        pen = QPen()
        pen.setWidthF(
            25
        )

        for wall in room.walls:
            self._scene.addLine(
                wall.start.x,
                wall.start.y,
                wall.end.x,
                wall.end.y,
                pen,
            )

    def drawBackground(
        self,
        painter,
        rect,
    ) -> None:
        minor_grid = 100
        major_grid = 1000

        minor_pen = QPen()
        minor_pen.setWidthF(0)

        painter.setPen(
            minor_pen
        )

        left = (
            int(rect.left())
            - int(rect.left()) % minor_grid
        )

        top = (
            int(rect.top())
            - int(rect.top()) % minor_grid
        )

        x = left

        while x < rect.right():
            if x % major_grid != 0:
                painter.drawLine(
                    x,
                    rect.top(),
                    x,
                    rect.bottom(),
                )

            x += minor_grid

        y = top

        while y < rect.bottom():
            if y % major_grid != 0:
                painter.drawLine(
                    rect.left(),
                    y,
                    rect.right(),
                    y,
                )

            y += minor_grid

        major_pen = QPen()
        major_pen.setWidthF(0)

        painter.setPen(
            major_pen
        )

        left = (
            int(rect.left())
            - int(rect.left()) % major_grid
        )

        top = (
            int(rect.top())
            - int(rect.top()) % major_grid
        )

        x = left

        while x < rect.right():
            painter.drawLine(
                x,
                rect.top(),
                x,
                rect.bottom(),
            )

            x += major_grid

        y = top

        while y < rect.bottom():
            painter.drawLine(
                rect.left(),
                y,
                rect.right(),
                y,
            )

            y += major_grid

    def wheelEvent(
        self,
        event,
    ) -> None:
        factor = (
            1.15
            if event.angleDelta().y() > 0
            else 1 / 1.15
        )

        current_scale = (
            self.transform().m11()
        )

        new_scale = (
            current_scale
            * factor
        )

        if not 0.02 <= new_scale <= 10:
            return

        self.scale(
            factor,
            factor,
        )

    def mousePressEvent(
        self,
        event,
    ) -> None:
        if (
            event.button()
            == Qt.MouseButton.MiddleButton
        ):
            self._panning = True
            self._pan_start = (
                event.position().toPoint()
            )

            self.setCursor(
                Qt.CursorShape.ClosedHandCursor
            )

            event.accept()
            return

        super().mousePressEvent(
            event
        )

    def mouseMoveEvent(
        self,
        event,
    ) -> None:
        position = self.mapToScene(
            event.position().toPoint()
        )

        self.mouse_position_changed.emit(
            position.x(),
            position.y(),
        )

        if self._panning:
            current = (
                event.position().toPoint()
            )

            delta = (
                current
                - self._pan_start
            )

            self._pan_start = current

            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value()
                - delta.x()
            )

            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value()
                - delta.y()
            )

            event.accept()
            return

        super().mouseMoveEvent(
            event
        )

    def mouseReleaseEvent(
        self,
        event,
    ) -> None:
        if (
            event.button()
            == Qt.MouseButton.MiddleButton
        ):
            self._panning = False

            self.setCursor(
                Qt.CursorShape.ArrowCursor
            )

            event.accept()
            return

        super().mouseReleaseEvent(
            event
        )
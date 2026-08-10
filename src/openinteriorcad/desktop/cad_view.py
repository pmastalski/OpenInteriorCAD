from PySide6.QtCore import QPoint, QPointF, Qt, Signal
from PySide6.QtGui import QKeyEvent, QPainter, QPen
from PySide6.QtWidgets import (
    QGraphicsScene,
    QGraphicsView,
)

from openinteriorcad.commands.history import CommandHistory
from openinteriorcad.desktop.tools.base_tool import BaseTool
from openinteriorcad.desktop.tools.select_tool import SelectTool
from openinteriorcad.domain.room import Room
from openinteriorcad.domain.vertex2d import Vertex2D
from openinteriorcad.domain.wall import Wall
from openinteriorcad.geometry.point2d import Point2D


class CadView(QGraphicsView):
    mouse_position_changed = Signal(
        float,
        float,
    )

    SNAP_SIZE = 100.0
    VERTEX_SNAP_DISTANCE = 150.0

    def __init__(self) -> None:
        super().__init__()

        self.graphics_scene = QGraphicsScene(
            self
        )

        self.setScene(
            self.graphics_scene
        )

        self.graphics_scene.setSceneRect(
            -50000,
            -50000,
            100000,
            100000,
        )

        self.setRenderHint(
            QPainter.RenderHint.Antialiasing
        )

        self.setMouseTracking(
            True
        )

        self.setFocusPolicy(
            Qt.FocusPolicy.StrongFocus
        )

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

        self.command_history = CommandHistory()

        self.active_tool: BaseTool = SelectTool(
            self
        )

        self.active_tool.activate()

        self.render_room(
            self.room
        )

    def set_tool(
        self,
        tool: BaseTool,
    ) -> None:
        self.active_tool.deactivate()

        self.active_tool = tool

        self.active_tool.activate()

    def snap_position(
        self,
        position: QPointF,
    ) -> Point2D:
        vertex = self.find_nearby_vertex(
            position
        )

        if vertex is not None:
            return vertex.position

        x = round(
            position.x() / self.SNAP_SIZE
        ) * self.SNAP_SIZE

        y = round(
            position.y() / self.SNAP_SIZE
        ) * self.SNAP_SIZE

        return Point2D(
            x,
            y,
        )

    def find_nearby_vertex(
        self,
        position: QPointF,
    ) -> Vertex2D | None:
        cursor_point = Point2D(
            position.x(),
            position.y(),
        )

        closest_vertex = None
        closest_distance = (
            self.VERTEX_SNAP_DISTANCE
        )

        for vertex in self.room.vertices:
            distance = (
                cursor_point.distance_to(
                    vertex.position
                )
            )

            if distance <= closest_distance:
                closest_vertex = vertex
                closest_distance = distance

        return closest_vertex

    def get_or_create_vertex(
        self,
        position: QPointF,
    ) -> Vertex2D:
        existing_vertex = (
            self.find_nearby_vertex(
                position
            )
        )

        if existing_vertex is not None:
            return existing_vertex

        snapped_position = self.snap_position(
            position
        )

        for vertex in self.room.vertices:
            if vertex.position == snapped_position:
                return vertex

        return Vertex2D(
            position=snapped_position
        )

    def _create_demo_room(self) -> Room:
        v1 = Vertex2D(
            position=Point2D(0, 0)
        )

        v2 = Vertex2D(
            position=Point2D(4000, 0)
        )

        v3 = Vertex2D(
            position=Point2D(4000, 3000)
        )

        v4 = Vertex2D(
            position=Point2D(0, 3000)
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
        self.graphics_scene.clear()

        wall_pen = QPen()
        wall_pen.setWidthF(
            25
        )

        vertex_pen = QPen()
        vertex_pen.setWidthF(
            20
        )

        for wall in room.walls:
            self.graphics_scene.addLine(
                wall.start.x,
                wall.start.y,
                wall.end.x,
                wall.end.y,
                wall_pen,
            )

        for vertex in room.vertices:
            radius = 35

            self.graphics_scene.addEllipse(
                vertex.position.x - radius,
                vertex.position.y - radius,
                radius * 2,
                radius * 2,
                vertex_pen,
            )

    def undo(self) -> None:
        if self.command_history.undo():
            self.render_room(
                self.room
            )

    def redo(self) -> None:
        if self.command_history.redo():
            self.render_room(
                self.room
            )

    def drawBackground(
        self,
        painter,
        rect,
    ) -> None:
        minor_grid = 100
        major_grid = 1000

        minor_pen = QPen()
        minor_pen.setWidthF(
            0
        )

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
        major_pen.setWidthF(
            0
        )

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
            current_scale * factor
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

        if (
            event.button()
            == Qt.MouseButton.LeftButton
        ):
            position = self.mapToScene(
                event.position().toPoint()
            )

            self.active_tool.mouse_press(
                position
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

        self.active_tool.mouse_move(
            position
        )

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

    def keyPressEvent(
        self,
        event: QKeyEvent,
    ) -> None:
        if event.key() == Qt.Key.Key_Escape:
            self.active_tool.cancel()

            event.accept()
            return

        super().keyPressEvent(
            event
        )
"""Visual board cut-layout panel for OpenInteriorCAD.

Cut Layout 0.1
"""

from __future__ import annotations

import html
from pathlib import Path

import FreeCADGui as Gui
from PySide import QtCore, QtGui, QtWidgets

from OICBoardParts import build_board_parts
from OICCutLayout import (
    calculate_layout,
    expand_board_parts,
)
from OICCutListPanel import get_cut_list_source


class CutLayoutView(
    QtWidgets.QGraphicsView
):
    """Zoomable graphics view."""

    def __init__(
        self,
        parent=None,
    ):
        super().__init__(
            parent
        )

        self.setRenderHint(
            QtGui.QPainter.Antialiasing,
            True,
        )

        self.setDragMode(
            QtWidgets.QGraphicsView.ScrollHandDrag
        )

        self.setTransformationAnchor(
            QtWidgets.QGraphicsView.AnchorUnderMouse
        )

    def wheelEvent(
        self,
        event,
    ):
        factor = (
            1.15
            if event.delta() > 0
            else 1.0 / 1.15
        )

        self.scale(
            factor,
            factor,
        )


class CutLayoutPanel:
    """Visualize Board Parts arranged on full sheets."""

    def __init__(
        self,
        furniture_objects=None,
    ):
        if furniture_objects is None:
            furniture_objects = get_cut_list_source()

        self.furniture_objects = list(
            furniture_objects
        )

        self.layouts = []
        self.unplaced = []
        self.current_layout = None

        self.form = QtWidgets.QWidget()
        self.form.setWindowTitle(
            "Board Cut Layout"
        )

        root = QtWidgets.QVBoxLayout(
            self.form
        )

        self.source_label = QtWidgets.QLabel()
        self.source_label.setWordWrap(
            True
        )
        root.addWidget(
            self.source_label
        )

        # --------------------------------------------------
        # Sheet settings
        # --------------------------------------------------

        settings = QtWidgets.QGroupBox(
            "Sheet Settings"
        )
        grid = QtWidgets.QGridLayout(
            settings
        )

        grid.addWidget(
            QtWidgets.QLabel(
                "Sheet width:"
            ),
            0,
            0,
        )

        self.sheet_width = QtWidgets.QDoubleSpinBox()
        self.sheet_width.setRange(
            100.0,
            10000.0,
        )
        self.sheet_width.setDecimals(
            1
        )
        self.sheet_width.setValue(
            2800.0
        )
        self.sheet_width.setSuffix(
            " mm"
        )
        grid.addWidget(
            self.sheet_width,
            0,
            1,
        )

        grid.addWidget(
            QtWidgets.QLabel(
                "Sheet height:"
            ),
            0,
            2,
        )

        self.sheet_height = QtWidgets.QDoubleSpinBox()
        self.sheet_height.setRange(
            100.0,
            10000.0,
        )
        self.sheet_height.setDecimals(
            1
        )
        self.sheet_height.setValue(
            2070.0
        )
        self.sheet_height.setSuffix(
            " mm"
        )
        grid.addWidget(
            self.sheet_height,
            0,
            3,
        )

        grid.addWidget(
            QtWidgets.QLabel(
                "Saw kerf:"
            ),
            1,
            0,
        )

        self.kerf = QtWidgets.QDoubleSpinBox()
        self.kerf.setRange(
            0.0,
            50.0,
        )
        self.kerf.setDecimals(
            1
        )
        self.kerf.setValue(
            4.0
        )
        self.kerf.setSuffix(
            " mm"
        )
        grid.addWidget(
            self.kerf,
            1,
            1,
        )

        grid.addWidget(
            QtWidgets.QLabel(
                "Outer margin:"
            ),
            1,
            2,
        )

        self.margin = QtWidgets.QDoubleSpinBox()
        self.margin.setRange(
            0.0,
            100.0,
        )
        self.margin.setDecimals(
            1
        )
        self.margin.setValue(
            10.0
        )
        self.margin.setSuffix(
            " mm"
        )
        grid.addWidget(
            self.margin,
            1,
            3,
        )

        self.rotation_checkbox = QtWidgets.QCheckBox(
            "Allow 90° rotation"
        )
        self.rotation_checkbox.setChecked(
            True
        )
        grid.addWidget(
            self.rotation_checkbox,
            2,
            0,
            1,
            1,
        )

        self.edge_marks_checkbox = QtWidgets.QCheckBox(
            "Show edge banding"
        )
        self.edge_marks_checkbox.setChecked(
            True
        )
        self.edge_marks_checkbox.toggled.connect(
            self._refresh_current_layout
        )
        grid.addWidget(
            self.edge_marks_checkbox,
            2,
            1,
            1,
            1,
        )

        note = QtWidgets.QLabel(
            "L-shaped corner parts are shown correctly, but in version 0.1 "
            "their full bounding rectangle is reserved during optimization."
        )
        note.setWordWrap(
            True
        )
        grid.addWidget(
            note,
            2,
            2,
            1,
            2,
        )

        root.addWidget(
            settings
        )

        # --------------------------------------------------
        # Actions / sheet selector
        # --------------------------------------------------

        actions = QtWidgets.QHBoxLayout()

        self.calculate_button = QtWidgets.QPushButton(
            "Calculate Layout"
        )
        self.calculate_button.clicked.connect(
            self.calculate
        )
        actions.addWidget(
            self.calculate_button
        )

        actions.addWidget(
            QtWidgets.QLabel(
                "Sheet:"
            )
        )

        self.sheet_combo = QtWidgets.QComboBox()
        self.sheet_combo.currentIndexChanged.connect(
            self._sheet_changed
        )
        actions.addWidget(
            self.sheet_combo,
            1,
        )

        self.fit_button = QtWidgets.QPushButton(
            "Fit"
        )
        self.fit_button.clicked.connect(
            self.fit_view
        )
        actions.addWidget(
            self.fit_button
        )

        self.export_button = QtWidgets.QPushButton(
            "Export SVG"
        )
        self.export_button.clicked.connect(
            self.export_svg
        )
        actions.addWidget(
            self.export_button
        )

        self.export_pdf_button = QtWidgets.QPushButton(
            "Export PDF"
        )
        self.export_pdf_button.setToolTip(
            "Export all calculated sheets to one multi-page PDF."
        )
        self.export_pdf_button.clicked.connect(
            self.export_pdf
        )
        actions.addWidget(
            self.export_pdf_button
        )

        root.addLayout(
            actions
        )

        # --------------------------------------------------
        # Graphics
        # --------------------------------------------------

        self.scene = QtWidgets.QGraphicsScene()
        self.view = CutLayoutView()
        self.view.setScene(
            self.scene
        )
        self.view.setMinimumHeight(
            430
        )

        root.addWidget(
            self.view,
            1,
        )

        legend_row = QtWidgets.QHBoxLayout()

        self.edge_legend_sample = QtWidgets.QLabel(
            "━━"
        )
        self.edge_legend_sample.setStyleSheet(
            "color: rgb(230, 120, 20); font-weight: bold; font-size: 18px;"
        )
        legend_row.addWidget(
            self.edge_legend_sample
        )

        self.edge_legend_label = QtWidgets.QLabel(
            "Short inner line = edge banding / ABS edge"
        )
        legend_row.addWidget(
            self.edge_legend_label
        )

        legend_row.addStretch(
            1
        )

        root.addLayout(
            legend_row
        )

        self.summary_label = QtWidgets.QLabel()
        self.summary_label.setWordWrap(
            True
        )
        root.addWidget(
            self.summary_label
        )

        self.calculate()

    # ======================================================
    # DATA
    # ======================================================

    def calculate(
        self,
    ):
        pieces = expand_board_parts(
            self.furniture_objects,
            build_board_parts,
        )

        self.layouts, self.unplaced = calculate_layout(
            pieces=pieces,
            sheet_width=self.sheet_width.value(),
            sheet_height=self.sheet_height.value(),
            kerf=self.kerf.value(),
            margin=self.margin.value(),
            allow_rotation=self.rotation_checkbox.isChecked(),
        )

        self.sheet_combo.blockSignals(
            True
        )
        self.sheet_combo.clear()

        for index, layout in enumerate(
            self.layouts
        ):
            self.sheet_combo.addItem(
                (
                    f"{index + 1}: "
                    f"{layout.material} / "
                    f"{layout.thickness:.1f} mm / "
                    f"sheet {layout.number}"
                ),
                index,
            )

        self.sheet_combo.blockSignals(
            False
        )

        cabinet_count = len(
            self.furniture_objects
        )

        self.source_label.setText(
            (
                f"Source: {cabinet_count} cabinet(s), "
                f"{len(pieces)} physical part(s). "
                "Selected cabinets are used when a selection exists; "
                "otherwise all cabinets in the document are used."
            )
        )

        if self.layouts:
            self.sheet_combo.setCurrentIndex(
                0
            )
            self._show_layout(
                self.layouts[0]
            )
        else:
            self.scene.clear()
            self.current_layout = None

        self._update_summary(
            pieces
        )

    def _update_summary(
        self,
        pieces,
    ):
        used_sheet_area = sum(
            layout.sheet_area
            for layout in self.layouts
        )

        reserved_piece_area = sum(
            layout.used_area
            for layout in self.layouts
        )

        utilization = (
            reserved_piece_area
            / used_sheet_area
            * 100.0
            if used_sheet_area > 0.0
            else 0.0
        )

        text = (
            f"Sheets: {len(self.layouts)}   |   "
            f"Parts: {len(pieces)}   |   "
            f"Average reserved-area utilization: {utilization:.1f}%"
        )

        if self.unplaced:
            text += (
                f"   |   NOT PLACED: {len(self.unplaced)}"
            )

        self.summary_label.setText(
            text
        )

    def _refresh_current_layout(
        self,
        *_args,
    ):
        if self.current_layout is not None:
            self._show_layout(
                self.current_layout
            )

    def _edge_segments(
        self,
        placed,
    ):
        """
        Return short edge-band indicator segments INSIDE the board outline.

        The mark is:
        - parallel to the physical edge to be banded,
        - offset slightly into the part,
        - centered on that edge,
        - intentionally shorter than the full edge.

        This matches common furniture-production drawing conventions better
        than drawing directly over the board outline.

        Board Parts convention:
        - Front / Back run along part Length
        - Left / Right run along part Width

        A 90-degree packed rotation rotates those assignments with the part.
        """

        piece = placed.piece

        x = placed.x
        y = placed.y
        w = placed.width
        h = placed.height

        # Keep the mark visually inside the board and readable at many scales.
        inset = max(
            8.0,
            min(
                22.0,
                min(
                    w,
                    h,
                ) * 0.06,
            ),
        )

        # Use a short centred dash: 30% of the edge length,
        # constrained to a practical visual range.
        horizontal_mark = max(
            35.0,
            min(
                w * 0.30,
                180.0,
            ),
        )

        vertical_mark = max(
            35.0,
            min(
                h * 0.30,
                180.0,
            ),
        )

        hx1 = (
            x
            + (w - horizontal_mark) / 2.0
        )
        hx2 = (
            hx1
            + horizontal_mark
        )

        vy1 = (
            y
            + (h - vertical_mark) / 2.0
        )
        vy2 = (
            vy1
            + vertical_mark
        )

        segments = []

        def add(
            enabled,
            name,
            x1,
            y1,
            x2,
            y2,
        ):
            if enabled:
                segments.append(
                    (
                        name,
                        x1,
                        y1,
                        x2,
                        y2,
                    )
                )

        if not placed.rotated:
            add(
                piece.edge_front,
                "Front",
                hx1,
                y + inset,
                hx2,
                y + inset,
            )
            add(
                piece.edge_back,
                "Back",
                hx1,
                y + h - inset,
                hx2,
                y + h - inset,
            )
            add(
                piece.edge_left,
                "Left",
                x + inset,
                vy1,
                x + inset,
                vy2,
            )
            add(
                piece.edge_right,
                "Right",
                x + w - inset,
                vy1,
                x + w - inset,
                vy2,
            )

        else:
            # 90° clockwise rotation:
            # Front -> Right
            # Back  -> Left
            # Left  -> Top
            # Right -> Bottom
            add(
                piece.edge_front,
                "Front",
                x + w - inset,
                vy1,
                x + w - inset,
                vy2,
            )
            add(
                piece.edge_back,
                "Back",
                x + inset,
                vy1,
                x + inset,
                vy2,
            )
            add(
                piece.edge_left,
                "Left",
                hx1,
                y + inset,
                hx2,
                y + inset,
            )
            add(
                piece.edge_right,
                "Right",
                hx1,
                y + h - inset,
                hx2,
                y + h - inset,
            )

        return segments



    def _edge_description(
        self,
        piece,
    ):
        names = []

        for enabled, label in (
            (
                piece.edge_front,
                "Front",
            ),
            (
                piece.edge_back,
                "Back",
            ),
            (
                piece.edge_left,
                "Left",
            ),
            (
                piece.edge_right,
                "Right",
            ),
        ):
            if enabled:
                names.append(
                    label
                )

        if names:
            material = (
                piece.edge_material
                or "Edge"
            )

            thickness = (
                f" {piece.edge_thickness:.1f} mm"
                if piece.edge_thickness > 0.0
                else ""
            )

            return (
                f"Edge banding: {material}{thickness} "
                f"({', '.join(names)})"
            )

        if piece.edge_pattern:
            return (
                f"Edge banding: {piece.edge_pattern}"
            )

        return "Edge banding: none"

    def _draw_edge_marks(
        self,
        placed,
    ):
        if not self.edge_marks_checkbox.isChecked():
            return

        piece = placed.piece

        edge_pen = QtGui.QPen(
            QtGui.QColor(
                230,
                120,
                20,
            )
        )
        edge_pen.setWidthF(
            max(
                3.0,
                min(
                    7.0,
                    min(
                        placed.width,
                        placed.height,
                    )
                    * 0.020,
                ),
            )
        )
        edge_pen.setCapStyle(
            QtCore.Qt.SquareCap
        )

        for (
            _name,
            x1,
            y1,
            x2,
            y2,
        ) in self._edge_segments(
            placed
        ):
            line = self.scene.addLine(
                x1,
                y1,
                x2,
                y2,
                edge_pen,
            )
            line.setZValue(
                5
            )
            line.setToolTip(
                self._edge_description(
                    piece
                )
            )

        # L-shaped parts currently carry "Custom (L)" reporting metadata
        # rather than exact per-segment flags. Do not invent segment
        # assignments: show an explicit marker instead.
        if (
            piece.shape == "L"
            and piece.edge_pattern
            and not self._edge_segments(
                placed
            )
        ):
            text_item = self.scene.addText(
                "EDGE: "
                + piece.edge_pattern
            )
            text_item.setDefaultTextColor(
                QtGui.QColor(
                    230,
                    120,
                    20,
                )
            )
            text_item.setPos(
                placed.x + 8.0,
                placed.y + max(
                    28.0,
                    min(
                        placed.height * 0.25,
                        55.0,
                    ),
                ),
            )
            text_item.setScale(
                max(
                    0.7,
                    min(
                        1.7,
                        min(
                            placed.width / 500.0,
                            placed.height / 180.0,
                        ),
                    ),
                )
            )
            text_item.setZValue(
                6
            )
            text_item.setToolTip(
                self._edge_description(
                    piece
                )
            )


    # ======================================================
    # DRAWING
    # ======================================================

    def _sheet_changed(
        self,
        index,
    ):
        if (
            index < 0
            or index >= len(
                self.layouts
            )
        ):
            return

        self._show_layout(
            self.layouts[
                index
            ]
        )

    def _show_layout(
        self,
        layout,
    ):
        self.current_layout = layout
        self.scene.clear()

        sw = layout.sheet_width
        sh = layout.sheet_height

        sheet_pen = QtGui.QPen()
        sheet_pen.setWidthF(
            2.0
        )

        sheet_brush = QtGui.QBrush(
            QtGui.QColor(
                245,
                245,
                245,
            )
        )

        sheet_item = self.scene.addRect(
            0.0,
            0.0,
            sw,
            sh,
            sheet_pen,
            sheet_brush,
        )
        sheet_item.setZValue(
            0
        )

        # Usable boundary.
        usable_pen = QtGui.QPen(
            QtGui.QColor(
                130,
                130,
                130,
            )
        )
        usable_pen.setStyle(
            QtCore.Qt.DashLine
        )
        usable_pen.setWidthF(
            1.0
        )

        self.scene.addRect(
            layout.margin,
            layout.margin,
            max(
                0.0,
                sw - 2.0 * layout.margin,
            ),
            max(
                0.0,
                sh - 2.0 * layout.margin,
            ),
            usable_pen,
        )

        palette = [
            QtGui.QColor(221, 235, 247),
            QtGui.QColor(226, 239, 218),
            QtGui.QColor(255, 242, 204),
            QtGui.QColor(242, 220, 219),
            QtGui.QColor(228, 223, 236),
            QtGui.QColor(218, 238, 243),
        ]

        for index, placed in enumerate(
            layout.pieces
        ):
            color = palette[
                index % len(
                    palette
                )
            ]

            brush = QtGui.QBrush(
                color
            )

            pen = QtGui.QPen(
                QtGui.QColor(
                    60,
                    60,
                    60,
                )
            )
            pen.setWidthF(
                1.2
            )

            piece = placed.piece

            if (
                piece.shape == "L"
                and not placed.rotated
            ):
                polygon = self._l_polygon(
                    placed,
                    piece,
                )

                item = self.scene.addPolygon(
                    polygon,
                    pen,
                    brush,
                )

            elif (
                piece.shape == "L"
                and placed.rotated
            ):
                polygon = self._rotated_l_polygon(
                    placed,
                    piece,
                )

                item = self.scene.addPolygon(
                    polygon,
                    pen,
                    brush,
                )

            else:
                item = self.scene.addRect(
                    placed.x,
                    placed.y,
                    placed.width,
                    placed.height,
                    pen,
                    brush,
                )

            item.setZValue(
                2
            )

            label = (
                f"{piece.name}"
                f"  {piece.length:.0f}×{piece.width:.0f}"
            )

            if placed.rotated:
                label += "  R"

            if any(
                (
                    piece.edge_front,
                    piece.edge_back,
                    piece.edge_left,
                    piece.edge_right,
                )
            ):
                label += "  EDGE"

            tooltip = (
                f"{piece.cabinet}\n"
                f"{piece.name}\n"
                f"{piece.length:.1f} × {piece.width:.1f} × "
                f"{piece.thickness:.1f} mm\n"
                f"{piece.material}\n"
                f"{self._edge_description(piece)}"
            )

            item.setToolTip(
                tooltip
            )

            self._draw_edge_marks(
                placed
            )

            # Label only if there is enough visual space.
            if (
                placed.width >= 100.0
                and placed.height >= 60.0
            ):
                text_item = self.scene.addText(
                    label
                )
                text_item.setDefaultTextColor(
                    QtGui.QColor(
                        25,
                        25,
                        25,
                    )
                )
                text_item.setPos(
                    placed.x + 8.0,
                    placed.y + 6.0,
                )
                text_item.setScale(
                    max(
                        0.8,
                        min(
                            2.3,
                            min(
                                placed.width / 450.0,
                                placed.height / 180.0,
                            ),
                        ),
                    )
                )
                text_item.setZValue(
                    3
                )
                text_item.setToolTip(
                    tooltip
                )

        title = self.scene.addText(
            (
                f"{layout.material} / {layout.thickness:.1f} mm"
                f"   |   sheet {layout.number}"
                f"   |   {len(layout.pieces)} part(s)"
                f"   |   reserved {layout.utilization * 100.0:.1f}%"
                + (
                    "   |   orange inner dash = edge banding"
                    if self.edge_marks_checkbox.isChecked()
                    else ""
                )
            )
        )

        title.setPos(
            0.0,
            -55.0,
        )
        title.setScale(
            1.6
        )

        self.scene.setSceneRect(
            -20.0,
            -70.0,
            sw + 40.0,
            sh + 90.0,
        )

        QtCore.QTimer.singleShot(
            0,
            self.fit_view,
        )

    def _l_polygon(
        self,
        placed,
        piece,
    ):
        x = placed.x
        y = placed.y
        w = placed.width
        h = placed.height

        cut_w = min(
            max(
                0.0,
                piece.cutout_width,
            ),
            w,
        )

        cut_h = min(
            max(
                0.0,
                piece.cutout_depth,
            ),
            h,
        )

        # Visual convention: cut-out at bottom-right of the bounding box.
        return QtGui.QPolygonF(
            [
                QtCore.QPointF(x, y),
                QtCore.QPointF(x + w, y),
                QtCore.QPointF(x + w, y + h - cut_h),
                QtCore.QPointF(x + w - cut_w, y + h - cut_h),
                QtCore.QPointF(x + w - cut_w, y + h),
                QtCore.QPointF(x, y + h),
            ]
        )

    def _rotated_l_polygon(
        self,
        placed,
        piece,
    ):
        x = placed.x
        y = placed.y
        w = placed.width
        h = placed.height

        cut_w = min(
            max(
                0.0,
                piece.cutout_depth,
            ),
            w,
        )

        cut_h = min(
            max(
                0.0,
                piece.cutout_width,
            ),
            h,
        )

        return QtGui.QPolygonF(
            [
                QtCore.QPointF(x, y),
                QtCore.QPointF(x + w, y),
                QtCore.QPointF(x + w, y + h),
                QtCore.QPointF(x + cut_w, y + h),
                QtCore.QPointF(x + cut_w, y + cut_h),
                QtCore.QPointF(x, y + cut_h),
            ]
        )

    def fit_view(
        self,
    ):
        if self.scene.items():
            self.view.fitInView(
                self.scene.sceneRect(),
                QtCore.Qt.KeepAspectRatio,
            )

    # ======================================================
    # SVG EXPORT
    # ======================================================

    def export_svg(
        self,
    ):
        layout = self.current_layout

        if layout is None:
            return

        filename, _selected_filter = QtWidgets.QFileDialog.getSaveFileName(
            self.form,
            "Export Cut Layout SVG",
            (
                f"cut_layout_{layout.material}_"
                f"{layout.thickness:.1f}mm_sheet_{layout.number}.svg"
            ),
            "SVG (*.svg)",
        )

        if not filename:
            return

        if not filename.lower().endswith(
            ".svg"
        ):
            filename += ".svg"

        try:
            self._write_svg(
                Path(
                    filename
                ),
                layout,
            )

            QtWidgets.QMessageBox.information(
                self.form,
                "Board Cut Layout",
                "SVG exported successfully.",
            )

        except Exception as error:
            QtWidgets.QMessageBox.critical(
                self.form,
                "Board Cut Layout",
                f"Could not export SVG:\n{error}",
            )

    def _write_svg(
        self,
        path,
        layout,
    ):
        sw = layout.sheet_width
        sh = layout.sheet_height

        lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            (
                f'<svg xmlns="http://www.w3.org/2000/svg" '
                f'width="{sw}mm" height="{sh}mm" '
                f'viewBox="0 0 {sw} {sh}">'
            ),
            '<rect x="0" y="0" width="100%" height="100%" '
            'fill="white" stroke="black" stroke-width="2"/>',
        ]

        for placed in layout.pieces:
            piece = placed.piece

            if piece.shape == "L":
                if placed.rotated:
                    points = self._svg_l_points_rotated(
                        placed,
                        piece,
                    )
                else:
                    points = self._svg_l_points(
                        placed,
                        piece,
                    )

                lines.append(
                    (
                        '<polygon points="'
                        + " ".join(
                            f"{x:.3f},{y:.3f}"
                            for x, y in points
                        )
                        + '" fill="#e9eef4" stroke="black" '
                        'stroke-width="1"/>'
                    )
                )
            else:
                lines.append(
                    (
                        f'<rect x="{placed.x:.3f}" y="{placed.y:.3f}" '
                        f'width="{placed.width:.3f}" '
                        f'height="{placed.height:.3f}" '
                        'fill="#e9eef4" stroke="black" stroke-width="1"/>'
                    )
                )

            label = html.escape(
                (
                    f"{piece.name} "
                    f"{piece.length:.0f}x{piece.width:.0f}"
                    + (
                        " R"
                        if placed.rotated
                        else ""
                    )
                )
            )

            lines.append(
                (
                    f'<text x="{placed.x + 8.0:.3f}" '
                    f'y="{placed.y + 20.0:.3f}" '
                    'font-family="Arial" font-size="16">'
                    f'{label}</text>'
                )
            )

            lines.extend(
                self._svg_edge_lines(
                    placed
                )
            )

        if self.edge_marks_checkbox.isChecked():
            lines.append(
                (
                    '<text x="20" y="40" font-family="Arial" '
                    'font-size="18" fill="#e67814">'
                    'Orange inner dashes = edge banding</text>'
                )
            )

        lines.append(
            "</svg>"
        )

        path.write_text(
            "\n".join(
                lines
            ),
            encoding="utf-8",
        )

    def _svg_l_points(
        self,
        placed,
        piece,
    ):
        x = placed.x
        y = placed.y
        w = placed.width
        h = placed.height
        cw = min(piece.cutout_width, w)
        ch = min(piece.cutout_depth, h)

        return [
            (x, y),
            (x + w, y),
            (x + w, y + h - ch),
            (x + w - cw, y + h - ch),
            (x + w - cw, y + h),
            (x, y + h),
        ]

    def _svg_l_points_rotated(
        self,
        placed,
        piece,
    ):
        x = placed.x
        y = placed.y
        w = placed.width
        h = placed.height
        cw = min(piece.cutout_depth, w)
        ch = min(piece.cutout_width, h)

        return [
            (x, y),
            (x + w, y),
            (x + w, y + h),
            (x + cw, y + h),
            (x + cw, y + ch),
            (x, y + ch),
        ]

    def _svg_edge_lines(
        self,
        placed,
    ):
        """Return SVG line elements for edge-band markings."""

        if not self.edge_marks_checkbox.isChecked():
            return []

        lines = []

        for (
            _name,
            x1,
            y1,
            x2,
            y2,
        ) in self._edge_segments(
            placed
        ):
            lines.append(
                (
                    f'<line x1="{x1:.3f}" y1="{y1:.3f}" '
                    f'x2="{x2:.3f}" y2="{y2:.3f}" '
                    'stroke="#e67814" stroke-width="5" '
                    'stroke-linecap="square"/>'
                )
            )

        piece = placed.piece

        if (
            piece.shape == "L"
            and piece.edge_pattern
            and not self._edge_segments(
                placed
            )
        ):
            marker = html.escape(
                "EDGE: "
                + piece.edge_pattern
            )

            lines.append(
                (
                    f'<text x="{placed.x + 8.0:.3f}" '
                    f'y="{placed.y + 42.0:.3f}" '
                    'font-family="Arial" font-size="16" '
                    'fill="#e67814">'
                    f'{marker}</text>'
                )
            )

        return lines


    # ======================================================
    # PDF EXPORT
    # ======================================================

    def export_pdf(
        self,
    ):
        """Export all calculated stock sheets to one multi-page PDF."""

        if not self.layouts:
            QtWidgets.QMessageBox.warning(
                self.form,
                "Board Cut Layout",
                "There are no calculated sheets to export.",
            )
            return

        filename, _selected_filter = QtWidgets.QFileDialog.getSaveFileName(
            self.form,
            "Export Cut Layout PDF",
            "cut_layout_all_sheets.pdf",
            "PDF (*.pdf)",
        )

        if not filename:
            return

        if not filename.lower().endswith(
            ".pdf"
        ):
            filename += ".pdf"

        try:
            self._write_pdf(
                Path(
                    filename
                )
            )

            QtWidgets.QMessageBox.information(
                self.form,
                "Board Cut Layout",
                (
                    f"PDF exported successfully.\n"
                    f"Sheets: {len(self.layouts)}"
                ),
            )

        except Exception as error:
            QtWidgets.QMessageBox.critical(
                self.form,
                "Board Cut Layout",
                f"Could not export PDF:\n{error}",
            )

    def _configure_pdf_writer(
        self,
        filename,
    ):
        """Create a vector PDF writer compatible with FreeCAD PySide."""

        if not hasattr(
            QtGui,
            "QPdfWriter",
        ):
            raise RuntimeError(
                "QtGui.QPdfWriter is not available in this FreeCAD build."
            )

        writer = QtGui.QPdfWriter(
            str(
                filename
            )
        )

        try:
            writer.setTitle(
                "OpenInteriorCAD Board Cut Layout"
            )
        except Exception:
            pass

        try:
            writer.setCreator(
                "OpenInteriorCAD"
            )
        except Exception:
            pass

        try:
            writer.setResolution(
                300
            )
        except Exception:
            pass

        # A3 landscape.
        try:
            page_size = QtGui.QPageSize(
                QtGui.QPageSize.A3
            )

            writer.setPageSize(
                page_size
            )
        except Exception:
            pass

        try:
            writer.setPageOrientation(
                QtGui.QPageLayout.Landscape
            )
        except Exception:
            pass

        # Small physical margins. The layout itself is still scaled to fit.
        try:
            writer.setPageMargins(
                QtCore.QMarginsF(
                    8.0,
                    8.0,
                    8.0,
                    8.0,
                ),
                QtGui.QPageLayout.Millimeter,
            )
        except Exception:
            pass

        return writer



    def _write_pdf(
        self,
        path,
    ):
        """
        Write every calculated stock sheet as a separate vector PDF page.

        Uses QtGui.QPdfWriter because FreeCAD 1.1 does not expose
        QtPrintSupport through its PySide compatibility module.
        """

        writer = self._configure_pdf_writer(
            path
        )

        painter = QtGui.QPainter()

        if not painter.begin(
            writer
        ):
            raise RuntimeError(
                "Could not start the PDF painter."
            )

        original_index = self.sheet_combo.currentIndex()

        try:
            for index, layout in enumerate(
                self.layouts
            ):
                if index > 0:
                    if not writer.newPage():
                        raise RuntimeError(
                            "Could not create the next PDF page."
                        )

                self._show_layout(
                    layout
                )

                source_rect = self.scene.sceneRect()

                # QPdfWriter exposes the current page layout in Qt6.
                # Use its paint rectangle in device pixels when available.
                target_rect = None

                try:
                    page_layout = writer.pageLayout()

                    target_rect = QtCore.QRectF(
                        page_layout.paintRectPixels(
                            writer.resolution()
                        )
                    )

                except Exception:
                    pass

                # Fallback: derive target rect from the writer dimensions.
                if (
                    target_rect is None
                    or target_rect.width() <= 0.0
                    or target_rect.height() <= 0.0
                ):
                    target_rect = QtCore.QRectF(
                        0.0,
                        0.0,
                        float(
                            writer.width()
                        ),
                        float(
                            writer.height()
                        ),
                    )

                    fallback_margin = max(
                        20.0,
                        min(
                            target_rect.width(),
                            target_rect.height(),
                        )
                        * 0.025,
                    )

                    target_rect.adjust(
                        fallback_margin,
                        fallback_margin,
                        -fallback_margin,
                        -fallback_margin,
                    )

                self.scene.render(
                    painter,
                    target_rect,
                    source_rect,
                    QtCore.Qt.KeepAspectRatio,
                )

        finally:
            painter.end()

            # Restore previously visible sheet.
            if (
                original_index >= 0
                and original_index < len(
                    self.layouts
                )
            ):
                self.sheet_combo.blockSignals(
                    True
                )

                self.sheet_combo.setCurrentIndex(
                    original_index
                )

                self.sheet_combo.blockSignals(
                    False
                )

                self._show_layout(
                    self.layouts[
                        original_index
                    ]
                )



    # ======================================================
    # TASK PANEL
    # ======================================================

    def getStandardButtons(
        self,
    ):
        return int(
            QtWidgets.QDialogButtonBox.Close
        )

    def reject(
        self,
    ):
        Gui.Control.closeDialog()
        return True

    def accept(
        self,
    ):
        Gui.Control.closeDialog()
        return True

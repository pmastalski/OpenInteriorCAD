"""Universal parametric cabinet object for OpenInteriorCAD.

Cabinet Architecture 0.3:
- Base
- Wall
- Tall
- Corner Base
- Corner Wall
- Blind Corner Base

All variants remain OpenInteriorCAD::Furniture and preserve the common
Width / Depth / Height / Position / RotationAngle interface used by
Move, Snap, Duplicate and Cabinet Run tools.
"""

import FreeCAD as App
import Part

from OICBoardParts import build_board_parts, board_parts_json


FURNITURE_TYPE = "OpenInteriorCAD::Furniture"

CABINET_BASE = "Base"
CABINET_WALL = "Wall"
CABINET_TALL = "Tall"
CABINET_CORNER_BASE = "Corner Base"
CABINET_CORNER_WALL = "Corner Wall"
CABINET_BLIND_CORNER_BASE = "Blind Corner Base"

GEOMETRY_BOX = "Box"
GEOMETRY_CARCASS = "Carcass"

FRONT_OPEN = "Open"
FRONT_SINGLE = "Single Door"
FRONT_DOUBLE = "Double Door"
FRONT_DRAWERS = "Drawers"
FRONT_DOOR_DRAWERS = "Door + Drawers"
FRONT_LIFT_UP = "Lift-up"
FRONT_CORNER_FOLDING = "Corner Folding Doors"


class FurnitureProxy:
    TYPE_ID = FURNITURE_TYPE

    def __init__(
        self,
        obj,
        width=600.0,
        depth=560.0,
        height=720.0,
        rotation=0.0,
        position=None,
        cabinet_type=CABINET_BASE,
        geometry_mode=GEOMETRY_CARCASS,
        panel_thickness=18.0,
        back_thickness=3.0,
        shelf_count=1,
        plinth_height=100.0,
        plinth_setback=50.0,
        mount_height=1400.0,
        width_b=900.0,
        depth_b=560.0,
        front_type=FRONT_OPEN,
        front_thickness=18.0,
        front_gap=2.0,
        drawer_count=3,
        drawer_zone_height=180.0,
        corner_opening_width=450.0,
        blind_box_width=600.0,
        blind_filler_width=100.0,
        blind_door_filler_width=50.0,
        blind_mate_width=600.0,
        blind_mate_depth=600.0,
        blind_side="Left",
    ):
        self._add_properties(obj)
        obj.Proxy = self

        if position is None:
            position = App.Vector(0.0, 0.0, 0.0)

        obj.Width = width
        obj.Depth = depth
        obj.Height = height
        obj.RotationAngle = rotation
        obj.Position = position

        obj.CabinetType = cabinet_type
        obj.GeometryMode = geometry_mode
        obj.PanelThickness = panel_thickness
        obj.BackThickness = back_thickness
        obj.ShelfCount = int(shelf_count)
        obj.PlinthHeight = plinth_height
        obj.PlinthSetback = plinth_setback
        obj.MountHeight = mount_height
        obj.WidthB = width_b
        obj.DepthB = depth_b
        obj.FrontType = front_type
        obj.FrontThickness = front_thickness
        obj.FrontGap = front_gap
        obj.DrawerCount = int(drawer_count)
        obj.DrawerZoneHeight = drawer_zone_height
        obj.CornerOpeningWidth = corner_opening_width
        obj.BlindBoxWidth = blind_box_width
        obj.BlindFillerWidth = blind_filler_width
        obj.BlindDoorFillerWidth = blind_door_filler_width
        obj.BlindMateWidth = blind_mate_width
        obj.BlindMateDepth = blind_mate_depth
        obj.BlindSide = blind_side

        self.rebuild_geometry(obj)

    def _add_properties(self, obj):
        def add(kind, name, group, help_text):
            if name not in obj.PropertiesList:
                obj.addProperty(kind, name, group, help_text)

        add(
            "App::PropertyString",
            "OICType",
            "OpenInteriorCAD",
            "Semantic object type.",
        )

        add(
            "App::PropertyEnumeration",
            "CabinetType",
            "Cabinet",
            "Cabinet construction type.",
        )

        if "CabinetType" in obj.PropertiesList:
            try:
                current_type = str(obj.CabinetType)
            except Exception:
                current_type = CABINET_BASE

            allowed = [
                CABINET_BASE,
                CABINET_WALL,
                CABINET_TALL,
                CABINET_CORNER_BASE,
                CABINET_CORNER_WALL,
                CABINET_BLIND_CORNER_BASE,
            ]

            obj.CabinetType = allowed

            if current_type in allowed:
                obj.CabinetType = current_type
            else:
                obj.CabinetType = CABINET_BASE

        add(
            "App::PropertyLength",
            "Width",
            "Dimensions",
            "Width A for corner cabinets; overall width for standard cabinets.",
        )

        add(
            "App::PropertyLength",
            "Depth",
            "Dimensions",
            "Depth A for corner cabinets; overall depth for standard cabinets.",
        )

        add(
            "App::PropertyLength",
            "WidthB",
            "Corner",
            "Width B of the perpendicular corner cabinet leg.",
        )

        add(
            "App::PropertyLength",
            "DepthB",
            "Corner",
            "Depth B of the perpendicular corner cabinet leg.",
        )

        add(
            "App::PropertyLength",
            "Height",
            "Dimensions",
            "Overall cabinet height.",
        )

        add(
            "App::PropertyVector",
            "Position",
            "Position",
            "Cabinet back-left reference point.",
        )

        add(
            "App::PropertyAngle",
            "RotationAngle",
            "Position",
            "Cabinet rotation around Z.",
        )

        add(
            "App::PropertyEnumeration",
            "GeometryMode",
            "Cabinet",
            "Simple box or generated carcass.",
        )

        if "GeometryMode" in obj.PropertiesList:
            try:
                current_geometry = str(obj.GeometryMode)
            except Exception:
                current_geometry = GEOMETRY_BOX

            obj.GeometryMode = [
                GEOMETRY_BOX,
                GEOMETRY_CARCASS,
            ]

            if current_geometry in (
                GEOMETRY_BOX,
                GEOMETRY_CARCASS,
            ):
                obj.GeometryMode = current_geometry
            else:
                obj.GeometryMode = GEOMETRY_BOX

        add(
            "App::PropertyLength",
            "PanelThickness",
            "Carcass",
            "Carcass panel thickness.",
        )

        add(
            "App::PropertyLength",
            "BackThickness",
            "Carcass",
            "Back panel thickness.",
        )

        add(
            "App::PropertyInteger",
            "ShelfCount",
            "Interior",
            "Number of internal shelves.",
        )

        add(
            "App::PropertyLength",
            "PlinthHeight",
            "Carcass",
            "Plinth height for floor-standing cabinets.",
        )

        add(
            "App::PropertyLength",
            "PlinthSetback",
            "Carcass",
            "Front setback of the plinth.",
        )

        add(
            "App::PropertyLength",
            "MountHeight",
            "Cabinet",
            "Suggested Z position for wall cabinets.",
        )

        if obj.PanelThickness.Value <= 0.0:
            obj.PanelThickness = 18.0

        if obj.BackThickness.Value <= 0.0:
            obj.BackThickness = 3.0

        if obj.PlinthHeight.Value < 0.0:
            obj.PlinthHeight = 100.0

        if obj.PlinthSetback.Value < 0.0:
            obj.PlinthSetback = 50.0

        if obj.MountHeight.Value <= 0.0:
            obj.MountHeight = 1400.0

        if obj.WidthB.Value <= 0.0:
            obj.WidthB = 900.0

        if obj.DepthB.Value <= 0.0:
            obj.DepthB = 560.0

        add(
            "App::PropertyLength",
            "CornerOpeningWidth",
            "Corner",
            "Clear width of each leaf/opening at the inside corner.",
        )

        if obj.CornerOpeningWidth.Value <= 0.0:
            obj.CornerOpeningWidth = 450.0

        add(
            "App::PropertyEnumeration",
            "BlindSide",
            "Blind Corner",
            "Side occupied by the hidden closed box.",
        )

        if "BlindSide" in obj.PropertiesList:
            try:
                current_blind_side = str(
                    obj.BlindSide
                )
            except Exception:
                current_blind_side = "Left"

            obj.BlindSide = [
                "Left",
                "Right",
            ]

            if current_blind_side in {
                "Left",
                "Right",
            }:
                obj.BlindSide = current_blind_side
            else:
                obj.BlindSide = "Left"

        add(
            "App::PropertyLength",
            "BlindBoxWidth",
            "Blind Corner",
            "Width of the hidden closed box section.",
        )

        add(
            "App::PropertyLength",
            "BlindFillerWidth",
            "Blind Corner",
            "Perpendicular spacer filler length toward the neighbouring cabinet.",
        )

        add(
            "App::PropertyLength",
            "BlindDoorFillerWidth",
            "Blind Corner",
            "Front clearance filler that shortens the usable door/front.",
        )

        add(
            "App::PropertyLength",
            "BlindMateWidth",
            "Blind Corner",
            "Width of the automatically inserted perpendicular cabinet.",
        )

        add(
            "App::PropertyLength",
            "BlindMateDepth",
            "Blind Corner",
            "Depth of the automatically inserted perpendicular cabinet.",
        )

        add(
            "App::PropertyLink",
            "BlindMate",
            "Blind Corner",
            "Automatically linked perpendicular corner cabinet.",
        )

        if obj.BlindBoxWidth.Value <= 0.0:
            obj.BlindBoxWidth = 600.0

        if obj.BlindFillerWidth.Value <= 0.0:
            obj.BlindFillerWidth = 100.0

        if obj.BlindDoorFillerWidth.Value < 0.0:
            obj.BlindDoorFillerWidth = 0.0

        if obj.BlindMateWidth.Value <= 0.0:
            obj.BlindMateWidth = 600.0

        if obj.BlindMateDepth.Value <= 0.0:
            obj.BlindMateDepth = 600.0

        add(
            "App::PropertyEnumeration",
            "FrontType",
            "Front Layout",
            "Front configuration for standard cabinets.",
        )

        if "FrontType" in obj.PropertiesList:
            try:
                current_front = str(obj.FrontType)
            except Exception:
                current_front = FRONT_OPEN

            front_options = [
                FRONT_OPEN,
                FRONT_SINGLE,
                FRONT_DOUBLE,
                FRONT_DRAWERS,
                FRONT_DOOR_DRAWERS,
                FRONT_LIFT_UP,
                FRONT_CORNER_FOLDING,
            ]

            obj.FrontType = front_options

            if current_front in front_options:
                obj.FrontType = current_front
            else:
                obj.FrontType = FRONT_OPEN

        add(
            "App::PropertyLength",
            "FrontThickness",
            "Front Layout",
            "Front panel thickness.",
        )

        add(
            "App::PropertyLength",
            "FrontGap",
            "Front Layout",
            "Reveal/gap around and between fronts.",
        )

        add(
            "App::PropertyAngle",
            "FrontOpenAngle",
            "Front Opening",
            "Visual opening angle for standard hinged fronts.",
        )

        add(
            "App::PropertyEnumeration",
            "SingleDoorHingeSide",
            "Front Opening",
            "Hinge side for a single hinged door.",
        )

        if "SingleDoorHingeSide" in obj.PropertiesList:
            try:
                current_hinge_side = str(
                    obj.SingleDoorHingeSide
                )
            except Exception:
                current_hinge_side = "Left"

            obj.SingleDoorHingeSide = [
                "Left",
                "Right",
            ]

            if current_hinge_side in {
                "Left",
                "Right",
            }:
                obj.SingleDoorHingeSide = current_hinge_side
            else:
                obj.SingleDoorHingeSide = "Left"

        if obj.FrontOpenAngle.Value < 0.0:
            obj.FrontOpenAngle = 0.0

        if obj.FrontOpenAngle.Value > 120.0:
            obj.FrontOpenAngle = 120.0

        add(
            "App::PropertyLength",
            "DrawerOpenDistance",
            "Front Opening",
            "Visual opening distance for drawer fronts.",
        )

        if obj.DrawerOpenDistance.Value < 0.0:
            obj.DrawerOpenDistance = 0.0

        add(
            "App::PropertyInteger",
            "DrawerCount",
            "Front Layout",
            "Number of drawer fronts.",
        )

        add(
            "App::PropertyLength",
            "DrawerZoneHeight",
            "Front Layout",
            "Height of the top drawer zone in Door + Drawers mode.",
        )

        if obj.FrontThickness.Value <= 0.0:
            obj.FrontThickness = 18.0

        if obj.FrontGap.Value < 0.0:
            obj.FrontGap = 2.0

        if int(obj.DrawerCount) <= 0:
            obj.DrawerCount = 3

        if obj.DrawerZoneHeight.Value <= 0.0:
            obj.DrawerZoneHeight = 180.0

        obj.OICType = self.TYPE_ID

    def _make_box_geometry(self, obj):
        """Create legacy box safely during FreeCAD property initialization."""

        width = obj.Width.Value
        depth = obj.Depth.Value
        height = obj.Height.Value

        if (
            width <= 0.001
            or depth <= 0.001
            or height <= 0.001
        ):
            return Part.Shape()

        return Part.makeBox(
            width,
            depth,
            height,
        )

    def _make_standard_carcass(
        self,
        obj,
        use_plinth,
    ):
        width = obj.Width.Value
        depth = obj.Depth.Value
        height = obj.Height.Value
        panel = obj.PanelThickness.Value
        back = obj.BackThickness.Value

        if min(
            width,
            depth,
            height,
            panel,
            back,
        ) <= 0.001:
            return Part.Shape()

        if (
            width <= 2.0 * panel
            or depth <= back
        ):
            return Part.Shape()

        plinth = (
            max(
                0.0,
                obj.PlinthHeight.Value,
            )
            if use_plinth
            else 0.0
        )

        if plinth >= height:
            return Part.Shape()

        body_height = (
            height
            - plinth
        )

        inner_width = (
            width
            - 2.0 * panel
        )

        inner_depth = (
            depth
            - back
        )

        inner_height = (
            body_height
            - 2.0 * panel
        )

        if min(
            inner_width,
            inner_depth,
            inner_height,
        ) <= 0.001:
            return Part.Shape()

        shapes = [
            # Left side.
            Part.makeBox(
                panel,
                depth,
                body_height,
                App.Vector(
                    0.0,
                    0.0,
                    plinth,
                ),
            ),

            # Right side.
            Part.makeBox(
                panel,
                depth,
                body_height,
                App.Vector(
                    width - panel,
                    0.0,
                    plinth,
                ),
            ),

            # Bottom.
            Part.makeBox(
                inner_width,
                inner_depth,
                panel,
                App.Vector(
                    panel,
                    back,
                    plinth,
                ),
            ),

            # Top.
            Part.makeBox(
                inner_width,
                inner_depth,
                panel,
                App.Vector(
                    panel,
                    back,
                    plinth
                    + body_height
                    - panel,
                ),
            ),

            # Back.
            Part.makeBox(
                inner_width,
                back,
                inner_height,
                App.Vector(
                    panel,
                    0.0,
                    plinth
                    + panel,
                ),
            ),
        ]

        shelf_count = max(
            0,
            int(
                obj.ShelfCount
            ),
        )

        if shelf_count > 0:
            available = (
                inner_height
                - shelf_count * panel
            )

            if available > 0.001:
                clear_gap = (
                    available
                    / (
                        shelf_count
                        + 1
                    )
                )

                z = (
                    plinth
                    + panel
                    + clear_gap
                )

                for _ in range(
                    shelf_count
                ):
                    shapes.append(
                        Part.makeBox(
                            inner_width,
                            inner_depth,
                            panel,
                            App.Vector(
                                panel,
                                back,
                                z,
                            ),
                        )
                    )

                    z += (
                        panel
                        + clear_gap
                    )

        if (
            use_plinth
            and plinth > 0.001
        ):
            setback = max(
                0.0,
                obj.PlinthSetback.Value,
            )

            plinth_y = max(
                0.0,
                min(
                    depth - panel,
                    depth
                    - setback
                    - panel,
                ),
            )

            shapes.append(
                Part.makeBox(
                    width,
                    panel,
                    plinth,
                    App.Vector(
                        0.0,
                        plinth_y,
                        0.0,
                    ),
                )
            )

        return Part.makeCompound(
            shapes
        )

    def _make_blind_corner_carcass(
        self,
        obj,
    ):
        """
        Straight blind-corner base cabinet.

        The footprint is a normal elongated rectangle, not an L.

        Construction:
        - continuous outer rectangular carcass,
        - one internal full-height partition,
        - hidden section closed at the front with a carcass panel,
        - usable shelves only in the accessible section,
        - continuous recessed plinth.

        BlindBoxWidth includes the partition thickness.
        """

        W = float(
            obj.Width.Value
        )
        D = float(
            obj.Depth.Value
        )
        H = float(
            obj.Height.Value
        )
        T = float(
            obj.PanelThickness.Value
        )
        BT = float(
            obj.BackThickness.Value
        )
        B = float(
            obj.BlindBoxWidth.Value
        )

        F = max(
            0.0,
            float(
                obj.BlindFillerWidth.Value
            ),
        )

        body_depth = (
            D
            - F
        )

        if min(
            W,
            body_depth,
            H,
            T,
            BT,
            B,
        ) <= 0.001:
            return Part.Shape()

        plinth = max(
            0.0,
            float(
                obj.PlinthHeight.Value
            ),
        )

        if plinth >= H:
            return Part.Shape()

        body_h = (
            H
            - plinth
        )

        clear_h = (
            body_h
            - 2.0 * T
        )

        inner_depth = (
            body_depth
            - BT
        )

        main_clear_w = (
            W
            - B
            - T
        )

        hidden_clear_w = (
            B
            - 2.0 * T
        )

        if min(
            clear_h,
            inner_depth,
            main_clear_w,
            hidden_clear_w,
        ) <= 0.001:
            return Part.Shape()

        blind_side = str(
            obj.BlindSide
        )

        shapes = [
            # Outer left side.
            Part.makeBox(
                T,
                body_depth,
                body_h,
                App.Vector(
                    0.0,
                    0.0,
                    plinth,
                ),
            ),

            # Outer right side.
            Part.makeBox(
                T,
                body_depth,
                body_h,
                App.Vector(
                    W - T,
                    0.0,
                    plinth,
                ),
            ),

            # Continuous bottom.
            Part.makeBox(
                W - 2.0 * T,
                inner_depth,
                T,
                App.Vector(
                    T,
                    BT,
                    plinth,
                ),
            ),

            # Continuous top.
            Part.makeBox(
                W - 2.0 * T,
                inner_depth,
                T,
                App.Vector(
                    T,
                    BT,
                    plinth
                    + body_h
                    - T,
                ),
            ),

            # Continuous back.
            Part.makeBox(
                W - 2.0 * T,
                BT,
                clear_h,
                App.Vector(
                    T,
                    0.0,
                    plinth + T,
                ),
            ),
        ]

        z_vertical = (
            plinth
            + T
        )

        if blind_side == "Right":
            partition_x = (
                W
                - B
            )

            main_x0 = T
            main_w = (
                partition_x
                - T
            )

            hidden_front_x = (
                partition_x
                + T
            )

        else:
            partition_x = (
                B
                - T
            )

            main_x0 = B
            main_w = (
                W
                - T
                - B
            )

            hidden_front_x = T

        # Partition separates the usable compartment from the hidden box.
        shapes.append(
            Part.makeBox(
                T,
                inner_depth,
                clear_h,
                App.Vector(
                    partition_x,
                    BT,
                    z_vertical,
                ),
            )
        )

        # Hidden section front closure.
        #
        # It sits inside the carcass front plane. The decorative spacer
        # filler is generated separately with the visible fronts.
        shapes.append(
            Part.makeBox(
                hidden_clear_w,
                T,
                clear_h,
                App.Vector(
                    hidden_front_x,
                    body_depth - T,
                    z_vertical,
                ),
            )
        )

        # Shelves exist only in the accessible compartment.
        shelf_count = max(
            0,
            int(
                obj.ShelfCount
            ),
        )

        if (
            shelf_count > 0
            and main_w > 0.001
        ):
            available = (
                clear_h
                - shelf_count * T
            )

            if available > 0.001:
                clear_gap = (
                    available
                    / float(
                        shelf_count + 1
                    )
                )

                z = (
                    z_vertical
                    + clear_gap
                )

                for _ in range(
                    shelf_count
                ):
                    shapes.append(
                        Part.makeBox(
                            main_w,
                            inner_depth,
                            T,
                            App.Vector(
                                main_x0,
                                BT,
                                z,
                            ),
                        )
                    )

                    z += (
                        T
                        + clear_gap
                    )

        # Recessed plinth system.
        #
        # The front plinth runs along the full new cabinet.
        # A perpendicular return closes the bottom at the corner and aligns
        # with the neighbouring cabinet's recessed plinth line.
        if plinth > 0.001:
            setback = max(
                0.0,
                float(
                    obj.PlinthSetback.Value
                ),
            )

            filler_run = max(
                0.0,
                float(
                    obj.BlindFillerWidth.Value
                ),
            )

            plinth_y = max(
                0.0,
                min(
                    body_depth - T,
                    body_depth
                    - setback
                    - T,
                ),
            )

            # Main straight toe-kick.
            shapes.append(
                Part.makeBox(
                    W,
                    T,
                    plinth,
                    App.Vector(
                        0.0,
                        plinth_y,
                        0.0,
                    ),
                )
            )

            # Perpendicular toe-kick return.
            #
            # It is calculated from the exact same corner/mate convention
            # as the linked 90-degree cabinet. This fixes the visibly
            # mismatched short plinth from 0.4 and makes Left / Right mirror.
            if filler_run > 0.001:
                # The perpendicular filler now defines the true gap.
                # The long cabinet body ends at D - filler_run and the
                # linked 90° cabinet remains referenced at the original D.
                corner_line_y = (
                    D
                    - filler_run
                )

                filler_end_y = (
                    corner_line_y
                    + filler_run
                )

                if blind_side == "Right":
                    boundary_x = (
                        W
                        - B
                    )

                    # +90° mate recessed plinth.
                    return_x = (
                        boundary_x
                        + setback
                    )

                else:
                    boundary_x = B

                    # Exact X mirror of the Right case.
                    return_x = (
                        boundary_x
                        - setback
                        - T
                    )

                # Parent front plinth starts here.
                parent_plinth_y = plinth_y

                return_y = min(
                    parent_plinth_y,
                    filler_end_y,
                )

                # Exact butt joint with the linked 90° cabinet plinth.
                #
                # STEP analysis showed that the previous "+ T" extension
                # made the short return enter the mate plinth by exactly
                # one panel thickness (18 x 18 x PlinthHeight at defaults).
                #
                # Stop at the mate-plinth face instead.
                return_len = abs(
                    filler_end_y
                    - parent_plinth_y
                )

                if return_len > 0.001:
                    shapes.append(
                        Part.makeBox(
                            T,
                            return_len,
                            plinth,
                            App.Vector(
                                return_x,
                                return_y,
                                0.0,
                            ),
                        )
                    )

        valid = [
            shape
            for shape in shapes
            if shape is not None
            and not shape.isNull()
        ]

        return Part.makeCompound(
            valid
        )


    def _make_l_plate(
        self,
        width_a,
        width_b,
        depth_a,
        depth_b,
        thickness,
        z,
    ):
        """
        Build one clean L-shaped horizontal board.

        Previous versions created the L from two overlapping boxes.  The
        overlap was visually harmless but unsuitable for production geometry,
        cut lists and later CNC export.

        This version creates the union and refines the result so the plate is
        a single solid without an internal coplanar/intersection seam.
        """

        if min(
            width_a,
            width_b,
            depth_a,
            depth_b,
            thickness,
        ) <= 0.001:
            return Part.Shape()

        leg_a = Part.makeBox(
            width_a,
            depth_a,
            thickness,
            App.Vector(
                0.0,
                0.0,
                z,
            ),
        )

        leg_b = Part.makeBox(
            depth_b,
            width_b,
            thickness,
            App.Vector(
                0.0,
                0.0,
                z,
            ),
        )

        result = leg_a.fuse(
            leg_b
        )

        try:
            result = result.removeSplitter()
        except Exception:
            pass

        return result


    def _inside_width(total_width, panel_thickness):
        """Clear width between two full-height side panels."""
        return max(
            0.001,
            total_width - 2.0 * panel_thickness,
        )


    def _make_corner_horizontal_board(
        self,
        width_a,
        width_b,
        depth_a,
        depth_b,
        panel,
        back,
        clear_opening,
        thickness,
        z,
    ):
        """
        Build one production-oriented L-shaped horizontal board.

        The raw L footprint is cut by every vertical carcass footprint:
        - both backs,
        - both outer end panels,
        - both opening boundary stiles.

        Therefore Bottom / Top / Shelves finish on the INNER faces of
        vertical boards instead of geometrically passing through them.
        """

        raw = self._make_l_plate(
            width_a,
            width_b,
            depth_a,
            depth_b,
            thickness,
            z,
        )

        if raw.isNull():
            return raw

        cutters = []

        # Back A: horizontal back strip.
        cutters.append(
            Part.makeBox(
                width_a,
                back,
                thickness,
                App.Vector(
                    0.0,
                    0.0,
                    z,
                ),
            )
        )

        # Back B: perpendicular back strip.
        cutters.append(
            Part.makeBox(
                back,
                width_b,
                thickness,
                App.Vector(
                    0.0,
                    0.0,
                    z,
                ),
            )
        )

        # Outer end panel A.
        cutters.append(
            Part.makeBox(
                panel,
                depth_a,
                thickness,
                App.Vector(
                    width_a - panel,
                    0.0,
                    z,
                ),
            )
        )

        # Outer end panel B.
        cutters.append(
            Part.makeBox(
                depth_b,
                panel,
                thickness,
                App.Vector(
                    0.0,
                    width_b - panel,
                    z,
                ),
            )
        )

        # Opening stile A — same position as in _make_corner_carcass().
        stile_a_x = min(
            depth_b + clear_opening,
            width_a - 2.0 * panel,
        )

        if stile_a_x > depth_b + 0.001:
            cutters.append(
                Part.makeBox(
                    panel,
                    panel,
                    thickness,
                    App.Vector(
                        stile_a_x,
                        max(
                            0.0,
                            depth_a - panel,
                        ),
                        z,
                    ),
                )
            )

        # Opening stile B.
        stile_b_y = min(
            depth_a + clear_opening,
            width_b - 2.0 * panel,
        )

        if stile_b_y > depth_a + 0.001:
            cutters.append(
                Part.makeBox(
                    panel,
                    panel,
                    thickness,
                    App.Vector(
                        max(
                            0.0,
                            depth_b - panel,
                        ),
                        stile_b_y,
                        z,
                    ),
                )
            )

        result = raw

        for cutter in cutters:
            try:
                result = result.cut(
                    cutter
                )
            except Exception:
                pass

        try:
            result = result.removeSplitter()
        except Exception:
            pass

        return result


    def _corner_layout(self, obj):
        """
        Shared plan-layout for Corner Base / Corner Wall.

        One source of truth for:
        - inner corner
        - equal filler widths
        - front extents
        - shelf front extents
        - plinth extents

        This prevents carcass/front/plinth geometry from drifting apart.
        """

        W = float(obj.Width.Value)
        DA = float(obj.Depth.Value)
        WB = float(obj.WidthB.Value)
        DB = float(obj.DepthB.Value)
        T = float(obj.PanelThickness.Value)

        requested = max(
            0.0,
            float(obj.CornerOpeningWidth.Value),
        )

        run_a = max(
            0.0,
            W - DB,
        )

        run_b = max(
            0.0,
            WB - DA,
        )

        min_run = min(
            run_a,
            run_b,
        )

        # Equal fillers on both sides.
        #
        # At minimum they are one panel thickness wide.
        # If CornerOpening is smaller than the shorter available run,
        # the remaining space becomes an equal filler width on both sides.
        filler = max(
            T,
            min_run - min(
                requested,
                min_run - T,
            ),
        )

        # Never let filler consume the complete front run.
        filler = min(
            filler,
            max(
                T,
                min_run - T,
            ),
        )

        # Filler A touches Side A exactly.
        filler_a_x0 = (
            W
            - T
            - filler
        )
        filler_a_x1 = (
            W
            - T
        )

        # Filler B touches Side B exactly.
        filler_b_y0 = (
            WB
            - T
            - filler
        )
        filler_b_y1 = (
            WB
            - T
        )

        # Clear front runs from the inside corner to inner filler faces.
        door_a_end = filler_a_x0
        door_b_end = filler_b_y0

        return {
            "W": W,
            "DA": DA,
            "WB": WB,
            "DB": DB,
            "T": T,
            "run_a": run_a,
            "run_b": run_b,
            "filler": filler,
            "filler_a_x0": filler_a_x0,
            "filler_a_x1": filler_a_x1,
            "filler_b_y0": filler_b_y0,
            "filler_b_y1": filler_b_y1,
            "door_a_end": door_a_end,
            "door_b_end": door_b_end,
        }


    def _make_corner_carcass(self, obj, use_plinth):
        """
        Corner Cabinet Generator 1.7

        Stable geometry based on _corner_layout():
        - equal left/right filler width,
        - each filler touches its side panel,
        - shelves terminate before fillers,
        - continuous full-length L plinth,
        - no filler / shelf / side intersections.
        """

        layout = self._corner_layout(obj)

        W = layout["W"]
        DA = layout["DA"]
        WB = layout["WB"]
        DB = layout["DB"]
        T = layout["T"]

        H = float(obj.Height.Value)
        BT = float(obj.BackThickness.Value)

        plinth = (
            float(obj.PlinthHeight.Value)
            if use_plinth
            else 0.0
        )

        body_h = H - plinth
        clear_h = body_h - 2.0 * T

        if min(W, DA, WB, DB, H, T, BT) <= 0.01:
            return Part.Shape()

        if clear_h <= 0.01:
            return Part.Shape()

        def plate_from_points(points, z, thickness):
            wire = Part.makePolygon(
                points + [points[0]]
            )
            face = Part.Face(wire)
            shape = face.extrude(
                App.Vector(0.0, 0.0, thickness)
            )
            shape.translate(
                App.Vector(0.0, 0.0, z)
            )
            try:
                return shape.removeSplitter()
            except Exception:
                return shape

        # Full outer L footprint for bottom/top.
        outer_pts = [
            App.Vector(0.0, 0.0, 0.0),
            App.Vector(W,   0.0, 0.0),
            App.Vector(W,   DA,  0.0),
            App.Vector(DB,  DA,  0.0),
            App.Vector(DB,  WB,  0.0),
            App.Vector(0.0, WB,  0.0),
        ]

        shapes = [
            plate_from_points(
                outer_pts,
                plinth,
                T,
            ),
            plate_from_points(
                outer_pts,
                plinth + body_h - T,
                T,
            ),
        ]

        z_vertical = plinth + T

        # Rear panels.
        shapes.append(
            Part.makeBox(
                W,
                BT,
                clear_h,
                App.Vector(0.0, 0.0, z_vertical),
            )
        )

        if WB - BT > 0.01:
            shapes.append(
                Part.makeBox(
                    BT,
                    WB - BT,
                    clear_h,
                    App.Vector(0.0, BT, z_vertical),
                )
            )

        # Outer sides.
        shapes.append(
            Part.makeBox(
                T,
                max(0.01, DA - BT),
                clear_h,
                App.Vector(W - T, BT, z_vertical),
            )
        )

        shapes.append(
            Part.makeBox(
                max(0.01, DB - BT),
                T,
                clear_h,
                App.Vector(BT, WB - T, z_vertical),
            )
        )

        # Equal-width fillers touching side panels.
        filler = layout["filler"]

        shapes.append(
            Part.makeBox(
                filler,
                T,
                clear_h,
                App.Vector(
                    layout["filler_a_x0"],
                    DA - T,
                    z_vertical,
                ),
            )
        )

        shapes.append(
            Part.makeBox(
                T,
                filler,
                clear_h,
                App.Vector(
                    DB - T,
                    layout["filler_b_y0"],
                    z_vertical,
                ),
            )
        )

        # Shelf footprint ends on INNER faces of fillers.
        shelf_pts = [
            App.Vector(BT, BT, 0.0),
            App.Vector(W - T, BT, 0.0),
            App.Vector(W - T, DA - T, 0.0),
            App.Vector(layout["filler_a_x0"], DA - T, 0.0),
            App.Vector(layout["filler_a_x0"], DA, 0.0),
            App.Vector(DB, DA, 0.0),
            App.Vector(DB, layout["filler_b_y0"], 0.0),
            App.Vector(DB - T, layout["filler_b_y0"], 0.0),
            App.Vector(DB - T, WB - T, 0.0),
            App.Vector(BT, WB - T, 0.0),
        ]

        shelf_count = max(
            0,
            int(obj.ShelfCount),
        )

        if shelf_count > 0:
            free_z = clear_h - shelf_count * T

            if free_z > 0.01:
                gap_z = free_z / float(
                    shelf_count + 1
                )

                z = z_vertical + gap_z

                for _ in range(shelf_count):
                    shapes.append(
                        plate_from_points(
                            shelf_pts,
                            z,
                            T,
                        )
                    )
                    z += T + gap_z

        # Connected recessed L plinth with a clean butt joint.
        #
        # A leg runs continuously through the inside corner.
        # B leg is shortened by exactly one plinth thickness at the joint,
        # so it meets the side face of A instead of overlapping it.

        if use_plinth and plinth > 0.01:
            setback = max(
                0.0,
                float(obj.PlinthSetback.Value),
            )

            plinth_t = T

            # Recessed front lines of both plinth legs.
            a_y = max(
                BT,
                DA - setback - plinth_t,
            )

            b_x = max(
                BT,
                DB - setback - plinth_t,
            )

            # --------------------------------------------------
            # A LEG — continuous through the inside corner
            # --------------------------------------------------

            a_x0 = b_x

            a_len = max(
                0.0,
                W - a_x0,
            )

            if a_len > 0.01:
                shapes.append(
                    Part.makeBox(
                        a_len,
                        plinth_t,
                        plinth,
                        App.Vector(
                            a_x0,
                            a_y,
                            0.0,
                        ),
                    )
                )

            # --------------------------------------------------
            # B LEG — shortened by exactly one plinth thickness
            # --------------------------------------------------
            #
            # In V2 B started at a_y, so it overlapped A.
            # Now it starts at a_y + plinth_t.
            # Result: clean edge-to-face connection with no overlap.

            b_y0 = (
                a_y
                + plinth_t
            )

            b_len = max(
                0.0,
                WB - b_y0,
            )

            if b_len > 0.01:
                shapes.append(
                    Part.makeBox(
                        plinth_t,
                        b_len,
                        plinth,
                        App.Vector(
                            b_x,
                            b_y0,
                            0.0,
                        ),
                    )
                )

        valid = [
            shape
            for shape in shapes
            if shape is not None
            and not shape.isNull()
        ]

        return Part.makeCompound(valid)


    def _front_vertical_range(
        self,
        obj,
    ):
        """Return usable front Z start and height for standard cabinets."""

        cabinet_type = str(
            obj.CabinetType
        )

        if cabinet_type in {
            CABINET_CORNER_BASE,
            CABINET_CORNER_WALL,
        }:
            return None

        if cabinet_type in {
            CABINET_BASE,
            CABINET_TALL,
            CABINET_BLIND_CORNER_BASE,
        }:
            z_start = max(
                0.0,
                obj.PlinthHeight.Value,
            )
        else:
            z_start = 0.0

        height = (
            obj.Height.Value
            - z_start
        )

        if height <= 0.001:
            return None

        return (
            z_start,
            height,
        )

    def _make_front_panel(
        self,
        x,
        z,
        width,
        height,
        depth,
        thickness,
    ):
        """Create one front panel on the cabinet local +Y face."""

        if (
            width <= 0.001
            or height <= 0.001
            or thickness <= 0.001
        ):
            return None

        return Part.makeBox(
            width,
            thickness,
            height,
            App.Vector(
                x,
                depth,
                z,
            ),
        )

    def _make_blind_corner_front_geometry(
        self,
        obj,
    ):
        """
        Visible front system for Blind Corner Base.

        The hidden box is closed by the carcass. This method adds:
        - a decorative spacer filler on the hidden side,
        - fronts only across the usable compartment.

        Standard Single / Double / Drawers / Door + Drawers / Lift-up
        configurations are supported.
        """

        W = float(
            obj.Width.Value
        )
        D = float(
            obj.Depth.Value
        )
        H = float(
            obj.Height.Value
        )
        T = float(
            obj.PanelThickness.Value
        )
        B = float(
            obj.BlindBoxWidth.Value
        )
        F = max(
            0.0,
            float(
                obj.BlindFillerWidth.Value
            ),
        )

        C = max(
            0.0,
            float(
                obj.BlindDoorFillerWidth.Value
            ),
        )

        front_depth = (
            D
            - F
        )

        if front_depth <= 0.001:
            return []

        front_t = max(
            0.001,
            float(
                obj.FrontThickness.Value
            ),
        )

        gap = max(
            0.0,
            float(
                obj.FrontGap.Value
            ),
        )

        plinth = max(
            0.0,
            float(
                obj.PlinthHeight.Value
            ),
        )

        setback = max(
            0.0,
            float(
                obj.PlinthSetback.Value
            ),
        )

        body_h = max(
            0.0,
            H - plinth,
        )

        front_h = max(
            0.0,
            H
            - plinth
            - 2.0 * gap,
        )

        if front_h <= 0.001:
            return []

        blind_side = str(
            obj.BlindSide
        )

        if blind_side == "Right":
            raw_main_left = T
            raw_main_right = (
                W
                - B
            )

            # Perpendicular spacer sits on the hidden-box boundary.
            spacer_x = (
                W
                - B
            )

            # Front clearance filler consumes width from the RIGHT side of
            # the usable opening, next to the corner.
            clearance_w = min(
                C,
                max(
                    0.0,
                    raw_main_right
                    - raw_main_left
                    - 2.0 * gap
                    - 1.0,
                ),
            )

            main_left = raw_main_left
            main_right = (
                raw_main_right
                - clearance_w
            )

            clearance_x = main_right

        else:
            raw_main_left = B
            raw_main_right = (
                W
                - T
            )

            # Mirror of the right-side solution.
            spacer_x = (
                B
                - front_t
            )

            # Front clearance filler consumes width from the LEFT side of
            # the usable opening, next to the corner.
            clearance_w = min(
                C,
                max(
                    0.0,
                    raw_main_right
                    - raw_main_left
                    - 2.0 * gap
                    - 1.0,
                ),
            )

            main_left = (
                raw_main_left
                + clearance_w
            )

            main_right = raw_main_right

            clearance_x = raw_main_left

        available_width = (
            main_right
            - main_left
            - 2.0 * gap
        )

        if available_width <= 0.001:
            return []

        shapes = []

        # --------------------------------------------------
        # 1) Perpendicular corner spacer / blenda dystansowa
        # --------------------------------------------------
        #
        # Height = cabinet height WITHOUT plinth.
        # Bottom = top of plinth.
        #
        # It is recessed by PlinthSetback so its corner line matches the
        # neighbouring cabinet's recessed toe-kick/plinth position.
        if (
            F > 0.001
            and body_h > 0.001
        ):
            # The perpendicular Corner Spacer is now the PHYSICAL distance
            # between the shortened long cabinet and the 90-degree cabinet.
            #
            # Long cabinet front/body: Y = D - F
            # 90-degree cabinet corner line: Y = D
            # Spacer: exactly fills Y = D-F ... D.
            spacer_y = front_depth

            filler = Part.makeBox(
                front_t,
                F,
                body_h,
                App.Vector(
                    spacer_x,
                    spacer_y,
                    plinth,
                ),
            )

            shapes.append(
                filler
            )

        # --------------------------------------------------
        # 2) Front clearance filler / blenda pod zawias
        # --------------------------------------------------
        #
        # This is a second independently adjustable filler in the cabinet
        # front plane. It shortens the doors/drawers so they have clearance
        # from the 90-degree neighbouring cabinet.
        if (
            clearance_w > 0.001
            and body_h > 0.001
        ):
            clearance_filler = Part.makeBox(
                clearance_w,
                front_t,
                body_h,
                App.Vector(
                    clearance_x,
                    front_depth,
                    plinth,
                ),
            )

            shapes.append(
                clearance_filler
            )

        front_type = str(
            obj.FrontType
        )

        if front_type == FRONT_OPEN:
            return shapes

        try:
            open_angle = max(
                0.0,
                min(
                    120.0,
                    float(
                        obj.FrontOpenAngle.Value
                    ),
                ),
            )
        except Exception:
            open_angle = 0.0

        try:
            drawer_open_distance = max(
                0.0,
                float(
                    obj.DrawerOpenDistance.Value
                ),
            )
        except Exception:
            drawer_open_distance = 0.0

        z_start = (
            plinth
            + gap
        )

        closed_x = (
            main_left
            + gap
        )

        left_hinge_x = main_left
        right_hinge_x = main_right
        hinge_y = front_depth

        is_open_preview = (
            abs(
                open_angle
            )
            > 0.0001
        )

        if front_type == FRONT_SINGLE:
            hinge_side = str(
                getattr(
                    obj,
                    "SingleDoorHingeSide",
                    "Left",
                )
            )

            if hinge_side == "Right":
                panel_x = (
                    right_hinge_x
                    - available_width
                    if is_open_preview
                    else closed_x
                )
            else:
                panel_x = (
                    left_hinge_x
                    if is_open_preview
                    else closed_x
                )

            panel = self._make_front_panel(
                panel_x,
                z_start,
                available_width,
                front_h,
                front_depth,
                front_t,
            )

            if panel is not None:
                if hinge_side == "Right":
                    panel = self._rotate_front_leaf(
                        panel,
                        right_hinge_x,
                        hinge_y,
                        -open_angle,
                    )
                else:
                    panel = self._rotate_front_leaf(
                        panel,
                        left_hinge_x,
                        hinge_y,
                        open_angle,
                    )

                shapes.append(
                    panel
                )

        elif front_type == FRONT_DOUBLE:
            leaf_w = (
                available_width
                - gap
            ) / 2.0

            if leaf_w > 0.001:
                if is_open_preview:
                    left_x = left_hinge_x
                    right_x = (
                        right_hinge_x
                        - leaf_w
                    )
                else:
                    left_x = closed_x
                    right_x = (
                        closed_x
                        + leaf_w
                        + gap
                    )

                left = self._make_front_panel(
                    left_x,
                    z_start,
                    leaf_w,
                    front_h,
                    front_depth,
                    front_t,
                )

                right = self._make_front_panel(
                    right_x,
                    z_start,
                    leaf_w,
                    front_h,
                    front_depth,
                    front_t,
                )

                if left is not None:
                    left = self._rotate_front_leaf(
                        left,
                        left_hinge_x,
                        hinge_y,
                        open_angle,
                    )
                    shapes.append(
                        left
                    )

                if right is not None:
                    right = self._rotate_front_leaf(
                        right,
                        right_hinge_x,
                        hinge_y,
                        -open_angle,
                    )
                    shapes.append(
                        right
                    )

        elif front_type == FRONT_DRAWERS:
            count = max(
                1,
                int(
                    obj.DrawerCount
                ),
            )

            drawer_h = (
                front_h
                - gap
                * (
                    count - 1
                )
            ) / count

            if drawer_h > 0.001:
                z = z_start

                for _ in range(
                    count
                ):
                    panel = self._make_front_panel(
                        closed_x,
                        z,
                        available_width,
                        drawer_h,
                        front_depth
                        + drawer_open_distance,
                        front_t,
                    )

                    if panel is not None:
                        shapes.append(
                            panel
                        )

                    z += (
                        drawer_h
                        + gap
                    )

        elif front_type == FRONT_DOOR_DRAWERS:
            requested_drawer_h = max(
                0.0,
                float(
                    obj.DrawerZoneHeight.Value
                ),
            )

            drawer_h = min(
                requested_drawer_h,
                max(
                    0.0,
                    front_h - gap,
                ),
            )

            door_h = (
                front_h
                - drawer_h
                - gap
            )

            if drawer_h > 0.001:
                drawer = self._make_front_panel(
                    closed_x,
                    z_start,
                    available_width,
                    drawer_h,
                    front_depth
                    + drawer_open_distance,
                    front_t,
                )

                if drawer is not None:
                    shapes.append(
                        drawer
                    )

            if door_h > 0.001:
                door = self._make_front_panel(
                    closed_x,
                    z_start
                    + drawer_h
                    + gap,
                    available_width,
                    door_h,
                    front_depth,
                    front_t,
                )

                if door is not None:
                    shapes.append(
                        door
                    )

        elif front_type == FRONT_LIFT_UP:
            panel = self._make_front_panel(
                closed_x,
                z_start,
                available_width,
                front_h,
                front_depth,
                front_t,
            )

            if panel is not None:
                shapes.append(
                    panel
                )

        return shapes


    def _rotate_point_around_z(
        self,
        point,
        pivot,
        angle,
    ):
        """Return a point rotated around a local vertical Z axis."""

        try:
            rotation = App.Rotation(
                App.Vector(
                    0.0,
                    0.0,
                    1.0,
                ),
                float(
                    angle
                ),
            )

            relative = (
                point
                - pivot
            )

            rotated = rotation.multVec(
                relative
            )

            return (
                pivot
                + rotated
            )

        except Exception:
            return point


    def _make_corner_front_geometry(self, obj):
        """
        Corner Generator 1.7 — Full Edge Fronts + Hinge Clearance

        Keeps the accepted full-edge 90-degree front geometry.

        Change:
        - Leaf A still owns the inside corner.
        - Leaf B is shortened ONLY at the meeting edge.
        - The shortening equals FrontGap.
        - Leaf B still reaches the outer cabinet edge.
        - This creates clearance for future opening/rotation of Leaf B.
        """

        if str(
            obj.FrontType
        ) != FRONT_CORNER_FOLDING:
            return []

        try:
            W = float(
                obj.Width.Value
            )
            DA = float(
                obj.Depth.Value
            )
            WB = float(
                obj.WidthB.Value
            )
            DB = float(
                obj.DepthB.Value
            )

            front_t = max(
                0.01,
                float(
                    obj.FrontThickness.Value
                ),
            )

            gap = max(
                0.0,
                float(
                    obj.FrontGap.Value
                ),
            )

            try:
                open_angle = max(
                    0.0,
                    min(
                        90.0,
                        float(
                            obj.FrontOpenAngle.Value
                        ),
                    ),
                )
            except Exception:
                open_angle = 0.0

        except Exception:
            return []

        if str(
            obj.CabinetType
        ) == CABINET_CORNER_BASE:
            z0 = max(
                0.0,
                float(
                    obj.PlinthHeight.Value
                ),
            )
        else:
            z0 = 0.0

        front_z = (
            z0
            + gap
        )

        front_h = (
            float(
                obj.Height.Value
            )
            - z0
            - 2.0 * gap
        )

        if front_h <= 0.01:
            return []

        # --------------------------------------------------
        # FULL-EDGE 90° JOINT WITH OPENING CLEARANCE
        # --------------------------------------------------
        #
        # Leaf A:
        #   starts at the inside corner and reaches the outer A edge.
        #
        # Leaf B:
        #   normally would start exactly after Leaf A thickness.
        #   We add one FrontGap at this meeting edge so the right leaf
        #   has physical clearance to rotate/open later.
        #
        # Outer edge position of Leaf B remains unchanged.

        leaf_a_len = (
            W
            - DB
            - gap
        )

        leaf_b_y0 = (
            DA
            + front_t
            + gap
        )

        leaf_b_outer_y = (
            WB
            - gap
        )

        leaf_b_len = (
            leaf_b_outer_y
            - leaf_b_y0
        )

        if (
            leaf_a_len <= 0.01
            or leaf_b_len <= 0.01
        ):
            return []

        leaf_a = Part.makeBox(
            leaf_a_len,
            front_t,
            front_h,
            App.Vector(
                DB,
                DA,
                front_z,
            ),
        )

        leaf_b = Part.makeBox(
            front_t,
            leaf_b_len,
            front_h,
            App.Vector(
                DB,
                leaf_b_y0,
                front_z,
            ),
        )

        # --------------------------------------------------
        # CORNER FOLDING OPENING
        # --------------------------------------------------
        #
        # At 0° nothing is transformed: this preserves the accepted
        # Corner Generator 1.7 closed geometry exactly.
        #
        # Opening model:
        # 1. Leaf A is hinged at its OUTER A edge.
        # 2. Leaf B follows Leaf A around that cabinet hinge.
        # 3. Leaf B then folds around the moving A/B joint.
        #
        # At 90° the two leaves become approximately parallel/folded
        # together outside the cabinet opening.

        if open_angle > 0.0001:
            outer_hinge = App.Vector(
                W - gap,
                DA,
                0.0,
            )

            joint_closed = App.Vector(
                DB,
                DA + front_t,
                0.0,
            )

            # The room/opening lies in the re-entrant corner. Rotating A
            # clockwise around its outer hinge moves it out of the cabinet.
            cabinet_rotation = -open_angle

            leaf_a.rotate(
                outer_hinge,
                App.Vector(
                    0.0,
                    0.0,
                    1.0,
                ),
                cabinet_rotation,
            )

            # Leaf B first follows the whole folding pair.
            leaf_b.rotate(
                outer_hinge,
                App.Vector(
                    0.0,
                    0.0,
                    1.0,
                ),
                cabinet_rotation,
            )

            # Find the joint after the first rotation.
            joint_open = self._rotate_point_around_z(
                joint_closed,
                outer_hinge,
                cabinet_rotation,
            )

            # Then fold B onto A around the moving joint.
            leaf_b.rotate(
                joint_open,
                App.Vector(
                    0.0,
                    0.0,
                    1.0,
                ),
                -open_angle,
            )

        return [
            leaf_a,
            leaf_b,
        ]


    def _rotate_front_leaf(
        self,
        shape,
        hinge_x,
        hinge_y,
        angle,
    ):
        """
        Rotate one standard front leaf around a local vertical hinge axis.

        Standard front-opening convention in OpenInteriorCAD:
        the leaf swings outward from the cabinet opening.

        The caller supplies a hinge axis located at the cabinet clear-opening
        boundary and on the cabinet front plane. When FrontOpenAngle is greater
        than zero, the leaf is rebuilt from that hinge line before rotation.
        This prevents the opened leaf from entering the cabinet interior while
        preserving the original closed overlay-front geometry at 0 degrees.

        Left-hinged leaf uses a positive Z rotation.
        Right-hinged leaf uses a negative Z rotation.
        """

        if shape is None:
            return None

        try:
            angle = float(
                angle
            )
        except Exception:
            angle = 0.0

        if abs(
            angle
        ) <= 0.0001:
            return shape

        try:
            shape.rotate(
                App.Vector(
                    float(
                        hinge_x
                    ),
                    float(
                        hinge_y
                    ),
                    0.0,
                ),
                App.Vector(
                    0.0,
                    0.0,
                    1.0,
                ),
                angle,
            )
        except Exception:
            return shape

        return shape


    def _make_front_geometry(
        self,
        obj,
    ):
        """
        Generate closed front panels for standard rectangular cabinets.

        Corner cabinets intentionally remain open in 0.1; their folding
        front system will be implemented separately.
        """

        front_type = str(
            obj.FrontType
        )

        cabinet_type = str(
            obj.CabinetType
        )

        if cabinet_type in {
            CABINET_CORNER_BASE,
            CABINET_CORNER_WALL,
        }:
            return self._make_corner_front_geometry(
                obj
            )

        if cabinet_type == CABINET_BLIND_CORNER_BASE:
            return self._make_blind_corner_front_geometry(
                obj
            )

        if front_type == FRONT_OPEN:
            return []

        vertical = self._front_vertical_range(
            obj
        )

        if vertical is None:
            return []

        z_start, front_height = vertical

        width = obj.Width.Value
        depth = obj.Depth.Value
        thickness = obj.FrontThickness.Value
        gap = max(
            0.0,
            obj.FrontGap.Value,
        )

        try:
            open_angle = max(
                0.0,
                min(
                    120.0,
                    float(
                        obj.FrontOpenAngle.Value
                    ),
                ),
            )
        except Exception:
            open_angle = 0.0

        try:
            drawer_open_distance = max(
                0.0,
                float(
                    obj.DrawerOpenDistance.Value
                ),
            )
        except Exception:
            drawer_open_distance = 0.0

        available_width = (
            width
            - 2.0 * gap
        )

        available_height = (
            front_height
            - 2.0 * gap
        )

        if (
            available_width <= 0.001
            or available_height <= 0.001
        ):
            return []

        y_depth = depth

        # Concealed-hinge visual pivot.
        #
        # The clear cabinet opening begins at the inner face of each side:
        #   left  = PanelThickness
        #   right = Width - PanelThickness
        #
        # The hinge axis is also moved to the OUTER face of the front
        # (Depth + FrontThickness). Rotating around the old axis at the
        # rear face of the front caused the door thickness itself to swing
        # beyond the cabinet side.
        panel_t = max(
            0.0,
            float(
                obj.PanelThickness.Value
            ),
        )

        # Hinge axis lies on the cabinet front plane.
        # The opened leaf is rebuilt from the clear-opening hinge line,
        # so it swings outward without moving into the cabinet interior.
        hinge_y = y_depth

        left_hinge_x = max(
            gap,
            panel_t,
        )

        right_hinge_x = min(
            width - gap,
            width - panel_t,
        )

        is_open_preview = (
            abs(
                open_angle
            )
            > 0.0001
        )

        shapes = []

        if front_type == FRONT_SINGLE:
            hinge_side = str(
                getattr(
                    obj,
                    "SingleDoorHingeSide",
                    "Left",
                )
            )

            if hinge_side == "Right":
                panel_x = (
                    right_hinge_x
                    - available_width
                    if is_open_preview
                    else gap
                )
            else:
                panel_x = (
                    left_hinge_x
                    if is_open_preview
                    else gap
                )

            panel = self._make_front_panel(
                panel_x,
                z_start + gap,
                available_width,
                available_height,
                y_depth,
                thickness,
            )

            if panel is not None:
                if hinge_side == "Right":
                    panel = self._rotate_front_leaf(
                        panel,
                        right_hinge_x,
                        hinge_y,
                        -open_angle,
                    )
                else:
                    panel = self._rotate_front_leaf(
                        panel,
                        left_hinge_x,
                        hinge_y,
                        open_angle,
                    )

                shapes.append(
                    panel
                )

        elif front_type == FRONT_DOUBLE:
            leaf_width = (
                available_width
                - gap
            ) / 2.0

            if leaf_width > 0.001:
                if is_open_preview:
                    left_x = left_hinge_x
                    right_x = (
                        right_hinge_x
                        - leaf_width
                    )
                else:
                    left_x = gap
                    right_x = (
                        gap
                        + leaf_width
                        + gap
                    )

                left = self._make_front_panel(
                    left_x,
                    z_start + gap,
                    leaf_width,
                    available_height,
                    y_depth,
                    thickness,
                )

                right = self._make_front_panel(
                    right_x,
                    z_start + gap,
                    leaf_width,
                    available_height,
                    y_depth,
                    thickness,
                )

                if left is not None:
                    left = self._rotate_front_leaf(
                        left,
                        left_hinge_x,
                        hinge_y,
                        open_angle,
                    )

                    shapes.append(
                        left
                    )

                if right is not None:
                    right = self._rotate_front_leaf(
                        right,
                        right_hinge_x,
                        hinge_y,
                        -open_angle,
                    )

                    shapes.append(
                        right
                    )

        elif front_type == FRONT_DRAWERS:
            count = max(
                1,
                int(
                    obj.DrawerCount
                ),
            )

            drawer_height = (
                available_height
                - gap
                * (
                    count
                    - 1
                )
            ) / count

            if drawer_height > 0.001:
                z = (
                    z_start
                    + gap
                )

                for _ in range(
                    count
                ):
                    panel = self._make_front_panel(
                        gap,
                        z,
                        available_width,
                        drawer_height,
                        y_depth
                        + drawer_open_distance,
                        thickness,
                    )

                    if panel is not None:
                        shapes.append(
                            panel
                        )

                    z += (
                        drawer_height
                        + gap
                    )

        elif front_type == FRONT_DOOR_DRAWERS:
            drawer_zone = max(
                0.0,
                min(
                    obj.DrawerZoneHeight.Value,
                    available_height
                    - gap,
                ),
            )

            door_height = (
                available_height
                - drawer_zone
                - gap
            )

            if (
                drawer_zone > 0.001
                and door_height > 0.001
            ):
                drawer = self._make_front_panel(
                    gap,
                    z_start
                    + gap
                    + door_height
                    + gap,
                    available_width,
                    drawer_zone,
                    y_depth
                    + drawer_open_distance,
                    thickness,
                )

                door = self._make_front_panel(
                    gap,
                    z_start + gap,
                    available_width,
                    door_height,
                    y_depth,
                    thickness,
                )

                if drawer is not None:
                    shapes.append(
                        drawer
                    )

                if door is not None:
                    shapes.append(
                        door
                    )

        elif front_type == FRONT_LIFT_UP:
            # In 0.1 this is a single closed horizontal lift-up panel.
            panel = self._make_front_panel(
                gap,
                z_start + gap,
                available_width,
                available_height,
                y_depth,
                thickness,
            )

            if panel is not None:
                shapes.append(
                    panel
                )

        return shapes

    def _make_carcass_geometry(
        self,
        obj,
    ):
        cabinet_type = str(
            obj.CabinetType
        )

        if cabinet_type == CABINET_WALL:
            return self._make_standard_carcass(
                obj,
                use_plinth=False,
            )

        if cabinet_type == CABINET_TALL:
            return self._make_standard_carcass(
                obj,
                use_plinth=True,
            )

        if cabinet_type == CABINET_CORNER_BASE:
            return self._make_corner_carcass(
                obj,
                use_plinth=True,
            )

        if cabinet_type == CABINET_CORNER_WALL:
            return self._make_corner_carcass(
                obj,
                use_plinth=False,
            )

        if cabinet_type == CABINET_BLIND_CORNER_BASE:
            return self._make_blind_corner_carcass(
                obj
            )

        return self._make_standard_carcass(
            obj,
            use_plinth=True,
        )

    def _ensure_board_part_properties(
        self,
        obj,
    ):
        """Add non-geometric production metadata properties."""

        if not hasattr(
            obj,
            "BoardPartsJSON",
        ):
            obj.addProperty(
                "App::PropertyString",
                "BoardPartsJSON",
                "Production",
                "Serialized logical board-part list for BOM / Cut List.",
            )

        if not hasattr(
            obj,
            "BoardPartCount",
        ):
            obj.addProperty(
                "App::PropertyInteger",
                "BoardPartCount",
                "Production",
                "Number of logical board parts in this cabinet.",
            )

        if not hasattr(
            obj,
            "BoardMaterial",
        ):
            obj.addProperty(
                "App::PropertyString",
                "BoardMaterial",
                "Production",
                "Material used for carcass boards.",
            )
            obj.BoardMaterial = "Carcass Board"

        if not hasattr(
            obj,
            "FrontMaterial",
        ):
            obj.addProperty(
                "App::PropertyString",
                "FrontMaterial",
                "Production",
                "Material used for fronts.",
            )
            obj.FrontMaterial = "Front Board"

        if not hasattr(
            obj,
            "BackMaterial",
        ):
            obj.addProperty(
                "App::PropertyString",
                "BackMaterial",
                "Production",
                "Material used for back panels.",
            )
            obj.BackMaterial = "Back Board"

        if not hasattr(
            obj,
            "EdgeMaterial",
        ):
            obj.addProperty(
                "App::PropertyString",
                "EdgeMaterial",
                "Production",
                "Default edge-band material.",
            )
            obj.EdgeMaterial = "ABS"

        if not hasattr(
            obj,
            "EdgeThickness",
        ):
            obj.addProperty(
                "App::PropertyLength",
                "EdgeThickness",
                "Production",
                "Default edge-band thickness.",
            )
            obj.EdgeThickness = 0.8

        if not hasattr(
            obj,
            "EdgeOverridesJSON",
        ):
            obj.addProperty(
                "App::PropertyString",
                "EdgeOverridesJSON",
                "Production",
                "Per-part edge-band overrides used by Cut List.",
            )
            obj.EdgeOverridesJSON = "{}"

        try:
            obj.setEditorMode(
                "BoardPartsJSON",
                1,
            )

            obj.setEditorMode(
                "BoardPartCount",
                1,
            )

            obj.setEditorMode(
                "EdgeOverridesJSON",
                1,
            )

        except Exception:
            pass


    def _update_board_parts(
        self,
        obj,
    ):
        """
        Rebuild logical production parts from current cabinet parameters.

        This does not change Shape and therefore cannot disturb the accepted
        cabinet geometry.
        """

        self._ensure_board_part_properties(
            obj
        )

        try:
            parts = build_board_parts(
                obj
            )
        except Exception:
            parts = []

        try:
            obj.BoardPartCount = len(
                parts
            )
        except Exception:
            pass

        try:
            obj.BoardPartsJSON = board_parts_json(
                parts
            )
        except Exception:
            try:
                obj.BoardPartsJSON = "[]"
            except Exception:
                pass


    def _corner_dimensions_ready(
        self,
        obj,
    ):
        """
        Return False while Width A / Width B are temporarily invalid.

        FreeCAD updates quantity spin boxes while the user is typing.
        For example, replacing 900 with 1000 can briefly produce 0 / 1 / 10.
        The old 1.7 generator tried to rebuild at each intermediate value,
        which caused Part.makeBox() errors such as:
        "width of box too small" / "length of box too small".

        This helper does NOT change any cabinet geometry. It only postpones
        the rebuild until the dimensions form a valid corner again.
        """

        try:
            cabinet_type = str(
                obj.CabinetType
            )

            if cabinet_type not in {
                CABINET_CORNER_BASE,
                CABINET_CORNER_WALL,
            }:
                return True

            width_a = float(
                obj.Width.Value
            )

            depth_a = float(
                obj.Depth.Value
            )

            width_b = float(
                obj.WidthB.Value
            )

            depth_b = float(
                obj.DepthB.Value
            )

            panel = float(
                obj.PanelThickness.Value
            )

        except Exception:
            return False

        eps = 0.01

        if min(
            width_a,
            depth_a,
            width_b,
            depth_b,
            panel,
        ) <= eps:
            return False

        # Each corner leg must leave actual space beyond the opposite depth.
        # Keep exactly the same 1.7 geometry assumptions; this is only a guard.
        if (
            width_a - depth_b <= panel + eps
            or width_b - depth_a <= panel + eps
        ):
            return False

        return True


    def _blind_corner_dimensions_ready(
        self,
        obj,
    ):
        """Validate Blind Corner Base dimensions during live editing."""

        try:
            if str(
                obj.CabinetType
            ) != CABINET_BLIND_CORNER_BASE:
                return True

            W = float(
                obj.Width.Value
            )
            D = float(
                obj.Depth.Value
            )
            H = float(
                obj.Height.Value
            )
            T = float(
                obj.PanelThickness.Value
            )
            BT = float(
                obj.BackThickness.Value
            )
            B = float(
                obj.BlindBoxWidth.Value
            )
            F = float(
                obj.BlindFillerWidth.Value
            )
            C = float(
                obj.BlindDoorFillerWidth.Value
            )
            MW = float(
                obj.BlindMateWidth.Value
            )
            MD = float(
                obj.BlindMateDepth.Value
            )

        except Exception:
            return False

        eps = 0.01

        if min(
            W,
            D,
            H,
            T,
            BT,
            B,
        ) <= eps:
            return False

        body_depth = (
            D - F
        )

        if body_depth <= BT + T + 100.0:
            return False

        # Hidden box needs two panel thicknesses and useful internal volume.
        if B <= 2.0 * T + 50.0:
            return False

        # Accessible compartment must retain useful clear width.
        if W - B - T <= 100.0:
            return False

        if F < 0.0:
            return False

        if C < 0.0:
            return False

        # The clearance filler must leave a usable front opening.
        if C >= W - B - T - 2.0:
            return False

        if MW <= 50.0:
            return False

        if MD <= 50.0:
            return False

        return True


    def _blind_mate_local_placement(
        self,
        obj,
    ):
        """
        Return mate origin/rotation in the parent cabinet LOCAL coordinate system.

        The perpendicular cabinet begins exactly after the adjustable corner
        spacer. Hidden Side mirrors the complete corner arrangement.
        """

        W = float(
            obj.Width.Value
        )
        D = float(
            obj.Depth.Value
        )
        B = float(
            obj.BlindBoxWidth.Value
        )
        F = max(
            0.0,
            float(
                obj.BlindFillerWidth.Value
            ),
        )
        setback = max(
            0.0,
            float(
                obj.PlinthSetback.Value
            ),
        )
        mate_depth = float(
            obj.BlindMateDepth.Value
        )

        # The 90° cabinet remains on the original outer corner line.
        # The long Blind Corner cabinet is shortened by F, so the Corner
        # Spacer occupies the exact gap between D-F and D.
        corner_line_y = D

        blind_side = str(
            obj.BlindSide
        )

        filler_end_y = corner_line_y

        mate_width = float(
            obj.BlindMateWidth.Value
        )

        if blind_side == "Left":
            # Hidden box / return cabinet on the LEFT.
            #
            # Rotation -90° maps the mate local +X (its Width) toward -Y.
            # Therefore its origin must be placed at the FAR Y end so the
            # complete cabinet spans:
            #
            #   Y = filler_end_y ... filler_end_y + mate_width
            #
            # exactly like the Right variant, but mirrored in X.
            boundary_x = B

            local_position = App.Vector(
                boundary_x
                - mate_depth,
                filler_end_y
                + mate_width,
                0.0,
            )

            relative_rotation = -90.0

        else:
            # Hidden box / return cabinet on the RIGHT.
            # Rotation +90° maps mate Width toward +Y.
            boundary_x = (
                W
                - B
            )

            local_position = App.Vector(
                boundary_x
                + mate_depth,
                filler_end_y,
                0.0,
            )

            relative_rotation = 90.0

        return (
            local_position,
            relative_rotation,
        )

    def _local_point_to_world(
        self,
        obj,
        point,
    ):
        """Transform a local parent-cabinet point into document coordinates."""

        rotation = App.Rotation(
            App.Vector(
                0.0,
                0.0,
                1.0,
            ),
            float(
                obj.RotationAngle.Value
            ),
        )

        rotated = rotation.multVec(
            point
        )

        return App.Vector(
            obj.Position.x + rotated.x,
            obj.Position.y + rotated.y,
            obj.Position.z + rotated.z,
        )

    def _sync_blind_corner_mate(
        self,
        obj,
    ):
        """Keep an existing linked perpendicular cabinet aligned."""

        if str(
            obj.CabinetType
        ) != CABINET_BLIND_CORNER_BASE:
            return

        try:
            mate = obj.BlindMate
        except Exception:
            mate = None

        if mate is None:
            return

        try:
            if mate.Document is None:
                return
        except Exception:
            return

        local_position, relative_rotation = (
            self._blind_mate_local_placement(
                obj
            )
        )

        world_position = (
            self._local_point_to_world(
                obj,
                local_position,
            )
        )

        try:
            mate.Position = world_position
            mate.RotationAngle = (
                float(
                    obj.RotationAngle.Value
                )
                + relative_rotation
            )

            mate.Width = float(
                obj.BlindMateWidth.Value
            )
            mate.Depth = float(
                obj.BlindMateDepth.Value
            )
            mate.Height = float(
                obj.Height.Value
            )

            # Keep construction levels aligned across the corner.
            mate.PanelThickness = float(
                obj.PanelThickness.Value
            )
            mate.BackThickness = float(
                obj.BackThickness.Value
            )
            mate.PlinthHeight = float(
                obj.PlinthHeight.Value
            )
            mate.PlinthSetback = float(
                obj.PlinthSetback.Value
            )

        except Exception:
            return


    def rebuild_geometry(
        self,
        obj,
    ):
        # Width A / Width B fields emit intermediate values while typing.
        # Keep the last valid Shape until the final valid value is entered.
        if not self._corner_dimensions_ready(
            obj
        ):
            return

        if not self._blind_corner_dimensions_ready(
            obj
        ):
            return

        self._update_board_parts(
            obj
        )

        if str(
            obj.GeometryMode
        ) == GEOMETRY_CARCASS:
            carcass = (
                self._make_carcass_geometry(
                    obj
                )
            )

            front_shapes = (
                self._make_front_geometry(
                    obj
                )
            )

            shapes = []

            if not carcass.isNull():
                shapes.append(
                    carcass
                )

            shapes.extend(
                front_shapes
            )

            if shapes:
                shape = Part.makeCompound(
                    shapes
                )
            else:
                shape = Part.Shape()

        else:
            shape = (
                self._make_box_geometry(
                    obj
                )
            )

        shape.Placement = App.Placement(
            App.Vector(
                obj.Position.x,
                obj.Position.y,
                obj.Position.z,
            ),
            App.Rotation(
                App.Vector(
                    0.0,
                    0.0,
                    1.0,
                ),
                obj.RotationAngle.Value,
            ),
        )

        obj.Shape = shape

        if str(
            obj.CabinetType
        ) == CABINET_BLIND_CORNER_BASE:
            self._sync_blind_corner_mate(
                obj
            )

    def execute(
        self,
        obj,
    ):
        self.rebuild_geometry(
            obj
        )

    def onChanged(
        self,
        obj,
        property_name,
    ):
        watched = {
            "CabinetType",
            "Width",
            "Depth",
            "WidthB",
            "DepthB",
            "Height",
            "Position",
            "RotationAngle",
            "GeometryMode",
            "PanelThickness",
            "BackThickness",
            "ShelfCount",
            "PlinthHeight",
            "PlinthSetback",
            "FrontType",
            "FrontThickness",
            "FrontGap",
            "FrontOpenAngle",
            "SingleDoorHingeSide",
            "DrawerOpenDistance",
            "DrawerCount",
            "DrawerZoneHeight",
            "CornerOpeningWidth",
            "BlindSide",
            "BlindBoxWidth",
            "BlindFillerWidth",
            "BlindDoorFillerWidth",
            "BlindMateWidth",
            "BlindMateDepth",
        }

        if property_name not in watched:
            return

        required = {
            "CabinetType",
            "Width",
            "Depth",
            "WidthB",
            "DepthB",
            "Height",
            "Position",
            "RotationAngle",
            "GeometryMode",
            "PanelThickness",
            "BackThickness",
            "ShelfCount",
            "PlinthHeight",
            "PlinthSetback",
            "MountHeight",
            "FrontType",
            "FrontThickness",
            "FrontGap",
            "FrontOpenAngle",
            "SingleDoorHingeSide",
            "DrawerOpenDistance",
            "DrawerCount",
            "DrawerZoneHeight",
            "BlindSide",
            "BlindBoxWidth",
            "BlindFillerWidth",
            "BlindDoorFillerWidth",
            "BlindMateWidth",
            "BlindMateDepth",
            "BlindMate",
        }

        if not required.issubset(
            set(
                obj.PropertiesList
            )
        ):
            return

        if not self._corner_dimensions_ready(
            obj
        ):
            return

        if not self._blind_corner_dimensions_ready(
            obj
        ):
            return

        try:
            self.rebuild_geometry(
                obj
            )

        except Exception as error:
            App.Console.PrintError(
                "OpenInteriorCAD furniture update error: "
                f"{error}\n"
            )

    def onDocumentRestored(
        self,
        obj,
    ):
        self._ensure_board_part_properties(
            obj
        )

        self._update_board_parts(
            obj
        )

        self._add_properties(
            obj
        )

        obj.Proxy = self


class FurnitureViewProvider:
    def __init__(
        self,
        view_object,
    ):
        view_object.Proxy = self

    def attach(
        self,
        view_object,
    ):
        return

    def updateData(
        self,
        obj,
        property_name,
    ):
        return

    def getDisplayModes(
        self,
        view_object,
    ):
        return []

    def getDefaultDisplayMode(
        self,
    ):
        return "Flat Lines"

    def setDisplayMode(
        self,
        mode,
    ):
        return mode

    def onChanged(
        self,
        view_object,
        property_name,
    ):
        return

    def dumps(
        self,
    ):
        return None

    def loads(
        self,
        state,
    ):
        return None


def ensure_blind_corner_mate(
    parent,
):
    """
    Create the perpendicular standard Base cabinet if it does not exist.

    The two cabinets remain separate Furniture objects so the companion can
    still receive its own fronts, shelves, materials and production data.
    Its position/dimensions are driven by the Blind Corner parent.
    """

    if parent is None:
        return None

    if str(
        getattr(
            parent,
            "CabinetType",
            "",
        )
    ) != CABINET_BLIND_CORNER_BASE:
        return None

    document = parent.Document

    if document is None:
        return None

    try:
        mate = parent.BlindMate
    except Exception:
        mate = None

    if mate is not None:
        try:
            if mate.Document is document:
                parent.Proxy._sync_blind_corner_mate(
                    parent
                )
                return mate
        except Exception:
            pass

    local_position, relative_rotation = (
        parent.Proxy._blind_mate_local_placement(
            parent
        )
    )

    world_position = (
        parent.Proxy._local_point_to_world(
            parent,
            local_position,
        )
    )

    mate = create_furniture(
        document=document,
        position=world_position,
        width=float(
            parent.BlindMateWidth.Value
        ),
        depth=float(
            parent.BlindMateDepth.Value
        ),
        height=float(
            parent.Height.Value
        ),
        rotation=(
            float(
                parent.RotationAngle.Value
            )
            + relative_rotation
        ),
        name="CornerMate",
        cabinet_type=CABINET_BASE,
        geometry_mode=str(
            parent.GeometryMode
        ),
        panel_thickness=float(
            parent.PanelThickness.Value
        ),
        back_thickness=float(
            parent.BackThickness.Value
        ),
        shelf_count=int(
            parent.ShelfCount
        ),
        plinth_height=float(
            parent.PlinthHeight.Value
        ),
        plinth_setback=float(
            parent.PlinthSetback.Value
        ),
        front_type=FRONT_OPEN,
        front_thickness=float(
            parent.FrontThickness.Value
        ),
        front_gap=float(
            parent.FrontGap.Value
        ),
    )

    mate.Label = "Corner Mate"

    if "CornerParent" not in mate.PropertiesList:
        mate.addProperty(
            "App::PropertyLink",
            "CornerParent",
            "Blind Corner",
            "Parent Blind Corner Base cabinet.",
        )

    mate.CornerParent = parent
    parent.BlindMate = mate

    parent.Proxy._sync_blind_corner_mate(
        parent
    )

    document.recompute()

    return mate


def create_furniture(
    document,
    position,
    width=600.0,
    depth=560.0,
    height=720.0,
    rotation=0.0,
    name="Furniture",
    cabinet_type=CABINET_BASE,
    geometry_mode=GEOMETRY_CARCASS,
    panel_thickness=18.0,
    back_thickness=3.0,
    shelf_count=1,
    plinth_height=100.0,
    plinth_setback=50.0,
    mount_height=1400.0,
    width_b=900.0,
    depth_b=560.0,
    front_type=FRONT_OPEN,
    front_thickness=18.0,
    front_gap=2.0,
    drawer_count=3,
    drawer_zone_height=180.0,
    corner_opening_width=450.0,
    blind_box_width=600.0,
    blind_filler_width=100.0,
    blind_door_filler_width=50.0,
    blind_mate_width=600.0,
    blind_mate_depth=600.0,
    blind_side="Left",
):
    """Create one universal Cabinet object."""

    obj = document.addObject(
        "Part::FeaturePython",
        name,
    )

    obj.Label = "Cabinet"

    FurnitureProxy(
        obj,
        width=width,
        depth=depth,
        height=height,
        rotation=rotation,
        position=position,
        cabinet_type=cabinet_type,
        geometry_mode=geometry_mode,
        panel_thickness=panel_thickness,
        back_thickness=back_thickness,
        shelf_count=shelf_count,
        plinth_height=plinth_height,
        plinth_setback=plinth_setback,
        mount_height=mount_height,
        width_b=width_b,
        depth_b=depth_b,
        front_type=front_type,
        front_thickness=front_thickness,
        front_gap=front_gap,
        drawer_count=drawer_count,
        drawer_zone_height=drawer_zone_height,
        corner_opening_width=corner_opening_width,
        blind_box_width=blind_box_width,
        blind_filler_width=blind_filler_width,
        blind_door_filler_width=blind_door_filler_width,
        blind_mate_width=blind_mate_width,
        blind_mate_depth=blind_mate_depth,
        blind_side=blind_side,
    )

    FurnitureViewProvider(
        obj.ViewObject
    )

    document.recompute()

    try:
        obj.ViewObject.ShapeColor = (
            0.78,
            0.68,
            0.52,
        )

    except Exception:
        pass

    obj.ViewObject.Visibility = True

    if cabinet_type == CABINET_BLIND_CORNER_BASE:
        try:
            ensure_blind_corner_mate(
                obj
            )
        except Exception as error:
            App.Console.PrintError(
                "OpenInteriorCAD corner mate creation error: "
                f"{error}\n"
            )

    return obj

"""Universal parametric cabinet object for OpenInteriorCAD.

Cabinet Architecture 0.3:
- Base
- Wall
- Tall
- Corner Base
- Corner Wall

All variants remain OpenInteriorCAD::Furniture and preserve the common
Width / Depth / Height / Position / RotationAngle interface used by
Move, Snap, Duplicate and Cabinet Run tools.
"""

import FreeCAD as App
import Part


FURNITURE_TYPE = "OpenInteriorCAD::Furniture"

CABINET_BASE = "Base"
CABINET_WALL = "Wall"
CABINET_TALL = "Tall"
CABINET_CORNER_BASE = "Corner Base"
CABINET_CORNER_WALL = "Corner Wall"

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

        return [
            leaf_a,
            leaf_b,
        ]


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

        if str(
            obj.CabinetType
        ) in {
            CABINET_CORNER_BASE,
            CABINET_CORNER_WALL,
        }:
            return self._make_corner_front_geometry(
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
        shapes = []

        if front_type == FRONT_SINGLE:
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

        elif front_type == FRONT_DOUBLE:
            leaf_width = (
                available_width
                - gap
            ) / 2.0

            if leaf_width > 0.001:
                left = self._make_front_panel(
                    gap,
                    z_start + gap,
                    leaf_width,
                    available_height,
                    y_depth,
                    thickness,
                )

                right = self._make_front_panel(
                    gap
                    + leaf_width
                    + gap,
                    z_start + gap,
                    leaf_width,
                    available_height,
                    y_depth,
                    thickness,
                )

                if left is not None:
                    shapes.append(
                        left
                    )

                if right is not None:
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
                        y_depth,
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
                    y_depth,
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

        return self._make_standard_carcass(
            obj,
            use_plinth=True,
        )

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
            "DrawerCount",
            "DrawerZoneHeight",
            "CornerOpeningWidth",
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
            "DrawerCount",
            "DrawerZoneHeight",
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

    return obj

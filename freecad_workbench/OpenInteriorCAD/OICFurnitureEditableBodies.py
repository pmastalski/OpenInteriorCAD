"""Convert cabinet solids to independent Part Design Bodies.

Convert the source cabinet into independent native Part Design Bodies.
Rectangular boards use FreeCAD native AdditiveBox primitives, and shaped
boards keep exact static starting solids. No custom parametric proxies or
Body-to-child expressions are created.
"""

import json
import math

import FreeCAD as App
import FreeCADGui as Gui
import Part
from PySide import QtWidgets


FURNITURE_TYPE = "OpenInteriorCAD::Furniture"


def _cabinet_solids(cabinet):
    """Return independent solids, preserving their displayed world position."""

    shape = cabinet.Shape
    if shape.isNull():
        raise ValueError("The selected cabinet has no geometry. Recompute first.")

    # Copy each TopoShape.  Never mutate the generating cabinet's Shape.
    solids = [solid.copy() for solid in shape.Solids if not solid.isNull()]
    if not solids:
        raise ValueError("The selected cabinet contains no solid geometry.")

    for solid in solids:
        if not solid.isValid():
            raise ValueError("The cabinet contains an invalid solid. Recompute first.")

    return solids



def _mm(value):
    return float(getattr(value, "Value", value))


def _production_part_instances(cabinet):
    """Expand the BOM, correcting differences between BOM and real geometry.

    Earlier naming matched BOM dimensions literally. That cannot work for
    many boards: e.g. standard sides are modeled at full body height while
    their BOM length is clear height; standard bottom/top are modeled at
    Depth-BackThickness while their BOM width is Depth; standard plinth is
    modeled across full Width but BOM previously reported Width-2*Panel.
    This function does NOT change BOM or cabinet geometry.
    """
    try:
        parts = json.loads(str(getattr(cabinet, "BoardPartsJSON", "[]")))
    except (ValueError, TypeError):
        return []
    if not isinstance(parts, list):
        return []

    kind = str(getattr(cabinet, "CabinetType", ""))
    standard = kind in ("Base", "Wall", "Tall")
    blind = kind == "Blind Corner Base"
    mode = str(getattr(cabinet, "GeometryMode", ""))
    box_mode = mode.lower().strip() in ("box", "simple box")
    result = []
    for part in parts:
        if not isinstance(part, dict):
            continue
        name = str(part.get("name", "")).strip()
        if not name:
            continue
        try:
            dimensions = [float(part[k]) for k in ("length", "width", "thickness")]
            quantity = int(part.get("quantity", 1))
        except (KeyError, ValueError, TypeError):
            continue
        if min(dimensions) <= 0 or quantity <= 0:
            continue
        if (standard or blind) and not box_mode:
            depth = _mm(cabinet.Depth)
            panel = _mm(cabinet.PanelThickness)
            back = _mm(cabinet.BackThickness)
            if blind:
                depth -= _mm(cabinet.BlindFillerWidth)
            if name in ("Left Side", "Right Side"):
                # The two generated sides are full-height, not clear-height.
                dimensions[0] += 2.0 * panel if standard else 0.0
            elif name in ("Bottom", "Top") and standard:
                # Generator starts these boards behind the back panel.
                dimensions[1] = depth - back
            elif name == "Plinth" and standard:
                # Generated plinth runs through the complete cabinet width.
                dimensions[0] = _mm(cabinet.Width)
            # Blind carcass dimensions are already described correctly by BOM.
        if min(dimensions) <= 0:
            continue
        dimensions.sort()
        for _ in range(min(quantity, 500)):
            result.append({
                "name": name,
                "dims": dimensions,
                "volume": math.prod(dimensions),
                "material": str(part.get("material", "") or ""),
            })
    return result


def _solid_box_dimensions(solid):
    """Exact oriented dimensions of a rectangular solid, independent of rotation.

    The earlier edge-length implementation often rejected boxes with equal
    sides and any translated/rotated box. Four edges per direction are expected
    for a six-face rectangular prism. Non-box machining is not mislabeled.
    """
    try:
        if len(solid.Faces) != 6 or len(solid.Edges) != 12:
            return None
        axes = []
        for edge in solid.Edges:
            if len(edge.Vertexes) != 2:
                return None
            vector = edge.Vertexes[1].Point.sub(edge.Vertexes[0].Point)
            length = float(vector.Length)
            if length <= 0.000001:
                return None
            vector.normalize()
            for item in axes:
                if abs(vector.dot(item[0])) >= 0.99999:
                    if abs(item[1] - length) > 0.05:
                        return None
                    item[2] += 1
                    break
            else:
                axes.append([vector, length, 1])
        if len(axes) != 3 or any(item[2] != 4 for item in axes):
            return None
        if any(abs(axes[i][0].dot(axes[j][0])) > 0.0001
               for i in range(3) for j in range(i+1, 3)):
            return None
        lengths = sorted(item[1] for item in axes)
        if abs(math.prod(lengths)-float(solid.Volume)) > max(0.5, float(solid.Volume)*0.0001):
            return None
        return lengths
    except (AttributeError, ValueError, TypeError):
        return None


def _local_centers(cabinet, solids):
    """Centers in cabinet's own axes; stable if user rotates furniture."""
    angle = math.radians(_mm(getattr(cabinet, "RotationAngle", 0)))
    cx, cy = math.cos(angle), math.sin(angle)
    position = cabinet.Position
    result = []
    for solid in solids:
        point = solid.CenterOfMass
        dx, dy = point.x-position.x, point.y-position.y
        result.append((dx*cx+dy*cy, -dx*cy+dy*cx, point.z-position.z))
    return result


def _match_parts(cabinet, solids):
    """One-to-one mapping, including physical dimensions and material.

    Match only credible shapes. Ambiguous side and top/bottom pairs are
    assigned using their positions in cabinet coordinates. Unmatched solids
    keep an honest Element label instead of a fabricated part assignment.
    """
    instances = _production_part_instances(cabinet)
    sizes = [_solid_box_dimensions(solid) for solid in solids]
    centers = _local_centers(cabinet, solids)
    matches = {}
    used = set()
    # Most specific physical board dimensions first.
    options = {}
    for i, (solid, dims) in enumerate(zip(solids, sizes)):
        if dims is None:
            options[i] = []
            continue
        options[i] = [j for j, part in enumerate(instances)
                      if all(abs(a-b) <= 0.2 for a,b in zip(dims, part["dims"]))
                      and abs(float(solid.Volume)-part["volume"])
                          <= max(1.,part["volume"]*.0001)]
    for i in sorted(range(len(solids)), key=lambda k: (len(options[k]) or 99999, k)):
        available = [j for j in options[i] if j not in used]
        if not available:
            continue
        # Reconcile named left/right and top/bottom using physical position.
        def priority(j):
            name = instances[j]["name"]
            x,y,z = centers[i]
            if name == "Left Side":
                return (x, j)
            if name == "Right Side":
                return (-x, j)
            if name == "Bottom":
                return (z, j)
            if name == "Top":
                return (-z, j)
            return (0.,j)
        selected = min(available, key=priority)
        matches[i] = dict(instances[selected])
        used.add(selected)

    # Correct ambiguous mirrored pairs regardless of which BOM item was
    # encountered first, including when their dimensions are identical.
    for first, second, axis in (("Left Side","Right Side",0), ("Bottom","Top",2)):
        ids = [i for i, part in matches.items() if part["name"] in (first, second)]
        if len(ids) == 2:
            ids.sort(key=lambda k: centers[k][axis])
            matches[ids[0]]["name"] = first
            matches[ids[1]]["name"] = second

    result = []
    for i, (solid,dims) in enumerate(zip(solids,sizes)):
        part = matches.get(i)
        if part is None:
            part = {"name": "Element {:03d}".format(i+1), "material":""}
        else:
            part = dict(part)
        if dims is not None:
            part["length"],part["width"],part["thickness"] = reversed(dims)
            part["dimensions_method"] = "Exact rectangular solid"
        else:
            # A non-rectangular body is not assigned misleading dimensions.
            part["length"] = part["width"] = part["thickness"] = 0.0
            part["dimensions_method"] = "Non-rectangular: no exact L/W/T"
        result.append(part)
    return result


def _match_part_names(cabinet, solids):
    """Backwards-compatible helper for the 0.2 installation diagnostic."""
    return [part["name"] for part in _match_parts(cabinet,solids)]


def _box_frame(solid):
    """Find one real corner and its three incident edges in a true box.

    The natural frame is reconstructed from the exported solid rather than
    assuming the cabinet is aligned to global XYZ. Each edge starts at the
    same original vertex, so any subsequent dimension change is anchored.
    """
    dimensions = _solid_box_dimensions(solid)
    if dimensions is None:
        return None
    vertices = [v.Point for v in solid.Vertexes]
    if len(vertices) != 8:
        return None
    corner = min(vertices, key=lambda v: (v.x+v.y+v.z, v.x, v.y, v.z))
    sides = []
    for edge in solid.Edges:
        a, b = edge.Vertexes[0].Point, edge.Vertexes[1].Point
        if (a.sub(corner)).Length <= 0.00001:
            vector = b.sub(a)
        elif (b.sub(corner)).Length <= 0.00001:
            vector = a.sub(b)
        else:
            continue
        length = float(vector.Length)
        if length <= 0.00001:
            continue
        vector.normalize()
        sides.append((length, vector))
    if len(sides) != 3:
        return None
    # Length / Width / Thickness consistently correspond to descending
    # dimensions even for a rotated board (ties are stable by edge order).
    sides.sort(key=lambda entry: -entry[0])
    x, y, z = (entry[1] for entry in sides)
    # FreeCAD placements are proper rotations. A left-handed corner frame
    # must be converted without moving or mirroring the original solid.
    if x.cross(y).dot(z) < 0:
        z = -z
        corner = corner.sub(z * sides[2][0])
    return corner, x, y, z


def _create_editable_base(body, solid, part, label):
    """Native FreeCAD Part Design feature, never a scripted cyclic feature.

    Rectangular boards: AdditiveBox has its OWN editable Length/Width/Height.
    Others: exact PartDesign::Feature snapshot; sketch/Pocket still works.
    """
    frame = _box_frame(solid)
    if frame is None:
        base = body.newObject("PartDesign::Feature", "OICBoardBase")
        base.Label = label + " - Base"
        base.Shape = solid.copy()
        return base, False

    origin, x, y, z = frame
    base = body.newObject("PartDesign::AdditiveBox", "OICEditableBoard")
    base.Label = label + " - Editable Dimensions"
    base.Length = float(part["length"])
    base.Width = float(part["width"])
    base.Height = float(part["thickness"])
    base.Placement = App.Placement(origin, App.Rotation(x, y, z, "ZXY"))
    return base, True


def _add_board_properties(body, part, cabinet):
    """Metadata on Body; actual editable dimensions live on AdditiveBox.

    Never introduce expressions from an object inside the Body to its own
    parent: FreeCAD reports a cyclic reference for those relationships.
    """
    category = "OpenInteriorCAD - Board Info"
    for key, kind, description in (
        ("PartName", "App::PropertyString", "Board name."),
        ("Material", "App::PropertyString", "Board material."),
        ("DimensionsMethod", "App::PropertyString", "Measurement method."),
    ):
        body.addProperty(kind, key, category, description)
    body.PartName = part["name"]
    body.Material = part["material"]
    body.DimensionsMethod = part["dimensions_method"]
    body.setEditorMode("DimensionsMethod", 1)


def _unique_names(names):
    """Give duplicates readable suffixes: Shelf 01, Shelf 02, etc."""
    from collections import Counter
    totals = Counter(names)
    seen = Counter()
    result = []
    for name in names:
        seen[name] += 1
        if totals[name] > 1:
            result.append("{} {:02d}".format(name, seen[name]))
        else:
            result.append(name)
    return result

def convert_furniture_to_bodies(cabinet):
    """Replace source cabinet with separate native editable Part Design Bodies.

    The operation is one undoable transaction. The source furniture is removed
    only after successful creation, recompute and validation of every part.
    """
    if getattr(cabinet, "OICType", "") != FURNITURE_TYPE:
        raise ValueError("Select a single OpenInteriorCAD cabinet.")
    document = cabinet.Document
    if document is None:
        raise ValueError("The cabinet has no document.")

    document.recompute()
    solids = _cabinet_solids(cabinet)
    label = cabinet.Label
    part_details = _match_parts(cabinet, solids)
    part_names = _unique_names([part["name"] for part in part_details])
    document.openTransaction("Convert OIC cabinet to editable Bodies")
    try:
        group = document.addObject("App::DocumentObjectGroup", "OICEditableBodies")
        group.Label = "Editable - " + label
        group.addProperty("App::PropertyString", "ConversionInfo", "OpenInteriorCAD")
        group.ConversionInfo = (
            "Independent Part Design Bodies. Rectangular boards: select the "
            "Editable Dimensions feature inside a Body to edit Length, Width "
            "and Height (= board thickness). No live source cabinet."
        )
        try:
            color = cabinet.ViewObject.ShapeColor
        except Exception:
            color = None

        created = []
        for solid, part_name, part in zip(solids, part_names, part_details):
            board_label = "{} - {}".format(label, part_name)
            body = document.addObject("PartDesign::Body", "OICBoardBody")
            body.Label = board_label
            group.addObject(body)
            _add_board_properties(body, part, cabinet)
            base, editable = _create_editable_base(body, solid, part, board_label)
            body.Tip = base
            if color is not None:
                try:
                    base.ViewObject.ShapeColor = color
                    body.ViewObject.ShapeColor = color
                except Exception:
                    pass
            created.append((body, solid, editable))

        document.recompute()
        for body, original, editable in created:
            result = body.Shape
            if result.isNull() or len(result.Solids) != 1 or not result.isValid():
                raise RuntimeError("Failed to create Body: " + body.Label)
            if abs(float(result.Volume) - float(original.Volume)) > max(
                0.5, float(original.Volume) * 0.0001
            ):
                raise RuntimeError("Dimension mismatch in Body: " + body.Label)
            original_bb, result_bb = original.BoundBox, result.BoundBox
            for key in ("XMin", "YMin", "ZMin", "XMax", "YMax", "ZMax"):
                if abs(float(getattr(original_bb, key)) - float(getattr(result_bb, key))) > 0.1:
                    raise RuntimeError("Placement mismatch in Body: " + body.Label)

        # Remove the live furniture ONLY when conversion is complete.
        # Be cautious about a linked blind-corner companion cabinet: its
        # physical geometry stays, but any link to this source may clear.
        document.removeObject(cabinet.Name)
        document.recompute()
        document.commitTransaction()
        return group, len(created)
    except Exception:
        document.abortTransaction()
        raise


class ConvertFurnitureToBodiesCommand:
    """FreeCAD menu / toolbar command."""

    def GetResources(self):
        return {
            "MenuText": "Convert to Editable Bodies",
            "ToolTip": (
                "Create one independent Part Design Body per cabinet solid "
                "for Sketch / Pocket / Pad. Original cabinet is replaced."
            ),
        }

    def IsActive(self):
        return App.ActiveDocument is not None

    def Activated(self):
        selection = Gui.Selection.getSelection()
        if len(selection) != 1 or getattr(
            selection[0], "OICType", ""
        ) != FURNITURE_TYPE:
            QtWidgets.QMessageBox.warning(
                Gui.getMainWindow(),
                "Convert to Editable Bodies",
                "Select exactly one OpenInteriorCAD cabinet.",
            )
            return

        cabinet = selection[0]
        try:
            count = len(_cabinet_solids(cabinet))
        except Exception as error:
            QtWidgets.QMessageBox.warning(
                Gui.getMainWindow(), "Convert to Editable Bodies", str(error)
            )
            return

        message = (
            "Replace the cabinet with {} separate editable Part Design Bodies?\n\n"
            "The original OpenInteriorCAD parametric cabinet will be REMOVED "
            "after a successful conversion (FreeCAD Undo can restore it). "
            "Each rectangular board has a native 'Editable Dimensions' "
            "feature: edit its Length, Width, Height (= thickness) in Data. "
            "You can then use Sketch/Pocket/Pad.\n\n"
            "Non-rectangular boards preserve their original shape as static "
            "Part Design bases. Cut List will not include later edits.\n\n"
            "For a linked blind-corner set, convert each cabinet separately."
        ).format(count)

        answer = QtWidgets.QMessageBox.question(
            Gui.getMainWindow(),
            "Convert to Editable Bodies",
            message,
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No,
        )
        if answer != QtWidgets.QMessageBox.Yes:
            return

        try:
            group, created = convert_furniture_to_bodies(cabinet)
        except Exception as error:
            App.Console.PrintError(
                "OpenInteriorCAD editable bodies error: {}\n".format(error)
            )
            QtWidgets.QMessageBox.critical(
                Gui.getMainWindow(),
                "Convert to Editable Bodies",
                "Conversion failed: {}".format(error),
            )
            return

        Gui.Selection.clearSelection()
        Gui.Selection.addSelection(group)
        QtWidgets.QMessageBox.information(
            Gui.getMainWindow(),
            "Convert to Editable Bodies",
            "Created {} Part Design Bodies in '{}'.\n\n"
            "Expand the group and select a Body: Data > OpenInteriorCAD - "
            "Board Dimensions allows editing Length / Width / Thickness. "
            "Activate the Body and sketch on its face for Pocket."
            .format(created, group.Label),
        )


Gui.addCommand(
    "OIC_ConvertFurnitureToBodies", ConvertFurnitureToBodiesCommand()
)

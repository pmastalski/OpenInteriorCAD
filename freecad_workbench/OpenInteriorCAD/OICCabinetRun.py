"""Cabinet Run helpers for OpenInteriorCAD."""

import math
import FreeCAD as App

CABINET_TYPE = "OpenInteriorCAD::Furniture"
RUN_TYPE = "OpenInteriorCAD::CabinetRun"


def get_run_cabinets(run):
    if run is None or getattr(run, "OICType", "") != RUN_TYPE:
        return []
    return [
        obj for obj in run.Group
        if getattr(obj, "OICType", "") == CABINET_TYPE
    ]


def update_run_properties(run):
    cabinets = get_run_cabinets(run)
    gap = run.CabinetGap.Value if "CabinetGap" in run.PropertiesList else 0.0
    total = sum(c.Width.Value for c in cabinets)
    if len(cabinets) > 1:
        total += gap * (len(cabinets) - 1)

    if "CabinetCount" in run.PropertiesList:
        run.CabinetCount = len(cabinets)
    if "TotalWidth" in run.PropertiesList:
        run.TotalWidth = total


def ensure_run_properties(run):
    if "OICType" not in run.PropertiesList:
        run.addProperty(
            "App::PropertyString", "OICType",
            "OpenInteriorCAD", "Semantic object type."
        )
    run.OICType = RUN_TYPE

    if "CabinetCount" not in run.PropertiesList:
        run.addProperty(
            "App::PropertyInteger", "CabinetCount",
            "Cabinet Run", "Number of cabinets in this run."
        )
    if "CabinetGap" not in run.PropertiesList:
        run.addProperty(
            "App::PropertyLength", "CabinetGap",
            "Cabinet Run", "Gap between adjacent cabinets."
        )
        run.CabinetGap = 0.0
    if "TotalWidth" not in run.PropertiesList:
        run.addProperty(
            "App::PropertyLength", "TotalWidth",
            "Cabinet Run", "Calculated total width of the run."
        )

    run.setEditorMode("CabinetCount", 1)
    run.setEditorMode("TotalWidth", 1)
    update_run_properties(run)


def create_cabinet_run(document, cabinets, name="CabinetRun"):
    cabinets = [
        obj for obj in cabinets
        if getattr(obj, "OICType", "") == CABINET_TYPE
    ]
    if len(cabinets) < 2:
        raise ValueError("Select at least two cabinets.")

    run = document.addObject("App::DocumentObjectGroupPython", name)
    run.Label = "Cabinet Run"

    for cabinet in cabinets:
        run.addObject(cabinet)

    ensure_run_properties(run)
    document.recompute()
    return run


def local_axes(rotation):
    angle = math.radians(rotation)
    return (
        App.Vector(math.cos(angle), math.sin(angle), 0.0),
        App.Vector(-math.sin(angle), math.cos(angle), 0.0),
    )


def arrange_cabinets(run, direction="right", gap=None):
    ensure_run_properties(run)
    cabinets = get_run_cabinets(run)
    if len(cabinets) < 2:
        return

    if gap is None:
        gap = run.CabinetGap.Value
    else:
        run.CabinetGap = gap

    anchor = cabinets[0]
    rotation = anchor.RotationAngle.Value
    local_x, _ = local_axes(rotation)

    if direction == "right":
        cursor = App.Vector(
            anchor.Position.x + local_x.x * (anchor.Width.Value + gap),
            anchor.Position.y + local_x.y * (anchor.Width.Value + gap),
            anchor.Position.z,
        )
        for cabinet in cabinets[1:]:
            cabinet.RotationAngle = rotation
            cabinet.Position = App.Vector(cursor.x, cursor.y, cabinet.Position.z)
            advance = cabinet.Width.Value + gap
            cursor = App.Vector(
                cursor.x + local_x.x * advance,
                cursor.y + local_x.y * advance,
                cursor.z,
            )
    else:
        cursor = App.Vector(anchor.Position.x, anchor.Position.y, anchor.Position.z)
        for cabinet in cabinets[1:]:
            cabinet.RotationAngle = rotation
            advance = cabinet.Width.Value + gap
            cursor = App.Vector(
                cursor.x - local_x.x * advance,
                cursor.y - local_x.y * advance,
                cursor.z,
            )
            cabinet.Position = App.Vector(cursor.x, cursor.y, cabinet.Position.z)

    update_run_properties(run)
    run.Document.recompute()


def align_fronts(run):
    ensure_run_properties(run)
    cabinets = get_run_cabinets(run)
    if len(cabinets) < 2:
        return

    anchor = cabinets[0]
    rotation = anchor.RotationAngle.Value
    local_x, local_y = local_axes(rotation)

    anchor_front_y = (
        anchor.Position.x * local_y.x
        + anchor.Position.y * local_y.y
        + anchor.Depth.Value
    )

    for cabinet in cabinets[1:]:
        cabinet.RotationAngle = rotation
        current_x = (
            cabinet.Position.x * local_x.x
            + cabinet.Position.y * local_x.y
        )
        target_back_y = anchor_front_y - cabinet.Depth.Value
        cabinet.Position = App.Vector(
            local_x.x * current_x + local_y.x * target_back_y,
            local_x.y * current_x + local_y.y * target_back_y,
            cabinet.Position.z,
        )

    run.Document.recompute()


def move_cabinet_run(run, delta):
    for cabinet in get_run_cabinets(run):
        cabinet.Position = App.Vector(
            cabinet.Position.x + delta.x,
            cabinet.Position.y + delta.y,
            cabinet.Position.z + delta.z,
        )
    update_run_properties(run)
    run.Document.recompute()


def dissolve_cabinet_run(run):
    document = run.Document
    for cabinet in list(get_run_cabinets(run)):
        try:
            run.removeObject(cabinet)
        except Exception:
            pass
    document.removeObject(run.Name)
    document.recompute()

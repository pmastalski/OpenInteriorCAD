"""Cabinet Run object for OpenInteriorCAD."""

import FreeCAD as App


CABINET_TYPE = "OpenInteriorCAD::Furniture"
RUN_TYPE = "OpenInteriorCAD::CabinetRun"


def get_selected_cabinets():
    """Return selected OpenInteriorCAD cabinets."""
    import FreeCADGui as Gui

    return [
        obj
        for obj in Gui.Selection.getSelection()
        if getattr(obj, "OICType", "") == CABINET_TYPE
    ]


def create_cabinet_run(document, cabinets, name="CabinetRun"):
    """Create a logical group containing existing cabinets."""

    if document is None:
        raise ValueError("No active document.")

    cabinets = [
        obj
        for obj in cabinets
        if getattr(obj, "OICType", "") == CABINET_TYPE
    ]

    if len(cabinets) < 2:
        raise ValueError(
            "Select at least two cabinets."
        )

    run = document.addObject(
        "App::DocumentObjectGroupPython",
        name,
    )

    run.Label = "Cabinet Run"

    if "OICType" not in run.PropertiesList:
        run.addProperty(
            "App::PropertyString",
            "OICType",
            "OpenInteriorCAD",
            "Semantic object type.",
        )

    run.OICType = RUN_TYPE

    if "CabinetCount" not in run.PropertiesList:
        run.addProperty(
            "App::PropertyInteger",
            "CabinetCount",
            "OpenInteriorCAD",
            "Number of cabinets in this run.",
        )

    run.setEditorMode(
        "CabinetCount",
        1,
    )

    for cabinet in cabinets:
        run.addObject(cabinet)

    run.CabinetCount = len(cabinets)

    document.recompute()

    return run


def get_run_cabinets(run):
    """Return cabinet objects stored in a Cabinet Run."""

    if run is None:
        return []

    if getattr(
        run,
        "OICType",
        "",
    ) != RUN_TYPE:
        return []

    return [
        obj
        for obj in run.Group
        if getattr(
            obj,
            "OICType",
            "",
        )
        == CABINET_TYPE
    ]


def run_reference_position(run):
    """Return a stable reference point for the run."""

    cabinets = get_run_cabinets(
        run
    )

    if not cabinets:
        return App.Vector()

    first = cabinets[0]

    return App.Vector(
        first.Position.x,
        first.Position.y,
        first.Position.z,
    )


def move_cabinet_run(
    run,
    delta,
):
    """Translate all cabinets in the run by the same vector."""

    cabinets = get_run_cabinets(
        run
    )

    if not cabinets:
        return

    for cabinet in cabinets:
        cabinet.Position = App.Vector(
            cabinet.Position.x
            + delta.x,
            cabinet.Position.y
            + delta.y,
            cabinet.Position.z
            + delta.z,
        )

    run.CabinetCount = len(cabinets)

    run.Document.recompute()


def dissolve_cabinet_run(
    run,
):
    """
    Remove only the run group.
    Cabinets remain in the document.
    """

    if run is None:
        return

    document = run.Document

    if document is None:
        return

    cabinets = list(
        get_run_cabinets(
            run
        )
    )

    for cabinet in cabinets:
        try:
            run.removeObject(
                cabinet
            )
        except Exception:
            pass

    document.removeObject(
        run.Name
    )

    document.recompute()

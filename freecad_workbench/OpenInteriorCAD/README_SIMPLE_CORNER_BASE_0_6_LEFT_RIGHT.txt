OpenInteriorCAD - Simple Corner Base 0.6 - Left / Right opening

NEW
- Simple Corner Base has an Opening Side selector: Right (previous behaviour) / Left.
- Right: fixed section on left, opening door on right, fillers at left edge and divider.
- Left:  fixed section on right, opening door on left, fillers mirrored to right edge and divider.
- Door hinges on the outside edge and opens toward the room in both configurations.
- Fixed section width, front gap, two filler projections and outer carcass size do not change.
- Internal partition and accessible-bay shelves mirror with the fronts.
- Board Parts / Cut List use side-aware labels and retain correct cut dimensions.
- Duplicate Furniture retains chosen side.

COMPATIBILITY
- Separate SimpleCornerOpeningSide property (default Right) is independent of
  BlindSide used by the older Blind Corner Base / Corner Mate assembly.
- Existing Simple Corner Base furniture from 0.5 opens Right after updating,
  matching its previous appearance.
- There is no auto-created 90-degree cabinet for Simple Corner Base.

INSTALL WINDOWS
- Shut down FreeCAD completely.
- Copy the FOUR Python files in this archive to:
  %APPDATA%\FreeCAD\v1-1\Mod\OpenInteriorCAD\
- Restart FreeCAD and re-edit the cabinet.

Validation: Python syntax + stand-in tests for mirrored front panels, fillers,
partition, shelf, hinge direction and production names. Must still be visually
verified in FreeCAD 1.1 on Windows.

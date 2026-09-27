OpenInteriorCAD — Simple Corner Base 0.1

Based on the user-supplied current working GitHub branch ZIP (2026-09-20).

NEW CABINET TYPE
  Simple Corner Base

HOW TO CREATE
  Add Cabinet -> select cabinet -> Edit Furniture -> Cabinet Type:
  Simple Corner Base
  Set Width A / Depth A / Width B / Depth B under Corner geometry.
  Front Type is fixed to Single Door for this model.

GEOMETRY
  Reuses stable single-object L-shaped corner carcass (no extra Corner Mate).
  Run A: stationary rectangular left front.
  Run B: independent rectangular right door.
  FrontOpening angle rotates the right door only.
  No folding doors, no auto-generated adjacent cabinet.
  Default corner geometry has an L-shaped bottom/top and L shelves.

PRODUCTION
  Board Parts / Cut List use existing L-shaped corner carcass parts, plus
  distinct Fixed Left Front and Opening Right Front at the same dimensions
  as the front solids at 0 degrees.

LIMITATIONS
  0.1 exposes the proven L geometry (Width A / Depth A / Width B / Depth B)
  instead of introducing a second overlapping blind-corner cabinet.
  No independent Left/Right mirroring yet; door is on run B.
  Back panels follow current accepted L corner carcass generator and are not
  affected by the later overlay-back adjustment for standard cabinets.
  The right-door hinge direction requires visual verification in FreeCAD.
  Existing Corner Base / Corner Wall / Blind Corner Base stay untouched.

INSTALL WINDOWS CMD (after extracting this ZIP):
  copy /Y "<EXTRACT>\OICFurniture.py" "%APPDATA%\FreeCAD\v1-1\Mod\OpenInteriorCAD\"
  copy /Y "<EXTRACT>\OICFurnitureEditPanel.py" "%APPDATA%\FreeCAD\v1-1\Mod\OpenInteriorCAD\"
  copy /Y "<EXTRACT>\OICBoardParts.py" "%APPDATA%\FreeCAD\v1-1\Mod\OpenInteriorCAD\"
  Restart FreeCAD.

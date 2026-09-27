OpenInteriorCAD 0.7 - Live Furniture Edit 0.2

PURPOSE
Edit many cabinets without repeatedly closing and reopening Edit Furniture.

BEHAVIOR
- All parameter changes are applied immediately, as before.
- The Close button is no longer an Apply/OK step; it only closes the editor.
- While Edit Furniture is open, click another OpenInteriorCAD cabinet:
    * in the 3D view, or
    * in the Model tree
  and the same panel immediately loads that cabinet.
- No Close -> select -> Edit cycle is required.
- The panel title and information label show the currently edited cabinet.
- Clearing selection does not close the editor and does not lose the current
  cabinet.
- Non-furniture objects are ignored.

NAVIGATION
Two optional buttons were added:
- Previous Cabinet
- Next Cabinet

They cycle through OpenInteriorCAD::Furniture objects in the active document
and synchronize FreeCAD selection with the shown cabinet.

DATA SAFETY
The existing editor already writes parameters live in _values_changed().
Switching cabinet does not discard values; it only changes which Furniture
object the controls are bound to.

SELECTION OBSERVER
The panel registers a FreeCAD Selection observer while open and removes it
when the editor is closed/accepted/rejected, preventing stale observers after
the task panel is gone.

BASE
This package is based on:
OpenInteriorCAD 0.7 - Base Reinforcements 0.1.

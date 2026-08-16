OpenInteriorCAD — Materials 0.1

NEW COMMAND:
Material Library

The library is persistent across FreeCAD sessions and documents.

Material types:
- Board
- Front
- Back
- Edge

Each material stores:
- Type
- Manufacturer
- Code
- Name
- Thickness

Library functions:
- Add
- Delete
- Save Library
- Reset Defaults

Selected Cabinet section:
- Carcass material
- Front material
- Back material
- Edge-band material
- Edge-band thickness
- Apply to Cabinet

Cut List automatically uses the assigned material names because it already
reads:
- BoardMaterial
- FrontMaterial
- BackMaterial
- EdgeMaterial
- EdgeThickness

IMPORTANT DESIGN DECISION:
Materials 0.1 does NOT automatically change cabinet geometry thickness.
For example, selecting an 18 mm board does not overwrite PanelThickness.
This avoids unexpected geometry changes in existing stable cabinets.

A later Materials 0.2 can add an explicit:
"Apply material thickness to geometry"
option with validation.

Persistent storage:
FreeCAD user parameters:
BaseApp/Preferences/Mod/OpenInteriorCAD/Materials

No cabinet Shape code was changed.

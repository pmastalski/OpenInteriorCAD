OpenInteriorCAD — Simple Corner Base 0.4 — Two 90-degree fillers

Keeps the ONE rectangular cabinet and the opening right door.
Adds a second perpendicular filler at the LEFT starting edge of the cabinet.
Both fillers extend from front plane Y=Depth backwards to Y=Depth-FillerDepth.
Positions (local coordinates):
- Starting filler: X=0 .. FrontThickness
- Corner filler: X=FixedLeftWidth-FrontThickness .. FixedLeftWidth

Both use the existing shared "Both 90° Fillers Depth" setting and
front material, thickness, and height. No new property or data migration.

Board Parts / Cut List now contain TWO individually named filler panels.
All other cabinet generators remain unchanged.

Install the three complete .py files into the active FreeCAD Mod folder,
then restart FreeCAD. Existing converted Part Design Bodies do not update.

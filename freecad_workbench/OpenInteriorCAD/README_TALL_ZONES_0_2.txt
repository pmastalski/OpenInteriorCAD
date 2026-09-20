OpenInteriorCAD — Tall Zones 0.2 / front overlaps / extended sides / placement height

Files: OICFurniture.py OICBoardParts.py OICTallZones.py OICFurnitureEditPanel.py OICFurnitureCommands.py OICFurniturePanel.py

Tall Zones: Auto Height assigns 0 mm to highlighted row and resolves remaining space.
Vertical zone fronts cover bottom/top carcass boards, and share intermediate dividers halfway with Front Gap. Lift-up front uses same panel size as Single Door.
Wall: Front Drop Below Cabinet lengthens ordinary wall fronts downward; matching production sizes.
Base/Tall: Floor-reaching Sides (None/Left/Right/Both); plinth fits between floor-reaching sides, avoiding solid collisions; Board Parts reflects lengths.
Insert: Placement Height (Z), default 0 mm. For nonzero height, picking an existing cabinet snaps against its left or right side based on clicked half, at specified Z; reference cabinet orientation is inherited. Without a hit the reference selected when pressing Pick Position is used; without reference, picks the exact clicked XY at specified Z. FreeCAD vertical world axis is Z, not Y.

Full FreeCAD runtime testing required. Syntax checked only.

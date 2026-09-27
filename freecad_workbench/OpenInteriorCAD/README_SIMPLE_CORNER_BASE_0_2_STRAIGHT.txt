OpenInteriorCAD Simple Corner Base 0.2 — rectangular, NOT L-shaped.

The original 0.1 construction was incorrect. This version makes a single
straight rectangular cabinet with an externally applied MDF back, fixed
left front, flat filler and opening right door, all in one front plane.
No perpendicular cabinet / Corner Mate is created.

Editable inputs under Straight Corner:
  Fixed Left Width = BlindBoxWidth (existing property)
  Flat Filler Width = BlindFillerWidth (existing property)
  Overall Width, Depth, Height, Front Gap, Front Open Angle, etc.

Its interior has a partition and shelves in the right accessible bay.
Board Parts has a rectangular cut list (not the previous L-shaped pieces).
The previously accepted L corner / Blind Corner generators are unchanged.

Only OICFurniture.py, OICFurnitureEditPanel.py and OICBoardParts.py
need replacing. Fully restart FreeCAD and re-create the Simple Corner Base.

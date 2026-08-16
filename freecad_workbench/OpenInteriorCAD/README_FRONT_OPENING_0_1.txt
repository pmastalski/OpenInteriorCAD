OpenInteriorCAD — Front Opening 0.1

NEW COMMAND:
Front Opening

SUPPORTED:
- Single Door
- Double Door

CONTROLS:
- slider 0°–120°
- numeric opening angle
- quick buttons:
  Closed
  45°
  90°
  110°

SINGLE DOOR:
- Left hinge
- Right hinge

DOUBLE DOOR:
- left leaf opens around its outer left edge
- right leaf opens around its outer right edge
- both open outward toward cabinet local +Y

NEW FURNITURE PROPERTIES:
- FrontOpenAngle
- SingleDoorHingeSide

IMPORTANT:
- default FrontOpenAngle is 0° = existing closed geometry
- carcass geometry is unchanged
- Board Parts / Cut List dimensions remain closed production dimensions
- material, edge, hardware and costing metadata are unchanged
- accepted Corner Folding Doors geometry is NOT modified
- corner opening is intentionally reserved for a later dedicated version
- drawers and lift-up are intentionally not animated yet

This version changes only the placement/orientation of standard front solids
inside the existing Furniture Shape.

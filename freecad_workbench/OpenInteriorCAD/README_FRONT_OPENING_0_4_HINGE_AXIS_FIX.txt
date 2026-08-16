OpenInteriorCAD — Front Opening 0.4 / Hinge Axis Fix

PROBLEM FIXED:
The door rotation axis in 0.3 was located on the outside edge/rear face of
the front. During opening, the front thickness could sweep beyond the
cabinet side.

NEW HINGE AXIS:
X:
- Left door  -> inner face of the left carcass side panel
- Right door -> inner face of the right carcass side panel

Y:
- outside/front face of the door
  (Depth + FrontThickness)

This approximates the motion of a concealed furniture hinge and keeps the
normal outward 0–90 degree opening aligned with the cabinet clear opening.

SUPPORTED:
- Single Door, Left hinge
- Single Door, Right hinge
- Double Door

UNCHANGED:
- closed front geometry
- carcass geometry
- production dimensions
- corner cabinet geometry
- materials
- edge assignments
- Cut List
- Hardware
- Costing

NOTE:
At opening angles greater than 90 degrees a real door naturally sweeps
around the cabinet side. Front Opening still allows up to 120 degrees for
hinge visualization.

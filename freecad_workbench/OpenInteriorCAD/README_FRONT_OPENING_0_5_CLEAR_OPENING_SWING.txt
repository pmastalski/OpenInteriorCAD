OpenInteriorCAD — Front Opening 0.5 / Clear Opening Swing

PROBLEM FIXED
Version 0.4 improved the hinge axis but the opened leaf could still move
into the cabinet clear opening because the front itself was still created
in the closed overlay-front position before rotation.

NEW BEHAVIOR
At FrontOpenAngle = 0 degrees:
- original closed overlay-front geometry is preserved exactly

At FrontOpenAngle > 0 degrees:
- the leaf is rebuilt from the cabinet clear-opening hinge line
- hinge Y is on the cabinet front plane
- the leaf then rotates outward

SINGLE DOOR
- Left hinge -> opens outward from left clear-opening edge
- Right hinge -> opens outward from right clear-opening edge

DOUBLE DOOR
- left leaf opens from the left clear-opening edge
- right leaf opens from the right clear-opening edge
- both swing outward

UNCHANGED
- carcass geometry
- production dimensions
- Board Parts / Cut List
- Edge Assignment
- Material Library
- Hardware
- Costing
- accepted corner cabinet geometry
- Corner Folding Doors geometry

This version changes only standard Single Door / Double Door opening preview.

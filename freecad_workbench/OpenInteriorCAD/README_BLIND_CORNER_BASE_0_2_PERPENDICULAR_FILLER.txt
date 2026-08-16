OpenInteriorCAD — Blind Corner Base 0.2 / Perpendicular Spacer Filler

CHANGE REQUEST IMPLEMENTED

The Blind Corner Base spacer filler (blenda dystansowa) is now:

- positioned at 90 degrees to the cabinet front
- a vertical Y-Z panel instead of a panel lying in the front plane
- extended from the cabinet front toward the neighbouring cabinet
- user-controlled with:
      Spacer Filler Width
- extended all the way down to floor level (Z = 0)
- extended to the full cabinet height

GEOMETRY

Cabinet front:
- lies at local Y = Depth

Spacer filler:
- thickness = FrontThickness
- length from cabinet = BlindFillerWidth
- height = full cabinet Height
- starts at floor level
- sits on the boundary between the hidden closed box and usable compartment

LEFT / RIGHT

Hidden Side = Left:
- spacer is placed at the right boundary of the hidden left box

Hidden Side = Right:
- spacer is mirrored to the left boundary of the hidden right box

PRODUCTION

Board Parts / Cut List now treat Spacer Filler as:
- Length = full cabinet Height
- Width = Spacer Filler Width
- Thickness = FrontThickness

The exposed long edge is marked for edge banding.

UNCHANGED

- hidden closed box
- internal partition
- accessible shelves
- usable cabinet fronts
- overall rectangular footprint
- existing L-shaped Corner Base / Corner Wall
- Cut Layout / PDF / SVG infrastructure

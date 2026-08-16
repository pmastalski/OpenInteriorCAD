OpenInteriorCAD — Blind Corner Set 0.4 / Automatic 90° Cabinet

NEW CONCEPT:
Blind Corner Base is now treated as a CORNER SET rather than a single
isolated cabinet.

When Blind Corner Base is created / selected by changing cabinet type,
OpenInteriorCAD automatically creates a second normal Base cabinet positioned
at 90 degrees to it.

WHY:
The corner spacer, toe-kick return and door-clearance filler only make full
geometric sense relative to the neighbouring perpendicular cabinet.

LINKED CABINET:
The second object is a real OpenInteriorCAD Furniture object:
    Label: Corner Mate
    CabinetType: Base

Therefore it can later have its own:
- fronts
- shelves
- materials
- hardware
- Board Parts
- Cut List / Cut Layout entries

PARENT CONTROLS:
Blind Corner panel now includes:
- Hidden Side
- Blind Box Width
- Corner Spacer Width
- Door Clearance Filler
- 90° Cabinet Width
- 90° Cabinet Depth
- Create / Reconnect 90° Cabinet

DEFAULT MATE:
600 x 600 mm

AUTOMATIC LINKING:
The Corner Mate follows the Blind Corner parent when you change:
- parent Position
- parent Rotation
- Hidden Side
- Corner Spacer Width
- 90° Cabinet Width
- 90° Cabinet Depth
- cabinet Height
- Panel Thickness
- Back Thickness
- Plinth Height
- Plinth Setback

MIRRORING:
Hidden Side = Left and Hidden Side = Right now mirror the complete corner:
- perpendicular spacer direction
- perpendicular plinth return
- 90° companion cabinet placement

CORNER SPACER:
The perpendicular spacer ends exactly where the linked cabinet front begins.

PRODUCTION:
Because Corner Mate is a separate Furniture object, it is naturally included
in Cut List and Cut Layout when the project/all cabinets are processed.

The existing L-shaped Corner Base and Corner Wall remain unchanged.

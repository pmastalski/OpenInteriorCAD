OpenInteriorCAD — Blind Corner Set 0.7 / Spacer Gap

CHANGE BASED ON THE NEW STEP EXPORT

Current STEP geometry showed:
- the long Blind Corner cabinet ended at the same front Y line as the 90° mate
- the perpendicular Corner Spacer was behind that line
- therefore the spacer was not the actual physical distance between cabinets

NEW RULE

Corner Spacer Width is now the ACTUAL gap between:
1. the long Blind Corner cabinet body/front
2. the linked cabinet at 90 degrees

Formula:
    Blind body depth = Corner Depth - Corner Spacer Width

Example:
    Corner Depth = 600 mm
    Corner Spacer Width = 100 mm

Result:
    long cabinet body/front depth = 500 mm
    spacer occupies 500..600 mm
    linked 90° cabinet starts at 600 mm

Thus:
    gap between cabinets = exactly 100 mm

GEOMETRY CHANGES
- long cabinet side panels are shortened by Corner Spacer Width
- bottom/top/shelves are shortened to the same effective depth
- hidden front closure moves back with the long cabinet front
- usable doors/drawers move back with the long cabinet front
- Door Clearance Filler moves to the new long-cabinet front plane
- door opening hinge plane moves with the front
- perpendicular Corner Spacer bridges exactly from long cabinet to 90° mate
- linked 90° cabinet remains on the original Corner Depth reference

PRODUCTION
Board Parts now use the shortened effective body depth:
    body_depth = Depth - BlindFillerWidth

This affects:
- Left Side
- Right Side
- Bottom
- Top
- Partition
- Shelves
- other depth-dependent blind-corner carcass parts

The perpendicular spacer remains a separate production part.

UI
Depth label for Blind Corner Base is now:
    Corner Depth

This makes clear that the property defines the full corner reference depth,
not the shortened long-cabinet body depth.

Existing standard and L-shaped corner cabinet geometry remains unchanged.

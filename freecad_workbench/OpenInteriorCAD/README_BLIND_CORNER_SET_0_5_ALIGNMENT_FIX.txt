OpenInteriorCAD — Blind Corner Set 0.5 / Alignment Fix

Based on visual test of version 0.4.

1. BOTH FILLERS MOVED TOWARD THE WALL

Corner Spacer:
- v0.4 line: Depth - PlinthSetback
- v0.5 line: Depth - 2 * PlinthSetback

With the usual PlinthSetback = 50 mm:
- Corner Spacer moves exactly another 50 mm toward the wall.

Door Clearance Filler:
- moved from Depth to Depth - PlinthSetback
- with 50 mm setback it also moves exactly 50 mm toward the wall.

2. LINKED 90-DEGREE CABINET MOVES WITH THE CORNER SPACER

The Corner Mate now uses the same:
    Depth - 2 * PlinthSetback
corner reference.

Therefore the spacer still ends directly at the linked cabinet front.

3. SHORT PLINTH RETURN REBUILT

The perpendicular short plinth is no longer simply:
    Corner Spacer Width + panel thickness

Its position is now derived from the REAL recessed plinth line of the
90-degree cabinet.

Right:
- return X = corner boundary + PlinthSetback

Left:
- return X = corner boundary - PlinthSetback - PanelThickness

Its Y length connects the parent recessed plinth to the near end of the
linked cabinet plinth.

This should make the short toe-kick visually line up with the side cabinet.

4. LEFT / RIGHT

The side logic is explicitly mirrored:
- Hidden Side = Left -> mate rotation -90°
- Hidden Side = Right -> mate rotation +90°

Changing Hidden Side now runs a dedicated full resync of the two-cabinet set.

5. PRODUCTION

Board Parts / Cut List now use the corrected Plinth Return length.

UNCHANGED:
- hidden closed box
- door-clearance width control
- mate width/depth controls
- production/Cut Layout infrastructure
- existing L-shaped corner cabinets
